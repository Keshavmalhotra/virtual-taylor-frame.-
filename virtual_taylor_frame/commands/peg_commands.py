"""
Concrete commands for individual Taylor peg operations.
"""
from typing import Optional

from virtual_taylor_frame.commands.base import Command
from virtual_taylor_frame.model.frame import TaylorFrame
from virtual_taylor_frame.model.peg import TaylorPeg
from virtual_taylor_frame.model.types import VerbosityLevel


class PlacePegCommand(Command):
    """Places or replaces a peg at a specified cell."""

    def __init__(self, row: int, col: int, peg: TaylorPeg):
        self.row = row
        self.col = col
        self.peg = peg
        self.previous_peg: Optional[TaylorPeg] = None

    @property
    def name(self) -> str:
        return f"Place {self.peg.symbol}"

    def execute(self, frame: TaylorFrame) -> bool:
        self.previous_peg = frame.place_peg(self.row, self.col, self.peg)
        return True

    def undo(self, frame: TaylorFrame) -> bool:
        if self.previous_peg is not None:
            frame.place_peg(self.row, self.col, self.previous_peg)
        else:
            frame.remove_peg(self.row, self.col)
        frame.set_cursor(self.row, self.col)
        return True

    def get_announcement(self, frame: TaylorFrame, verbosity: VerbosityLevel) -> str:
        display_r = self.row + 1
        display_c = self.col + 1
        if verbosity == VerbosityLevel.MINIMAL:
            return self.peg.symbol
        elif verbosity == VerbosityLevel.NORMAL:
            return f"Placed {self.peg.label} at Row {display_r}, Column {display_c}."
        else:
            return (
                f"Placed {self.peg.label} at Row {display_r}, Column {display_c}. "
                f"{self.peg.describe(verbosity)}"
            )


class RemovePegCommand(Command):
    """Removes a peg from a cell."""

    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.removed_peg: Optional[TaylorPeg] = None

    @property
    def name(self) -> str:
        sym = self.removed_peg.symbol if self.removed_peg else "peg"
        return f"Remove {sym}"

    def execute(self, frame: TaylorFrame) -> bool:
        self.removed_peg = frame.remove_peg(self.row, self.col)
        return self.removed_peg is not None

    def undo(self, frame: TaylorFrame) -> bool:
        if self.removed_peg is not None:
            frame.place_peg(self.row, self.col, self.removed_peg)
            frame.set_cursor(self.row, self.col)
            return True
        return False

    def get_announcement(self, frame: TaylorFrame, verbosity: VerbosityLevel) -> str:
        display_r = self.row + 1
        display_c = self.col + 1
        if self.removed_peg is None:
            return f"Row {display_r}, column {display_c} is already empty."
        if verbosity == VerbosityLevel.MINIMAL:
            return "Empty."
        elif verbosity == VerbosityLevel.NORMAL:
            return f"Removed {self.removed_peg.label} from Row {display_r}, Column {display_c}. Empty."
        else:
            return f"Removed {self.removed_peg.label}. Row {display_r}, Column {display_c} is now empty."


class RotatePegCommand(Command):
    """Rotates a peg in a cell clockwise or counter-clockwise."""

    def __init__(self, row: int, col: int, clockwise: bool = True):
        self.row = row
        self.col = col
        self.clockwise = clockwise
        self.previous_peg: Optional[TaylorPeg] = None
        self.new_peg: Optional[TaylorPeg] = None

    @property
    def name(self) -> str:
        direction = "clockwise" if self.clockwise else "counter-clockwise"
        return f"Rotate peg {direction}"

    def execute(self, frame: TaylorFrame) -> bool:
        cell = frame.get_cell(self.row, self.col)
        if not cell.is_occupied:
            return False
        self.previous_peg = cell.peg
        self.new_peg = (
            self.previous_peg.rotate_cw()
            if self.clockwise
            else self.previous_peg.rotate_ccw()
        )
        frame.place_peg(self.row, self.col, self.new_peg)
        return True

    def undo(self, frame: TaylorFrame) -> bool:
        if self.previous_peg is not None:
            frame.place_peg(self.row, self.col, self.previous_peg)
            frame.set_cursor(self.row, self.col)
            return True
        return False

    def get_announcement(self, frame: TaylorFrame, verbosity: VerbosityLevel) -> str:
        if self.new_peg is None:
            return "Cannot rotate: Cell is empty."
        rot_dir = "clockwise" if self.clockwise else "counter-clockwise"
        if verbosity == VerbosityLevel.MINIMAL:
            return self.new_peg.symbol
        elif verbosity == VerbosityLevel.NORMAL:
            return f"Rotated {rot_dir} to {self.new_peg.label}."
        else:
            return (
                f"Rotated {rot_dir} to {self.new_peg.orientation.value}° "
                f"{self.new_peg.orientation.compass_name}: {self.new_peg.label}."
            )


