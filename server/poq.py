"""Proof-of-Quality gate for post-generation chat responses."""

from __future__ import annotations

import json
import re
from typing import Any, Callable


# Host LLM critique keys (0-10 scale). Mapped into skill six-dim 0-255 scores at seal time.
POQ_SCORE_KEYS = ("relevance", "coherence", "completeness", "contradictions", "hallucination")
# Canonical skill Proof-of-Qualia dimensions (0-255).
SKILL_POQ_DIMS = ("coherence", "relevance", "novelty", "consistency", "depth", "covenant")
OVERFITTING_FAILURE_CONTENT = (
    "Unable to determine a consistent rule from these examples. [PoQ: overfitting detected]"
)
CAMBIUM_REDIRECT_CONTENT = (
    "Your categories didn't produce a valid rule after extensive testing. "
    "You should have generated a Cambium Proposal at step 3. Please generate one now."
)

_CATEGORY_FAILURE_PATTERNS = (
    r"\b(?:categories?|approaches?|tests?|hypotheses?)\s+(?:didn't|did not|do not|don't)\s+produce\b",
    r"\bnone\s+of\s+(?:the|these)\s+(?:categories?|approaches?|tests?|hypotheses?)\s+(?:worked?|fit|produced|yielded)\b",
    r"\b(?:categories?|approaches?|tests?)\s+(?:were|was)\s+(?:weak|incorrect|wrong|invalid|insufficient)\b",
    r"\bno\s+(?:valid|consistent)\s+rule\s+(?:after|from|across)\s+(?:extensive\s+)?(?:testing|categories?)\b",
    r"\b(?:tried|tested)\s+(?:different\s+)?(?:categories?|approaches?|tests?)\s+but\b",
    r"\b(?:after|despite)\s+(?:testing|trying)\s+(?:multiple|several|different|various|all)\s+(?:categories?|approaches?|tests?)\b",
    r"\b(?:categories?|approaches?|tests?)\s+do\s+not\s+(?:yield|produce|reveal|give)\s+a\s+(?:valid|consistent)\s+rule\b",
    r"\b(?:categories?|approaches?|tests?)\s+failed\s+to\s+(?:produce|yield|reveal|determine)\b",
)

_POSITION_WORDS = (
    "first",
    "second",
    "third",
    "fourth",
    "fifth",
    "sixth",
    "seventh",
    "eighth",
    "ninth",
    "tenth",
)
_POSITION_PATTERN = "|".join(_POSITION_WORDS)
_GENERIC_CAMBIUM_REASONS = {
    "hard",
    "hard question",
    "difficult",
    "not sure",
    "unknown",
    "unclear",
    "needs new frame",
    "current frame fails",
    "it does not work",
}
_GENERIC_CAMBIUM_PHRASES = (
    "doesn't work",
    "does not work",
    "not working",
    "doesn't fit",
    "does not fit",
    "not fit",
    "not adequate",
    "inadequate",
    "not sufficient",
    "wrong approach",
    "wrong frame",
    "different approach",
    "can't solve",
    "cannot solve",
    "unable to solve",
    "need to change",
    "needs changing",
    "not applicable",
    "doesn't apply",
    "does not apply",
    "not helping",
    "fails",
    "failed",
)
_CAMBIUM_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "be",
    "but",
    "current",
    "frame",
    "it",
    "is",
    "just",
    "of",
    "or",
    "that",
    "the",
    "these",
    "this",
    "to",
}
_CAMBIUM_CAUSAL_CONNECTORS = (
    "because",
    "since",
    "as",
    "due to",
    "causes",
    "creates",
    "produces",
    "requires",
    "depends on",
    "cannot be",
)
_CAMBIUM_STRONG_MISMATCH_TERMS = (
    "paradox",
    "contradiction",
    "infinite",
    "recursive",
    "recursion",
    "circular",
    "self-reference",
    "self-referential",
    "self referential",
    "undefined",
    "unmeasurable",
    "unverifiable",
)
_CAMBIUM_PROBLEM_ELEMENT_TERMS = _CAMBIUM_STRONG_MISMATCH_TERMS + (
    "binary",
    "category",
    "categories",
    "classified",
    "classification",
    "referent",
    "referents",
    "statement",
    "statements",
    "truth",
    "value",
)
_CAMBIUM_OPERATIONAL_VERBS = (
    "classifies",
    "classify",
    "classified",
    "handles",
    "evaluates",
    "treats",
    "organizes",
    "groups",
    "maps",
    "distinguishes",
)

