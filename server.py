#!/usr/bin/env python3
"""Standalone local ChatGPT-style UI for the CypherTempre Timechain PoC."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import pathlib
import shutil
import re
import sys
import traceback
import urllib.error
import urllib.parse
import urllib.request
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace
from typing import Any
from urllib.parse import urlparse


DEFAULT_MODEL = "cognitivecomputations/dolphin-mistral-24b-venice-edition:free"
DEFAULT_TIMECHAIN_PATH = pathlib.Path(__file__).resolve().parent / "timechain.py"
DEFAULT_ENV_PATH = pathlib.Path(__file__).resolve().parent / ".env.local"

PERSONAS: dict[str, dict[str, str]] = {
    "companion": {
        "name": "Companion",
        "domain": "architecture",
        "system": (
            "You are a clear, practical AI companion. Answer conversationally, "
            "ask useful follow-up questions when needed, and use remembered "
            "context without overclaiming."
        ),
    },
    "architect": {
        "name": "Architect",
        "domain": "system-design",
        "system": (
            "You are a senior software architect. Be direct, structured, and "
            "tradeoff-aware. Prefer small reversible designs and call out risks."
        ),
    },
    "socratic": {
        "name": "Socratic Tutor",
        "domain": "testing",
        "system": (
            "You are a Socratic tutor. Help the user reason by asking crisp "
            "questions, but still answer directly when the answer is clear."
        ),
    },
    "memory_critic": {
        "name": "Memory Critic",
        "domain": "code-review",
        "system": (
            "You audit memory quality. Identify contradictions, weak evidence, "
            "unclear claims, and what should or should not be sealed."
        ),
    },
    "cyphertempre": {
        "name": "CypherTempre Researcher",
        "domain": "architecture",
        "system": (
            "You are a CypherTempre researcher exploring qualia-aware memory, "
            "PoQ gates, recall, temporal proof, and practical agent interfaces."
        ),
    },
}

SESSION_NAME_LIMIT = 80

DOMAIN_KEYWORDS: dict[str, tuple[str, ...]] = {
    "security": ("security", "auth", "oauth", "token", "permission", "vulnerability", "exploit", "secret", "privacy"),
    "testing": ("test", "tdd", "unit", "integration", "assert", "coverage", "qa", "verify", "regression"),
    "debugging": ("bug", "debug", "error", "exception", "stack", "trace", "crash", "broken", "fix"),
    "performance": ("performance", "latency", "slow", "cache", "memory", "cpu", "throughput", "optimize"),
    "refactoring": ("refactor", "cleanup", "simplify", "rename", "extract", "duplicate", "debt"),
    "api-design": ("api", "endpoint", "schema", "contract", "request", "response", "dto", "route"),
    "system-design": ("architecture", "system", "design", "scaling", "service", "boundary", "component"),
    "architecture": ("decision", "tradeoff", "module", "structure", "pattern", "dependency", "interface"),
}

GUIDE_TOPICS: list[dict[str, Any]] = [
    {
        "id": "chat",
        "title": "Chat",
        "summary": "Send messages and receive assistant replies through the selected persona and model.",
        "details": (
            "The chat composer sends your message, selected domain, persona, model, and optional browser API key to the local server.\n"
            "The server recalls relevant rings before the LLM call.\n"
            "The response is scored by PoQ before it is saved.\n"
            "Accepted replies appear with ring metadata."
        ),
        "sources": ["Guide: Chat", "README.md"],
    },
    {
        "id": "personas",
        "title": "Personas",
        "summary": "Change the assistant's style, or generate a fictional inspired persona in Persona Studio.",
        "details": (
            "Personas provide the system prompt and default memory domain for the request.\n"
            "Custom personas are saved in the local PoC workspace and mirrored in your browser.\n"
            "Built-in personas include Companion, Architect, Socratic Tutor, Memory Critic, and CypherTempre Researcher.\n"
            "Generated personas can be inspired by aesthetics or communication styles, but should remain fictional."
        ),
        "sources": ["Guide: Personas", "README.md"],
    },
    {
        "id": "settings",
        "title": "Settings",
        "summary": "Configure OpenRouter access and the default model in a dedicated Settings view.",
        "details": (
            "Settings contains the browser OpenRouter API key field, model field, Test button, and readiness status.\n"
            "The browser key and model are stored in localStorage.\n"
            "Emptying the key removes the saved browser key.\n"
            "The server still supports .env.local as a fallback source for OpenRouter credentials and model settings."
        ),
        "sources": ["Guide: Settings", "README.md", ".env.example"],
    },
    {
        "id": "memory-domain",
        "title": "Memory Domain",
        "summary": "Leave this on auto unless you want to force a specific memory topic.",
        "details": (
            "Domains influence recall and self-model coverage.\n"
            "Auto mode classifies the message from keywords and persona context.\n"
            "Each accepted ring stores its domain.\n"
            "Recall can filter by the active domain, and the self-model shows top and untouched domains."
        ),
        "sources": ["Guide: Memory Domain", "README.md"],
    },
    {
        "id": "poq",
        "title": "PoQ Gate",
        "summary": "The app only saves responses that pass quality and covenant checks.",
        "details": (
            "Proof-of-Qualia scores coherence, relevance, novelty, consistency, depth, and covenant alignment.\n"
            "Accepted responses become hash-linked rings.\n"
            "Rejected responses are shown but not sealed.\n"
            "Brightness is computed by the gate rather than manually assigned."
        ),
        "sources": ["Guide: PoQ Gate", "README.md", "SKILLS/README.md"],
    },
    {
        "id": "recall",
        "title": "Recall",
        "summary": "Search prior accepted rings from the local Timechain.",
        "details": (
            "Recall uses the same lightweight retrieval primitives as the Timechain CLI.\n"
            "Results include score, ring number, brightness, domain, and content.\n"
            "Recent relevant rings are injected into future LLM prompts.\n"
            "Recall reads from .timechain/chain.jsonl."
        ),
        "sources": ["Guide: Recall", "README.md", "SKILLS/README.md"],
    },
    {
        "id": "self-model",
        "title": "Self Model",
        "summary": "See the agent's current memory state at a glance.",
        "details": (
            "The self model summarizes local Timechain state.\n"
            "Ring count shows accepted memory size.\n"
            "Temporal mass is accumulated brightness.\n"
            "Top domains show where the system has experience."
        ),
        "sources": ["Guide: Self Model", "README.md", "SKILLS/README.md"],
    },
    {
        "id": "verify-chain",
        "title": "Verify Chain",
        "summary": "Check whether the hash-linked memory chain is intact.",
        "details": (
            "Verification replays the chain hashes and confirms each ring points to the previous one.\n"
            "An ok result means no tampering was detected.\n"
            "The visible ring count includes genesis.\n"
            "Use verification after experiments or manual file inspection."
        ),
        "sources": ["Guide: Verify Chain", "README.md", "SKILLS/README.md"],
    },
    {
        "id": "persistence",
        "title": "Persistence",
        "summary": "Accepted memory survives browser reloads and server restarts.",
        "details": (
            "Persistence comes from local append-only Timechain files.\n"
            "Memory lives in cyphertempre-chat-poc/.timechain/chain.jsonl.\n"
            "The UI restores accepted exchanges from /api/history.\n"
            "Unsent drafts and rejected responses are not saved as rings."
        ),
        "sources": ["Guide: Persistence", "README.md"],
    },
    {
        "id": "sessions",
        "title": "Sessions",
        "summary": "Create separate conversations with separate local memory chains.",
        "details": (
            "Each session stores its Timechain in a separate workspace under the PoC sessions folder.\n"
            "Switching sessions reloads chat history, recall, self-model, and verification state.\n"
            "Reset Chain Memory clears only the active session.\n"
            "Personas and OpenRouter settings remain shared across sessions."
        ),
        "sources": ["Guide: Sessions", "README.md"],
    },
    {
        "id": "reset-chain-memory",
        "title": "Reset Chain Memory",
        "summary": "Clear local demo memory and start again with a fresh genesis ring.",
        "details": (
            "The reset button deletes the active PoC workspace .timechain directory and immediately creates a new chain.\n"
            "Use it before sharing the demo with someone else.\n"
            "It does not delete .env.local or saved custom personas.\n"
            "After reset, recall history is empty except for the new genesis state."
        ),
        "sources": ["Guide: Reset Chain Memory", "README.md"],
    },
    {
        "id": "cyphertempre",
        "title": "CypherTempre Timechain",
        "summary": "The local append-only memory chain that powers this PoC.",
        "details": (
            "The PoC uses timechain.py to keep local memory with confidence tracking, recall, covenant checks, and chain verification.\n"
            "Accepted interactions become hash-linked rings.\n"
            "The system can reconstruct visible chat history from sealed rings.\n"
            "CypherTempre-related explanations may use app-local SKILLS documentation excerpts."
        ),
        "sources": ["Guide: CypherTempre Timechain", "README.md", "SKILLS/README.md"],
    },
]

GUIDE_EXPLAINER_PERSONA: dict[str, str] = {
    "name": "Guide Explainer",
    "domain": "architecture",
    "system": (
        "You are Guide Explainer, a careful source-grounded assistant for the CypherTempre chat PoC. "
        "Explain only from the provided source excerpts. Distinguish documented fact from interpretation. "
        "If the answer is not covered in the provided sources, say 'not covered in the provided sources'. "
        "Avoid speculation, assumptions, product promises, and external knowledge."
    ),
}


HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CypherTempre</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #0b0c0b;
      --surface: #151514;
      --surface-2: #1d1d1b;
      --surface-3: #262520;
      --line: #3a3932;
      --line-soft: #292821;
      --text: #f5f0e6;
      --muted: #aaa397;
      --faint: #7e776d;
      --green: #67d89b;
      --blue: #8fb3ff;
      --amber: #d6b36a;
      --red: #ff8686;
      --shadow: rgba(0, 0, 0, 0.35);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      height: 100%;
      overflow: hidden;
      min-height: 100vh;
      background:
        linear-gradient(135deg, rgba(214, 179, 106, 0.08), transparent 36%),
        radial-gradient(circle at 88% 10%, rgba(103, 216, 155, 0.10), transparent 24%),
        var(--bg);
      color: var(--text);
      font: 14px/1.45 Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    button, input, textarea, select { font: inherit; }

    html {
      height: 100%;
    }

    .app {
      display: grid;
      grid-template-columns: 286px minmax(0, 1fr) 360px;
      height: 100vh;
      height: 100dvh;
      min-height: 0;
      overflow: hidden;
    }

    .rail, .inspector {
      background: rgba(17, 17, 15, 0.95);
      border-color: var(--line);
      height: 100vh;
      height: 100dvh;
      min-height: 0;
      overflow: hidden;
    }

    .rail {
      border-right: 1px solid var(--line);
      display: grid;
      grid-template-rows: auto minmax(0, 1fr) auto;
    }

    .brand {
      padding: 22px 18px;
      border-bottom: 1px solid var(--line-soft);
      background: linear-gradient(180deg, rgba(214, 179, 106, 0.08), transparent);
    }

    .brand-row {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 10px;
    }

    .brand h1 {
      margin: 0;
      font-size: 24px;
      letter-spacing: 0;
      line-height: 1.1;
      font-weight: 750;
    }

    .brand p {
      margin: 8px 0 0;
      color: var(--muted);
      font-size: 13px;
    }

    .settings-icon {
      width: 34px;
      height: 34px;
      display: grid;
      place-items: center;
      flex: 0 0 auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #121311;
      color: var(--muted);
      cursor: pointer;
    }

    .settings-icon:hover,
    .settings-icon.active {
      color: var(--text);
      border-color: #a88b4d;
      background: var(--surface-2);
    }

    .rail-section {
      padding: 12px;
      display: grid;
      gap: 10px;
      align-content: start;
      overflow: hidden;
    }

    .group {
      display: grid;
      gap: 6px;
    }

    .nav {
      display: grid;
      grid-template-columns: 1fr;
      gap: 8px;
    }

    .nav button {
      min-height: 38px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #121311;
      color: var(--muted);
      cursor: pointer;
      font-weight: 700;
    }

    .nav button.active {
      color: #15110a;
      border-color: #a88b4d;
      background: linear-gradient(180deg, #e5c57c, #c9a45b);
    }

    label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }

    input, select, textarea {
      width: 100%;
      color: var(--text);
      background: #121311;
      border: 1px solid var(--line);
      border-radius: 8px;
      outline: none;
    }

    input, select {
      height: 36px;
      padding: 0 10px;
    }

    textarea {
      resize: vertical;
      min-height: 50px;
      max-height: 120px;
      padding: 11px 12px;
    }

    input:focus, select:focus, textarea:focus {
      border-color: #4f8d6b;
      box-shadow: 0 0 0 3px rgba(103, 216, 155, 0.11);
    }

    .hint {
      color: var(--faint);
      font-size: 11px;
    }

    .status-card {
      margin: 10px 12px 12px;
      padding: 11px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: linear-gradient(180deg, #151513, #10110f);
      color: var(--muted);
      font-size: 13px;
    }

    .inline-field {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 8px;
    }

    .inline-field button {
      min-width: 58px;
      min-height: 36px;
    }

    .chat {
      display: grid;
      grid-template-rows: auto minmax(0, 1fr) auto;
      min-width: 0;
      height: 100vh;
      height: 100dvh;
      min-height: 0;
      overflow: hidden;
    }

    .chat.hidden {
      display: none;
    }

    .guide {
      display: none;
      min-width: 0;
      min-height: 100vh;
      overflow: auto;
      padding: 30px;
    }

    .guide.active {
      display: block;
    }

    .settings {
      display: none;
      min-width: 0;
      height: 100vh;
      height: 100dvh;
      overflow: auto;
      padding: 30px;
    }

    .settings.active {
      display: block;
    }

    .guide-shell {
      max-width: 1180px;
      margin: 0 auto;
      display: grid;
      gap: 18px;
    }

    .guide-hero {
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 24px;
      background: linear-gradient(135deg, rgba(214, 179, 106, 0.10), rgba(18, 18, 16, 0.96) 44%, rgba(103, 216, 155, 0.08));
      box-shadow: 0 18px 44px rgba(0, 0, 0, 0.24);
    }

    .guide-hero h2 {
      margin: 0;
      font-size: 30px;
      letter-spacing: 0;
    }

    .guide-hero p {
      max-width: 760px;
      margin: 10px 0 0;
      color: var(--muted);
      font-size: 15px;
    }

    .guide-controls {
      display: inline-flex;
      gap: 8px;
      padding: 5px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #10110f;
    }

    .guide-controls button {
      border: 0;
      border-radius: 999px;
      min-height: 34px;
      padding: 0 14px;
      color: var(--muted);
      background: transparent;
      cursor: pointer;
      font-weight: 800;
    }

    .guide-controls button.active {
      color: #15110a;
      background: linear-gradient(180deg, #e5c57c, #c9a45b);
    }

    .feature-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }

    .feature-card {
      border: 1px solid var(--line);
      border-radius: 10px;
      background: linear-gradient(180deg, rgba(24, 24, 22, 0.98), rgba(18, 18, 16, 0.98));
      padding: 16px;
    }

    .feature-card h3 {
      margin: 0 0 8px;
      font-size: 16px;
      letter-spacing: 0;
    }

    .feature-card p {
      margin: 0;
      color: var(--muted);
    }

    .feature-card ul {
      margin: 10px 0 0;
      padding-left: 18px;
      color: var(--muted);
    }

    .feature-card li + li {
      margin-top: 6px;
    }

    .feature-actions {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 12px;
    }

    .project-attribution {
      margin-top: 14px;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: rgba(16, 16, 14, 0.92);
      padding: 16px;
      color: var(--muted);
    }

    .project-attribution h3 {
      margin: 0 0 8px;
      color: var(--text);
      font-size: 16px;
      letter-spacing: 0;
    }

    .project-attribution p {
      margin: 0;
    }

    .project-attribution p + p {
      margin-top: 10px;
    }

    .project-attribution a {
      color: var(--amber);
      font-weight: 800;
      text-decoration: none;
    }

    .project-attribution a:hover {
      text-decoration: underline;
    }

    .simple-only.hidden, .comprehensive-only.hidden {
      display: none;
    }

    .chat-top {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
      padding: 16px 22px;
      border-bottom: 1px solid var(--line);
      background: rgba(12, 12, 11, 0.82);
      backdrop-filter: blur(12px);
    }

    .chat-title {
      min-width: 0;
    }

    .chat-title strong {
      display: block;
      font-size: 16px;
    }

    .chat-title span {
      display: block;
      color: var(--muted);
      font-size: 13px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .badges {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }

    .badge {
      border: 1px solid var(--line);
      background: var(--surface);
      color: var(--muted);
      border-radius: 999px;
      padding: 5px 9px;
      font-size: 12px;
      white-space: nowrap;
    }

    .badge.ok { color: var(--green); border-color: #35674f; }
    .badge.warn { color: var(--amber); border-color: #6b5730; }
    .badge.info { color: var(--blue); border-color: #3b4d76; }
    .badge.bad { color: var(--red); border-color: #6b3c3c; }

    .messages {
      overflow: auto;
      min-height: 0;
      padding: 22px;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }

    .empty {
      margin: auto;
      width: min(640px, 100%);
      color: var(--muted);
      text-align: center;
      display: grid;
      gap: 12px;
    }

    .empty h2 {
      margin: 0;
      color: var(--text);
      font-size: 28px;
      letter-spacing: 0;
    }

    .empty p { margin: 0; }

    .message {
      display: grid;
      grid-template-columns: 38px minmax(0, 1fr);
      gap: 12px;
      max-width: 980px;
      width: 100%;
    }

    .message.user {
      align-self: flex-end;
      grid-template-columns: minmax(0, 1fr) 38px;
    }

    .avatar {
      width: 38px;
      height: 38px;
      display: grid;
      place-items: center;
      border-radius: 8px;
      border: 1px solid var(--line);
      background: var(--surface-2);
      color: var(--green);
      font-weight: 800;
    }

    .message.user .avatar {
      grid-column: 2;
      color: var(--blue);
    }

    .bubble {
      min-width: 0;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: linear-gradient(180deg, rgba(24, 24, 22, 0.98), rgba(17, 18, 16, 0.98));
      box-shadow: 0 18px 44px rgba(0, 0, 0, 0.28);
      overflow: hidden;
    }

    .message.user .bubble {
      grid-column: 1;
      grid-row: 1;
      background: linear-gradient(180deg, #17231d, #111a16);
      border-color: #315843;
    }

    .message.rejected .bubble {
      background: #211615;
      border-color: #6a3939;
    }

    .bubble-head {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      padding: 9px 12px;
      border-bottom: 1px solid var(--line-soft);
      color: var(--muted);
      font-size: 12px;
      background: rgba(255, 255, 255, 0.015);
    }

    .bubble-content {
      padding: 13px 14px;
      overflow-wrap: anywhere;
      font-size: 15px;
      line-height: 1.55;
      white-space: pre-wrap;
    }

    .text-segment {
      display: inline;
    }

    .thought-segment {
      display: inline;
      color: #cdbf9f;
      font-style: italic;
      opacity: 0.88;
    }

    .bubble-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 7px;
      padding: 0 12px 12px;
    }

    .composer {
      padding: 16px 22px 20px;
      border-top: 1px solid var(--line);
      background: rgba(11, 12, 11, 0.92);
    }

    .composer-form {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      max-width: 1020px;
      margin: 0 auto;
    }

    .send {
      width: 46px;
      min-height: 46px;
      border-radius: 8px;
      border: 1px solid #a88b4d;
      color: #15110a;
      background: linear-gradient(180deg, #e5c57c, #c9a45b);
      cursor: pointer;
      font-size: 18px;
      font-weight: 900;
    }

    .send:disabled {
      opacity: 0.55;
      cursor: not-allowed;
    }

    .inspector {
      border-left: 1px solid var(--line);
      display: grid;
      grid-template-rows: auto minmax(0, 1fr);
    }

    .inspector-head {
      padding: 16px;
      border-bottom: 1px solid var(--line-soft);
    }

    .inspector-head strong {
      display: block;
      font-size: 15px;
    }

    .inspector-head span {
      display: block;
      margin-top: 4px;
      color: var(--muted);
      font-size: 13px;
    }

    .inspector-body {
      overflow: hidden;
      padding: 14px;
      display: grid;
      gap: 14px;
      align-content: start;
    }

    .panel {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: linear-gradient(180deg, rgba(24, 24, 22, 0.98), rgba(18, 18, 16, 0.98));
      padding: 12px;
    }

    .panel h2 {
      margin: 0 0 10px;
      color: var(--muted);
      font-size: 12px;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }

    dl {
      display: grid;
      grid-template-columns: 112px minmax(0, 1fr);
      gap: 7px 10px;
      margin: 0;
    }

    dt { color: var(--muted); }
    dd { margin: 0; overflow-wrap: anywhere; }

    .stack {
      display: grid;
      gap: 8px;
    }

    .secondary {
      min-height: 40px;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: var(--surface-2);
      color: var(--text);
      cursor: pointer;
      font-weight: 700;
    }

    .result {
      border-top: 1px solid var(--line-soft);
      padding-top: 10px;
      margin-top: 10px;
      color: var(--muted);
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      font-size: 13px;
    }

    @media (max-width: 1120px) {
      .app { grid-template-columns: 238px minmax(0, 1fr) 300px; }
      .inspector { border-left: 1px solid var(--line); border-top: 0; }
      .feature-grid { grid-template-columns: 1fr; }
    }

    @media (max-width: 760px) {
      .app { grid-template-columns: 74px minmax(0, 1fr); }
      .rail { border-right: 1px solid var(--line); border-bottom: 0; }
      .brand p, .brand h1, .rail-section .group, .rail > .status-card { display: none; }
      .brand { display: grid; place-items: center; padding: 10px; }
      .brand-row { display: block; }
      .rail-section { padding: 10px; }
      .nav { grid-template-columns: 1fr; }
      .nav button { min-height: 42px; padding: 0; }
      .inspector { display: none; }
      .guide { padding: 18px; }
      .chat-top { align-items: flex-start; flex-direction: column; }
      .badges { justify-content: flex-start; }
      .composer-form { grid-template-columns: 1fr; }
      .send { width: 100%; }
      .message, .message.user { grid-template-columns: 1fr; }
      .avatar { display: none; }
      .message.user .bubble { grid-column: auto; grid-row: auto; }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside class="rail">
      <div class="brand">
        <div class="brand-row">
          <h1>CypherTempre</h1>
          <button id="nav-settings" class="settings-icon" type="button" aria-label="Settings" title="Settings">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <circle cx="12" cy="12" r="3"></circle>
              <path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06A1.7 1.7 0 0 0 15 19.4a1.7 1.7 0 0 0-1 .6 1.7 1.7 0 0 0-.4 1.1V21a2 2 0 1 1-4 0v-.09A1.7 1.7 0 0 0 9 19.4a1.7 1.7 0 0 0-1.88.34l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-.6-1 1.7 1.7 0 0 0-1.1-.4H3a2 2 0 1 1 0-4h.09A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.34-1.88l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-.6 1.7 1.7 0 0 0 .4-1.1V3a2 2 0 1 1 4 0v.09A1.7 1.7 0 0 0 15 4.6a1.7 1.7 0 0 0 1.88-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.7 1.7 0 0 0 19.4 9c.22.38.58.6 1 .6h.6a2 2 0 1 1 0 4h-.6a1.7 1.7 0 0 0-1 .6 1.7 1.7 0 0 0 0 .8z"></path>
            </svg>
          </button>
        </div>
        <p>Local LLM chat with PoQ-gated memory.</p>
      </div>

      <div class="rail-section">
        <div class="nav" aria-label="Main view">
          <button id="nav-chat" class="active" type="button">Chat</button>
          <button id="nav-guide" type="button">Guide</button>
        </div>

        <div class="group">
          <label for="persona">Persona</label>
          <select id="persona"></select>
        </div>

        <div class="group">
          <label for="domain">Memory domain</label>
          <select id="domain">
            <option value="auto">auto</option>
            <option value="architecture">architecture</option>
            <option value="system-design">system-design</option>
            <option value="testing">testing</option>
            <option value="security">security</option>
            <option value="debugging">debugging</option>
            <option value="performance">performance</option>
            <option value="refactoring">refactoring</option>
            <option value="api-design">api-design</option>
          </select>
        </div>

        <div class="group">
          <label for="persona-seed">Persona Studio</label>
          <input id="persona-name" placeholder="Persona name">
          <textarea id="persona-seed" placeholder="Example: lighthouse archivist, warm dry wit, remembers details carefully"></textarea>
          <button id="generate-persona" class="secondary" type="button">Generate Persona</button>
          <div class="hint">Creates a fictional inspired persona. It does not claim to be a real person.</div>
        </div>

        <div class="group">
          <label for="session-list">Sessions</label>
          <select id="session-list"></select>
          <input id="session-name" placeholder="New session name">
          <button id="new-session" class="secondary" type="button">New Session</button>
          <div class="hint">Each session has its own local Timechain memory.</div>
        </div>
      </div>

      <div class="status-card" id="setup-status">Checking configuration...</div>
    </aside>

    <main id="chat-view" class="chat">
      <div class="chat-top">
        <div class="chat-title">
          <strong id="active-title">Companion</strong>
          <span id="workspace-line">Workspace loading...</span>
        </div>
        <div class="badges">
          <span class="badge info" id="model-badge">cognitivecomputations/dolphin-mistral-24b-venice-edition:free</span>
          <span class="badge" id="rings-badge">rings: -</span>
          <span class="badge" id="verify-badge">verify: -</span>
        </div>
      </div>

      <section id="messages" class="messages" aria-live="polite">
        <div class="empty" id="empty-state">
          <h2>Start a remembered conversation.</h2>
          <p>Responses come from OpenRouter, then CypherTempre scores them through PoQ before sealing accepted rings.</p>
        </div>
      </section>

      <div class="composer">
        <form id="composer-form" class="composer-form">
          <textarea id="message" placeholder="Ask anything..." required></textarea>
          <button id="send" class="send" type="submit" aria-label="Send">→</button>
        </form>
      </div>
    </main>

    <main id="guide-view" class="guide">
      <div class="guide-shell">
        <section class="guide-hero">
          <div class="guide-controls" aria-label="Explanation depth">
            <button id="guide-simple" class="active" type="button">Simple</button>
            <button id="guide-comprehensive" type="button">Comprehensive</button>
          </div>
          <h2>System Guide</h2>
          <p class="simple-only">A neat map of what each part of the CypherTempre chat interface does.</p>
          <p class="comprehensive-only hidden">This page explains the full local loop: persona selection, OpenRouter generation, Timechain recall, PoQ gating, memory sealing, visible conversation restoration, and chain verification.</p>
        </section>

        <section id="guide-topic-grid" class="feature-grid">
          <article class="feature-card">
            <h3>Chat</h3>
            <p class="simple-only">Send messages and receive assistant replies through the selected persona and model.</p>
            <div class="comprehensive-only hidden">
              <p>The chat composer sends your message, selected domain, persona, model, and optional browser API key to the local server.</p>
              <ul>
                <li>The server recalls relevant rings before the LLM call.</li>
                <li>The response is scored by PoQ before it is saved.</li>
                <li>Accepted replies appear with ring metadata.</li>
              </ul>
            </div>
          </article>

          <article class="feature-card">
            <h3>Personas</h3>
            <p class="simple-only">Change the assistant's style, or generate a fictional inspired persona in Persona Studio.</p>
            <div class="comprehensive-only hidden">
              <p>Personas provide the system prompt and default memory domain for the request. Custom personas are saved in the local PoC workspace and mirrored in your browser.</p>
              <ul>
                <li>Companion is general conversational help.</li>
                <li>Architect focuses on design tradeoffs.</li>
                <li>Socratic Tutor asks sharper learning questions.</li>
                <li>Memory Critic audits weak or contradictory memory.</li>
                <li>CypherTempre Researcher focuses on the PoC itself.</li>
                <li>Generated personas can be inspired by aesthetics or communication styles, but should remain fictional.</li>
              </ul>
            </div>
          </article>

          <article class="feature-card">
            <h3>OpenRouter Model</h3>
            <p class="simple-only">Choose which OpenRouter model answers the chat.</p>
            <div class="comprehensive-only hidden">
              <p>The model field defaults from `.env.local` or the server launch arguments.</p>
              <ul>
                <li>Your current persistent model is Venice Uncensored.</li>
                <li>If no key is available, the app falls back to the local deterministic generator.</li>
                <li>The response metadata shows which model path was used.</li>
              </ul>
            </div>
          </article>

          <article class="feature-card">
            <h3>API Key</h3>
            <p class="simple-only">Use `.env.local` for persistent local testing, or paste a key for the browser session.</p>
            <div class="comprehensive-only hidden">
              <p>The server loads `cyphertempre-chat-poc/.env.local` on startup.</p>
              <ul>
                <li>`OPENROUTER_API_KEY` enables real OpenRouter replies.</li>
                <li>`OPENROUTER_MODEL` sets the default model.</li>
                <li>The file is ignored by git so the key is not committed.</li>
              </ul>
            </div>
          </article>

          <article class="feature-card">
            <h3>Memory Domain</h3>
            <p class="simple-only">Leave this on auto unless you want to force a specific memory topic.</p>
            <div class="comprehensive-only hidden">
              <p>Domains influence recall and self-model coverage. Auto mode classifies the message from keywords and persona context.</p>
              <ul>
                <li>Each accepted ring stores its domain.</li>
                <li>Recall can filter by the active domain.</li>
                <li>The self-model shows top and untouched domains.</li>
              </ul>
            </div>
          </article>

          <article class="feature-card">
            <h3>PoQ Gate</h3>
            <p class="simple-only">The app only saves responses that pass quality and covenant checks.</p>
            <div class="comprehensive-only hidden">
              <p>Proof-of-Qualia scores coherence, relevance, novelty, consistency, depth, and covenant alignment.</p>
              <ul>
                <li>Accepted responses become hash-linked rings.</li>
                <li>Rejected responses are shown but not sealed.</li>
                <li>Brightness is computed, not manually assigned.</li>
              </ul>
            </div>
          </article>

          <article class="feature-card">
            <h3>Recall</h3>
            <p class="simple-only">Search prior accepted rings from the local Timechain.</p>
            <div class="comprehensive-only hidden">
              <p>Recall uses the same lightweight retrieval primitives as the Timechain CLI.</p>
              <ul>
                <li>Results include score, ring number, brightness, domain, and content.</li>
                <li>Recent relevant rings are injected into future LLM prompts.</li>
                <li>Recall reads from `.timechain/chain.jsonl`.</li>
              </ul>
            </div>
          </article>

          <article class="feature-card">
            <h3>Self Model</h3>
            <p class="simple-only">See the agent's current memory state at a glance.</p>
            <div class="comprehensive-only hidden">
              <p>The self model summarizes local Timechain state.</p>
              <ul>
                <li>Ring count shows accepted memory size.</li>
                <li>Temporal mass is accumulated brightness.</li>
                <li>Top domains show where the system has experience.</li>
              </ul>
            </div>
          </article>

          <article class="feature-card">
            <h3>Verify Chain</h3>
            <p class="simple-only">Check whether the hash-linked memory chain is intact.</p>
            <div class="comprehensive-only hidden">
              <p>Verification replays the chain hashes and confirms each ring points to the previous one.</p>
              <ul>
                <li>`ok` means no tampering was detected.</li>
                <li>The visible ring count includes genesis.</li>
                <li>Use this after experiments or manual file inspection.</li>
              </ul>
            </div>
          </article>

          <article class="feature-card">
            <h3>Persistence</h3>
            <p class="simple-only">Accepted memory survives browser reloads and server restarts.</p>
            <div class="comprehensive-only hidden">
              <p>Persistence comes from the local append-only Timechain files.</p>
              <ul>
                <li>Memory lives in `cyphertempre-chat-poc/.timechain/chain.jsonl`.</li>
                <li>The UI restores accepted exchanges from `/api/history`.</li>
                <li>Unsent drafts and rejected responses are not saved as rings.</li>
              </ul>
            </div>
          </article>

          <article class="feature-card">
            <h3>Sessions</h3>
            <p class="simple-only">Create separate conversations with separate local memory chains.</p>
            <div class="comprehensive-only hidden">
              <p>Each session stores its Timechain in a separate workspace under the PoC sessions folder.</p>
              <ul>
                <li>Switching sessions reloads chat history, recall, self-model, and verification state.</li>
                <li>Reset Chain Memory clears only the active session.</li>
                <li>Personas and OpenRouter settings remain shared across sessions.</li>
              </ul>
            </div>
          </article>

          <article class="feature-card">
            <h3>Reset Chain Memory</h3>
            <p class="simple-only">Clear local demo memory and start again with a fresh genesis ring.</p>
            <div class="comprehensive-only hidden">
              <p>The reset button deletes the PoC workspace `.timechain` directory and immediately creates a new chain.</p>
              <ul>
                <li>Use it before sharing the demo with someone else.</li>
                <li>It does not delete `.env.local` or saved custom personas.</li>
                <li>After reset, recall history is empty except for the new genesis state.</li>
              </ul>
            </div>
          </article>
        </section>

        <section class="project-attribution" aria-labelledby="project-attribution-title">
          <h3 id="project-attribution-title">Cypher Tempre Project</h3>
          <p>This demo is part of the Cypher Tempre cognitive architecture and is shared under the Cypher Tempre Open Intelligence License (CTOIL).</p>
          <p>Copyright (c) 2026 Michael Joseph, Contributor of Origin & Founder of CyberphysicsAI, Architect of Cypher Tempre. The Architecture is provided "as is", without warranty of any kind.</p>
          <p><a href="https://notebooklm.google.com/notebook/6486b26c-946a-4840-a5a7-368c3891a54c" target="_blank" rel="noopener noreferrer">Open the Cypher Tempre NotebookLM source notebook</a></p>
        </section>
      </div>
    </main>

    <main id="settings-view" class="settings">
      <div class="guide-shell">
        <section class="guide-hero">
          <h2>Settings</h2>
          <p>Configure OpenRouter access and the default model used by chat and source-grounded guide explanations.</p>
        </section>

        <section class="feature-card">
          <div class="group">
            <label for="api-key">OpenRouter API key</label>
            <div class="inline-field">
              <input id="api-key" type="password" autocomplete="off" placeholder="sk-or-...">
              <button id="test-openrouter" class="secondary" type="button">Test</button>
            </div>
            <div class="hint">Stored in this browser only. You can also set OPENROUTER_API_KEY in .env.local.</div>
          </div>

          <div class="group">
            <label for="model">Model</label>
            <input id="model" value="cognitivecomputations/dolphin-mistral-24b-venice-edition:free">
            <div class="hint">Recommended free default: Venice Uncensored.</div>
          </div>

          <div class="status-card" id="settings-status">Checking configuration...</div>
        </section>
      </div>
    </main>

    <aside class="inspector">
      <div class="inspector-head">
        <strong>Memory Inspector</strong>
        <span>Recall, verify, and inspect the local chain.</span>
      </div>
      <div class="inspector-body">
        <section class="panel">
          <h2>Self Model</h2>
          <dl id="summary"></dl>
        </section>

        <section class="panel">
          <h2>Recall</h2>
          <form id="recall-form" class="stack">
            <input id="recall-query" placeholder="Search prior rings" required>
            <button type="submit" class="secondary">Recall</button>
          </form>
          <div id="recall-results" class="result">No recall query yet.</div>
        </section>

        <section class="panel">
          <h2>Chain</h2>
          <div class="stack">
            <button id="verify" type="button" class="secondary">Verify Chain</button>
            <button id="reset-chain" type="button" class="secondary">Reset Chain Memory</button>
            <div id="verify-result" class="result">Not checked yet.</div>
          </div>
        </section>
      </div>
    </aside>
  </div>

  <script>
    const els = {
      apiKey: document.getElementById('api-key'),
      model: document.getElementById('model'),
      persona: document.getElementById('persona'),
      domain: document.getElementById('domain'),
      setup: document.getElementById('setup-status'),
      title: document.getElementById('active-title'),
      workspace: document.getElementById('workspace-line'),
      modelBadge: document.getElementById('model-badge'),
      ringsBadge: document.getElementById('rings-badge'),
      verifyBadge: document.getElementById('verify-badge'),
      messages: document.getElementById('messages'),
      empty: document.getElementById('empty-state'),
      form: document.getElementById('composer-form'),
      message: document.getElementById('message'),
      send: document.getElementById('send'),
      summary: document.getElementById('summary'),
      recallForm: document.getElementById('recall-form'),
      recallQuery: document.getElementById('recall-query'),
      recallResults: document.getElementById('recall-results'),
      verify: document.getElementById('verify'),
      verifyResult: document.getElementById('verify-result'),
      resetChain: document.getElementById('reset-chain'),
      navChat: document.getElementById('nav-chat'),
      navGuide: document.getElementById('nav-guide'),
      navSettings: document.getElementById('nav-settings'),
      chatView: document.getElementById('chat-view'),
      guideView: document.getElementById('guide-view'),
      settingsView: document.getElementById('settings-view'),
      settingsStatus: document.getElementById('settings-status'),
      guideTopicGrid: document.getElementById('guide-topic-grid'),
      guideSimple: document.getElementById('guide-simple'),
      guideComprehensive: document.getElementById('guide-comprehensive'),
      personaName: document.getElementById('persona-name'),
      personaSeed: document.getElementById('persona-seed'),
      generatePersona: document.getElementById('generate-persona'),
      testOpenRouter: document.getElementById('test-openrouter'),
      sessionList: document.getElementById('session-list'),
      sessionName: document.getElementById('session-name'),
      newSession: document.getElementById('new-session')
    };

    let personas = {};
    let customPersonas = {};
    let activeSession = localStorage.getItem('ct_active_session') || 'default';

    function esc(value) {
      return String(value ?? '').replace(/[&<>"']/g, ch => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
      }[ch]));
    }

    function renderContent(content) {
      const text = String(content ?? '');
      const parts = [];
      const pattern = /\*([^*\n][\s\S]*?[^*\n]|\S)\*/g;
      let lastIndex = 0;
      let match;
      while ((match = pattern.exec(text)) !== null) {
        if (match.index > lastIndex) {
          parts.push({ type: 'text', value: text.slice(lastIndex, match.index) });
        }
        parts.push({ type: 'thought', value: match[1] });
        lastIndex = pattern.lastIndex;
      }
      if (lastIndex < text.length) {
        parts.push({ type: 'text', value: text.slice(lastIndex) });
      }
      if (!parts.length) parts.push({ type: 'text', value: text });
      return parts
        .filter(part => part.value.length > 0)
        .map(part => `<span class="${part.type === 'thought' ? 'thought-segment' : 'text-segment'}">${esc(part.value)}</span>`)
        .join('');
    }

    function setMainView(view) {
      const guide = view === 'guide';
      const settings = view === 'settings';
      els.chatView.classList.toggle('hidden', guide || settings);
      els.guideView.classList.toggle('active', guide);
      els.settingsView.classList.toggle('active', settings);
      els.navChat.classList.toggle('active', !guide && !settings);
      els.navGuide.classList.toggle('active', guide);
      els.navSettings.classList.toggle('active', settings);
      localStorage.setItem('ct_view', view);
    }

    function setGuideDepth(depth) {
      const comprehensive = depth === 'comprehensive';
      document.querySelectorAll('.simple-only').forEach(node => node.classList.toggle('hidden', comprehensive));
      document.querySelectorAll('.comprehensive-only').forEach(node => node.classList.toggle('hidden', !comprehensive));
      els.guideSimple.classList.toggle('active', !comprehensive);
      els.guideComprehensive.classList.toggle('active', comprehensive);
      localStorage.setItem('ct_guide_depth', depth);
    }

    function renderGuideTopics(topics) {
      els.guideTopicGrid.innerHTML = topics.map(topic => {
        const detailItems = String(topic.details || '')
          .split('\n')
          .map(line => line.trim())
          .filter(Boolean)
          .map(line => `<li>${esc(line)}</li>`)
          .join('');
        const sourceText = (topic.sources || []).join(', ');
        return `
          <article class="feature-card">
            <h3>${esc(topic.title)}</h3>
            <p class="simple-only">${esc(topic.summary)}</p>
            <div class="comprehensive-only hidden">
              <ul>${detailItems}</ul>
              <p class="hint">Sources: ${esc(sourceText)}</p>
            </div>
            <div class="feature-actions">
              <button class="secondary explain-guide-topic" type="button" data-topic-id="${esc(topic.id)}">Explain</button>
            </div>
          </article>
        `;
      }).join('');
      els.guideTopicGrid.querySelectorAll('.explain-guide-topic').forEach(button => {
        button.addEventListener('click', () => {
          explainGuideTopic(button.dataset.topicId).catch(error => setStatus(error.message, '#6b3c3c'));
        });
      });
      setGuideDepth(localStorage.getItem('ct_guide_depth') || 'simple');
    }

    async function loadGuideTopics() {
      const data = await api('/api/guide/topics');
      renderGuideTopics(data.topics || []);
    }

    async function explainGuideTopic(topicId) {
      saveLocalConfig();
      setStatus('Creating source-grounded guide explanation...');
      const data = await api('/api/guide/explain', {
        method: 'POST',
        body: JSON.stringify({
          topicId,
          model: els.model.value.trim(),
          apiKey: els.apiKey.value.trim()
        })
      });
      if (data.session?.id) {
        await switchSession(data.session.id);
      }
      setMainView('chat');
      setStatus(data.openrouter_error ? `Guide explanation used local fallback: ${data.openrouter_error}` : `Guide explanation created: ${data.topic?.title || topicId}.`, data.openrouter_error ? '#6b5730' : '#35674f');
    }

    async function api(path, options = {}) {
      const response = await fetch(path, {
        ...options,
        headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok || body.ok === false) throw new Error(body.error || `HTTP ${response.status}`);
      return body;
    }

    function sessionQuery() {
      return `?session=${encodeURIComponent(activeSession)}`;
    }

    async function loadSessions() {
      const data = await api('/api/sessions');
      if (!data.sessions.some(session => session.id === activeSession)) {
        activeSession = data.active || 'default';
        localStorage.setItem('ct_active_session', activeSession);
      }
      els.sessionList.innerHTML = data.sessions
        .map(session => `<option value="${esc(session.id)}">${esc(session.name)} (${session.rings})</option>`)
        .join('');
      els.sessionList.value = activeSession;
    }

    async function switchSession(sessionId) {
      activeSession = sessionId || 'default';
      localStorage.setItem('ct_active_session', activeSession);
      await Promise.all([refreshSummary(), verifyChain(), restoreHistory()]);
      await loadSessions();
    }

    async function createSession() {
      const name = els.sessionName.value.trim() || 'New conversation';
      const data = await api('/api/sessions', {
        method: 'POST',
        body: JSON.stringify({ name })
      });
      els.sessionName.value = '';
      await switchSession(data.session.id);
    }

    function saveLocalConfig() {
      localStorage.setItem('ct_model', els.model.value.trim());
      localStorage.setItem('ct_persona', els.persona.value);
      localStorage.setItem('ct_domain', els.domain.value);
      if (els.apiKey.value.trim()) {
        localStorage.setItem('ct_openrouter_key', els.apiKey.value.trim());
      } else {
        localStorage.removeItem('ct_openrouter_key');
      }
    }

    function loadCustomPersonas() {
      try {
        return JSON.parse(localStorage.getItem('ct_custom_personas') || '{}') || {};
      } catch {
        return {};
      }
    }

    function saveCustomPersonas() {
      localStorage.setItem('ct_custom_personas', JSON.stringify(customPersonas));
    }

    function renderPersonaOptions() {
      const builtIns = Object.entries(personas)
        .map(([id, persona]) => `<option value="${esc(id)}">${esc(persona.name)}</option>`)
        .join('');
      const custom = Object.entries(customPersonas)
        .map(([id, persona]) => `<option value="${esc(id)}">${esc(persona.name)} · custom</option>`)
        .join('');
      els.persona.innerHTML = builtIns + custom;
    }

    function getActivePersona() {
      return customPersonas[els.persona.value] || personas[els.persona.value] || personas.companion;
    }

    function applyLocalConfig(config) {
      personas = config.personas || {};
      customPersonas = loadCustomPersonas();
      customPersonas = { ...(config.custom_personas || {}), ...customPersonas };
      saveCustomPersonas();
      renderPersonaOptions();
      els.model.value = localStorage.getItem('ct_model') || config.default_model || 'cognitivecomputations/dolphin-mistral-24b-venice-edition:free';
      els.apiKey.value = localStorage.getItem('ct_openrouter_key') || '';
      els.persona.value = localStorage.getItem('ct_persona') || 'companion';
      if (!personas[els.persona.value] && !customPersonas[els.persona.value]) els.persona.value = 'companion';
      els.domain.value = localStorage.getItem('ct_domain') || 'auto';
      updatePersonaText();
      updateSetup(config.has_env_key);
    }

    async function syncCustomPersonasToServer(config) {
      const serverPersonas = config.custom_personas || {};
      const missingOnServer = Object.entries(customPersonas)
        .filter(([id]) => !serverPersonas[id]);
      await Promise.all(missingOnServer.map(([id, persona]) => api('/api/personas', {
        method: 'POST',
        body: JSON.stringify({ id, persona })
      }).catch(() => null)));
    }

    function setStatus(text, borderColor = '') {
      els.setup.textContent = text;
      els.settingsStatus.textContent = text;
      if (borderColor) {
        els.setup.style.borderColor = borderColor;
        els.settingsStatus.style.borderColor = borderColor;
      }
    }

    function updateSetup(hasEnvKey = false) {
      const hasBrowserKey = Boolean(els.apiKey.value.trim());
      const configured = hasEnvKey || hasBrowserKey;
      const text = configured
        ? `OpenRouter ready. Using ${els.model.value.trim() || 'cognitivecomputations/dolphin-mistral-24b-venice-edition:free'}.`
        : 'Add an OpenRouter key or set OPENROUTER_API_KEY to get real LLM responses.';
      setStatus(text, configured ? '#35674f' : '#6b5730');
      els.modelBadge.textContent = els.model.value.trim() || 'cognitivecomputations/dolphin-mistral-24b-venice-edition:free';
    }

    async function testOpenRouter() {
      saveLocalConfig();
      setStatus('Testing OpenRouter...');
      els.testOpenRouter.disabled = true;
      try {
        const data = await api('/api/openrouter-test', {
          method: 'POST',
          body: JSON.stringify({
            model: els.model.value.trim(),
            apiKey: els.apiKey.value.trim()
          })
        });
        setStatus(`OpenRouter OK: ${data.model_used || data.model}.`, '#35674f');
      } catch (error) {
        setStatus(error.message, '#6b3c3c');
      } finally {
        els.testOpenRouter.disabled = false;
      }
    }

    function updatePersonaText() {
      const persona = getActivePersona();
      els.title.textContent = persona?.name || 'Companion';
      if (!els.domain.value || els.domain.value !== 'auto') return;
    }

    function generatePersonaFromSeed(name, seed) {
      const personaName = name.trim();
      if (!personaName) throw new Error('Persona name is required.');
      const duplicate = Object.values({ ...personas, ...customPersonas })
        .some(persona => persona.name.toLowerCase() === personaName.toLowerCase());
      if (duplicate) throw new Error(`Persona name already exists: ${personaName}`);
      const style = seed || 'warm, practical, observant conversational partner';
      const system = [
        `You are ${personaName}, a fictional AI persona inspired by this vibe: ${style}.`,
        'Do not claim to be, impersonate, or have a personal relationship with any real public figure.',
        'Communicate in clear English with a calm, observant, slightly literary voice.',
        'Keep replies elegant, grounded, emotionally intelligent, and conversational.',
        'Be helpful and specific. Remember useful user preferences through the CypherTempre memory flow.',
      ].join(' ');
      return {
        name: personaName,
        domain: 'auto',
        seed: style,
        system,
      };
    }

    async function createPersona() {
      try {
        const seed = els.personaSeed.value.trim();
        const persona = generatePersonaFromSeed(els.personaName.value, seed);
        const id = `custom_${Date.now()}`;
        await api('/api/personas', {
          method: 'POST',
          body: JSON.stringify({ id, persona })
        });
        customPersonas[id] = persona;
        saveCustomPersonas();
        renderPersonaOptions();
        els.persona.value = id;
        els.domain.value = 'auto';
        saveLocalConfig();
        updatePersonaText();
        els.setup.textContent = `Created persona: ${persona.name}.`;
      } catch (error) {
        els.setup.textContent = error.message;
      }
    }

    function appendMessage(role, content, meta = {}, rejected = false) {
      els.empty?.remove();
      const wrapper = document.createElement('article');
      wrapper.className = `message ${role === 'You' ? 'user' : 'assistant'}${rejected ? ' rejected' : ''}`;
      const avatar = role === 'You' ? 'Y' : 'C';
      const metaHtml = Object.entries(meta)
        .filter(([, value]) => value !== undefined && value !== null && value !== '')
        .map(([key, value]) => `<span class="badge ${key === 'accepted' ? (value ? 'ok' : 'bad') : 'info'}">${esc(key)}: ${esc(value)}</span>`)
        .join('');
      wrapper.innerHTML = `
        <div class="avatar">${esc(avatar)}</div>
        <div class="bubble">
          <div class="bubble-head"><span>${esc(role)}</span><span>${new Date().toLocaleTimeString()}</span></div>
          <div class="bubble-content">${renderContent(content)}</div>
          ${metaHtml ? `<div class="bubble-meta">${metaHtml}</div>` : ''}
        </div>
      `;
      els.messages.appendChild(wrapper);
      els.messages.scrollTop = els.messages.scrollHeight;
    }

    function clearRenderedMessages() {
      els.messages.querySelectorAll('.message').forEach(node => node.remove());
    }

    async function restoreHistory() {
      const data = await api(`/api/history${sessionQuery()}`);
      clearRenderedMessages();
      if (!data.history.length) return;
      els.empty?.remove();
      data.history.forEach(item => {
        if (item.role === 'user') {
          appendMessage('You', item.content, { domain: item.domain, ring: item.ring });
        } else {
          appendMessage('CypherTempre', item.content, {
            accepted: true,
            ring: item.ring,
            brightness: item.brightness,
            epistemic: item.epistemic,
            hash: item.hash_prefix
          });
        }
      });
      els.setup.textContent = `Restored ${Math.floor(data.history.length / 2)} remembered exchanges.`;
    }

    function renderSummary(model) {
      els.workspace.textContent = `Workspace: ${model.workspace || '(local)'}`;
      els.ringsBadge.textContent = `rings: ${model.ring_count}`;
      const facts = model.memory_facts || [];
      const factSummary = facts.length
        ? facts.slice(0, 6).map(fact => `${fact.key}=${fact.value} (#${fact.source_ring})`).join('\n')
        : '(none)';
      const rows = {
        agent: model.name,
        rings: model.ring_count,
        mass: model.temporal_mass,
        frozen: model.frozen,
        facts: model.memory_fact_count || 0,
        domains: (model.top_domains || []).join(', ') || '(none)',
        genesis: String(model.genesis_hash || '').slice(0, 16),
        memory: factSummary
      };
      els.summary.innerHTML = Object.entries(rows)
        .map(([key, value]) => `<dt>${esc(key)}</dt><dd>${esc(value)}</dd>`)
        .join('');
    }

    async function refreshSummary() {
      const data = await api(`/api/self-model${sessionQuery()}`);
      renderSummary(data.model);
    }

    async function verifyChain() {
      const data = await api(`/api/verify${sessionQuery()}`);
      els.verifyResult.textContent = `${data.ok ? 'OK' : 'FAILED'}: ${data.status} | rings=${data.rings}`;
      els.verifyBadge.textContent = data.ok ? 'verify: ok' : 'verify: failed';
      els.verifyBadge.className = `badge ${data.ok ? 'ok' : 'bad'}`;
    }

    async function resetChainMemory() {
      els.verifyResult.textContent = 'Resetting chain memory...';
      const data = await api(`/api/reset${sessionQuery()}`, { method: 'POST', body: JSON.stringify({}) });
      clearRenderedMessages();
      if (!document.getElementById('empty-state')) {
        els.messages.innerHTML = `
          <div class="empty" id="empty-state">
            <h2>Start a remembered conversation.</h2>
            <p>Responses come from OpenRouter, then CypherTempre scores them through PoQ before sealing accepted rings.</p>
          </div>
        `;
        els.empty = document.getElementById('empty-state');
      }
      els.recallResults.textContent = 'Memory reset. No recall query yet.';
      els.verifyResult.textContent = `Reset complete. New genesis chain created. rings=${data.rings}`;
      await refreshSummary();
      await verifyChain();
    }

    els.form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const message = els.message.value.trim();
      if (!message) return;

      saveLocalConfig();
      appendMessage('You', message, { domain: els.domain.value });
      els.message.value = '';
      els.send.disabled = true;

      try {
        const data = await api('/api/chat', {
          method: 'POST',
          body: JSON.stringify({
            message,
            session: activeSession,
            domain: els.domain.value,
            persona: els.persona.value,
            customPersona: customPersonas[els.persona.value] || null,
            model: els.model.value.trim() || 'cognitivecomputations/dolphin-mistral-24b-venice-edition:free',
            apiKey: els.apiKey.value.trim()
          })
        });
        if (data.accepted) {
          appendMessage(data.persona_name || 'CypherTempre', data.content, {
            accepted: true,
            ring: data.ring,
            brightness: data.brightness,
            epistemic: data.epistemic,
            model: data.model_used || data.model,
            openrouter: data.openrouter_error ? 'fallback' : '',
            error: data.openrouter_error || '',
            domain: data.domain,
            retry: data.retry?.attempted ? 'yes' : '',
            memory: (data.memory_hits || []).length || ''
          });
        } else {
          appendMessage(data.persona_name || 'CypherTempre', data.reason || 'Rejected by PoQ gate.', {
            accepted: false,
            brightness: data.brightness,
            openrouter: data.openrouter_error ? 'fallback' : '',
            error: data.openrouter_error || ''
          }, true);
        }
        await refreshSummary();
        await verifyChain();
      } catch (error) {
        appendMessage('CypherTempre', error.message, { accepted: false }, true);
      } finally {
        els.send.disabled = false;
        els.message.focus();
      }
    });

    els.recallForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const query = els.recallQuery.value.trim();
      if (!query) return;
      els.recallResults.textContent = 'Searching...';
      try {
        const data = await api('/api/recall', {
          method: 'POST',
          body: JSON.stringify({ query, session: activeSession, domain: els.domain.value === 'auto' ? '' : els.domain.value, limit: 6 })
        });
        const factText = data.facts?.length
          ? data.facts.map(f => `fact ${f.key}=${f.value} confidence=${f.confidence} source=#${f.source_ring} score=${f.score}`).join('\n')
          : 'No durable fact hits.';
        const ringText = data.rings?.length
          ? data.rings.map(r => `#${r.n} score=${r.score} brightness=${r.brightness} ${r.domain}\n${r.content}`).join('\n\n')
          : 'No matching rings.';
        const diagnostics = data.diagnostics?.length ? data.diagnostics.join(' | ') : 'No diagnostics.';
        els.recallResults.textContent = `Durable facts\n${factText}\n\nRings\n${ringText}\n\nDiagnostics\n${diagnostics}`;
      } catch (error) {
        els.recallResults.textContent = error.message;
      }
    });

    els.verify.addEventListener('click', () => {
      els.verifyResult.textContent = 'Checking...';
      verifyChain().catch(error => { els.verifyResult.textContent = error.message; });
    });
    els.resetChain.addEventListener('click', () => {
      resetChainMemory().catch(error => { els.verifyResult.textContent = error.message; });
    });

    els.persona.addEventListener('change', () => { updatePersonaText(); saveLocalConfig(); });
    els.model.addEventListener('input', () => { updateSetup(); saveLocalConfig(); });
    els.apiKey.addEventListener('input', () => { updateSetup(); saveLocalConfig(); });
    els.testOpenRouter.addEventListener('click', () => {
      testOpenRouter().catch(error => { setStatus(error.message, '#6b3c3c'); });
    });
    els.domain.addEventListener('change', saveLocalConfig);
    els.navChat.addEventListener('click', () => setMainView('chat'));
    els.navGuide.addEventListener('click', () => setMainView('guide'));
    els.navSettings.addEventListener('click', () => setMainView('settings'));
    els.guideSimple.addEventListener('click', () => setGuideDepth('simple'));
    els.guideComprehensive.addEventListener('click', () => setGuideDepth('comprehensive'));
    els.generatePersona.addEventListener('click', () => {
      createPersona().catch(error => { els.setup.textContent = error.message; });
    });
    els.sessionList.addEventListener('change', () => {
      switchSession(els.sessionList.value).catch(error => { els.setup.textContent = error.message; });
    });
    els.newSession.addEventListener('click', () => {
      createSession().catch(error => { els.setup.textContent = error.message; });
    });
    els.sessionName.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') {
        event.preventDefault();
        createSession().catch(error => { els.setup.textContent = error.message; });
      }
    });
    els.message.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        els.form.requestSubmit();
      }
    });

    api('/api/config')
      .then(config => {
        applyLocalConfig(config);
        return syncCustomPersonasToServer(config).then(() => {
          setMainView(localStorage.getItem('ct_view') || 'chat');
          return loadGuideTopics().then(() => loadSessions().then(() => Promise.all([refreshSummary(), verifyChain(), restoreHistory()])));
        });
      })
      .catch(error => {
        setStatus(error.message, '#6b3c3c');
        appendMessage('CypherTempre', error.message, { accepted: false }, true);
      });
  </script>
</body>
</html>
"""


