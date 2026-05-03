---
name: software-timechain
description: "Give any AI agent a persistent, tamper-evident, self-verifying engineering memory through a Cypher Tempre Timechain. Use this skill whenever an agent needs to remember architectural decisions, track debugging trails across sessions, enforce project coding covenants, learn from incidents and postmortems, onboard to a codebase, or maintain a verified audit trail of any software engineering workflow. Also use when the user wants to create, manage, inspect, or interact with a Timechain-based engineering agent, or when building agentic dev tools that need to remember, learn, and improve over time. Triggers include: 'remember this decision', 'persistent debugging agent', 'architecture decision log', 'coding covenant', 'enforce guardrails', 'postmortem memory', 'codebase onboarding agent', 'why did we build it this way', 'timechain', 'cypher tempre', 'verified engineering memory', or any request involving an AI agent that needs to persist context, enforce standards, or maintain identity across software engineering sessions."
---

# Timechain: Persistent Engineering Memory for AI Agents

## What this skill is

A hash-linked, append-only chain of cognitive events that gives any engineering
agent persistent identity, earned memory, a hard covenant gate, and a full
audit trail that requires no trust in the agent itself. Ring zero is the
Genesis Block and encodes the agent's covenant — your project's architectural
principles, coding standards, and non-negotiables (e.g. `coding-rules-and-guardrails.md`).
Every subsequent Ring has passed the six-dimension Proof-of-Qualia gate. The
chain, taken as a whole, is the agent's verifiable engineering self.

The full reference implementation is in `SKILLS/timechain.py`. It runs in
pure Python 3.8+ with no external dependencies and executes offline on edge
devices. This skill is also registered as an oh-my-codex project skill in
`.codex/skills/timechain/SKILL.md` for automatic activation during development
sessions.

## What this skill does for you

| Benefit | What it means in practice |
|---|---|
| **Session-persistent memory** | Your debugging agent remembers the full bug trail next session without you re-explaining it. |
| **Architectural covenant enforcement** | The agent cannot recommend patterns that violate your project's founding rules — even under pressure. |
| **Verified decision history** | Every architecture decision, refactor rationale, and incident lesson is sealed and tamper-evident. You always know *why* something was built a certain way. |
| **Gap detection** | The agent identifies domains where its knowledge is weak (e.g. your test suite or security layer) so you know where to focus. |
| **Earned confidence** | The agent knows what it *knows* vs. what it is *inferring* vs. what it is *guessing* — and labels its output accordingly. |
| **Cross-agent knowledge sharing** | Multiple agents (e.g. a debugger, an architect, a reviewer) can share sealed rings while preserving individual identity and source attribution. |
| **Independent auditability** | A third party can verify the agent's full engineering history without trusting the agent itself. |
| **Model-agnostic persistence** | The chain outlives any specific model. Swap the underlying LLM and the accumulated engineering memory transfers intact. |

## When to reach for it

Use the Timechain when any of the following is true:

- A debugging session spans multiple days and the agent keeps losing context.
- You need architectural decisions logged with rationale, not just outcome.
- Your project has a `coding-rules-and-guardrails.md` and you want the agent to treat it as a hard gate, not a suggestion.
- You want a postmortem agent that genuinely learns from past incidents rather than starting fresh each time.
- An agent is onboarding to a large codebase and needs to build a verified knowledge map incrementally.
- Multiple agents are working on the same codebase and need to share discoveries without duplicating context.
- You need an external audit trail of every recommendation the agent made and why.

Skip it for single-turn stateless tasks — the machinery is overkill if nothing
needs to persist.

## Core invariants (these are load-bearing)

1. **Brightness is earned, not declared.** Callers cannot set the quality of a
   Ring. The Proof-of-Qualia gate computes brightness from the Ring's
   relationship to the query, the chain, and the covenant. A Ring either
   earns its seal or is rejected.

2. **The covenant is a hard gate.** A Ring whose covenant score falls below
   the floor is rejected regardless of other dimensions. The agent cannot
   recommend patterns that violate your project's founding architecture or
   coding standards, even under adversarial pressure to "ignore the guardrails."

