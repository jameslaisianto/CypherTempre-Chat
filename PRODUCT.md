# Forge — Product Vision (CypherTempre PoC)

**Forge** is the application shell. **CypherTempre** is the personal intelligence
runtime it proves out. This host is a proof-of-concept for that continuum.

You should choose this over ChatGPT or Grok when continuity, ownership, and
honest self-modeling matter more than a polished generic chat box.

## Positioning

**CypherTempre is a personal intelligence runtime with a verifiable memory.**
**Forge is the local chat host built to exercise it.**

| | ChatGPT / Grok | CypherTempre |
|--|--|--|
| Memory | Opaque provider memory | Local append-only Timechain you can verify |
| Honesty | Model confidence | PoQ gate + uncertainty reseals |
| Continuity | Session chat history | Hash-linked rings + durable reviewed memory |
| Ownership | Their servers, their terms | Your machine, your chain, your keys |
| Identity | One generic assistant | Personas + marketplace + covenant |
| Growth | Static model | Cambium / dream / faculty growth on the skill |

The models are interchangeable (OpenRouter, Morpheus, Kimi, SurplusIntelligence…).
**The product is the self-model around the model.**

## Daily-driver standard

Treat every release against this bar:

1. **Opens in one click** — `Start CypherTempre.bat` or `python -m server`
2. **Feels as fast as commercial chat** — streaming, snappy UI, clear loading
3. **Remembers what you care about** — durable memory review is friction-light; recall hits when it should
4. **Never pretends** — rejected / uncertain turns stay honest
5. **You can audit it** — verify chain, inspect rings, export sync snapshot
6. **Works on phone** — PWA + same Wi‑Fi launcher already exist; keep them first-class
7. **Your data stays yours** — local files under `data/users/…`

## Current stack (post skill integration)

- **Cognitive engine:** Cypher Tempre skill v3.28 (OpenClaw bundle) in `skill/`
- **Host app:** multi-user chat, personas, marketplace, Memory Inspector, Image/Video studios
- **Seal path:** skill PoQ + optional LLM critique scores

## Product roadmap (priority order)

### P0 — “I use this every day” ✅ implemented

| Item | Status |
|--|--|
| **Streaming replies** | `/api/chat/stream` SSE + UI progressive tokens; PoQ seal still on final event |
| **Recommended defaults** | Settings → “Apply recommended defaults”; `RECOMMENDED_PROFILE` in `server/product.py` |
| **Memory autopilot** | off / conservative / trusted — auto-accepts staged memories after seal |
| **Identity bridge** | user `identity/` Timechain + automatic cross-session recall when enabled |
| **Trust strip** | always-visible skill version, verify, height, last seal, product prefs |

### P1 — “I prefer this for real work” ✅ implemented

| Item | Status |
|--|--|
| **Cited answers from chain** | skill `Recall.answer` span-guard after generation; UI citation box |
| **Project / task chains** | Session project mode + `task/` sub-chain for progress seals |
| **Export / backup / restore** | `/api/backup/export` zip + restore merge/replace (`server/workpack.py`) |
| **Offline-friendly local fallback** | Answers from durable memory + sealed rings when provider is down |
| **Keyboard-first power UX** | Ctrl/Cmd+K command palette (sessions, verify, backup, project, …) |

### P2 — “This is a platform”

| Item | Why |
|--|--|
| Multi-device sync (optional encrypted) | Without surrendering chain ownership |
| Team / dual-seal personas | Collaboration without a shared black box |
| Packaged installer (Windows/macOS) | Non-developer install |
| Public skill-upgrade channel | One-click skill update preserving chains |

## Non-goals

- Becoming another thin wrapper around one closed model API
- Claiming AGI or “full native architecture” beyond what the skill + host actually do
- Shipping silent model-authored executable code (skill propose-then-activate stays)

## Success metric (personal)

You stop opening ChatGPT/Grok for:

- ongoing projects with decisions and corrections
- personal preferences and working style
- anything you want to **verify later**

You still open them when you only need a disposable one-shot answer with zero local state — and that’s fine. CypherTempre wins the **continuum**, not the throwaway.

## Versioning

- App host: `Forge/0.1` (PoC shell for CypherTempre)
- Skill engine: pin in `skill/cypher-tempre-self-model/VERSION`