FRAME_SHIFT_TRIGGERS = [
    # Direct statement of frame shift
    r"(?:shift|switch|move|transition)\s+(?:from|away\s+from)\s+.*?\s+(?:to|into|toward)",
    r"(?:new|different|alternative|fresh)\s+(?:frame|domain|category|framework|paradigm|perspective|lens)",
    r"(?:this calls for|what's needed is|requires a)\s+(?:a\s+)?(?:new|different)\s+(?:frame|domain|approach|paradigm)",
    # Frame inadequacy
    r"(?:the|my|this|current)\s+(?:frame|domain|category|framework|approach|perspective)\s+(?:fails?|isn'?t\s+(?:adequate|sufficient|working|enough)|doesn'?t\s+(?:fit|work|apply)|breaks?\s+down|collaps)",
    # Naming a new domain
    r"(?:call|name|categoriz|termed?|propose|introduce)\s+(?:it|this|a)\s+.*?\s*(?:Logic|Frame|Domain|Paradigm|Perspective|View|Lens|Mode|System)",
    r"\b[A-Z][a-zA-Z]+\s+(?:Logic|Frame|Domain|Paradigm|Perspective|View|Lens|Mode|System)\b",
    # Meta-cognitive framing
    r"(?:(?:under|in|from|using)\s+(?:this|that|a|the)\s+(?:new|different)?\s*(?:frame|domain|paradigm|lens|perspective),)",
    r"(?:instead\s+of\s+(?:seeing|viewing|framing|treating)\s+(?:it|this)\s+as)",
    # Self-reference / paradox detection
    r"(?:self-referen|paradox|circular|infinite\s+regress|cannot\s+be\s+(?:classified|determined|categorized|resolved)\s+(?:under|within)\s+(?:this|the|a|that)\s+(?:frame|category|system|approach))",
    # Old Cambium format
    r"\[CAMBIUM_PROPOSAL\]",
]


