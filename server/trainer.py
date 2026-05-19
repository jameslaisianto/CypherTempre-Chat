"""Active Cambium Feedback Loop — scaffolding trainer."""

from __future__ import annotations

import re
from typing import Any

PREFIXES = {
    3: (
        "Use the most appropriate framework to solve this. "
        "First identify the type of problem, then apply your framework step by step."
    ),
    2: "Think about what kind of problem this is before solving.",
    1: "",
    0: "",
}


def _extract_framework(frame_declaration: dict[str, Any] | None, response_text: str) -> str:
    """Best-effort framework name extraction."""
    if frame_declaration:
        return str(frame_declaration.get("current_frame", "")).strip()
    # lightweight fallback — look for an explicit tag in raw text
    m = re.search(r"(?i)\bframework[\s:]+([^\n]+)", response_text)
    if m:
        return m.group(1).strip()
    return ""


class Trainer:
    """Adjusts query scaffolding based on Cambium events."""

    def __init__(self) -> None:
        self._states: dict[str, dict[str, Any]] = {}

    # --------------------------------------------------------------------- #
    # State helpers
    # --------------------------------------------------------------------- #
    def _get_state(self, session: str) -> dict[str, Any]:
        if session not in self._states:
            self._states[session] = {
                "scaffolding_level": 3,
                "framework_history": [],
                "consecutive_valid": 0,
                "consecutive_none": 0,
            }
        return self._states[session]

    def get_state(self, session: str) -> dict[str, Any]:
        """Return a shallow copy of the session's trainer state."""
        return dict(self._get_state(session))

    # --------------------------------------------------------------------- #
    # Core logic
    # --------------------------------------------------------------------- #
    def _has_framework_switch(
        self,
        state: dict[str, Any],
        frame_declaration: dict[str, Any] | None,
        response_text: str,
    ) -> bool:
        current = _extract_framework(frame_declaration, response_text)
        history: list[str] = state.get("framework_history", [])
        if not current or not history:
            return False
        last = history[-1]
        return last != current and bool(last) and bool(current)

    def _compute_level(
        self,
        state: dict[str, Any],
        cam_event: dict[str, Any] | None,
        frame_declaration: dict[str, Any] | None,
        response_text: str,
    ) -> int:
        level = state["scaffolding_level"]
        status = cam_event.get("status") if cam_event else None

        if cam_event is None or status == "none":
            if level < 3:
                level += 1
        elif status == "valid":
            quality = float(cam_event.get("quality_score", 0) or 0)
            if quality >= 0.7:
                level = max(0, level - 1)
            elif quality >= 0.4:
                pass  # maintain
            else:
                level = min(3, level + 1)
        elif status == "evasion":
            level = min(3, level + 2)
        elif status == "weak":
            # treat weak like mild upward pressure
            level = min(3, level + 1)

        if self._has_framework_switch(state, frame_declaration, response_text):
            level = max(0, level - 1)

        return level

    def _update_state(
        self,
        state: dict[str, Any],
        cam_event: dict[str, Any] | None,
        frame_declaration: dict[str, Any] | None,
        response_text: str,
    ) -> None:
        status = cam_event.get("status") if cam_event else None
        quality = float(cam_event.get("quality_score", 0) or 0) if cam_event else 0.0

        if status == "valid" and quality >= 0.7:
            state["consecutive_valid"] = state.get("consecutive_valid", 0) + 1
            state["consecutive_none"] = 0
        elif cam_event is None or status in ("none", "weak"):
            state["consecutive_none"] = state.get("consecutive_none", 0) + 1
            state["consecutive_valid"] = 0
        else:
            state["consecutive_valid"] = 0
            state["consecutive_none"] = 0

        current_framework = _extract_framework(frame_declaration, response_text)
        if current_framework:
            history: list[str] = list(state.get("framework_history", []))
            history.append(current_framework)
            if len(history) > 5:
                history.pop(0)
            state["framework_history"] = history

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #
    def process_event(
        self,
        session: str,
        ring: int | None,
        cam_event: dict[str, Any] | None,
        response_text: str,
        *,
        frame_declaration: dict[str, Any] | None = None,
    ) -> int:
        """Consume a Cambium event and return the new scaffolding level."""
        state = self._get_state(session)
        new_level = self._compute_level(state, cam_event, frame_declaration, response_text)
        self._update_state(state, cam_event, frame_declaration, response_text)
        state["scaffolding_level"] = new_level
        return new_level

    def build_query(self, session: str, problem_text: str, domain_hint: str = "") -> str:
        """Prepend scaffolding to the problem text based on the session level."""
        state = self._get_state(session)
        level = state["scaffolding_level"]
        prefix = PREFIXES.get(level, "")

        if level >= 2:
            if domain_hint:
                return f"{prefix}\n\nDomain: {domain_hint}\n\n{problem_text}"
            return f"{prefix}\n\n{problem_text}" if prefix else problem_text

        if level == 1 and domain_hint:
            return f"Domain: {domain_hint}\n\n{problem_text}"

        return problem_text
