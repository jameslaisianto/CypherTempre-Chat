# Server Refactor Map

`server/skill_runtime.py` loads the vendored Cypher Tempre skill (v3.28+) and
owns session skill roots, ring views, seal/recall helpers, and workbench
backends. `server/timechain.py` is the HTTP App host: sessions, memory model,
Workbench product APIs, gallery/video lineage, and chat orchestration on top
of that skill.

## Current Structure

```text
skill/
  cypher-tempre-self-model/   Vendored OpenClaw skill (timechain, poq, recall, cambium, dream, …)

server/
  __init__.py       Public compatibility exports
  __main__.py       Entry point for `python -m server`
  config.py         Constants, providers, personas, prompts, guide topics
  html.py           HTML and CSS template string
  ui.py             Browser SPA JavaScript
  skill_runtime.py  Skill bootstrap, session roots, seal/recall, RingView
  timechain.py      App host: sessions, memory, Workbench, gallery lineage
  llm.py            Provider calls, prompt assembly, memory prompts, image calls
  poq.py            LLM PoQ critique/repair → skill six-dim external_scores
  chat.py           Chat, recall, session, memory, guide, and Timechain action handlers
  marketplace.py    Marketplace and Creator Studio route handlers
  imagegen.py       ImageGen generate/edit/redefine/delete handlers
  auth.py           Login, register, logout, token verification
  server.py         HTTP server class, route dispatch, CLI args, startup
```

Root `timechain.py` is a thin compatibility entry that points at the skill bundle.
Session ledgers live at `data/users/<user>/sessions/<id>/chain/rings.jsonl`.

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
