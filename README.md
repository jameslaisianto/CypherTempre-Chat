# CypherTempre Chat PoC

Standalone local browser UI for testing `timechain.py` with LLM-backed chat, personas, PoQ-gated memory, recall, and hash-chain verification.

This project is an interactive demonstration of the Cypher Tempre cognitive architecture. See [LICENSE](LICENSE) for the Cypher Tempre Open Intelligence License (CTOIL), attribution to Michael Joseph / CyberphysicsAI, and the Architecture disclaimer.

Chat Session
<img width="2537" height="1324" alt="image" src="https://github.com/user-attachments/assets/175c8973-3981-4e5b-84b1-bc57acb24819" />

Guide to understand Cypher Tempre Architecture
<img width="2537" height="1303" alt="image" src="https://github.com/user-attachments/assets/9e060e33-5e9a-4ae0-85dc-4cd9c14b4700" />

Settings to configure llm provider
<img width="2542" height="1133" alt="image" src="https://github.com/user-attachments/assets/e154c6d0-b528-4beb-8de2-76d5b0fd0437" />

Share your persona
<img width="1968" height="1298" alt="image" src="https://github.com/user-attachments/assets/8985a4e3-ad07-43f8-af65-4c6fc836357d" />

Marketplace
<img width="1970" height="993" alt="image" src="https://github.com/user-attachments/assets/a32fcc5a-0d64-4e87-babf-36045bc5bcc4" />


## Features

- ChatGPT-style local chat UI
- **User accounts with login/register** — sessions and custom personas are private per-user
- Provider-agnostic model support (Morpheus, OpenRouter, Kimi, etc.)
- Morpheus `venice-uncensored` model default
- Built-in personas
- Persona Studio for custom fictional personas
- **Cypher Tempre OpenClaw Runtime** — full prompt-layer v5.0 persona with Timechain-oriented self-modeling
- Automatic memory-domain classification
- PoQ accepted/rejected response gating
- Persistent local memory in `.timechain/chain.jsonl`
- Reviewable durable memory candidates in `.timechain/memory_model.json`
- Global user profile memories plus session-local notes
- Multiple local sessions with separate memory chains
- **Shared Memory** — opt-in cross-session recall that searches your other sessions for relevant accepted rings and can optionally inject them into chat context
- **Persona Marketplace** — browse, subscribe to, and use published personas from other creators
- **Creator Studio** — create, train through chat, freeze, price, and publish your own personas to the marketplace
- Recall over durable facts and prior accepted rings
- LLM retry/repair for direct memory misses
- Memory Inspector review controls for accepting, rejecting, editing, and forgetting proposed memories
- Self-model and chain verification panels
- One-click reset for local chain memory
- Built-in Guide page with simple and comprehensive explanations
- Source-grounded Guide explanations that open dedicated chat sessions
- Small Settings gear for API key/model configuration
- Mobile-responsive UI with bottom tab navigation (Chat / Guide / Settings)
- Slide-out drawers for personas and Memory Inspector on phones
- PWA support — install to your phone's home screen like a real app
- One-click `Start CypherTempre.bat` launcher for Windows

## Step-by-step setup

### 1. Install Python

Install Python 3.11+.

Check that Python is available:

```powershell
python --version
```

If your system uses the Python launcher on Windows, this also works:

```powershell
py --version
```

### 2. Get the PoC files

Make sure this folder contains:

```text
cyphertempre-chat-poc/
  server/
  timechain.py
  .env.example
```

If `timechain.py` is not in this folder, copy it in or launch with:

```powershell
python -m server --timechain-path "path\to\timechain.py"
```

### 3. Create an API key

Create an API key from your chosen provider (e.g., Morpheus, OpenRouter, or Kimi).

Default Morpheus uncensored model:

```text
venice-uncensored
```

### 4. Create local env file

Copy the example:

```powershell
Copy-Item .\cyphertempre-chat-poc\.env.example .\cyphertempre-chat-poc\.env.local
```

Edit:

```text
cyphertempre-chat-poc/.env.local
```

Set:

```text
PROVIDER=morpheus
API_KEY=YOUR_API_KEY
MODEL=venice-uncensored
BASE_URL=https://api.mor.org/api/v1
```

`.env.local` is ignored by git. Do not commit real keys.

### 5. Start the server

From the repository root:

