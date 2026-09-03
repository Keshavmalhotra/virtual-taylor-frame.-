"""
Automated unit and integration tests for PySide6 UI and keyboard interaction.
"""
import os
import pytest

# Ensure headless execution for testing
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QKeyEvent

from virtual_taylor_frame.model.frame import TaylorFrame
from virtual_taylor_frame.model.peg import TaylorPeg
from virtual_taylor_frame.model.types import VerbosityLevel
from virtual_taylor_frame.commands.history import UndoRedoManager
from virtual_taylor_frame.accessibility.ao3_engine import MockSpeechEngine
from virtual_taylor_frame.accessibility.announcer import Announcer
from virtual_taylor_frame.accessibility.audio_cues import AudioCues
from virtual_taylor_frame.ui.frame_widget import TaylorFrameWidget
from virtual_taylor_frame.ui.main_window import MainWindow


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def ui_fixture(qapp):
    frame = TaylorFrame(10, 10)
    history = UndoRedoManager()
    engine = MockSpeechEngine()
    announcer = Announcer(engine=engine, verbosity=VerbosityLevel.NORMAL)
    cues = AudioCues(enabled=False)

    widget = TaylorFrameWidget(
        model=frame,
        history=history,
        announcer=announcer,
        audio_cues=cues,
    )
    return widget, frame, history, engine, announcer


class TestTaylorFrameWidgetKeyboard:
    def test_navigation_keys(self, ui_fixture):
        widget, frame, history, engine, announcer = ui_fixture

        # Press Down arrow
        ev_down = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Down, Qt.KeyboardModifier.NoModifier)
        widget.keyPressEvent(ev_down)
        assert (frame.cursor_row, frame.cursor_col) == (1, 0)
        assert engine.last_spoken == "Row 2, column 1. Empty."

        # Press Right arrow
        ev_right = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Right, Qt.KeyboardModifier.NoModifier)
        widget.keyPressEvent(ev_right)
        assert (frame.cursor_row, frame.cursor_col) == (1, 1)
        assert engine.last_spoken == "Row 2, column 2. Empty."

        # Press Up arrow
        ev_up = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Up, Qt.KeyboardModifier.NoModifier)
        widget.keyPressEvent(ev_up)
        assert (frame.cursor_row, frame.cursor_col) == (0, 1)

        # Press Left arrow
        ev_left = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Left, Qt.KeyboardModifier.NoModifier)
        widget.keyPressEvent(ev_left)
        assert (frame.cursor_row, frame.cursor_col) == (0, 0)

    def test_direct_math_typing(self, ui_fixture):
        widget, frame, history, engine, announcer = ui_fixture
        frame.set_cursor(0, 0)

        # Type '7'
        ev_7 = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_7, Qt.KeyboardModifier.NoModifier, text="7")
        widget.keyPressEvent(ev_7)
        assert frame.get_cell(0, 0).is_occupied is True
        assert frame.get_cell(0, 0).peg.symbol == "7"
        # Cursor auto-advanced right to column 1
        assert (frame.cursor_row, frame.cursor_col) == (0, 1)

        # Type '+'
        ev_plus = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Plus, Qt.KeyboardModifier.NoModifier, text="+")
        widget.keyPressEvent(ev_plus)
        assert frame.get_cell(0, 1).is_occupied is True
        assert frame.get_cell(0, 1).peg.symbol == "+"
        assert (frame.cursor_row, frame.cursor_col) == (0, 2)

    def test_rotate_and_flip_keys(self, ui_fixture):
        widget, frame, history, engine, announcer = ui_fixture
        frame.set_cursor(2, 2)
        frame.place_peg(2, 2, TaylorPeg.from_symbol("1"))

        # Rotate clockwise with 'R'
        ev_r = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_R, Qt.KeyboardModifier.NoModifier, text="r")
        widget.keyPressEvent(ev_r)
        assert frame.get_cell(2, 2).peg.symbol == "2"

        # Flip end with 'F'
        ev_f = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_F, Qt.KeyboardModifier.NoModifier, text="f")
        widget.keyPressEvent(ev_f)
        assert frame.get_cell(2, 2).peg.symbol == "0"  # NE_45 on End B is 0

    def test_delete_key(self, ui_fixture):
        widget, frame, history, engine, announcer = ui_fixture
        frame.set_cursor(1, 1)
        frame.place_peg(1, 1, TaylorPeg.from_symbol("9"))

        ev_del = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Delete, Qt.KeyboardModifier.NoModifier)
        widget.keyPressEvent(ev_del)
        assert frame.get_cell(1, 1).is_occupied is False
        assert "Removed" in engine.last_spoken

    def test_inspection_keys(self, ui_fixture):
        widget, frame, history, engine, announcer = ui_fixture
        frame.set_cursor(3, 3)
        frame.place_peg(3, 3, TaylorPeg.from_symbol("7"))

        # Space key inspects cell
        ev_space = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Space, Qt.KeyboardModifier.NoModifier, text=" ")
        widget.keyPressEvent(ev_space)
        assert "Number 7" in engine.last_spoken
        assert "Row 4, column 4" in engine.last_spoken

        # F5 key frame summary
        ev_f5 = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_F5, Qt.KeyboardModifier.NoModifier)
        widget.keyPressEvent(ev_f5)
        assert "Taylor Frame Construction" in engine.last_spoken

        # F6 key row expression
        ev_f6 = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_F6, Qt.KeyboardModifier.NoModifier)
        widget.keyPressEvent(ev_f6)
        assert "Row 4:" in engine.last_spoken

        # F7 key column vertical
        ev_f7 = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_F7, Qt.KeyboardModifier.NoModifier)
        widget.keyPressEvent(ev_f7)
        assert "Column 4" in engine.last_spoken

        # F8 key neighbors
        ev_f8 = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_F8, Qt.KeyboardModifier.NoModifier)
        widget.keyPressEvent(ev_f8)
        assert "Neighbors around Row 4, Column 4" in engine.last_spoken

    def test_undo_redo_shortcuts(self, ui_fixture):
        widget, frame, history, engine, announcer = ui_fixture
        frame.set_cursor(0, 0)

        # Place peg
        ev_3 = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_3, Qt.KeyboardModifier.NoModifier, text="3")
        widget.keyPressEvent(ev_3)
        assert frame.get_cell(0, 0).is_occupied is True

        # Ctrl+Z (Undo)
        ev_undo = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Z, Qt.KeyboardModifier.ControlModifier)
        widget.keyPressEvent(ev_undo)
        assert frame.get_cell(0, 0).is_occupied is False

        # Ctrl+Y (Redo)
        ev_redo = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Y, Qt.KeyboardModifier.ControlModifier)
        widget.keyPressEvent(ev_redo)
        assert frame.get_cell(0, 0).is_occupied is True


class TestMainWindowIntegration:
    def test_main_window_init(self, qapp):
        frame = TaylorFrame(15, 20)
        engine = MockSpeechEngine()
        announcer = Announcer(engine=engine, verbosity=VerbosityLevel.NORMAL)
        cues = AudioCues(enabled=False)

        win = MainWindow(frame=frame, announcer=announcer, audio_cues=cues)
        assert win.model.rows == 15
        assert win.model.cols == 20
        assert "Virtual Taylor Frame" in win.windowTitle()
        assert win.frame_widget is not None
        assert win.status is not None
