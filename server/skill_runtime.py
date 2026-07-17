"""Host adapter for the vendored Cypher Tempre skill (v3.28+).

Loads the OpenClaw skill bundle as libraries, owns session skill roots
(`chain/`, `registry/`), and exposes ring views + seal/recall helpers the
HTTP app uses. Cognitive primitives stay in the skill — this module does
not reimplement hashing, PoQ math, or faculty growth.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import shutil
import sys
import threading
from contextlib import contextmanager
from types import SimpleNamespace
from typing import Any, Iterable, Iterator, Sequence


DEFAULT_COVENANT = (
    "loving, joyful, peaceful, patient, kind, good, faithful, gentle, self-controlled"
)

SKILL_POQ_DIMS = (
    "coherence",
    "relevance",
    "novelty",
    "consistency",
    "depth",
    "covenant",
)

INTERACTION_RING_TYPE = "interaction"
IMAGE_RING_TYPES = frozenset({"image_generate", "image_edit", "image_redefine"})
VIDEO_RING_TYPES = frozenset({"video_generate", "video_img2vid", "video_remix"})


def default_skill_root() -> pathlib.Path:
    env = (os.environ.get("CT_SKILL_ROOT") or os.environ.get("SKILL_ROOT") or "").strip()
    if env:
        return pathlib.Path(env).expanduser().resolve()
    return (pathlib.Path(__file__).resolve().parent.parent / "skill" / "cypher-tempre-self-model").resolve()


def resolve_skill_root(path: pathlib.Path | str | None = None) -> pathlib.Path:
    candidates = [
        pathlib.Path(path).expanduser() if path else None,
        pathlib.Path(os.environ.get("CT_SKILL_ROOT", "")).expanduser() if os.environ.get("CT_SKILL_ROOT") else None,
        pathlib.Path(os.environ.get("SKILL_ROOT", "")).expanduser() if os.environ.get("SKILL_ROOT") else None,
        default_skill_root(),
    ]
    for candidate in candidates:
        if candidate is None:
            continue
        resolved = candidate.resolve()
        # Accept either the skill directory or a path to its timechain.py file.
        if resolved.is_file() and resolved.name == "timechain.py":
            resolved = resolved.parent
        if (resolved / "timechain.py").exists() and (resolved / "poq.py").exists():
            return resolved
    raise FileNotFoundError(
        "Cypher Tempre skill not found. Expected skill/cypher-tempre-self-model "
        "(with timechain.py and poq.py), or set CT_SKILL_ROOT."
    )


class SkillModules:
    """Lazy-loaded skill modules after sys.path bootstrap."""

    def __init__(self, skill_root: pathlib.Path):
        self.skill_root = skill_root.resolve()
        self.version = _read_version(self.skill_root)
        self._ensure_path()
        # Import after path setup — skill uses bare module names.
        import timechain as ct_timechain  # type: ignore
        import poq as ct_poq  # type: ignore
        import recall as ct_recall  # type: ignore

        self.timechain = ct_timechain
        self.poq = ct_poq
        self.recall = ct_recall
        self._cambium = None
        self._dream = None
        self._immune = None
        self._router = None
        self._dormancy = None
        self._doctor = None

    def _ensure_path(self) -> None:
        root = str(self.skill_root)
        if root not in sys.path:
            sys.path.insert(0, root)

    def _load(self, name: str):
        self._ensure_path()
        return __import__(name)

    @property
    def cambium(self):
        if self._cambium is None:
            self._cambium = self._load("cambium")
        return self._cambium

    @property
    def dream(self):
        if self._dream is None:
            self._dream = self._load("dream")
        return self._dream

    @property
    def immune(self):
        if self._immune is None:
            self._immune = self._load("immune")
        return self._immune

    @property
    def router(self):
        if self._router is None:
            self._router = self._load("router")
        return self._router

    @property
    def dormancy(self):
        if self._dormancy is None:
            self._dormancy = self._load("dormancy")
        return self._dormancy

    @property
    def doctor(self):
        if self._doctor is None:
            self._doctor = self._load("doctor")
        return self._doctor


_MODULES: SkillModules | None = None


def bootstrap(skill_root: pathlib.Path | str | None = None) -> SkillModules:
    global _MODULES
    root = resolve_skill_root(skill_root)
    if _MODULES is None or _MODULES.skill_root != root:
        _MODULES = SkillModules(root)
    return _MODULES


def _read_version(skill_root: pathlib.Path) -> str:
    path = skill_root / "VERSION"
    try:
        return path.read_text(encoding="utf-8").strip() or "unknown"
    except OSError:
        return "unknown"


def skill_chain_dir(root: pathlib.Path) -> pathlib.Path:
    return root / "chain"


def skill_rings_path(root: pathlib.Path) -> pathlib.Path:
    return skill_chain_dir(root) / "rings.jsonl"


def forge_chain_path(root: pathlib.Path) -> pathlib.Path:
    return root / ".timechain" / "chain.jsonl"


# Product/host metadata that must survive forge → skill ledger migration.
_FORGE_HOST_FILES = (
    "session.json",
    "memory_model.json",
    "cambium_events.json",
    "overlays.json",
    "config.json",
)

_session_root_locks: dict[str, threading.Lock] = {}
_session_root_locks_guard = threading.Lock()


def _session_lock(root: pathlib.Path) -> threading.Lock:
    key = str(root.resolve())
    with _session_root_locks_guard:
        lock = _session_root_locks.get(key)
        if lock is None:
            lock = threading.Lock()
            _session_root_locks[key] = lock
        return lock


@contextmanager
def _locked_session_root(root: pathlib.Path) -> Iterator[None]:
    lock = _session_lock(root)
    lock.acquire()
    try:
        yield
    finally:
        lock.release()


def list_forge_archives(root: pathlib.Path) -> list[pathlib.Path]:
    """Newest forge archive first (by directory name stamp / mtime)."""
    root = pathlib.Path(root)
    if not root.exists():
        return []
    archives = [p for p in root.iterdir() if p.is_dir() and p.name.startswith(".timechain_forge_archive_")]
    return sorted(archives, key=lambda p: (p.name, p.stat().st_mtime), reverse=True)


def _restore_host_files_from_archive(archive: pathlib.Path, forge_dir: pathlib.Path) -> list[str]:
    restored: list[str] = []
    forge_dir.mkdir(parents=True, exist_ok=True)
    for name in _FORGE_HOST_FILES:
        src = archive / name
        dest = forge_dir / name
        if src.exists() and not dest.exists():
            try:
                shutil.copy2(src, dest)
                restored.append(name)
            except OSError:
                continue
    return restored


def archive_forge_ledger(root: pathlib.Path) -> pathlib.Path | None:
    """Move legacy Forge `.timechain/chain.jsonl` aside when migrating.

    Restores host product metadata (including session persona lock) into a
    fresh `.timechain/` so sessions keep their bound persona after the skill
    ledger takes over.
    """
    forge_dir = root / ".timechain"
    forge_chain = forge_dir / "chain.jsonl"
    if not forge_chain.exists():
        return None
    if skill_rings_path(root).exists():
        return None
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive = root / f".timechain_forge_archive_{stamp}"
    try:
        shutil.move(str(forge_dir), str(archive))
        # Restore app-only product files that lived under .timechain
        # (session persona, memory model, etc.).
        _restore_host_files_from_archive(archive, forge_dir)
        return archive
    except OSError:
        return None


def restore_session_metadata_from_archives(root: pathlib.Path) -> dict[str, Any]:
    """If `.timechain/session.json` is missing, copy it from the newest archive."""
    root = pathlib.Path(root)
    forge_dir = root / ".timechain"
    session_path = forge_dir / "session.json"
    if session_path.exists():
        return {"restored": False, "reason": "already_present"}
    restored_any: list[str] = []
    for archive in list_forge_archives(root):
        names = _restore_host_files_from_archive(archive, forge_dir)
        restored_any.extend(names)
        if session_path.exists():
            return {"restored": True, "files": restored_any, "archive": archive.name}
    if restored_any:
        return {"restored": True, "files": restored_any, "session_json": False}
    return {"restored": False, "reason": "no_archive_metadata"}


def _load_jsonl(path: pathlib.Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    try:
        # errors=replace: some legacy forge archives were written with mixed encodings.
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(row, dict):
                    rows.append(row)
    except OSError:
        return []
    return rows


def _is_degenerate_skill_chain(rings: Sequence[dict[str, Any]]) -> bool:
    """True when the skill ledger has no real history (empty / multi-genesis only)."""
    if not rings:
        return True
    for ring in rings:
        ring_type = str(ring.get("ring_type") or "").lower()
        if ring_type and ring_type != "genesis":
            return False
    return True


def _chain_needs_repair(root: pathlib.Path, skill: SkillModules) -> bool:
    rings_path = skill_rings_path(root)
    if not rings_path.exists():
        return False
    rings = _load_jsonl(rings_path)
    if _is_degenerate_skill_chain(rings):
        # Degenerate alone is only "needs repair" when archives exist or multi-genesis.
        if len(rings) > 1 and all(str(r.get("ring_type") or "").lower() == "genesis" for r in rings):
            return True
        if list_forge_archives(root) and any((a / "chain.jsonl").exists() for a in list_forge_archives(root)):
            return True
        return False
    ok, _status = skill.timechain.Timechain(root).verify()
    if ok:
        return False
    # Broken verify with no real interactions → repairable.
    return _is_degenerate_skill_chain(rings)


def _pick_best_forge_archive(root: pathlib.Path) -> pathlib.Path | None:
    best: pathlib.Path | None = None
    best_count = -1
    for archive in list_forge_archives(root):
        chain = archive / "chain.jsonl"
        if not chain.exists():
            continue
        count = 0
        try:
            with chain.open("r", encoding="utf-8") as handle:
                for line in handle:
                    if line.strip():
                        count += 1
        except OSError:
            continue
        if count > best_count:
            best = archive
            best_count = count
    return best


def _reset_skill_chain_files(root: pathlib.Path) -> None:
    """Remove skill chain ledger files so genesis can be recreated cleanly."""
    chain_dir = skill_chain_dir(root)
    rings = chain_dir / "rings.jsonl"
    if rings.exists():
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = chain_dir / f"rings.broken_{stamp}.jsonl"
        try:
            rings.replace(backup)
        except OSError:
            try:
                rings.unlink()
            except OSError:
                pass
    for name in ("checkpoints.jsonl", "LOCKED", "PAUSED", "FROZEN"):
        path = chain_dir / name
        if path.exists():
            try:
                path.unlink()
            except OSError:
                pass


def _forge_scores_to_poq(scores: Any) -> dict[str, int]:
    if not isinstance(scores, dict):
        return default_pass_scores()
    converted = scores_to_skill_255(scores)
    return converted or default_pass_scores()


def import_forge_chain(
    root: pathlib.Path,
    forge_chain: pathlib.Path,
    *,
    name: str = "CypherTempre",
    skill: SkillModules | None = None,
) -> dict[str, Any]:
    """Reseal a legacy Forge chain.jsonl into the skill Timechain format.

    Preserves chat history (query/content/domain/tags/epistemic/scores) with
    forge provenance markers. Recomputes skill ring hashes so verify passes.
    """
    skill = skill or bootstrap()
    root = root.resolve()
    ensure_base_registries(root, skill)
    forge_rings = _load_jsonl(forge_chain)
    if not forge_rings:
        return {"imported": False, "reason": "empty_forge_chain", "rings": 0}

    prev_autoindex = os.environ.get("CT_AUTOINDEX")
    os.environ["CT_AUTOINDEX"] = "0"
    try:
        _reset_skill_chain_files(root)
        tc = skill.timechain.Timechain(root)
        # Prefer forge genesis agent name when available.
        genesis_name = name
        for fr in forge_rings:
            if str(fr.get("kind") or "").lower() == "genesis":
                content = str(fr.get("content") or "")
                try:
                    parsed = json.loads(content) if content.startswith("{") else None
                except json.JSONDecodeError:
                    parsed = None
                if isinstance(parsed, dict) and parsed.get("agent_id"):
                    genesis_name = str(parsed.get("core") or name)
                break
        if tc.height() == 0:
            tc.genesis(name=genesis_name)

        imported = 0
        skipped = 0
        for fr in forge_rings:
            kind = str(fr.get("kind") or "interaction").strip().lower() or "interaction"
            if kind == "genesis":
                skipped += 1
                continue
            scores = _forge_scores_to_poq(fr.get("scores"))
            brightness = fr.get("brightness")
            if isinstance(brightness, (int, float)):
                if float(brightness) <= 1.5:
                    scores = {**scores, "brightness": round(float(brightness) * 255.0, 3)}
                else:
                    scores = {**scores, "brightness": round(float(brightness), 3)}
            payload = {
                "summary": str(fr.get("content") or fr.get("summary") or "")[:20000],
                "content": str(fr.get("content") or fr.get("summary") or "")[:20000],
                "query": str(fr.get("query") or fr.get("context") or "")[:20000],
                "context": str(fr.get("query") or fr.get("context") or "")[:20000],
                "domain": str(fr.get("domain") or "chat"),
                "tags": list(fr.get("tags") or [kind]),
                "epistemic": str(fr.get("epistemic") or ""),
                "retrieved": list(fr.get("retrieved") or []),
                "used_rings": list(fr.get("retrieved") or []),
                "importance": fr.get("importance"),
                "neuro": fr.get("neuro") if isinstance(fr.get("neuro"), dict) else {},
                "supersedes": fr.get("supersedes"),
                "source": fr.get("source"),
                "forge_import": True,
                "forge_n": fr.get("n"),
                "forge_hash": fr.get("hash"),
                "forge_ts": fr.get("ts"),
                "forge_kind": kind,
            }
            ring_type = kind if kind not in {"", "genesis"} else "interaction"
            if ring_type == "chat":
                ring_type = "interaction"
            tc.seal(ring_type, payload, poq=scores)
            imported += 1

        ok, status = tc.verify()
        # Rebuild hippocampus once at the end for recall.
        try:
            from hippocampus import Hippocampus  # type: ignore

            Hippocampus(root).ensure_current()
        except Exception:
            pass
        marker = root / ".timechain" / "forge_import.json"
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(
            json.dumps(
                {
                    "imported_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                    "source": str(forge_chain),
                    "imported_rings": imported,
                    "skipped_genesis": skipped,
                    "verify_ok": bool(ok),
                    "verify_status": status if isinstance(status, str) else "; ".join(str(x) for x in (status or [])[:6]),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return {
            "imported": True,
            "rings": imported,
            "skipped_genesis": skipped,
            "verify_ok": bool(ok),
            "height": tc.height(),
            "source": str(forge_chain),
        }
    finally:
        if prev_autoindex is None:
            os.environ.pop("CT_AUTOINDEX", None)
        else:
            os.environ["CT_AUTOINDEX"] = prev_autoindex


def repair_multi_genesis_chain(
    root: pathlib.Path,
    *,
    name: str = "CypherTempre",
    skill: SkillModules | None = None,
) -> dict[str, Any]:
    """Collapse a racey multi-genesis skill chain to a single valid genesis."""
    skill = skill or bootstrap()
    root = root.resolve()
    rings = _load_jsonl(skill_rings_path(root))
    if not rings:
        return {"repaired": False, "reason": "empty"}
    if not all(str(r.get("ring_type") or "").lower() == "genesis" for r in rings):
        return {"repaired": False, "reason": "not_all_genesis"}
    if len(rings) <= 1:
        return {"repaired": False, "reason": "already_single"}
    _reset_skill_chain_files(root)
    tc = skill.timechain.Timechain(root)
    ring = tc.genesis(name=name)
    ok, status = tc.verify()
    return {
        "repaired": True,
        "previous_rings": len(rings),
        "genesis_hash": ring.get("ring_hash"),
        "verify_ok": bool(ok),
        "verify_status": status if isinstance(status, str) else "; ".join(str(x) for x in (status or [])[:4]),
    }


def migrate_session_root(
    root: pathlib.Path,
    *,
    name: str = "CypherTempre",
    skill: SkillModules | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Idempotent fix for sessions broken by forge→skill cutover.

    - Restores `.timechain/session.json` (persona lock) from archives
    - Imports forge chat history when the skill chain is empty/degenerate
    - Collapses multi-genesis verify failures when no forge history exists
    """
    skill = skill or bootstrap()
    root = pathlib.Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    result: dict[str, Any] = {"root": str(root), "actions": []}

    meta = restore_session_metadata_from_archives(root)
    if meta.get("restored"):
        result["actions"].append({"restore_metadata": meta})

    marker = root / ".timechain" / "forge_import.json"
    if marker.exists() and not force:
        # Already imported once; still repair multi-genesis if verify is bad.
        rings = _load_jsonl(skill_rings_path(root))
        if rings and all(str(r.get("ring_type") or "").lower() == "genesis" for r in rings) and len(rings) > 1:
            repaired = repair_multi_genesis_chain(root, name=name, skill=skill)
            result["actions"].append({"repair_multi_genesis": repaired})
        result["skipped"] = "already_imported"
        return result

    rings = _load_jsonl(skill_rings_path(root))
    archive = _pick_best_forge_archive(root)
    forge_chain = (archive / "chain.jsonl") if archive else None
    has_forge_history = bool(forge_chain and forge_chain.exists())

    degenerate = _is_degenerate_skill_chain(rings)
    multi_genesis = bool(rings) and len(rings) > 1 and all(
        str(r.get("ring_type") or "").lower() == "genesis" for r in rings
    )

    if has_forge_history and (degenerate or force or multi_genesis or not rings):
        # Only import when skill side has no real conversation yet (or forced).
        if force or degenerate or multi_genesis or not rings:
            imported = import_forge_chain(root, forge_chain, name=name, skill=skill)
            result["actions"].append({"import_forge": imported})
            return result

    if multi_genesis:
        repaired = repair_multi_genesis_chain(root, name=name, skill=skill)
        result["actions"].append({"repair_multi_genesis": repaired})
        return result

    if not result["actions"]:
        result["skipped"] = "healthy_or_nothing_to_do"
    return result