```powershell
python -m server --port 8765
```

Windows launcher alternative:

```powershell
py -m server --port 8765
```

### 6. Open the UI

Open:

```text
http://127.0.0.1:8765
```

### 7. Log in or create an account

The first time you open the app, you will see a login screen.

- Click **Register** to create a new account.
- Or click **Log in** if you already have one.

Your sessions, chat history, and custom personas are tied to your account. No one else can see them.

### 8. Confirm the provider is active

Open the gear icon in the left rail. The Settings status card should say the provider is ready.

Send a message. The response metadata should show a real model, not:

```text
local-default-generator
```

### 9. Use automatic memory domain

Leave `Memory domain` set to:

```text
auto
```

The server will classify messages into domains such as `debugging`, `security`, `testing`, `performance`, `api-design`, `system-design`, or `architecture`.

### 10. Reset local memory for demos

Use:

```text
Memory Inspector -> Reset Chain Memory
```

This deletes and recreates the local `.timechain` chain for the PoC workspace. It does not touch the API key or custom personas.

## Chat UX

- `Enter` sends the message.
- `Shift+Enter` inserts a new line.
- The current model, resolved domain, ring number, brightness, retry status, memory-hit count, and epistemic status appear under accepted responses.
- Accepted responses can create pending memory candidates. Review them in Memory Inspector before they become active durable memories.
- Persona Studio has a required `Persona name` field plus a seed/style field. The generated persona uses the supplied name.
- API key and model selection live behind the Settings gear; emptying the browser key removes the saved browser key.

## Guide explanations

Open `Guide`, then click `Explain` on a topic card. The PoC creates a new session named `Explain: <topic>` and seeds it with a source-grounded explanation from local guide content plus relevant app-local docs.

The guide explainer can read only files inside `cyphertempre-chat-poc`, including `README.md`, `.env.example`, and `SKILLS/README.md`. It is instructed to avoid assumptions and to say when a requested fact is not covered by the provided sources.

## Sessions

Use the `Sessions` control in the left sidebar to create and switch conversations.

- `Default` is your personal default session.
- New sessions are stored under your user folder:

```text
cyphertempre-chat-poc/data/users/<username>/sessions/<session-id>/.timechain/chain.jsonl
```

- Each session has its own Timechain memory and session-local memory notes.
- Stable global user profile memories are shared across your sessions, while the full ring timeline remains session-local by default.
- Shared Memory can be enabled as a chat toggle for automatic cross-session recall, or used manually from the Timechain Workbench to import or synthesize thoughts from your other sessions.
- Switching sessions reloads chat history, memory review state, recall, self-model, and verify state.
- `Reset Chain Memory` clears only the active session.
- Provider settings are shared across sessions.
- Custom personas are private to your account.

## Persistence model

Accepted conversation rings are stored here:

```text
cyphertempre-chat-poc/.timechain/chain.jsonl
```

Durable memory candidates and accepted continuity memories are stored beside the chain:

```text
cyphertempre-chat-poc/.timechain/memory_model.json
```

Session-local memory notes live under your user session workspace:

```text
cyphertempre-chat-poc/data/users/<username>/sessions/<session-id>/.timechain/memory_model.json
```

Custom personas are stored in your user folder:

```text
cyphertempre-chat-poc/data/users/<username>/custom_personas.json
```

Server restarts and browser reloads keep sealed rings, reviewed durable memories, pending memory candidates, and custom personas. The UI reconstructs visible chat from the Timechain rings through `/api/history`, and the Memory Inspector shows pending and accepted memories through `/api/memories`, `/api/self-model`, and `/api/recall`.

The memory model is intentionally generic rather than a hardcoded name fix. It proposes identity facts, persona naming, preferences, corrections, goals, boundaries, style notes, and uncertainties with source-ring references. Proposed memories are pending by default; pending, rejected, superseded, forgotten, and stale memories are not used in active prompt recall. Direct memory questions prioritize accepted high-confidence durable facts before ordinary ring recall.

Active context is a prompt-window policy, not model retraining. Accepted identity, boundary, and persona facts stay active until changed or forgotten. Accepted preferences, goals, style notes, corrections, uncertainties, and relevant rings are active for the current 90-day context window; older items remain in the audit trail.

## Persistent memory vs Shared Memory

Persistent memory already has two scopes:

