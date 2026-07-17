#!/usr/bin/env python3
"""Compatibility entrypoint — the Cypher Tempre skill now lives under skill/.

This file is intentionally not the Forge ledger. The authoritative engine is the
vendored OpenClaw skill bundle:

    skill/cypher-tempre-self-model/

Host integration:

    from server.skill_runtime import bootstrap, SkillSession

CLI:

    python skill/cypher-tempre-self-model/timechain.py verify --root <session-root>
"""

from __future__ import annotations

import importlib.util
import pathlib
import runpy
import sys

_SKILL_DIR = pathlib.Path(__file__).resolve().parent / "skill" / "cypher-tempre-self-model"
_SKILL_MAIN = _SKILL_DIR / "timechain.py"


def _load_skill_timechain():
    if not _SKILL_MAIN.exists():
        raise ImportError(
            "Vendored skill missing. Expected skill/cypher-tempre-self-model/timechain.py "
            "from https://github.com/cyberphysicsai/cypher-tempre-genesis (OpenClaw bundle)."
        )
    root = str(_SKILL_DIR.resolve())
    if root not in sys.path:
        sys.path.insert(0, root)
    spec = importlib.util.spec_from_file_location("cypher_tempre_skill_timechain", _SKILL_MAIN)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load skill timechain from {_SKILL_MAIN}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["cypher_tempre_skill_timechain"] = module
    spec.loader.exec_module(module)
    return module


_skill_tc = _load_skill_timechain()

# Re-export public skill timechain API under the historical root import name.
for _name in dir(_skill_tc):
    if _name.startswith("_") and _name not in {"__version__"}:
        continue
    globals()[_name] = getattr(_skill_tc, _name)

Timechain = _skill_tc.Timechain
Blockspace = getattr(_skill_tc, "Blockspace", None)
main = _skill_tc.main
SKILL_ROOT = _SKILL_DIR
SKILL_VERSION = (_SKILL_DIR / "VERSION").read_text(encoding="utf-8").strip() if (_SKILL_DIR / "VERSION").exists() else "unknown"

if __name__ == "__main__":
    # Run the skill CLI in-process.
    sys.argv[0] = str(_SKILL_MAIN)
    raise SystemExit(runpy.run_path(str(_SKILL_MAIN), run_name="__main__"))
