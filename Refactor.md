So timechain.py should own everything Timechain-related: not just the low-level operations, but also the server-level Timechain logic like session paths, memory model management, cambium scanning, overlays, dream synthesis, fleet import, challenge, memory sync, etc.

Here's the updated plan:

Final Structure

server/
├── __init__.py          # Package init
├── __main__.py          # Entry point: argparse + run server
├── config.py            # Constants, providers, personas, prompts, guide topics (pure data)
├── html.py              # The HTML + CSS template string
├── ui.py                # The inline JavaScript SPA string
├── timechain.py         # ALL Timechain operations: load/append/recall/verify, self-model, cambium, overlays, dream, fleet, challenge, memory sync, session workspace paths
├── llm.py               # LLM provider calls, PoQ scoring, fallback generator, image generation
├── chat.py              # Chat handler: message processing, persona selection, memory injection, response sealing
├── marketplace.py       # Marketplace routes: listing, detail, subscribe, creator studio, publish
├── auth.py              # Auth routes: login, register, logout, token verification
├── server.py            # HTTP server class, route dispatch, all do_GET/do_POST routing, main()
What goes into timechain.py
Everything from server.py that touches the Timechain:

load_timechain() — loads chain.jsonl for a session
append_ring() — seals a new ring
recall() — search rings + memory facts
verify_chain() — hash chain verification
summarize_self_model() — self-model summary
scan_cambium() — gap detection + growth proposals
save_overlay() / load_overlays()
run_dream() — cross-domain synthesis
fleet_import() — import foreign ring
run_challenge() — temporal proof
memory_sync() — write MEMORY.md
get_session_path() — workspace path resolution
reset_chain() — delete + recreate chain
archive_and_rewind() — archive + truncate
freeze_chain() / unfreeze_chain()
load_memory_model() / save_memory_model() — memory.json CRUD
extract_memory_candidates() — post-chat memory extraction
restore_history() — reconstruct chat from rings
This keeps the existing root timechain.py as the low-level library, while server/timechain.py adds the server-specific session-aware layer on top.