#!/usr/bin/env python3
"""Entry point — argument parsing and server start.

Usage:
    python -m server [--host 127.0.0.1] [--port 8765] [--workspace .] [--timechain-path timechain.py]
"""

import sys
import pathlib

# Ensure the project root is on sys.path so `import marketplace` works
_project_root = pathlib.Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from server.server import main

if __name__ == "__main__":
    sys.exit(main())
