"""
Main Window for the Virtual Taylor Frame desktop application.
"""
from typing import Optional
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow,
    QScrollArea,
    QStatusBar,
    QLabel,
    QFileDialog,
    QMessageBox,
    QApplication,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QKeySequence, QIcon

from virtual_taylor_frame.model.frame import TaylorFrame
from virtual_taylor_frame.commands.history import UndoRedoManager
from virtual_taylor_frame.commands.block_commands import ClearAllCommand
from virtual_taylor_frame.accessibility.announcer import Announcer
from virtual_taylor_frame.accessibility.audio_cues import AudioCues
from virtual_taylor_frame.accessibility.ao3_engine import AO3Engine
from virtual_taylor_frame.model.types import VerbosityLevel
from virtual_taylor_frame.storage.tframe_format import (
    TFrameStorage,
    TFrameError,
)
from virtual_taylor_frame.storage.text_export import TextExporter
from virtual_taylor_frame.storage.json_export import JSONExporter
from virtual_taylor_frame.ui.frame_widget import TaylorFrameWidget
from virtual_taylor_frame.ui.dialogs.help_dialog import HelpDialog
from virtual_taylor_frame.ui.dialogs.goto_dialog import GoToDialog
from virtual_taylor_frame.ui.dialogs.new_frame_dialog import NewFrameDialog
from virtual_taylor_frame.ui.dialogs.inspect_dialog import InspectDialog


