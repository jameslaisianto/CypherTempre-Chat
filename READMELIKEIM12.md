# CypherTempre: setup like you're 12

This is your **own chat app** with a real memory chain — not a school demo.

## 1. Install Python

Install Python 3.11 or newer from python.org. Check:

```powershell
python --version
```

## 2. Get an API key

Sign up with a model provider (Morpheus, OpenRouter, Kimi, SurplusIntelligence, …) and copy a key.

## 3. Put the key in a secret file

In this folder:

```powershell
Copy-Item .\.env.example .\.env.local
```

Open `.env.local` and set `API_KEY=` (and `PROVIDER=` / `MODEL=` if you want).

## 4. Start it

Double-click **`Start CypherTempre.bat`**

or:

```powershell
python -m server --port 8765
```

## 5. Open it

Go to: [http://127.0.0.1:8765](http://127.0.0.1:8765)

Register an account. Chat. Your sealed turns live in a Timechain on **your** computer.

## Why bother?

ChatGPT forgets or remembers in a black box.  
CypherTempre **seals** what it keeps, can **verify** the chain, and lets **you** review durable memories.

Read [PRODUCT.md](PRODUCT.md) when you want the grown-up version.