class FlipPegCommand(Command):
    """Flips a peg between End A and End B (inverts the peg)."""

    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.previous_peg: Optional[TaylorPeg] = None
        self.new_peg: Optional[TaylorPeg] = None

    @property
    def name(self) -> str:
        return "Flip peg end"

    def execute(self, frame: TaylorFrame) -> bool:
        cell = frame.get_cell(self.row, self.col)
        if not cell.is_occupied:
            return False
        self.previous_peg = cell.peg
        self.new_peg = self.previous_peg.flip_end()
        frame.place_peg(self.row, self.col, self.new_peg)
        return True

    def undo(self, frame: TaylorFrame) -> bool:
        if self.previous_peg is not None:
            frame.place_peg(self.row, self.col, self.previous_peg)
            frame.set_cursor(self.row, self.col)
            return True
        return False

    def get_announcement(self, frame: TaylorFrame, verbosity: VerbosityLevel) -> str:
        if self.new_peg is None:
            return "Cannot flip: Cell is empty."
        if verbosity == VerbosityLevel.MINIMAL:
            return self.new_peg.symbol
        elif verbosity == VerbosityLevel.NORMAL:
            return f"Flipped to {self.new_peg.peg_end.friendly_name}: {self.new_peg.label}."
        else:
            return (
                f"Flipped to {self.new_peg.peg_end.friendly_name}, "
                f"{self.new_peg.orientation.value}° {self.new_peg.orientation.compass_name}: {self.new_peg.label}."
            )


class ToggleTypeCommand(Command):
    """Toggles peg type between Arithmetic and Algebraic."""

    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.previous_peg: Optional[TaylorPeg] = None
        self.new_peg: Optional[TaylorPeg] = None

    @property
    def name(self) -> str:
        return "Toggle peg type"

    def execute(self, frame: TaylorFrame) -> bool:
        cell = frame.get_cell(self.row, self.col)
        if not cell.is_occupied:
            return False
        self.previous_peg = cell.peg
        self.new_peg = self.previous_peg.toggle_type()
        frame.place_peg(self.row, self.col, self.new_peg)
        return True

    def undo(self, frame: TaylorFrame) -> bool:
        if self.previous_peg is not None:
            frame.place_peg(self.row, self.col, self.previous_peg)
            frame.set_cursor(self.row, self.col)
            return True
        return False

    def get_announcement(self, frame: TaylorFrame, verbosity: VerbosityLevel) -> str:
        if self.new_peg is None:
            return "Cannot toggle type: Cell is empty."
        if verbosity == VerbosityLevel.MINIMAL:
            return self.new_peg.symbol
        else:
            return f"Switched to {self.new_peg.peg_type.friendly_name} Type: {self.new_peg.label}."


class MovePegCommand(Command):
    """Moves a peg from one cell to another cell."""

    def __init__(self, from_row: int, from_col: int, to_row: int, to_col: int):
        self.from_row = from_row
        self.from_col = from_col
        self.to_row = to_row
        self.to_col = to_col
        self.moved_peg: Optional[TaylorPeg] = None
        self.target_previous_peg: Optional[TaylorPeg] = None

    @property
    def name(self) -> str:
        return f"Move peg to Row {self.to_row + 1}, Col {self.to_col + 1}"

    def execute(self, frame: TaylorFrame) -> bool:
        src_cell = frame.get_cell(self.from_row, self.from_col)
        if not src_cell.is_occupied:
            return False
        self.moved_peg = frame.remove_peg(self.from_row, self.from_col)
        self.target_previous_peg = frame.place_peg(self.to_row, self.to_col, self.moved_peg)
        frame.set_cursor(self.to_row, self.to_col)
        return True

    def undo(self, frame: TaylorFrame) -> bool:
        if self.moved_peg is not None:
            frame.place_peg(self.from_row, self.from_col, self.moved_peg)
            if self.target_previous_peg is not None:
                frame.place_peg(self.to_row, self.to_col, self.target_previous_peg)
            else:
                frame.remove_peg(self.to_row, self.to_col)
            frame.set_cursor(self.from_row, self.from_col)
            return True
        return False

    def get_announcement(self, frame: TaylorFrame, verbosity: VerbosityLevel) -> str:
        if self.moved_peg is None:
            return "Cannot move: Source cell is empty."
        return (
            f"Moved {self.moved_peg.label} from Row {self.from_row + 1}, Column {self.from_col + 1} "
            f"to Row {self.to_row + 1}, Column {self.to_col + 1}."
        )