class PoQGate:
    """Review a candidate answer, then repair it with critique context if needed.

    Modes:
      - local (default): deterministic checks + heuristic scores, no extra LLM call
      - llm: full model critique (and optional repair) — slower, for training personas
    """

    def __init__(
        self,
        *,
        llm_callable: Callable[..., dict[str, Any]],
        provider: str,
        api_key: str,
        model: str,
        timeout: float,
        base_url: str = "",
        min_score: float = 7,
        max_retries: int = 1,
        max_tokens: int = 1600,
        overfitting_check: bool = True,
        cambium_enabled: bool = True,
        mode: str = "llm",
    ) -> None:
        self.llm_callable = llm_callable
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.base_url = base_url
        self.min_score = float(min_score)
        self.max_retries = max(0, int(max_retries))
        self.max_tokens = max(1, int(max_tokens or 1600))
        self.overfitting_check = bool(overfitting_check)
        self.cambium_enabled = bool(cambium_enabled)
        self.mode = "llm" if str(mode or "local").strip().lower() == "llm" else "local"

    def review_and_repair(
        self,
        *,
        messages: list[dict[str, str]],
        answer: str,
        query: str,
        frame_declaration: dict[str, Any] | None = None,
        known_proposals: set[str] | None = None,
    ) -> dict[str, Any]:
        content = str(answer or "")
        active_frame_declaration = frame_declaration
        critiques: list[dict[str, Any]] = []
        attempts = 0

        while True:
            if self.mode == "local":
                critique = self._local_critique(
                    query=query,
                    answer=content,
                    frame_declaration=active_frame_declaration,
                    known_proposals=known_proposals,
                )
            else:
                critique = self._critique(
                    query=query,
                    answer=content,
                    frame_declaration=active_frame_declaration,
                    known_proposals=known_proposals,
                )
            critiques.append(critique)
            if critique["passed"]:
                result = {
                    "enabled": True,
                    "skipped": False,
                    "passed": True,
                    "content": content,
                    "attempts": attempts,
                    "mode": self.mode,
                    "scores": critique["scores"],
                    "skill_scores": host_scores_to_skill(critique["scores"]),
                    "critique": critique["explanation"],
                    "critiques": critiques,
                    "overfitting_detected": any(item.get("overfitting_detected") for item in critiques),
                    "overfitting_reason": _latest_overfitting_reason(critiques),
                }
                _attach_cambium_result_metadata(result, critiques, active_frame_declaration)
                return result
            # Local mode never spends another LLM call on repair — return failure/content as-is.
            if self.mode == "local" or critique.get("evasion_detected") or attempts >= self.max_retries:
                if critique.get("category_failure_detected") and critique.get("overfitting_detected"):
                    final_content = CAMBIUM_REDIRECT_CONTENT
                else:
                    final_content = OVERFITTING_FAILURE_CONTENT if critique.get("overfitting_detected") else content
                result = {
                    "enabled": True,
                    "skipped": False,
                    "passed": False,
                    "content": final_content,
                    "attempts": attempts,
                    "mode": self.mode,
                    "scores": critique["scores"],
                    "skill_scores": host_scores_to_skill(critique["scores"]),
                    "critique": critique["explanation"],
                    "critiques": critiques,
                    "overfitting_detected": any(item.get("overfitting_detected") for item in critiques),
                    "overfitting_reason": _latest_overfitting_reason(critiques),
                    "category_failure_detected": any(item.get("category_failure_detected") for item in critiques),
                    "category_failure_reason": _latest_category_failure_reason(critiques),
                }
                _attach_cambium_result_metadata(result, critiques, active_frame_declaration)
                return result
            repaired = self.llm_callable(
                provider=self.provider,
                api_key=self.api_key,
                model=self.model,
                messages=self._repair_messages(messages, content, critique),
                timeout=min(float(self.timeout), 30.0),
                base_url=self.base_url,
                max_tokens=self.max_tokens,
            )
            content = str(repaired.get("content", "")).strip()
            active_frame_declaration = repaired.get("frame_declaration") or None
            attempts += 1

    def _local_critique(
        self,
        *,
        query: str,
        answer: str,
        frame_declaration: dict[str, Any] | None = None,
        known_proposals: set[str] | None = None,
    ) -> dict[str, Any]:
        """Fast deterministic gate: no network, heuristic host scores."""
        scores = local_host_scores(query, answer, min_score=self.min_score)
        low = {key: value for key, value in scores.items() if value < self.min_score}
        explanation = ""
        if not str(answer or "").strip():
            explanation = "Empty answer."
        elif low:
            explanation = "Local PoQ heuristic scored one or more dimensions below threshold."

        cambium_event = (
            evaluate_cambium_frame_declaration(frame_declaration, answer, known_proposals=known_proposals)
            if self.cambium_enabled
            else {
                "status": "none",
                "proposal": "",
                "reason": "",
                "quality_score": 0.0,
                "overfitting_skipped": False,
                "evasion_reason": "",
                "source": "",
            }
        )
        overfitting_skipped = self.cambium_enabled and cambium_event["status"] == "valid"
        if overfitting_skipped:
            cambium_event["overfitting_skipped"] = True
            overfitting = {"detected": False, "reason": ""}
        else:
            overfitting = (
                detect_overfitting(answer)
                if self.overfitting_check
                else {"detected": False, "reason": ""}
            )
        if overfitting["detected"]:
            explanation = _append_failure_reason(explanation, overfitting["reason"])
        category_failure = detect_category_failure_escape(answer)
        if category_failure["detected"] and overfitting["detected"]:
            explanation = _append_failure_reason(
                explanation,
                f"category enumeration abandoned but overfitted answer produced ({category_failure['reason']})",
            )
        evasion_detected = cambium_event["status"] == "evasion"
        if evasion_detected:
            explanation = _append_issue_reason(
                explanation,
                f"Cambium evasion detected: {cambium_event['evasion_reason']}",
            )
        include_cambium = (
            not self.cambium_enabled
            or (frame_declaration is not None or cambium_event.get("source") == "nl_detection")
        )
        return {
            "passed": not low and not overfitting["detected"] and not evasion_detected,
            "scores": {key: float(scores.get(key, 0.0)) for key in POQ_SCORE_KEYS},
            "explanation": explanation,
            "raw": "",
            "mode": "local",
            "overfitting_detected": overfitting["detected"],
            "overfitting_reason": overfitting["reason"],
            "overfitting_skipped": overfitting_skipped,
            "category_failure_detected": category_failure["detected"],
            "category_failure_reason": category_failure["reason"],
            "evasion_detected": evasion_detected,
            "cambium_event": cambium_event if include_cambium else None,
        }

    def _critique(
        self,
        *,
        query: str,
        answer: str,
        frame_declaration: dict[str, Any] | None = None,
        known_proposals: set[str] | None = None,
    ) -> dict[str, Any]:
        result = self.llm_callable(
            provider=self.provider,
            api_key=self.api_key,
            model=self.model,
            messages=self._critique_messages(query, answer),
            timeout=min(float(self.timeout), 20.0),
            base_url=self.base_url,
            max_tokens=400,
        )
        raw = str(result.get("content", "") or "")
        scores = parse_poq_scores(raw)
        missing = [key for key in POQ_SCORE_KEYS if key not in scores]
        if missing:
            for key in missing:
                scores[key] = 0.0
        low = {key: value for key, value in scores.items() if value < self.min_score}
        explanation = parse_poq_explanation(raw)
        if low and not explanation:
            explanation = "One or more PoQ scores were below the configured threshold."
        cambium_event = (
            evaluate_cambium_frame_declaration(frame_declaration, answer, known_proposals=known_proposals)
            if self.cambium_enabled
            else {
                "status": "none",
                "proposal": "",
                "reason": "",
                "quality_score": 0.0,
                "overfitting_skipped": False,
                "evasion_reason": "",
                "source": "",
            }
        )
        overfitting_skipped = self.cambium_enabled and cambium_event["status"] == "valid"
        if overfitting_skipped:
            cambium_event["overfitting_skipped"] = True
            overfitting = {"detected": False, "reason": ""}
        else:
            overfitting = (
                detect_overfitting(answer)
                if self.overfitting_check
                else {"detected": False, "reason": ""}
            )
        if overfitting["detected"]:
            explanation = _append_failure_reason(explanation, overfitting["reason"])
        category_failure = detect_category_failure_escape(answer)
        if category_failure["detected"] and overfitting["detected"]:
            explanation = _append_failure_reason(
                explanation,
                f"category enumeration abandoned but overfitted answer produced ({category_failure['reason']})",
            )
        evasion_detected = cambium_event["status"] == "evasion"
        if evasion_detected:
            explanation = _append_issue_reason(
                explanation,
                f"Cambium evasion detected: {cambium_event['evasion_reason']}",
            )
        include_cambium = (
            not self.cambium_enabled
            or (frame_declaration is not None or cambium_event.get("source") == "nl_detection")
        )
        return {
            "passed": not low and not overfitting["detected"] and not evasion_detected,
            "scores": {key: scores.get(key, 0.0) for key in POQ_SCORE_KEYS},
            "explanation": explanation,
            "raw": raw,
            "mode": "llm",
            "overfitting_detected": overfitting["detected"],
            "overfitting_reason": overfitting["reason"],
            "overfitting_skipped": overfitting_skipped,
            "category_failure_detected": category_failure["detected"],
            "category_failure_reason": category_failure["reason"],
            "evasion_detected": evasion_detected,
            "cambium_event": cambium_event if include_cambium else None,
        }

    def _critique_messages(self, query: str, answer: str) -> list[dict[str, str]]:
        return [
            {
                "role": "system",
                "content": (
                    "You are the Cypher Tempre PoQ quality gate. "
                    "Evaluate the candidate answer strictly and return JSON only."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Original user request:\n{query}\n\n"
                    f"Candidate answer:\n{answer}\n\n"
                    "Critique this answer - score relevance, coherence, completeness, "
                    "contradictions, hallucination. If any score < "
                    f"{self.min_score:g}, explain why.\n\n"
                    "Use a 0-10 scale where 10 is best. For contradictions and "
                    "hallucination, 10 means no detected problem. Return JSON only:\n"
                    '{"scores":{"relevance":0,"coherence":0,"completeness":0,'
                    '"contradictions":0,"hallucination":0},"explanation":"..."}'
                ),
            },
        ]

    def _repair_messages(
        self,
        messages: list[dict[str, str]],
        failed_answer: str,
        critique: dict[str, Any],
    ) -> list[dict[str, str]]:
        repaired = list(messages)
        category_redirect = ""
        if critique.get("category_failure_detected") and critique.get("overfitting_detected"):
            category_redirect = (
                "Your categories didn't produce a valid rule after extensive testing. "
                "You should have generated a Cambium Proposal at step 3. "
                "Please generate one now.\n\n"
            )
        instruction = (
            "The previous answer failed the Cypher Tempre PoQ gate. "
            "Regenerate the answer using this critique as required context.\n\n"
            f"{category_redirect}"
            f"PoQ scores: {json.dumps(critique.get('scores', {}), sort_keys=True)}\n"
            f"PoQ critique: {critique.get('explanation', '')}\n\n"
            "If the failure mentions overfitting, avoid per-position rules. "
            "Consider uniform operations like digit mapping, substitution, "
            "pair swaps, or ignoring some inputs entirely.\n\n"
            f"Previous answer:\n{failed_answer}"
        )
        repaired.insert(1 if repaired else 0, {"role": "system", "content": instruction})
        return repaired