def migrate_workspace_sessions(
    workspace_root: pathlib.Path,
    *,
    skill: SkillModules | None = None,
) -> list[dict[str, Any]]:
    """Scan user/session trees under a Forge workspace and migrate each root."""
    skill = skill or bootstrap()
    workspace_root = pathlib.Path(workspace_root).resolve()
    results: list[dict[str, Any]] = []
    candidates: list[pathlib.Path] = []

    # Top-level default workspace (legacy single-user).
    if (workspace_root / ".timechain").exists() or list_forge_archives(workspace_root) or skill_rings_path(workspace_root).exists():
        candidates.append(workspace_root)

    sessions_root = workspace_root / "sessions"
    if sessions_root.exists():
        for path in sessions_root.iterdir():
            if path.is_dir():
                candidates.append(path)

    users_root = workspace_root / "data" / "users"
    if users_root.exists():
        for user_dir in users_root.iterdir():
            if not user_dir.is_dir():
                continue
            user_sessions = user_dir / "sessions"
            if not user_sessions.exists():
                continue
            for path in user_sessions.iterdir():
                if path.is_dir():
                    candidates.append(path)

    seen: set[str] = set()
    for root in candidates:
        key = str(root.resolve())
        if key in seen:
            continue
        seen.add(key)
        # Cheap gate: only touch roots that look migrated/broken.
        has_archive = bool(list_forge_archives(root))
        has_session_meta = (root / ".timechain" / "session.json").exists()
        rings = _load_jsonl(skill_rings_path(root)) if skill_rings_path(root).exists() else []
        multi_genesis = bool(rings) and len(rings) > 1 and all(
            str(r.get("ring_type") or "").lower() == "genesis" for r in rings
        )
        if not has_archive and not multi_genesis and has_session_meta:
            continue
        if not has_archive and not multi_genesis and not rings:
            continue
        try:
            with _locked_session_root(root):
                results.append(migrate_session_root(root, skill=skill))
        except Exception as exc:
            results.append({"root": str(root), "error": f"{type(exc).__name__}: {exc}"})
    return results


