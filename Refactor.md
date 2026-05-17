# Server Refactor Map

`server/timechain.py` owns the server-level Timechain surface: session paths, memory model management, Cambium scanning, overlays, dream synthesis, fleet import, temporal challenge, memory sync, memory anchors, PoQ Cambium event summaries, and image lineage.

## Current Structure

```text
server/
  __init__.py       Public compatibility exports
  __main__.py       Entry point for `python -m server`
  config.py         Constants, providers, personas, prompts, guide topics
  html.py           HTML and CSS template string
  ui.py             Browser SPA JavaScript
  timechain.py      Session-aware Timechain, memory, Workbench, gallery lineage
  llm.py            Provider calls, prompt assembly, memory prompts, image calls, frame metadata parsing
  poq.py            PoQ review, repair prompts, overfitting checks, Cambium frame/evasion scoring
  chat.py           Chat, recall, session, memory, guide, and Timechain action handlers
  marketplace.py    Marketplace and Creator Studio route handlers
  imagegen.py       ImageGen generate/edit/redefine/delete handlers
  auth.py           Login, register, logout, token verification
  server.py         HTTP server class, route dispatch, CLI args, startup
```

The root `timechain.py` remains the low-level library. `server/timechain.py` is the app-specific, user/session-aware layer on top.

## Timechain Responsibilities

- Load, append, recall, verify, freeze, reset, archive, and rewind session chains.
- Manage global and session-local memory models.
- Stage, accept, reject, edit, forget, and supersede durable memory candidates.
- Reconstruct visible chat history from accepted rings.
- Build self-model, ring timeline, Cambium, overlays, Dream, Shared Memory, Sync Snapshot, Memory Sync, fleet import, temporal challenge, and memory-anchor outputs.
- Persist PoQ Cambium frame-shift events in `.timechain/cambium_events.json` for Workbench summaries.
- Store ImageGen gallery files and seal image-domain lineage rings under `data/users/<username>/gallery/.timechain/`.

## PoQ/Cambium Split

- `server/llm.py` instructs the model to attach hidden `CT_FRAME_DECLARATION` metadata only for real Cambium frame shifts, strips that metadata from visible chat, and forwards the parsed sidecar.
- `server/poq.py` scores the sidecar for reason specificity, frame coherence, and answer follow-through. Valid or weak shifts can skip deterministic overfitting rejection; shallow shifts are marked as evasion and fail PoQ.
- `server/timechain.py` records valid/evasive PoQ Cambium events and includes their summary in `/api/cambium`.
