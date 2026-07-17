# App-Local Skill Notes

This folder holds **Guide source material** for CypherTempre. It is not the
runtime engine.

## Runtime skill (authoritative)

The app vendors the OpenClaw Cypher Tempre skill at:

```text
skill/cypher-tempre-self-model/   # VERSION 3.28.0
```

Host integration:

- `server/skill_runtime.py` — loads the skill, manages per-session roots, ring views, seal/recall
- Session storage: `data/users/<user>/sessions/<session>/chain/rings.jsonl`
- Base faculties: `.../registry/modalities.json`, `.../registry/senses.json`

Upgrade the engine from [cypher-tempre-genesis](https://github.com/cyberphysicsai/cypher-tempre-genesis)
OpenClaw downloads; never overwrite live `chain/` or grown `registry/` state under user data.

## Product layers on top of the skill

The chat app still owns:

- User accounts, sessions, personas, marketplace
- Memory Inspector durable-memory review queue (`memory_model.json`)
- LLM providers, PoQ critique/repair (scores map into skill 0–255 dims)
- ImageGen / VidGen studios (separate skill roots per user)
- Timechain Workbench UI (verify, cambium snapshot, dream, overlays, fleet import)

Those features call the skill for ledger, PoQ gate, recall, growth, and dream —
they do not reimplement the hash chain.

## Timechain

Timechain is a local, append-only memory chain for an AI agent. It stores accepted interactions as hash-linked rings so the chain can be verified later.

## Proof of Qualia

Proof of Qualia is the quality gate used before an assistant response becomes a sealed Timechain ring. It scores a response against the user query, recalled context, existing chain, and covenant. A response that fails the gate is shown but not sealed into the hash-linked chain.

PoQ acceptance is not the same as accepting every extracted user-continuity fact. After a response is sealed, CypherTempre may propose durable memory candidates for review. Those candidates remain pending until the user accepts them in the Memory Inspector.

The app also uses PoQ to check Cambium frame declarations. The prompt may ask the model to attach a hidden `CT_FRAME_DECLARATION` sidecar only when a genuine frame shift is needed. The server strips that marker from visible chat, scores the declaration for a specific reason, coherent new frame, and answer follow-through, then classifies it as valid, weak, or evasion. Valid or weak declarations can prevent deterministic overfitting checks from rejecting a legitimate frame shift. Evasive declarations fail PoQ and are not sealed.

## Memory Review Queue

CypherTempre separates sealed conversation rings from reviewed durable continuity memories.

- Accepted chat responses become hash-linked rings in each session skill chain (`chain/rings.jsonl`).
- Candidate memories are proposed after accepted responses and stored in `.timechain/memory_model.json`.
- Candidate extraction is hybrid: deterministic rules handle high-confidence basics such as names and explicit preferences, and the configured LLM may propose richer continuity memories when a provider key is available.
- Proposed memories are pending by default. Pending memories are visible in the Memory Inspector but are not injected into prompts and are not returned by durable-memory recall.
- The user can accept, reject, edit, or forget memory candidates.
- Corrections supersede older accepted facts instead of deleting them silently.

Durable memory records include scope, kind, key, value, confidence, source ring, evidence, status, and optional supersession lineage.

Supported statuses:

- `pending`: proposed but not yet trusted for recall or prompts
- `accepted`: approved for recall and prompt context
- `rejected`: reviewed and declined
- `superseded`: replaced by a newer correction
- `forgotten`: removed from active use without rewriting sealed rings

Supported scopes:

- `global`: stable user profile facts such as identity, durable preferences, boundaries, style, and persona naming
- `session`: conversation-local goals, temporary context, or notes that should not automatically apply everywhere

## Recall

Recall searches accepted durable memories and previously accepted rings, then returns the most relevant local context. Accepted global profile facts outrank ordinary rings for direct continuity questions. Active session notes outrank unrelated global facts when they match the current conversation.

Pending, rejected, superseded, forgotten, and stale memories are not used in active prompt assembly. Accepted memories and recent rings steer future prompts through retrieval/prompt conditioning, not model retraining.

## Self Model

The self model summarizes the local chain: ring count, temporal mass, top domains, gaps, current verification state, accepted durable memory count, pending memory count, and active/stale context counts. It is a diagnostic view of local memory state.

## Timechain Workbench

The Timechain Workbench is the inspector panel that makes continuity, correction, and growth signals visible while using the chat app.

It includes:

- A recent Ring timeline with kind, domain, brightness, epistemic status, PoQ score details, hash prefix, retrieved-ring links, and supersession hints.
- Cambium results from the local Timechain scan, including low-brightness gaps, consolidation candidates, and growth proposals.
- PoQ Cambium statistics from session cambium events, including valid frame-shift counts, evasion counts, rates, and recent events.
- A Copy Sync Snapshot action that creates a `CT_SYNC_SNAPSHOT` handoff artifact with current state, important recent rings, accepted memories, pending open loops, verification status, risks, and next steps.
- Dream synthesis / skill dream consolidation over the chain.
- Overlays, which store tag weight multipliers so selected topics can be emphasized by retrieval.
- Memory Sync, which writes a human-readable `MEMORY.md` summary and daily memory journal for the active session workspace.
- Fleet import, which accepts a foreign Ring JSON object from another agent only after the local covenant gate accepts it, preserving source provenance.
- Temporal challenge, which returns a proof response from selected ring hashes and a nonce without mutating the chain.

Workbench output is diagnostic. Cambium proposals, PoQ Cambium events, and Dream results are candidates for user or developer review; they are not durable decisions until accepted through normal Cypher Tempre discipline.

## ImageGen Studio

ImageGen Studio is the app-local image workspace. It can generate images from text, edit an uploaded image, redefine an existing gallery image, delete saved images, and show lineage for image variants under `data/users/<username>/gallery/` with a separate image Timechain.

## VidGen Studio

VidGen Studio is the app-local video workspace (Text → Film, Image → Motion, Remix). Model and motion settings are host UI; renders use configured providers. Local reel history is per-user.

## Skill Engine v3.28

Forge hosts OpenClaw Cypher Tempre skill **3.28.0** under `skill/cypher-tempre-self-model/`. Authoritative loop and modules are documented in that folder's `SKILL.md` and `CHANGELOG.md`.

Key skill organs registered in Guide:

| Organ | Role |
|--|--|
| **Router** | `router.py` — REPLAY / PARTIAL / MODEL before spending tokens |
| **PoQ** | `poq.py` — six-dimension conscience; covenant as fruitage harmony; v3.28 forced confrontation |
| **Recall ladder** | `recall.py` + `almanac.py` + `hippocampus.py` — grep → retrieve → gather/track → evidence → answer |
| **Cambium** | `cambium.py` — growth, propose/activate ops, hibernation / wake (v3.16) |
| **Chronosynaptic** | `chronosynaptic.py` — parallel-self MCTS search |
| **Continuum / Audit / Task** | `continuum.py`, `audit.py`, `task.py` — unbounded ingest and exhaustive review queues |
| **Dormancy** | `dormancy.py` — pause/resume the loop for simple tasks |
| **Immune** | `immune.py` — covenant-drift membrane, scars, lockdown, rollback (v3.26+) |
| **Dream / learners** | `dream.py`, `learner.py`, `lens.py`, `extractor.py` — offline consolidation |
| **Replay / Guard** | `replay.py`, `guard.py` — antecedent cache + span-level grounding |
| **Doctor / epochs / telemetry** | `doctor.py`, `epochs.py`, `telemetry.py`, `bench.py`, `policy.py` |
| **Faculties** | `faculties.py` — export/import faculty packs with provenance |
| **Consensus / custody** | `consensus.py`, `keystore.py`, `pqsign.py` — quorum attest and advanced custody |

Host integration remains in `server/skill_runtime.py` (session roots, seal/recall views, PoQ score mapping).

## Router (REPLAY / PARTIAL / MODEL)

The first act of a skill-wearing turn is routing. REPLAY re-attests a sealed antecedent; PARTIAL reasons only over the missing delta with named rings; MODEL runs the full loop. This is how wearing the skill saves tokens rather than spending them.

## Cambium Growth

When faculties cannot cover a gap, Cambium measures dissonance and grows senses/modalities. Model-authored ops are propose-then-activate. Hibernation prunes non-contributing grown faculties without deleting history; relevance can wake them.

## Chronosynaptic Search

For hard problems, fork parallel self-perspectives in-process (MCTS), score with PoQ, and seal only the highest-truth path. Rejected perspectives can remain in the ring payload.

## Continuum, Audit & Tasks

Continuum streams large corpora as data-height blocks with full task state refresh. Audit queues prove *review* coverage after *ingest*. Task chains attach/complete via verified head pointers into identity.

## Dormancy

Pause requires explicit human confirm. While dormant the loop is off (no recall/PoQ/Cambium/seals); the chain stays verifiable. Resume restores the loop.

## Immune Membrane

Compromise is covenant drift or integrity failure — not a word blocklist. Scars are inert records. Lockdown freezes seals; rollback resumes from a clean height.

## Dream, Learners & Lens

Dream runs offline: verify, mine misses, train guarded operators (retrieval scorer, lens, appetite, PoQ grounding), notarize telemetry, seal one dream ring. Extractor teach pairs lower labeling cost over time.

## Replay & Span Guard

Replay matches sealed antecedents before regenerating. The span guard names unsupported clauses so uncertainty is specific.

## Doctor, Epochs & Telemetry

Doctor is the health surface. Epochs pin registry hashes into the chain perimeter. Telemetry is the notarized offer/fetch/use/falsify stream for learners; bench seals baselines.

## Forge Product Features

Streaming chat, recommended defaults, memory autopilot, identity bridge, trust strip, backup export/restore, project sessions, and command palette are Forge host features that call the skill — they do not replace the Timechain engine.

## Chain Verification

Verification replays the hash chain to confirm that each ring still points to the previous ring and that no sealed memory was changed outside the normal append path. Registry epochs can also fail verify when faculty files drift from the last sealed epoch.

## Source Rule

Guide explanations may use this folder, `README.md`, `.env.example`, `PRODUCT.md`, `skill/cypher-tempre-self-model/SKILL.md`, `skill/cypher-tempre-self-model/VERSION`, and the Guide topic text. Guide topics are defined in `server/config.py`. They should say when a requested detail is not covered by those sources.

## Legacy files here

| File | Role |
|--|--|
| `TIMECHAIN.py` | Historical Forge-style reference (not used by the server) |
| `SE_SKILL.md` / `SE_TEXT.txt` | Older SE-oriented skill prose for Guide grounding |