class MainWindow(QMainWindow):
    """
    Accessible PySide6 Main Window for Virtual Taylor Frame.
    """

    def __init__(
        self,
        frame: Optional[TaylorFrame] = None,
        announcer: Optional[Announcer] = None,
        audio_cues: Optional[AudioCues] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Virtual Taylor Frame")
        self.resize(1024, 768)
        self.setMinimumSize(640, 480)

        self.current_filepath: Optional[str] = None
        self.model: TaylorFrame = frame if frame is not None else TaylorFrame(20, 30)
        self.history: UndoRedoManager = UndoRedoManager()
        self.audio_cues: AudioCues = audio_cues if audio_cues is not None else AudioCues()
        self.announcer: Announcer = (
            announcer if announcer is not None else Announcer(AO3Engine())
        )

        # Build UI
        self._init_ui()
        self._create_actions()
        self._create_menus()
        self._create_status_bar()

        # Connect history and cursor updates
        self.history.add_listener(self._update_title_and_actions)
        self.frame_widget.cursor_changed.connect(self._on_cursor_changed)
        self.frame_widget.frame_modified.connect(self._update_status_bar)

        self._update_title_and_actions()
        self._update_status_bar()

        # Initial speech announcement
        self.announcer.output(
            f"Welcome to Virtual Taylor Frame. Board size: {self.model.rows} rows by {self.model.cols} columns. "
            f"Cursor at Row 1, Column 1. Press F1 for Help."
        )

    def _init_ui(self) -> None:
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAccessibleName("Taylor Frame Board View Area")

        self.frame_widget = TaylorFrameWidget(
            model=self.model,
            history=self.history,
            announcer=self.announcer,
            audio_cues=self.audio_cues,
            parent=self.scroll_area,
        )
        self.scroll_area.setWidget(self.frame_widget)
        self.setCentralWidget(self.scroll_area)
        self.frame_widget.setFocus()

    def _create_actions(self) -> None:
        # File Actions
        self.act_new = QAction("&New Frame...", self)
        self.act_new.setShortcut(QKeySequence("Ctrl+N"))
        self.act_new.setStatusTip("Create a new Taylor Frame with custom dimensions")
        self.act_new.triggered.connect(self._on_file_new)

        self.act_open = QAction("&Open...", self)
        self.act_open.setShortcut(QKeySequence("Ctrl+O"))
        self.act_open.setStatusTip("Open an existing .tframe file")
        self.act_open.triggered.connect(self._on_file_open)

        self.act_save = QAction("&Save", self)
        self.act_save.setShortcut(QKeySequence("Ctrl+S"))
        self.act_save.setStatusTip("Save current Taylor Frame")
        self.act_save.triggered.connect(self._on_file_save)

        self.act_save_as = QAction("Save &As...", self)
        self.act_save_as.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.act_save_as.setStatusTip("Save current Taylor Frame with a new filename")
        self.act_save_as.triggered.connect(self._on_file_save_as)

        self.act_export_txt = QAction("Export to Plain &Text (.txt)...", self)
        self.act_export_txt.setStatusTip("Export accessible ASCII/text representation")
        self.act_export_txt.triggered.connect(self._on_export_text)

        self.act_export_json = QAction("Export to &JSON (.json)...", self)
        self.act_export_json.setStatusTip("Export structured interchange JSON")
        self.act_export_json.triggered.connect(self._on_export_json)

        self.act_exit = QAction("E&xit", self)
        self.act_exit.setShortcut(QKeySequence("Ctrl+Q"))
        self.act_exit.triggered.connect(self.close)

        # Edit Actions
        self.act_undo = QAction("&Undo", self)
        self.act_undo.setShortcut(QKeySequence("Ctrl+Z"))
        self.act_undo.triggered.connect(self._on_undo)

        self.act_redo = QAction("&Redo", self)
        self.act_redo.setShortcut(QKeySequence("Ctrl+Y"))
        self.act_redo.triggered.connect(self._on_redo)

        self.act_cut = QAction("Cu&t", self)
        self.act_cut.setShortcut(QKeySequence("Ctrl+X"))
        self.act_cut.triggered.connect(self.frame_widget._cut_selection)

        self.act_copy = QAction("&Copy", self)
        self.act_copy.setShortcut(QKeySequence("Ctrl+C"))
        self.act_copy.triggered.connect(self.frame_widget._copy_selection)

        self.act_paste = QAction("&Paste", self)
        self.act_paste.setShortcut(QKeySequence("Ctrl+V"))
        self.act_paste.triggered.connect(self.frame_widget._paste_clipboard)

        self.act_clear_frame = QAction("Clear &All Objects...", self)
        self.act_clear_frame.setShortcut(QKeySequence("Ctrl+Shift+Delete"))
        self.act_clear_frame.triggered.connect(self._on_clear_frame)

        # Navigation Actions
        self.act_goto = QAction("&Go to Coordinate...", self)
        self.act_goto.setShortcut(QKeySequence("Ctrl+G"))
        self.act_goto.triggered.connect(self._on_goto)

        # Inspection Actions
        self.act_inspect_cell = QAction("Inspect &Current Socket", self)
        self.act_inspect_cell.setShortcut(QKeySequence("Space"))
        self.act_inspect_cell.triggered.connect(lambda: self.announcer.announce_cell_inspect(self.model.get_current_cell()))

        self.act_inspect_frame = QAction("Describe Entire &Frame Summary", self)
        self.act_inspect_frame.setShortcut(QKeySequence("F5"))
        self.act_inspect_frame.triggered.connect(lambda: self.announcer.announce_frame_summary(self.model))

        self.act_inspect_row = QAction("Read Current &Row Expression", self)
        self.act_inspect_row.setShortcut(QKeySequence("F6"))
        self.act_inspect_row.triggered.connect(lambda: self.announcer.announce_row(self.model.cursor_row, self.model))

        self.act_inspect_col = QAction("Read Current &Column Vertically", self)
        self.act_inspect_col.setShortcut(QKeySequence("F7"))
        self.act_inspect_col.triggered.connect(lambda: self.announcer.announce_column(self.model.cursor_col, self.model))

        self.act_inspect_neighbors = QAction("Read Surrounding &Neighbors", self)
        self.act_inspect_neighbors.setShortcut(QKeySequence("F8"))
        self.act_inspect_neighbors.triggered.connect(lambda: self.announcer.announce_neighbors(self.model.cursor_row, self.model.cursor_col, self.model))

        self.act_view_summary_dialog = QAction("Open &Summary Viewer...", self)
        self.act_view_summary_dialog.triggered.connect(self._on_view_summary_dialog)

        # Accessibility Actions
        self.act_cycle_verbosity = QAction("&Cycle Verbosity (Minimal / Normal / Detailed)", self)
        self.act_cycle_verbosity.setShortcut(QKeySequence("F2"))
        self.act_cycle_verbosity.triggered.connect(self._on_cycle_verbosity)

        self.act_toggle_sound = QAction("Enable Sound &Cues (Earcons)", self)
        self.act_toggle_sound.setCheckable(True)
        self.act_toggle_sound.setChecked(self.audio_cues.enabled)
        self.act_toggle_sound.triggered.connect(self._on_toggle_sound)

        # Help Actions
        self.act_help = QAction("&Keyboard Guide && Documentation", self)
        self.act_help.setShortcut(QKeySequence("F1"))
        self.act_help.triggered.connect(self._on_help)

        self.act_about = QAction("&About Virtual Taylor Frame", self)
        self.act_about.triggered.connect(self._on_about)

    def _create_menus(self) -> None:
        mb = self.menuBar()

        # File Menu
        menu_file = mb.addMenu("&File")
        menu_file.addAction(self.act_new)
        menu_file.addAction(self.act_open)
        menu_file.addAction(self.act_save)
        menu_file.addAction(self.act_save_as)
        menu_file.addSeparator()
        menu_file.addAction(self.act_export_txt)
        menu_file.addAction(self.act_export_json)
        menu_file.addSeparator()
        menu_file.addAction(self.act_exit)

        # Edit Menu
        menu_edit = mb.addMenu("&Edit")
        menu_edit.addAction(self.act_undo)
        menu_edit.addAction(self.act_redo)
        menu_edit.addSeparator()
        menu_edit.addAction(self.act_cut)
        menu_edit.addAction(self.act_copy)
        menu_edit.addAction(self.act_paste)
        menu_edit.addSeparator()
        menu_edit.addAction(self.act_clear_frame)

        # Navigate Menu
        menu_nav = mb.addMenu("&Navigate")
        menu_nav.addAction(self.act_goto)

        # Inspect Menu
        menu_inspect = mb.addMenu("&Inspect")
        menu_inspect.addAction(self.act_inspect_cell)
        menu_inspect.addAction(self.act_inspect_frame)
        menu_inspect.addAction(self.act_inspect_row)
        menu_inspect.addAction(self.act_inspect_col)
        menu_inspect.addAction(self.act_inspect_neighbors)
        menu_inspect.addSeparator()
        menu_inspect.addAction(self.act_view_summary_dialog)

        # Accessibility Menu
        menu_a11y = mb.addMenu("&Accessibility")
        menu_a11y.addAction(self.act_cycle_verbosity)
        menu_a11y.addAction(self.act_toggle_sound)
        menu_a11y.addSeparator()

        # Theme Submenu
        menu_themes = menu_a11y.addMenu("Visual Contrast &Themes")
        act_theme_dark = menu_themes.addAction("High Contrast &Dark (Recommended)")
        act_theme_dark.triggered.connect(lambda: self.frame_widget.set_theme("dark_high_contrast"))
        act_theme_light = menu_themes.addAction("High Contrast &Light")
        act_theme_light.triggered.connect(lambda: self.frame_widget.set_theme("light_high_contrast"))
        act_theme_classic = menu_themes.addAction("&Classic Metal Frame")
        act_theme_classic.triggered.connect(lambda: self.frame_widget.set_theme("classic_frame"))

        # Help Menu
        menu_help = mb.addMenu("&Help")
        menu_help.addAction(self.act_help)
        menu_help.addAction(self.act_about)

    def _create_status_bar(self) -> None:
        self.status = QStatusBar(self)
        self.setStatusBar(self.status)

        self.lbl_pos = QLabel("Row: 1, Col: 1", self)
        self.lbl_content = QLabel("Socket: Empty", self)
        self.lbl_verbosity = QLabel("Verbosity: Normal", self)
        self.lbl_engine = QLabel(f"Engine: {self.announcer.engine.name}", self)

        self.status.addWidget(self.lbl_pos, 1)
        self.status.addWidget(self.lbl_content, 2)
        self.status.addWidget(self.lbl_verbosity, 1)
        self.status.addWidget(self.lbl_engine, 1)

    def _on_cursor_changed(self, display_row: int, display_col: int) -> None:
        self._update_status_bar()

    def _update_status_bar(self) -> None:
        r, c = self.model.display_cursor_row, self.model.display_cursor_col
        self.lbl_pos.setText(f"Row: {r}, Col: {c}")

        cell = self.model.get_current_cell()
        if cell.is_occupied:
            self.lbl_content.setText(f"Content: {cell.peg.label} ({cell.peg.symbol})")
        else:
            self.lbl_content.setText("Content: Empty")

        self.lbl_verbosity.setText(f"Verbosity: {self.announcer.verbosity.value.capitalize()}")
        self.lbl_engine.setText(f"Engine: {self.announcer.engine.name}")

    def _update_title_and_actions(self) -> None:
        title = "Virtual Taylor Frame"
        file_part = Path(self.current_filepath).name if self.current_filepath else "Untitled"
        dirty_marker = " *" if self.history.is_dirty else ""
        self.setWindowTitle(f"{title} - [{file_part}{dirty_marker}]")

        self.act_undo.setEnabled(self.history.can_undo)
        if self.history.undo_action_name:
            self.act_undo.setText(f"&Undo ({self.history.undo_action_name})")
        else:
            self.act_undo.setText("&Undo")

        self.act_redo.setEnabled(self.history.can_redo)
        if self.history.redo_action_name:
            self.act_redo.setText(f"&Redo ({self.history.redo_action_name})")
        else:
            self.act_redo.setText("&Redo")

    # --- File Operations ---

    def _maybe_save_dirty(self) -> bool:
        if not self.history.is_dirty:
            return True
        res = QMessageBox.question(
            self,
            "Unsaved Changes",
            "Do you want to save changes to the current Taylor Frame?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
        )
        if res == QMessageBox.StandardButton.Save:
            return self._on_file_save()
        elif res == QMessageBox.StandardButton.Cancel:
            return False
        return True

    def _on_file_new(self) -> None:
        if not self._maybe_save_dirty():
            return
        dlg = NewFrameDialog(self.model.rows, self.model.cols, self)
        if dlg.exec():
            rows, cols = dlg.get_dimensions()
            new_model = TaylorFrame(rows=rows, cols=cols)
            self.model = new_model
            self.history.clear()
            self.current_filepath = None
            self.frame_widget.set_model(new_model)
            self._update_title_and_actions()
            self._update_status_bar()
            self.announcer.output(f"Created new Taylor Frame with {rows} rows by {cols} columns.")

    def _on_file_open(self) -> None:
        if not self._maybe_save_dirty():
            return
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Open Taylor Frame",
            "",
            "Taylor Frame Files (*.tframe);;All Files (*)",
        )
        if not filepath:
            return

        try:
            loaded_frame, meta = TFrameStorage.load(filepath)
            self.model = loaded_frame
            self.history.clear()
            self.current_filepath = filepath
            self.frame_widget.set_model(loaded_frame)
            self._update_title_and_actions()
            self._update_status_bar()
            obj_cnt = loaded_frame.count_occupied()
            self.announcer.output(
                f"Loaded {Path(filepath).name}. Frame size: {loaded_frame.rows} rows by {loaded_frame.cols} columns. "
                f"{obj_cnt} objects present."
            )
        except TFrameError as e:
            QMessageBox.critical(self, "Error Opening File", str(e))
            self.announcer.output(f"Error opening file: {e}")

    def _on_file_save(self) -> bool:
        if not self.current_filepath:
            return self._on_file_save_as()
        try:
            TFrameStorage.save(self.current_filepath, self.model)
            self.history.mark_clean()
            self._update_title_and_actions()
            self.announcer.output(f"Saved {Path(self.current_filepath).name}.")
            return True
        except TFrameError as e:
            QMessageBox.critical(self, "Save Error", str(e))
            self.announcer.output(f"Error saving file: {e}")
            return False

    def _on_file_save_as(self) -> bool:
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Taylor Frame As",
            self.current_filepath or "my-maths.tframe",
            "Taylor Frame Files (*.tframe);;All Files (*)",
        )
        if not filepath:
            return False
        if not filepath.endswith(".tframe"):
            filepath += ".tframe"
        self.current_filepath = filepath
        return self._on_file_save()

    def _on_export_text(self) -> None:
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Plain Text",
            "taylor_frame_export.txt",
            "Plain Text Files (*.txt);;All Files (*)",
        )
        if not filepath:
            return
        try:
            content = TextExporter.export_text(self.model)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            self.announcer.output(f"Exported plain text to {Path(filepath).name}.")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def _on_export_json(self) -> None:
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export JSON",
            "taylor_frame_export.json",
            "JSON Files (*.json);;All Files (*)",
        )
        if not filepath:
            return
        try:
            content = JSONExporter.export_json(self.model)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            self.announcer.output(f"Exported JSON to {Path(filepath).name}.")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    # --- Edit Commands ---

    def _on_undo(self) -> None:
        success, msg = self.history.undo(self.model, self.announcer.verbosity)
        self.announcer.output(msg)
        self.frame_widget.update()

    def _on_redo(self) -> None:
        success, msg = self.history.redo(self.model, self.announcer.verbosity)
        self.announcer.output(msg)
        self.frame_widget.update()

    def _on_clear_frame(self) -> None:
        res = QMessageBox.warning(
            self,
            "Clear Entire Frame",
            "Are you sure you want to clear all objects from the Taylor Frame?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if res == QMessageBox.StandardButton.Yes:
            cmd = ClearAllCommand()
            success, msg = self.history.execute_command(cmd, self.model, self.announcer.verbosity)
            self.audio_cues.play_clear()
            self.announcer.output(msg)
            self.frame_widget.update()

    def _on_goto(self) -> None:
        dlg = GoToDialog(
            self.model.cursor_row,
            self.model.cursor_col,
            self.model.rows,
            self.model.cols,
            self,
        )
        if dlg.exec():
            r, c = dlg.get_coordinates()
            self.frame_widget._navigate_to(r, c, direction="Go To", is_jump=True)

    def _on_view_summary_dialog(self) -> None:
        summary = self.model.summarize_frame()
        dlg = InspectDialog(summary, self)
        dlg.exec()

    def _on_cycle_verbosity(self) -> None:
        self.announcer.cycle_verbosity()
        self._update_status_bar()

    def _on_toggle_sound(self, checked: bool) -> None:
        self.audio_cues.enabled = checked
        status = "enabled" if checked else "disabled"
        self.announcer.output(f"Audio cues {status}.")

    def _on_help(self) -> None:
        dlg = HelpDialog(self)
        dlg.exec()

    def _on_about(self) -> None:
        QMessageBox.about(
            self,
            "About Virtual Taylor Frame",
            "<h3>Virtual Taylor Frame</h3>"
            "<p>Version 1.0.0</p>"
            "<p>A fully accessible digital emulation of the physical Taylor Frame "
            "designed for blind and visually impaired mathematics students.</p>"
            "<p>Supports keyboard-first interaction, Accessible Output 3 (AO3), "
            "and native .tframe mathematical files.</p>",
        )

    def closeEvent(self, event) -> None:
        if self._maybe_save_dirty():
            event.accept()
        else:
            event.ignore()
