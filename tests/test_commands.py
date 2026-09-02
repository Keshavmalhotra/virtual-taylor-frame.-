"""
Unit tests for command execution, undo, redo, and history management.
"""
import pytest
from virtual_taylor_frame.model import (
    TaylorFrame,
    TaylorPeg,
    SelectionRange,
    ClipboardBlock,
    VerbosityLevel,
)
from virtual_taylor_frame.commands import (
    PlacePegCommand,
    RemovePegCommand,
    RotatePegCommand,
    FlipPegCommand,
    ToggleTypeCommand,
    MovePegCommand,
    ClearRowCommand,
    ClearRegionCommand,
    ClearAllCommand,
    PasteBlockCommand,
    UndoRedoManager,
)


class TestCommands:
    def test_place_and_undo(self):
        frame = TaylorFrame(10, 10)
        history = UndoRedoManager()
        peg = TaylorPeg.from_symbol("7")

        cmd = PlacePegCommand(3, 4, peg)
        success, msg = history.execute_command(cmd, frame)
        assert success is True
        assert frame.get_cell(3, 4).is_occupied is True
        assert frame.get_cell(3, 4).peg.symbol == "7"
        assert "7" in msg
        assert history.can_undo is True
        assert history.is_dirty is True

        # Undo
        success, undo_msg = history.undo(frame)
        assert success is True
        assert frame.get_cell(3, 4).is_occupied is False
        assert history.can_undo is False
        assert history.can_redo is True

        # Redo
        success, redo_msg = history.redo(frame)
        assert success is True
        assert frame.get_cell(3, 4).is_occupied is True
        assert frame.get_cell(3, 4).peg.symbol == "7"

    def test_remove_and_undo(self):
        frame = TaylorFrame(10, 10)
        history = UndoRedoManager()
        frame.place_peg(2, 2, TaylorPeg.from_symbol("+"))

        cmd = RemovePegCommand(2, 2)
        success, msg = history.execute_command(cmd, frame)
        assert success is True
        assert frame.get_cell(2, 2).is_occupied is False
        assert "Removed" in msg

        history.undo(frame)
        assert frame.get_cell(2, 2).is_occupied is True
        assert frame.get_cell(2, 2).peg.symbol == "+"

    def test_rotate_and_undo(self):
        frame = TaylorFrame(10, 10)
        history = UndoRedoManager()
        # Digit 1 is North (0°)
        frame.place_peg(1, 1, TaylorPeg.from_symbol("1"))

        # Rotate clockwise -> Digit 2 (45°)
        cmd = RotatePegCommand(1, 1, clockwise=True)
        success, msg = history.execute_command(cmd, frame)
        assert success is True
        assert frame.get_cell(1, 1).peg.symbol == "2"

        history.undo(frame)
        assert frame.get_cell(1, 1).peg.symbol == "1"

    def test_flip_and_undo(self):
        frame = TaylorFrame(10, 10)
        history = UndoRedoManager()
        # Digit 1 (End A, 0°) -> Flip to Digit 9 (End B, 0°)
        frame.place_peg(1, 1, TaylorPeg.from_symbol("1"))

        cmd = FlipPegCommand(1, 1)
        success, msg = history.execute_command(cmd, frame)
        assert success is True
        assert frame.get_cell(1, 1).peg.symbol == "9"

        history.undo(frame)
        assert frame.get_cell(1, 1).peg.symbol == "1"

    def test_move_peg_and_undo(self):
        frame = TaylorFrame(10, 10)
        history = UndoRedoManager()
        frame.place_peg(0, 0, TaylorPeg.from_symbol("5"))

        cmd = MovePegCommand(0, 0, 3, 3)
        success, msg = history.execute_command(cmd, frame)
        assert success is True
        assert frame.get_cell(0, 0).is_occupied is False
        assert frame.get_cell(3, 3).peg.symbol == "5"

        history.undo(frame)
        assert frame.get_cell(0, 0).peg.symbol == "5"
        assert frame.get_cell(3, 3).is_occupied is False

    def test_clear_row_and_undo(self):
        frame = TaylorFrame(10, 10)
        history = UndoRedoManager()
        frame.place_peg(2, 0, TaylorPeg.from_symbol("1"))
        frame.place_peg(2, 1, TaylorPeg.from_symbol("2"))
        frame.place_peg(2, 2, TaylorPeg.from_symbol("3"))

        cmd = ClearRowCommand(2)
        success, msg = history.execute_command(cmd, frame)
        assert success is True
        assert frame.count_occupied() == 0

        history.undo(frame)
        assert frame.count_occupied() == 3
        assert frame.get_cell(2, 0).peg.symbol == "1"
        assert frame.get_cell(2, 1).peg.symbol == "2"
        assert frame.get_cell(2, 2).peg.symbol == "3"

    def test_clear_region_and_undo(self):
        frame = TaylorFrame(10, 10)
        history = UndoRedoManager()
        frame.place_peg(1, 1, TaylorPeg.from_symbol("1"))
        frame.place_peg(1, 2, TaylorPeg.from_symbol("2"))
        frame.place_peg(5, 5, TaylorPeg.from_symbol("9"))  # Outside region

        sel = SelectionRange(start_row=1, start_col=1, end_row=2, end_col=2)
        cmd = ClearRegionCommand(sel)
        success, msg = history.execute_command(cmd, frame)
        assert success is True
        assert frame.count_occupied() == 1
        assert frame.get_cell(5, 5).is_occupied is True

        history.undo(frame)
        assert frame.count_occupied() == 3

    def test_paste_block_and_undo(self):
        frame = TaylorFrame(10, 10)
        history = UndoRedoManager()
        block = ClipboardBlock(
            num_rows=1,
            num_cols=3,
            grid=[[
                TaylorPeg.from_symbol("7"),
                TaylorPeg.from_symbol("+"),
                TaylorPeg.from_symbol("3"),
            ]]
        )

        cmd = PasteBlockCommand(target_row=4, target_col=2, block=block)
        success, msg = history.execute_command(cmd, frame)
        assert success is True
        assert frame.get_cell(4, 2).peg.symbol == "7"
        assert frame.get_cell(4, 3).peg.symbol == "+"
        assert frame.get_cell(4, 4).peg.symbol == "3"

        history.undo(frame)
        assert frame.count_occupied() == 0
