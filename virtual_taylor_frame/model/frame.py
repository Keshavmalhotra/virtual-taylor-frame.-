"""
Core mathematical Taylor Frame board model.
Completely independent of UI and graphic frameworks.
"""
from typing import List, Optional, Tuple, Dict, Any, Callable
from dataclasses import dataclass, field

from virtual_taylor_frame.model.types import (
    PegOrientation,
    PegEnd,
    PegType,
    VerbosityLevel,
)
from virtual_taylor_frame.model.peg import TaylorPeg
from virtual_taylor_frame.model.cell import Cell
from virtual_taylor_frame.model.selection import SelectionRange, ClipboardBlock
from virtual_taylor_frame.model.expression import ExpressionAnalyzer


DEFAULT_ROWS = 20
DEFAULT_COLS = 30


class TaylorFrame:
    """
    Mathematical grid representing the Taylor Frame board.
    Grid coordinates are 0-indexed internally [0..rows-1, 0..cols-1].
    User-facing display coordinates are 1-indexed [1..rows, 1..cols].
    """

    def __init__(self, rows: int = DEFAULT_ROWS, cols: int = DEFAULT_COLS):
        if rows < 1 or cols < 1:
            raise ValueError(f"Frame dimensions must be >= 1x1, got {rows}x{cols}")
        self.rows: int = rows
        self.cols: int = cols
        self._grid: List[List[Cell]] = [
            [Cell(row=r, col=c) for c in range(cols)] for r in range(rows)
        ]
        self._cursor_row: int = 0
        self._cursor_col: int = 0
        self._selection: Optional[SelectionRange] = None
        self._listeners: List[Callable[[str, Dict[str, Any]], None]] = []

    # --- Listeners / Observers ---

    def add_listener(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """Register an observer for model events."""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """Unregister an observer."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify(self, event_name: str, **kwargs) -> None:
        """Dispatch event notification to all registered observers."""
        for listener in self._listeners:
            try:
                listener(event_name, kwargs)
            except Exception as e:
                # Observers must not crash the core model
                pass

    # --- Cursor & Navigation Properties ---

    @property
    def cursor_row(self) -> int:
        return self._cursor_row

    @property
    def cursor_col(self) -> int:
        return self._cursor_col

    @property
    def display_cursor_row(self) -> int:
        return self._cursor_row + 1

    @property
    def display_cursor_col(self) -> int:
        return self._cursor_col + 1

    @property
    def selection(self) -> Optional[SelectionRange]:
        return self._selection

    def set_cursor(self, row: int, col: int) -> bool:
        """
        Set cursor to 0-based row and col within bounds.
        Returns True if cursor moved.
        """
        clamped_r = max(0, min(self.rows - 1, row))
        clamped_c = max(0, min(self.cols - 1, col))
        if clamped_r != self._cursor_row or clamped_c != self._cursor_col:
            old_r, old_c = self._cursor_row, self._cursor_col
            self._cursor_row = clamped_r
            self._cursor_col = clamped_c
            self._notify(
                "cursor_moved",
                old_row=old_r,
                old_col=old_c,
                new_row=clamped_r,
                new_col=clamped_c,
            )
            return True
        return False

    def move_cursor(self, delta_row: int, delta_col: int) -> bool:
        """Move cursor relative to current position."""
        return self.set_cursor(self._cursor_row + delta_row, self._cursor_col + delta_col)

    def jump_to_next_occupied(self, delta_row: int, delta_col: int) -> bool:
        """
        Jump to the next occupied cell in the given direction vector.
        """
        if delta_row == 0 and delta_col == 0:
            return False

        r, c = self._cursor_row + delta_row, self._cursor_col + delta_col
        while 0 <= r < self.rows and 0 <= c < self.cols:
            if self._grid[r][c].is_occupied:
                return self.set_cursor(r, c)
            r += delta_row
            c += delta_col
        return False

    # --- Selection ---

    def set_selection(self, selection: Optional[SelectionRange]) -> None:
        self._selection = selection
        self._notify("selection_changed", selection=selection)

    def clear_selection(self) -> None:
        if self._selection is not None:
            self._selection = None
            self._notify("selection_changed", selection=None)

    # --- Cell & Peg Access ---

    def is_valid_coord(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols

    def get_cell(self, row: int, col: int) -> Cell:
        if not self.is_valid_coord(row, col):
            raise IndexError(f"Cell coordinates ({row}, {col}) out of bounds ({self.rows}x{self.cols})")
        return self._grid[row][col]

    def get_current_cell(self) -> Cell:
        return self._grid[self._cursor_row][self._cursor_col]

    def place_peg(self, row: int, col: int, peg: TaylorPeg) -> Optional[TaylorPeg]:
        """
        Place a peg in the specified cell.
        Returns the previous peg if any.
        """
        cell = self.get_cell(row, col)
        old_peg = cell.peg
        cell.peg = peg
        self._notify("cell_changed", row=row, col=col, old_peg=old_peg, new_peg=peg)
        return old_peg

    def remove_peg(self, row: int, col: int) -> Optional[TaylorPeg]:
        """
        Remove peg from the specified cell.
        Returns the removed peg or None if already empty.
        """
        cell = self.get_cell(row, col)
        if not cell.is_occupied:
            return None
        old_peg = cell.peg
        cell.peg = None
        self._notify("cell_changed", row=row, col=col, old_peg=old_peg, new_peg=None)
        return old_peg

    def clear_row(self, row: int) -> List[Tuple[int, int, TaylorPeg]]:
        """
        Remove all pegs in the given row.
        Returns list of (row, col, old_peg).
        """
        if not (0 <= row < self.rows):
            return []
        cleared = []
        for c in range(self.cols):
            cell = self._grid[row][c]
            if cell.is_occupied:
                old_peg = cell.peg
                cell.peg = None
                cleared.append((row, c, old_peg))
                self._notify("cell_changed", row=row, col=c, old_peg=old_peg, new_peg=None)
        return cleared

    def clear_all(self) -> List[Tuple[int, int, TaylorPeg]]:
        """
        Remove all pegs from the entire frame.
        Returns list of (row, col, old_peg).
        """
        cleared = []
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self._grid[r][c]
                if cell.is_occupied:
                    old_peg = cell.peg
                    cell.peg = None
                    cleared.append((r, c, old_peg))
                    self._notify("cell_changed", row=r, col=c, old_peg=old_peg, new_peg=None)
        self._notify("frame_cleared")
        return cleared

    # --- Surrounding Neighbor Inspection ---

    def get_neighbors(self, row: int, col: int) -> Dict[str, Optional[Cell]]:
        """
        Return the 4-way adjacent cells (North, South, East, West).
        None represents out-of-bounds boundary.
        """
        return {
            "North": self._grid[row - 1][col] if row > 0 else None,
            "South": self._grid[row + 1][col] if row < self.rows - 1 else None,
            "East": self._grid[row][col + 1] if col < self.cols - 1 else None,
            "West": self._grid[row][col - 1] if col > 0 else None,
        }

    def describe_neighbors(self, row: int, col: int) -> str:
        """
        Generate screen reader description of surrounding cells (F8).
        """
        neighbors = self.get_neighbors(row, col)
        parts = []
        for dir_name, cell in neighbors.items():
            if cell is None:
                parts.append(f"{dir_name}: frame edge")
            elif not cell.is_occupied:
                parts.append(f"{dir_name}: empty")
            else:
                parts.append(f"{dir_name}: {cell.peg.label}")  # type: ignore
        return f"Neighbors around Row {row + 1}, Column {col + 1}: " + "; ".join(parts) + "."

    # --- Query & Statistics ---

    def count_occupied(self) -> int:
        return sum(1 for row in self._grid for cell in row if cell.is_occupied)

    def occupied_cells(self) -> List[Cell]:
        return [cell for row in self._grid for cell in row if cell.is_occupied]

    # --- Inspection & Summaries ---

    def describe_current_cell(self, verbosity: VerbosityLevel = VerbosityLevel.NORMAL) -> str:
        return self.get_current_cell().describe(verbosity, include_coords=True)

    def describe_row(self, row: int) -> str:
        if not (0 <= row < self.rows):
            return f"Row {row + 1}: Out of bounds."
        return ExpressionAnalyzer.describe_row(row, self._grid[row])

    def describe_current_row(self) -> str:
        return self.describe_row(self._cursor_row)

    def describe_column(self, col: int) -> str:
        if not (0 <= col < self.cols):
            return f"Column {col + 1}: Out of bounds."
        col_cells = [self._grid[r][col] for r in range(self.rows)]
        return ExpressionAnalyzer.describe_column(col, col_cells)

    def describe_current_column(self) -> str:
        return self.describe_column(self._cursor_col)

    def summarize_frame(self) -> str:
        return ExpressionAnalyzer.summarize_frame(self.rows, self.cols, self._grid)

    # --- Serialization ---

    def to_dict(self) -> Dict[str, Any]:
        """Serialize frame structure and occupied cells."""
        occupied_cells_data = [
            cell.to_dict() for row in self._grid for cell in row if cell.is_occupied
        ]
        return {
            "dimensions": {
                "rows": self.rows,
                "columns": self.cols,
            },
            "cursor": {
                "row": self.display_cursor_row,
                "column": self.display_cursor_col,
            },
            "cells": occupied_cells_data,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaylorFrame":
        """Reconstruct frame from serialized dictionary."""
        dims = data.get("dimensions", {})
        rows = int(dims.get("rows", DEFAULT_ROWS))
        cols = int(dims.get("columns", DEFAULT_COLS))

        frame = cls(rows=rows, cols=cols)

        # Restore cells
        cells_data = data.get("cells", [])
        for c_data in cells_data:
            cell = Cell.from_dict(c_data)
            if frame.is_valid_coord(cell.row, cell.col) and cell.peg is not None:
                frame.place_peg(cell.row, cell.col, cell.peg)

        # Restore cursor
        cursor_data = data.get("cursor", {})
        c_row = int(cursor_data.get("row", 1)) - 1
        c_col = int(cursor_data.get("column", 1)) - 1
        frame.set_cursor(c_row, c_col)

        return frame
