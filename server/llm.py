"""Prompt building, memory context, serialization, LLM calls, and image generation."""

from __future__ import annotations

import base64
import datetime as dt
import json
import os
import pathlib
import re
import time
import urllib.error
import urllib.request
import uuid
from types import SimpleNamespace
from typing import Any

from server.config import (
    DEFAULT_MODEL, DEFAULT_PROVIDER, PROVIDERS, IMAGE_PROVIDERS, PERSONAS, DOMAIN_KEYWORDS,
    RECALLED_RING_SNIPPET_CHARS, TRIMMED_RECALLED_RING_SNIPPET_CHARS,
    PROMPT_BUDGET_CHARS, MIN_COMPACTED_PERSONA_CHARS,
    DEFAULT_RESPONSE_TOKENS, LONG_RESPONSE_TOKENS,
    ACTIVE_CONTEXT_DAYS, SESSION_PAUSE_NOTICE_DAYS,
    default_provider_url, resolve_chat_completions_url,
)

MEMORY_ACCEPTED_STATUSES = {"accepted", "known", "uncertain"}
FRAME_DECLARATION_START = "[CT_FRAME_DECLARATION]"
FRAME_DECLARATION_END = "[/CT_FRAME_DECLARATION]"
RUNTIME_PROFILE_STANDARD = "standard_enhanced"
RUNTIME_PROFILE_CYPHERTEMPRE = "cyphertempre_full"


def resolve_runtime_options(
    persona_id: str = "",
    persona: dict[str, Any] | None = None,
    runtime_profile: str | None = None,
) -> dict[str, Any]:
    """Return safe prompt/runtime capabilities for a selected persona."""
    persona = persona or {}
    profile = str(runtime_profile or persona.get("runtime_profile", "") or "").strip()
    system = str(persona.get("system", "") or "")
    is_cyphertempre = (
        profile == RUNTIME_PROFILE_CYPHERTEMPRE
        or sanitize_session_id(persona_id or "") == "openclaw"
        or "Cypher Tempre Prompt-Layer Runtime" in system
    )
    if is_cyphertempre:
        profile = RUNTIME_PROFILE_CYPHERTEMPRE
    else:
        profile = RUNTIME_PROFILE_STANDARD
    return {
        "runtime_profile": profile,
        "enhanced_thinking": True,
        "requires_high_context": profile == RUNTIME_PROFILE_CYPHERTEMPRE,
        "supports_cambium_training": profile == RUNTIME_PROFILE_CYPHERTEMPRE,
        "include_cyphertempre_runtime": profile == RUNTIME_PROFILE_CYPHERTEMPRE,
    }


def safe_persona_metadata(persona_id: str, persona: dict[str, Any]) -> dict[str, Any]:
    options = resolve_runtime_options(persona_id, persona)
    return {
        "name": persona.get("name", "Untitled"),
        "domain": persona.get("domain", "auto"),
        "runtime_profile": options["runtime_profile"],
        "enhanced_thinking": options["enhanced_thinking"],
        "requires_high_context": options["requires_high_context"],
    }


def extract_frame_declaration(content: str) -> tuple[str, dict[str, Any] | None]:
    """Extract a hidden frame declaration sidecar from assistant content."""
    text = str(content or "")
    pattern = re.compile(
        rf"{re.escape(FRAME_DECLARATION_START)}\s*(.*?)\s*{re.escape(FRAME_DECLARATION_END)}",
        re.I | re.S,
    )
    match = pattern.search(text)
    if not match:
        return text.strip(), None

    visible = (text[:match.start()] + text[match.end():]).strip()
    raw = match.group(1).strip()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return visible, None
    if not isinstance(parsed, dict):
        return visible, None

    declaration: dict[str, Any] = {}
    for key in (
        "current_frame",
        "reason",
        "cambium_proposal",
        "cambium_definition",
    ):
        value = parsed.get(key)
        if isinstance(value, str):
            declaration[key] = value.strip()
    if isinstance(parsed.get("frame_adequate"), bool):
        declaration["frame_adequate"] = parsed["frame_adequate"]
    elif isinstance(parsed.get("frame_adequate"), str):
        lowered = parsed["frame_adequate"].strip().lower()
        if lowered in {"true", "false"}:
            declaration["frame_adequate"] = lowered == "true"
    return visible, declaration or None

def sanitize_session_id(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "-", value.strip())[:80].strip("-")
    return cleaned or "default"

def _clean_fact_value(value: str, *, max_words: int = 12) -> str:
    cleaned = re.sub(r"\s+", " ", value or "").strip(" .,!?:;\"'")
    words = cleaned.split()
    return " ".join(words[:max_words]).strip(" .,!?:;\"'")

def _parse_iso_datetime(value: Any) -> dt.datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        parsed = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)

def _age_days(value: Any, *, now: dt.datetime | None = None) -> int | None:
    parsed = _parse_iso_datetime(value)
    if not parsed:
        return None
    current = now or dt.datetime.now(dt.timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=dt.timezone.utc)
    delta = current.astimezone(dt.timezone.utc) - parsed
    return max(0, delta.days)