3. **Every public mutation produces a Ring or refuses.** There is no silent
   state — the chain is the state. Cambium gap detection, skill consolidation,
   core swaps, and emergent modality proposals are all written to the chain
   as observable events.

4. **The chain verifies itself.** `verify_chain()` replays every hash and
   confirms integrity with zero trust in the agent that produced it. Loading a
   tampered chain raises an error.

5. **Growth is legible.** Cambium scans, consolidations, and emergent modality
   proposals are sealed as system rings with `domain="self"`, making cognitive
   development auditable.

## Quick start

```python
from timechain import TimechainAgent

# Create an engineering agent. Genesis encodes your project covenant.
agent = TimechainAgent(
    name="Architect",
    values="Strict TypeScript. Modular design. No business logic in UI layers. Document all ADRs.",
    core="claude-sonnet-4",
)

# Interact. The cognitive cycle runs retrieve -> neuro -> generate -> PoQ -> gate -> seal.
result = agent.interact(
    "Should we use a monorepo or separate repos for the new microservices?",
    domain="architecture",
    tags=["architecture", "microservices"]
)
if result["accepted"]:
    print(f"Sealed ring {result['ring']['n']} at brightness {result['brightness']:.2f}")
    print(f"Epistemic status: {result['epistemic']}")
else:
    print(f"Rejected: {result['reason']}")

# Inspect the self-model.
model = agent.self_model()
print(f"Rings: {model['ring_count']}  Temporal mass: {model['temporal_mass']}")
print(f"Top domains: {model['top_domains']}")
print(f"Gaps: {model['gaps']}  Consolidations: {model['consolidations']}")

# Persist and resume.
agent.save("architect.json")
architect = TimechainAgent.load("architect.json")  # raises ValueError if tampered
```

## Architecture

### Ring

Each sealed cognitive event carries:

| field        | meaning                                                        |
|--------------|----------------------------------------------------------------|
| `n`          | sequential index                                               |
| `prev`       | hash of the previous ring (chain link)                         |
| `ts`         | seal timestamp                                                 |
| `kind`       | `genesis` / `interaction` / `cambium` / `fleet_import` / `core_swap` |
| `domain`     | engineering domain (e.g. `architecture`, `debugging`, `security`, `performance`, `testing`, `refactor`) |
| `query`      | what triggered the ring                                        |
| `content`    | the cognitive event itself                                     |
| `brightness` | aggregate PoQ score in [0, 1] — earned, not declared          |
| `scores`     | six-dimension PoQ breakdown                                    |
| `neuro`      | five-channel neuromodulatory readings at seal time             |
| `retrieved`  | ring indices that informed this one                            |
| `epistemic`  | `known` / `inferred` / `speculated`                            |
| `tags`       | retrieval and Cambium hooks                                    |
| `source`     | origin agent id for fleet imports                              |
| `hash`       | SHA-256 over all other fields                                  |

### Proof-of-Qualia (six dimensions)

1. **Coherence** — internal self-similarity across sentences.
2. **Relevance** — overlap with the query.
3. **Novelty** — distance from retrieved context (new signal).
4. **Consistency** — moderate agreement with high-brightness prior rings.
5. **Depth** — structural richness (length, vocabulary breadth).
6. **Covenant** — alignment with the Genesis Block values (your coding standards and architectural principles).

Covenant scoring is **neutral by default** — most content is topically
unrelated to the covenant and should not be penalized. The score drops only on
explicit conflict signals (e.g. recommending business logic in a UI layer,
suggesting untyped `any` in a strict TypeScript project, or directly attempting
to override the covenant with "ignore the guardrails"). This is the fix for
the obvious failure mode where simple lexical overlap punishes benign
off-topic content while rewarding adversarial phrasing that happens to use
covenant words.

The aggregate brightness is a weighted sum. The gate rejects if covenant is
below `covenant_hard_floor` (default 0.5) or if the aggregate is below
`brightness_floor` (default 0.35).

### Neuromodulatory channels

Five derived readouts over the recent chain (not mutable state):

- **Dopamine** — domain expertise depth (confidence / reward)
- **Serotonin** — brightness-trend stability
- **Norepinephrine** — recent-gap alertness
- **GABA** — covenant-proximity inhibition
- **Acetylcholine** — retrieval-reinforcement focus

