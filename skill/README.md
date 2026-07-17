# Vendored Cypher Tempre skill

This folder holds the **OpenClaw** runtime bundle of Cypher Tempre, vendored from:

https://github.com/cyberphysicsai/cypher-tempre-genesis

| Field | Value |
|--|--|
| Bundle | `skills/openclaw/cypher-tempre-self-model` |
| Version | **3.28.0** (see `cypher-tempre-self-model/VERSION`) |
| Role | Authoritative ledger, PoQ, recall, Cambium, dream, immune, router |

## Do not edit engine code here for app features

App-specific behavior lives under `server/` (especially `server/skill_runtime.py`). Upgrade the skill by replacing only the bundle code files while **preserving** each session’s `chain/` and `registry/` state under `data/users/...` (those are not in this folder).

## Upgrade

1. Back up the app and any local session data.
2. Download the new OpenClaw zip from the genesis repo `downloads/`.
3. Replace `skill/cypher-tempre-self-model/` **code** (`*.py`, `SKILL.md`, `VERSION`, `CHANGELOG.md`, base `registry/modalities.json` / `senses.json` only if you intend a fresh faculty baseline).
4. Never delete live session `chain/` or per-session grown registries under user data.
5. Run `python -c "from server.skill_runtime import bootstrap; print(bootstrap().version)"` and a chat smoke test.
