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

def _run():
    from virtual_taylor_frame.main import main
    return main()

if __name__ == "__main__":
    try:
        sys.exit(_run())
    except Exception:
        import traceback
        import ctypes
        err = traceback.format_exc()
        try:
            ctypes.windll.user32.MessageBoxW(
                0,
                f"An error occurred while launching Virtual Taylor Frame:\n\n{err}",
                "Virtual Taylor Frame - Startup Error",
                0x10,
            )
        except Exception:
            pass
        sys.exit(1)