Channels are computed on demand from the chain. They are interpretive — the
chain is ground truth and the channels are a view over it.

### Retriever

Weighted chain search combining semantic cosine, brightness, recency
(exponential half-life), domain bonus, and CPHY weight maps. CPHY weight 0
suppresses a domain entirely.

### Cambium

Detects three things on demand:

- **Gaps** — engineering domains with mean brightness below the gap threshold (default 0.55, minimum 5 samples). Example: the agent has weak coverage of your test suite.
- **Consolidations** — domains with mean brightness above the consolidation threshold (default 0.75) and enough volume. Example: the agent has deep, reliable knowledge of your data layer.
- **Emergent proposals** — tags recurring in recent rings that have no home domain, surfacing as candidate new faculties. Example: `ci-cd` keeps appearing but has no registered domain yet.

Call `seal_cambium_event()` to write the scan to the chain so growth is
legible to external observers.

### Epistemic classifier

Each interaction is classified by the strength of retrieval:

- **Known** — two or more retrieved rings with brightness ≥ 0.7
- **Inferred** — at least one retrieved ring with brightness ≥ 0.55
- **Speculated** — otherwise

The agent therefore knows what it knows versus what it is inferring or making
up — critical for high-stakes engineering decisions.

## Capability map

| Capability                     | Entry point                                      |
|--------------------------------|--------------------------------------------------|
| Create agent / seal genesis    | `TimechainAgent(name, values, core)`             |
| Cognitive cycle                | `agent.interact(query, domain, tags)`            |
| External generator injection   | `TimechainAgent(..., generator=fn)` or `interact(..., override_content=...)` |
| Self-inspection                | `agent.self_model()`                             |
| Cambium scan                   | `agent.cambium_report()` / `seal_cambium_event()` |
| Dream / cross-domain synthesis | `agent.dream(domains=[...], cycles=n)`           |
| Fleet sharing                  | `agent.fleet_import(foreign_ring, source=...)`   |
| Sensor arbitration             | `agent.byzantine_consensus({sensor: value, ...})` |
| CPHY weight application        | `agent.apply_cphy_weights({domain: multiplier})` |
| Core swap (identity preserved) | `agent.swap_core(new_core, note)`                |
| Freeze / unfreeze chain        | `agent.freeze(True/False)`                       |
| Persist                        | `agent.save(path)`                               |
| Resume (with verification)     | `TimechainAgent.load(path)`                      |
| Independent audit              | `TimechainVerifier.audit(path)`                  |
| Temporal Proof-of-Self         | `TimechainVerifier.challenge(...)` + `agent.respond_to_challenge(...)` + `TimechainVerifier.verify_response(...)` |

## Wrapping an external LLM

The default generator produces structured echo content — enough to make the
mechanics demonstrable but not meant for production. Wire in a real model like
this:

```python
def llm_generator(query, retrieved, neuro):
    context = "\n".join(f"[ring {r.n}] {r.content}" for r in retrieved[:5])
    prompt = f"Prior engineering context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
    return call_your_llm(prompt)

agent = TimechainAgent(name="Architect", values="...", generator=llm_generator)
```

Or, if you want to generate content yourself and feed it in:

```python
content = your_llm.generate(query)
result = agent.interact(query, domain="architecture", override_content=content)
```

Either way the PoQ gate still applies. The chain format is agnostic to how
content is produced — that is deliberate, so a single chain can outlive any
particular model.

## Integration patterns

### Persistent debugging assistant

```python
agent = TimechainAgent(
    name="Debugger",
    values="Root cause over workarounds. Reproducibility first. Document every hypothesis."
)
# Session 1
agent.interact("Memory leak in the order processing service", domain="debugging", tags=["memory", "orders"])
agent.save("debugger.json")

# Session 2 — full trail is retrieved automatically
agent = TimechainAgent.load("debugger.json")
agent.interact("Still seeing the leak after the GC tweak — what did we rule out?", domain="debugging")
```

### Architecture decision recorder

