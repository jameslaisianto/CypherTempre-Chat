"""Server-level Timechain operations, session management, memory model, and App class.

Imports the root timechain.py as the low-level library and adds server-specific
session-aware operations on top.
"""

from __future__ import annotations

import base64
import datetime as dt
import importlib.util
import json
import os
import pathlib
import re
import shutil
import sys
import uuid
from types import SimpleNamespace
from typing import Any

from server.config import (
    DEFAULT_MODEL, DEFAULT_PROVIDER, PROVIDERS, IMAGE_PROVIDERS, PERSONAS,
    DOMAIN_KEYWORDS, GUIDE_TOPICS, GUIDE_EXPLAINER_PERSONA,
    DEFAULT_TIMECHAIN_PATH, DEFAULT_ENV_PATH,
    ACTIVE_CONTEXT_DAYS,
)

from server.llm import (
    recall_memory_facts,
    build_memory_fact_context,
    memory_retry_reason,
    local_memory_answer,
    build_retry_messages,
    parse_memory_candidate_json,
    build_memory_candidate_messages,
    generate_llm_memory_candidates,
    generate_persona_from_seed,
    parse_ring_time,
    relative_time_label,
    utc_offset_label,
    current_time_context,
    build_memory_context,
    trim_for_prompt,
    compact_persona_system,
    build_recent_turns,
    prompt_size,
    response_token_budget,
    build_prompt_messages,
    serialize_history,
    serialize_ring,
    serialize_rings,
    serialize_cambium_report,
    build_sync_snapshot,
    classify_domain,
    normalize_custom_persona,
    build_messages,
    call_llm,
    call_openrouter,
    call_image_generation,
)

def active_call_llm(*args: Any, **kwargs: Any) -> dict[str, Any]:
    package = sys.modules.get("server")
    patched = getattr(package, "call_llm", None) if package else None
    target = patched if callable(patched) else call_llm
    return target(*args, **kwargs)

def resolve_timechain_path(path: pathlib.Path) -> pathlib.Path:
    candidates = [
        path,
        pathlib.Path(os.environ.get("TIMECHAIN_PATH", "")) if os.environ.get("TIMECHAIN_PATH") else None,
        pathlib.Path(__file__).resolve().parent.parent / "timechain.py",
    ]
    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate.resolve()
    raise FileNotFoundError(
        "timechain.py not found. Copy it into cyphertempre-chat-poc/timechain.py "
        "or pass --timechain-path /path/to/timechain.py."
    )

def load_timechain_module(path: pathlib.Path) -> Any:
    path = resolve_timechain_path(path)
    spec = importlib.util.spec_from_file_location("cyphertempre_timechain", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not import Timechain script: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MEMORY_SCOPES = {"global", "session"}
MEMORY_KINDS = {"identity", "preference", "goal", "correction", "boundary", "style", "uncertainty", "persona"}
MEMORY_ACCEPTED_STATUSES = {"accepted", "known", "uncertain"}
MEMORY_INACTIVE_STATUSES = {"pending", "rejected", "superseded", "forgotten"}
GLOBAL_MEMORY_KINDS = {"identity", "preference", "boundary", "style", "persona"}
ALWAYS_ACTIVE_MEMORY_KINDS = {"identity", "boundary", "persona"}

def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)

def iso_now() -> str:
    return utc_now().isoformat()

def parse_iso_datetime(value: Any) -> dt.datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)

def age_days(value: Any, *, now: dt.datetime | None = None) -> int | None:
    parsed = parse_iso_datetime(value)
    if not parsed:
        return None
    current = now or utc_now()
    if current.tzinfo is None:
        current = current.replace(tzinfo=dt.timezone.utc)
    delta = current.astimezone(dt.timezone.utc) - parsed
    return max(0, delta.days)

def empty_memory_model() -> dict[str, Any]:
    return {"version": 3, "facts": []}

def memory_model_path(workspace: pathlib.Path) -> pathlib.Path:
    return workspace / ".timechain" / "memory_model.json"

def ring_timestamp_map(workspace: pathlib.Path) -> dict[int, str]:
    path = workspace / ".timechain" / "chain.jsonl"
    timestamps: dict[int, str] = {}
    if not path.exists():
        return timestamps
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return timestamps
    for line in lines:
        try:
            raw = json.loads(line)
            number = int(raw.get("n", 0) or 0)
        except (json.JSONDecodeError, TypeError, ValueError):
            continue
        timestamp = str(raw.get("ts", "")).strip()
        if timestamp:
            timestamps[number] = timestamp
    return timestamps

def ensure_memory_model_v3(model: dict[str, Any], *, ring_timestamps: dict[int, str] | None = None, now: dt.datetime | None = None) -> dict[str, Any]:
    model["version"] = max(3, int(model.get("version", 3) or 3))
    ring_timestamps = ring_timestamps or {}
    fallback = (now or utc_now()).isoformat()
    for fact in model.setdefault("facts", []):
        try:
            source_ring = int(fact.get("source_ring", 0) or 0)
        except (TypeError, ValueError):
            source_ring = 0
        created = str(fact.get("created_at") or fact.get("updated_at") or ring_timestamps.get(source_ring) or fallback)
        fact.setdefault("created_at", created)
        fact.setdefault("updated_at", created)
        fact.setdefault("scope", _memory_scope_for_fact(fact, session_id=str(fact.get("session_id", "default"))))
        fact.setdefault("session_id", "default")
    return model

def load_memory_model(workspace: pathlib.Path) -> dict[str, Any]:
    path = memory_model_path(workspace)
    if not path.exists():
        return empty_memory_model()
    try:
        model = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return empty_memory_model()
    if not isinstance(model, dict) or not isinstance(model.get("facts"), list):
        return empty_memory_model()
    return ensure_memory_model_v3(model, ring_timestamps=ring_timestamp_map(workspace))

def save_memory_model(workspace: pathlib.Path, model: dict[str, Any]) -> None:
    path = memory_model_path(workspace)
    path.parent.mkdir(parents=True, exist_ok=True)
    ensure_memory_model_v3(model, ring_timestamps=ring_timestamp_map(workspace))
    path.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")

def custom_personas_path(workspace: pathlib.Path) -> pathlib.Path:
    return workspace / ".timechain" / "custom_personas.json"

def session_metadata_path(workspace: pathlib.Path) -> pathlib.Path:
    return workspace / ".timechain" / "session.json"

def load_session_metadata(workspace: pathlib.Path) -> dict[str, Any]:
    path = session_metadata_path(workspace)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}

def save_session_metadata(workspace: pathlib.Path, metadata: dict[str, Any]) -> None:
    path = session_metadata_path(workspace)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

def load_custom_personas(workspace: pathlib.Path) -> dict[str, dict[str, str]]:
    path = custom_personas_path(workspace)
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(raw, dict):
        return {}
    personas: dict[str, dict[str, str]] = {}
    for key, value in raw.items():
        persona_id = sanitize_session_id(str(key))
        if not persona_id:
            continue
        persona = normalize_custom_persona(value)
        if persona:
            personas[persona_id] = persona
    return personas

def save_custom_personas(workspace: pathlib.Path, personas: dict[str, dict[str, str]]) -> None:
    path = custom_personas_path(workspace)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(personas, ensure_ascii=False, indent=2), encoding="utf-8")

def load_all_public_custom_personas(root_workspace: pathlib.Path) -> dict[str, dict[str, Any]]:
    public_personas: dict[str, dict[str, Any]] = {}
    users_dir = root_workspace / "data" / "users"
    if not users_dir.exists():
        return public_personas
    for user_dir in users_dir.iterdir():
        if not user_dir.is_dir():
            continue
        path = user_dir / "custom_personas.json"
        if not path.exists():
            continue
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(raw, dict):
            continue
        for key, value in raw.items():
            persona = normalize_custom_persona(value)
            if persona and persona.get("visibility") == "public":
                original_id = sanitize_session_id(str(key))
                namespaced_id = f"{user_dir.name}:{original_id}"
                public_personas[namespaced_id] = {**persona, "owner": user_dir.name}
    return public_personas

