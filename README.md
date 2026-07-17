# Forge

**Forge** is the local application shell — a **proof-of-concept host for CypherTempre**, the personal intelligence runtime with a verifiable Timechain self-model.

Choose this when you want **continuity you own**: sealed memory, Proof-of-Qualia honesty, personas, and audit trails that outlive any single model provider.

See [PRODUCT.md](PRODUCT.md) for the product vision and roadmap, and [LICENSE](LICENSE) for the Cypher Tempre Open Intelligence License (CTOIL), attribution to Michael Joseph / CyberphysicsAI, and architecture disclaimer.

Chat Session  
<img width="2537" height="1324" alt="image" src="https://github.com/user-attachments/assets/175c8973-3981-4e5b-84b1-bc57acb24819" />

Guide  
<img width="2537" height="1303" alt="image" src="https://github.com/user-attachments/assets/9e060e33-5e9a-4ae0-85dc-4cd9c14b4700" />

Settings  
<img width="2542" height="1133" alt="image" src="https://github.com/user-attachments/assets/e154c6d0-b528-4beb-8de2-76d5b0fd0437" />

Marketplace  
<img width="1970" height="993" alt="image" src="https://github.com/user-attachments/assets/a32fcc5a-0d64-4e87-babf-36045bc5bcc4" />

## Why not just ChatGPT or Grok?

| They win at | CypherTempre wins at |
|--|--|
| One-shot answers, polished mobile apps | **Owned memory** — append-only Timechain on your machine |
| Huge default models | **Honest sealing** — PoQ gate + uncertainty, not fake confidence |
| Opaque “memory” toggles | **Auditable history** — verify hashes, inspect rings, export snapshots |
| One product persona | **Personas + marketplace** you can train and publish |
| Vendor lock-in | **Provider-agnostic** models; the chain outlives the API |

The LLM is swappable. **The self-model is the product.**

## Features

- Chat UI built for daily use (desktop + mobile/PWA)
- **User accounts** — private sessions and personas per user
- Provider-agnostic models (SurplusIntelligence, Morpheus, OpenRouter, Kimi, custom OpenAI-compatible)
- Built-in personas + Persona Studio
- **Cypher Tempre OpenClaw Runtime** — skill v3.28 vendored engine (Timechain, PoQ, recall, Cambium, dream). Full host + skill integration for the existing chat flow; does not require any new provider, runtime abstraction, or external integration beyond your chosen LLM API. Honest scope: this is not a claim of closed-source native architecture beyond what the open skill implements
- PoQ-gated sealing of accepted turns into a hash-linked ledger
- Durable memory review (Memory Inspector): accept / reject / edit / forget
- Global profile memories + session-local notes
- Multi-session workspaces with separate chains
- **Shared Memory** — opt-in cross-session recall and import
- **Persona Marketplace** + Creator Studio
- Timechain Workbench — rings, Cambium, dream, overlays, fleet import, temporal challenge
- ImageGen + VidGen studios with lineage rings
- Guide with source-grounded explanations
- Windows one-click launcher: `Start CypherTempre.bat`

## Quick start

### 1. Python 3.11+

```powershell
python --version
```

### 2. Project layout

From the repo root you should have:

```text
CypherTempre-Chat/
  server/
  skill/cypher-tempre-self-model/   # vendored skill engine
  .env.example
  Start CypherTempre.bat
```

### 3. API key

Pick a provider and create a key. Example Morpheus uncensored default:

```text
gemma-4-uncensored
```

### 4. Local env

```powershell
Copy-Item .\.env.example .\.env.local
```

Edit `.env.local` (gitignored):

```text
PROVIDER=morpheus
API_KEY=YOUR_API_KEY
MODEL=gemma-4-uncensored
BASE_URL=https://api.mor.org/api/v1
POQ_ENABLED=true
POQ_MIN_SCORE=7
POQ_MAX_RETRIES=1
POQ_OVERFITTING_CHECK=true
```

### 5. Run

```powershell
python -m server --port 8765
```

Or double-click **`Start CypherTempre.bat`**.

Open [http://127.0.0.1:8765](http://127.0.0.1:8765) — register/login, then chat.

Optional skill path:

```powershell
python -m server --skill-root ".\skill\cypher-tempre-self-model"
```

## Daily use

- **Enter** sends · **Shift+Enter** newline
- Under each accepted reply: model, domain, ring #, brightness, memory hits, epistemic status
- Review **Memory Inspector** so durable facts stay high quality
- Use **Sessions** for project separation; enable **Shared Memory** when you want cross-session bounce
- **Workbench** when you need verify / dream / import / challenge
- Reset clears only the **active session** chain (not your API keys)

## Where your mind lives

Skill Timechain (per session):

```text
data/users/<username>/sessions/<session-id>/chain/rings.jsonl
data/users/<username>/sessions/<session-id>/registry/
```

App durable memory (review queue + accepted facts):

```text
data/users/<username>/sessions/<session-id>/.timechain/memory_model.json
```

Personas, gallery, video:

```text
data/users/<username>/custom_personas.json
data/users/<username>/gallery/
data/users/<username>/videogen/
```

Nothing required is uploaded by the core runtime. Optional embedding providers (if you enable them on the skill) may send text off-machine — default is local.

## Architecture (short)

```text
Browser UI  →  server/ (host)  →  skill/cypher-tempre-self-model (engine)
                     │
                     ├─ LLM providers (chat / image / video / audio)
                     ├─ Memory Inspector product layer
                     └─ Marketplace / personas
```

See [Refactor.md](Refactor.md), [skill/README.md](skill/README.md), and [PRODUCT.md](PRODUCT.md).

## Development

```powershell
python -m pytest test_server.py -q
```

## License

Cypher Tempre Open Intelligence License (CTOIL) — see [LICENSE](LICENSE).
