"""
Block and multi-cell commands for Taylor Frame operations.
"""
from typing import List, Tuple, Optional, Dict, Any

from virtual_taylor_frame.commands.base import Command
from virtual_taylor_frame.model.frame import TaylorFrame
from virtual_taylor_frame.model.peg import TaylorPeg
from virtual_taylor_frame.model.selection import SelectionRange, ClipboardBlock
from virtual_taylor_frame.model.types import VerbosityLevel


class ClearRowCommand(Command):
    """Clears all pegs in a specific row."""

    def __init__(self, row: int):
        self.row = row
        self.cleared_pegs: List[Tuple[int, int, TaylorPeg]] = []

    @property
    def name(self) -> str:
        return f"Clear Row {self.row + 1}"

    def execute(self, frame: TaylorFrame) -> bool:
        self.cleared_pegs = frame.clear_row(self.row)
        return len(self.cleared_pegs) > 0

    def undo(self, frame: TaylorFrame) -> bool:
        for r, c, peg in self.cleared_pegs:
            frame.place_peg(r, c, peg)
        frame.set_cursor(self.row, 0)
        return True

    def get_announcement(self, frame: TaylorFrame, verbosity: VerbosityLevel) -> str:
        count = len(self.cleared_pegs)
        if count == 0:
            return f"Row {self.row + 1} was already empty."
        return f"Cleared {count} object{'s' if count > 1 else ''} from Row {self.row + 1}."


class ClearRegionCommand(Command):
    """Clears all pegs within a selection rectangle."""

    def __init__(self, selection: SelectionRange):
        self.selection = selection
        self.cleared_pegs: List[Tuple[int, int, TaylorPeg]] = []

    @property
    def name(self) -> str:
        return "Clear Selection"

    def execute(self, frame: TaylorFrame) -> bool:
        self.cleared_pegs = []
        for r in range(self.selection.min_row, self.selection.max_row + 1):
            for c in range(self.selection.min_col, self.selection.max_col + 1):
                cell = frame.get_cell(r, c)
                if cell.is_occupied:
                    old_peg = frame.remove_peg(r, c)
                    if old_peg:
                        self.cleared_pegs.append((r, c, old_peg))
        return len(self.cleared_pegs) > 0

    def undo(self, frame: TaylorFrame) -> bool:
        for r, c, peg in self.cleared_pegs:
            frame.place_peg(r, c, peg)
        frame.set_selection(self.selection)
        return True

    def get_announcement(self, frame: TaylorFrame, verbosity: VerbosityLevel) -> str:
        count = len(self.cleared_pegs)
        if count == 0:
            return "Selected region was already empty."
        return f"Cleared {count} object{'s' if count > 1 else ''} from selected region."


class ClearAllCommand(Command):
    """Clears the entire frame."""

    def __init__(self):
        self.cleared_pegs: List[Tuple[int, int, TaylorPeg]] = []

    @property
    def name(self) -> str:
        return "Clear Frame"

    def execute(self, frame: TaylorFrame) -> bool:
        self.cleared_pegs = frame.clear_all()
        return len(self.cleared_pegs) > 0

    def undo(self, frame: TaylorFrame) -> bool:
        for r, c, peg in self.cleared_pegs:
            frame.place_peg(r, c, peg)
        return True

    def get_announcement(self, frame: TaylorFrame, verbosity: VerbosityLevel) -> str:
        count = len(self.cleared_pegs)
        if count == 0:
            return "Frame was already empty."
        return f"Cleared all {count} object{'s' if count > 1 else ''} from Taylor Frame."


class PasteBlockCommand(Command):
    """Pastes a clipboard block into the frame starting at target_row, target_col."""

    def __init__(self, target_row: int, target_col: int, block: ClipboardBlock):
        self.target_row = target_row
        self.target_col = target_col
        self.block = block
        self.placed_pegs: List[Tuple[int, int, TaylorPeg]] = []
        self.overwritten_pegs: List[Tuple[int, int, Optional[TaylorPeg]]] = []

    @property
    def name(self) -> str:
        return f"Paste {self.block.count_pegs()} items"

    def execute(self, frame: TaylorFrame) -> bool:
        self.placed_pegs = []
        self.overwritten_pegs = []

        for dr in range(self.block.num_rows):
            for dc in range(self.block.num_cols):
                r = self.target_row + dr
                c = self.target_col + dc
                peg = self.block.grid[dr][dc]
                if frame.is_valid_coord(r, c) and peg is not None:
                    old_peg = frame.place_peg(r, c, peg)
                    self.overwritten_pegs.append((r, c, old_peg))
                    self.placed_pegs.append((r, c, peg))

        return len(self.placed_pegs) > 0

    def undo(self, frame: TaylorFrame) -> bool:
        for r, c, old_peg in self.overwritten_pegs:
            if old_peg is not None:
                frame.place_peg(r, c, old_peg)
            else:
                frame.remove_peg(r, c)
        frame.set_cursor(self.target_row, self.target_col)
        return True

    def get_announcement(self, frame: TaylorFrame, verbosity: VerbosityLevel) -> str:
        count = len(self.placed_pegs)
        return (
            f"Pasted {count} object{'s' if count > 1 else ''} starting at "
            f"Row {self.target_row + 1}, Column {self.target_col + 1}."
        )