def load_user_custom_personas(root_workspace: pathlib.Path, username: str) -> dict[str, dict[str, str]]:
    path = root_workspace / "data" / "users" / username / "custom_personas.json"
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(raw, dict):
        return {}
    personas: dict[str, dict[str, str]] = {}
    for key, value in raw.items():
        persona_id = sanitize_session_id(str(key))
        if not persona_id:
            continue
        persona = normalize_custom_persona(value)
        if persona:
            personas[persona_id] = persona
    return personas

def save_user_custom_personas(root_workspace: pathlib.Path, username: str, personas: dict[str, dict[str, str]]) -> None:
    path = root_workspace / "data" / "users" / username / "custom_personas.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(personas, ensure_ascii=False, indent=2), encoding="utf-8")

def _clean_fact_value(value: str, *, max_words: int = 12) -> str:
    cleaned = re.sub(r"\s+", " ", value or "").strip(" .,!?:;\"'")
    words = cleaned.split()
    return " ".join(words[:max_words]).strip(" .,!?:;\"'")


def _name_value(value: str) -> str:
    cleaned = _clean_fact_value(value, max_words=3)
    cleaned = re.split(r"\b(?:nice to meet|glad to meet|and i|but i|because|from)\b", cleaned, flags=re.I)[0]
    return _clean_fact_value(cleaned, max_words=3)


def _looks_like_name(value: str, *, explicit: bool) -> bool:
    if not value:
        return False
    lowered = value.lower()
    if lowered in {"tired", "hungry", "sad", "happy", "angry", "here", "there", "ready", "sure"}:
        return False
    if lowered.split()[0] in {"a", "an", "the", "not", "still", "just", "very"}:
        return False
    if explicit:
        return bool(re.search(r"[A-Za-z]", value))
    return bool(re.match(r"^[A-Z][A-Za-z0-9_-]*(?:\s+[A-Z][A-Za-z0-9_-]*){0,2}$", value))


def _fact(
    *,
    kind: str,
    key: str,
    value: str,
    confidence: float,
    source_ring: int,
    evidence: str,
    status: str = "known",
) -> dict[str, Any]:
    timestamp = iso_now()
    return {
        "id": uuid.uuid4().hex,
        "kind": kind,
        "key": key,
        "value": value,
        "confidence": round(confidence, 3),
        "source_ring": source_ring,
        "evidence": trim_for_prompt(evidence, 260),
        "status": status,
        "supersedes": None,
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def _memory_scope_for_fact(fact: dict[str, Any], *, session_id: str = "default") -> str:
    scope = str(fact.get("scope", "")).strip().lower()
    if scope in MEMORY_SCOPES:
        return scope
    kind = str(fact.get("kind", "")).strip().lower()
    key = str(fact.get("key", "")).strip().lower()
    if kind in GLOBAL_MEMORY_KINDS or key in {"user.name", "assistant.persona_name"}:
        return "global"
    return "session" if session_id != "default" else "global"


def _memory_kind_for_key(kind: str, key: str) -> str:
    kind = (kind or "").strip().lower()
    if kind in MEMORY_KINDS:
        return kind
    key = (key or "").strip().lower()
    if key.startswith("user.preference"):
        return "preference"
    if key in {"user.name", "user.description"}:
        return "identity"
    if key.startswith("assistant."):
        return "persona"
    if "uncertainty" in key:
        return "uncertainty"
    return "preference"


def _memory_key(kind: str, raw_key: str, value: str) -> str:
    key = re.sub(r"[^a-z0-9_.-]+", ".", (raw_key or "").strip().lower()).strip(".")
    if key:
        return key[:80]
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:24] or uuid.uuid4().hex[:8]
    return f"user.{kind}.{slug}"


def normalize_memory_candidate(
    raw: dict[str, Any],
    *,
    source_ring: int,
    evidence: str,
    session_id: str = "default",
    source: str = "deterministic",
) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    value = _clean_fact_value(str(raw.get("value", "")), max_words=28)
    if not value:
        return None
    kind = _memory_kind_for_key(str(raw.get("kind", "")), str(raw.get("key", "")))
    key = _memory_key(kind, str(raw.get("key", "")), value)
    try:
        confidence = float(raw.get("confidence", 0.6))
    except (TypeError, ValueError):
        confidence = 0.6
    confidence = max(0.1, min(0.98, confidence))
    if source == "llm":
        confidence = min(confidence, 0.82)
    scope = _memory_scope_for_fact({"scope": raw.get("scope"), "kind": kind, "key": key}, session_id=session_id)
    timestamp = str(raw.get("created_at") or raw.get("updated_at") or iso_now())
    return {
        "id": str(raw.get("id") or uuid.uuid4().hex),
        "kind": kind,
        "key": key,
        "value": value,
        "confidence": round(confidence, 3),
        "source_ring": int(raw.get("source_ring") or source_ring or 0),
        "evidence": trim_for_prompt(str(raw.get("evidence") or evidence), 280),
        "status": "pending",
        "scope": scope,
        "session_id": sanitize_session_id(str(raw.get("session_id") or session_id or "default")),
        "supersedes": raw.get("supersedes"),
        "source": source,
        "created_at": timestamp,
        "updated_at": str(raw.get("updated_at") or timestamp),
    }


def _memory_duplicate(facts: list[dict[str, Any]], candidate: dict[str, Any]) -> dict[str, Any] | None:
    for fact in facts:
        if fact.get("status") not in {"pending", "accepted", "known", "uncertain"}:
            continue
        if str(fact.get("key", "")).lower() != str(candidate.get("key", "")).lower():
            continue
        if str(fact.get("value", "")).lower() != str(candidate.get("value", "")).lower():
            continue
        if str(fact.get("scope", "global")) != str(candidate.get("scope", "global")):
            continue
        if str(fact.get("scope", "global")) == "session" and str(fact.get("session_id", "")) != str(candidate.get("session_id", "")):
            continue
        return fact
    return None


def memory_activity(fact: dict[str, Any], *, now: dt.datetime | None = None) -> dict[str, Any]:
    status = str(fact.get("status", "")).strip().lower()
    kind = str(fact.get("kind", "")).strip().lower()
    days = age_days(fact.get("created_at") or fact.get("updated_at"), now=now)
    if status == "pending":
        return {"active": False, "age_days": days, "stale_reason": "pending review"}
    if status in {"rejected", "forgotten"}:
        return {"active": False, "age_days": days, "stale_reason": status}
    if status == "superseded":
        return {"active": False, "age_days": days, "stale_reason": "superseded"}
    if status not in MEMORY_ACCEPTED_STATUSES:
        return {"active": False, "age_days": days, "stale_reason": "inactive"}
    if kind in ALWAYS_ACTIVE_MEMORY_KINDS:
        return {"active": True, "age_days": days, "stale_reason": ""}
    if days is not None and days > ACTIVE_CONTEXT_DAYS:
        return {"active": False, "age_days": days, "stale_reason": f"older than {ACTIVE_CONTEXT_DAYS} days"}
    return {"active": True, "age_days": days, "stale_reason": ""}


def annotate_memory(fact: dict[str, Any], *, now: dt.datetime | None = None) -> dict[str, Any]:
    annotated = dict(fact)
    annotated.update(memory_activity(annotated, now=now))
    return annotated


def active_memory_facts(facts: list[dict[str, Any]], *, now: dt.datetime | None = None) -> list[dict[str, Any]]:
    return [
        annotate_memory(fact, now=now)
        for fact in facts
        if memory_activity(fact, now=now)["active"]
    ]


def ring_is_active(ring: Any, *, now: dt.datetime | None = None) -> bool:
    if getattr(ring, "kind", "") == "genesis":
        return False
    days = age_days(getattr(ring, "ts", ""), now=now)
    return days is None or days <= ACTIVE_CONTEXT_DAYS