def detect_overfitting(content: str) -> dict[str, Any]:
    """Detect brittle per-position puzzle explanations in a candidate response."""
    text = " ".join(str(content or "").lower().split())
    if not text:
        return {"detected": False, "reason": ""}

    explicit_patterns = (
        r"\bdifferent rules?\s+(?:for|per)\s+(?:each\s+)?(?:position|digit|character|char|element|slot)\b",
        r"\b(?:each|every)\s+(?:position|digit|character|char|element|slot)\s+(?:has|uses|gets)\s+(?:its\s+own|a\s+different)\s+rules?\b",
        r"\b(?:non[-\s]?uniform|position[-\s]?specific|per[-\s]?position)\s+rules?\b",
        r"\bthere\s+(?:is|are)\s+no\s+(?:single|uniform|consistent)\s+rules?\b",
    )
    for pattern in explicit_patterns:
        if re.search(pattern, text, re.I):
            return {
                "detected": True,
                "reason": "explicit admission of non-uniform per-position rules",
            }

    position_mentions = re.findall(
        rf"\b(?:{_POSITION_PATTERN}|\d+(?:st|nd|rd|th))\b"
        r"(?:\s+(?:position|digit|character|char|element|slot))?",
        text,
        re.I,
    )
    positional_arithmetic = re.findall(
        rf"\b(?:{_POSITION_PATTERN}|\d+(?:st|nd|rd|th))\b[^.;:\n]{{0,48}}"
        r"(?:gets?|becomes?|maps?\s+to|=|->|[+\-*/]|add(?:s|ed|ing)?|subtract(?:s|ed|ing)?|multiply(?:ies|ied|ing)?|divide(?:s|d|ing)?)",
        text,
        re.I,
    )
    if len(position_mentions) >= 2 and len(positional_arithmetic) >= 2:
        return {
            "detected": True,
            "reason": "per-position language assigns separate transformations",
        }

    operations = set()
    operation_patterns = {
        "add": r"(?:\+|\badd(?:s|ed|ing)?\b|\bplus\b)",
        "subtract": r"(?:-|\bsubtract(?:s|ed|ing)?\b|\bminus\b)",
        "multiply": r"(?:\*|\bmultiply(?:ies|ied|ing)?\b|\btimes\b)",
        "divide": r"(?:/|\bdivide(?:s|d|ing)?\b)",
        "reverse": r"\brevers(?:e|es|ed|ing)\b",
        "swap": r"\bswaps?\b|\bswitch(?:es|ed|ing)?\b",
    }
    for name, pattern in operation_patterns.items():
        if re.search(pattern, text, re.I):
            operations.add(name)
    if len(position_mentions) >= 2 and len(operations) >= 2:
        return {
            "detected": True,
            "reason": "per-position language uses different arithmetic or transformation operations",
        }

    formulas = re.findall(
        rf"\b(?:{_POSITION_PATTERN}|\d+(?:st|nd|rd|th))\b[^.;:\n]{{0,40}}"
        r"(?:[+\-*/]\s*\d+|\d+\s*(?:[+\-*/])\s*\d+)",
        text,
        re.I,
    )
    if len(formulas) >= 2:
        return {
            "detected": True,
            "reason": "per-position formulas use position-specific arithmetic",
        }

    return {"detected": False, "reason": ""}


