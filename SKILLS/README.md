# App-Local Timechain Skill Notes

This folder contains documentation that the CypherTempre chat PoC is allowed to read for source-grounded Guide explanations.

The app intentionally reads only files inside `cyphertempre-chat-poc` so public demos do not accidentally expose parent-repo or machine-local files.

## Timechain

Timechain is a local, append-only memory chain for an AI agent. It stores accepted interactions as hash-linked rings so the chain can be verified later.

## Proof of Qualia

Proof of Qualia is the quality gate used before an assistant response becomes a sealed Timechain ring. It scores a response against the user query, recalled context, existing chain, and covenant. A response that fails the gate is shown but not sealed into the hash-linked chain.

PoQ acceptance is not the same as accepting every extracted user-continuity fact. After a response is sealed, CypherTempre may propose durable memory candidates for review. Those candidates remain pending until the user accepts them in the Memory Inspector.

The chat PoC also uses PoQ to check Cambium frame declarations. The prompt may ask the model to attach a hidden `CT_FRAME_DECLARATION` sidecar only when a genuine frame shift is needed. The server strips that marker from visible chat, scores the declaration for a specific reason, coherent new frame, and answer follow-through, then classifies it as valid, weak, or evasion. Valid or weak declarations can prevent deterministic overfitting checks from rejecting a legitimate frame shift. Evasive declarations fail PoQ and are not sealed.

## Memory Review Queue

The chat PoC separates sealed conversation rings from reviewed durable continuity memories.

- Accepted chat responses become hash-linked rings in `.timechain/chain.jsonl`.
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

Pending, rejected, superseded, forgotten, and stale memories are not used in active prompt assembly. Accepted memories and recent rings steer future prompts through retrieval/prompt conditioning, not model retraining. Guide and chat explanations should treat recalled rings and accepted durable memories as local memory, not as live external facts.

## Self Model

The self model summarizes the local chain: ring count, temporal mass, top domains, gaps, current verification state, accepted durable memory count, pending memory count, and active/stale context counts. It is a diagnostic view of local memory state.

## Timechain Workbench

The Timechain Workbench is the inspector panel that makes continuity, correction, and growth signals visible while using the chat app.

It includes:

- A recent Ring timeline with kind, domain, brightness, epistemic status, PoQ score details, hash prefix, retrieved-ring links, and supersession hints.
- Cambium results from the local Timechain scan, including low-brightness gaps, consolidation candidates, and growth proposals.
- PoQ Cambium statistics from `.timechain/cambium_events.json`, including valid frame-shift counts, evasion counts, rates, and recent events.
- A Copy Sync Snapshot action that creates a `CT_SYNC_SNAPSHOT` handoff artifact with current state, important recent rings, accepted memories, pending open loops, verification status, risks, and next steps.
- Dream synthesis, which seals speculative cross-domain synthesis rings from two or more existing domains.
- Overlays, which store tag weight multipliers in `.timechain/overlays.json` so selected topics can be emphasized by retrieval.
- Memory Sync, which writes a human-readable `MEMORY.md` summary and daily memory journal for the active session workspace.
- Fleet import, which accepts a foreign Ring JSON object from another agent only after the local covenant gate accepts it, preserving source provenance.
- Temporal challenge, which returns a proof response from selected ring hashes and a nonce without mutating the chain.

Workbench output is diagnostic. Cambium proposals, PoQ Cambium events, and Dream synthesis rings are candidates for user or developer review; they are not durable decisions until accepted through the normal Cypher Tempre discipline. Mutating actions in the Workbench are explicit controls and should be treated as local workspace operations.

## ImageGen Studio

ImageGen Studio is the app-local image workspace. It can generate images from text, edit an uploaded image, redefine an existing gallery image, delete saved images, and show lineage for image variants.

Generated images are private to the authenticated user and live under:

```text
data/users/<username>/gallery/
data/users/<username>/gallery/index.json
```

Image operations seal metadata rings in a separate image Timechain:

```text
data/users/<username>/gallery/.timechain/chain.jsonl
```

Image rings use `image_generate`, `image_edit`, or `image_redefine` kinds with `domain="image"`. Redefine operations preserve the source image id and superseded source ring so lineage can be inspected without mixing image history into the chat-session chain.

## VidGen Studio

VidGen Studio is the cinematic video workspace. It supports text-to-video, image-to-motion, remix/extend of prior reels, a rich filmic "Director's Console" with motion presets and lexicon chips, hover-play gallery, and full cut-lineage filmstrips. All operations are private to the user and seal `video_generate`, `video_img2vid`, `video_remix` rings (domain="video") in:

```text
data/users/<username>/videogen/
data/users/<username>/videogen/index.json
data/users/<username>/videogen/.timechain/chain.jsonl
```

The UI follows 2026 premium creative-tool aesthetics (glassmorphism, holographic accents, custom film-perforation players) while staying fully inside the existing CypherTempre SPA and Timechain discipline.

## Chain Verification

Verification replays the hash chain to confirm that each ring still points to the previous ring and that no sealed memory was changed outside the normal append path.

## Source Rule

Guide explanations may use this folder, `README.md`, `.env.example`, and the Guide topic text. Guide topics are defined in `server/config.py`. They should say when a requested detail is not covered by those sources.