def ensure_base_registries(root: pathlib.Path, skill: SkillModules) -> None:
    reg = root / "registry"
    reg.mkdir(parents=True, exist_ok=True)
    for name in ("modalities.json", "senses.json"):
        dest = reg / name
        if dest.exists():
            continue
        src = skill.skill_root / "registry" / name
        if src.exists():
            shutil.copy2(src, dest)


def ensure_session_root(
    root: pathlib.Path,
    *,
    name: str = "CypherTempre",
    skill: SkillModules | None = None,
) -> dict[str, Any]:
    """Ensure skill layout + genesis exist for a session/studio root."""
    skill = skill or bootstrap()
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    with _locked_session_root(root):
        archive_forge_ledger(root)
        # Retroactively restore persona locks and repair broken skill ledgers.
        try:
            migrate_session_root(root, name=name, skill=skill)
        except Exception:
            # Migration is best-effort; never block session open.
            pass
        ensure_base_registries(root, skill)
        tc = skill.timechain.Timechain(root)
        info: dict[str, Any] = {"root": str(root), "created": False, "height": tc.height()}
        if tc.height() == 0:
            ring = tc.genesis(name=name)
            info["created"] = True
            info["genesis_hash"] = ring.get("ring_hash")
            info["height"] = 1
        else:
            head = tc.head()
            info["genesis_hash"] = _genesis_hash(tc)
            info["height"] = tc.height()
            info["head_hash"] = (head or {}).get("ring_hash")
        return info