def resolve_timechain_path(path: pathlib.Path) -> pathlib.Path:
    candidates = [
        path,
        pathlib.Path(os.environ.get("TIMECHAIN_PATH", "")) if os.environ.get("TIMECHAIN_PATH") else None,
        pathlib.Path(__file__).resolve().parent / "timechain.py",
    ]
    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate.resolve()
    raise FileNotFoundError(
        "timechain.py not found. Copy it into cyphertempre-chat-poc/timechain.py "
        "or pass --timechain-path /path/to/timechain.py."
    )


def load_timechain_module(path: pathlib.Path) -> Any:
    path = resolve_timechain_path(path)
    spec = importlib.util.spec_from_file_location("cyphertempre_timechain", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not import Timechain script: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def empty_memory_model() -> dict[str, Any]:
    return {"version": 1, "facts": []}


def memory_model_path(workspace: pathlib.Path) -> pathlib.Path:
    return workspace / ".timechain" / "memory_model.json"


def load_memory_model(workspace: pathlib.Path) -> dict[str, Any]:
    path = memory_model_path(workspace)
    if not path.exists():
        return empty_memory_model()
    try:
        model = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return empty_memory_model()
    if not isinstance(model, dict) or not isinstance(model.get("facts"), list):
        return empty_memory_model()
    model.setdefault("version", 1)
    return model


def save_memory_model(workspace: pathlib.Path, model: dict[str, Any]) -> None:
    path = memory_model_path(workspace)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")


def custom_personas_path(workspace: pathlib.Path) -> pathlib.Path:
    return workspace / ".timechain" / "custom_personas.json"


def load_custom_personas(workspace: pathlib.Path) -> dict[str, dict[str, str]]:
    path = custom_personas_path(workspace)
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(raw, dict):
        return {}
    personas: dict[str, dict[str, str]] = {}
    for key, value in raw.items():
        persona_id = sanitize_session_id(str(key))
        if not persona_id:
            continue
        persona = normalize_custom_persona(value)
        if persona:
            personas[persona_id] = persona
    return personas


def save_custom_personas(workspace: pathlib.Path, personas: dict[str, dict[str, str]]) -> None:
    path = custom_personas_path(workspace)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(personas, ensure_ascii=False, indent=2), encoding="utf-8")