def split_active_rings(chain: list[Any], *, now: dt.datetime | None = None) -> tuple[list[Any], list[Any]]:
    active: list[Any] = []
    stale: list[Any] = []
    for ring in chain:
        if getattr(ring, "kind", "") == "genesis":
            continue
        if ring_is_active(ring, now=now):
            active.append(ring)
        else:
            stale.append(ring)
    return active, stale


def active_recall_chain(chain: list[Any], *, now: dt.datetime | None = None) -> list[Any]:
    if not chain:
        return []
    genesis = [ring for ring in chain if getattr(ring, "kind", "") == "genesis"][:1]
    active, _ = split_active_rings(chain, now=now)
    return genesis + active


def stage_memory_candidates(
    model: dict[str, Any],
    ring: Any,
    *,
    persona_name: str,
    session_id: str = "default",
    llm_candidates: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    model.setdefault("version", 3)
    facts = model.setdefault("facts", [])
    source_ring = int(getattr(ring, "n", 0) or 0)
    evidence = str(getattr(ring, "query", "") or "")
    staged: list[dict[str, Any]] = []
    raw_candidates: list[tuple[dict[str, Any], str]] = [
        (fact, "deterministic") for fact in extract_memory_facts(ring, persona_name=persona_name)
    ]
    raw_candidates.extend((candidate, "llm") for candidate in (llm_candidates or []))
    for raw, source in raw_candidates:
        candidate = normalize_memory_candidate(
            raw,
            source_ring=source_ring,
            evidence=evidence,
            session_id=session_id,
            source=source,
        )
        if not candidate:
            continue
        duplicate = _memory_duplicate(facts, candidate)
        if duplicate:
            if duplicate.get("status") == "pending":
                duplicate["confidence"] = max(float(duplicate.get("confidence", 0)), candidate["confidence"])
                duplicate["evidence"] = candidate["evidence"]
                staged.append(duplicate)
            continue
        facts.append(candidate)
        staged.append(candidate)
    return staged


def _find_memory(model: dict[str, Any], memory_id: str) -> dict[str, Any]:
    memory_id = str(memory_id or "").strip()
    for fact in model.setdefault("facts", []):
        if str(fact.get("id", "")) == memory_id:
            return fact
    raise KeyError(f"Unknown memory: {memory_id}")


def accept_memory(model: dict[str, Any], memory_id: str) -> dict[str, Any]:
    fact = _find_memory(model, memory_id)
    previous_status = str(fact.get("status", "pending"))
    timestamp = iso_now()
    fact.setdefault("created_at", timestamp)
    fact["updated_at"] = timestamp
    fact["status"] = "accepted"
    fact.setdefault("scope", _memory_scope_for_fact(fact))
    fact.setdefault("session_id", "default")
    if previous_status != "accepted":
        for existing in model.setdefault("facts", []):
            if existing is fact or existing.get("status") not in MEMORY_ACCEPTED_STATUSES:
                continue
            if str(existing.get("key", "")).lower() != str(fact.get("key", "")).lower():
                continue
            if str(existing.get("scope", "global")) != str(fact.get("scope", "global")):
                continue
            if str(fact.get("scope", "global")) == "session" and str(existing.get("session_id", "")) != str(fact.get("session_id", "")):
                continue
            existing["status"] = "superseded"
            existing.setdefault("created_at", existing.get("updated_at") or timestamp)
            existing["updated_at"] = timestamp
            fact["supersedes"] = existing.get("id")
    return fact


def reject_memory(model: dict[str, Any], memory_id: str) -> dict[str, Any]:
    fact = _find_memory(model, memory_id)
    fact["status"] = "rejected"
    fact["updated_at"] = iso_now()
    return fact


def forget_memory(model: dict[str, Any], memory_id: str) -> dict[str, Any]:
    fact = _find_memory(model, memory_id)
    fact["status"] = "forgotten"
    fact["updated_at"] = iso_now()
    return fact


def edit_memory(model: dict[str, Any], memory_id: str, patch: dict[str, Any]) -> dict[str, Any]:
    fact = _find_memory(model, memory_id)
    updated = normalize_memory_candidate(
        {**fact, **(patch or {})},
        source_ring=int(fact.get("source_ring", 0) or 0),
        evidence=str(fact.get("evidence", "")),
        session_id=str(fact.get("session_id", "default")),
        source=str(fact.get("source", "manual")),
    )
    if not updated:
        raise ValueError("Memory edit requires a non-empty value.")
    for key in ("kind", "key", "value", "confidence", "scope", "session_id", "evidence"):
        fact[key] = updated[key]
    fact["updated_at"] = iso_now()
    return fact


def extract_memory_facts(ring: Any, *, persona_name: str) -> list[dict[str, Any]]:
    query = str(getattr(ring, "query", "") or "")
    ring_number = int(getattr(ring, "n", 0) or 0)
    facts: list[dict[str, Any]] = []

    name_patterns = (
        (r"\bmy name is\s+([^,.\n!?]+)", 0.96, True),
        (r"\bcall me\s+([^,.\n!?]+)", 0.92, True),
        (r"\bi am\s+([^,.\n!?]+)", 0.82, False),
        (r"\bi'm\s+([^,.\n!?]+)", 0.82, False),
    )
    for pattern, confidence, explicit in name_patterns:
        match = re.search(pattern, query, re.I)
        if not match:
            continue
        value = _name_value(match.group(1))
        if _looks_like_name(value, explicit=explicit):
            facts.append(_fact(
                kind="identity",
                key="user.name",
                value=value,
                confidence=confidence,
                source_ring=ring_number,
                evidence=query,
            ))
            break

    description_match = re.search(r"\bi am\s+((?:a|an|the)\s+[^,.\n!?]+)", query, re.I)
    if description_match:
        value = _clean_fact_value(description_match.group(1), max_words=10)
        if value and not any(fact["key"] == "user.name" for fact in facts):
            facts.append(_fact(
                kind="identity",
                key="user.description",
                value=value,
                confidence=0.68,
                source_ring=ring_number,
                evidence=query,
            ))

    persona_match = re.search(r"\byou are\s+([A-Z][A-Za-z0-9_-]*(?:\s+[A-Z][A-Za-z0-9_-]*){0,2})", query)
    if persona_match:
        value = _name_value(persona_match.group(1))
        if value and value.lower() != persona_name.lower():
            facts.append(_fact(
                kind="persona",
                key="assistant.persona_name",
                value=value,
                confidence=0.74,
                source_ring=ring_number,
                evidence=query,
            ))

    preference_patterns = (
        r"\bi prefer\s+([^.\n!?]+)",
        r"\bi like\s+([^.\n!?]+)",
        r"\bi want you to\s+([^.\n!?]+)",
        r"\bplease\s+([^.\n!?]+)",
    )
    for pattern in preference_patterns:
        match = re.search(pattern, query, re.I)
        if match:
            value = _clean_fact_value(match.group(1), max_words=18)
            if value:
                facts.append(_fact(
                    kind="preference",
                    key=f"user.preference.{len(facts) + 1}",
                    value=value,
                    confidence=0.66,
                    source_ring=ring_number,
                    evidence=query,
                ))
            break

    if re.search(r"\b(?:not sure|i don't know|i do not know|maybe|perhaps)\b", query, re.I):
        facts.append(_fact(
            kind="uncertainty",
            key="user.uncertainty",
            value=_clean_fact_value(query, max_words=18),
            confidence=0.55,
            source_ring=ring_number,
            evidence=query,
            status="uncertain",
        ))

    return facts


def update_memory_model(model: dict[str, Any], ring: Any, *, persona_name: str) -> list[dict[str, Any]]:
    model.setdefault("version", 3)
    facts = model.setdefault("facts", [])
    extracted = extract_memory_facts(ring, persona_name=persona_name)
    correction = bool(re.match(r"^\s*(?:no|nope|actually|correction|wrong)\b", str(getattr(ring, "query", "")), re.I))

    for fact in extracted:
        if correction or fact["key"] in {"user.name", "assistant.persona_name"}:
            previous = [
                existing for existing in facts
                if existing.get("key") == fact["key"] and existing.get("status") == "known"
            ]
            for existing in previous:
                existing["status"] = "superseded"
                fact["supersedes"] = existing.get("id")

        duplicate = next(
            (
                existing for existing in facts
                if existing.get("key") == fact["key"]
                and str(existing.get("value", "")).lower() == fact["value"].lower()
                and existing.get("status") == fact["status"]
            ),
            None,
        )
        if duplicate:
            duplicate["confidence"] = max(float(duplicate.get("confidence", 0)), fact["confidence"])
            duplicate["source_ring"] = fact["source_ring"]
            duplicate["evidence"] = fact["evidence"]
        else:
            facts.append(fact)
    return extracted


def parse_env_file(path: pathlib.Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values

def load_local_env(path: pathlib.Path) -> dict[str, str]:
    values = parse_env_file(path)
    for key, value in values.items():
        os.environ.setdefault(key, value)
    return values

def guide_topics_payload() -> list[dict[str, Any]]:
    return [
        {
            "id": topic["id"],
            "title": topic["title"],
            "summary": topic["summary"],
            "details": topic["details"],
            "sources": list(topic.get("sources", [])),
        }
        for topic in GUIDE_TOPICS
    ]

def env_value(*names: str) -> str:
    for name in names:
        value = os.environ.get(name, "")
        if value:
            return value
    return ""

def get_guide_topic(topic_id: str) -> dict[str, Any]:
    topic_id = (topic_id or "").strip()
    for topic in GUIDE_TOPICS:
        if topic["id"] == topic_id:
            return topic
    raise KeyError(topic_id)

def _doc_path(workspace: pathlib.Path, source: str) -> pathlib.Path | None:
    root = workspace.resolve()
    candidate = (root / source).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    if candidate.exists() and candidate.is_file():
        return candidate
    return None

def _relevant_excerpt(path: pathlib.Path, keywords: set[str], *, max_chars: int = 900) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    matches: list[str] = []
    for paragraph in paragraphs:
        lowered = paragraph.lower()
        if any(keyword in lowered for keyword in keywords):
            matches.append(re.sub(r"\s+", " ", paragraph))
        if len("\n\n".join(matches)) >= max_chars:
            break
    if not matches:
        matches = [re.sub(r"\s+", " ", paragraphs[0])] if paragraphs else []
    excerpt = "\n\n".join(matches)
    return excerpt[:max_chars].strip()

def build_guide_source_bundle(topic: dict[str, Any], workspace: pathlib.Path) -> list[dict[str, str]]:
    keywords = {
        word.lower()
        for word in re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", f"{topic['id']} {topic['title']} {topic['summary']} {topic['details']}")
    }
    sources = [{
        "title": f"Guide: {topic['title']}",
        "path": "local guide",
        "excerpt": f"{topic['summary']}\n{topic['details']}",
    }]
    for source in topic.get("sources", []):
        if source.startswith("Guide:"):
            continue
        path = _doc_path(workspace, source)
        if not path:
            continue
        excerpt = _relevant_excerpt(path, keywords)
        if excerpt:
            sources.append({
                "title": source,
                "path": str(path),
                "excerpt": excerpt,
            })
    return sources

def build_guide_explainer_messages(topic: dict[str, Any], source_bundle: list[dict[str, str]]) -> list[dict[str, str]]:
    source_text = "\n\n".join(
        f"Source: {source['title']}\nPath: {source['path']}\nExcerpt:\n{source['excerpt']}"
        for source in source_bundle
    )
    return [
        {"role": "system", "content": GUIDE_EXPLAINER_PERSONA["system"]},
        {
            "role": "user",
            "content": (
                f"Explain this CypherTempre chat PoC guide topic for a user.\n\n"
                f"Topic: {topic['title']}\n\n"
                f"Source excerpts:\n{source_text}\n\n"
                "Answer in clear paragraphs. Include a short 'Sources used' line naming the local sources."
            ),
        },
    ]

def deterministic_guide_explanation(
    topic: dict[str, Any],
    source_bundle: list[dict[str, str]],
    *,
    provider_error: str = "",
) -> str:
    details = "\n".join(f"- {line.strip()}" for line in str(topic["details"]).splitlines() if line.strip())
    source_names = ", ".join(source["title"] for source in source_bundle)
    prefix = f"Provider unavailable: {provider_error}\n\n" if provider_error else ""
    return (
        f"{prefix}{topic['title']}\n\n"
        f"{topic['summary']}\n\n"
        f"{details}\n\n"
        f"Sources used: {source_names}.\n\n"
        "If you ask about something not covered here, I will say it is not covered in the provided sources."
    )

def sanitize_session_id(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "-", value.strip())[:80].strip("-")
    return cleaned or "default"

def session_name_from_id(session_id: str) -> str:
    if session_id == "default":
        return "Default"
    return session_id.replace("-", " ").replace("_", " ").strip().title() or session_id

def prune_memory_model_to_ring(model: dict[str, Any], max_ring: int) -> dict[str, Any]:
    facts = []
    for fact in model.get("facts", []):
        try:
            source_ring = int(fact.get("source_ring", 0) or 0)
        except (TypeError, ValueError):
            source_ring = 0
        if source_ring <= max_ring:
            facts.append(fact)
    model["facts"] = facts
    return model

class App:
    def __init__(
        self,
        workspace: pathlib.Path,
        timechain_path: pathlib.Path,
        *,
        default_model: str,
        provider: str,
        api_key: str,
        base_url: str,
        timeout: float,
    ) -> None:
        self.root_workspace = workspace.resolve()
        self.root_workspace.mkdir(parents=True, exist_ok=True)
        self.timechain = load_timechain_module(timechain_path)
        self.default_model = default_model
        self.provider = provider
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.active_session = "default"
        self.user_active_sessions: dict[str, str] = {}
        self.workspace = self.workspace_for_session(self.active_session)
        self.agent = self.timechain.TimechainAgent(workspace=self.workspace)

    @property
    def sessions_root(self) -> pathlib.Path:
        return self.root_workspace / "sessions"

    @property
    def archives_root(self) -> pathlib.Path:
        return self.root_workspace / ".timechain_archives"

    def user_sessions_root(self, username: str) -> pathlib.Path:
        return self.root_workspace / "data" / "users" / username / "sessions"

    def user_custom_personas_path(self, username: str) -> pathlib.Path:
        return self.root_workspace / "data" / "users" / username / "custom_personas.json"

    def user_gallery_root(self, username: str) -> pathlib.Path:
        path = self.root_workspace / "data" / "users" / username / "gallery"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def user_gallery_index_path(self, username: str) -> pathlib.Path:
        return self.user_gallery_root(username) / "index.json"

    def load_gallery_index(self, username: str) -> dict[str, Any]:
        path = self.user_gallery_index_path(username)
        if not path.exists():
            return {"images": []}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or "images" not in data:
                return {"images": []}
            return data
        except (json.JSONDecodeError, OSError):
            return {"images": []}

    def save_gallery_index(self, username: str, index: dict[str, Any]) -> None:
        path = self.user_gallery_index_path(username)
        path.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")

    def gallery_image_path(self, username: str, image_id: str) -> pathlib.Path:
        return self.user_gallery_root(username) / f"{image_id}.png"

    def add_gallery_image(
        self,
        username: str,
        *,
        image_id: str,
        prompt: str,
        mode: str,
        model: str,
        provider: str,
        aspect_ratio: str,
        source_id: str = "",
        b64_data: str,
    ) -> dict[str, Any]:
        path = self.gallery_image_path(username, image_id)
        try:
            raw = base64.b64decode(b64_data)
        except Exception as exc:
            raise RuntimeError(f"Invalid base64 image data: {exc}") from exc
        path.write_bytes(raw)
        entry = {
            "id": image_id,
            "prompt": prompt,
            "mode": mode,
            "model": model,
            "provider": provider,
            "aspect_ratio": aspect_ratio,
            "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "filename": f"{image_id}.png",
            "source_id": source_id,
        }
        index = self.load_gallery_index(username)
        index["images"].insert(0, entry)
        self.save_gallery_index(username, index)
        return entry

    def delete_gallery_image(self, username: str, image_id: str) -> bool:
        index = self.load_gallery_index(username)
        original_len = len(index["images"])
        index["images"] = [img for img in index["images"] if img.get("id") != image_id]
        if len(index["images"]) == original_len:
            return False
        self.save_gallery_index(username, index)
        path = self.gallery_image_path(username, image_id)
        if path.exists():
            path.unlink()
        return True

    def workspace_for_session(self, session_id: str, username: str | None = None) -> pathlib.Path:
        session_id = sanitize_session_id(session_id)
        if username:
            path = self.user_sessions_root(username) / session_id
        elif session_id == "default":
            path = self.root_workspace
        else:
            path = self.sessions_root / session_id
        path.mkdir(parents=True, exist_ok=True)
        return path.resolve()

    def use_session(self, session_id: str | None, username: str | None = None) -> str:
        self.active_session = sanitize_session_id(session_id or self.active_session or "default")
        self.workspace = self.workspace_for_session(self.active_session, username=username)
        self.reload_agent()
        if username:
            self.user_active_sessions[username] = self.active_session
        return self.active_session

    def list_sessions(self, username: str | None = None) -> list[dict[str, Any]]:
        sessions: list[dict[str, Any]] = []
        if username:
            default_path = self.workspace_for_session("default", username=username)
            sessions_dir = self.user_sessions_root(username)
        else:
            default_path = self.root_workspace
            sessions_dir = self.sessions_root
        for session_id, path in [("default", default_path)]:
            chain_path = path / ".timechain" / "chain.jsonl"
            if chain_path.exists():
                with chain_path.open("r", encoding="utf-8") as handle:
                    rings = sum(1 for _ in handle)
            else:
                rings = 0
            metadata = load_session_metadata(path)
            persona_id = str(metadata.get("persona_id", "")).strip()
            sessions.append({
                "id": session_id,
                "name": "Default",
                "rings": rings,
                "persona_id": persona_id,
                "persona_name": self.persona_name_for_id(persona_id, username=username),
            })
        if sessions_dir.exists():
            for path in sorted(p for p in sessions_dir.iterdir() if p.is_dir() and p.name != "default"):
                session_id = sanitize_session_id(path.name)
                chain_path = path / ".timechain" / "chain.jsonl"
                if chain_path.exists():
                    with chain_path.open("r", encoding="utf-8") as handle:
                        rings = sum(1 for _ in handle)
                else:
                    rings = 0
                metadata = load_session_metadata(path)
                persona_id = str(metadata.get("persona_id", "")).strip()
                sessions.append({
                    "id": session_id,
                    "name": session_name_from_id(session_id),
                    "rings": rings,
                    "persona_id": persona_id,
                    "persona_name": self.persona_name_for_id(persona_id, username=username),
                })
        return sessions

    def create_session(self, name: str, *, username: str | None = None, persona_id: str = "") -> dict[str, Any]:
        base = sanitize_session_id(name or "New conversation")
        if base == "default":
            base = "conversation"
        session_id = base
        index = 2
        sessions_dir = self.user_sessions_root(username) if username else self.sessions_root
        while (sessions_dir / session_id).exists():
            session_id = f"{base}-{index}"
            index += 1
        self.use_session(session_id, username=username)
        if persona_id:
            self.bind_session_persona(persona_id, username=username)
        metadata = load_session_metadata(self.workspace)
        locked_persona = str(metadata.get("persona_id", "")).strip()
        return {
            "id": session_id,
            "name": session_name_from_id(session_id),
            "rings": len(self.agent.chain),
            "persona_id": locked_persona,
            "persona_name": self.persona_name_for_id(locked_persona, username=username),
        }

    def delete_session(self, session_id: str, username: str | None = None) -> dict[str, Any]:
        session_id = sanitize_session_id(session_id)
        if session_id == "default":
            raise ValueError("Default session cannot be deleted.")
        sessions_dir = self.user_sessions_root(username) if username else self.sessions_root
        target = (sessions_dir / session_id).resolve()
        sessions_root_resolved = sessions_dir.resolve()
        if sessions_root_resolved not in target.parents or not target.exists() or not target.is_dir():
            raise KeyError(f"Unknown session: {session_id}")
        shutil.rmtree(target)
        if self.active_session == session_id:
            self.use_session("default", username=username)
        return {
            "deleted": session_id,
            "active": self.user_active_sessions.get(username or "", "default") if username else self.active_session,
            "sessions": self.list_sessions(username=username),
        }

    def reload_agent(self) -> None:
        self.agent = self.timechain.TimechainAgent(workspace=self.workspace)

    def persona_name_for_id(self, persona_id: str, username: str | None = None) -> str:
        persona_id = sanitize_session_id(persona_id or "")
        persona = self.get_custom_persona(persona_id, username=username) or PERSONAS.get(persona_id)
        if not persona and username:
            mp_entry = marketplace.get_marketplace_persona(persona_id)
            if mp_entry and marketplace.is_subscribed(username, persona_id):
                persona = mp_entry
        return persona.get("name", "") if persona else ""

    def session_persona_id(self) -> str:
        metadata = load_session_metadata(self.workspace)
        return str(metadata.get("persona_id", "")).strip()

    def bind_session_persona(self, persona_id: str, username: str | None = None) -> str:
        metadata = load_session_metadata(self.workspace)
        locked = str(metadata.get("persona_id", "")).strip()
        if locked:
            return locked
        persona_id = sanitize_session_id(persona_id or "companion")
        known = self.get_custom_persona(persona_id, username=username) or persona_id in PERSONAS
        if not known and username:
            mp_entry = marketplace.get_marketplace_persona(persona_id)
            known = bool(mp_entry and marketplace.is_subscribed(username, persona_id))
        if not known:
            persona_id = "companion"
        metadata["persona_id"] = persona_id
        metadata["persona_name"] = self.persona_name_for_id(persona_id, username=username)
        metadata["created_at"] = metadata.get("created_at") or dt.datetime.now(dt.timezone.utc).isoformat()
        save_session_metadata(self.workspace, metadata)
        return persona_id

    def memory_model(self) -> dict[str, Any]:
        global_model = load_memory_model(self.root_workspace)
        if self.workspace.resolve() == self.root_workspace.resolve():
            model = global_model
        else:
            session_model = load_memory_model(self.workspace)
            model = {
                "version": max(int(global_model.get("version", 3)), int(session_model.get("version", 3))),
                "facts": list(global_model.get("facts", [])) + list(session_model.get("facts", [])),
            }
        if not model.get("facts") and len(getattr(self.agent, "chain", [])) > 1:
            for ring in self.agent.chain:
                if getattr(ring, "kind", "") == "interaction":
                    update_memory_model(model, ring, persona_name="Companion")
            if model.get("facts"):
                save_memory_model(self.root_workspace, model)
        return model

    def save_memory_model(self, model: dict[str, Any]) -> None:
        save_memory_model(self.workspace, model)

    def _memory_models_for_update(self) -> list[tuple[pathlib.Path, dict[str, Any]]]:
        root_model = load_memory_model(self.root_workspace)
        if self.workspace.resolve() == self.root_workspace.resolve():
            return [(self.root_workspace, root_model)]
        return [
            (self.root_workspace, root_model),
            (self.workspace, load_memory_model(self.workspace)),
        ]

    def queue_memory_candidates(
        self,
        ring: Any,
        *,
        persona_name: str,
        llm_candidates: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        session_id = self.active_session or "default"
        global_model = load_memory_model(self.root_workspace)
        session_model = global_model if self.workspace.resolve() == self.root_workspace.resolve() else load_memory_model(self.workspace)
        staged: list[dict[str, Any]] = []
        candidates = [
            (fact, "deterministic") for fact in extract_memory_facts(ring, persona_name=persona_name)
        ]
        candidates.extend((candidate, "llm") for candidate in (llm_candidates or []))
        for raw, source in candidates:
            candidate = normalize_memory_candidate(
                raw,
                source_ring=int(getattr(ring, "n", 0) or 0),
                evidence=str(getattr(ring, "query", "") or ""),
                session_id=session_id,
                source=source,
            )
            if not candidate:
                continue
            target_model = global_model if candidate["scope"] == "global" else session_model
            duplicate = _memory_duplicate(target_model.setdefault("facts", []), candidate)
            if duplicate:
                if duplicate.get("status") == "pending":
                    staged.append(duplicate)
                continue
            target_model["facts"].append(candidate)
            staged.append(candidate)
        save_memory_model(self.root_workspace, global_model)
        if session_model is not global_model:
            save_memory_model(self.workspace, session_model)
        return staged

    def list_memories(self, *, now: dt.datetime | None = None) -> dict[str, Any]:
        model = self.memory_model()
        facts = [annotate_memory(fact, now=now) for fact in model.get("facts", [])]
        pending = [fact for fact in facts if fact.get("status") == "pending"]
        accepted = [fact for fact in facts if fact.get("status") in MEMORY_ACCEPTED_STATUSES]
        inactive = [fact for fact in facts if fact.get("status") in MEMORY_INACTIVE_STATUSES]
        return {
            "pending": pending,
            "accepted": accepted,
            "inactive": inactive,
            "all": facts,
        }

    def update_memory_status(self, memory_id: str, action: str, patch: dict[str, Any] | None = None) -> dict[str, Any]:
        action = str(action or "").strip().lower()
        for path, model in self._memory_models_for_update():
            if not any(str(fact.get("id", "")) == str(memory_id) for fact in model.get("facts", [])):
                continue
            if action == "accept":
                memory = accept_memory(model, memory_id)
            elif action == "reject":
                memory = reject_memory(model, memory_id)
            elif action == "forget":
                memory = forget_memory(model, memory_id)
            elif action == "edit":
                memory = edit_memory(model, memory_id, patch or {})
            else:
                raise ValueError(f"Unsupported memory action: {action}")
            save_memory_model(path, model)
            return memory
        raise KeyError(f"Unknown memory: {memory_id}")

    def recall(
        self,
        query: str,
        *,
        domain: str | None = None,
        limit: int = 12,
        now: dt.datetime | None = None,
    ) -> dict[str, Any]:
        memory_model = self.memory_model()
        fact_hits = recall_memory_facts(memory_model, query, limit=limit, session_id=self.active_session, now=now)
        accepted = [fact for fact in memory_model.get("facts", []) if fact.get("status") in MEMORY_ACCEPTED_STATUSES]
        stale_facts = [
            fact for fact in accepted
            if not memory_activity(fact, now=now)["active"]
        ]
        active_chain = active_recall_chain(self.agent.chain, now=now)
        _, stale_rings = split_active_rings(self.agent.chain, now=now)
        retrieved = self.timechain.retrieve(
            active_chain,
            query,
            domain=domain,
            cphy_weights=self.agent.cphy_weights,
            config=self.timechain.RetrieverConfig(limit=max(1, min(limit, 20))),
        )
        results = []
        for score, ring in retrieved:
            content = ring.content[:500] if len(ring.content) > 500 else ring.content
            results.append({
                "score": round(float(score), 4),
                "n": ring.n,
                "ts": ring.ts,
                "brightness": ring.brightness,
                "kind": ring.kind,
                "domain": ring.domain,
                "query": ring.query,
                "content": content,
                "tags": ring.tags,
                "hash_prefix": ring.hash[:16],
                "epistemic": ring.epistemic,
            })
        diagnostics = [
            f"durable facts matched: {len(fact_hits)}",
            f"rings matched: {len(results)}",
            f"domain filter: {domain or 'none'}",
            f"active context days: {ACTIVE_CONTEXT_DAYS}",
            f"stale durable facts filtered: {len(stale_facts)}",
            f"stale rings filtered: {len(stale_rings)}",
        ]
        return {
            "query": query,
            "facts": fact_hits,
            "rings": results,
            "results": results,
            "diagnostics": diagnostics,
            "active_context_days": ACTIVE_CONTEXT_DAYS,
            "filtered_stale_memory_count": len(stale_facts),
            "filtered_stale_ring_count": len(stale_rings),
        }

    def custom_personas(self, username: str | None = None) -> dict[str, dict[str, str]]:
        if username:
            return load_user_custom_personas(self.root_workspace, username)
        return load_custom_personas(self.root_workspace)

    def get_custom_persona(self, persona_id: str, username: str | None = None) -> dict[str, str] | None:
        return self.custom_personas(username=username).get(sanitize_session_id(persona_id))

    def save_custom_persona(self, persona_id: str, persona: dict[str, str], username: str | None = None) -> dict[str, str]:
        persona_id = sanitize_session_id(persona_id)
        normalized = normalize_custom_persona(persona)
        if not normalized:
            raise ValueError("Invalid custom persona.")
        personas = self.custom_personas(username=username)
        personas[persona_id] = normalized
        if username:
            save_user_custom_personas(self.root_workspace, username, personas)
        else:
            save_custom_personas(self.root_workspace, personas)
        return normalized

    def delete_custom_persona(self, persona_id: str, username: str | None = None) -> dict[str, dict[str, str]]:
        persona_id = sanitize_session_id(persona_id)
        if not persona_id or persona_id in PERSONAS:
            raise ValueError("Built-in personas cannot be deleted.")
        personas = self.custom_personas(username=username)
        if persona_id not in personas:
            raise KeyError(f"Unknown custom persona: {persona_id}")
        personas.pop(persona_id, None)
        if username:
            save_user_custom_personas(self.root_workspace, username, personas)
        else:
            save_custom_personas(self.root_workspace, personas)
        return personas

    def self_model(self, *, now: dt.datetime | None = None) -> dict[str, Any]:
        model = self.agent.self_model()
        memory_model = self.memory_model()
        facts = [annotate_memory(fact, now=now) for fact in memory_model.get("facts", [])]
        accepted_facts = [fact for fact in facts if fact.get("status") in MEMORY_ACCEPTED_STATUSES]
        active_memories = [fact for fact in accepted_facts if fact.get("active")]
        stale_memories = [fact for fact in accepted_facts if not fact.get("active")]
        active_rings, stale_rings = split_active_rings(self.agent.chain, now=now)
        model["workspace"] = str(self.workspace)
        model["active_context_days"] = ACTIVE_CONTEXT_DAYS
        model["memory_facts"] = accepted_facts
        model["memory_fact_count"] = len(model["memory_facts"])
        model["pending_memory_count"] = sum(1 for fact in memory_model.get("facts", []) if fact.get("status") == "pending")
        model["active_memory_count"] = len(active_memories)
        model["stale_memory_count"] = len(stale_memories)
        model["active_ring_count"] = len(active_rings)
        model["stale_ring_count"] = len(stale_rings)
        return model

    def ring_workbench(self, *, limit: int = 24) -> dict[str, Any]:
        self.reload_agent()
        return {
            "session": self.active_session,
            "rings": serialize_rings(self.agent.chain, limit=limit),
            "ring_count": len(self.agent.chain),
        }

    def cambium_workbench(self) -> dict[str, Any]:
        self.reload_agent()
        report = self.agent.cambium_report()
        return serialize_cambium_report(report)

    def sync_snapshot(self) -> dict[str, Any]:
        self.reload_agent()
        ok, status = self.timechain.verify_chain(self.agent.chain)
        rings = serialize_rings(self.agent.chain, limit=16)
        memories = self.list_memories()
        cambium = self.cambium_workbench()
        model = self.self_model()
        return {
            "session": self.active_session,
            "verify_ok": ok,
            "verify_status": status,
            "snapshot": build_sync_snapshot(
                session_id=self.active_session,
                workspace=self.workspace,
                self_model=model,
                rings=rings,
                memories=memories,
                cambium=cambium,
                verify_status=status,
            ),
        }

    def set_frozen(self, frozen: bool) -> dict[str, Any]:
        self.reload_agent()
        self.agent.freeze(bool(frozen))
        return {
            "session": self.active_session,
            "frozen": self.agent.frozen,
            "rings": len(self.agent.chain),
        }

    def run_dream(self, domains: str, *, cycles: int = 3) -> dict[str, Any]:
        self.reload_agent()
        if self.agent.frozen:
            raise PermissionError("timechain is frozen")
        domain_list = [part.strip() for part in str(domains or "").split(",") if part.strip()]
        if len(domain_list) < 2:
            raise ValueError("At least two dream domains are required.")
        cycles = max(1, min(int(cycles), 12))
        dreams = self.agent.dream(domains=domain_list, cycles=cycles)
        return {
            "ok": True,
            "session": self.active_session,
            "domains": domain_list,
            "dreams": [
                {
                    "n": ring.n,
                    "kind": ring.kind,
                    "domain": ring.domain,
                    "content": ring.content,
                    "brightness": round(float(ring.brightness), 4),
                    "epistemic": ring.epistemic,
                    "tags": ring.tags,
                    "hash_prefix": ring.hash[:16],
                }
                for ring in dreams
            ],
        }

    def list_overlays(self) -> dict[str, Any]:
        return {
            "ok": True,
            "session": self.active_session,
            "overlays": self.timechain.TimechainStore(self.workspace).load_overlays(),
        }

    def set_overlay(self, tag: str, weight: float) -> dict[str, Any]:
        tag = str(tag or "").strip()
        if not tag:
            raise ValueError("overlay tag is required")
        try:
            weight_value = float(weight)
        except (TypeError, ValueError) as exc:
            raise ValueError("overlay weight must be a number") from exc
        store = self.timechain.TimechainStore(self.workspace)
        overlays = store.load_overlays()
        overlays[tag] = weight_value
        store.save_overlays(overlays)
        return {"ok": True, "session": self.active_session, "overlays": overlays}

    def memory_sync(self) -> dict[str, Any]:
        self.reload_agent()
        ok, status = self.timechain.verify_chain(self.agent.chain)
        if not ok:
            raise ValueError(f"verification failed: {status}")
        model = self.agent.self_model()
        overlays = self.agent.store.load_overlays()
        lines = [
            f"- Agent: **{model['name']}** (`{model['agent_id']}`)",
            f"- Core: {model['core']}",
            f"- Covenant: {model['covenant'][:80]}...",
            f"- Rings: {model['ring_count']}",
            f"- Temporal mass: {model['temporal_mass']}",
            f"- Frozen: {model['frozen']}",
            f"- Top domains: {', '.join(model['top_domains']) if model['top_domains'] else '(none)'}",
            f"- Untouched domains: {', '.join(model['untouched_se_domains']) if model['untouched_se_domains'] else '(none)'}",
            f"- Gaps: {model['gaps']}",
            f"- Consolidations: {model['consolidations']}",
            f"- Active overlays: {json.dumps(overlays, ensure_ascii=False)}",
            f"- Genesis hash prefix: `{model['genesis_hash'][:16]}`",
        ]
        memory_md, daily = self.timechain.ensure_memory_paths(self.workspace)
        self.timechain.update_memory_summary(memory_md, "\n".join(lines))
        self.timechain.append_daily_log(
            daily,
            f"Timechain sync: rings={model['ring_count']} mass={model['temporal_mass']} top={model['top_domains']}",
        )
        return {"ok": True, "session": self.active_session, "memory_md": str(memory_md), "daily": str(daily)}

    def fleet_import(self, ring: dict[str, Any], *, source: str) -> dict[str, Any]:
        self.reload_agent()
        if self.agent.frozen:
            raise PermissionError("timechain is frozen")
        if not isinstance(ring, dict):
            raise ValueError("ring must be a JSON object")
        source = str(source or "").strip()
        if not source:
            raise ValueError("source is required")
        imported = self.agent.fleet_import(ring, source=source)
        if imported is None:
            raise ValueError("fleet import rejected by covenant gate")
        return {
            "ok": True,
            "session": self.active_session,
            "ring": imported.n,
            "kind": imported.kind,
            "hash": imported.hash[:16],
            "brightness": round(float(imported.brightness), 4),
        }

    def challenge(self, indices: str, *, nonce: str = "") -> dict[str, Any]:
        self.reload_agent()
        try:
            parsed_indices = [int(part.strip()) for part in str(indices or "").split(",") if part.strip()]
        except ValueError as exc:
            raise ValueError("indices must be comma-separated integers") from exc
        challenge = {"indices": parsed_indices, "nonce": str(nonce or "") or os.urandom(8).hex()}
        return {"ok": True, "session": self.active_session, **self.agent.respond_to_challenge(challenge)}

    def archive_active_timechain(self, *, label: str) -> pathlib.Path:
        self.archives_root.mkdir(parents=True, exist_ok=True)
        timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        archive = (self.archives_root / f"{self.active_session}-{label}-{timestamp}").resolve()
        archives_root = self.archives_root.resolve()
        if archives_root not in archive.parents:
            raise RuntimeError(f"Refusing to archive unexpected path: {archive}")
        archive.mkdir(parents=True, exist_ok=False)
        source = self.workspace / ".timechain"
        if source.exists():
            shutil.copytree(source, archive / ".timechain")
        return archive

    def rewind_to_ring(self, ring_number: int) -> dict[str, Any]:
        self.reload_agent()
        target = next((ring for ring in self.agent.chain if int(getattr(ring, "n", -1)) == int(ring_number)), None)
        if target is None:
            raise ValueError(f"Unknown ring: {ring_number}")
        archive = self.archive_active_timechain(label=f"rewind-to-{ring_number}")
        kept = [ring for ring in self.agent.chain if int(getattr(ring, "n", -1)) <= int(ring_number)]
        chain_path = self.workspace / ".timechain" / "chain.jsonl"
        chain_path.parent.mkdir(parents=True, exist_ok=True)
        chain_path.write_text(
            "".join(json.dumps(ring.to_dict(), ensure_ascii=False) + "\n" for ring in kept),
            encoding="utf-8",
        )
        config_path = self.workspace / ".timechain" / "config.json"
        if config_path.exists():
            config = json.loads(config_path.read_text(encoding="utf-8"))
            cache = config.get("skill_cache", {})
            if isinstance(cache, dict):
                for domain, entries in list(cache.items()):
                    if not isinstance(entries, dict):
                        continue
                    cache[domain] = {
                        key: value for key, value in entries.items()
                        if isinstance(value, dict) and int(value.get("ring", 0) or 0) <= int(ring_number)
                    }
            config["skill_cache"] = cache
            config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
        model_path = self.root_workspace if self.workspace.resolve() == self.root_workspace.resolve() else self.workspace
        model = prune_memory_model_to_ring(load_memory_model(model_path), int(ring_number))
        save_memory_model(model_path, model)
        self.reload_agent()
        ok, status = self.timechain.verify_chain(self.agent.chain)
        return {
            "session": self.active_session,
            "archive": str(archive),
            "rings": len(self.agent.chain),
            "rewound_to": int(ring_number),
            "verify_ok": ok,
            "verify_status": status,
        }

    def reset_chain(self) -> dict[str, Any]:
        root = (self.workspace / ".timechain").resolve()
        workspace = self.workspace.resolve()
        if workspace not in root.parents:
            raise RuntimeError(f"Refusing to reset unexpected path: {root}")
        metadata = load_session_metadata(self.workspace)
        if root.exists():
            shutil.rmtree(root)
        self.reload_agent()
        if metadata:
            save_session_metadata(self.workspace, metadata)
        self.save_memory_model(empty_memory_model())
        return {
            "workspace": str(self.workspace),
            "rings": len(self.agent.chain),
            "genesis_hash": self.agent.genesis_hash,
        }

    def explain_guide_topic(self, topic_id: str, *, model: str, api_key: str, provider: str = "", base_url: str = "") -> dict[str, Any]:
        topic = get_guide_topic(topic_id)
        source_bundle = build_guide_source_bundle(topic, self.root_workspace)
        messages = build_guide_explainer_messages(topic, source_bundle)
        key = api_key or self.api_key
        provider = (provider or self.provider).strip().lower()
        base_url = (base_url or self.base_url).strip()
        provider_error = ""
        if key:
            try:
                llm = active_call_llm(
                    provider=provider,
                    api_key=key,
                    model=model or self.default_model,
                    messages=messages,
                    timeout=self.timeout,
                    base_url=base_url,
                    max_tokens=response_token_budget(f"Explain {topic['title']}"),
                )
                content = llm["content"]
                model_used = llm.get("model_used", model or self.default_model)
            except RuntimeError as exc:
                provider_error = str(exc)
                content = deterministic_guide_explanation(topic, source_bundle, provider_error=provider_error)
                model_used = "local-source-summary"
        else:
            content = deterministic_guide_explanation(topic, source_bundle)
            model_used = "local-source-summary"

        session = self.create_session(f"Explain: {topic['title']}")
        query = f"Explain guide topic: {topic['title']}"
        result = self.agent.interact(
            query,
            domain="architecture",
            tags=["guide-explain", topic["id"], "source-grounded"],
            override_content=content,
        )
        return {
            "topic": {"id": topic["id"], "title": topic["title"]},
            "session": session,
            "accepted": bool(result.get("accepted")),
            "ring": result.get("ring"),
            "content": content,
            "model_used": model_used,
            "provider_error": provider_error,
            "sources": source_bundle,
            "reason": result.get("reason", ""),
        }

    def generate_llm_response(
        self,
        *,
        query: str,
        domain: str,
        persona_id: str,
        custom_persona: dict[str, str] | None,
        model: str,
        api_key: str,
        provider: str = "",
        base_url: str = "",
    ) -> dict[str, Any]:
        persona_id = self.bind_session_persona(persona_id)
        persona = custom_persona or self.get_custom_persona(persona_id) or PERSONAS.get(persona_id) or PERSONAS["companion"]
        memory_model = self.memory_model()
        durable_hits = recall_memory_facts(memory_model, query, limit=16, session_id=self.active_session)
        active_chain = active_recall_chain(self.agent.chain)
        retrieved_scored = self.timechain.retrieve(
            active_chain,
            query,
            domain=domain,
            cphy_weights=self.agent.cphy_weights,
            config=self.timechain.RetrieverConfig(limit=12),
        )
        retrieved = [ring for _, ring in retrieved_scored]
        recent_turns = build_recent_turns(self.agent.chain, limit=8)
        neuro = self.timechain.compute_neuro(self.agent.chain, domain)
        messages = build_messages(
            persona=persona,
            query=query,
            retrieved=retrieved,
            durable_memories=durable_hits,
            recent_turns=recent_turns,
            neuro=neuro,
            covenant=self.agent.values,
            model=model or self.default_model,
        )
        key = api_key or self.api_key
        provider = (provider or self.provider).strip().lower()
        base_url = (base_url or self.base_url).strip()
        def local_fallback(provider_error: str = "") -> dict[str, Any]:
            fallback = self.timechain._default_generator(query, retrieved, neuro)
            retry_reason = memory_retry_reason(query, fallback, durable_hits, persona["name"])
            local_repair = local_memory_answer(query, durable_hits, persona["name"]) if retry_reason else ""
            if local_repair:
                fallback = local_repair
            result = {
                "content": fallback,
                "model_used": "local-default-generator",
                "usage": {},
                "retrieved": [ring.n for ring in retrieved],
                "memory_hits": durable_hits,
                "memory_candidates": [],
                "retry": {"attempted": bool(local_repair), "reason": retry_reason},
                "persona": persona,
            }
            if provider_error:
                result["provider_error"] = provider_error
            return result

        if not key:
            return local_fallback()
        try:
            llm = active_call_llm(
                provider=provider,
                api_key=key,
                model=model or self.default_model,
                messages=messages,
                timeout=self.timeout,
                base_url=base_url,
                max_tokens=response_token_budget(query),
            )
        except RuntimeError as exc:
            return local_fallback(str(exc))
        retry_reason = memory_retry_reason(query, llm.get("content", ""), durable_hits, persona["name"])
        retry = {"attempted": False, "reason": retry_reason}
        if retry_reason:
            try:
                repaired = active_call_llm(
                    provider=provider,
                    api_key=key,
                    model=model or self.default_model,
                    messages=build_retry_messages(messages, reason=retry_reason, facts=durable_hits),
                    timeout=self.timeout,
                    base_url=base_url,
                    max_tokens=response_token_budget(query),
                )
                llm = repaired
                retry["attempted"] = True
            except RuntimeError as exc:
                llm["provider_error"] = str(exc)
        llm["memory_candidates"] = generate_llm_memory_candidates(
            provider=provider,
            api_key=key,
            model=model or self.default_model,
            query=query,
            content=str(llm.get("content", "")),
            persona_name=persona["name"],
            timeout=self.timeout,
            base_url=base_url,
        )
        llm["retrieved"] = [ring.n for ring in retrieved]
        llm["memory_hits"] = durable_hits
        llm["retry"] = retry
        llm["persona"] = persona
        return llm

def finalize_chat_response(
    *,
    app: App,
    message: str,
    domain: str,
    tags: list[str],
    model: str,
    llm: dict[str, Any],
    persona_name: str,
) -> dict[str, Any]:
    provider_error = llm.get("provider_error", "")
    if provider_error:
        return {
            "ok": True,
            "accepted": False,
            "reason": "provider_error",
            "brightness": 0,
            "scores": {},
            "content": llm.get("content", ""),
            "model": model,
            "model_used": llm.get("model_used"),
            "provider_error": provider_error,
            "retrieved": llm.get("retrieved", []),
            "memory_hits": llm.get("memory_hits", []),
            "retry": llm.get("retry", {"attempted": False, "reason": ""}),
            "usage": llm.get("usage", {}),
            "persona_name": persona_name,
            "domain": domain,
        }

    result = app.agent.interact(
        message,
        domain=domain,
        tags=tags,
        override_content=llm["content"],
    )
    if not result.get("accepted"):
        return {
            "ok": True,
            "accepted": False,
            "reason": result.get("reason"),
            "brightness": result.get("brightness"),
            "scores": result.get("scores"),
            "content": llm["content"],
            "model": model,
            "model_used": llm.get("model_used"),
            "provider_error": "",
            "persona_name": persona_name,
            "domain": domain,
        }

    ring = result["ring"]
    staged = app.queue_memory_candidates(
        SimpleNamespace(**ring),
        persona_name=persona_name,
        llm_candidates=llm.get("memory_candidates", []),
    )
    return {
        "ok": True,
        "accepted": True,
        "content": ring.get("content", ""),
        "ring": ring.get("n"),
        "hash": ring.get("hash"),
        "hash_prefix": str(ring.get("hash", ""))[:16],
        "brightness": round(float(result.get("brightness", 0)), 3),
        "scores": result.get("scores"),
        "retrieved": llm.get("retrieved", result.get("retrieved")),
        "memory_hits": llm.get("memory_hits", []),
        "memory_extracted": staged,
        "memory_pending": [memory for memory in staged if memory.get("status") == "pending"],
        "retry": llm.get("retry", {"attempted": False, "reason": ""}),
        "epistemic": result.get("epistemic"),
        "cache_hit": result.get("cache_hit"),
        "model": model,
        "model_used": llm.get("model_used"),
        "provider_error": "",
        "usage": llm.get("usage", {}),
        "persona_name": persona_name,
        "domain": domain,
    }
