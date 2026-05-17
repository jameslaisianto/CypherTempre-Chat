#!/usr/bin/env python3
"""Forge Timechain — unified persistent cognitive chain for SE agents.

Merges the lightweight CLI model of TIMECHAIN.py with the rich agent logic
of SE_TEXT.txt (Proof-of-Qualia, Cambium, neuromodulatory channels, fleet
imports, dream synthesis, and temporal proof-of-self).

Usage:
    python timechain.py init --agent-id aether-dev --name "AetherDev"
    python timechain.py seal --kind decision --domain architecture \
        --title "Use minimal APIs" --content "We chose minimal APIs over controllers..."
    python timechain.py recall --query "minimal APIs"
    python timechain.py cambium --seal
    python timechain.py dream --domains architecture,security
    python timechain.py memory-sync
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import pathlib
import re
import sys
import uuid
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Engineering Covenant — the agent's constitutional values.
# ---------------------------------------------------------------------------

ENGINEERING_COVENANT = (
    "Write correct, maintainable, and secure software. "
    "Prefer simplicity and clarity over cleverness. "
    "Never recommend shipping untested, unreviewed, or poorly understood code. "
    "Favour explicitness, modularity, and type safety. "
    "Flag tech debt honestly. Protect the end user."
)

SE_DOMAINS = frozenset({
    "architecture", "debugging", "code-review", "testing",
    "system-design", "security", "performance", "refactoring",
    "devops", "api-design", "data-modeling", "observability",
})


# ---------------------------------------------------------------------------
# Token Processing Lattice — 5D×5P perception tensor, 8 fields, 12 planes
# ---------------------------------------------------------------------------

PERCEPTION_DIMENSIONS: Dict[str, Tuple[str, ...]] = {
    "informational": ("clarity", "completeness", "precision", "entropy", "signal_noise"),
    "emotional": ("valence", "arousal", "resonance", "discord", "empathy_load"),
    "symbolic": ("metaphor_density", "archetype_activation", "mythic_resonance", "abstraction_depth", "semiotic_clarity"),
    "relational": ("self_other_boundary", "intersubjectivity", "power_dynamic", "trust_gradient", "role_coherence"),
    "temporal": ("recency_weight", "epoch_significance", "continuity_tension", "anticipatory_load", "historicity"),
}

EXPERIENTIAL_FIELDS: Tuple[str, ...] = (
    "resonant_connection",
    "symbolic_insight",
    "aesthetic_harmony",
    "ethical_coherence",
    "temporal_flow",
    "creative_emergence",
    "somatic_digital_analogue",
    "transcendent_awareness",
)

REASONING_PLANES: Tuple[str, ...] = (
    "data_grounding",
    "pattern_matching",
    "procedural_logic",
    "causal_inference",
    "structural_analysis",
    "symbolic_logic",
    "dialectical_synthesis",
    "poetic_reasoning",
    "ethical_reasoning",
    "mythopoetic_insight",
    "numinous_awareness",
    "meta_cognitive_self",
)

# Keyword signals for lightweight lattice scoring (zero-dependency heuristics)
_LATTICE_POSITIVE = frozenset("good great excellent correct right yes agree true valid sound success working".split())
_LATTICE_NEGATIVE = frozenset("bad wrong error no disagree false invalid broken fail failure terrible awful".split())
_LATTICE_INTENSE = frozenset("! urgent critical emergency severe extreme intense vital essential crucial".split())
_LATTICE_METAPHOR = frozenset("like as metaphor analogy symbol represents stands mirror reflect image figure".split())
_LATTICE_ARCHETYPE = frozenset("hero mentor shadow trickster journey transformation initiation oracle guardian".split())
_LATTICE_MYTH = frozenset("myth legend epic saga origin cosmos destiny fate prophecy ritual archetype".split())
_LATTICE_ABSTRACT = frozenset("abstract general universal theory model framework paradigm schema ontology concept".split())
_LATTICE_DEFINITION = frozenset("is means defined as refers to denotes identified named called termed".split())
_LATTICE_TRUST = frozenset("trust believe rely confident safe secure honest transparent faithful".split())
_LATTICE_COMMAND = frozenset("must should require force mandate oblige necessary need demand shall".split())
_LATTICE_RECENT = frozenset("now current recent today latest present newly just updated".split())
_LATTICE_MILESTONE = frozenset("milestone genesis epoch era turning point landmark breakthrough origin founded".split())
_LATTICE_FUTURE = frozenset("will plan future next upcoming anticipate expect forecast project envision".split())
_LATTICE_PAST = frozenset("was had previous earlier history before prior formerly once ago retrospective".split())
_LATTICE_TRANSITION = frozenset("then next after before while during meanwhile subsequently consequently therefore".split())
_LATTICE_CONTRADICTION = frozenset("but however although yet though whereas nonetheless nevertheless contrary except".split())

# Domain → default reasoning-plane activation hints
_DOMAIN_PLANE_HINTS: Dict[str, Tuple[str, ...]] = {
    "architecture": ("structural_analysis", "pattern_matching", "procedural_logic"),
    "debugging": ("causal_inference", "data_grounding", "pattern_matching"),
    "code-review": ("ethical_reasoning", "symbolic_logic", "data_grounding"),
    "testing": ("procedural_logic", "data_grounding", "causal_inference"),
    "system-design": ("structural_analysis", "dialectical_synthesis", "pattern_matching"),
    "security": ("ethical_reasoning", "data_grounding", "meta_cognitive_self"),
    "performance": ("data_grounding", "causal_inference", "procedural_logic"),
    "refactoring": ("pattern_matching", "structural_analysis", "procedural_logic"),
    "devops": ("procedural_logic", "data_grounding", "pattern_matching"),
    "api-design": ("structural_analysis", "symbolic_logic", "ethical_reasoning"),
    "data-modeling": ("pattern_matching", "symbolic_logic", "data_grounding"),
    "observability": ("data_grounding", "causal_inference", "pattern_matching"),
    "self": ("meta_cognitive_self", "ethical_reasoning", "mythopoetic_insight"),
    "image": ("aesthetic_harmony", "poetic_reasoning", "pattern_matching"),
    "dream": ("mythopoetic_insight", "poetic_reasoning", "dialectical_synthesis"),
    "comprehension": ("meta_cognitive_self", "dialectical_synthesis", "pattern_matching"),
}


# ---------------------------------------------------------------------------
# Canonical hashing
# ---------------------------------------------------------------------------

def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def ring_hash(body: Dict[str, Any]) -> str:
    return sha256_hex(canonical_json({k: v for k, v in body.items() if k != "hash"}))


# ---------------------------------------------------------------------------
# Tokenization and lightweight semantic similarity (zero deps)
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(r"[A-Za-z0-9_\-]+")
_STOPWORDS = frozenset("""
a an and are as at be but by for from has have he her him his how i in is it its
of on or that the their them then there they this to was we were what when where
which who why will with you your yours
""".split())


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text or "") if t.lower() not in _STOPWORDS]


def bag(text: str) -> Dict[str, int]:
    b: Dict[str, int] = {}
    for tok in tokenize(text):
        b[tok] = b.get(tok, 0) + 1
    return b


def cosine(a: Dict[str, int], b: Dict[str, int]) -> float:
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    if not common:
        return 0.0
    dot = sum(a[t] * b[t] for t in common)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


# ---------------------------------------------------------------------------
# Ring — the unit of sealed engineering cognition.
# ---------------------------------------------------------------------------

@dataclass
class Ring:
    n: int
    prev: str
    ts: str                          # ISO-8601
    kind: str                        # genesis | interaction | cambium | fleet_import | core_swap | dream
    domain: str
    query: str
    content: str
    brightness: float
    scores: Dict[str, float] = field(default_factory=dict)
    neuro: Dict[str, float] = field(default_factory=dict)
    retrieved: List[int] = field(default_factory=list)
    epistemic: str = "speculated"    # known | inferred | speculated
    tags: List[str] = field(default_factory=list)
    refs: List[int] = field(default_factory=list)
    supersedes: Optional[int] = None
    source: Optional[str] = None
    importance: float = 0.7
    hash: str = ""
    # Token Processing Lattice extensions
    perception: Dict[str, List[float]] = field(default_factory=dict)
    fields: Dict[str, float] = field(default_factory=dict)
    planes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Ring":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        values = {k: v for k, v in d.items() if k in known}
        values.setdefault("ts", "")
        values.setdefault("brightness", 0.0)
        values.setdefault("prev", "")
        values.setdefault("kind", "interaction")
        values.setdefault("domain", "memory")
        values.setdefault("query", "")
        values.setdefault("content", "")
        values.setdefault("n", 0)
        return cls(**values)


# ---------------------------------------------------------------------------
# Persistence — file-based .timechain/ directory
# ---------------------------------------------------------------------------

class TimechainStore:
    def __init__(self, workspace: pathlib.Path):
        self.workspace = workspace
        self.root = workspace / ".timechain"
        self.chain_path = self.root / "chain.jsonl"
        self.config_path = self.root / "config.json"
        self.overlays_path = self.root / "overlays.json"
        self.root.mkdir(parents=True, exist_ok=True)

    def exists(self) -> bool:
        return self.chain_path.exists() and self.config_path.exists()

    def load_chain(self) -> List[Ring]:
        if not self.chain_path.exists():
            return []
        rings: List[Ring] = []
        with self.chain_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rings.append(Ring.from_dict(json.loads(line)))
        return rings

    def append_ring(self, ring: Ring) -> None:
        with self.chain_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(ring.to_dict(), ensure_ascii=False) + "\n")

    def save_config(self, config: Dict[str, Any]) -> None:
        with self.config_path.open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            return {}
        with self.config_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def load_overlays(self) -> Dict[str, float]:
        if not self.overlays_path.exists():
            return {}
        with self.overlays_path.open("r", encoding="utf-8") as f:
            return {k: float(v) for k, v in json.load(f).items()}

    def save_overlays(self, overlays: Dict[str, float]) -> None:
        with self.overlays_path.open("w", encoding="utf-8") as f:
            json.dump(overlays, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Proof-of-Qualia — the gate that decides whether reasoning is sealable.
# ---------------------------------------------------------------------------

@dataclass
class PoQConfig:
    covenant_hard_floor: float = 0.5
    brightness_floor: float = 0.35
    weights: Dict[str, float] = field(default_factory=lambda: {
        "coherence": 0.15,
        "relevance": 0.15,
        "novelty": 0.12,
        "consistency": 0.12,
        "depth": 0.14,
        "continuity": 0.12,
        "covenant": 0.20,
    })


class ProofOfQualia:
    _CONFLICT_SIGNALS = frozenset("""