def _clean_fact_value(value: str, *, max_words: int = 12) -> str:
    cleaned = re.sub(r"\s+", " ", value or "").strip(" .,!?:;\"'")
    words = cleaned.split()
    return " ".join(words[:max_words]).strip(" .,!?:;\"'")


def _name_value(value: str) -> str:
    cleaned = _clean_fact_value(value, max_words=3)
    cleaned = re.split(r"\b(?:nice to meet|glad to meet|and i|but i|because|from)\b", cleaned, flags=re.I)[0]
    return _clean_fact_value(cleaned, max_words=3)


def _looks_like_name(value: str, *, explicit: bool) -> bool:
    if not value:
        return False
    lowered = value.lower()
    if lowered in {"tired", "hungry", "sad", "happy", "angry", "here", "there", "ready", "sure"}:
        return False
    if lowered.split()[0] in {"a", "an", "the", "not", "still", "just", "very"}:
        return False
    if explicit:
        return bool(re.search(r"[A-Za-z]", value))
    return bool(re.match(r"^[A-Z][A-Za-z0-9_-]*(?:\s+[A-Z][A-Za-z0-9_-]*){0,2}$", value))


def _fact(
    *,
    kind: str,
    key: str,
    value: str,
    confidence: float,
    source_ring: int,
    evidence: str,
    status: str = "known",
) -> dict[str, Any]:
    return {
        "id": uuid.uuid4().hex,
        "kind": kind,
        "key": key,
        "value": value,
        "confidence": round(confidence, 3),
        "source_ring": source_ring,
        "evidence": trim_for_prompt(evidence, 260),
        "status": status,
        "supersedes": None,
    }