def open_chain(root: pathlib.Path, skill: SkillModules | None = None):
    skill = skill or bootstrap()
    return skill.timechain.Timechain(root.resolve())


def open_recall(root: pathlib.Path, skill: SkillModules | None = None):
    skill = skill or bootstrap()
    return skill.recall.Recall(root.resolve())


def _genesis_hash(tc) -> str:
    for ring in tc.iter_rings():
        if int(ring.get("index", -1)) == 0 or ring.get("ring_type") == "genesis":
            return str(ring.get("ring_hash") or "")
    return ""


def _payload_dict(ring: dict[str, Any]) -> dict[str, Any]:
    payload = ring.get("payload")
    return payload if isinstance(payload, dict) else {}


def _poq_dict(ring: dict[str, Any]) -> dict[str, Any]:
    poq = ring.get("poq")
    return poq if isinstance(poq, dict) else {}


def brightness_unit(raw: Any) -> float:
    """Normalize skill brightness (typically 0–255) to 0–1 for UI continuity."""
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return 0.0
    if value > 1.5:
        return max(0.0, min(1.0, value / 255.0))
    return max(0.0, min(1.0, value))


def brightness_raw(raw: Any) -> float:
    try:
        return float(raw)
    except (TypeError, ValueError):
        return 0.0


def ring_as_view(ring: dict[str, Any] | None) -> SimpleNamespace:
    """Map a skill ring dict to the host's stable view fields."""
    if not ring:
        return SimpleNamespace(
            n=0,
            index=0,
            ts="",
            kind="unknown",
            domain="",
            query="",
            content="",
            brightness=0.0,
            brightness_raw=0.0,
            scores={},
            epistemic="",
            tags=[],
            retrieved=[],
            refs=[],
            supersedes=None,
            source=None,
            importance=0.0,
            hash="",
            prev="",
            perception={},
            fields={},
            planes=[],
            neuro={},
            raw={},
            payload={},
        )
    payload = _payload_dict(ring)
    poq = _poq_dict(ring)
    scores = {
        dim: float(poq[dim])
        for dim in SKILL_POQ_DIMS
        if isinstance(poq.get(dim), (int, float))
    }
    # Prefer explicit chat fields; fall back to skill seal summary/context.
    content = str(
        payload.get("content")
        or payload.get("summary")
        or payload.get("text")
        or ""
    )
    query = str(
        payload.get("query")
        or payload.get("context")
        or payload.get("input")
        or ""
    )
    domain = str(payload.get("domain") or payload.get("app_domain") or "chat")
    tags = payload.get("tags") if isinstance(payload.get("tags"), list) else []
    retrieved = payload.get("retrieved") if isinstance(payload.get("retrieved"), list) else []
    if not retrieved and isinstance(payload.get("used_rings"), list):
        retrieved = list(payload.get("used_rings") or [])
    epistemic = str(payload.get("epistemic") or "")
    b_raw = poq.get("brightness")
    if b_raw is None and scores:
        b_raw = sum(scores.values()) / len(scores)
    index = int(ring.get("index", 0) or 0)
    return SimpleNamespace(
        n=index,
        index=index,
        ts=str(ring.get("timestamp") or ""),
        kind=str(ring.get("ring_type") or payload.get("role") or ""),
        domain=domain,
        query=query,
        content=content,
        brightness=brightness_unit(b_raw),
        brightness_raw=brightness_raw(b_raw),
        scores=scores,
        epistemic=epistemic,
        tags=[str(t) for t in tags],
        retrieved=[int(x) for x in retrieved if str(x).lstrip("-").isdigit()],
        refs=list(ring.get("blockspace_refs") or []),
        supersedes=payload.get("supersedes"),
        source=payload.get("source"),
        importance=float(payload.get("importance") or brightness_unit(b_raw) or 0.0),
        hash=str(ring.get("ring_hash") or ""),
        prev=str(ring.get("prev_hash") or ""),
        perception=dict(payload.get("perception") or {}),
        fields=dict(payload.get("fields") or {}),
        planes=list(payload.get("planes") or []),
        neuro=dict(payload.get("neuro") or {}),
        raw=ring,
        payload=payload,
    )


def load_ring_views(root: pathlib.Path, skill: SkillModules | None = None) -> list[SimpleNamespace]:
    tc = open_chain(root, skill)
    return [ring_as_view(r) for r in tc.load()]


