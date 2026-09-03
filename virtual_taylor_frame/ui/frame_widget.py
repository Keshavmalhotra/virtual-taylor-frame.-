"""
Interactive Taylor Frame visual QWidget with full keyboard accessibility,
vector rendering, selection handling, and event integration.
"""
from typing import Optional, Dict, Any, Tuple
from PySide6.QtWidgets import QWidget, QSizePolicy, QInputDialog
from PySide6.QtCore import Qt, QRectF, QPointF, QSize, Signal
from PySide6.QtGui import (
    QPainter,
    QPen,
    QBrush,
    QColor,
    QFont,
    QKeyEvent,
    QMouseEvent,
    QPaintEvent,
)

from virtual_taylor_frame.model.frame import TaylorFrame
from virtual_taylor_frame.model.peg import TaylorPeg
from virtual_taylor_frame.model.selection import SelectionRange, ClipboardBlock
from virtual_taylor_frame.model.types import (
    PegOrientation,
    PegEnd,
    PegType,
    VerbosityLevel,
    SYMBOL_TO_PEG,
    SYMBOL_ALIASES,
)
from virtual_taylor_frame.commands.history import UndoRedoManager
from virtual_taylor_frame.commands.peg_commands import (
    PlacePegCommand,
    RemovePegCommand,
    RotatePegCommand,
    FlipPegCommand,
    ToggleTypeCommand,
)
from virtual_taylor_frame.commands.block_commands import (
    ClearRowCommand,
    ClearRegionCommand,
    PasteBlockCommand,
    MoveSelectionCommand,
)
from virtual_taylor_frame.accessibility.announcer import Announcer
from virtual_taylor_frame.accessibility.audio_cues import AudioCues
from virtual_taylor_frame.ui.themes import THEMES, ThemeColors
from virtual_taylor_frame.ui.peg_renderer import PegRenderer


