# CypherTempre Chat PoC: Setup From Scratch

This guide shows how to run the local chat demo on your computer.

This demo points back to the Cypher Tempre Project. See [LICENSE](LICENSE) for the Cypher Tempre Open Intelligence License (CTOIL), attribution, and disclaimer.

## 1. Open PowerShell

Go to the repo folder:

```powershell
cd path\to\CypherTempre-Chat
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
python -m server
```

You should see something like:

```text
CypherTempre chat PoC running at http://127.0.0.1:8765
```

**Easy way:** Double-click `Start CypherTempre.bat`. It starts the server and shows the address to use on your phone.

## 5. Open It In Your Browser

Open:

```text
http://127.0.0.1:8765
```

## 6. Log In or Register

When the page loads, you will see a login screen.

1. Click **Register** if this is your first time.
2. Pick a username and password.
3. Click **Log in** after you register.

Your chats, sessions, and custom personas are saved under your account. They are private to you.

## Use It On Your Phone

The app works on your phone too.

1. Make sure your phone is on the same Wi-Fi as your computer.
2. Use `Start CypherTempre.bat` or start the server with:
   ```powershell
   python -m server --host 0.0.0.0
   ```
3. On your phone browser, go to the address the batch file shows you.
4. If it does not load, run this in PowerShell once:
   ```powershell
   New-NetFirewallRule -DisplayName "CypherTempre Chat" -Direction Inbound -LocalPort 8765 -Protocol TCP -Action Allow
   ```

### Add It To Your Home Screen

In Chrome or Samsung Internet on your phone:

1. Open the site.
2. Tap the menu (the three dots).
3. Tap **"Add to Home screen"**.
4. It now opens like a real app with no browser bar.

## 7. Test OpenRouter

In the app:

1. Click the small gear icon in the left rail.
2. Check that the model is filled in.
3. Click `Test`.

If OpenRouter is working, you will see an OK message.

If it says `429 Too Many Requests`, the free model is rate-limited. Wait a bit or use another OpenRouter model.

## 8. Start Chatting

Click `Chat`, type a message, and press Enter.

The app will:

1. Send your message to OpenRouter if a key is available.
2. Score the reply with the PoQ gate.
3. Save accepted replies into local memory.
4. Show memory metadata under the response.

## 9. Use The Guide

Click `Guide`.

Each card has an `Explain` button.

Clicking `Explain` creates a new chat session that explains that topic using local guide text and local docs.

## 10. Stop The App

Go back to PowerShell and press:

```text
Ctrl+C
```

## Where Stuff Is Saved

Your chat history and sessions are saved under your username:

```text
data\users\<your-username>\sessions\<session-name>\.timechain\chain.jsonl
```

Your custom personas:

```text
data\users\<your-username>\custom_personas.json
```

Global memory (shared):

```text
.timechain\chain.jsonl
```

App-local guide source notes:

```text
SKILLS\README.md
```

Your API key:

```text
.env.local
```

## What Changed In The Refactor

The app no longer starts from one big `server.py` file.

It now starts from the `server` package:

```text
server\
  __main__.py      starts the app when you run python -m server
  server.py        HTTP server and route dispatch
  chat.py          chat, sessions, personas, memory actions
  auth.py          login, register, logout
  marketplace.py   marketplace and creator routes
  imagegen.py      image generation routes
  timechain.py     app Timechain/session logic
  llm.py           provider calls and prompt building
  config.py        settings, personas, guide topics
  html.py          page template
  ui.py            browser app JavaScript
```

So use this command now:

```powershell
python -m server
```