def memory_activity(fact: dict[str, Any], *, now: dt.datetime | None = None) -> dict[str, Any]:
    status = str(fact.get("status", "known"))
    if status not in MEMORY_ACCEPTED_STATUSES:
        return {"active": False, "age_days": None, "stale_reason": f"status={status}"}
    kind = str(fact.get("kind", "")).lower()
    days = _age_days(fact.get("updated_at") or fact.get("created_at"), now=now)
    if kind in {"identity", "boundary", "persona"}:
        return {"active": True, "age_days": days, "stale_reason": ""}
    if days is not None and days > ACTIVE_CONTEXT_DAYS:
        return {"active": False, "age_days": days, "stale_reason": f"older than {ACTIVE_CONTEXT_DAYS} days"}
    return {"active": True, "age_days": days, "stale_reason": ""}

def recall_memory_facts(
    model: dict[str, Any],
    query: str,
    *,
    limit: int = 16,
    session_id: str = "default",
    now: dt.datetime | None = None,
    active_only: bool = True,
) -> list[dict[str, Any]]:
    query_tokens = set(re.findall(r"[A-Za-z0-9_-]+", query.lower()))
    wants_name = bool(re.search(r"\b(?:my name|call me|who am i|what is my name)\b", query, re.I))
    wants_persona = bool(re.search(r"\b(?:who are you|your name|what is your name)\b", query, re.I))
    active_session = sanitize_session_id(session_id or "default")
    scored: list[tuple[float, dict[str, Any]]] = []
    for fact in model.get("facts", []):
        status = str(fact.get("status", "known"))
        if status not in MEMORY_ACCEPTED_STATUSES:
            continue
        activity = memory_activity(fact, now=now)
        if active_only and not activity["active"]:
            continue
        scope = str(fact.get("scope", "global"))
        if scope == "session" and str(fact.get("session_id", "")) not in {"", active_session}:
            continue
        fact_text = f"{fact.get('key', '')} {fact.get('value', '')} {fact.get('kind', '')}".lower()
        fact_tokens = set(re.findall(r"[A-Za-z0-9_-]+", fact_text))
        overlap = len(query_tokens & fact_tokens) / max(1, len(query_tokens))
        score = overlap + float(fact.get("confidence", 0.0))
        if scope == "global":
            score += 0.1
        if scope == "session":
            score += 0.35
        if wants_name and fact.get("key") == "user.name":
            score += 2.0
        if wants_persona and fact.get("key") == "assistant.persona_name":
            score += 1.4
        if status == "uncertain" or fact.get("kind") == "uncertainty":
            score -= 0.25
        if score > 0.3:
            hit = dict(fact)
            hit.update(activity)
            hit["score"] = round(score, 4)
            scored.append((score, hit))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [fact for _, fact in scored[: max(1, min(limit, 20))]]

def build_memory_fact_context(facts: list[dict[str, Any]] | None) -> str:
    active_facts = [
        fact for fact in (facts or [])
        if str(fact.get("status", "known")) in MEMORY_ACCEPTED_STATUSES
    ]
    if not active_facts:
        return "No durable memories matched this query."
    lines = []
    for fact in active_facts[:16]:
        status = fact.get("status", "known")
        key = fact.get("key", "memory")
        value = fact.get("value", "")
        confidence = float(fact.get("confidence", 0.0))
        source = fact.get("source_ring", "?")
        scope = str(fact.get("scope", "")).strip().lower()
        if scope == "global":
            prefix = "Global"
        elif scope == "session":
            prefix = "Session"
        else:
            prefix = "Uncertain" if status == "uncertain" else "Known"
        lines.append(f"- {prefix} {key}: {value} (confidence={confidence:.2f}, source ring #{source})")
    return "\n".join(lines)

def memory_retry_reason(query: str, content: str, facts: list[dict[str, Any]] | None, persona_name: str) -> str:
    answer = (content or "").strip()
    if not answer:
        return "The model returned an empty answer."
    facts = facts or []
    name_fact = next((fact for fact in facts if fact.get("key") == "user.name" and fact.get("status") == "known"), None)
    if name_fact and re.search(r"\b(?:my name|what is my name|who am i)\b", query, re.I):
        value = str(name_fact.get("value", "")).strip()
        if value and value.lower() not in answer.lower():
            return f"The answer missed the known user.name durable memory: {value}."
    if re.search(r"\b(?:who are you|what is your name|your name)\b", query, re.I):
        persona = persona_name.strip()
        if persona and persona.lower() not in answer.lower():
            return f"The answer missed the active persona name: {persona}."
    if "i don't know" in answer.lower() and facts:
        return "The answer claimed memory was absent even though durable memory hits were available."
    return ""

def local_memory_answer(query: str, facts: list[dict[str, Any]], persona_name: str) -> str:
    name_fact = next((fact for fact in facts if fact.get("key") == "user.name" and fact.get("status") == "known"), None)
    if name_fact and re.search(r"\b(?:my name|what is my name|who am i)\b", query, re.I):
        return f"Your name is {name_fact['value']}."
    persona_fact = next((fact for fact in facts if fact.get("key") == "assistant.persona_name" and fact.get("status") == "known"), None)
    if re.search(r"\b(?:who are you|what is your name|your name)\b", query, re.I):
        return f"I am {persona_fact.get('value') if persona_fact else persona_name}."
    return ""

def build_retry_messages(
    messages: list[dict[str, str]],
    *,
    reason: str,
    facts: list[dict[str, Any]],
) -> list[dict[str, str]]:
    retry = list(messages)
    has_system = any(m.get("role") == "system" for m in retry)
    instruction = (
        "Repair the previous answer. The prior response failed this requirement: "
        f"{reason}\nUse these durable memories as higher priority than ordinary chat text:\n"
        f"{build_memory_fact_context(facts)}"
    )
    retry.insert(1, {
        "role": "system" if has_system else "user",
        "content": instruction,
    })
    return retry

