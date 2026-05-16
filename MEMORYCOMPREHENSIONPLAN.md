# Shared Memory Comprehension Plan

## Summary

Best first move: implement Pathway 2 as an opt-in shared memory/comprehension layer. The app already has separate sessions, personas, accepted rings, PoQ, recall, Dream synthesis, Fleet import, Sync Snapshots, and workbench routes, so the clean move is to let high-quality thoughts move between memory lanes before attempting fine-tuning or self-modifying config.

This is not “AGI achieved.” It is a measurable primitive: ideas from one session/persona can be retrieved, imported, and synthesized into a new accepted comprehension ring.

## Key Changes

- Add `SharedMemoryHit` records derived from accepted rings in other sessions owned by the same authenticated user:
  - `id`, `source_session`, `source_ring`, `source_hash_prefix`, `domain`, `query`, `content`, `brightness`, `epistemic`, `score`, `tags`.
- Add backend methods in `server/timechain.py`:
  - `shared_recall(username, query, exclude_session, limit)` searches other user sessions using the existing Timechain retrieval primitives.
  - `import_shared_memory(hit_id, target_session)` seals the selected source thought into the active session through existing `fleet_import`/PoQ checks.
  - `synthesize_comprehension(query, hit_ids, target_session)` creates a PoQ-gated comprehension ring from selected shared hits.
- Extend `server/llm.py` prompt assembly with an optional “Shared memory from other lanes” context block.
- Extend `/api/chat` with `sharedMemory: true|false`; default `false` to preserve current session isolation.
- Add API routes:
  - `GET /api/shared-memory?session=...&query=...&limit=...`
  - `POST /api/shared-memory/import`
  - `POST /api/shared-memory/synthesize`
- Add a “Shared Memory” section to the existing Timechain Workbench:
  - search across memory lanes
  - view source session/ring/brightness/provenance
  - import selected thoughts
  - synthesize selected thoughts into a comprehension ring
  - chat toggle: “Use shared memory”

## Behavior Rules

- Only accepted rings are eligible.
- Current session is excluded from shared recall.
- Pending, rejected, superseded, forgotten, and stale memories remain excluded unless explicitly revived by existing recall rules.
- Shared memory is same-user only; no marketplace/public persona leakage.
- Imports and syntheses must pass the target session’s PoQ gate before becoming rings.
- Source provenance is preserved in `source`/tags and shown in the UI.
- No model fine-tuning, LoRA, AGENTS.md rewriting, or external autonomous agent runtime in this first pass.

## Test Plan

- Unit: shared recall finds a relevant high-brightness ring from another session and excludes active-session rings.
- Unit: shared recall refuses unauthenticated or cross-user access.
- Unit: shared prompt context appears only when `sharedMemory` is true.
- Unit: importing a shared hit creates a `fleet_import` ring and preserves source provenance.
- Unit: comprehension synthesis creates an accepted ring with selected source references, or returns PoQ rejection without mutation.
- Regression: existing `/api/recall`, `/api/dream`, `/api/fleet-import`, memory review, session switching, and chain verification still pass.
- UI: Workbench exposes shared-memory search/import/synthesize controls and refreshes rings, summary, memories, and verify state after mutation.

## Assumptions

- “Ideas bouncing between memory” means cross-session/persona transfer inside the current local app.
- The first milestone should prove transfer and synthesis before training weights.
- Session memory remains isolated by default; shared recall is explicit and visible.
- Existing standard-library-only style stays intact; no new dependencies.