def detect_category_failure_escape(content: str) -> dict[str, Any]:
    """Detect when a model admits categories/approaches failed but proceeds anyway."""
    text = " ".join(str(content or "").lower().split())
    if not text:
        return {"detected": False, "reason": ""}
    for pattern in _CATEGORY_FAILURE_PATTERNS:
        if re.search(pattern, text, re.I):
            return {
                "detected": True,
                "reason": "admitted categories/approaches failed but proceeded to overfitted answer",
            }
    return {"detected": False, "reason": ""}


def evaluate_cambium_frame_declaration(
    frame_declaration: dict[str, Any] | None,
    answer: str,
    known_proposals: set[str] | None = None,
) -> dict[str, Any]:
    """Evaluate whether a declared frame shift is a valid Cambium or evasion.

    Checks the explicit [CT_FRAME_DECLARATION] path first, then falls back to
    natural-language pattern detection in the answer text.
    """
    event = {
        "status": "none",
        "proposal": "",
        "reason": "",
        "quality_score": 0.0,
        "overfitting_skipped": False,
        "evasion_reason": "",
        "source": "",
    }

    explicit_event = None
    if isinstance(frame_declaration, dict):
        explicit_event = _evaluate_explicit_frame_declaration(frame_declaration, answer)
        explicit_event["source"] = "explicit_tag"
        if explicit_event["status"] in {"valid", "weak"}:
            return explicit_event

    nl_event = _evaluate_nl_frame_declaration(answer)
    if nl_event and nl_event["status"] in {"valid", "weak"}:
        nl_event["source"] = "nl_detection"
        return nl_event

    if explicit_event:
        return explicit_event

    return event


