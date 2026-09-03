"""
Application entry point for Virtual Taylor Frame.
Supports both standard terminal execution and windowed/no-console execution (pythonw).
"""
import sys
import os
import io
import argparse
from pathlib import Path

# Safe stream redirection for windowed execution (pythonw on Windows has None for stdout/stderr)
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

# Ensure the root package directory is always in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from virtual_taylor_frame.model.frame import TaylorFrame
from virtual_taylor_frame.model.types import VerbosityLevel
from virtual_taylor_frame.accessibility.ao3_engine import AO3Engine
from virtual_taylor_frame.accessibility.announcer import Announcer
from virtual_taylor_frame.accessibility.audio_cues import AudioCues
from virtual_taylor_frame.storage.tframe_format import TFrameStorage
from virtual_taylor_frame.ui.main_window import MainWindow


def parse_args():
    parser = argparse.ArgumentParser(description="Virtual Taylor Frame - Accessible Math Tool")
    parser.add_argument("file", nargs="?", help="Path to .tframe file to open")
    parser.add_argument("--rows", type=int, default=20, help="Initial rows (default 20)")
    parser.add_argument("--cols", type=int, default=30, help="Initial columns (default 30)")
    parser.add_argument(
        "--verbosity",
        choices=["minimal", "normal", "detailed"],
        default="normal",
        help="Speech verbosity level",
    )
    parser.add_argument("--no-audio", action="store_true", help="Disable earcon sound cues")
    return parser.parse_args()


def main():
    args = parse_args()

    # Create Qt Application
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    app.setApplicationName("Virtual Taylor Frame")
    app.setOrganizationName("AccessibleMath")
    app.setApplicationVersion("0.1.0")

    # Initialize accessibility components
    ao_engine = AO3Engine()
    verbosity = VerbosityLevel(args.verbosity)
    announcer = Announcer(engine=ao_engine, verbosity=verbosity)
    audio_cues = AudioCues(enabled=not args.no_audio)

    # Initial frame
    frame = None
    if args.file and Path(args.file).exists():
        try:
            frame, _ = TFrameStorage.load(args.file)
        except Exception:
            frame = TaylorFrame(rows=args.rows, cols=args.cols)
    else:
        frame = TaylorFrame(rows=args.rows, cols=args.cols)

    window = MainWindow(
        frame=frame,
        announcer=announcer,
        audio_cues=audio_cues,
    )

    if args.file and Path(args.file).exists():
        window.current_filepath = str(Path(args.file).resolve())
        window._update_title_and_actions()

    window.show()
    window.raise_()
    window.activateWindow()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
