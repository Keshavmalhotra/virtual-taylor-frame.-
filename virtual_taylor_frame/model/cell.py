"""
Cell model representing a single socket location on the Taylor Frame grid.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any

from virtual_taylor_frame.model.peg import TaylorPeg
from virtual_taylor_frame.model.types import VerbosityLevel


@dataclass
class Cell:
    """
    Represents an individual slot on the Taylor frame board.
    Internal indices are 0-based. Display / speech coordinates are 1-based.
    """
    row: int
    col: int
    peg: Optional[TaylorPeg] = None

    @property
    def display_row(self) -> int:
        """1-based row number for user-facing speech and UI."""
        return self.row + 1

    @property
    def display_col(self) -> int:
        """1-based column number for user-facing speech and UI."""
        return self.col + 1

    @property
    def is_occupied(self) -> bool:
        return self.peg is not None

    def describe(
        self,
        verbosity: VerbosityLevel = VerbosityLevel.NORMAL,
        include_coords: bool = True,
    ) -> str:
        """
        Generate screen reader accessible description for this cell.
        """
        coord_prefix = f"Row {self.display_row}, column {self.display_col}. " if include_coords else ""
        if not self.is_occupied:
            if verbosity == VerbosityLevel.MINIMAL:
                return f"{coord_prefix}Empty."
            elif verbosity == VerbosityLevel.NORMAL:
                return f"{coord_prefix}Empty."
            else:
                return f"{coord_prefix}Empty octagonal socket."

        peg_desc = self.peg.describe(verbosity)
        return f"{coord_prefix}{peg_desc}."

    def to_dict(self) -> Dict[str, Any]:
        """Serialize cell with 1-based display coordinates for .tframe JSON."""
        return {
            "row": self.display_row,
            "column": self.display_col,
            "peg": self.peg.to_dict() if self.peg else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Cell":
        """Deserialize cell from .tframe dictionary (translates 1-based to 0-based)."""
        row = int(data.get("row", 1)) - 1
        col = int(data.get("column", 1)) - 1
        peg_data = data.get("peg")
        peg = TaylorPeg.from_dict(peg_data) if peg_data else None
        return cls(row=row, col=col, peg=peg)