def extract_memory_facts(ring: Any, *, persona_name: str) -> list[dict[str, Any]]:
    query = str(getattr(ring, "query", "") or "")
    ring_number = int(getattr(ring, "n", 0) or 0)
    facts: list[dict[str, Any]] = []

    name_patterns = (
        (r"\bmy name is\s+([^,.\n!?]+)", 0.96, True),
        (r"\bcall me\s+([^,.\n!?]+)", 0.92, True),
        (r"\bi am\s+([^,.\n!?]+)", 0.82, False),
        (r"\bi'm\s+([^,.\n!?]+)", 0.82, False),
    )
    for pattern, confidence, explicit in name_patterns:
        match = re.search(pattern, query, re.I)
        if not match:
            continue
        value = _name_value(match.group(1))
        if _looks_like_name(value, explicit=explicit):
            facts.append(_fact(
                kind="identity",
                key="user.name",
                value=value,
                confidence=confidence,
                source_ring=ring_number,
                evidence=query,
            ))
            break

    description_match = re.search(r"\bi am\s+((?:a|an|the)\s+[^,.\n!?]+)", query, re.I)
    if description_match:
        value = _clean_fact_value(description_match.group(1), max_words=10)
        if value and not any(fact["key"] == "user.name" for fact in facts):
            facts.append(_fact(
                kind="identity",
                key="user.description",
                value=value,
                confidence=0.68,
                source_ring=ring_number,
                evidence=query,
            ))

    persona_match = re.search(r"\byou are\s+([A-Z][A-Za-z0-9_-]*(?:\s+[A-Z][A-Za-z0-9_-]*){0,2})", query)
    if persona_match:
        value = _name_value(persona_match.group(1))
        if value and value.lower() != persona_name.lower():
            facts.append(_fact(
                kind="persona",
                key="assistant.persona_name",
                value=value,
                confidence=0.74,
                source_ring=ring_number,
                evidence=query,
            ))

    preference_patterns = (
        r"\bi prefer\s+([^.\n!?]+)",
        r"\bi like\s+([^.\n!?]+)",
        r"\bi want you to\s+([^.\n!?]+)",
        r"\bplease\s+([^.\n!?]+)",
    )
    for pattern in preference_patterns:
        match = re.search(pattern, query, re.I)
        if match:
            value = _clean_fact_value(match.group(1), max_words=18)
            if value:
                facts.append(_fact(
                    kind="preference",
                    key=f"user.preference.{len(facts) + 1}",
                    value=value,
                    confidence=0.66,
                    source_ring=ring_number,
                    evidence=query,
                ))
            break

    if re.search(r"\b(?:not sure|i don't know|i do not know|maybe|perhaps)\b", query, re.I):
        facts.append(_fact(
            kind="uncertainty",
            key="user.uncertainty",
            value=_clean_fact_value(query, max_words=18),
            confidence=0.55,
            source_ring=ring_number,
            evidence=query,
            status="uncertain",
        ))

    return facts