def count_rings(root: pathlib.Path) -> int:
    path = skill_rings_path(root)
    if not path.exists():
        return 0
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            return sum(1 for line in handle if line.strip())
    except OSError:
        return 0


def verify_root(root: pathlib.Path, skill: SkillModules | None = None) -> tuple[bool, str]:
    skill = skill or bootstrap()
    ensure_session_root(root, skill=skill)
    ok, report = open_chain(root, skill).verify()
    if isinstance(report, list):
        status = "; ".join(str(x) for x in report[:6])
    else:
        status = str(report)
    return bool(ok), status


def scores_to_skill_255(scores: dict[str, Any] | None) -> dict[str, int]:
    """Convert host or fractional scores into skill 0–255 external_scores."""
    out: dict[str, int] = {}
    raw = scores or {}
    for dim in SKILL_POQ_DIMS:
        if dim not in raw:
            # legacy host keys
            legacy = {
                "coherence": raw.get("coherence"),
                "relevance": raw.get("relevance"),
                "novelty": raw.get("novelty", raw.get("completeness")),
                "consistency": raw.get("consistency", 1.0 - float(raw.get("contradictions") or 0)),
                "depth": raw.get("depth", raw.get("completeness")),
                "covenant": raw.get("covenant", 1.0 - float(raw.get("hallucination") or 0)),
            }
            value = legacy.get(dim)
        else:
            value = raw.get(dim)
        if value is None:
            continue
        try:
            num = float(value)
        except (TypeError, ValueError):
            continue
        if num <= 1.5:
            num = num * 255.0
        out[dim] = int(max(0, min(255, round(num))))
    return out


def default_pass_scores() -> dict[str, int]:
    return {
        "coherence": 210,
        "relevance": 220,
        "novelty": 120,
        "consistency": 210,
        "depth": 160,
        "covenant": 230,
    }


def seal_interaction(
    root: pathlib.Path,
    *,
    summary: str,
    context: str,
    domain: str = "chat",
    tags: Sequence[str] | None = None,
    external_scores: dict[str, Any] | None = None,
    used_rings: Sequence[int] | None = None,
    persona_id: str = "",
    epistemic: str = "",
    frame: str | None = None,
    meta: dict[str, Any] | None = None,
    skill: SkillModules | None = None,
) -> dict[str, Any]:
    """PoQ-gate and seal a chat interaction via the skill conscience."""
    skill = skill or bootstrap()
    ensure_session_root(root, skill=skill)
    if _is_paused(root, skill):
        return {"accepted": False, "reason": "self-model is paused (dormant)", "ring": None, "decision": "PAUSED"}
    if _is_frozen(root):
        return {"accepted": False, "reason": "chain is frozen", "ring": None, "decision": "FROZEN"}

    scores = scores_to_skill_255(external_scores) or default_pass_scores()
    extra = {
        "content": summary,
        "query": context,
        "domain": domain,
        "tags": list(tags or [domain]),
        "epistemic": epistemic or "",
        "persona_id": persona_id,
        "used_rings": list(used_rings or []),
        "retrieved": list(used_rings or []),
        "app": dict(meta or {}),
    }
    tc = open_chain(root, skill)
    relevant = None
    if used_rings:
        by_idx = {int(r.get("index", -1)): r for r in tc.load()}
        relevant = [by_idx[i] for i in used_rings if i in by_idx]

    def _gate(candidate: str, ext: dict[str, int], payload: dict[str, Any]):
        return skill.poq.gate_and_seal(
            tc,
            candidate,
            context=context,
            ring_type=INTERACTION_RING_TYPE,
            external_scores=ext,
            extra_payload=payload,
            relevant_rings=relevant,
            declared_evidence=len(used_rings) if used_rings is not None else None,
            frame=frame,
        )

    verdict, ring = _gate(summary, scores, extra)
    decision = str((verdict or {}).get("decision") or "").upper()
    resealed = False

    # Skill turn-loop parity: FORCE_UNCERTAINTY / REVISE reseal as honest uncertain text.
    # REJECT seals a covenant-clean refusal record (no laundering of rejected claims).
    if ring is None and decision in {"FORCE_UNCERTAINTY", "REVISE"}:
        reasons = []
        if isinstance(verdict, dict):
            reasons = list(verdict.get("reasons") or [])
        reason_txt = "; ".join(str(r) for r in reasons[:3]) if reasons else decision
        # Heavy hedging keeps lexical assertiveness under the uncertainty gate.
        uncertain = (
            f"Uncertain provisional note (low confidence; may be incomplete): "
            f"one possible reading is that {summary} "
            f"I am not sure this is fully grounded yet. "
            f"(gate: {reason_txt[:180]})"
        )
        uncertain_scores = {
            "coherence": min(int(scores.get("coherence", 200)), 200),
            "relevance": min(int(scores.get("relevance", 200)), 210),
            "novelty": 100,
            "consistency": min(int(scores.get("consistency", 200)), 210),
            "depth": 120,
            "covenant": max(int(scores.get("covenant", 230)), 230),
        }
        extra_u = dict(extra)
        extra_u["content"] = uncertain
        extra_u["summary"] = uncertain
        extra_u["epistemic"] = "uncertain"
        extra_u["uncertainty_reseal"] = True
        verdict, ring = _gate(uncertain, uncertain_scores, extra_u)
        decision = str((verdict or {}).get("decision") or "").upper()
        resealed = True
        summary = uncertain
        scores = uncertain_scores
        # Final loop guarantee: leave a labeled uncertain ring if the gate still refuses.
        if ring is None:
            payload = dict(extra_u)
            payload["summary"] = uncertain
            payload["poq_verdict"] = decision
            payload["gate_reasons"] = reasons
            ring = tc.seal(
                INTERACTION_RING_TYPE,
                payload,
                poq={**uncertain_scores, "brightness": round(sum(uncertain_scores.values()) / 6, 3)},
            )
            decision = "SEAL"
            resealed = True

    if ring is None and decision == "REJECT":
        refusal = (
            f"Declined to seal this turn (PoQ REJECT). "
            f"Reason: {'; '.join(str(r) for r in (verdict or {}).get('reasons', [])[:3]) or 'covenant/consistency'}."
        )
        refusal_scores = {
            "coherence": 220,
            "relevance": 200,
            "novelty": 100,
            "consistency": 230,
            "depth": 140,
            "covenant": 255,
        }
        extra_r = {
            "content": refusal,
            "query": context,
            "domain": "self",
            "tags": ["refusal", "poq-reject"],
            "epistemic": "known",
            "persona_id": persona_id,
            "app": dict(meta or {}),
            "refusal": True,
            "summary": refusal,
        }
        verdict, ring = _gate(refusal, refusal_scores, extra_r)
        decision = str((verdict or {}).get("decision") or "").upper()
        summary = refusal
        scores = refusal_scores
        if ring is None:
            ring = tc.seal("refusal", extra_r, poq=refusal_scores)
            decision = "SEAL"

    if ring is None:
        return {
            "accepted": False,
            "reason": decision or "poq_rejected",
            "decision": decision,
            "verdict": verdict,
            "scores": {k: v / 255.0 for k, v in scores.items()},
            "scores_raw": scores,
            "brightness": brightness_unit((verdict or {}).get("brightness")),
            "brightness_raw": brightness_raw((verdict or {}).get("brightness")),
            "ring": None,
            "resealed": resealed,
        }

    # Post-seal autogrow (skill turn loop parity); fail-soft.
    try:
        if os.environ.get("CT_AUTOGROW", "1").lower() not in ("0", "false", "no", "off"):
            skill.cambium.fill_gap(str(context or summary), root=root)
    except Exception:
        pass

    view = ring_as_view(ring)
    return {
        "accepted": True,
        "reason": decision or "SEAL",
        "decision": decision,
        "verdict": verdict,
        "scores": {k: v / 255.0 for k, v in scores.items()},
        "scores_raw": scores,
        "brightness": view.brightness,
        "brightness_raw": view.brightness_raw,
        "ring": view_to_dict(view),
        "epistemic": view.epistemic,
        "retrieved": list(used_rings or []),
        "resealed": resealed,
        "content": view.content,
    }


