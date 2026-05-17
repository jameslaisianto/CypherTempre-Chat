"""Proof-of-Quality gate for post-generation chat responses."""

from __future__ import annotations

import json
import re
from typing import Any, Callable


POQ_SCORE_KEYS = ("relevance", "coherence", "completeness", "contradictions", "hallucination")
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


class PoQGate:
    """Review a candidate answer, then repair it with critique context if needed."""

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

    def review_and_repair(
        self,
        *,
        messages: list[dict[str, str]],
        answer: str,
        query: str,
    ) -> dict[str, Any]:
        content = str(answer or "")
        critiques: list[dict[str, Any]] = []
        attempts = 0

        while True:
            critique = self._critique(query=query, answer=content)
            critiques.append(critique)
            if critique["passed"]:
                return {
                    "enabled": True,
                    "skipped": False,
                    "passed": True,
                    "content": content,
                    "attempts": attempts,
                    "scores": critique["scores"],
                    "critique": critique["explanation"],
                    "critiques": critiques,
                    "overfitting_detected": any(item.get("overfitting_detected") for item in critiques),
                    "overfitting_reason": _latest_overfitting_reason(critiques),
                }
            if attempts >= self.max_retries:
                if critique.get("category_failure_detected") and critique.get("overfitting_detected"):
                    final_content = CAMBIUM_REDIRECT_CONTENT
                else:
                    final_content = OVERFITTING_FAILURE_CONTENT if critique.get("overfitting_detected") else content
                return {
                    "enabled": True,
                    "skipped": False,
                    "passed": False,
                    "content": final_content,
                    "attempts": attempts,
                    "scores": critique["scores"],
                    "critique": critique["explanation"],
                    "critiques": critiques,
                    "overfitting_detected": any(item.get("overfitting_detected") for item in critiques),
                    "overfitting_reason": _latest_overfitting_reason(critiques),
                    "category_failure_detected": any(item.get("category_failure_detected") for item in critiques),
                    "category_failure_reason": _latest_category_failure_reason(critiques),
                }
            repaired = self.llm_callable(
                provider=self.provider,
                api_key=self.api_key,
                model=self.model,
                messages=self._repair_messages(messages, content, critique),
                timeout=self.timeout,
                base_url=self.base_url,
                max_tokens=self.max_tokens,
            )
            content = str(repaired.get("content", "")).strip()
            attempts += 1

    def _critique(self, *, query: str, answer: str) -> dict[str, Any]:
        result = self.llm_callable(
            provider=self.provider,
            api_key=self.api_key,
            model=self.model,
            messages=self._critique_messages(query, answer),
            timeout=self.timeout,
            base_url=self.base_url,
            max_tokens=700,
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
        return {
            "passed": not low and not overfitting["detected"],
            "scores": {key: scores.get(key, 0.0) for key in POQ_SCORE_KEYS},
            "explanation": explanation,
            "raw": raw,
            "overfitting_detected": overfitting["detected"],
            "overfitting_reason": overfitting["reason"],
            "category_failure_detected": category_failure["detected"],
            "category_failure_reason": category_failure["reason"],
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


def _append_failure_reason(explanation: str, reason: str) -> str:
    overfitting_reason = f"Overfitting detected: {reason}."
    if not explanation:
        return overfitting_reason
    return f"{explanation} {overfitting_reason}"


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
