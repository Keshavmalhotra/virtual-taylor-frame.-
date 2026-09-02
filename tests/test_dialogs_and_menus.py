"""
Unit tests for accessible dialogs, menu actions, and vector paint rendering.
"""
import os
import tempfile
import pytest

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QKeyEvent

from virtual_taylor_frame.model.frame import TaylorFrame
from virtual_taylor_frame.model.peg import TaylorPeg
from virtual_taylor_frame.model.types import (
    PegOrientation,
    PegEnd,
    PegType,
    VerbosityLevel,
)
from virtual_taylor_frame.commands.history import UndoRedoManager
from virtual_taylor_frame.accessibility.ao3_engine import MockSpeechEngine
from virtual_taylor_frame.accessibility.announcer import Announcer
from virtual_taylor_frame.accessibility.audio_cues import AudioCues
from virtual_taylor_frame.ui.main_window import MainWindow
from virtual_taylor_frame.ui.frame_widget import TaylorFrameWidget
from virtual_taylor_frame.ui.dialogs import (
    HelpDialog,
    GoToDialog,
    NewFrameDialog,
    InspectDialog,
)
from virtual_taylor_frame.ui.themes import THEMES


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestDialogs:
    def test_help_dialog(self, qapp):
        dlg = HelpDialog()
        assert dlg.windowTitle() == "Virtual Taylor Frame - Help & Keyboard Reference"
        assert "Keyboard" in dlg.browser.toPlainText()
        dlg.close()

    def test_goto_dialog(self, qapp):
        dlg = GoToDialog(current_row=4, current_col=7, max_rows=20, max_cols=30)
        assert dlg.row_spin.value() == 5
        assert dlg.col_spin.value() == 8

        dlg.row_spin.setValue(12)
        dlg.col_spin.setValue(18)
        r, c = dlg.get_coordinates()
        assert (r, c) == (11, 17)
        dlg.close()

    def test_new_frame_dialog_preset(self, qapp):
        dlg = NewFrameDialog(default_rows=20, default_cols=30)
        # Choose Small Frame (15x20)
        dlg.preset_combo.setCurrentIndex(1)
        rows, cols = dlg.get_dimensions()
        assert (rows, cols) == (15, 20)
        dlg.close()

    def test_inspect_dialog(self, qapp):
        sample_text = "Taylor Frame Summary.\nRow 5: 7 + 3 = 10"
        dlg = InspectDialog(sample_text)
        assert dlg.text_edit.toPlainText() == sample_text
        dlg._copy_to_clipboard()
        assert dlg.copy_btn.text() == "Copied!"
        dlg.close()


class TestPaintRendering:
    def test_widget_paint_rendering(self, qapp):
        frame = TaylorFrame(10, 10)
        # Place various peg types to test all rendering branches
        frame.place_peg(0, 0, TaylorPeg.from_state(PegType.ARITHMETIC, PegEnd.END_A_BAR, PegOrientation.N_0))
        frame.place_peg(0, 1, TaylorPeg.from_state(PegType.ARITHMETIC, PegEnd.END_B_DOTS, PegOrientation.E_90))
        frame.place_peg(0, 2, TaylorPeg.from_state(PegType.ALGEBRAIC, PegEnd.END_A_ALGEBRA, PegOrientation.N_0))
        frame.place_peg(0, 3, TaylorPeg.from_state(PegType.ALGEBRAIC, PegEnd.END_B_ALGEBRA, PegOrientation.NW_315))

        engine = MockSpeechEngine()
        announcer = Announcer(engine=engine)
        cues = AudioCues(enabled=False)
        history = UndoRedoManager()

        widget = TaylorFrameWidget(frame, history, announcer, cues)
        widget.resize(600, 600)

        # Test paint on pixmap for all themes
        pixmap = QPixmap(600, 600)
        for theme_key in THEMES:
            widget.set_theme(theme_key)
            widget.render(pixmap)
            assert not pixmap.isNull()


class TestMainWindowOperations:
    def test_main_window_menu_actions(self, qapp):
        frame = TaylorFrame(10, 10)
        engine = MockSpeechEngine()
        announcer = Announcer(engine=engine)
        cues = AudioCues(enabled=False)

        win = MainWindow(frame=frame, announcer=announcer, audio_cues=cues)
        win.show()

        # Type '7'
        ev_7 = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_7, Qt.KeyboardModifier.NoModifier, text="7")
        win.frame_widget.keyPressEvent(ev_7)
        assert win.history.is_dirty is True
        assert "*" in win.windowTitle()

        # Save to temp file
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_file = os.path.join(tmpdir, "menu_test.tframe")
            win.current_filepath = temp_file
            saved = win._on_file_save()
            assert saved is True
            assert win.history.is_dirty is False
            assert "*" not in win.windowTitle()

        # Cycle verbosity
        win._on_cycle_verbosity()
        assert "Verbosity" in engine.last_spoken

        # Toggle sound
        win._on_toggle_sound(True)
        assert win.audio_cues.enabled is True

        win.close()
