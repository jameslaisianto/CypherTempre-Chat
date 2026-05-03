# CypherTempre Chat PoC: Setup From Scratch

This guide shows how to run the local chat demo on your computer.

This demo points back to the Cypher Tempre Project. See [LICENSE](LICENSE) for the Cypher Tempre Open Intelligence License (CTOIL), attribution, and disclaimer.

## 1. Open PowerShell

Go to the repo folder:

```powershell
cd path\to\Aetherchain\cyphertempre-chat-poc
```

## 2. Check Python

Run:

```powershell
python --version
```

You need Python 3.11 or newer.

If that command does not work, install Python from:

```text
https://www.python.org/downloads/
```

During install, turn on:

```text
Add Python to PATH
```

Then close PowerShell, open it again, and run:

```powershell
python --version
```

## 3. Create Your Local Env File

Copy the example file:

```powershell
Copy-Item .env.example .env.local
```

Open `.env.local` in a text editor.

Put your own OpenRouter key here:

```text
OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY
OPENROUTER_MODEL=cognitivecomputations/dolphin-mistral-24b-venice-edition:free
```

Do not share `.env.local`. It contains your private key.

## 4. Run The App

Start the local server:

```powershell
python server.py
```

You should see something like:

```text
CypherTempre chat PoC running at http://127.0.0.1:8765
```

## 5. Open It In Your Browser

Open:

```text
http://127.0.0.1:8765
```

## 6. Test OpenRouter

In the app:

1. Click the small gear icon in the left rail.
2. Check that the model is filled in.
3. Click `Test`.

If OpenRouter is working, you will see an OK message.

If it says `429 Too Many Requests`, the free model is rate-limited. Wait a bit or use another OpenRouter model.

## 7. Start Chatting

Click `Chat`, type a message, and press Enter.

The app will:

1. Send your message to OpenRouter if a key is available.
2. Score the reply with the PoQ gate.
3. Save accepted replies into local memory.
4. Show memory metadata under the response.

## 8. Use The Guide

Click `Guide`.

Each card has an `Explain` button.

Clicking `Explain` creates a new chat session that explains that topic using local guide text and local docs.

## 9. Stop The App

Go back to PowerShell and press:

```text
Ctrl+C
```

## Where Stuff Is Saved

Chat memory:

```text
.timechain\chain.jsonl
```

Custom personas:

```text
.timechain\custom_personas.json
```

Separate sessions:

```text
sessions\<session-name>\.timechain\chain.jsonl
```

App-local guide source notes:

```text
SKILLS\README.md
```

Your API key:

```text
.env.local
```