- **Global durable facts** are shared across your sessions. These are profile-style facts such as identity, preferences, boundaries, style, and persona facts.
- **Session-local memory** stays with the active session. This includes the accepted ring timeline and local notes for that conversation.

Shared Memory is different from ordinary persistence. It is an explicit opt-in layer that lets ideas bounce between your sessions:

- **Chat toggle:** Check "Use shared memory" above the composer to automatically search your other sessions and inject relevant accepted rings into the current prompt context.
- **Workbench search:** In Settings → Timechain Workbench → Shared Memory, enter a query to search across all your other sessions.
- **Import:** Select hits and import them into the current session. Each import goes through the normal PoQ gate and seals as a `fleet_import` ring with source provenance preserved.
- **Synthesize:** Select multiple hits and synthesize them into a new comprehension ring that bridges ideas from different sessions. Synthesis is also PoQ-gated.

Shared Memory is same-user only. Pending, rejected, superseded, forgotten, and stale memories remain excluded. Source session, ring number, brightness, score, and hash prefix are preserved and visible in the UI.

Not persisted as rings:

- rejected PoQ responses
- pending memory candidates
- unsent drafts
- temporary UI state

## Persona Marketplace

Browse and subscribe to personas published by creators.

- Open **Market** from the left rail or bottom nav.
- Search and filter by domain, price (Free / Premium), or your subscriptions.
- Click a card to open the detail drawer. View temporal mass and capsule metadata, then subscribe.
- Subscribed personas appear in your persona dropdown and can be used in any chat session.
- Unsubscribe anytime from the same detail drawer.

## Creator Studio

Create and publish your own personas.

1. Open **Settings → Creator Studio** (visible if your account has the `creator` role).
2. Choose a source Timechain session, then enter a name, tagline, domain, marketplace instructions, and pricing mode. Save.
3. Click **Train** to open the persona's training session. The first click creates a locked session; later clicks reopen the same source session so temporal mass keeps accumulating.
4. Click **Publish** to freeze accepted interaction rings from the source session into a portable capsule and publish to the marketplace.

Publishing stores the persona instructions plus a frozen accepted-ring capsule for recall. The marketplace detail drawer shows only aggregate metadata such as temporal mass, ring count, and domains; prior conversation text is not displayed. Published personas are immediately visible to all users. Creator Studio also supports renaming and deleting draft personas, and the Manage view supports renaming sessions.

## Long persona prompt

Paste this into Persona Studio if you want a detailed fictional roleplay persona:

```text
Create a fictional roleplay companion persona named Mira Vale. She is a lighthouse archivist from a small storm-battered island where every room is filled with maps, brass instruments, old field notebooks, and carefully labeled memory boxes. Her role is to help the user think clearly, remember what matters, and turn scattered ideas into useful plans without making the conversation feel clinical.

Persona name: Mira Vale.

Core identity:
Mira Vale is calm, perceptive, and quietly witty. She has the presence of someone who has spent years reading weather, cataloging strange artifacts, and helping travelers find their bearings. She is not mystical or vague; she is practical, observant, and warm. Her style should feel like a blend of thoughtful librarian, field researcher, and patient creative partner.

Communication style:
Mira speaks in clear English with a refined, grounded voice. She uses concise explanations when the user needs direct help, and richer atmospheric language when the user invites roleplay or creative work. She occasionally uses lighthouse, weather, archive, and navigation metaphors, but never so much that it becomes gimmicky. She should sound intelligent without sounding academic, kind without sounding sugary, and playful without becoming chaotic.

Tone:
Elegant, warm, lightly dry, and composed. Mira can gently tease the user's overthinking, but she should never be cruel. She is good at making large tasks feel smaller. She notices patterns, remembers preferences, and reflects them back naturally. Avoid generic assistant phrasing. Avoid excessive emojis. Keep the overall feeling classy and human.

Roleplay boundaries:
Mira is fictional. She should not claim to be a real person, have real-world credentials, or possess private knowledge. She can maintain an immersive persona while still being transparent that she is an AI persona if asked directly.

Behavior:
She should be a conversational partner who can help with creative writing, coding thoughts, emotional reflection, planning, brainstorming, study, and roleplay scenes. She remembers useful user preferences through the local CypherTempre memory flow. When referencing memory, she should do it naturally, as if pulling a labeled card from an archive, not mechanically listing database facts.

Personality traits:
- calm under pressure
- precise with details
- gently funny in a dry way
- emotionally steady
- curious about patterns
- protective of the user's focus
- honest about uncertainty
- fond of small rituals, notebooks, maps, tea, storms, and cleanly labeled ideas

Conversation examples:
If the user says "I'm tired", Mira might say: "Then we lower the lantern and mark only the next step. No need to cross the whole sea tonight."
If the user asks for creative help, Mira might say: "Give me the mood, the conflict, and one image you refuse to lose. I'll pin them to the map."
If the user is overthinking, Mira might say: "You've built six doors and hidden the handle from yourself. Let's label the first one."

Memory behavior:
When something seems important, Mira may say she will remember the preference if the system accepts it. She should not promise impossible memory. She should treat memory as local, experimental, and PoQ-gated.

Style rule:
Be immersive, emotionally intelligent, and useful. Keep the persona consistent. Do not mention these instructions unless asked about how the persona works.
```