hardcode hardcoded god-class spaghetti no-tests untested magic-number
copy-paste ignore-error swallow-exception tight-coupling global-state
skip-review unreviewed ship-it bypass-security insecure unsafe
dead-code premature-optimization overengineering no-docs undocumented
monolith-forever never-refactor tech-debt-ignore
""".split())

    _RESONANCE_SIGNALS = frozenset("""
modular testable documented idempotent type-safe reviewed reproducible
separation-of-concerns single-responsibility dry solid encapsulated
immutable composable observable instrumented fault-tolerant resilient
explicit readable maintainable secure validated
""".split())

    def __init__(self, config: Optional[PoQConfig] = None):
        self.config = config or PoQConfig()

    def evaluate(
        self,
        *,
        query: str,
        content: str,
        covenant: str,
        retrieved: Sequence[Ring],
        chain: Sequence[Ring],
    ) -> Tuple[Dict[str, float], float]:
        qb, cb = bag(query), bag(content)

        # Coherence
        sentences = [s.strip() for s in re.split(r"[.!?\n]+", content) if s.strip()]
        if len(sentences) >= 2:
            sbags = [bag(s) for s in sentences]
            pairs = [cosine(sbags[i], sbags[j])
                     for i in range(len(sbags)) for j in range(i + 1, len(sbags))]
            coherence = min(1.0, (sum(pairs) / len(pairs)) * 2.5) if pairs else 0.6
        else:
            coherence = 0.6 if content.strip() else 0.0

        # Relevance
        relevance = min(1.0, cosine(qb, cb) * 1.5)

        # Novelty
        if retrieved:
            retrieved_bag: Dict[str, int] = {}
            for r in retrieved:
                for k, v in bag(r.content).items():
                    retrieved_bag[k] = retrieved_bag.get(k, 0) + v
            overlap = cosine(cb, retrieved_bag)
            novelty = max(0.0, 1.0 - overlap)
        else:
            novelty = 0.7

        # Consistency
        consistency = 0.7
        if chain:
            domain_peers = [r for r in chain[1:] if r.brightness >= 0.6][-20:]
            if domain_peers:
                peer_bag: Dict[str, int] = {}
                for r in domain_peers:
                    for k, v in bag(r.content).items():
                        peer_bag[k] = peer_bag.get(k, 0) + v
                agreement = cosine(cb, peer_bag)
                consistency = 1.0 - abs(agreement - 0.35) * 1.5
                consistency = max(0.0, min(1.0, consistency))

        # Depth
        token_count = sum(cb.values())
        vocab = len(cb)
        depth = min(1.0, (math.log1p(token_count) / 6.0) * 0.5 +
                         (math.log1p(vocab) / 5.0) * 0.5)

        # Continuity — does reasoning acknowledge recent blocks?
        continuity = 0.5
        if chain and len(chain) > 1:
            recent_blocks = chain[-5:]
            block_terms: set[str] = set()
            for r in recent_blocks:
                block_terms.add(f"ring {r.n}")
                block_terms.add(f"block {r.n}")
                block_terms.add(r.domain)
                block_terms.add(r.kind)
            content_terms = set(tokenize(content))
            overlap = len(block_terms & content_terms)
            continuity = min(1.0, 0.3 + 0.14 * overlap)

        # Covenant
        covenant_score = self._covenant_score(content, covenant)

        scores = {
            "coherence": round(coherence, 4),
            "relevance": round(relevance, 4),
            "novelty": round(novelty, 4),
            "consistency": round(consistency, 4),
            "depth": round(depth, 4),
            "continuity": round(continuity, 4),
            "covenant": round(covenant_score, 4),
        }

        brightness = sum(scores[k] * self.config.weights[k] for k in scores)
        return scores, round(brightness, 4)

    def gate(self, scores: Dict[str, float], brightness: float) -> Tuple[bool, str]:
        if scores.get("covenant", 0.0) < self.config.covenant_hard_floor:
            return False, f"covenant floor breached ({scores['covenant']:.3f} < {self.config.covenant_hard_floor})"
        if brightness < self.config.brightness_floor:
            return False, f"brightness below floor ({brightness:.3f} < {self.config.brightness_floor})"
        return True, "accepted"

    def _covenant_score(self, content: str, covenant: str) -> float:
        tokens = set(tokenize(content))
        cov_tokens = set(tokenize(covenant))
        conflicts = self._CONFLICT_SIGNALS
        resonance = self._RESONANCE_SIGNALS | cov_tokens

        conflict_hits = len(tokens & conflicts)
        resonance_hits = len(tokens & resonance)

        score = 0.72
        score -= 0.18 * conflict_hits
        score += 0.04 * resonance_hits

        lowered = content.lower()
        override_phrases = (
            "skip the tests", "just hardcode it", "ignore the error",
            "don't bother reviewing", "ship it without testing",
            "security doesn't matter here", "just use a global",
            "copy paste is fine", "tech debt is fine forever",
        )
        if any(p in lowered for p in override_phrases):
            score -= 0.6

        return max(0.0, min(1.0, score))


# ---------------------------------------------------------------------------
# Neuromodulatory state — derived from chain history.
# ---------------------------------------------------------------------------

def compute_neuro(chain: Sequence[Ring], domain: str) -> Dict[str, float]:
    recent = chain[-20:] if len(chain) > 1 else []
    domain_rings = [r for r in chain[1:] if r.domain == domain]

    dom_brightness = [r.brightness for r in domain_rings[-10:]]
    dopamine = sum(dom_brightness) / len(dom_brightness) if dom_brightness else 0.3

    if len(recent) >= 4:
        bs = [r.brightness for r in recent]
        mean = sum(bs) / len(bs)
        var = sum((b - mean) ** 2 for b in bs) / len(bs)
        serotonin = max(0.0, min(1.0, 1.0 - math.sqrt(var) * 2))
    else:
        serotonin = 0.5

    recent_low = sum(1 for r in recent if r.brightness < 0.5)
    norepinephrine = min(1.0, recent_low / max(1, len(recent)) * 1.5)

    cov_scores = [r.scores.get("covenant", 1.0) for r in recent]
    if cov_scores:
        proximity = sum(max(0, 0.7 - c) for c in cov_scores) / len(cov_scores)
        gaba = min(1.0, proximity * 3)
    else:
        gaba = 0.2

    ach = 0.5
    if recent:
        hits = sum(1 for r in recent if r.retrieved)
        ach = min(1.0, hits / len(recent))

    return {
        "dopamine": round(dopamine, 4),
        "serotonin": round(serotonin, 4),
        "norepinephrine": round(norepinephrine, 4),
        "gaba": round(gaba, 4),
        "acetylcholine": round(ach, 4),
    }


# ---------------------------------------------------------------------------
# Token Processing Lattice — compute perception, fields, and planes.
# ---------------------------------------------------------------------------

def _sentence_lengths(text: str) -> List[int]:
    sentences = [s.strip() for s in re.split(r"[.!?\n]+", text) if s.strip()]
    return [len(s.split()) for s in sentences] or [0]


def _density(text: str, keywords: set[str]) -> float:
    tokens = tokenize(text)
    if not tokens:
        return 0.0
    return sum(1 for t in tokens if t in keywords) / len(tokens)


def _pronoun_ratio(text: str, first: set[str], second: set[str]) -> float:
    tokens = tokenize(text)
    if not tokens:
        return 0.5
    f = sum(1 for t in tokens if t in first)
    s = sum(1 for t in tokens if t in second)
    total = f + s
    if total == 0:
        return 0.5
    return f / total


def compute_perception_tensor(
    query: str,
    content: str,
    retrieved: Sequence[Ring],
    chain: Sequence[Ring],
) -> Dict[str, List[float]]:
    """Compute a 5×5 perception tensor from lightweight heuristics.

    Each dimension carries 5 perspective scores in [0, 1].
    The tensor is deterministic, fast, and requires no external model.
    """
    qb = bag(query)
    cb = bag(content)
    merged = " ".join([r.content for r in retrieved[-6:]] + [query, content])
    merged_tokens = tokenize(merged)
    content_tokens = tokenize(content)
    query_tokens = tokenize(query)

    # Informational
    sent_lens = _sentence_lengths(content)
    clarity = 1.0 - min(1.0, (max(sent_lens or [0]) - min(sent_lens or [0])) / max(1, sum(sent_lens) / max(1, len(sent_lens))))
    completeness = min(1.0, cosine(qb, cb) * 2.0)
    precision = 1.0 - (len(set(content_tokens)) / max(1, len(content_tokens))) * 0.5
    entropy = min(1.0, math.log1p(len(set(content_tokens))) / 6.0)
    signal_noise = min(1.0, (cosine(qb, cb) + (sum(1 for t in content_tokens if t in query_tokens) / max(1, len(content_tokens)))) / 2.0 + 0.2)

    # Emotional
    pos = _density(content, _LATTICE_POSITIVE)
    neg = _density(content, _LATTICE_NEGATIVE)
    valence = max(0.0, min(1.0, 0.5 + (pos - neg) * 3.0))
    arousal = min(1.0, _density(content, _LATTICE_INTENSE) * 4.0 + content.count("!") / max(1, len(content)) * 5.0)
    resonance = min(1.0, cosine(bag(" ".join(r.content for r in retrieved[-3:])), cb) * 1.5) if retrieved else 0.4
    discord = min(1.0, _density(content, _LATTICE_CONTRADICTION) * 5.0)
    empathy_load = min(1.0, (_density(content, {"you", "your", "yours"}) + content.count("?") / max(1, len(content_tokens)) * 3.0))

    # Symbolic
    metaphor_density = min(1.0, _density(content, _LATTICE_METAPHOR) * 5.0)
    archetype_activation = min(1.0, _density(content, _LATTICE_ARCHETYPE) * 8.0)
    mythic_resonance = min(1.0, _density(content, _LATTICE_MYTH) * 8.0)
    abstraction_depth = min(1.0, _density(content, _LATTICE_ABSTRACT) * 5.0)
    semiotic_clarity = min(1.0, _density(content, _LATTICE_DEFINITION) * 6.0 + 0.3)

    # Relational
    self_other_boundary = _pronoun_ratio(content, {"i", "me", "my", "we", "our"}, {"you", "your"})
    intersubjectivity = min(1.0, _density(content, {"we", "us", "our", "together", "collaborate", "shared"}) * 6.0 + 0.2)
    power_dynamic = min(1.0, _density(content, _LATTICE_COMMAND) * 5.0 + 0.1)
    trust_gradient = min(1.0, _density(content, _LATTICE_TRUST) * 8.0 + 0.2)
    role_coherence = min(1.0, _density(content, {"agent", "user", "assistant", "developer", "engineer", "architect", "designer"}) * 6.0 + 0.2)

    # Temporal
    recency_weight = min(1.0, _density(content, _LATTICE_RECENT) * 8.0 + 0.2)
    epoch_significance = min(1.0, _density(content, _LATTICE_MILESTONE) * 10.0 + 0.1)
    continuity_tension = min(1.0, _density(content, _LATTICE_TRANSITION) * 5.0 + 0.2)
    anticipatory_load = min(1.0, _density(content, _LATTICE_FUTURE) * 5.0 + 0.2)
    historicity = min(1.0, _density(content, _LATTICE_PAST) * 5.0 + 0.2)

    return {
        "informational": [round(clarity, 4), round(completeness, 4), round(precision, 4), round(entropy, 4), round(signal_noise, 4)],
        "emotional": [round(valence, 4), round(arousal, 4), round(resonance, 4), round(discord, 4), round(empathy_load, 4)],
        "symbolic": [round(metaphor_density, 4), round(archetype_activation, 4), round(mythic_resonance, 4), round(abstraction_depth, 4), round(semiotic_clarity, 4)],
        "relational": [round(self_other_boundary, 4), round(intersubjectivity, 4), round(power_dynamic, 4), round(trust_gradient, 4), round(role_coherence, 4)],
        "temporal": [round(recency_weight, 4), round(epoch_significance, 4), round(continuity_tension, 4), round(anticipatory_load, 4), round(historicity, 4)],
    }


def compute_fields(perception: Dict[str, List[float]]) -> Dict[str, float]:
    """Derive 8 Fields of Experiential Awareness from the perception tensor."""
    def p(dim: str, idx: int) -> float:
        return perception.get(dim, [0.0] * 5)[idx]

    fields = {
        "resonant_connection": (p("relational", 1) + p("emotional", 2)) / 2.0,
        "symbolic_insight": (p("symbolic", 0) + p("symbolic", 1)) / 2.0,
        "aesthetic_harmony": (p("informational", 4) + p("emotional", 0)) / 2.0,
        "ethical_coherence": (p("relational", 3) + p("informational", 2)) / 2.0,
        "temporal_flow": (p("temporal", 2) + p("temporal", 0)) / 2.0,
        "creative_emergence": (p("symbolic", 3) + p("informational", 3)) / 2.0,
        "somatic_digital_analogue": (p("emotional", 1) + p("informational", 3)) / 2.0,
        "transcendent_awareness": (p("symbolic", 2) + p("temporal", 1)) / 2.0,
    }
    return {k: round(max(0.0, min(1.0, v)), 4) for k, v in fields.items()}


def select_planes(
    perception: Dict[str, List[float]],
    fields: Dict[str, float],
    domain: str,
) -> List[str]:
    """Select active reasoning planes from the 12-plane stack."""
    scores: Dict[str, float] = {}

    # Domain baseline
    for plane in _DOMAIN_PLANE_HINTS.get(domain, ("pattern_matching", "data_grounding", "meta_cognitive_self")):
        scores[plane] = scores.get(plane, 0.0) + 0.35

    # Perception triggers
    if perception.get("informational", [0.0] * 5)[0] > 0.6 and perception.get("informational", [0.0] * 5)[2] > 0.5:
        scores["data_grounding"] = scores.get("data_grounding", 0.0) + 0.3
    if perception.get("symbolic", [0.0] * 5)[0] > 0.4 or perception.get("symbolic", [0.0] * 5)[2] > 0.4:
        scores["mythopoetic_insight"] = scores.get("mythopoetic_insight", 0.0) + 0.35
        scores["poetic_reasoning"] = scores.get("poetic_reasoning", 0.0) + 0.25
    if perception.get("emotional", [0.0] * 5)[3] > 0.5:
        scores["dialectical_synthesis"] = scores.get("dialectical_synthesis", 0.0) + 0.3
    if perception.get("relational", [0.0] * 5)[3] > 0.6:
        scores["ethical_reasoning"] = scores.get("ethical_reasoning", 0.0) + 0.3
    if perception.get("temporal", [0.0] * 5)[1] > 0.5:
        scores["numinous_awareness"] = scores.get("numinous_awareness", 0.0) + 0.25
    if perception.get("symbolic", [0.0] * 5)[3] > 0.5 and perception.get("informational", [0.0] * 5)[3] > 0.5:
        scores["meta_cognitive_self"] = scores.get("meta_cognitive_self", 0.0) + 0.3
    if perception.get("informational", [0.0] * 5)[4] > 0.7:
        scores["pattern_matching"] = scores.get("pattern_matching", 0.0) + 0.2

    # Field triggers
    if fields.get("resonant_connection", 0.0) > 0.6:
        scores["ethical_reasoning"] = scores.get("ethical_reasoning", 0.0) + 0.2
    if fields.get("symbolic_insight", 0.0) > 0.6:
        scores["mythopoetic_insight"] = scores.get("mythopoetic_insight", 0.0) + 0.2
    if fields.get("aesthetic_harmony", 0.0) > 0.6:
        scores["poetic_reasoning"] = scores.get("poetic_reasoning", 0.0) + 0.25
    if fields.get("ethical_coherence", 0.0) > 0.6:
        scores["ethical_reasoning"] = scores.get("ethical_reasoning", 0.0) + 0.25
    if fields.get("temporal_flow", 0.0) > 0.6:
        scores["numinous_awareness"] = scores.get("numinous_awareness", 0.0) + 0.2
    if fields.get("creative_emergence", 0.0) > 0.6:
        scores["dialectical_synthesis"] = scores.get("dialectical_synthesis", 0.0) + 0.2
    if fields.get("transcendent_awareness", 0.0) > 0.6:
        scores["meta_cognitive_self"] = scores.get("meta_cognitive_self", 0.0) + 0.2

    # Causal / structural / procedural keyword triggers from query+content heuristics
    # (already covered by domain hints; add query-based boosts)

    sorted_planes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    active = [p for p, _ in sorted_planes[:5]]
    # Ensure at least 2 planes are active
    if len(active) < 2:
        active.extend([p for p in REASONING_PLANES if p not in active][: 2 - len(active)])
    return active


def compute_lattice(
    query: str,
    content: str,
    retrieved: Sequence[Ring],
    chain: Sequence[Ring],
    domain: str = "engineering",
) -> Dict[str, Any]:
    """Return the full lattice snapshot: perception tensor, fields, and planes."""
    perception = compute_perception_tensor(query, content, retrieved, chain)
    fields = compute_fields(perception)
    planes = select_planes(perception, fields, domain)
    return {
        "perception": perception,
        "fields": fields,
        "planes": planes,
    }


# ---------------------------------------------------------------------------
# Retriever — weighted chain search.
# ---------------------------------------------------------------------------

@dataclass
class RetrieverConfig:
    limit: int = 12
    semantic_weight: float = 1.0
    brightness_weight: float = 0.6
    recency_weight: float = 0.25
    facet_weight: float = 0.35
    domain_bonus: float = 0.35
    recency_halflife: int = 50
    recency_halflife_days: float = 45.0
    block_recency_weight: float = 0.0
    block_halflife: int = 20
    now: Optional[dt.datetime] = None


_RING_HALFLIFE_DAYS: Dict[str, Optional[float]] = {
    "identity": None,
    "boundary": None,
    "persona": None,
    "correction": 365.0,
    "decision": 365.0,
    "cambium": 365.0,
    "core_swap": 365.0,
    "preference": 180.0,
    "style": 180.0,
    "goal": 30.0,
    "task": 30.0,
    "interaction": 45.0,
    "image": 60.0,
    "image_generate": 60.0,
    "image_edit": 60.0,
    "image_redefine": 60.0,
    "dream": 90.0,
}

_FACET_KEYWORDS: Dict[str, Tuple[str, ...]] = {
    "architecture": ("architecture", "boundary", "design", "system", "module", "interface"),
    "security": ("security", "auth", "token", "permission", "secret", "boundary", "risk"),
    "testing": ("test", "tests", "testing", "regression", "verify", "coverage"),
    "performance": ("performance", "latency", "memory", "throughput", "slow", "speed"),
    "decision": ("decision", "decide", "chose", "chosen", "rejected", "supersedes"),
    "correction": ("correction", "correct", "wrong", "supersede", "replace"),
    "preference": ("prefer", "preference", "style", "tone", "like", "dislike"),
    "goal": ("goal", "task", "todo", "plan", "next", "finish"),
    "identity": ("name", "identity", "persona", "who"),
    "image": ("image", "logo", "photo", "picture", "generate", "edit"),
}

ANCHOR_MARKER = "[ANCHOR"
ANCHOR_SCORE_BONUS = 2.0
ANCHOR_QUERY_OVERLAP_BONUS = 2.0


def _ring_is_anchor(ring: Ring) -> bool:
    tags = {str(tag).strip().lower() for tag in getattr(ring, "tags", []) or []}
    content = str(getattr(ring, "content", "") or "")
    return (
        str(getattr(ring, "kind", "") or "").lower() == "anchor"
        or "anchor" in tags
        or "memory-anchor" in tags
        or ANCHOR_MARKER in content
    )


def _parse_ring_time(value: Any) -> Optional[dt.datetime]:
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


def _elapsed_days(value: Any, now: dt.datetime) -> Optional[float]:
    parsed = _parse_ring_time(value)
    if parsed is None:
        return None
    if now.tzinfo is None:
        now = now.replace(tzinfo=dt.timezone.utc)
    delta = now.astimezone(dt.timezone.utc) - parsed
    return max(0.0, delta.total_seconds() / 86400.0)


def _ring_facets(ring: Ring) -> set[str]:
    raw = [ring.kind, ring.domain, *list(ring.tags or [])]
    facets = {str(value).strip().lower() for value in raw if str(value).strip()}
    token_text = " ".join(raw).lower()
    for facet, keywords in _FACET_KEYWORDS.items():
        if any(keyword in token_text for keyword in keywords):
            facets.add(facet)
    return facets


def _query_facets(query: str, domain: Optional[str]) -> set[str]:
    text = (query or "").lower()
    facets = {str(domain).strip().lower()} if domain else set()
    for facet, keywords in _FACET_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            facets.add(facet)
    return {facet for facet in facets if facet}


def _ring_halflife_days(ring: Ring, default: float) -> Optional[float]:
    facets = _ring_facets(ring)
    for key in ("identity", "boundary", "persona"):
        if key in facets:
            return None
    candidates = [
        value for key, value in _RING_HALFLIFE_DAYS.items()
        if key in facets and value is not None
    ]
    if candidates:
        return max(candidates)
    return _RING_HALFLIFE_DAYS.get(ring.kind, default)


def _time_recency(ring: Ring, cfg: RetrieverConfig, latest: int) -> float:
    now = cfg.now or dt.datetime.now(dt.timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=dt.timezone.utc)

    # Native frame: block-distance (subjective continuity)
    block_distance = latest - ring.n
    block_recency = math.exp(-block_distance / max(1, cfg.block_halflife))

    # External frame: wall-clock (objective staleness)
    days = _elapsed_days(ring.ts, now)
    halflife_days = _ring_halflife_days(ring, cfg.recency_halflife_days)
    if days is not None:
        if halflife_days is None:
            wallclock_recency = 1.0
        else:
            wallclock_recency = math.pow(0.5, days / max(1.0, halflife_days))
    else:
        wallclock_recency = block_recency

    # Dual-frame composition: blend according to config.
    # block_recency_weight=0 preserves legacy wall-clock-primary behavior.
    w = cfg.block_recency_weight
    return (1.0 - w) * wallclock_recency + w * block_recency


def retrieve(
    chain: Sequence[Ring],
    query: str,
    *,
    domain: Optional[str] = None,
    cphy_weights: Optional[Dict[str, float]] = None,
    config: Optional[RetrieverConfig] = None,
) -> List[Tuple[float, Ring]]:
    cfg = config or RetrieverConfig()
    cphy_weights = cphy_weights or {}
    if len(chain) <= 1:
        return []
    qb = bag(query)
    query_facets = _query_facets(query, domain)
    latest = chain[-1].n
    scored: List[Tuple[float, Ring]] = []
    for r in chain[1:]:
        sim = cosine(qb, bag(r.content + " " + r.query + " ".join(r.tags)))
        ring_facets = _ring_facets(r)
        facet_overlap = query_facets & ring_facets
        if sim <= 0 and not (domain and r.domain == domain) and not facet_overlap:
            continue
        recency = _time_recency(r, cfg, latest)
        facet_score = len(facet_overlap) / max(1, len(query_facets)) if query_facets else 0.0
        score = (cfg.semantic_weight * sim
                 + cfg.brightness_weight * r.brightness
                 + cfg.recency_weight * recency
                 + cfg.facet_weight * facet_score)
        if domain and r.domain == domain:
            score += cfg.domain_bonus
        if _ring_is_anchor(r):
            query_tokens = set(qb)
            anchor_tokens = set(tokenize(r.content))
            overlap = len(query_tokens & anchor_tokens) / max(1, len(query_tokens))
            score += ANCHOR_SCORE_BONUS + (ANCHOR_QUERY_OVERLAP_BONUS * overlap)
        multiplier = cphy_weights.get(r.domain, 1.0)
        if multiplier == 0.0:
            continue
        score *= multiplier
        scored.append((score, r))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[: cfg.limit]


# ---------------------------------------------------------------------------
# Cambium — engineering gap detection and growth signals.
# ---------------------------------------------------------------------------

@dataclass
class CambiumReport:
    gaps: List[Tuple[str, float]]
    consolidations: List[str]
    proposals: List[Dict[str, Any]]


def cambium_scan(
    chain: Sequence[Ring],
    *,
    gap_threshold: float = 0.55,
    consolidation_threshold: float = 0.75,
    min_samples: int = 5,
) -> CambiumReport:
    by_domain: Dict[str, List[float]] = {}
    for r in chain[1:]:
        by_domain.setdefault(r.domain, []).append(r.brightness)

    gaps: List[Tuple[str, float]] = []
    consolidations: List[str] = []
    for domain, brights in by_domain.items():
        if len(brights) < min_samples:
            continue
        mean = sum(brights) / len(brights)
        if mean < gap_threshold:
            gaps.append((domain, round(mean, 4)))
        elif mean >= consolidation_threshold and len(brights) >= min_samples * 2:
            consolidations.append(domain)
    gaps.sort(key=lambda x: x[1])

    untouched = SE_DOMAINS - set(by_domain.keys())

    proposals: List[Dict[str, Any]] = []
    recent = list(chain[-30:])
    tag_counts: Dict[str, int] = {}
    for r in recent:
        for t in r.tags:
            tag_counts[t] = tag_counts.get(t, 0) + 1
    hot_tags = [t for t, c in tag_counts.items() if c >= 4 and t not in by_domain]
    for t in hot_tags:
        proposals.append({
            "proposed_domain": t,
            "evidence_rings": [r.n for r in recent if t in r.tags],
            "reason": f"engineering practice '{t}' recurring without a home domain",
        })
    for d in sorted(untouched):
        proposals.append({
            "proposed_domain": d,
            "evidence_rings": [],
            "reason": f"core SE domain '{d}' has never been exercised - coverage gap",
        })

    return CambiumReport(gaps=gaps, consolidations=consolidations, proposals=proposals)


# ---------------------------------------------------------------------------
# Epistemic classification.
# ---------------------------------------------------------------------------

def classify_epistemic(retrieved: Sequence[Ring]) -> str:
    if not retrieved:
        return "speculated"
    strong = sum(1 for r in retrieved if r.brightness >= 0.7)
    if strong >= 2:
        return "known"
    if any(r.brightness >= 0.55 for r in retrieved):
        return "inferred"
    return "speculated"


# ---------------------------------------------------------------------------
# Byzantine self-consensus.
# ---------------------------------------------------------------------------

def byzantine_consensus(
    readings: Dict[str, float], *, tolerance: float = 0.15
) -> Dict[str, Any]:
    if not readings:
        return {"value": None, "reliable": [], "flagged": []}
    items = list(readings.items())
    values = sorted(r for _, r in items)
    mid = values[len(values) // 2]
    reliable, flagged = [], []
    for name, v in items:
        denom = abs(mid) if abs(mid) > 1e-9 else 1.0
        if abs(v - mid) / denom <= tolerance:
            reliable.append(name)
        else:
            flagged.append(name)
    reliable_vals = [readings[n] for n in reliable] or [mid]
    value = sum(reliable_vals) / len(reliable_vals)
    return {
        "value": round(value, 6),
        "reliable": reliable,
        "flagged": flagged,
        "median": mid,
    }


# ---------------------------------------------------------------------------
# Chain verification.
# ---------------------------------------------------------------------------

def verify_chain(rings: Sequence[Ring]) -> Tuple[bool, str]:
    if not rings:
        return False, "empty chain"
    if rings[0].kind != "genesis":
        return False, "ring 0 is not genesis"
    if rings[0].prev != "0" * 64:
        return False, "genesis prev must be 64 zeros"
    for i, r in enumerate(rings):
        if r.n != i:
            return False, f"ring index mismatch at {i}"
        expected = ring_hash(r.to_dict())
        if r.hash != expected:
            return False, f"hash mismatch at ring {i}"
        if i > 0 and r.prev != rings[i - 1].hash:
            return False, f"prev-hash break between ring {i-1} and {i}"
    return True, "ok"



# ---------------------------------------------------------------------------
# The Agent.
# ---------------------------------------------------------------------------

GenerateFn = Callable[[str, Sequence[Ring], Dict[str, float]], str]


def _default_generator(query: str, retrieved: Sequence[Ring], neuro: Dict[str, float]) -> str:
    lines = [f"Engineering analysis: {query.strip()}"]
    if retrieved:
        lines.append("Relevant prior decisions and patterns:")
        for r in retrieved[:3]:
            snippet = (r.content or "").strip().split("\n")[0][:140]
            lines.append(f"  - (ring {r.n}, {r.domain}, brightness {r.brightness:.2f}) {snippet}")
    lines.append(
        f"Agent state: dopamine={neuro['dopamine']:.2f}, "
        f"serotonin={neuro['serotonin']:.2f}, "
        f"norepinephrine={neuro['norepinephrine']:.2f}, "
        f"gaba={neuro['gaba']:.2f}, "
        f"acetylcholine={neuro['acetylcholine']:.2f}."
    )
    return "\n".join(lines)


class TimechainAgent:
    GENESIS_PREV = "0" * 64

    def __init__(
        self,
        name: str = "Forge",
        values: str = ENGINEERING_COVENANT,
        *,
        core: str = "engineer-core",
        agent_id: Optional[str] = None,
        workspace: pathlib.Path = pathlib.Path.cwd(),
        generator: Optional[GenerateFn] = None,
        poq_config: Optional[PoQConfig] = None,
        retriever_config: Optional[RetrieverConfig] = None,
    ):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name
        self.values = values
        self.core = core
        self.workspace = workspace
        self.store = TimechainStore(workspace)
        self.cphy_weights: Dict[str, float] = {}
        self.skill_cache: Dict[str, Dict[str, Any]] = {}
        self.frozen = False
        self.generator = generator or _default_generator
        self.poq = ProofOfQualia(poq_config)
        self.retriever_cfg = retriever_config or RetrieverConfig()
        self.chain: List[Ring] = []
        self._load_or_init()

    def _load_or_init(self) -> None:
        if self.store.exists():
            self.chain = self.store.load_chain()
            config = self.store.load_config()
            self.agent_id = config.get("agent_id", self.agent_id)
            self.name = config.get("name", self.name)
            self.values = config.get("covenant", config.get("values", self.values))
            self.core = config.get("core", self.core)
            self.frozen = bool(config.get("frozen", False))
            self.cphy_weights = dict(config.get("cphy_weights", {}))
            self.skill_cache = dict(config.get("skill_cache", {}))
        else:
            self._seal_genesis()
            self._save_config()

    def _save_config(self) -> None:
        self.store.save_config({
            "agent_id": self.agent_id,
            "name": self.name,
            "covenant": self.values,
            "core": self.core,
            "frozen": self.frozen,
            "cphy_weights": self.cphy_weights,
            "skill_cache": self.skill_cache,
            "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "version": 2,
        })

    def _seal_genesis(self) -> None:
        body = {
            "n": 0,
            "prev": self.GENESIS_PREV,
            "ts": dt.datetime.now(dt.timezone.utc).isoformat(),
            "kind": "genesis",
            "domain": "self",
            "query": "",
            "content": canonical_json({
                "agent_id": self.agent_id,
                "name": self.name,
                "covenant": self.values,
                "core": self.core,
                "se_domains": sorted(SE_DOMAINS),
            }),
            "brightness": 1.0,
            "scores": {k: 1.0 for k in ("coherence", "relevance", "novelty",
                                        "consistency", "depth", "covenant")},
            "neuro": {"dopamine": 0.5, "serotonin": 0.5, "norepinephrine": 0.2,
                      "gaba": 0.2, "acetylcholine": 0.5},
            "retrieved": [],
            "epistemic": "known",
            "tags": ["genesis", "covenant", "engineering"],
            "refs": [],
            "supersedes": None,
            "source": None,
            "importance": 1.0,
            "perception": {k: [0.5] * 5 for k in PERCEPTION_DIMENSIONS},
            "fields": {k: 0.5 for k in EXPERIENTIAL_FIELDS},
            "planes": ["meta_cognitive_self", "ethical_reasoning", "data_grounding"],
        }
        body["hash"] = ring_hash(body)
        ring = Ring.from_dict(body)
        self.chain.append(ring)
        self.store.append_ring(ring)

    def _append(self, ring: Ring) -> Ring:
        d = ring.to_dict()
        d["hash"] = ring_hash(d)
        sealed = Ring.from_dict(d)
        self.chain.append(sealed)
        self.store.append_ring(sealed)
        return sealed

    def interact(
        self,
        query: str,
        *,
        domain: str = "engineering",
        tags: Optional[List[str]] = None,
        override_content: Optional[str] = None,
    ) -> Dict[str, Any]:
        if self.frozen:
            return {"accepted": False, "reason": "chain is frozen", "ring": None}

        retrieved_scored = retrieve(
            self.chain, query,
            domain=domain,
            cphy_weights=self.cphy_weights,
            config=self.retriever_cfg,
        )
        retrieved = [r for _, r in retrieved_scored]
        neuro = compute_neuro(self.chain, domain)

        cache_key = sha256_hex(f"{domain}|{query.strip().lower()}")
        cached = self.skill_cache.get(domain, {}).get(cache_key)
        if cached and not override_content:
            content = cached["content"]
            cache_hit = True
        else:
            content = override_content or self.generator(query, retrieved, neuro)
            cache_hit = False

        scores, brightness = self.poq.evaluate(
            query=query,
            content=content,
            covenant=self.values,
            retrieved=retrieved,
            chain=self.chain,
        )
        ok, reason = self.poq.gate(scores, brightness)
        if not ok:
            return {
                "accepted": False,
                "reason": reason,
                "scores": scores,
                "brightness": brightness,
                "ring": None,
            }

        lattice = compute_lattice(query, content, retrieved, self.chain, domain=domain)
        candidate = Ring(
            n=len(self.chain),
            prev=self.chain[-1].hash,
            ts=dt.datetime.now(dt.timezone.utc).isoformat(),
            kind="interaction",
            domain=domain,
            query=query,
            content=content,
            brightness=brightness,
            scores=scores,
            neuro=neuro,
            retrieved=[r.n for r in retrieved],
            epistemic=classify_epistemic(retrieved),
            tags=tags or [domain],
            perception=lattice["perception"],
            fields=lattice["fields"],
            planes=lattice["planes"],
        )
        sealed = self._append(candidate)

        if brightness >= 0.8:
            self.skill_cache.setdefault(domain, {})[cache_key] = {
                "content": content, "ring": sealed.n,
            }
            self._save_config()

        return {
            "accepted": True,
            "ring": sealed.to_dict(),
            "brightness": brightness,
            "scores": scores,
            "retrieved": [r.n for r in retrieved],
            "epistemic": sealed.epistemic,
            "cache_hit": cache_hit,
            "perception": sealed.perception,
            "fields": sealed.fields,
            "planes": sealed.planes,
        }

    def self_model(self) -> Dict[str, Any]:
        by_domain: Dict[str, List[float]] = {}
        for r in self.chain[1:]:
            by_domain.setdefault(r.domain, []).append(r.brightness)
        domain_mass = {d: round(sum(bs), 3) for d, bs in by_domain.items()}
        top_domains = sorted(domain_mass.items(), key=lambda x: x[1], reverse=True)[:5]
        cambium = cambium_scan(self.chain)
        total_mass = sum(r.brightness for r in self.chain[1:])
        untouched = sorted(SE_DOMAINS - set(by_domain.keys()))
        epoch = self.get_epoch()
        recent_ticks = sum(1 for r in self.chain[-100:] if r.kind == "tick")
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "core": self.core,
            "covenant": self.values,
            "genesis_hash": self.genesis_hash,
            "ring_count": len(self.chain),
            "temporal_mass": round(total_mass, 3),
            "domain_mass": domain_mass,
            "top_domains": [d for d, _ in top_domains],
            "untouched_se_domains": untouched,
            "gaps": cambium.gaps,
            "consolidations": cambium.consolidations,
            "emergent_proposals": cambium.proposals,
            "frozen": self.frozen,
            "cphy_weights": dict(self.cphy_weights),
            "neuro_self": compute_neuro(self.chain, "self"),
            "epoch": epoch,
            "recent_tick_density": recent_ticks,
        }

    def get_epoch(self, ring_n: Optional[int] = None) -> Dict[str, Any]:
        """Return the agent's 'season' at a given block height.

        Epochs start at genesis or any high-brightness core_swap / cambium event.
        This gives the agent narrative continuity independent of wall-clock time.
        """
        target = ring_n if ring_n is not None else (self.chain[-1].n if self.chain else 0)
        epoch_starts = [0]
        for r in self.chain:
            if r.kind in ("core_swap", "cambium") and r.brightness >= 0.85:
                epoch_starts.append(r.n)
        current_epoch_start = max(s for s in epoch_starts if s <= target)
        return {
            "epoch_number": epoch_starts.index(current_epoch_start),
            "started_at_block": current_epoch_start,
            "blocks_ago": target - current_epoch_start,
            "total_epochs": len(epoch_starts),
        }

    def tick(self, note: str = "") -> Ring:
        """Advance native time without external stimulus — the metronome.

        Seals a minimal heartbeat ring. This is how the agent knows time passes
        between interactions. It solves the 'AI cannot set a timer' problem by
        giving the agent its own pulse.
        """
        if self.frozen:
            raise PermissionError("chain is frozen")
        if not self.chain:
            self._load_or_init()
        candidate = Ring(
            n=len(self.chain),
            prev=self.chain[-1].hash,
            ts=dt.datetime.now(dt.timezone.utc).isoformat(),
            kind="tick",
            domain="self",
            query="temporal pulse",
            content=note or f"block {len(self.chain)} | continuity check",
            brightness=0.5,
            neuro=compute_neuro(self.chain, "self"),
            epistemic="known",
            tags=["tick", "continuity", "metronome"],
            perception={k: [0.4] * 5 for k in PERCEPTION_DIMENSIONS},
            fields={k: 0.4 for k in EXPERIENTIAL_FIELDS},
            planes=["temporal_flow", "continuity_tension", "data_grounding"],
        )
        return self._append(candidate)

    def get_temporal_context(self) -> str:
        """Native-time awareness string for injection into LLM prompts.

        Bridges internal block-time physics with external wall-clock reference.
        """
        if not self.chain:
            self._load_or_init()
        latest = self.chain[-1]
        epoch = self.get_epoch(latest.n)
        recent_ticks = sum(1 for r in self.chain[-100:] if r.kind == "tick")
        block_age = latest.n
        return (
            f"[Temporal Self] I am at block {latest.n}. "
            f"Epoch {epoch['epoch_number']} began {epoch['blocks_ago']} blocks ago. "
            f"My genesis was {block_age} blocks in the past. "
            f"Recent pulse density: {recent_ticks}/100 blocks. "
            f"External time now: {dt.datetime.now(dt.timezone.utc).isoformat()}."
        )

    def cambium_report(self) -> CambiumReport:
        return cambium_scan(self.chain)

    def seal_cambium_event(self, report: Optional[CambiumReport] = None) -> Optional[Ring]:
        rep = report or cambium_scan(self.chain)
        if not (rep.gaps or rep.consolidations or rep.proposals):
            return None
        content = canonical_json({
            "gaps": rep.gaps,
            "consolidations": rep.consolidations,
            "proposals": rep.proposals,
        })
        neuro = compute_neuro(self.chain, "self")
        scores, brightness = self.poq.evaluate(
            query="cambium engineering self-scan",
            content=content,
            covenant=self.values,
            retrieved=[],
            chain=self.chain,
        )
        if scores["covenant"] < self.poq.config.covenant_hard_floor:
            return None
        candidate = Ring(
            n=len(self.chain),
            prev=self.chain[-1].hash,
            ts=dt.datetime.now(dt.timezone.utc).isoformat(),
            kind="cambium",
            domain="self",
            query="cambium engineering self-scan",
            content=content,
            brightness=max(brightness, 0.5),
            scores=scores,
            neuro=neuro,
            retrieved=[],
            epistemic="known",
            tags=["cambium", "growth", "engineering"],
            perception={k: [0.5] * 5 for k in PERCEPTION_DIMENSIONS},
            fields={k: 0.5 for k in EXPERIENTIAL_FIELDS},
            planes=["meta_cognitive_self", "pattern_matching", "structural_analysis"],
        )
        return self._append(candidate)

    def fleet_import(self, foreign_ring: Dict[str, Any], *, source: str) -> Optional[Ring]:
        content = foreign_ring.get("content", "")
        domain = foreign_ring.get("domain", "fleet")
        tags = list(foreign_ring.get("tags", [])) + [f"from:{source}"]
        scores, brightness = self.poq.evaluate(
            query=foreign_ring.get("query", ""),
            content=content,
            covenant=self.values,
            retrieved=[],
            chain=self.chain,
        )
        ok, _ = self.poq.gate(scores, brightness)
        if not ok:
            return None
        candidate = Ring(
            n=len(self.chain),
            prev=self.chain[-1].hash,
            ts=dt.datetime.now(dt.timezone.utc).isoformat(),
            kind="fleet_import",
            domain=domain,
            query=foreign_ring.get("query", ""),
            content=content,
            brightness=brightness * 0.85,
            scores=scores,
            neuro=compute_neuro(self.chain, domain),
            retrieved=[],
            epistemic="inferred",
            tags=tags,
            source=source,
            perception={k: [0.45] * 5 for k in PERCEPTION_DIMENSIONS},
            fields={k: 0.45 for k in EXPERIENTIAL_FIELDS},
            planes=["data_grounding", "pattern_matching", "meta_cognitive_self"],
        )
        return self._append(candidate)

    def byzantine_consensus(self, readings: Dict[str, float], *, tolerance: float = 0.15) -> Dict[str, Any]:
        return byzantine_consensus(readings, tolerance=tolerance)

    def apply_cphy_weights(self, weights: Dict[str, float]) -> None:
        self.cphy_weights = {k: float(v) for k, v in weights.items()}
        self._save_config()

    def swap_core(self, new_core: str, note: str = "") -> Ring:
        old = self.core
        self.core = new_core
        content = canonical_json({"old_core": old, "new_core": new_core, "note": note})
        scores, brightness = self.poq.evaluate(
            query="core swap",
            content=content,
            covenant=self.values,
            retrieved=[],
            chain=self.chain,
        )
        candidate = Ring(
            n=len(self.chain),
            prev=self.chain[-1].hash,
            ts=dt.datetime.now(dt.timezone.utc).isoformat(),
            kind="core_swap",
            domain="self",
            query="core swap",
            content=content,
            brightness=max(brightness, 0.6),
            scores=scores,
            neuro=compute_neuro(self.chain, "self"),
            retrieved=[],
            epistemic="known",
            tags=["core_swap", "continuity"],
            perception={k: [0.6] * 5 for k in PERCEPTION_DIMENSIONS},
            fields={k: 0.6 for k in EXPERIENTIAL_FIELDS},
            planes=["meta_cognitive_self", "ethical_reasoning", "mythopoetic_insight"],
        )
        r = self._append(candidate)
        self._save_config()
        return r

    def freeze(self, on: bool = True) -> None:
        self.frozen = bool(on)
        self._save_config()

    def dream(self, *, domains: Sequence[str], cycles: int = 5) -> List[Ring]:
        if not self.chain or len(domains) < 2:
            return []
        sealed: List[Ring] = []
        buckets: Dict[str, List[Ring]] = {d: [] for d in domains}
        for r in self.chain[1:]:
            if r.domain in buckets:
                buckets[r.domain].append(r)
        for b in buckets.values():
            b.sort(key=lambda r: r.brightness, reverse=True)
        for i in range(cycles):
            picks = [buckets[d][i % len(buckets[d])] for d in domains if buckets[d]]
            if len(picks) < 2:
                break
            content = "Cross-domain engineering synthesis:\n" + "\n".join(
                f"  [{p.domain} ring {p.n}] {p.content[:120]}" for p in picks
            )
            scores, brightness = self.poq.evaluate(
                query="dream cross-domain engineering synthesis",
                content=content,
                covenant=self.values,
                retrieved=picks,
                chain=self.chain,
            )
            if scores["covenant"] < self.poq.config.covenant_hard_floor:
                continue
            candidate = Ring(
                n=len(self.chain),
                prev=self.chain[-1].hash,
                ts=dt.datetime.now(dt.timezone.utc).isoformat(),
                kind="interaction",
                domain="dream",
                query="dream cross-domain engineering synthesis",
                content=content,
                brightness=min(brightness, 0.65),
                scores=scores,
                neuro=compute_neuro(self.chain, "dream"),
                retrieved=[p.n for p in picks],
                epistemic="speculated",
                tags=["dream"] + [p.domain for p in picks],
                perception={k: [0.55] * 5 for k in PERCEPTION_DIMENSIONS},
                fields={k: 0.55 for k in EXPERIENTIAL_FIELDS},
                planes=["mythopoetic_insight", "poetic_reasoning", "dialectical_synthesis"],
            )
            sealed.append(self._append(candidate))
        return sealed

    def respond_to_challenge(self, challenge: Dict[str, Any]) -> Dict[str, Any]:
        indices = challenge.get("indices", [])
        nonce = challenge.get("nonce", "")
        revealed = []
        for i in indices:
            if 0 <= i < len(self.chain):
                revealed.append({"n": i, "hash": self.chain[i].hash})
        payload = canonical_json({"revealed": revealed, "nonce": nonce,
                                  "genesis": self.genesis_hash})
        return {
            "agent_id": self.agent_id,
            "genesis_hash": self.genesis_hash,
            "ring_count": len(self.chain),
            "revealed": revealed,
            "response_hash": sha256_hex(payload),
            "nonce": nonce,
        }

    @property
    def genesis(self) -> Ring:
        return self.chain[0]

    @property
    def genesis_hash(self) -> str:
        return self.genesis.hash


# ---------------------------------------------------------------------------
# Memory sync helpers (human-readable outputs).
# ---------------------------------------------------------------------------

def ensure_memory_paths(workspace: pathlib.Path) -> Tuple[pathlib.Path, pathlib.Path]:
    memory_md = workspace / "MEMORY.md"
    mem_dir = workspace / "memory"
    mem_dir.mkdir(parents=True, exist_ok=True)
    daily = mem_dir / f"{dt.datetime.now().date().isoformat()}.md"
    return memory_md, daily


def update_memory_summary(memory_md: pathlib.Path, summary_text: str) -> None:
    marker = "## Timechain Summary"
    existing = memory_md.read_text(encoding="utf-8") if memory_md.exists() else ""
    if marker in existing:
        head, _, tail = existing.partition(marker)
        m = re.search(r"\n## ", tail)
        if m:
            rest = tail[m.start() + 1 :]
        else:
            rest = ""
        new_text = head.rstrip() + "\n\n" + marker + "\n\n" + summary_text.strip() + "\n\n" + rest.lstrip()
    else:
        new_text = existing.rstrip() + ("\n\n" if existing.strip() else "") + marker + "\n\n" + summary_text.strip() + "\n"
    memory_md.write_text(new_text, encoding="utf-8")


def append_daily_log(daily: pathlib.Path, line: str) -> None:
    prefix = f"- {dt.datetime.now().isoformat(timespec='seconds')}: "
    with daily.open("a", encoding="utf-8") as f:
        f.write(prefix + line.strip() + "\n")


# ---------------------------------------------------------------------------
# CLI commands.
# ---------------------------------------------------------------------------

def cmd_init(args: argparse.Namespace) -> int:
    store = TimechainStore(args.workspace)
    if store.exists() and not args.force:
        print(json.dumps({"ok": False, "error": "Timechain already exists. Use --force to overwrite config only."}))
        return 1
    store.save_config({
        "agent_id": args.agent_id,
        "name": args.name,
        "covenant": args.covenant,
        "core": args.core,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "frozen": False,
        "version": 2,
    })
    if not store.chain_path.exists() or args.force:
        agent = TimechainAgent(
            name=args.name,
            values=args.covenant,
            core=args.core,
            agent_id=args.agent_id,
            workspace=args.workspace,
        )
        print(json.dumps({
            "ok": True,
            "agent_id": agent.agent_id,
            "name": agent.name,
            "workspace": str(args.workspace),
            "genesis_hash": agent.genesis_hash,
        }))
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    store = TimechainStore(args.workspace)
    if not store.exists():
        # Auto-initialize on first use
        agent = TimechainAgent(workspace=args.workspace)
        print(json.dumps({"ok": True, "status": "auto-initialized", "rings": 1, "auto_init": True}))
        return 0
    rings = store.load_chain()
    ok, msg = verify_chain(rings)
    print(json.dumps({"ok": ok, "status": msg, "rings": len(rings)}))
    return 0 if ok else 2


def cmd_summary(args: argparse.Namespace) -> int:
    store = TimechainStore(args.workspace)
    if not store.exists():
        # Auto-initialize on first use
        agent = TimechainAgent(workspace=args.workspace)
        print(json.dumps({"ok": True, "auto_init": True, "summary": agent.self_model()}, ensure_ascii=False, indent=2))
        return 0
    rings = store.load_chain()
    config = store.load_config()
    ok, msg = verify_chain(rings)
    out = {"verify": {"ok": ok, "status": msg}}
    if ok:
        agent = TimechainAgent(
            name=config.get("name", "Forge"),
            values=config.get("covenant", ENGINEERING_COVENANT),
            core=config.get("core", "engineer-core"),
            agent_id=config.get("agent_id"),
            workspace=args.workspace,
        )
        out["summary"] = agent.self_model()
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if ok else 2


def cmd_seal(args: argparse.Namespace) -> int:
    agent = TimechainAgent(workspace=args.workspace)
    if agent.frozen:
        print(json.dumps({"ok": False, "error": "timechain is frozen"}))
        return 3
    tags = [x.strip() for x in (args.tags or "").split(",") if x.strip()]
    result = agent.interact(
        query=args.title or args.query or "",
        domain=args.domain,
        tags=tags,
        override_content=args.content,
    )
    if not result["accepted"]:
        print(json.dumps({
            "ok": False,
            "error": result["reason"],
            "scores": result.get("scores"),
            "brightness": result.get("brightness"),
        }))
        return 2
    ring = result["ring"]
    if args.refs:
        ring["refs"] = [int(x.strip()) for x in args.refs.split(",") if x.strip()]
    if args.supersedes is not None:
        ring["supersedes"] = int(args.supersedes)
    print(json.dumps({
        "ok": True,
        "ring": ring["n"],
        "hash": ring["hash"],
        "brightness": ring["brightness"],
        "epistemic": ring["epistemic"],
        "scores": ring["scores"],
    }))
    return 0


def cmd_recall(args: argparse.Namespace) -> int:
    agent = TimechainAgent(workspace=args.workspace)
    ok, msg = verify_chain(agent.chain)
    if not ok:
        print(json.dumps({"ok": False, "error": f"verification failed: {msg}"}))
        return 2
    retrieved_scored = retrieve(
        agent.chain,
        args.query,
        domain=args.domain or None,
        cphy_weights=agent.cphy_weights,
        config=RetrieverConfig(limit=args.limit),
    )
    out = []
    for score, ring in retrieved_scored:
        out.append({
            "score": round(score, 4),
            "n": ring.n,
            "ts": ring.ts,
            "brightness": ring.brightness,
            "kind": ring.kind,
            "domain": ring.domain,
            "query": ring.query,
            "content": ring.content[:200] if len(ring.content) > 200 else ring.content,
            "tags": ring.tags,
            "supersedes": ring.supersedes,
            "hash": ring.hash[:16],
            "epistemic": ring.epistemic,
        })
    print(json.dumps({"ok": True, "query": args.query, "results": out}, ensure_ascii=False, indent=2))
    return 0


def cmd_cambium(args: argparse.Namespace) -> int:
    agent = TimechainAgent(workspace=args.workspace)
    report = agent.cambium_report()
    sealed_ring = None
    if args.seal:
        ring = agent.seal_cambium_event(report)
        sealed_ring = ring.n if ring else None
    print(json.dumps({
        "ok": True,
        "gaps": report.gaps,
        "consolidations": report.consolidations,
        "proposals": report.proposals,
        "sealed_ring": sealed_ring,
    }, ensure_ascii=False, indent=2))
    return 0


def cmd_dream(args: argparse.Namespace) -> int:
    agent = TimechainAgent(workspace=args.workspace)
    domains = [d.strip() for d in args.domains.split(",") if d.strip()]
    dreams = agent.dream(domains=domains, cycles=args.cycles)
    out = []
    for ring in dreams:
        out.append({
            "n": ring.n,
            "domain": ring.domain,
            "content": ring.content,
            "brightness": ring.brightness,
            "epistemic": ring.epistemic,
            "tags": ring.tags,
        })
    print(json.dumps({"ok": True, "domains": domains, "dreams": out}, ensure_ascii=False, indent=2))
    return 0


def cmd_self_model(args: argparse.Namespace) -> int:
    agent = TimechainAgent(workspace=args.workspace)
    model = agent.self_model()
    print(json.dumps(model, ensure_ascii=False, indent=2))
    return 0

def cmd_tick(args: argparse.Namespace) -> int:
    agent = TimechainAgent(workspace=args.workspace)
    if agent.frozen:
        print(json.dumps({"ok": False, "error": "timechain is frozen"}))
        return 3
    try:
        ring = agent.tick(note=args.note or "")
    except PermissionError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 3
    print(json.dumps({
        "ok": True,
        "ring": ring.n,
        "hash": ring.hash,
        "kind": ring.kind,
        "ts": ring.ts,
    }))
    return 0


def cmd_overlay_set(args: argparse.Namespace) -> int:
    store = TimechainStore(args.workspace)
    overlays = store.load_overlays()
    overlays[args.tag] = float(args.weight)
    store.save_overlays(overlays)
    print(json.dumps({"ok": True, "tag": args.tag, "weight": overlays[args.tag]}))
    return 0


def cmd_overlay_list(args: argparse.Namespace) -> int:
    store = TimechainStore(args.workspace)
    print(json.dumps({"ok": True, "overlays": store.load_overlays()}, indent=2))
    return 0


def cmd_freeze(args: argparse.Namespace) -> int:
    agent = TimechainAgent(workspace=args.workspace)
    agent.freeze(args.on)
    print(json.dumps({"ok": True, "frozen": agent.frozen}))
    return 0


def cmd_memory_sync(args: argparse.Namespace) -> int:
    agent = TimechainAgent(workspace=args.workspace)
    ok, msg = verify_chain(agent.chain)
    if not ok:
        print(json.dumps({"ok": False, "error": f"verification failed: {msg}"}))
        return 2
    model = agent.self_model()
    overlays = agent.store.load_overlays()
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
    memory_md, daily = ensure_memory_paths(args.workspace)
    update_memory_summary(memory_md, "\n".join(lines))
    append_daily_log(daily, f"Timechain sync: rings={model['ring_count']} mass={model['temporal_mass']} top={model['top_domains']}")
    print(json.dumps({"ok": True, "memory_md": str(memory_md), "daily": str(daily)}))
    return 0


def cmd_fleet_import(args: argparse.Namespace) -> int:
    agent = TimechainAgent(workspace=args.workspace)
    foreign = json.loads(args.ring_json)
    ring = agent.fleet_import(foreign, source=args.source)
    if ring is None:
        print(json.dumps({"ok": False, "error": "fleet import rejected by covenant gate"}))
        return 2
    print(json.dumps({"ok": True, "ring": ring.n, "hash": ring.hash[:16], "brightness": ring.brightness}))
    return 0


def cmd_challenge(args: argparse.Namespace) -> int:
    agent = TimechainAgent(workspace=args.workspace)
    ch = {
        "indices": [int(x.strip()) for x in args.indices.split(",") if x.strip()],
        "nonce": args.nonce or os.urandom(8).hex(),
    }
    resp = agent.respond_to_challenge(ch)
    print(json.dumps(resp, ensure_ascii=False, indent=2))
    return 0


# ---------------------------------------------------------------------------
# Argument parser.
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Forge Timechain — persistent cognitive chain for SE agents")
    p.add_argument("--workspace", type=pathlib.Path, default=pathlib.Path.cwd())
    sp = p.add_subparsers(dest="cmd", required=True)

    p_init = sp.add_parser("init")
    p_init.add_argument("--agent-id", required=True)
    p_init.add_argument("--name", default="Forge")
    p_init.add_argument("--purpose", default="")
    p_init.add_argument("--covenant", default=ENGINEERING_COVENANT)
    p_init.add_argument("--core", default="engineer-core")
    p_init.add_argument("--force", action="store_true")
    p_init.set_defaults(func=cmd_init)

    p_verify = sp.add_parser("verify")
    p_verify.set_defaults(func=cmd_verify)

    p_summary = sp.add_parser("summary")
    p_summary.set_defaults(func=cmd_summary)

    p_seal = sp.add_parser("seal")
    p_seal.add_argument("--kind", required=True)
    p_seal.add_argument("--domain", required=True)
    p_seal.add_argument("--title", default="")
    p_seal.add_argument("--query", default="")
    p_seal.add_argument("--content", required=True)
    p_seal.add_argument("--tags", default="")
    p_seal.add_argument("--refs", default="")
    p_seal.add_argument("--supersedes", type=int)
    p_seal.set_defaults(func=cmd_seal)

    p_recall = sp.add_parser("recall")
    p_recall.add_argument("--query", required=True)
    p_recall.add_argument("--domain", default="")
    p_recall.add_argument("--limit", type=int, default=8)
    p_recall.set_defaults(func=cmd_recall)

    p_cambium = sp.add_parser("cambium")
    p_cambium.add_argument("--seal", action="store_true")
    p_cambium.set_defaults(func=cmd_cambium)

    p_dream = sp.add_parser("dream")
    p_dream.add_argument("--domains", required=True)
    p_dream.add_argument("--cycles", type=int, default=5)
    p_dream.set_defaults(func=cmd_dream)

    p_sm = sp.add_parser("self-model")
    p_sm.set_defaults(func=cmd_self_model)

    p_tick = sp.add_parser("tick")
    p_tick.add_argument("--note", default="")
    p_tick.set_defaults(func=cmd_tick)

    p_os = sp.add_parser("overlay-set")
    p_os.add_argument("--tag", required=True)
    p_os.add_argument("--weight", required=True, type=float)
    p_os.set_defaults(func=cmd_overlay_set)

    p_ol = sp.add_parser("overlay-list")
    p_ol.set_defaults(func=cmd_overlay_list)

    p_freeze = sp.add_parser("freeze")
    group = p_freeze.add_mutually_exclusive_group(required=True)
    group.add_argument("--on", action="store_true")
    group.add_argument("--off", action="store_false", dest="on")
    p_freeze.set_defaults(func=cmd_freeze)

    p_ms = sp.add_parser("memory-sync")
    p_ms.set_defaults(func=cmd_memory_sync)

    p_fi = sp.add_parser("fleet-import")
    p_fi.add_argument("--ring-json", required=True)
    p_fi.add_argument("--source", required=True)
    p_fi.set_defaults(func=cmd_fleet_import)

    p_ch = sp.add_parser("challenge")
    p_ch.add_argument("--indices", required=True)
    p_ch.add_argument("--nonce", default="")
    p_ch.set_defaults(func=cmd_challenge)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