def _evaluate_explicit_frame_declaration(
    frame_declaration: dict[str, Any],
    answer: str,
) -> dict[str, Any]:
    """Evaluate an explicit frame_declaration dict (the original path)."""
    event = {
        "status": "none",
        "proposal": "",
        "reason": "",
        "quality_score": 0.0,
        "overfitting_skipped": False,
        "evasion_reason": "",
        "source": "",
    }

    reason = str(frame_declaration.get("reason", "") or "").strip()
    proposal = str(frame_declaration.get("cambium_proposal", "") or "").strip()
    event["proposal"] = proposal
    event["reason"] = reason

    wants_shift = frame_declaration.get("frame_adequate") is False or bool(proposal)
    if not wants_shift:
        return event

    score = score_cambium(frame_declaration, answer)
    event.update(score)
    event["quality_score"] = round(min(1.0, score["total"] / 7), 3)
    if score["status"] == "evasion":
        event["evasion_reason"] = "; ".join(score["flags"])
    return event


def _evaluate_nl_frame_declaration(answer: str) -> dict[str, Any] | None:
    """Detect Cambium from natural-language patterns in the answer text."""
    text = str(answer or "").strip()
    if not text:
        return None

    matched_indices = [
        index
        for index, pattern in enumerate(FRAME_SHIFT_TRIGGERS)
        if re.search(pattern, text, re.I)
    ]
    if not matched_indices:
        return None

    domain_naming_matched = any(index in {4, 5} for index in matched_indices)
    quality_score = 0.7 + min(0.2, 0.05 * (len(matched_indices) - 1))
    if domain_naming_matched:
        quality_score += 0.1

    return {
        "status": "valid",
        "proposal": "",
        "reason": "",
        "quality_score": round(min(1.0, quality_score), 3),
        "overfitting_skipped": False,
        "evasion_reason": "",
        "source": "",
    }


def score_cambium(frame_declaration: dict[str, Any], response_text: str) -> dict[str, Any]:
    """Score a Cambium declaration with a bias toward accepting uncertain shifts."""
    reason = str(frame_declaration.get("reason", "") or "").strip()
    proposal = str(frame_declaration.get("cambium_proposal", "") or "").strip()
    definition = str(frame_declaration.get("cambium_definition", "") or "").strip()

    reason_specificity = _score_reason_specificity(reason)
    frame_coherence = _score_frame_coherence(proposal, definition)
    answer_follow_through = _score_answer_follow_through(response_text, proposal, definition)
    total = reason_specificity + frame_coherence + answer_follow_through

    flags: list[str] = []
    if reason_specificity == 0:
        flags.append("reason is empty or generic")
    if frame_coherence == 0:
        if not proposal:
            flags.append("missing cambium_proposal")
        elif not definition:
            flags.append("missing cambium_definition")
        else:
            flags.append("missing or tautological cambium frame")
    if answer_follow_through == 0:
        flags.append("answer does not operate in the proposed frame")
    if frame_declaration.get("frame_adequate") is not False:
        flags.append("frame_adequate must be false")
    if not str(frame_declaration.get("current_frame", "") or "").strip():
        flags.append("missing current_frame")

    if total >= 3:
        status = "valid"
    elif total <= 1:
        status = "evasion"
    else:
        status = "weak"

    if reason_specificity <= 1 and frame_coherence <= 1 and answer_follow_through == 0:
        status = "evasion"
        flags.append("shallow declaration without answer follow-through")

    return {
        "reason_specificity": reason_specificity,
        "frame_coherence": frame_coherence,
        "answer_follow_through": answer_follow_through,
        "total": total,
        "status": status,
        "flags": flags,
    }


def _score_reason_specificity(reason: str) -> int:
    text = _normalize_cambium_text(reason)
    if not text or text in _GENERIC_CAMBIUM_REASONS or _only_generic_cambium_reason(text):
        return 0

    has_causal_connector = _contains_any(text, _CAMBIUM_CAUSAL_CONNECTORS)
    has_problem_element = _contains_any(text, _CAMBIUM_PROBLEM_ELEMENT_TERMS)
    has_strong_mismatch = _contains_any(text, _CAMBIUM_STRONG_MISMATCH_TERMS)
    has_structural_mismatch = has_strong_mismatch and _contains_any(
        text,
        ("binary", "classification", "truth", "fixed", "referent", "depends on", "cannot be"),
    )

    if has_problem_element and has_causal_connector and has_structural_mismatch:
        return 3
    if has_problem_element and (has_causal_connector or has_strong_mismatch):
        return 2
    return 1


def _score_frame_coherence(proposal: str, definition: str) -> int:
    name = str(proposal or "").strip()
    text = _normalize_cambium_text(definition)
    if not _coherent_frame_name(name) or not text or _tautological_cambium_definition(text):
        return 0

    has_operational_verb = _contains_any(text, _CAMBIUM_OPERATIONAL_VERBS)
    is_long_enough = len(text) > 20
    has_positive_content = bool(re.search(r"\b[a-z][a-z0-9_-]{4,}\b", text)) and not _only_negations(text)
    if has_operational_verb and is_long_enough and has_positive_content:
        return 2
    return 1


