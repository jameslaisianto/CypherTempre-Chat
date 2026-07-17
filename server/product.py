"""Daily-driver product policies: defaults, memory autopilot, identity bridge, trust status."""

from __future__ import annotations

from typing import Any

from server.config import DEFAULT_MODEL, DEFAULT_PROVIDER, default_provider_url


# ---------------------------------------------------------------------------
# Recommended "just works" profile
# ---------------------------------------------------------------------------

RECOMMENDED_PROFILE: dict[str, Any] = {
    "provider": DEFAULT_PROVIDER,
    "default_model": DEFAULT_MODEL,
    "base_url": default_provider_url(DEFAULT_PROVIDER),
    "memory_autopilot": "conservative",
    "identity_bridge": True,
    "stream_replies": True,
}

MEMORY_AUTOPILOT_MODES = frozenset({"off", "conservative", "trusted"})
AUTOPILOT_TRUSTED_KINDS = frozenset({"identity", "preference", "boundary", "style", "persona"})
AUTOPILOT_CONSERVATIVE_MIN_CONF = 0.85
AUTOPILOT_TRUSTED_MIN_CONF = 0.7

PRODUCT_SETTING_KEYS = frozenset({
    "memory_autopilot",
    "identity_bridge",
    "stream_replies",
})


def normalize_memory_autopilot(value: Any) -> str:
    text = str(value or "conservative").strip().lower()
    return text if text in MEMORY_AUTOPILOT_MODES else "conservative"


def coerce_bool(value: Any, default: bool = True) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off"}:
        return False
    return default


def product_settings_from_user(settings: dict[str, Any] | None) -> dict[str, Any]:
    raw = settings or {}
    return {
        "memory_autopilot": normalize_memory_autopilot(raw.get("memory_autopilot", RECOMMENDED_PROFILE["memory_autopilot"])),
        "identity_bridge": coerce_bool(raw.get("identity_bridge"), True),
        "stream_replies": coerce_bool(raw.get("stream_replies"), True),
    }


def should_auto_accept_memory(memory: dict[str, Any], mode: str) -> bool:
    mode = normalize_memory_autopilot(mode)
    if mode == "off":
        return False
    if str(memory.get("status", "pending")) != "pending":
        return False
    kind = str(memory.get("kind") or "").strip().lower()
    scope = str(memory.get("scope") or "session").strip().lower()
    try:
        confidence = float(memory.get("confidence") or 0)
    except (TypeError, ValueError):
        confidence = 0.0
    if mode == "conservative":
        return (
            scope == "global"
            and kind in AUTOPILOT_TRUSTED_KINDS
            and confidence >= AUTOPILOT_CONSERVATIVE_MIN_CONF
        )
    # trusted
    return confidence >= AUTOPILOT_TRUSTED_MIN_CONF and (
        scope == "global" or kind in AUTOPILOT_TRUSTED_KINDS or kind in {"goal", "correction"}
    )


def apply_memory_autopilot(
    memories: list[dict[str, Any]],
    *,
    mode: str,
    accept_fn,
) -> list[dict[str, Any]]:
    """Accept pending memories per policy. accept_fn(memory_id) -> memory dict."""
    mode = normalize_memory_autopilot(mode)
    accepted: list[dict[str, Any]] = []
    if mode == "off":
        return accepted
    for memory in memories:
        if not should_auto_accept_memory(memory, mode):
            continue
        memory_id = str(memory.get("id") or "")
        if not memory_id:
            continue
        try:
            updated = accept_fn(memory_id)
            if updated:
                accepted.append(updated)
        except Exception:
            continue
    return accepted