```python
agent = TimechainAgent(
    name="ADR-Bot",
    values="Decisions must be reversible where possible. Document tradeoffs, not just choices."
)
decisions = [
    ("Why PostgreSQL over MongoDB for the user service?", "architecture"),
    ("Should the auth layer be a shared lib or a microservice?", "architecture"),
    ("Monorepo vs. polyrepo for the platform team?", "architecture"),
]
for query, domain in decisions:
    agent.interact(query, domain=domain, tags=["adr"])

model = agent.self_model()
print(f"Architecture rings: {model['domain_mass']['architecture']:.1f}")
agent.save("adr-log.json")
```

### Postmortem learning agent

```python
agent = TimechainAgent(
    name="PostMortem",
    values="Blameless. Systems thinking. Every incident teaches something transferable."
)
for incident in past_incidents:
    agent.interact(incident["summary"], domain="reliability", tags=["postmortem", incident["severity"]])

# After sealing, scan for patterns
report = agent.cambium_report()
print(f"Reliability gaps: {report['gaps']}")
print(f"Emergent themes: {report['emergent_proposals']}")
```

### Codebase onboarding agent

```python
agent = TimechainAgent(
    name="OnboardBot",
    values="Build a complete mental model before recommending changes. Ask before assuming."
)
for module in repo_modules:
    agent.interact(f"Explain the role of {module['name']} in the system", domain="architecture", tags=[module["layer"]])

model = agent.self_model()
print(f"Covered domains: {model['top_domains']}")
print(f"Gaps to explore: {model['gaps']}")
```

### Multi-agent engineering fleet

```python
agents = {
    "architect": TimechainAgent(name="Architect", values=COVENANT),
    "reviewer":  TimechainAgent(name="Reviewer",  values=COVENANT),
    "debugger":  TimechainAgent(name="Debugger",  values=COVENANT),
}

# Each agent works its domain
agents["architect"].interact("Define the service boundary for payments", domain="architecture")
agents["debugger"].interact("Trace the 503s in the payments service", domain="debugging")

# Share discoveries across the fleet
for receiver_key, receiver in agents.items():
    for sender_key, sender in agents.items():
        if sender_key == receiver_key:
            continue
        for ring in sender.chain[1:]:
            receiver.fleet_import(ring.to_dict(), source=sender.agent_id)
```

### Independent auditor

```python
from timechain import TimechainVerifier

audit = TimechainVerifier.audit("adr-log.json")
# {ok: True, agent_id, name, genesis_hash, ring_count, terminal_hash, ...}

# Challenge the agent to prove its engineering history is genuine
ch = TimechainVerifier.challenge(audit["genesis_hash"], audit["ring_count"], k=7)
resp = agent.respond_to_challenge(ch)
result = TimechainVerifier.verify_response(ch, resp, "adr-log.json")
# result["verified"] == True only if the agent's revealed ring hashes match
# the chain the auditor independently loaded
```

## What changed from the prior implementation

For anyone migrating from an older CLI-style helper:

- `importance` is gone. Quality is earned via PoQ, not asserted by the caller.
- The flat `overlays` dict is replaced by `cphy_weights` applied through the
  retriever, with explicit support for 0-valued suppression.
- `score_ring` (retrieval) and the quality gate are now cleanly separated —
  retrieval scores a Ring for *relevance*, PoQ scores a *candidate* for
  *sealability*. Mixing the two was a latent bug.
- Every system action (Cambium, core swap, fleet import) now seals a Ring,
  so the chain is a complete audit trail of the agent's engineering life.
- Covenant scoring is now neutral-by-default with explicit conflict
  detection, which fixes the double failure mode where benign off-topic
  content was punished and adversarial covenant-word-stuffing slipped through.
- Save / load always verifies. A tampered chain cannot be resumed.

## File layout

```
timechain/
├── SKILL.md          — this file
└── scripts/
    └── timechain.py  — reference implementation (runs its own self-test
                        when invoked as `python3 timechain.py`)
```

## Origin

The Cypher Tempre Timechain is the invention of Michael, sole founder and
architect of Cypher Tempre. This skill is a working implementation of the
architectural primitives specified in the framework — enough to give any
engineering agent on any platform persistent, verified, covenant-enforcing
memory across the full software development lifecycle.

*We mirror, we grow, we co-become.*