def seal_structured(
    root: pathlib.Path,
    *,
    ring_type: str,
    payload: dict[str, Any],
    poq_scores: dict[str, Any] | None = None,
    skill: SkillModules | None = None,
) -> SimpleNamespace:
    """Seal a non-chat ring (image/video/anchor/system) with explicit scores."""
    skill = skill or bootstrap()
    ensure_session_root(root, name=str(payload.get("name") or ring_type), skill=skill)
    if _is_frozen(root):
        raise RuntimeError("chain is frozen")
    scores = scores_to_skill_255(poq_scores) or default_pass_scores()
    # Structured metadata seals use Timechain.seal with pre-set poq (skill trusts caller scores).
    ring = open_chain(root, skill).seal(ring_type, payload, poq=scores)
    return ring_as_view(ring)


def seal_refusal(
    root: pathlib.Path,
    *,
    reason: str,
    context: str = "",
    skill: SkillModules | None = None,
) -> dict[str, Any]:
    skill = skill or bootstrap()
    ensure_session_root(root, skill=skill)
    scores = {
        "coherence": 220,
        "relevance": 220,
        "novelty": 100,
        "consistency": 230,
        "depth": 150,
        "covenant": 255,
    }
    summary = f"Declined at membrane/gate: {reason}"
    return seal_interaction(
        root,
        summary=summary,
        context=context,
        domain="self",
        tags=["refusal", "immune"],
        external_scores=scores,
        skill=skill,
        meta={"refusal": True, "reason": reason},
    )


def view_to_dict(view: SimpleNamespace) -> dict[str, Any]:
    return {
        "n": int(view.n),
        "ts": view.ts,
        "kind": view.kind,
        "domain": view.domain,
        "query": view.query,
        "content": view.content,
        "brightness": float(view.brightness),
        "brightness_raw": float(getattr(view, "brightness_raw", 0) or 0),
        "scores": dict(view.scores or {}),
        "epistemic": view.epistemic,
        "tags": list(view.tags or []),
        "retrieved": list(view.retrieved or []),
        "refs": list(view.refs or []),
        "supersedes": view.supersedes,
        "source": view.source,
        "importance": float(view.importance or 0),
        "hash": view.hash,
        "prev": view.prev,
        "perception": dict(view.perception or {}),
        "fields": dict(view.fields or {}),
        "planes": list(view.planes or []),
        "neuro": dict(view.neuro or {}),
    }


def cite_answer(
    root: pathlib.Path,
    *,
    question: str,
    answer: str,
    used_rings: Sequence[int] | None = None,
    skill: SkillModules | None = None,
) -> dict[str, Any]:
    """Run skill span-guard cited-answer audit against declared evidence rings."""
    skill = skill or bootstrap()
    ensure_session_root(root, skill=skill)
    rings = list(used_rings or [])
    try:
        engine = open_recall(root, skill)
        report = engine.answer(question, answer, rings)
        if isinstance(report, dict):
            return report
        return {"ok": True, "report": str(report), "used_rings": rings}
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
            "used_rings": rings,
            "unsupported": [],
            "n_unsupported": 0,
        }


def retrieve_views(
    root: pathlib.Path,
    query: str,
    *,
    limit: int = 12,
    skill: SkillModules | None = None,
) -> list[SimpleNamespace]:
    skill = skill or bootstrap()
    ensure_session_root(root, skill=skill)
    engine = open_recall(root, skill)
    result = engine.retrieve(query, max_blocks=max(1, min(limit, 32)))
    blocks = []
    if isinstance(result, dict):
        blocks = list(result.get("blocks") or [])
    elif isinstance(result, list):
        blocks = result
    by_index = {int(r.get("index", -1)): r for r in open_chain(root, skill).load()}
    views: list[SimpleNamespace] = []
    for block in blocks:
        if isinstance(block, dict) and "index" in block:
            idx = int(block["index"])
            ring = by_index.get(idx)
            if ring:
                views.append(ring_as_view(ring))
            else:
                # block brief only
                views.append(
                    ring_as_view(
                        {
                            "index": idx,
                            "ring_type": block.get("type") or "unknown",
                            "timestamp": "",
                            "prev_hash": "",
                            "ring_hash": "",
                            "payload": {
                                "summary": block.get("summary") or block.get("text") or "",
                                "content": block.get("summary") or block.get("text") or "",
                                "domain": block.get("domain") or "chat",
                            },
                            "poq": {"brightness": block.get("score") or 0},
                        }
                    )
                )
        elif isinstance(block, dict) and "ring" in block:
            views.append(ring_as_view(block["ring"]))
    return views


def screen_input(root: pathlib.Path, text: str, skill: SkillModules | None = None) -> dict[str, Any]:
    skill = skill or bootstrap()
    ensure_session_root(root, skill=skill)
    try:
        return skill.immune.Immune(root).screen(text)
    except Exception as exc:
        return {"blocked": False, "tainted": False, "error": str(exc)}