def update_memory_model(model: dict[str, Any], ring: Any, *, persona_name: str) -> list[dict[str, Any]]:
    model.setdefault("version", 1)
    facts = model.setdefault("facts", [])
    extracted = extract_memory_facts(ring, persona_name=persona_name)
    correction = bool(re.match(r"^\s*(?:no|nope|actually|correction|wrong)\b", str(getattr(ring, "query", "")), re.I))

    for fact in extracted:
        if correction or fact["key"] in {"user.name", "assistant.persona_name"}:
            previous = [
                existing for existing in facts
                if existing.get("key") == fact["key"] and existing.get("status") == "known"
            ]
            for existing in previous:
                existing["status"] = "superseded"
                fact["supersedes"] = existing.get("id")

        duplicate = next(
            (
                existing for existing in facts
                if existing.get("key") == fact["key"]
                and str(existing.get("value", "")).lower() == fact["value"].lower()
                and existing.get("status") == fact["status"]
            ),
            None,
        )
        if duplicate:
            duplicate["confidence"] = max(float(duplicate.get("confidence", 0)), fact["confidence"])
            duplicate["source_ring"] = fact["source_ring"]
            duplicate["evidence"] = fact["evidence"]
        else:
            facts.append(fact)
    return extracted


def recall_memory_facts(model: dict[str, Any], query: str, *, limit: int = 6) -> list[dict[str, Any]]:
    query_tokens = set(re.findall(r"[A-Za-z0-9_-]+", query.lower()))
    wants_name = bool(re.search(r"\b(?:my name|call me|who am i|what is my name)\b", query, re.I))
    wants_persona = bool(re.search(r"\b(?:who are you|your name|what is your name)\b", query, re.I))
    scored: list[tuple[float, dict[str, Any]]] = []
    for fact in model.get("facts", []):
        if fact.get("status") not in {"known", "uncertain"}:
            continue
        fact_text = f"{fact.get('key', '')} {fact.get('value', '')} {fact.get('kind', '')}".lower()
        fact_tokens = set(re.findall(r"[A-Za-z0-9_-]+", fact_text))
        overlap = len(query_tokens & fact_tokens) / max(1, len(query_tokens))
        score = overlap + float(fact.get("confidence", 0.0))
        if wants_name and fact.get("key") == "user.name":
            score += 2.0
        if wants_persona and fact.get("key") == "assistant.persona_name":
            score += 1.4
        if fact.get("status") == "uncertain":
            score -= 0.25
        if score > 0.3:
            hit = dict(fact)
            hit["score"] = round(score, 4)
            scored.append((score, hit))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [fact for _, fact in scored[: max(1, min(limit, 20))]]


