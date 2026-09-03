"""
Block and multi-cell commands for Taylor Frame operations.
"""
from typing import List, Tuple, Optional, Dict, Any

from virtual_taylor_frame.commands.base import Command
from virtual_taylor_frame.model.frame import TaylorFrame
from virtual_taylor_frame.model.peg import TaylorPeg
from virtual_taylor_frame.model.selection import SelectionRange, ClipboardBlock
from virtual_taylor_frame.model.types import VerbosityLevel


class ExtendFrameCommand(Command):
    """Extend the frame with empty rows and/or columns."""

    def __init__(self, rows: int = 0, cols: int = 0):
        self.add_rows, self.add_cols = rows, cols
        self.old_rows = self.old_cols = 0

    @property
    def name(self) -> str:
        return "Extend Frame"

    def execute(self, frame: TaylorFrame) -> bool:
        self.old_rows, self.old_cols = frame.rows, frame.cols
        frame.extend(self.add_rows, self.add_cols)
        return True

    def undo(self, frame: TaylorFrame) -> bool:
        frame.shrink_to(self.old_rows, self.old_cols)
        return True

    def get_announcement(self, frame: TaylorFrame, verbosity: VerbosityLevel) -> str:
        return f"Frame extended. {frame.rows} rows, {frame.cols} columns."


class ShrinkFrameCommand(Command):
    """Remove empty rows and/or columns from the bottom/right of the frame."""

    def __init__(self, rows: int = 0, cols: int = 0):
        self.remove_rows, self.remove_cols = rows, cols
        self.old_rows = self.old_cols = 0

    @property
    def name(self) -> str:
        return "Shrink Frame"

    def execute(self, frame: TaylorFrame) -> bool:
        self.old_rows, self.old_cols = frame.rows, frame.cols
        try:
            frame.shrink_to(frame.rows - self.remove_rows, frame.cols - self.remove_cols)
        except ValueError:
            return False
        return True

    def undo(self, frame: TaylorFrame) -> bool:
        frame.extend(self.old_rows - frame.rows, self.old_cols - frame.cols)
        return True

    def get_announcement(self, frame: TaylorFrame, verbosity: VerbosityLevel) -> str:
        return f"Frame shrunk. {frame.rows} rows, {frame.cols} columns."


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


class MoveSelectionCommand(Command):
    """Move every occupied cell in a selection by one grid step."""

    def __init__(self, selection: SelectionRange, delta_row: int, delta_col: int):
        if abs(delta_row) + abs(delta_col) != 1:
            raise ValueError("Selection moves must be one cell in one direction")
        self.selection = selection
        self.delta_row, self.delta_col = delta_row, delta_col
        self.items: List[Tuple[int, int, TaylorPeg]] = []

    @property
    def name(self) -> str:
        return "Move selection"

    def execute(self, frame: TaylorFrame) -> bool:
        self.items = [(r, c, frame.get_cell(r, c).peg)
                      for r in range(self.selection.min_row, self.selection.max_row + 1)
                      for c in range(self.selection.min_col, self.selection.max_col + 1)
                      if frame.get_cell(r, c).is_occupied]
        if not self.items:
            return False
        destinations = {(r + self.delta_row, c + self.delta_col) for r, c, _ in self.items}
        if any(not frame.is_valid_coord(r, c) for r, c in destinations):
            return False
        sources = {(r, c) for r, c, _ in self.items}
        if any(frame.get_cell(r, c).is_occupied and (r, c) not in sources for r, c in destinations):
            return False
        for r, c, _ in self.items:
            frame.remove_peg(r, c)
        for r, c, peg in self.items:
            frame.place_peg(r + self.delta_row, c + self.delta_col, peg)
        frame.set_selection(SelectionRange(self.selection.start_row + self.delta_row,
                                            self.selection.start_col + self.delta_col,
                                            self.selection.end_row + self.delta_row,
                                            self.selection.end_col + self.delta_col))
        frame.set_cursor(self.selection.start_row + self.delta_row, self.selection.start_col + self.delta_col)
        return True

    def undo(self, frame: TaylorFrame) -> bool:
        for r, c, _ in self.items:
            frame.remove_peg(r + self.delta_row, c + self.delta_col)
        for r, c, peg in self.items:
            frame.place_peg(r, c, peg)
        frame.set_selection(self.selection)
        frame.set_cursor(self.selection.start_row, self.selection.start_col)
        return True

    def get_announcement(self, frame: TaylorFrame, verbosity: VerbosityLevel) -> str:
        direction = {(-1, 0): "up", (1, 0): "down", (0, -1): "left", (0, 1): "right"}[(self.delta_row, self.delta_col)]
        return f"Moved selection {direction}."
