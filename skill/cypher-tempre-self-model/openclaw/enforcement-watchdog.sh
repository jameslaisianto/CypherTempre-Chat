#!/bin/bash
# Optional OpenClaw watchdog for Cypher Tempre.
# Use this when OpenClaw lifecycle hooks are unavailable or not yet wired. It
# checks whether the most recently marked turn has sealed a ring.

set -euo pipefail

SKILL="${CT_SKILL_DIR:-$HOME/.openclaw/workspace/skills/cypher-tempre-self-model}"

if [ ! -f "$SKILL/enforce.py" ]; then
  echo "Cypher Tempre skill not found at: $SKILL" >&2
  echo "Set CT_SKILL_DIR=/path/to/cypher-tempre-self-model and try again." >&2
  exit 2
fi

out="$(python3 "$SKILL/enforce.py" stop-check 2>&1 || true)"
if [ -n "$out" ]; then
  printf '%s\n' "$out"
else
  echo "Cypher Tempre watchdog: no pending marked OpenClaw turn is currently unsealed."
fi