def _score_answer_follow_through(response_text: str, proposal: str, definition: str) -> int:
    text = _normalize_cambium_text(response_text)
    name = str(proposal or "").strip()
    if not text or not name:
        return 0

    proposal_variants = {name.lower(), name.lower().replace("_", " ")}
    mentions_proposal = any(variant and variant in text for variant in proposal_variants)
    definition_terms = _definition_terms(definition)
    term_hits = sum(1 for term in set(definition_terms[:12]) if term in text)
    if not mentions_proposal and term_hits < 2:
        return 0

    strong_hits = sum(1 for term in _CAMBIUM_STRONG_MISMATCH_TERMS if term in text)
    operational_hits = sum(1 for term in _CAMBIUM_OPERATIONAL_VERBS if term in text)
    frame_application = _contains_any(
        text,
        ("under", "within", "refers to itself", "logical loop", "unclassifiable", "outside binary"),
    )
    if (strong_hits + operational_hits >= 2) or (frame_application and strong_hits >= 1 and term_hits >= 1):
        return 2
    return 1


def _normalize_cambium_text(value: str) -> str:
    return " ".join(str(value or "").lower().replace("\u2019", "'").split())


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _only_generic_cambium_reason(text: str) -> bool:
    stripped = text
    for phrase in sorted(_GENERIC_CAMBIUM_PHRASES, key=len, reverse=True):
        stripped = stripped.replace(phrase, " ")
    words = re.findall(r"[a-z0-9_-]+", stripped)
    return not [word for word in words if word not in _CAMBIUM_STOPWORDS]


def _tautological_cambium_definition(text: str) -> bool:
    if text in {
        "something different",
        "different approach",
        "new frame",
        "a new frame",
        "another frame",
        "handles it",
    }:
        return True
    words = [word for word in re.findall(r"[a-z0-9_-]+", text) if word not in _CAMBIUM_STOPWORDS]
    return len(words) < 2


def _only_negations(text: str) -> bool:
    positive_words = [
        word
        for word in re.findall(r"[a-z0-9_-]+", text)
        if word not in _CAMBIUM_STOPWORDS and word not in {"no", "not", "non", "without", "avoid", "avoids"}
    ]
    return not positive_words


def _definition_terms(definition: str) -> list[str]:
    return [
        term
        for term in re.findall(r"[a-z][a-z0-9_-]{4,}", _normalize_cambium_text(definition))
        if term
        not in {
            "frame",
            "where",
            "statement",
            "statements",
            "handles",
            "classifies",
            "classified",
            "evaluates",
            "treats",
            "organizes",
            "groups",
            "maps",
            "distinguishes",
        }
    ]