def parse_memory_candidate_json(content: str) -> list[dict[str, Any]]:
    text = (content or "").strip()
    if not text:
        return []
    if "```" in text:
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I).strip()
        text = re.sub(r"\s*```$", "", text).strip()
    start = text.find("[")
    end = text.rfind("]")
    if start >= 0 and end > start:
        text = text[start:end + 1]
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, list):
        return []
    return [item for item in parsed if isinstance(item, dict)][:6]

def build_memory_candidate_messages(query: str, content: str, persona_name: str) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "Extract only stable user-continuity memories from this exchange. "
                "Return JSON only: an array of objects with scope, kind, key, value, confidence, evidence. "
                "Allowed scopes: global, session. Allowed kinds: identity, preference, goal, correction, boundary, style, uncertainty. "
                "Use global for stable identity/preferences/style/boundaries. Use session for temporary goals or local conversation context. "
                "Do not invent facts. Return [] if there is nothing worth remembering."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Active persona: {persona_name}\n"
                f"User message:\n{query}\n\n"
                f"Assistant response:\n{content}"
            ),
        },
    ]

def generate_llm_memory_candidates(
    *,
    provider: str,
    api_key: str,
    model: str,
    query: str,
    content: str,
    persona_name: str,
    timeout: float,
    base_url: str = "",
) -> list[dict[str, Any]]:
    if not api_key.strip() or not query.strip() or not content.strip():
        return []
    try:
        result = call_llm(
            provider=provider,
            api_key=api_key,
            model=model,
            messages=build_memory_candidate_messages(query, content, persona_name),
            timeout=min(timeout, 20.0),
            base_url=base_url,
            max_tokens=500,
        )
    except RuntimeError:
        return []
    return parse_memory_candidate_json(str(result.get("content", "")))

def generate_persona_from_seed(name: str, seed: str) -> dict[str, str]:
    persona_name = _clean_fact_value(name, max_words=4)
    if not persona_name:
        raise ValueError("Persona name is required.")
    style = _clean_fact_value(seed, max_words=40) or "warm, practical, observant conversational partner"
    system = (
        f"You are {persona_name}, a fictional AI persona inspired by this vibe: {style}. "
        "Do not claim to be, impersonate, or have a personal relationship with any real public figure. "
        "Communicate in clear English with a consistent, grounded voice. "
        "Be helpful and specific. Remember useful user preferences through the CypherTempre memory flow."
    )
    return {"name": persona_name[:80], "domain": "auto", "system": system}

def parse_ring_time(value: Any) -> dt.datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = dt.datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)

def relative_time_label(value: Any, *, now: dt.datetime | None = None) -> str:
    ring_time = parse_ring_time(value)
    if ring_time is None:
        return "time unknown"
    current = now or dt.datetime.now(dt.timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=dt.timezone.utc)
    current = current.astimezone(dt.timezone.utc)
    seconds = int((current - ring_time).total_seconds())
    tense = "ago"
    if seconds < 0:
        seconds = abs(seconds)
        tense = "from now"
    if seconds < 60:
        amount, unit = max(0, seconds), "second"
    elif seconds < 3600:
        amount, unit = seconds // 60, "minute"
    elif seconds < 86400:
        amount, unit = seconds // 3600, "hour"
    else:
        amount, unit = seconds // 86400, "day"
    suffix = "" if amount == 1 else "s"
    return f"{amount} {unit}{suffix} {tense}"

