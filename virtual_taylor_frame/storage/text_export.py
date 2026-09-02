"""
Plain text exporter generating clean, accessible text representations of the Taylor Frame.
"""
from typing import List, Dict
from virtual_taylor_frame.model.frame import TaylorFrame
from virtual_taylor_frame.model.expression import ExpressionAnalyzer


class TextExporter:
    """
    Exports a Taylor Frame to an accessible, human-readable plain-text document.
    """

    @staticmethod
    def export_text(frame: TaylorFrame) -> str:
        lines: List[str] = [
            "============================================================",
            "                   VIRTUAL TAYLOR FRAME                     ",
            "============================================================",
            f"Frame Size: {frame.rows} Rows x {frame.cols} Columns",
            f"Total Objects Placed: {frame.count_occupied()}",
            "============================================================",
            "",
            "--- MATHEMATICAL EXPRESSIONS ---",
        ]

        has_content = False
        for r in range(frame.rows):
            segments = ExpressionAnalyzer.extract_row_segments(r, frame._grid[r])
            if segments:
                has_content = True
                row_desc = ExpressionAnalyzer.describe_row(r, frame._grid[r])
                lines.append(row_desc)

        if not has_content:
            lines.append("No mathematical objects on this frame.")

        lines.extend([
            "",
            "--- 2D GRID LAYOUT ---",
            "(Empty slots are represented by '.' dots, objects by their symbols)",
            "",
        ])

        # Generate ASCII grid header
        col_header = "       " + "".join(f"{c+1:2} " if (c+1)%5==0 or c==0 else " . " for c in range(frame.cols))
        lines.append(col_header)

        for r in range(frame.rows):
            row_chars = []
            for c in range(frame.cols):
                cell = frame.get_cell(r, c)
                if cell.is_occupied:
                    sym = cell.peg.symbol
                    row_chars.append(f" {sym} ")
                else:
                    row_chars.append(" . ")
            lines.append(f"Row {r+1:2}: " + "".join(row_chars))

        lines.extend([
            "",
            "--- OBJECT INVENTORY ---",
        ])

        counts: Dict[str, int] = {}
        for cell in frame.occupied_cells():
            lbl = cell.peg.label
            counts[lbl] = counts.get(lbl, 0) + 1

        for lbl, cnt in sorted(counts.items()):
            lines.append(f"  - {lbl}: {cnt}")

        lines.append("")
        lines.append("============================================================")
        return "\n".join(lines)