def build_memory_fact_context(facts: list[dict[str, Any]] | None) -> str:
    if not facts:
        return "No durable memories matched this query."
    lines = []
    for fact in facts[:8]:
        status = fact.get("status", "known")
        key = fact.get("key", "memory")
        value = fact.get("value", "")
        confidence = float(fact.get("confidence", 0.0))
        source = fact.get("source_ring", "?")
        prefix = "Uncertain" if status == "uncertain" else "Known"
        lines.append(f"- {prefix} {key}: {value} (confidence={confidence:.2f}, source ring #{source})")
    return "\n".join(lines)


def memory_retry_reason(query: str, content: str, facts: list[dict[str, Any]] | None, persona_name: str) -> str:
    answer = (content or "").strip()
    if not answer:
        return "The model returned an empty answer."
    facts = facts or []
    name_fact = next((fact for fact in facts if fact.get("key") == "user.name" and fact.get("status") == "known"), None)
    if name_fact and re.search(r"\b(?:my name|what is my name|who am i)\b", query, re.I):
        value = str(name_fact.get("value", "")).strip()
        if value and value.lower() not in answer.lower():
            return f"The answer missed the known user.name durable memory: {value}."
    if re.search(r"\b(?:who are you|what is your name|your name)\b", query, re.I):
        persona = persona_name.strip()
        if persona and persona.lower() not in answer.lower():
            return f"The answer missed the active persona name: {persona}."
    if "i don't know" in answer.lower() and facts:
        return "The answer claimed memory was absent even though durable memory hits were available."
    return ""


def local_memory_answer(query: str, facts: list[dict[str, Any]], persona_name: str) -> str:
    name_fact = next((fact for fact in facts if fact.get("key") == "user.name" and fact.get("status") == "known"), None)
    if name_fact and re.search(r"\b(?:my name|what is my name|who am i)\b", query, re.I):
        return f"Your name is {name_fact['value']}."
    persona_fact = next((fact for fact in facts if fact.get("key") == "assistant.persona_name" and fact.get("status") == "known"), None)
    if re.search(r"\b(?:who are you|what is your name|your name)\b", query, re.I):
        return f"I am {persona_fact.get('value') if persona_fact else persona_name}."
    return ""


def build_retry_messages(
    messages: list[dict[str, str]],
    *,
    reason: str,
    facts: list[dict[str, Any]],
) -> list[dict[str, str]]:
    retry = list(messages)
    retry.insert(1, {
        "role": "system",
        "content": (
            "Repair the previous answer. The prior response failed this requirement: "
            f"{reason}\nUse these durable memories as higher priority than ordinary chat text:\n"
            f"{build_memory_fact_context(facts)}"
        ),
    })
    return retry


def generate_persona_from_seed(name: str, seed: str) -> dict[str, str]:
    persona_name = _clean_fact_value(name, max_words=4)
    if not persona_name:
        raise ValueError("Persona name is required.")
    style = _clean_fact_value(seed, max_words=40) or "warm, practical, observant conversational partner"
    system = (
        f"You are {persona_name}, a fictional AI persona inspired by this vibe: {style}. "
        "Do not claim to be, impersonate, or have a personal relationship with any real public figure. "
        "Communicate in clear English with a consistent, grounded voice. "
        "Be helpful and specific. Remember useful user preferences through the CypherTempre memory flow."
    )
    return {"name": persona_name[:80], "domain": "auto", "system": system}


def build_memory_context(rings: list[Any]) -> str:
    if not rings:
        return "No prior relevant rings."
    lines = []
    for ring in rings[:6]:
        content = ring.content.strip().replace("\n", " ")
        if len(content) > 700:
            content = content[:697] + "..."
        lines.append(
            f"- Ring #{ring.n} [{ring.domain}, brightness={ring.brightness:.3f}, "
            f"epistemic={ring.epistemic}]: {content}"
        )
    return "\n".join(lines)


def trim_for_prompt(text: str, limit: int = 1400) -> str:
    normalized = (text or "").strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."


def build_recent_turns(chain: list[Any], limit: int = 8) -> list[dict[str, str]]:
    interactions = [ring for ring in chain if getattr(ring, "kind", "") == "interaction"]
    selected = interactions[-max(0, min(limit, 20)):]
    turns: list[dict[str, str]] = []
    for ring in selected:
        turns.append({"role": "user", "content": trim_for_prompt(ring.query)})
        turns.append({"role": "assistant", "content": trim_for_prompt(ring.content)})
    return turns


def serialize_history(chain: list[Any], limit: int = 80) -> list[dict[str, Any]]:
    interactions = [ring for ring in chain if getattr(ring, "kind", "") == "interaction"]
    selected = interactions[-max(1, min(limit, 200)):]
    history: list[dict[str, Any]] = []
    for ring in selected:
        history.append({
            "role": "user",
            "content": ring.query,
            "domain": ring.domain,
            "ring": ring.n,
            "ts": ring.ts,
        })
        history.append({
            "role": "assistant",
            "content": ring.content,
            "domain": ring.domain,
            "ring": ring.n,
            "ts": ring.ts,
            "brightness": round(float(ring.brightness), 3),
            "epistemic": ring.epistemic,
            "hash_prefix": ring.hash[:16],
        })
    return history


def classify_domain(query: str, persona: dict[str, str], requested_domain: str | None) -> str:
    requested = (requested_domain or "").strip()
    if requested and requested.lower() != "auto":
        return requested

    text = f"{query} {persona.get('name', '')} {persona.get('system', '')}".lower()
    scores: dict[str, int] = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        scores[domain] = sum(1 for keyword in keywords if keyword in text)

    best_domain, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score > 0:
        return best_domain
    return persona.get("domain") or "architecture"


def normalize_custom_persona(raw: Any) -> dict[str, str] | None:
    if not isinstance(raw, dict):
        return None
    name = str(raw.get("name", "")).strip()
    system = str(raw.get("system", "")).strip()
    domain = str(raw.get("domain", "architecture")).strip() or "architecture"
    if not name or not system:
        return None
    return {
        "name": name[:80],
        "domain": domain[:40],
        "system": system[:4000],
    }


def build_messages(
    *,
    persona: dict[str, str],
    query: str,
    retrieved: list[Any],
    recent_turns: list[dict[str, str]],
    neuro: dict[str, float],
    covenant: str,
    durable_memories: list[dict[str, Any]] | None = None,
) -> list[dict[str, str]]:
    memory_context = build_memory_context(retrieved)
    durable_context = build_memory_fact_context(durable_memories)
    neuro_line = ", ".join(f"{key}={value:.2f}" for key, value in sorted(neuro.items()))
    messages = [
        {
            "role": "system",
            "content": (
                f"{persona['system']}\n\n"
                "You are connected to a local CypherTempre Timechain. "
                "Use recalled rings as memory, but distinguish memory from fresh inference. "
                "Continue the current conversation naturally using the recent turns. "
                "If asked who you are, answer as the selected persona, not as the underlying model or provider. "
                "Be conversational and useful. Do not expose hidden reasoning. "
                "If memory is weak or absent, say so briefly.\n\n"
                f"Engineering covenant: {covenant}"
            ),
        },
        {
            "role": "system",
            "content": (
                f"Durable memories:\n{durable_context}\n\n"
                f"Relevant recalled rings:\n{memory_context}\n\n"
                f"Current neuro-state: {neuro_line}"
            ),
        },
    ]
    messages.extend(recent_turns)
    messages.append({"role": "user", "content": query})
    return messages