def utc_offset_label(value: dt.datetime) -> str:
    offset = value.utcoffset()
    if offset is None:
        return "UTC offset unknown"
    minutes = int(offset.total_seconds() // 60)
    sign = "+" if minutes >= 0 else "-"
    minutes = abs(minutes)
    hours, remainder = divmod(minutes, 60)
    return f"UTC{sign}{hours:02d}:{remainder:02d}"

def current_time_context(now: dt.datetime) -> str:
    if now.tzinfo is None:
        now = now.replace(tzinfo=dt.timezone.utc)
    utc_now = now.astimezone(dt.timezone.utc)
    local_now = utc_now.astimezone()
    local_label = local_now.strftime("%H:%M")
    utc_label = utc_now.strftime("%A %Y-%m-%d %H:%MZ")
    return (
        f"Current date/time context: UTC {utc_label}; local {local_label} {utc_offset_label(local_now)}. "
        "authoritative now for rel dates unless user/memory gives date/TZ; "
        "convert explicit times; note missing TZ."
    )

def build_memory_context(
    rings: list[Any],
    *,
    now: dt.datetime | None = None,
    snippet_limit: int = RECALLED_RING_SNIPPET_CHARS,
) -> str:
    if not rings:
        return "No prior relevant rings."
    lines = []
    for ring in rings[:12]:
        content = ring.content.strip().replace("\n", " ")
        if len(content) > snippet_limit:
            content = content[: max(0, snippet_limit - 3)].rstrip() + "..."
        label = relative_time_label(getattr(ring, "ts", ""), now=now)
        days = _age_days(getattr(ring, "ts", ""), now=now)
        if days is not None and days > ACTIVE_CONTEXT_DAYS:
            label = f"{label}, revived older memory"
        lines.append(
            f"- Ring #{ring.n} [{ring.domain}, brightness={ring.brightness:.3f}, "
            f"epistemic={ring.epistemic}, {label}]: {content}"
        )
    return "\n".join(lines)


def build_shared_memory_context(hits: list[dict[str, Any]] | None) -> str:
    if not hits:
        return ""
    lines = []
    for hit in (hits or [])[:8]:
        content = str(hit.get("content", "")).strip().replace("\n", " ")
        if len(content) > RECALLED_RING_SNIPPET_CHARS:
            content = content[: RECALLED_RING_SNIPPET_CHARS - 3].rstrip() + "..."
        lines.append(
            f"- [{hit.get('domain', '?')}, brightness={hit.get('brightness', 0):.3f}, "
            f"session={hit.get('source_session', '?')}, ring={hit.get('source_ring', '?')}]: {content}"
        )
    return "Shared memory from other sessions:\n" + "\n".join(lines)

def trim_for_prompt(text: str, limit: int = 1400) -> str:
    normalized = (text or "").strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."

def compact_persona_system(system: str, limit: int) -> str:
    text = (system or "").strip()
    if limit <= 0 or len(text) <= limit:
        return text
    limit = max(200, limit)
    marker = (
        "\n\n[OpenClaw prompt compacted to fit provider context. Preserve identity, truth constraint, "
        "Timechain orientation, PoQ discipline, correction lineage, and practical usefulness.]\n\n"
    )
    final_index = text.rfind("FINAL ACTIVATION")
    if "Cypher Tempre Prompt-Layer Runtime" in text and final_index > 0:
        head_budget = max(400, int((limit - len(marker)) * 0.62))
        tail_budget = max(300, limit - len(marker) - head_budget)
        compacted = text[:head_budget].rstrip() + marker + text[final_index: final_index + tail_budget].strip()
    else:
        head_budget = max(100, limit - len(marker) - 3)
        compacted = text[:head_budget].rstrip() + marker.rstrip()
    if len(compacted) > limit:
        compacted = compacted[: limit - 3].rstrip() + "..."
    return compacted

def build_recent_turns(chain: list[Any], limit: int = 8) -> list[dict[str, str]]:
    interactions = [ring for ring in chain if getattr(ring, "kind", "") == "interaction"]
    selected = interactions[-max(0, min(limit, 20)):]
    turns: list[dict[str, str]] = []
    for ring in selected:
        timestamp = str(getattr(ring, "ts", "") or "")
        user_turn = {"role": "user", "content": trim_for_prompt(ring.query)}
        assistant_turn = {"role": "assistant", "content": trim_for_prompt(ring.content)}
        if timestamp:
            user_turn["ts"] = timestamp
            assistant_turn["ts"] = timestamp
        turns.append(user_turn)
        turns.append(assistant_turn)
    return turns

def prompt_size(messages: list[dict[str, str]]) -> int:
    return sum(len(message.get("role", "")) + len(message.get("content", "")) for message in messages)

def response_token_budget(query: str) -> int:
    text = (query or "").lower()
    if re.search(r"\b(lengthy|long|comprehensive|detailed|deep dive|in depth|in-depth)\b", text):
        return LONG_RESPONSE_TOKENS
    return DEFAULT_RESPONSE_TOKENS

def build_prompt_messages(
    *,
    persona: dict[str, str],
    query: str,
    durable_context: str,
    memory_context: str,
    recent_turns: list[dict[str, str]],
    neuro_line: str,
    covenant: str,
    now: dt.datetime,
    model: str = "",
    temporal_context: str = "",
    shared_memory_context: str = "",
    lattice: dict[str, Any] | None = None,
    include_frame_declaration_instruction: bool = True,
    runtime_options: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    pause_note = ""
    for turn in reversed(recent_turns):
        parsed = parse_ring_time(turn.get("ts", ""))
        if parsed is None:
            continue
        days = _age_days(parsed.isoformat(), now=now)
        if days is not None and days >= SESSION_PAUSE_NOTICE_DAYS:
            pause_note = (
                f"\n\nUser may be returning after a pause: last interaction was "
                f"{relative_time_label(parsed.isoformat(), now=now)}. "
                "Prefer a brief continuity check before assuming current intent."
            )
        break
    runtime_options = runtime_options or resolve_runtime_options(persona=persona)
    cyphertempre_runtime = bool(runtime_options.get("include_cyphertempre_runtime"))
    temporal_line = f"{temporal_context}\n\n" if temporal_context and cyphertempre_runtime else ""
    shared_block = f"{shared_memory_context}\n\n" if shared_memory_context else ""
    lattice_block = ""
    if lattice:
        planes = ", ".join(lattice.get("planes", [])[:5])
        top_fields = sorted(
            (lattice.get("fields") or {}).items(),
            key=lambda x: x[1], reverse=True,
        )[:3]
        fields_str = ", ".join(f"{k}={v:.2f}" for k, v in top_fields)
        dim_summary = []
        for dim, vals in (lattice.get("perception") or {}).items():
            if vals:
                avg = sum(vals) / len(vals)
                dim_summary.append(f"{dim[:3]}:{avg:.2f}")
        lattice_block = (
            f"[Lattice: planes={planes} | fields={fields_str} | dims={'; '.join(dim_summary)}]\n\n"
        )
    frame_declaration_instruction = (
        "Only for genuine Cambium frame shifts, attach hidden metadata outside visible text: "
        f'{FRAME_DECLARATION_START}{{"current_frame":"","frame_adequate":false,"reason":"","cambium_proposal":"","cambium_definition":""}}{FRAME_DECLARATION_END} '
        "The answer must use the new frame.\n\n"
        if include_frame_declaration_instruction and cyphertempre_runtime
        else ""
    )
    if cyphertempre_runtime:
        system_text = (
            f"{persona['system']}\n\n"
            "You are connected to a local CypherTempre Timechain. "
            "Use recalled rings as memory, but distinguish memory from fresh inference. "
            "Continue the current conversation naturally using the recent turns. "
            "If asked who you are, answer as the selected persona, not as the underlying model or provider. "
            "Be conversational and useful. Do not expose hidden reasoning. "
            "If memory is weak or absent, say so briefly.\n\n"
            f"{frame_declaration_instruction}"
            f"Engineering covenant: {covenant}\n\n"
            f"{current_time_context(now)}{pause_note}\n\n"
            f"{lattice_block}"
            f"{temporal_line}"
            f"Durable memories:\n{durable_context}\n\n"
            f"Relevant recalled rings:\n{memory_context}\n\n"
            f"{shared_block}"
            f"Current neuro-state: {neuro_line}"
        )
    else:
        standard_memory_context = re.sub(r"\bRing #", "Memory #", memory_context)
        system_text = (
            f"{persona['system']}\n\n"
            "Use the selected persona's voice. Use recalled context when relevant, "
            "but distinguish memory from fresh inference. If asked who you are, answer as the selected persona. "
            "Quiet thinking support: choose an appropriate approach, be clear about uncertainty, "
            "correct conflicts, and do not expose hidden reasoning.\n\n"
            f"{current_time_context(now)}{pause_note}\n\n"
            f"Durable memories:\n{durable_context}\n\n"
            f"Relevant recalled context:\n{standard_memory_context}\n\n"
            f"{shared_block}".rstrip()
        )
    model_id = (model or "").lower()
    is_gemma = "gemma" in model_id
    messages: list[dict[str, str]] = []
    if is_gemma:
        # Gemma via Google AI Studio does not support system/developer instructions.
        # Inject system context as a user message before the conversation.
        messages.append({"role": "user", "content": f"[System Instruction]\n{system_text}\n\nAcknowledge these instructions."})
        messages.append({"role": "assistant", "content": "Understood. I will follow these instructions."})
    else:
        messages.append({"role": "system", "content": system_text})
    messages.extend(
        {"role": turn.get("role", "user"), "content": turn.get("content", "")}
        for turn in recent_turns
    )
    messages.append({"role": "user", "content": query})
    return messages

def serialize_history(chain: list[Any], limit: int = 80) -> list[dict[str, Any]]:
    interactions = [ring for ring in chain if getattr(ring, "kind", "") == "interaction"]
    selected = interactions[-max(1, min(limit, 200)):]
    history: list[dict[str, Any]] = []
    for ring in selected:
        history.append({
            "role": "user",
            "content": ring.query,
            "domain": ring.domain,
            "ring": ring.n,
            "ts": ring.ts,
        })
        history.append({
            "role": "assistant",
            "content": ring.content,
            "domain": ring.domain,
            "ring": ring.n,
            "ts": ring.ts,
            "brightness": round(float(ring.brightness), 3),
            "epistemic": ring.epistemic,
            "hash_prefix": ring.hash[:16],
        })
    return history

def serialize_ring(ring: Any, *, content_limit: int = 700) -> dict[str, Any]:
    content = str(getattr(ring, "content", "") or "")
    query = str(getattr(ring, "query", "") or "")
    return {
        "n": int(getattr(ring, "n", 0) or 0),
        "ts": str(getattr(ring, "ts", "") or ""),
        "kind": str(getattr(ring, "kind", "") or ""),
        "domain": str(getattr(ring, "domain", "") or ""),
        "query": query[:content_limit],
        "content": content[:content_limit],
        "brightness": round(float(getattr(ring, "brightness", 0) or 0), 3),
        "epistemic": str(getattr(ring, "epistemic", "") or ""),
        "tags": list(getattr(ring, "tags", []) or []),
        "retrieved": list(getattr(ring, "retrieved", []) or []),
        "refs": list(getattr(ring, "refs", []) or []),
        "supersedes": getattr(ring, "supersedes", None),
        "importance": round(float(getattr(ring, "importance", 0) or 0), 3),
        "hash_prefix": str(getattr(ring, "hash", "") or "")[:16],
        "prev_prefix": str(getattr(ring, "prev", "") or "")[:16],
        "scores": {
            str(key): round(float(value), 3)
            for key, value in dict(getattr(ring, "scores", {}) or {}).items()
        },
        "perception": dict(getattr(ring, "perception", {}) or {}),
        "fields": {
            str(key): round(float(value), 3)
            for key, value in dict(getattr(ring, "fields", {}) or {}).items()
        },
        "planes": list(getattr(ring, "planes", []) or []),
    }

def serialize_rings(chain: list[Any], limit: int = 24) -> list[dict[str, Any]]:
    selected = chain[-max(1, min(limit, 100)):]
    return [serialize_ring(ring) for ring in reversed(selected)]

def serialize_cambium_report(report: Any) -> dict[str, Any]:
    gaps = [
        {"domain": str(domain), "mean_brightness": round(float(score), 4)}
        for domain, score in list(getattr(report, "gaps", []) or [])
    ]
    consolidations = [str(domain) for domain in list(getattr(report, "consolidations", []) or [])]
    proposals = list(getattr(report, "proposals", []) or [])
    return {
        "gaps": gaps,
        "consolidations": consolidations,
        "proposals": proposals,
        "proposal_count": len(proposals),
        "gap_count": len(gaps),
        "consolidation_count": len(consolidations),
    }

def build_sync_snapshot(
    *,
    session_id: str,
    workspace: pathlib.Path,
    self_model: dict[str, Any],
    rings: list[dict[str, Any]],
    memories: dict[str, Any],
    cambium: dict[str, Any],
    verify_status: str,
) -> str:
    recent = rings[:8]
    accepted = list(memories.get("accepted", []) or [])[:8]
    pending = list(memories.get("pending", []) or [])[:8]
    top_domains = ", ".join(self_model.get("top_domains", []) or []) or "(none)"
    ring_lines = [
        f"- #{ring['n']} {ring['kind']} {ring['domain']} brightness={ring['brightness']} epistemic={ring['epistemic']}: {ring['query'] or ring['content']}"
        for ring in recent
    ] or ["- (none)"]
    accepted_lines = [
        f"- {fact.get('scope', 'legacy')} {fact.get('key', 'memory')}={fact.get('value', '')} source=#{fact.get('source_ring', '?')}"
        for fact in accepted
    ] or ["- (none)"]
    pending_lines = [
        f"- {fact.get('scope', 'legacy')} {fact.get('key', 'memory')}={fact.get('value', '')} source=#{fact.get('source_ring', '?')}"
        for fact in pending
    ] or ["- (none)"]
    cambium_lines = [
        f"- gap {gap['domain']} mean_brightness={gap['mean_brightness']}"
        for gap in cambium.get("gaps", [])
    ]
    cambium_lines.extend(
        f"- consolidate {domain}" for domain in cambium.get("consolidations", [])
    )
    cambium_lines.extend(
        f"- proposal {proposal.get('proposed_domain', 'unknown')}: {proposal.get('reason', '')}"
        for proposal in cambium.get("proposals", [])[:8]
    )
    if not cambium_lines:
        cambium_lines = ["- (none)"]
    return "\n".join([
        "[CT_SYNC_SNAPSHOT]",
        "Genesis:",
        f"- Agent: {self_model.get('name', 'CypherTempre')}",
        f"- Genesis hash: {self_model.get('genesis_hash', '')}",
        f"- Workspace: {workspace}",
        "Current goal:",
        f"- Continue session '{session_id}' with Timechain continuity visible.",
        "Current state:",
        f"- Rings: {self_model.get('ring_count', 0)}",
        f"- Temporal mass: {self_model.get('temporal_mass', 0)}",
        f"- Top domains: {top_domains}",
        f"- Verify: {verify_status}",
        "Important Rings:",
        *ring_lines,
        "Decisions:",
        "- Use accepted rings and reviewed memories as local continuity context.",
        "Corrections:",
        "- Corrections should supersede prior memories or rings without erasing lineage.",
        "Artifacts:",
        f"- Chain workspace: {workspace / '.timechain'}",
        "Tests and evidence:",
        f"- Chain verification status: {verify_status}",
        "Known facts:",
        *accepted_lines,
        "Inferences:",
        "- Recent rings and Cambium signals indicate the highest-value next context.",
        "Speculation:",
        "- Cambium proposals are growth candidates until accepted by the user.",
        "Risks:",
        "- Pending memories are not trusted for recall until reviewed.",
        "Open loops:",
        *pending_lines,
        "Next steps:",
        *cambium_lines,
        "[/CT_SYNC_SNAPSHOT]",
    ])

def classify_domain(query: str, persona: dict[str, str], requested_domain: str | None) -> str:
    requested = (requested_domain or "").strip()
    if requested and requested.lower() != "auto":
        return requested

    text = f"{query} {persona.get('name', '')} {persona.get('system', '')}".lower()
    scores: dict[str, int] = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        scores[domain] = sum(1 for keyword in keywords if keyword in text)

    best_domain, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score > 0:
        return best_domain
    return persona.get("domain") or "architecture"

def normalize_custom_persona(raw: Any) -> dict[str, str] | None:
    if not isinstance(raw, dict):
        return None
    name = str(raw.get("name", "")).strip()
    system = str(raw.get("system", "")).strip()
    domain = str(raw.get("domain", "architecture")).strip() or "architecture"
    if not name or not system:
        return None
    visibility = str(raw.get("visibility", "private")).strip().lower()
    if visibility not in ("public", "private"):
        visibility = "private"
    return {
        "name": name[:80],
        "domain": domain[:40],
        "system": system[:4000],
        "visibility": visibility,
    }

def build_messages(
    *,
    persona: dict[str, str],
    query: str,
    retrieved: list[Any],
    recent_turns: list[dict[str, str]],
    neuro: dict[str, float],
    covenant: str,
    durable_memories: list[dict[str, Any]] | None = None,
    shared_hits: list[dict[str, Any]] | None = None,
    prompt_budget_chars: int = PROMPT_BUDGET_CHARS,
    now: dt.datetime | None = None,
    model: str = "",
    temporal_context: str = "",
    lattice: dict[str, Any] | None = None,
    runtime_options: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    current_time = now or dt.datetime.now(dt.timezone.utc)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=dt.timezone.utc)
    current_time = current_time.astimezone(dt.timezone.utc)
    memory_context = build_memory_context(retrieved, now=current_time)
    durable_context = build_memory_fact_context(durable_memories)
    shared_memory_context = build_shared_memory_context(shared_hits)
    neuro_line = ", ".join(f"{key}={value:.2f}" for key, value in sorted(neuro.items()))
    active_recent_turns = list(recent_turns)
    runtime_options = runtime_options or resolve_runtime_options(persona=persona)
    include_frame_declaration_instruction = True
    messages = build_prompt_messages(
        persona=persona,
        query=query,
        durable_context=durable_context,
        memory_context=memory_context,
        recent_turns=active_recent_turns,
        neuro_line=neuro_line,
        covenant=covenant,
        now=current_time,
        model=model,
        temporal_context=temporal_context,
        shared_memory_context=shared_memory_context,
        lattice=lattice,
        include_frame_declaration_instruction=include_frame_declaration_instruction,
        runtime_options=runtime_options,
    )
    if prompt_budget_chars > 0 and prompt_size(messages) > prompt_budget_chars:
        include_frame_declaration_instruction = False
        messages = build_prompt_messages(
            persona=persona,
            query=query,
            durable_context=durable_context,
            memory_context=memory_context,
            recent_turns=active_recent_turns,
            neuro_line=neuro_line,
            covenant=covenant,
            now=current_time,
            model=model,
            temporal_context=temporal_context,
            shared_memory_context=shared_memory_context,
            lattice=lattice,
            include_frame_declaration_instruction=include_frame_declaration_instruction,
            runtime_options=runtime_options,
        )
    if prompt_budget_chars > 0 and prompt_size(messages) > prompt_budget_chars and retrieved:
        memory_context = build_memory_context(
            retrieved,
            now=current_time,
            snippet_limit=TRIMMED_RECALLED_RING_SNIPPET_CHARS,
        )
        messages = build_prompt_messages(
            persona=persona,
            query=query,
            durable_context=durable_context,
            memory_context=memory_context,
            recent_turns=active_recent_turns,
            neuro_line=neuro_line,
            covenant=covenant,
            now=current_time,
            model=model,
            shared_memory_context=shared_memory_context,
            lattice=lattice,
            include_frame_declaration_instruction=include_frame_declaration_instruction,
            runtime_options=runtime_options,
        )
    if prompt_budget_chars > 0 and prompt_size(messages) > prompt_budget_chars and retrieved:
        memory_context = f"{len(retrieved[:12])} retrieved rings omitted to preserve prompt budget."
        messages = build_prompt_messages(
            persona=persona,
            query=query,
            durable_context=durable_context,
            memory_context=memory_context,
            recent_turns=active_recent_turns,
            neuro_line=neuro_line,
            covenant=covenant,
            now=current_time,
            model=model,
            shared_memory_context=shared_memory_context,
            lattice=lattice,
            include_frame_declaration_instruction=include_frame_declaration_instruction,
            runtime_options=runtime_options,
        )
    while prompt_budget_chars > 0 and prompt_size(messages) > prompt_budget_chars and active_recent_turns:
        drop_count = 2 if len(active_recent_turns) >= 2 else 1
        active_recent_turns = active_recent_turns[drop_count:]
        messages = build_prompt_messages(
            persona=persona,
            query=query,
            durable_context=durable_context,
            memory_context=memory_context,
            recent_turns=active_recent_turns,
            neuro_line=neuro_line,
            covenant=covenant,
            now=current_time,
            model=model,
            shared_memory_context=shared_memory_context,
            lattice=lattice,
            include_frame_declaration_instruction=include_frame_declaration_instruction,
            runtime_options=runtime_options,
        )
    if prompt_budget_chars > 0 and prompt_size(messages) > prompt_budget_chars:
        overhead = prompt_size(messages) - len(persona.get("system", ""))
        persona_budget = max(MIN_COMPACTED_PERSONA_CHARS, prompt_budget_chars - overhead - 120)
        compacted_persona = {
            **persona,
            "system": compact_persona_system(persona.get("system", ""), persona_budget),
        }
        messages = build_prompt_messages(
            persona=compacted_persona,
            query=query,
            durable_context=durable_context,
            memory_context=memory_context,
            recent_turns=active_recent_turns,
            neuro_line=neuro_line,
            covenant=covenant,
            now=current_time,
            model=model,
            shared_memory_context=shared_memory_context,
            lattice=lattice,
            include_frame_declaration_instruction=include_frame_declaration_instruction,
            runtime_options=runtime_options,
        )
        while prompt_budget_chars > 0 and prompt_size(messages) > prompt_budget_chars and persona_budget > 400:
            persona_budget = max(400, persona_budget - max(200, prompt_size(messages) - prompt_budget_chars + 80))
            compacted_persona["system"] = compact_persona_system(persona.get("system", ""), persona_budget)
            messages = build_prompt_messages(
                persona=compacted_persona,
                query=query,
                durable_context=durable_context,
                memory_context=memory_context,
                recent_turns=active_recent_turns,
                neuro_line=neuro_line,
                covenant=covenant,
                now=current_time,
                model=model,
                shared_memory_context=shared_memory_context,
                lattice=lattice,
                include_frame_declaration_instruction=include_frame_declaration_instruction,
                runtime_options=runtime_options,
            )
    return messages

def call_llm(
    *,
    provider: str,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    timeout: float,
    base_url: str = "",
    max_tokens: int = DEFAULT_RESPONSE_TOKENS,
) -> dict[str, Any]:
    api_key = api_key.strip()
    if not api_key:
        raise RuntimeError("API key is missing. Add a browser key or set API_KEY.")
    if api_key in {"YOUR_API_KEY", "YOUR_MORPHEUS_API_KEY", "YOUR_OPENROUTER_API_KEY", "sk-or-your-key-here", "sk-or-your-real-key"}:
        raise RuntimeError("API key is still the example placeholder.")
    config = PROVIDERS.get(provider, PROVIDERS[DEFAULT_PROVIDER])
    if provider == "other":
        config = {"url": "", "needs_referer": False, "needs_title": False, "label": "Custom"}
    url = resolve_chat_completions_url(provider, base_url)
    payload = {
        "model": model or DEFAULT_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": max(1, min(int(max_tokens or DEFAULT_RESPONSE_TOKENS), 4000)),
    }
    headers: dict[str, str] = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if config.get("needs_referer"):
        headers["HTTP-Referer"] = "http://127.0.0.1:8765"
    if config.get("needs_title"):
        headers["X-Title"] = "CypherTempre Chat PoC"
    last_message = ""
    for attempt in range(3):
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(detail)
                message = parsed.get("error", {}).get("message") or parsed.get("message") or detail
            except json.JSONDecodeError:
                message = detail
            if exc.code == 429:
                message = (
                    f"{message} The selected model is rate-limited or temporarily unavailable. "
                    "Wait and retry, or choose a different model in Settings."
                )
            last_message = message
            if exc.code in {429, 502, 503, 504} and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"{config['label']} HTTP {exc.code}: {message}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"{config['label']} request failed: {exc.reason}") from exc
    else:
        raise RuntimeError(f"{config['label']} request failed after retries: {last_message}")

    choices = body.get("choices") or []
    if not choices:
        raise RuntimeError(f"{config['label']} returned no choices.")
    message = choices[0].get("message") or {}
    content, frame_declaration = extract_frame_declaration(message.get("content") or "")
    if not content:
        raise RuntimeError(f"{config['label']} returned an empty response.")
    result = {
        "content": content,
        "model_used": body.get("model") or model,
        "usage": body.get("usage") or {},
    }
    if frame_declaration:
        result["frame_declaration"] = frame_declaration
    return result

def call_openrouter(
    *,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    timeout: float,
) -> dict[str, Any]:
    """Backward-compatible wrapper that defaults to the openrouter provider."""
    return call_llm(provider="openrouter", api_key=api_key, model=model, messages=messages, timeout=timeout)

def call_image_generation(
    *,
    provider: str,
    api_key: str,
    model: str,
    messages: list[dict[str, Any]],
    timeout: float,
    base_url: str = "",
    modalities: list[str] | None = None,
) -> list[str]:
    """Generate images via a provider that supports image output modalities.

    Returns a list of base64-encoded image data strings (without data URL prefix).
    """
    if api_key in {"YOUR_API_KEY", "YOUR_MORPHEUS_API_KEY", "YOUR_OPENROUTER_API_KEY", "sk-or-your-key-here", "sk-or-your-real-key"}:
        raise RuntimeError("API key is still the example placeholder.")
    config = IMAGE_PROVIDERS.get(provider, IMAGE_PROVIDERS.get("openrouter", {}))
    if provider == "other":
        config = {"url": "", "needs_referer": False, "needs_title": False, "label": "Custom"}
    url = (base_url or config.get("url", "")).rstrip("/")
    if not url:
        raise RuntimeError(f"No URL configured for image provider: {provider}")
    payload: dict[str, Any] = {
        "model": model or config.get("default_model", ""),
        "messages": messages,
    }
    if modalities:
        payload["modalities"] = modalities
    headers: dict[str, str] = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if config.get("needs_referer"):
        headers["HTTP-Referer"] = "http://127.0.0.1:8765"
    if config.get("needs_title"):
        headers["X-Title"] = "CypherTempre Chat PoC"
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(detail)
            message = parsed.get("error", {}).get("message") or parsed.get("message") or detail
        except json.JSONDecodeError:
            message = detail
        raise RuntimeError(f"{config.get('label', provider)} HTTP {exc.code}: {message}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"{config.get('label', provider)} request failed: {exc.reason}") from exc

    choices = body.get("choices") or []
    if not choices:
        raise RuntimeError(f"{config.get('label', provider)} returned no choices.")
    message = choices[0].get("message") or {}
    images = message.get("images") or []
    results: list[str] = []
    for img in images:
        if isinstance(img, dict):
            data = img.get("data") or ""
            b64 = img.get("b64_json") or ""
            url_str = img.get("url") or ""
            if b64:
                results.append(b64)
            elif data:
                results.append(data)
            elif url_str:
                results.append(url_str)
        elif isinstance(img, str):
            results.append(img)
    # Some providers may embed image in content as markdown or data URL
    if not results:
        content = (message.get("content") or "").strip()
        if content.startswith("data:image"):
            results.append(content.split(",", 1)[1] if "," in content else content)
    return results