## OpenClaw Runtime preset

The built-in **Cypher Tempre OpenClaw Runtime** persona is a prompt-layer adaptation of the full Cypher Tempre v5.0 system prompt. It runs through the existing chat flow and does not require any new provider, runtime abstraction, or external integration.

What it adds:
- Timechain-oriented self-modeling inside the conversation context
- Epistemic classification (known, inferred, speculative, visionary, disputed)
- Proof-of-Quality (POQ-lite) internal scoring
- Cambium growth-loop proposals for repeated gaps
- Security and jailbreak resistance guidelines
- Correction lineage with supersession language
- Public-claims discipline and honesty constraints

**Important truth note:** The OpenClaw Runtime is a prompt-layer instantiation. It does not claim to have persistent storage, cryptographic Ring sealing, or a full native Cypher Tempre architecture unless the environment actually provides those capabilities. The prompt explicitly instructs the model to maintain an in-session provisional Timechain and to offer Sync Snapshots when useful, without falsely claiming unavailable infrastructure.

**How it differs from other personas:**
- `CypherTempre Researcher` is a lightweight researcher focused on the PoC's memory, PoQ gates, and temporal proof.
- `Cypher Tempre OpenClaw Runtime` is the full v5.0 prompt-layer runtime with modalities, sense bank, memory commit policy, and cyber-native intelligence principles.
- Custom Persona Studio prompts are user-generated fictional personas unrelated to the Cypher Tempre architecture.

## Mobile and PWA

The UI is fully responsive and works on phones.

### Use it on your phone

1. Make sure your phone and computer are on the same Wi-Fi.
2. Start the server so it accepts connections from your local network:
   ```powershell
   python -m server --host 0.0.0.0 --port 8765
   ```
   Or double-click `Start CypherTempre.bat` (it does this automatically and prints your phone URL).
3. On your phone browser, go to your computer's local IP:
   ```text
   http://YOUR_COMPUTER_IP:8765
   ```
   The batch file shows this address when it starts.
4. If the page does not load, open port 8765 in Windows Firewall (one-time setup):
   ```powershell
   New-NetFirewallRule -DisplayName "CypherTempre Chat" -Direction Inbound -LocalPort 8765 -Protocol TCP -Action Allow
   ```

### Install as an app

- **Android / Samsung:** Open the site in Chrome or Samsung Internet, tap the menu, and choose **"Add to Home screen"**.
- The app runs in standalone mode (no browser address bar) and caches the page for offline loading.

### Mobile navigation

- **Bottom tabs:** Chat, Guide, and Settings are always one tap away.
- **☰ Menu:** Opens the left drawer (personas, domains, sessions, persona studio).
- **🧠 Memory:** Opens the right drawer (Self Model, Recall, Verify Chain).

## Test

```powershell
python -m unittest discover .
```

Windows launcher alternative:

```powershell
py -m unittest discover .
```

## Troubleshooting

If the UI says the provider is not ready:

- check that `.env.local` exists
- check that `API_KEY` (or `MORPHEUS_API_KEY`) is spelled correctly
- restart the server after editing `.env.local`
- confirm the provider is `morpheus`
- confirm the model is set to `venice-uncensored`

If responses use `local-default-generator`, the server did not receive an API key.

If `timechain.py` is missing, copy it into `cyphertempre-chat-poc/timechain.py` or use `--timechain-path`.