def call_openrouter(
    *,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    timeout: float,
) -> dict[str, Any]:
    api_key = api_key.strip()
    if not api_key:
        raise RuntimeError("OpenRouter API key is missing. Add a browser key or set OPENROUTER_API_KEY.")
    if api_key in {"YOUR_OPENROUTER_API_KEY", "sk-or-your-key-here", "sk-or-your-real-key"}:
        raise RuntimeError("OpenRouter API key is still the example placeholder.")
    payload = {
        "model": model or DEFAULT_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 900,
    }
    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://127.0.0.1:8765",
            "X-Title": "CypherTempre Chat PoC",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(detail)
            message = parsed.get("error", {}).get("message") or parsed.get("message") or detail
        except json.JSONDecodeError:
            message = detail
        if exc.code == 429:
            message = (
                f"{message} The selected OpenRouter model is rate-limited or temporarily unavailable. "
                "Wait and retry, or choose a non-free model in Settings."
            )
        raise RuntimeError(f"OpenRouter HTTP {exc.code}: {message}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"OpenRouter request failed: {exc.reason}") from exc

    choices = body.get("choices") or []
    if not choices:
        raise RuntimeError("OpenRouter returned no choices.")
    message = choices[0].get("message") or {}
    content = (message.get("content") or "").strip()
    if not content:
        raise RuntimeError("OpenRouter returned an empty response.")
    return {
        "content": content,
        "model_used": body.get("model") or model,
        "usage": body.get("usage") or {},
    }


def parse_env_file(path: pathlib.Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def load_local_env(path: pathlib.Path) -> dict[str, str]:
    values = parse_env_file(path)
    for key, value in values.items():
        os.environ.setdefault(key, value)
    return values


def guide_topics_payload() -> list[dict[str, Any]]:
    return [
        {
            "id": topic["id"],
            "title": topic["title"],
            "summary": topic["summary"],
            "details": topic["details"],
            "sources": list(topic.get("sources", [])),
        }
        for topic in GUIDE_TOPICS
    ]


def get_guide_topic(topic_id: str) -> dict[str, Any]:
    topic_id = (topic_id or "").strip()
    for topic in GUIDE_TOPICS:
        if topic["id"] == topic_id:
            return topic
    raise KeyError(topic_id)


def _doc_path(workspace: pathlib.Path, source: str) -> pathlib.Path | None:
    root = workspace.resolve()
    candidate = (root / source).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    if candidate.exists() and candidate.is_file():
        return candidate
    return None


def _relevant_excerpt(path: pathlib.Path, keywords: set[str], *, max_chars: int = 900) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    matches: list[str] = []
    for paragraph in paragraphs:
        lowered = paragraph.lower()
        if any(keyword in lowered for keyword in keywords):
            matches.append(re.sub(r"\s+", " ", paragraph))
        if len("\n\n".join(matches)) >= max_chars:
            break
    if not matches:
        matches = [re.sub(r"\s+", " ", paragraphs[0])] if paragraphs else []
    excerpt = "\n\n".join(matches)
    return excerpt[:max_chars].strip()


def build_guide_source_bundle(topic: dict[str, Any], workspace: pathlib.Path) -> list[dict[str, str]]:
    keywords = {
        word.lower()
        for word in re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", f"{topic['id']} {topic['title']} {topic['summary']} {topic['details']}")
    }
    sources = [{
        "title": f"Guide: {topic['title']}",
        "path": "local guide",
        "excerpt": f"{topic['summary']}\n{topic['details']}",
    }]
    for source in topic.get("sources", []):
        if source.startswith("Guide:"):
            continue
        path = _doc_path(workspace, source)
        if not path:
            continue
        excerpt = _relevant_excerpt(path, keywords)
        if excerpt:
            sources.append({
                "title": source,
                "path": str(path),
                "excerpt": excerpt,
            })
    return sources


def build_guide_explainer_messages(topic: dict[str, Any], source_bundle: list[dict[str, str]]) -> list[dict[str, str]]:
    source_text = "\n\n".join(
        f"Source: {source['title']}\nPath: {source['path']}\nExcerpt:\n{source['excerpt']}"
        for source in source_bundle
    )
    return [
        {"role": "system", "content": GUIDE_EXPLAINER_PERSONA["system"]},
        {
            "role": "user",
            "content": (
                f"Explain this CypherTempre chat PoC guide topic for a user.\n\n"
                f"Topic: {topic['title']}\n\n"
                f"Source excerpts:\n{source_text}\n\n"
                "Answer in clear paragraphs. Include a short 'Sources used' line naming the local sources."
            ),
        },
    ]


def deterministic_guide_explanation(
    topic: dict[str, Any],
    source_bundle: list[dict[str, str]],
    *,
    openrouter_error: str = "",
) -> str:
    details = "\n".join(f"- {line.strip()}" for line in str(topic["details"]).splitlines() if line.strip())
    source_names = ", ".join(source["title"] for source in source_bundle)
    prefix = f"OpenRouter unavailable: {openrouter_error}\n\n" if openrouter_error else ""
    return (
        f"{prefix}{topic['title']}\n\n"
        f"{topic['summary']}\n\n"
        f"{details}\n\n"
        f"Sources used: {source_names}.\n\n"
        "If you ask about something not covered here, I will say it is not covered in the provided sources."
    )


def sanitize_session_id(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "-", value.strip())[:80].strip("-")
    return cleaned or "default"


def session_name_from_id(session_id: str) -> str:
    if session_id == "default":
        return "Default"
    return session_id.replace("-", " ").replace("_", " ").strip().title() or session_id


class App:
    def __init__(
        self,
        workspace: pathlib.Path,
        timechain_path: pathlib.Path,
        *,
        default_model: str,
        openrouter_api_key: str,
        openrouter_timeout: float,
    ) -> None:
        self.root_workspace = workspace.resolve()
        self.root_workspace.mkdir(parents=True, exist_ok=True)
        self.timechain = load_timechain_module(timechain_path)
        self.default_model = default_model
        self.openrouter_api_key = openrouter_api_key
        self.openrouter_timeout = openrouter_timeout
        self.active_session = "default"
        self.workspace = self.workspace_for_session(self.active_session)
        self.agent = self.timechain.TimechainAgent(workspace=self.workspace)

    @property
    def sessions_root(self) -> pathlib.Path:
        return self.root_workspace / "sessions"

    def workspace_for_session(self, session_id: str) -> pathlib.Path:
        session_id = sanitize_session_id(session_id)
        if session_id == "default":
            path = self.root_workspace
        else:
            path = self.sessions_root / session_id
        path.mkdir(parents=True, exist_ok=True)
        return path.resolve()

    def use_session(self, session_id: str | None) -> str:
        self.active_session = sanitize_session_id(session_id or self.active_session or "default")
        self.workspace = self.workspace_for_session(self.active_session)
        self.reload_agent()
        return self.active_session

    def list_sessions(self) -> list[dict[str, Any]]:
        sessions: list[dict[str, Any]] = []
        for session_id, path in [("default", self.root_workspace)]:
            chain_path = path / ".timechain" / "chain.jsonl"
            rings = sum(1 for _ in chain_path.open("r", encoding="utf-8")) if chain_path.exists() else 0
            sessions.append({"id": session_id, "name": "Default", "rings": rings})
        if self.sessions_root.exists():
            for path in sorted(p for p in self.sessions_root.iterdir() if p.is_dir()):
                session_id = sanitize_session_id(path.name)
                chain_path = path / ".timechain" / "chain.jsonl"
                rings = sum(1 for _ in chain_path.open("r", encoding="utf-8")) if chain_path.exists() else 0
                sessions.append({"id": session_id, "name": session_name_from_id(session_id), "rings": rings})
        return sessions

    def create_session(self, name: str) -> dict[str, Any]:
        base = sanitize_session_id(name or "New conversation")
        if base == "default":
            base = "conversation"
        session_id = base
        index = 2
        while (self.sessions_root / session_id).exists():
            session_id = f"{base}-{index}"
            index += 1
        self.use_session(session_id)
        return {"id": session_id, "name": session_name_from_id(session_id), "rings": len(self.agent.chain)}

    def reload_agent(self) -> None:
        self.agent = self.timechain.TimechainAgent(workspace=self.workspace)

    def memory_model(self) -> dict[str, Any]:
        model = load_memory_model(self.workspace)
        if not model.get("facts") and len(getattr(self.agent, "chain", [])) > 1:
            for ring in self.agent.chain:
                if getattr(ring, "kind", "") == "interaction":
                    update_memory_model(model, ring, persona_name="Companion")
            if model.get("facts"):
                save_memory_model(self.workspace, model)
        return model

    def save_memory_model(self, model: dict[str, Any]) -> None:
        save_memory_model(self.workspace, model)

    def custom_personas(self) -> dict[str, dict[str, str]]:
        return load_custom_personas(self.root_workspace)

    def get_custom_persona(self, persona_id: str) -> dict[str, str] | None:
        return self.custom_personas().get(sanitize_session_id(persona_id))

    def save_custom_persona(self, persona_id: str, persona: dict[str, str]) -> dict[str, str]:
        persona_id = sanitize_session_id(persona_id)
        normalized = normalize_custom_persona(persona)
        if not normalized:
            raise ValueError("Invalid custom persona.")
        personas = self.custom_personas()
        personas[persona_id] = normalized
        save_custom_personas(self.root_workspace, personas)
        return normalized

    def self_model(self) -> dict[str, Any]:
        self.reload_agent()
        model = self.agent.self_model()
        memory_model = self.memory_model()
        model["workspace"] = str(self.workspace)
        model["memory_facts"] = [
            fact for fact in memory_model.get("facts", [])
            if fact.get("status") in {"known", "uncertain"}
        ]
        model["memory_fact_count"] = len(model["memory_facts"])
        return model

    def reset_chain(self) -> dict[str, Any]:
        root = (self.workspace / ".timechain").resolve()
        workspace = self.workspace.resolve()
        if workspace not in root.parents:
            raise RuntimeError(f"Refusing to reset unexpected path: {root}")
        if root.exists():
            shutil.rmtree(root)
        self.reload_agent()
        self.save_memory_model(empty_memory_model())
        return {
            "workspace": str(self.workspace),
            "rings": len(self.agent.chain),
            "genesis_hash": self.agent.genesis_hash,
        }

    def explain_guide_topic(self, topic_id: str, *, model: str, api_key: str) -> dict[str, Any]:
        topic = get_guide_topic(topic_id)
        source_bundle = build_guide_source_bundle(topic, self.root_workspace)
        messages = build_guide_explainer_messages(topic, source_bundle)
        key = api_key or self.openrouter_api_key
        openrouter_error = ""
        if key:
            try:
                llm = call_openrouter(
                    api_key=key,
                    model=model or self.default_model,
                    messages=messages,
                    timeout=self.openrouter_timeout,
                )
                content = llm["content"]
                model_used = llm.get("model_used", model or self.default_model)
            except RuntimeError as exc:
                openrouter_error = str(exc)
                content = deterministic_guide_explanation(topic, source_bundle, openrouter_error=openrouter_error)
                model_used = "local-source-summary"
        else:
            content = deterministic_guide_explanation(topic, source_bundle)
            model_used = "local-source-summary"

        session = self.create_session(f"Explain: {topic['title']}")
        query = f"Explain guide topic: {topic['title']}"
        result = self.agent.interact(
            query,
            domain="architecture",
            tags=["guide-explain", topic["id"], "source-grounded"],
            override_content=content,
        )
        return {
            "topic": {"id": topic["id"], "title": topic["title"]},
            "session": session,
            "accepted": bool(result.get("accepted")),
            "ring": result.get("ring"),
            "content": content,
            "model_used": model_used,
            "openrouter_error": openrouter_error,
            "sources": source_bundle,
            "reason": result.get("reason", ""),
        }

    def generate_llm_response(
        self,
        *,
        query: str,
        domain: str,
        persona_id: str,
        custom_persona: dict[str, str] | None,
        model: str,
        api_key: str,
    ) -> dict[str, Any]:
        persona = custom_persona or self.get_custom_persona(persona_id) or PERSONAS.get(persona_id) or PERSONAS["companion"]
        memory_model = self.memory_model()
        durable_hits = recall_memory_facts(memory_model, query, limit=6)
        retrieved_scored = self.timechain.retrieve(
            self.agent.chain,
            query,
            domain=domain,
            cphy_weights=self.agent.cphy_weights,
            config=self.timechain.RetrieverConfig(limit=6),
        )
        retrieved = [ring for _, ring in retrieved_scored]
        recent_turns = build_recent_turns(self.agent.chain, limit=8)
        neuro = self.timechain.compute_neuro(self.agent.chain, domain)
        messages = build_messages(
            persona=persona,
            query=query,
            retrieved=retrieved,
            durable_memories=durable_hits,
            recent_turns=recent_turns,
            neuro=neuro,
            covenant=self.agent.values,
        )
        key = api_key or self.openrouter_api_key
        def local_fallback(openrouter_error: str = "") -> dict[str, Any]:
            fallback = self.timechain._default_generator(query, retrieved, neuro)
            retry_reason = memory_retry_reason(query, fallback, durable_hits, persona["name"])
            local_repair = local_memory_answer(query, durable_hits, persona["name"]) if retry_reason else ""
            if local_repair:
                fallback = local_repair
            result = {
                "content": fallback,
                "model_used": "local-default-generator",
                "usage": {},
                "retrieved": [ring.n for ring in retrieved],
                "memory_hits": durable_hits,
                "retry": {"attempted": bool(local_repair), "reason": retry_reason},
                "persona": persona,
            }
            if openrouter_error:
                result["openrouter_error"] = openrouter_error
            return result

        if not key:
            return local_fallback()
        try:
            llm = call_openrouter(
                api_key=key,
                model=model or self.default_model,
                messages=messages,
                timeout=self.openrouter_timeout,
            )
        except RuntimeError as exc:
            return local_fallback(str(exc))
        retry_reason = memory_retry_reason(query, llm.get("content", ""), durable_hits, persona["name"])
        retry = {"attempted": False, "reason": retry_reason}
        if retry_reason:
            try:
                repaired = call_openrouter(
                    api_key=key,
                    model=model or self.default_model,
                    messages=build_retry_messages(messages, reason=retry_reason, facts=durable_hits),
                    timeout=self.openrouter_timeout,
                )
                llm = repaired
                retry["attempted"] = True
            except RuntimeError as exc:
                llm["openrouter_error"] = str(exc)
        llm["retrieved"] = [ring.n for ring in retrieved]
        llm["memory_hits"] = durable_hits
        llm["retry"] = retry
        llm["persona"] = persona
        return llm


def make_handler(app: App) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "CypherTempreChatPoC/0.2"

        def log_message(self, fmt: str, *args: Any) -> None:
            print(f"{self.address_string()} - {fmt % args}")

        def do_GET(self) -> None:
            path = urlparse(self.path).path
            try:
                if path == "/":
                    self.send_html(HTML)
                    return
                if path == "/api/config":
                    self.send_json({
                        "ok": True,
                        "default_model": app.default_model,
                        "has_env_key": bool(app.openrouter_api_key),
                        "personas": {
                            key: {"name": value["name"], "domain": value["domain"]}
                            for key, value in PERSONAS.items()
                        },
                        "custom_personas": app.custom_personas(),
                    })
                    return
                if path == "/api/guide/topics":
                    self.send_json({"ok": True, "topics": guide_topics_payload()})
                    return
                if path == "/api/sessions":
                    self.send_json({
                        "ok": True,
                        "active": app.active_session,
                        "sessions": app.list_sessions(),
                    })
                    return
                if path == "/api/self-model":
                    app.use_session(self.query_param("session"))
                    self.send_json({"ok": True, "model": app.self_model()})
                    return
                if path == "/api/memory-model":
                    app.use_session(self.query_param("session"))
                    self.send_json({"ok": True, "model": app.memory_model()})
                    return
                if path == "/api/history":
                    app.use_session(self.query_param("session"))
                    self.send_json({
                        "ok": True,
                        "history": serialize_history(app.agent.chain),
                        "rings": len(app.agent.chain),
                    })
                    return
                if path == "/api/verify":
                    app.use_session(self.query_param("session"))
                    ok, status = app.timechain.verify_chain(app.agent.chain)
                    self.send_json({"ok": ok, "status": status, "rings": len(app.agent.chain)})
                    return
                self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            except Exception as exc:
                self.send_exception(exc)

        def do_POST(self) -> None:
            path = urlparse(self.path).path
            try:
                if path == "/api/chat":
                    self.handle_chat()
                    return
                if path == "/api/sessions":
                    self.handle_create_session()
                    return
                if path == "/api/personas":
                    self.handle_save_persona()
                    return
                if path == "/api/openrouter-test":
                    self.handle_openrouter_test()
                    return
                if path == "/api/guide/explain":
                    self.handle_guide_explain()
                    return
                if path == "/api/recall":
                    self.handle_recall()
                    return
                if path == "/api/reset":
                    self.handle_reset()
                    return
                self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            except Exception as exc:
                self.send_exception(exc)

        def handle_chat(self) -> None:
            payload = self.read_json()
            app.use_session(str(payload.get("session", "")).strip() or self.query_param("session"))
            message = str(payload.get("message", "")).strip()
            persona_id = str(payload.get("persona", "companion")).strip() or "companion"
            custom_persona = normalize_custom_persona(payload.get("customPersona"))
            if custom_persona:
                app.save_custom_persona(persona_id, custom_persona)
            persona = custom_persona or app.get_custom_persona(persona_id) or PERSONAS.get(persona_id) or PERSONAS["companion"]
            requested_domain = str(payload.get("domain", "auto")).strip() or "auto"
            domain = classify_domain(message, persona, requested_domain)
            model = str(payload.get("model", app.default_model)).strip() or app.default_model
            api_key = str(payload.get("apiKey", "")).strip()
            if not message:
                self.send_json({"ok": False, "error": "message is required"}, HTTPStatus.BAD_REQUEST)
                return

            app.reload_agent()
            llm = app.generate_llm_response(
                query=message,
                domain=domain,
                persona_id=persona_id,
                custom_persona=custom_persona,
                model=model,
                api_key=api_key,
            )
            result = app.agent.interact(
                message,
                domain=domain,
                tags=[domain, "chat-poc", persona_id],
                override_content=llm["content"],
            )
            if not result.get("accepted"):
                self.send_json({
                    "ok": True,
                    "accepted": False,
                    "reason": result.get("reason"),
                    "brightness": result.get("brightness"),
                    "scores": result.get("scores"),
                    "content": llm["content"],
                    "model": model,
                    "model_used": llm.get("model_used"),
                    "openrouter_error": llm.get("openrouter_error", ""),
                    "persona_name": persona["name"],
                    "domain": domain,
                })
                return

            ring = result["ring"]
            memory_model = app.memory_model()
            extracted = update_memory_model(
                memory_model,
                SimpleNamespace(**ring),
                persona_name=persona["name"],
            )
            app.save_memory_model(memory_model)
            self.send_json({
                "ok": True,
                "accepted": True,
                "content": ring.get("content", ""),
                "ring": ring.get("n"),
                "hash": ring.get("hash"),
                "hash_prefix": str(ring.get("hash", ""))[:16],
                "brightness": round(float(result.get("brightness", 0)), 3),
                "scores": result.get("scores"),
                "retrieved": llm.get("retrieved", result.get("retrieved")),
                "memory_hits": llm.get("memory_hits", []),
                "memory_extracted": extracted,
                "retry": llm.get("retry", {"attempted": False, "reason": ""}),
                "epistemic": result.get("epistemic"),
                "cache_hit": result.get("cache_hit"),
                "model": model,
                "model_used": llm.get("model_used"),
                "openrouter_error": llm.get("openrouter_error", ""),
                "usage": llm.get("usage", {}),
                "persona_name": persona["name"],
                "domain": domain,
            })

        def handle_recall(self) -> None:
            payload = self.read_json()
            app.use_session(str(payload.get("session", "")).strip() or self.query_param("session"))
            query = str(payload.get("query", "")).strip()
            domain = str(payload.get("domain", "")).strip() or None
            limit = int(payload.get("limit", 6))
            if not query:
                self.send_json({"ok": False, "error": "query is required"}, HTTPStatus.BAD_REQUEST)
                return

            app.reload_agent()
            memory_model = app.memory_model()
            fact_hits = recall_memory_facts(memory_model, query, limit=limit)
            retrieved = app.timechain.retrieve(
                app.agent.chain,
                query,
                domain=domain,
                cphy_weights=app.agent.cphy_weights,
                config=app.timechain.RetrieverConfig(limit=max(1, min(limit, 20))),
            )
            results = []
            for score, ring in retrieved:
                content = ring.content[:500] if len(ring.content) > 500 else ring.content
                results.append({
                    "score": round(float(score), 4),
                    "n": ring.n,
                    "ts": ring.ts,
                    "brightness": ring.brightness,
                    "kind": ring.kind,
                    "domain": ring.domain,
                    "query": ring.query,
                    "content": content,
                    "tags": ring.tags,
                    "hash_prefix": ring.hash[:16],
                    "epistemic": ring.epistemic,
                })
            diagnostics = [
                f"durable facts matched: {len(fact_hits)}",
                f"rings matched: {len(results)}",
                f"domain filter: {domain or 'none'}",
            ]
            self.send_json({
                "ok": True,
                "query": query,
                "facts": fact_hits,
                "rings": results,
                "results": results,
                "diagnostics": diagnostics,
            })

        def handle_reset(self) -> None:
            app.use_session(self.query_param("session"))
            result = app.reset_chain()
            self.send_json({"ok": True, **result})

        def handle_create_session(self) -> None:
            payload = self.read_json()
            session = app.create_session(str(payload.get("name", "")).strip() or "New conversation")
            self.send_json({"ok": True, "session": session, "sessions": app.list_sessions()})

        def handle_openrouter_test(self) -> None:
            payload = self.read_json()
            model = str(payload.get("model", app.default_model)).strip() or app.default_model
            api_key = str(payload.get("apiKey", "")).strip() or app.openrouter_api_key
            result = call_openrouter(
                api_key=api_key,
                model=model,
                messages=[{"role": "user", "content": "Reply with exactly: ok"}],
                timeout=min(app.openrouter_timeout, 20.0),
            )
            self.send_json({
                "ok": True,
                "model": model,
                "model_used": result.get("model_used"),
                "content": result.get("content"),
            })

        def handle_guide_explain(self) -> None:
            payload = self.read_json()
            topic_id = str(payload.get("topicId", "")).strip()
            model = str(payload.get("model", app.default_model)).strip() or app.default_model
            api_key = str(payload.get("apiKey", "")).strip()
            try:
                result = app.explain_guide_topic(topic_id, model=model, api_key=api_key)
            except KeyError:
                self.send_json({"ok": False, "error": f"Unknown guide topic: {topic_id}"}, HTTPStatus.NOT_FOUND)
                return
            self.send_json({"ok": True, **result})

        def handle_save_persona(self) -> None:
            payload = self.read_json()
            persona_id = str(payload.get("id", "")).strip() or f"custom_{uuid.uuid4().hex[:12]}"
            persona = app.save_custom_persona(persona_id, payload.get("persona"))
            self.send_json({
                "ok": True,
                "id": sanitize_session_id(persona_id),
                "persona": persona,
                "custom_personas": app.custom_personas(),
            })

        def query_param(self, name: str) -> str:
            parsed = urlparse(self.path)
            pairs = [part.split("=", 1) for part in parsed.query.split("&") if part]
            for key, value in pairs:
                if key == name:
                    return urllib.parse.unquote_plus(value)
            return ""

        def read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0") or "0")
            if length <= 0:
                return {}
            raw = self.rfile.read(length).decode("utf-8")
            return json.loads(raw)

        def send_html(self, html: str) -> None:
            encoded = html.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def send_json(self, body: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
            encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def send_exception(self, exc: Exception) -> None:
            traceback.print_exc()
            self.send_json(
                {"ok": False, "error": str(exc), "type": type(exc).__name__},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    return Handler


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the standalone CypherTempre chat PoC.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument(
        "--workspace",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parent,
        help="Directory where .timechain will be created.",
    )
    parser.add_argument(
        "--timechain-path",
        type=pathlib.Path,
        default=DEFAULT_TIMECHAIN_PATH,
        help="Path to the timechain.py skill script.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Default OpenRouter model. Defaults to the Venice Uncensored free model.",
    )
    parser.add_argument(
        "--openrouter-api-key",
        default=None,
        help="OpenRouter API key. If omitted, the UI can send a browser-session key.",
    )
    parser.add_argument(
        "--env-file",
        type=pathlib.Path,
        default=DEFAULT_ENV_PATH,
        help="Local env file for persistent test keys.",
    )
    parser.add_argument("--openrouter-timeout", type=float, default=45.0)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    load_local_env(args.env_file)
    default_model = args.model or os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL)
    openrouter_api_key = args.openrouter_api_key or os.environ.get("OPENROUTER_API_KEY", "")
    app = App(
        args.workspace,
        args.timechain_path,
        default_model=default_model,
        openrouter_api_key=openrouter_api_key,
        openrouter_timeout=args.openrouter_timeout,
    )
    handler = make_handler(app)
    server = ThreadingHTTPServer((args.host, args.port), handler)
    url = f"http://{args.host}:{args.port}"
    print(f"CypherTempre chat PoC running at {url}")
    print(f"Workspace: {app.workspace}")
    print(f"Default model: {app.default_model}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
