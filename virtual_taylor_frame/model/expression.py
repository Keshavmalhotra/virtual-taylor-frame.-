"""
Mathematical expression analyzer and reader for the Taylor Frame.
Parses horizontal rows, vertical columns, and 2D spatial layouts into structured mathematical text.
"""
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any

from virtual_taylor_frame.model.cell import Cell
from virtual_taylor_frame.model.peg import TaylorPeg


@dataclass
class RowExpressionSegment:
    """A contiguous segment of occupied cells within a single row."""
    row: int  # 0-based
    start_col: int  # 0-based
    end_col: int  # 0-based inclusive
    pegs: List[TaylorPeg]

    @property
    def display_row(self) -> int:
        return self.row + 1

    @property
    def display_start_col(self) -> int:
        return self.start_col + 1

    @property
    def display_end_col(self) -> int:
        return self.end_col + 1

    @property
    def raw_symbols(self) -> str:
        return "".join(p.symbol for p in self.pegs)

    @property
    def math_text(self) -> str:
        """Formatted mathematical representation with proper spacing."""
        parts = []
        for peg in self.pegs:
            sym = peg.symbol
            if sym in ("+", "-", "*", "/", "=", ":"):
                parts.append(f" {sym} ")
            elif sym in (",", ";"):
                parts.append(f"{sym} ")
            else:
                parts.append(sym)
        # Collapse multiple spaces
        text = "".join(parts).strip()
        while "  " in text:
            text = text.replace("  ", " ")
        return text

    @property
    def spoken_text(self) -> str:
        """Spoken accessible representation for screen readers."""
        spoken_parts = []
        for peg in self.pegs:
            sym = peg.symbol
            if sym == "+":
                spoken_parts.append("plus")
            elif sym == "-":
                spoken_parts.append("minus")
            elif sym == "*":
                spoken_parts.append("times")
            elif sym == "/":
                spoken_parts.append("divided by")
            elif sym == "=":
                spoken_parts.append("equals")
            elif sym == ".":
                spoken_parts.append("point")
            elif sym == "^":
                spoken_parts.append("to the power of")
            elif sym == "√":
                spoken_parts.append("square root of")
            elif sym == "(":
                spoken_parts.append("open paren")
            elif sym == ")":
                spoken_parts.append("close paren")
            elif sym == "_":
                spoken_parts.append("line")
            else:
                spoken_parts.append(sym)
        return " ".join(spoken_parts)


class ExpressionAnalyzer:
    """
    Analyzes mathematical content on a Taylor Frame grid.
    """

    @staticmethod
    def extract_row_segments(
        row_idx: int,
        row_cells: List[Cell],
    ) -> List[RowExpressionSegment]:
        """
        Extract all contiguous non-empty cell segments from a single row.
        """
        segments: List[RowExpressionSegment] = []
        current_pegs: List[TaylorPeg] = []
        seg_start_col = -1

        for c_idx, cell in enumerate(row_cells):
            if cell.is_occupied:
                if not current_pegs:
                    seg_start_col = c_idx
                current_pegs.append(cell.peg)  # type: ignore
            else:
                if current_pegs:
                    segments.append(
                        RowExpressionSegment(
                            row=row_idx,
                            start_col=seg_start_col,
                            end_col=c_idx - 1,
                            pegs=list(current_pegs),
                        )
                    )
                    current_pegs.clear()

        if current_pegs:
            segments.append(
                RowExpressionSegment(
                    row=row_idx,
                    start_col=seg_start_col,
                    end_col=len(row_cells) - 1,
                    pegs=list(current_pegs),
                )
            )

        return segments

    @staticmethod
    def describe_row(row_idx: int, row_cells: List[Cell]) -> str:
        """
        Summarize a single row for accessible speech output (F6).
        """
        display_row = row_idx + 1
        segments = ExpressionAnalyzer.extract_row_segments(row_idx, row_cells)
        if not segments:
            return f"Row {display_row}: Empty."

        descriptions = []
        for seg in segments:
            col_info = (
                f"Column {seg.display_start_col}"
                if seg.display_start_col == seg.display_end_col
                else f"Columns {seg.display_start_col} to {seg.display_end_col}"
            )
            descriptions.append(f"{col_info}: {seg.spoken_text}")

        return f"Row {display_row}: " + "; ".join(descriptions)

    @staticmethod
    def describe_column(col_idx: int, col_cells: List[Cell]) -> str:
        """
        Summarize a single column top-to-bottom for accessible speech output (F7).
        """
        display_col = col_idx + 1
        occupied = [(c.display_row, c.peg) for c in col_cells if c.is_occupied]
        if not occupied:
            return f"Column {display_col}: Empty."

        entries = []
        for r_disp, peg in occupied:
            entries.append(f"Row {r_disp}: {peg.label}")

        return f"Column {display_col} ({len(occupied)} items): " + ", ".join(entries)

    @staticmethod
    def summarize_frame(
        rows: int,
        cols: int,
        grid: List[List[Cell]],
    ) -> str:
        """
        Generate a comprehensive full-frame description (F5).
        """
        occupied_count = 0
        non_empty_rows: List[Tuple[int, List[RowExpressionSegment]]] = []
        min_r, max_r = rows, -1
        min_c, max_c = cols, -1

        for r_idx, row in enumerate(grid):
            segments = ExpressionAnalyzer.extract_row_segments(r_idx, row)
            if segments:
                non_empty_rows.append((r_idx, segments))
                min_r = min(min_r, r_idx)
                max_r = max(max_r, r_idx)
                for seg in segments:
                    occupied_count += len(seg.pegs)
                    min_c = min(min_c, seg.start_col)
                    max_c = max(max_c, seg.end_col)

        lines = [
            "Taylor Frame Construction.",
            f"Frame size: {rows} rows by {cols} columns.",
        ]

        if occupied_count == 0:
            lines.append("The frame is completely empty.")
            return "\n".join(lines)

        lines.append(f"Total objects: {occupied_count}.")
        lines.append(
            f"Content bounds: Rows {min_r + 1} to {max_r + 1}, "
            f"Columns {min_c + 1} to {max_c + 1}."
        )
        lines.append("\nExpressions by row:")

        for r_idx, segments in non_empty_rows:
            r_disp = r_idx + 1
            for seg in segments:
                col_range = (
                    f"Col {seg.display_start_col}"
                    if seg.display_start_col == seg.display_end_col
                    else f"Cols {seg.display_start_col}-{seg.display_end_col}"
                )
                lines.append(f"  Row {r_disp}, {col_range}: {seg.math_text} (spoken: {seg.spoken_text})")

        return "\n".join(lines)