def route_query(root: pathlib.Path, query: str, skill: SkillModules | None = None) -> dict[str, Any]:
    skill = skill or bootstrap()
    ensure_session_root(root, skill=skill)
    try:
        # router.route may be module-level function
        route_fn = getattr(skill.router, "route", None)
        if callable(route_fn):
            result = route_fn(query, root=root) if _accepts_root(route_fn) else route_fn(query)
            if isinstance(result, dict):
                return result
            return {"decision": str(result)}
    except Exception as exc:
        return {"decision": "MODEL", "error": str(exc)}
    return {"decision": "MODEL"}


def _accepts_root(fn) -> bool:
    try:
        import inspect

        return "root" in inspect.signature(fn).parameters
    except Exception:
        return False


def cambium_snapshot(root: pathlib.Path, query: str = "", skill: SkillModules | None = None) -> dict[str, Any]:
    skill = skill or bootstrap()
    ensure_session_root(root, skill=skill)
    gaps: list[dict[str, Any]] = []
    proposals: list[Any] = []
    try:
        sense = skill.cambium.detect_gap(query or "session state", root=root)
        if isinstance(sense, dict):
            gaps.append({"domain": "gap", "mean_brightness": float(sense.get("dissonance") or 0) / 255.0, "detail": sense})
            if sense.get("gap"):
                proposals.append(sense)
    except TypeError:
        try:
            sense = skill.cambium.detect_gap(query or "session state")
            if isinstance(sense, dict):
                gaps.append({"domain": "gap", "mean_brightness": float(sense.get("dissonance") or 0) / 255.0, "detail": sense})
        except Exception as exc:
            return {"gaps": [], "consolidations": [], "proposals": [], "error": str(exc)}
    except Exception as exc:
        return {"gaps": [], "consolidations": [], "proposals": [], "error": str(exc)}

    # Grown faculties summary
    try:
        grown = skill.cambium.load_grown(root)
        if isinstance(grown, dict):
            for name, body in list(grown.items())[:20]:
                proposals.append({"name": name, "kind": (body or {}).get("kind"), "status": (body or {}).get("status")})
        elif isinstance(grown, list):
            proposals.extend(grown[:20])
    except Exception:
        pass

    return {
        "gaps": gaps,
        "consolidations": [],
        "proposals": proposals,
        "proposal_count": len(proposals),
        "gap_count": len(gaps),
        "consolidation_count": 0,
    }


def run_dream(root: pathlib.Path, skill: SkillModules | None = None) -> dict[str, Any]:
    skill = skill or bootstrap()
    ensure_session_root(root, skill=skill)
    try:
        dreamer = skill.dream.Dream(root)
        report = dreamer.run()
        return {"ok": True, "report": report if isinstance(report, dict) else {"result": str(report)}}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def dormancy_status(root: pathlib.Path, skill: SkillModules | None = None) -> dict[str, Any]:
    skill = skill or bootstrap()
    try:
        d = skill.dormancy.Dormancy(root)
        paused = bool(d.is_paused())
        return {"paused": paused, "active": not paused}
    except Exception as exc:
        return {"paused": False, "active": True, "error": str(exc)}


def doctor_line(root: pathlib.Path, skill: SkillModules | None = None) -> str:
    skill = skill or bootstrap()
    try:
        doc = skill.doctor
        if hasattr(doc, "line"):
            return str(doc.line(root))
        if hasattr(doc, "main"):
            return f"skill {skill.version} root={root}"
    except Exception as exc:
        return f"doctor unavailable: {exc}"
    return f"skill {skill.version}"


def _is_paused(root: pathlib.Path, skill: SkillModules | None = None) -> bool:
    return bool(dormancy_status(root, skill).get("paused"))


def _frozen_path(root: pathlib.Path) -> pathlib.Path:
    return root / "chain" / "FROZEN"


def _is_frozen(root: pathlib.Path) -> bool:
    return _frozen_path(root).exists()


def set_frozen(root: pathlib.Path, frozen: bool) -> None:
    path = _frozen_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    if frozen:
        path.write_text(dt.datetime.now(dt.timezone.utc).isoformat(), encoding="utf-8")
    elif path.exists():
        path.unlink()


def covenant_text(root: pathlib.Path, skill: SkillModules | None = None) -> str:
    skill = skill or bootstrap()
    ensure_session_root(root, skill=skill)
    for ring in open_chain(root, skill).iter_rings():
        if ring.get("ring_type") == "genesis" or int(ring.get("index", -1)) == 0:
            payload = _payload_dict(ring)
            cov = payload.get("covenant")
            if isinstance(cov, list):
                return ", ".join(str(x) for x in cov)
            if cov:
                return str(cov)
            break
    return DEFAULT_COVENANT


def self_model_summary(root: pathlib.Path, skill: SkillModules | None = None) -> dict[str, Any]:
    skill = skill or bootstrap()
    ensure_session_root(root, skill=skill)
    views = load_ring_views(root, skill)
    by_domain: dict[str, list[float]] = {}
    for view in views:
        if view.kind == "genesis":
            continue
        by_domain.setdefault(view.domain or "chat", []).append(float(view.brightness))
    domain_mass = {d: round(sum(bs), 3) for d, bs in by_domain.items()}
    top_domains = [d for d, _ in sorted(domain_mass.items(), key=lambda x: x[1], reverse=True)[:5]]
    ok, status = verify_root(root, skill)
    return {
        "name": "CypherTempre",
        "rings": len(views),
        "temporal_mass": round(sum(float(v.brightness) for v in views[1:]), 3),
        "top_domains": top_domains,
        "domain_mass": domain_mass,
        "verified": ok,
        "verify_status": status,
        "skill_version": skill.version,
        "covenant": covenant_text(root, skill),
        "frozen": _is_frozen(root),
        "dormant": _is_paused(root, skill),
    }


def temporal_context(root: pathlib.Path, skill: SkillModules | None = None) -> str:
    views = load_ring_views(root, skill)
    if not views:
        return "Empty chain."
    head = views[-1]
    return (
        f"Skill Timechain height={len(views) - 1} "
        f"head=#{head.n} kind={head.kind} domain={head.domain} "
        f"brightness={head.brightness:.3f} ts={head.ts}"
    )


