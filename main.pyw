"""
Windowed launcher for Virtual Taylor Frame (Runs with NO console/terminal window).
"""
import sys
import os
import io
from pathlib import Path

if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from virtual_taylor_frame.main import main

if __name__ == "__main__":
    sys.exit(main())