class TaylorFrameWidget(QWidget):
    """
    Main interactive grid canvas displaying the Taylor Frame.
    """

    cursor_changed = Signal(int, int)  # 1-based display row, col
    frame_modified = Signal()

    def __init__(
        self,
        model: TaylorFrame,
        history: UndoRedoManager,
        announcer: Announcer,
        audio_cues: AudioCues,
        parent=None,
    ):
        super().__init__(parent)
        self.auto_advance = True
        # When regions overlap, the first region in model.regions wins.  This
        # is deterministic and preserves the order in which regions are loaded/created.
        self.announce_named_regions = True
        self.model: TaylorFrame = model
        self.history: UndoRedoManager = history
        self.announcer: Announcer = announcer
        self.audio_cues: AudioCues = audio_cues
        self.theme: ThemeColors = THEMES["dark_high_contrast"]

        self.clipboard: Optional[ClipboardBlock] = None
        self._selection_anchor: Optional[Tuple[int, int]] = None

        # Visual layout metrics
        self.cell_size: int = 56
        self.margin_left: int = 40
        self.margin_top: int = 40
        self.margin_right: int = 20
        self.margin_bottom: int = 20

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAccessibleName("Taylor Frame Grid Canvas")
        self._update_accessible_info()

        # Connect model listener
        self.model.add_listener(self._on_model_event)

    def set_model(self, new_model: TaylorFrame) -> None:
        """Switch to a new Taylor Frame model."""
        self.model.remove_listener(self._on_model_event)
        self.model = new_model
        self.model.add_listener(self._on_model_event)
        self.updateGeometry()
        self.update()
        self._update_accessible_info()
        self.cursor_changed.emit(self.model.display_cursor_row, self.model.display_cursor_col)

    def set_theme(self, theme_key: str) -> None:
        if theme_key in THEMES:
            self.theme = THEMES[theme_key]
            self.update()

    def _on_model_event(self, event_name: str, kwargs: Dict[str, Any]) -> None:
        self.update()
        self.frame_modified.emit()
        self._update_accessible_info()

    def _update_accessible_info(self) -> None:
        cell = self.model.get_current_cell()
        desc = cell.describe(self.announcer.verbosity, include_coords=True)
        self.setAccessibleDescription(
            f"{desc} Frame size: {self.model.rows} rows by {self.model.cols} columns."
        )

    # --- Sizing & Coordinate Mapping ---

    def sizeHint(self) -> QSize:
        w = self.margin_left + self.margin_right + self.model.cols * self.cell_size
        h = self.margin_top + self.margin_bottom + self.model.rows * self.cell_size
        return QSize(w, h)

    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()

    def cell_rect(self, row: int, col: int) -> QRectF:
        x = self.margin_left + col * self.cell_size
        y = self.margin_top + row * self.cell_size
        return QRectF(x, y, self.cell_size, self.cell_size)

    def coord_at_pos(self, x: float, y: float) -> Optional[Tuple[int, int]]:
        col = int((x - self.margin_left) // self.cell_size)
        row = int((y - self.margin_top) // self.cell_size)
        if 0 <= row < self.model.rows and 0 <= col < self.model.cols:
            return row, col
        return None

    # --- Painting ---

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # 1. Background
        painter.fillRect(self.rect(), self.theme.background)

        # 2. Board Background
        board_rect = QRectF(
            self.margin_left - 4,
            self.margin_top - 4,
            self.model.cols * self.cell_size + 8,
            self.model.rows * self.cell_size + 8,
        )
        painter.fillRect(board_rect, self.theme.board_background)
        painter.setPen(QPen(self.theme.socket_border, 2))
        painter.drawRect(board_rect)

        # 3. Draw Header Margins (Row numbers & Column numbers)
        painter.setPen(QPen(self.theme.grid_label_color))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))

        # Column headers (top)
        for c in range(self.model.cols):
            x = self.margin_left + c * self.cell_size
            rect = QRectF(x, 0, self.cell_size, self.margin_top - 6)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(c + 1))

        # Row headers (left)
        for r in range(self.model.rows):
            y = self.margin_top + r * self.cell_size
            rect = QRectF(0, y, self.margin_left - 6, self.cell_size)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(r + 1))

        # 4. Selection Highlight
        selection = self.model.selection
        if selection is not None:
            sel_rect = QRectF(
                self.margin_left + selection.min_col * self.cell_size,
                self.margin_top + selection.min_row * self.cell_size,
                selection.num_cols * self.cell_size,
                selection.num_rows * self.cell_size,
            )
            painter.fillRect(sel_rect, self.theme.selection_fill)
            painter.setPen(QPen(self.theme.selection_border, 2.0, Qt.PenStyle.DashLine))
            painter.drawRect(sel_rect)

        # 5. Draw Sockets and Pegs
        for r in range(self.model.rows):
            for c in range(self.model.cols):
                rect = self.cell_rect(r, c)
                # Socket
                PegRenderer.draw_socket(painter, rect, self.theme)
                # Peg if occupied
                cell = self.model.get_cell(r, c)
                if cell.is_occupied:
                    PegRenderer.draw_peg(painter, rect, cell.peg, self.theme)

        # 6. Cursor Box
        cur_r, cur_c = self.model.cursor_row, self.model.cursor_col
        cur_rect = self.cell_rect(cur_r, cur_c)
        painter.fillRect(cur_rect, self.theme.cursor_fill)
        painter.setPen(QPen(self.theme.cursor_border, 3.0))
        painter.drawRect(cur_rect.adjusted(2, 2, -2, -2))

        # 7. Focus Border
        if self.hasFocus():
            painter.setPen(QPen(self.theme.cursor_border, 1.5, Qt.PenStyle.DotLine))
            painter.drawRect(cur_rect.adjusted(4, 4, -4, -4))

    # --- Mouse Support ---

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            coord = self.coord_at_pos(event.position().x(), event.position().y())
            if coord:
                r, c = coord
                self._selection_anchor = (r, c)
                self.model.clear_selection()
                self._navigate_to(r, c, direction="Click")

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._selection_anchor is not None:
            coord = self.coord_at_pos(event.position().x(), event.position().y())
            if coord:
                r, c = coord
                ar, ac = self._selection_anchor
                sel = SelectionRange(ar, ac, r, c)
                self.model.set_selection(sel)
                self.model.set_cursor(r, c)
                self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            if self.model.selection:
                self.announcer.announce_selection(self.model.selection)
            self._selection_anchor = None

    # --- Keyboard Navigation & Editing ---

    def _region_at(self, row: int, col: int):
        """Return the first named region containing a logical cell."""
        return next(
            (region for region in self.model.regions
             if region.start_row <= row <= region.end_row
             and region.start_col <= col <= region.end_col),
            None,
        )

    def _navigate_to(
        self,
        r: int,
        c: int,
        direction: str = "",
        is_jump: bool = False,
    ) -> None:
        old_r, old_c = self.model.cursor_row, self.model.cursor_col
        moved = self.model.set_cursor(r, c)
        if moved or direction == "Click":
            cell = self.model.get_current_cell()
            old_region = self._region_at(old_r, old_c)
            new_region = self._region_at(cell.row, cell.col)
            entered_region = None
            if (moved and self.announce_named_regions and new_region is not None
                    and (old_region is None or old_region is not new_region)):
                entered_region = new_region.name
            self.announcer.announce_navigation(
                direction=direction,
                display_row=cell.display_row,
                display_col=cell.display_col,
                cell=cell,
                is_jump=is_jump,
                entered_region=entered_region,
            )
            self.cursor_changed.emit(cell.display_row, cell.display_col)
            self.update()
        else:
            self.audio_cues.play_boundary()
            boundary = f"Edge ({direction})" if direction else "Edge"
            self.announcer.announce_boundary(boundary)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        modifiers = event.modifiers()
        has_ctrl = bool(modifiers & Qt.KeyboardModifier.ControlModifier)
        has_shift = bool(modifiers & Qt.KeyboardModifier.ShiftModifier)

        # Meaningful mathematical navigation (Ctrl+Alt, leaving existing keys intact).
        if has_ctrl and bool(modifiers & Qt.KeyboardModifier.AltModifier):
            if key == Qt.Key.Key_R and self.model.selection:
                name, ok = QInputDialog.getText(self, "Create Named Region", "Region name:")
                if ok and name.strip():
                    s = self.model.selection
                    try:
                        region = self.model.create_region(name.strip(), s.start_row, s.start_col, s.end_row, s.end_col)
                        self.announcer.announce_region(self.model, region)
                    except ValueError as exc: self.announcer.output(str(exc))
                return
            if key in (Qt.Key.Key_G, Qt.Key.Key_M):
                if key == Qt.Key.Key_G:
                    moved = self.model.jump_region(not has_shift)
                    if moved:
                        region = self._region_at(self.model.cursor_row, self.model.cursor_col)
                        self.announcer.announce_region(self.model, region)
                    else: self.announcer.output("No named regions.")
                else:
                    current = self._region_at(self.model.cursor_row, self.model.cursor_col)
                    self.announcer.announce_region(self.model, current) if current else self.announcer.output("Cursor is not in a named region.")
                return
            nav = {Qt.Key.Key_T:("number",True), Qt.Key.Key_P:("number",False),
                   Qt.Key.Key_O:("operator",True), Qt.Key.Key_I:("operator",False),
                   Qt.Key.Key_E:("expression",True), Qt.Key.Key_W:("expression",False)}
            if key in nav:
                kind, forward = nav[key]
                if self.model.jump_math_object(kind, forward): self.announcer.announce_math_destination(self.model, kind)
                else: self.announcer.output(f"No {'next' if forward else 'previous'} {kind}.")
                self.update(); return
            if key in (Qt.Key.Key_H, Qt.Key.Key_J):
                if self.model.expression_boundary(key == Qt.Key.Key_H): self.announcer.announce_math_destination(self.model, "expression")
                else: self.announcer.output("No current expression.")
                self.update(); return

        # 1. Navigation with Arrow Keys
        if key in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right):
            dr, dc, dir_name = 0, 0, ""
            if key == Qt.Key.Key_Up:
                dr, dir_name = -1, "Up"
            elif key == Qt.Key.Key_Down:
                dr, dir_name = 1, "Down"
            elif key == Qt.Key.Key_Left:
                dc, dir_name = -1, "Left"
            elif key == Qt.Key.Key_Right:
                dc, dir_name = 1, "Right"

            # With a selection, arrows manipulate the mathematical structure.
            # Unmodified arrows retain their original cursor-navigation behavior
            # when no selection is active.
            if self.model.selection and not has_shift and not has_ctrl:
                cmd = MoveSelectionCommand(self.model.selection, dr, dc)
                success, msg = self.history.execute_command(
                    cmd, self.model, self.announcer.verbosity
                )
                self.announcer.output(msg)
                self.update()
                return

            if has_shift:
                # Expand selection
                if not self.model.selection:
                    self._selection_anchor = (self.model.cursor_row, self.model.cursor_col)
                target_r = max(0, min(self.model.rows - 1, self.model.cursor_row + dr))
                target_c = max(0, min(self.model.cols - 1, self.model.cursor_col + dc))
                ar, ac = self._selection_anchor or (self.model.cursor_row, self.model.cursor_col)
                sel = SelectionRange(ar, ac, target_r, target_c)
                self.model.set_selection(sel)
                self._navigate_to(target_r, target_c)
                self.announcer.announce_selection(sel)
                return

            if has_ctrl:
                # Jump to next occupied peg
                jumped = self.model.jump_to_next_occupied(dr, dc)
                if jumped:
                    cell = self.model.get_current_cell()
                    self.announcer.announce_navigation(
                        direction=dir_name,
                        display_row=cell.display_row,
                        display_col=cell.display_col,
                        cell=cell,
                        is_jump=True,
                    )
                    self.cursor_changed.emit(cell.display_row, cell.display_col)
                    self.update()
                else:
                    self.audio_cues.play_boundary()
                    self.announcer.output(f"No occupied objects in {dir_name} direction.")
                return

            # Normal single-cell navigation
            self.model.clear_selection()
            self._selection_anchor = None
            self._navigate_to(
                self.model.cursor_row + dr,
                self.model.cursor_col + dc,
            )
            return

        # 2. Home / End
        if key == Qt.Key.Key_Home:
            self.model.clear_selection()
            if has_ctrl:
                self._navigate_to(0, 0, direction="Top-Left (Row 1, Column 1)", is_jump=True)
            else:
                self._navigate_to(self.model.cursor_row, 0, direction="Start of row", is_jump=True)
            return

        if key == Qt.Key.Key_End:
            self.model.clear_selection()
            if has_ctrl:
                # Bottom-right
                self._navigate_to(self.model.rows - 1, self.model.cols - 1, direction="Bottom-Right", is_jump=True)
            else:
                self._navigate_to(self.model.cursor_row, self.model.cols - 1, direction="End of row", is_jump=True)
            return

        # 3. Page Up / Page Down (Jump 5 rows)
        if key == Qt.Key.Key_PageUp:
            self.model.clear_selection()
            self._navigate_to(max(0, self.model.cursor_row - 5), self.model.cursor_col, direction="Page Up", is_jump=True)
            return

        if key == Qt.Key.Key_PageDown:
            self.model.clear_selection()
            self._navigate_to(min(self.model.rows - 1, self.model.cursor_row + 5), self.model.cursor_col, direction="Page Down", is_jump=True)
            return

        # 4. Inspection Shortcuts
        if key == Qt.Key.Key_Space:
            self.announcer.announce_cell_inspect(self.model.get_current_cell())
            return

        if key == Qt.Key.Key_F5:
            if has_shift:
                self.announcer.announce_row(self.model.cursor_row, self.model)
            elif has_ctrl:
                self.announcer.announce_column(self.model.cursor_col, self.model)
            else:
                self.announcer.announce_frame_summary(self.model)
            return

        if key == Qt.Key.Key_F6:
            self.announcer.announce_row(self.model.cursor_row, self.model)
            return

        if key == Qt.Key.Key_F7:
            self.announcer.announce_column(self.model.cursor_col, self.model)
            return

        if key == Qt.Key.Key_F8:
            self.announcer.announce_neighbors(self.model.cursor_row, self.model.cursor_col, self.model)
            return

        if key == Qt.Key.Key_F2 or (key == Qt.Key.Key_V and not has_ctrl):
            self.announcer.cycle_verbosity()
            return

        # 5. Undo / Redo
        if has_ctrl and key == Qt.Key.Key_Z:
            if has_shift:
                success, msg = self.history.redo(self.model, self.announcer.verbosity)
            else:
                success, msg = self.history.undo(self.model, self.announcer.verbosity)
            self.announcer.output(msg)
            self.update()
            return

        if has_ctrl and key == Qt.Key.Key_Y:
            success, msg = self.history.redo(self.model, self.announcer.verbosity)
            self.announcer.output(msg)
            self.update()
            return

        # 6. Clipboard (Copy / Cut / Paste)
        if has_ctrl and key == Qt.Key.Key_C:
            self._copy_selection()
            return

        if has_ctrl and key == Qt.Key.Key_X:
            self._cut_selection()
            return

        if has_ctrl and key == Qt.Key.Key_V:
            self._paste_clipboard()
            return

        if has_ctrl and key == Qt.Key.Key_A:
            self.model.set_selection(SelectionRange(0, 0, self.model.rows - 1, self.model.cols - 1))
            self.announcer.announce_selection(self.model.selection)
            self.update()
            return

        if key == Qt.Key.Key_Escape:
            if self.model.selection:
                self.model.clear_selection()
                self.announcer.output("Selection cleared.")
                self.update()
            return

        # 7. Peg Deletion
        if key in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            if has_shift:
                # Clear current row
                cmd = ClearRowCommand(self.model.cursor_row)
                success, msg = self.history.execute_command(cmd, self.model, self.announcer.verbosity)
                self.audio_cues.play_remove()
                self.announcer.output(msg)
                self.update()
            elif self.model.selection:
                # Clear selection
                cmd = ClearRegionCommand(self.model.selection)
                success, msg = self.history.execute_command(cmd, self.model, self.announcer.verbosity)
                self.audio_cues.play_remove()
                self.announcer.output(msg)
                self.model.clear_selection()
                self.update()
            else:
                # Delete single peg
                cmd = RemovePegCommand(self.model.cursor_row, self.model.cursor_col)
                success, msg = self.history.execute_command(cmd, self.model, self.announcer.verbosity)
                if success:
                    self.audio_cues.play_remove()
                self.announcer.output(msg)
                self.update()
            return

        # 8. Tactile Peg Manipulation (Rotate, Flip, Toggle)
        if key in (Qt.Key.Key_R, Qt.Key.Key_BracketRight, Qt.Key.Key_BracketLeft):
            clockwise = not has_shift and key != Qt.Key.Key_BracketLeft
            cmd = RotatePegCommand(self.model.cursor_row, self.model.cursor_col, clockwise=clockwise)
            success, msg = self.history.execute_command(cmd, self.model, self.announcer.verbosity)
            self.announcer.output(msg)
            self.update()
            return

        if key == Qt.Key.Key_F and not has_ctrl:
            cmd = FlipPegCommand(self.model.cursor_row, self.model.cursor_col)
            success, msg = self.history.execute_command(cmd, self.model, self.announcer.verbosity)
            self.announcer.output(msg)
            self.update()
            return

        if key == Qt.Key.Key_T and not has_ctrl:
            cmd = ToggleTypeCommand(self.model.cursor_row, self.model.cursor_col)
            success, msg = self.history.execute_command(cmd, self.model, self.announcer.verbosity)
            self.announcer.output(msg)
            self.update()
            return

        # 9. Direct Mathematical Character Typing (0-9, +, -, *, /, =, ., a-z, etc.)
        text = event.text()
        if text and len(text) == 1 and not has_ctrl:
            peg = TaylorPeg.from_symbol(text)
            if peg is not None:
                cmd = PlacePegCommand(self.model.cursor_row, self.model.cursor_col, peg)
                success, msg = self.history.execute_command(cmd, self.model, self.announcer.verbosity)
                self.audio_cues.play_place()
                self.announcer.output(msg)
                # Auto-advance cursor right if not at right edge
                if self.auto_advance and self.model.cursor_col < self.model.cols - 1:
                    self.model.move_cursor(0, 1)
                    self.cursor_changed.emit(self.model.display_cursor_row, self.model.display_cursor_col)
                self.update()
                return

        super().keyPressEvent(event)

    # --- Clipboard Helpers ---

    def _copy_selection(self) -> None:
        sel = self.model.selection
        if not sel:
            # Copy single cell
            sel = SelectionRange(
                self.model.cursor_row,
                self.model.cursor_col,
                self.model.cursor_row,
                self.model.cursor_col,
            )
        self.clipboard = ClipboardBlock.from_region(sel, lambda r, c: self.model.get_cell(r, c).peg)
        count = self.clipboard.count_pegs()
        self.announcer.output(f"Copied {count} object{'s' if count > 1 else ''}.")

    def _cut_selection(self) -> None:
        self._copy_selection()
        if self.model.selection:
            cmd = ClearRegionCommand(self.model.selection)
            self.history.execute_command(cmd, self.model, self.announcer.verbosity)
            self.model.clear_selection()
        else:
            cmd = RemovePegCommand(self.model.cursor_row, self.model.cursor_col)
            self.history.execute_command(cmd, self.model, self.announcer.verbosity)
        self.audio_cues.play_remove()
        self.update()

    def _paste_clipboard(self) -> None:
        if not self.clipboard:
            self.announcer.output("Clipboard is empty.")
            return
        cmd = PasteBlockCommand(self.model.cursor_row, self.model.cursor_col, self.clipboard)
        success, msg = self.history.execute_command(cmd, self.model, self.announcer.verbosity)
        self.audio_cues.play_place()
        self.announcer.output(msg)
        self.update()