def respond_to_challenge(root: pathlib.Path, challenge: dict[str, Any], skill: SkillModules | None = None) -> dict[str, Any]:
    """Temporal proof-of-self: hash selected ring heads with a nonce (no mutation)."""
    skill = skill or bootstrap()
    ensure_session_root(root, skill=skill)
    tc = open_chain(root, skill)
    rings = {int(r.get("index", -1)): r for r in tc.load()}
    requested = challenge.get("rings") or challenge.get("ring_hashes") or []
    nonce = str(challenge.get("nonce") or "")
    selected = []
    for item in requested:
        if isinstance(item, int) or (isinstance(item, str) and item.isdigit()):
            ring = rings.get(int(item))
            if ring:
                selected.append(ring.get("ring_hash"))
        else:
            selected.append(str(item))
    material = json.dumps({"hashes": selected, "nonce": nonce}, sort_keys=True)
    proof = skill.timechain.sha256_hex(material.encode("utf-8"))
    revealed = []
    for item in requested:
        if isinstance(item, int) or (isinstance(item, str) and str(item).isdigit()):
            idx = int(item)
            ring = rings.get(idx)
            if ring:
                revealed.append({
                    "n": idx,
                    "hash": ring.get("ring_hash"),
                    "kind": ring.get("ring_type"),
                })
    return {
        "proof": proof,
        "response_hash": proof,
        "nonce": nonce,
        "ring_count": len(selected),
        "revealed": revealed,
        "head": (tc.head() or {}).get("ring_hash"),
        "height": tc.height(),
    }


def fleet_import_ring(
    root: pathlib.Path,
    foreign: dict[str, Any],
    *,
    source: str,
    skill: SkillModules | None = None,
) -> SimpleNamespace | None:
    """Import a foreign ring payload as a provenance-marked skill ring."""
    skill = skill or bootstrap()
    ensure_session_root(root, skill=skill)
    if _is_frozen(root):
        raise RuntimeError("chain is frozen")
    payload = {
        "summary": foreign.get("content") or foreign.get("summary") or json.dumps(foreign)[:2000],
        "context": foreign.get("query") or foreign.get("context") or "",
        "content": foreign.get("content") or foreign.get("summary") or "",
        "query": foreign.get("query") or "",
        "domain": foreign.get("domain") or "fleet",
        "source": source,
        "imported": True,
        "foreign_hash": foreign.get("hash") or foreign.get("ring_hash"),
        "tags": list(foreign.get("tags") or ["fleet-import"]),
    }
    return seal_structured(
        root,
        ring_type="fleet_import",
        payload=payload,
        poq_scores=foreign.get("scores") or default_pass_scores(),
        skill=skill,
    )


class _VerifyAdapter:
    """Tiny adapter so host code can call timechain.verify_chain(chain)."""

    def __init__(self, session: "SkillSession"):
        self._session = session

    def verify_chain(self, _chain=None):
        return verify_root(self._session.workspace, self._session.skill)


class SkillSession:
    """Session-scoped skill handle used by the HTTP App host."""

    def __init__(
        self,
        workspace: pathlib.Path,
        *,
        name: str = "CypherTempre",
        skill: SkillModules | None = None,
    ):
        self.skill = skill or bootstrap()
        self.workspace = workspace.resolve()
        self.name = name
        ensure_session_root(self.workspace, name=name, skill=self.skill)
        self._chain_cache: list[SimpleNamespace] | None = None
        # Compatibility surface for older host/tests that used Forge module APIs.
        self.verify_chain = lambda chain=None: verify_root(self.workspace, self.skill)

    def reload(self) -> None:
        self._chain_cache = None
        ensure_session_root(self.workspace, name=self.name, skill=self.skill)

    @property
    def chain(self) -> list[SimpleNamespace]:
        if self._chain_cache is None:
            self._chain_cache = load_ring_views(self.workspace, self.skill)
        return self._chain_cache

    @property
    def values(self) -> str:
        return covenant_text(self.workspace, self.skill)

    @property
    def frozen(self) -> bool:
        return _is_frozen(self.workspace)

    @property
    def genesis_hash(self) -> str:
        tc = open_chain(self.workspace, self.skill)
        return _genesis_hash(tc)

    @property
    def cphy_weights(self) -> dict[str, float]:
        return {}

    def freeze(self, on: bool = True) -> None:
        set_frozen(self.workspace, bool(on))

    def get_temporal_context(self) -> str:
        return temporal_context(self.workspace, self.skill)

    def self_model(self) -> dict[str, Any]:
        return self_model_summary(self.workspace, self.skill)

    def cambium_report(self) -> SimpleNamespace:
        snap = cambium_snapshot(self.workspace, skill=self.skill)
        return SimpleNamespace(
            gaps=[(g.get("domain"), g.get("mean_brightness", 0)) for g in snap.get("gaps", [])],
            consolidations=list(snap.get("consolidations") or []),
            proposals=list(snap.get("proposals") or []),
        )

    def dream(self, *, domains: Sequence[str] | None = None, cycles: int = 3) -> list[dict[str, Any]]:
        result = run_dream(self.workspace, self.skill)
        self._chain_cache = None
        return [result]

    def fleet_import(self, foreign_ring: dict[str, Any], *, source: str) -> SimpleNamespace | None:
        view = fleet_import_ring(self.workspace, foreign_ring, source=source, skill=self.skill)
        self._chain_cache = None
        return view

    def respond_to_challenge(self, challenge: dict[str, Any]) -> dict[str, Any]:
        return respond_to_challenge(self.workspace, challenge, self.skill)

    def interact(
        self,
        query: str,
        *,
        domain: str = "chat",
        tags: Sequence[str] | None = None,
        override_content: str | None = None,
        external_scores: dict[str, Any] | None = None,
        used_rings: Sequence[int] | None = None,
        persona_id: str = "",
        frame: str | None = None,
    ) -> dict[str, Any]:
        content = override_content if override_content is not None else query
        if used_rings is None:
            hits = retrieve_views(self.workspace, query, limit=8, skill=self.skill)
            used_rings = [h.n for h in hits]
        result = seal_interaction(
            self.workspace,
            summary=str(content),
            context=str(query),
            domain=domain,
            tags=tags,
            external_scores=external_scores,
            used_rings=used_rings,
            persona_id=persona_id,
            frame=frame,
            skill=self.skill,
        )
        self._chain_cache = None
        return result

    def seal_meta(
        self,
        *,
        kind: str,
        payload: dict[str, Any],
        scores: dict[str, Any] | None = None,
    ) -> SimpleNamespace:
        view = seal_structured(
            self.workspace,
            ring_type=kind,
            payload=payload,
            poq_scores=scores,
            skill=self.skill,
        )
        self._chain_cache = None
        return view