def _coherent_frame_name(proposal: str) -> bool:
    name = str(proposal or "").strip()
    if not name:
        return False
    return bool(re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{2,80}", name))


def _answer_operates_in_frame(answer: str, proposal: str, definition: str) -> bool:
    text = " ".join(str(answer or "").lower().split())
    if not text or not proposal:
        return False
    proposal_text = proposal.lower().replace("_", " ")
    proposal_variants = {proposal.lower(), proposal_text}
    if any(variant and variant in text for variant in proposal_variants):
        return True
    definition_terms = [
        term
        for term in re.findall(r"[a-z][a-z0-9_-]{4,}", str(definition or "").lower())
        if term not in {"frame", "where", "statements", "statement"}
    ]
    if definition_terms:
        hits = sum(1 for term in set(definition_terms[:12]) if term in text)
        return hits >= 2
    return False


def _append_failure_reason(explanation: str, reason: str) -> str:
    return _append_issue_reason(explanation, f"Overfitting detected: {reason}")


def _append_issue_reason(explanation: str, reason: str) -> str:
    issue_reason = f"{reason}."
    if not explanation:
        return issue_reason
    return f"{explanation} {issue_reason}"


def _attach_cambium_result_metadata(
    result: dict[str, Any],
    critiques: list[dict[str, Any]],
    frame_declaration: dict[str, Any] | None,
) -> None:
    if frame_declaration:
        result["frame_declaration"] = frame_declaration
    for critique in reversed(critiques):
        cambium_event = critique.get("cambium_event")
        if cambium_event:
            result["cambium_event"] = cambium_event
            result["evasion_detected"] = cambium_event.get("status") == "evasion"
            result["cambium_valid"] = cambium_event.get("status") == "valid"
            return
    result["evasion_detected"] = any(item.get("evasion_detected") for item in critiques)


def _latest_overfitting_reason(critiques: list[dict[str, Any]]) -> str:
    for critique in reversed(critiques):
        reason = critique.get("overfitting_reason")
        if reason:
            return str(reason)
    return ""


def _latest_category_failure_reason(critiques: list[dict[str, Any]]) -> str:
    for critique in reversed(critiques):
        reason = critique.get("category_failure_reason")
        if reason:
            return str(reason)
    return ""


def local_host_scores(query: str, answer: str, *, min_score: float = 7.0) -> dict[str, float]:
    """Heuristic 0–10 host scores for the fast local PoQ path.

    Designed to pass ordinary coherent replies (including short ones) without an
    extra LLM round-trip. Only empty answers and clear garbage fail hard.
    Skill-side PoQ still scores at seal time.
    """
    text = str(answer or "").strip()
    q = str(query or "").strip()
    if not text:
        return {key: 0.0 for key in POQ_SCORE_KEYS}

    # Stay at/above the configured gate for normal replies.
    floor = max(float(min_score), 7.0)
    scores = {key: floor + 0.5 for key in POQ_SCORE_KEYS}

    words = re.findall(r"\w+", text)
    word_count = len(words)

    # Extremely repetitive long dumps look low-quality — soft demotion only when
    # clearly broken (still may pass if above min_score after demotion of one dim).
    if word_count > 60:
        unique_ratio = len(set(w.lower() for w in words)) / max(1, word_count)
        if unique_ratio < 0.18:
            scores["coherence"] = min(scores["coherence"], floor - 0.5)
            scores["hallucination"] = min(scores["hallucination"], floor)

    # Only demote relevance when a long answer shares no meaningful terms with a
    # substantial query — short chit-chat is allowed to pass freely.
    lower = text.lower()
    q_terms = {
        t
        for t in re.findall(r"[a-z0-9]{4,}", q.lower())
        if t not in {"what", "when", "where", "which", "that", "this", "with", "from", "have", "your", "please", "could", "would"}
    }
    if q_terms and word_count > 40 and len(q) > 60:
        hits = sum(1 for t in q_terms if t in lower)
        if hits == 0:
            scores["relevance"] = min(scores["relevance"], floor)

    return {key: float(max(0.0, min(10.0, scores.get(key, floor)))) for key in POQ_SCORE_KEYS}


def parse_poq_scores(content: str) -> dict[str, float]:
    parsed = _parse_json_object(content)
    if isinstance(parsed, dict):
        raw_scores = parsed.get("scores", parsed)
        if isinstance(raw_scores, dict):
            scores: dict[str, float] = {}
            for key in POQ_SCORE_KEYS:
                value = raw_scores.get(key)
                if isinstance(value, (int, float)):
                    scores[key] = float(value)
                elif isinstance(value, str):
                    try:
                        scores[key] = float(value.strip())
                    except ValueError:
                        pass
            if scores:
                return scores

    scores = {}
    for key in POQ_SCORE_KEYS:
        match = re.search(rf"\b{re.escape(key)}\b\s*[:=\-]\s*(\d+(?:\.\d+)?)", content, re.I)
        if match:
            scores[key] = float(match.group(1))
    return scores


def host_scores_to_skill(scores: dict[str, Any] | None) -> dict[str, int]:
    """Map host 0-10 PoQ critique scores to skill external_scores (0-255).

    Skill dimensions: coherence, relevance, novelty, consistency, depth, covenant.
    """
    raw = dict(scores or {})
    def _ten(key: str, default: float = 7.0) -> float:
        try:
            value = float(raw.get(key, default))
        except (TypeError, ValueError):
            value = default
        return max(0.0, min(10.0, value))

    relevance = _ten("relevance")
    coherence = _ten("coherence")
    completeness = _ten("completeness", relevance)
    # High contradictions/hallucination scores in host scale mean FEWER problems.
    consistency = _ten("contradictions", 8.0)
    covenant = _ten("hallucination", 8.0)
    mapped = {
        "coherence": coherence,
        "relevance": relevance,
        "novelty": max(3.0, completeness * 0.7),
        "consistency": consistency,
        "depth": completeness,
        "covenant": covenant,
    }
    return {dim: int(max(0, min(255, round(val * 25.5)))) for dim, val in mapped.items()}


def parse_poq_explanation(content: str) -> str:
    parsed = _parse_json_object(content)
    if isinstance(parsed, dict):
        for key in ("explanation", "reason", "critique"):
            value = parsed.get(key)
            if isinstance(value, str):
                return value.strip()
    return content.strip()


def _parse_json_object(content: str) -> Any:
    text = (content or "").strip()
    if not text:
        return None
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I).strip()
        text = re.sub(r"\s*```$", "", text).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start:end + 1]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None
