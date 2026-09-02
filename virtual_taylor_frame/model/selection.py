"""
Selection and clipboard data models for block operations on the Taylor Frame.
"""
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any

from virtual_taylor_frame.model.peg import TaylorPeg


@dataclass(frozen=True)
class SelectionRange:
    """
    Represents a rectangular region of cells on the Taylor Frame (0-indexed internally).
    """
    start_row: int
    start_col: int
    end_row: int
    end_col: int

    @property
    def min_row(self) -> int:
        return min(self.start_row, self.end_row)

    @property
    def max_row(self) -> int:
        return max(self.start_row, self.end_row)

    @property
    def min_col(self) -> int:
        return min(self.start_col, self.end_col)

    @property
    def max_col(self) -> int:
        return max(self.start_col, self.end_col)

    @property
    def num_rows(self) -> int:
        return self.max_row - self.min_row + 1

    @property
    def num_cols(self) -> int:
        return self.max_col - self.min_col + 1

    @property
    def total_cells(self) -> int:
        return self.num_rows * self.num_cols

    def contains(self, row: int, col: int) -> bool:
        return (self.min_row <= row <= self.max_row) and (self.min_col <= col <= self.max_col)

    def describe(self) -> str:
        r1, c1 = self.min_row + 1, self.min_col + 1
        r2, c2 = self.max_row + 1, self.max_col + 1
        return (
            f"Selected {self.num_rows} row{'s' if self.num_rows > 1 else ''} by "
            f"{self.num_cols} column{'s' if self.num_cols > 1 else ''} "
            f"(Row {r1}, Column {c1} to Row {r2}, Column {c2})."
        )


@dataclass
class ClipboardBlock:
    """
    Represents a 2D block of copied pegs with relative offsets (0-indexed).
    """
    num_rows: int
    num_cols: int
    # Grid of pegs: None represents empty socket in the block
    grid: List[List[Optional[TaylorPeg]]]

    @classmethod
    def from_region(
        cls,
        selection: SelectionRange,
        get_peg_fn,
    ) -> "ClipboardBlock":
        min_r, max_r = selection.min_row, selection.max_row
        min_c, max_c = selection.min_col, selection.max_col
        num_r = max_r - min_r + 1
        num_c = max_c - min_c + 1

        grid: List[List[Optional[TaylorPeg]]] = []
        for r in range(min_r, max_r + 1):
            row_pegs = []
            for c in range(min_c, max_c + 1):
                row_pegs.append(get_peg_fn(r, c))
            grid.append(row_pegs)

        return cls(num_rows=num_r, num_cols=num_c, grid=grid)

    def count_pegs(self) -> int:
        return sum(1 for row in self.grid for peg in row if peg is not None)
