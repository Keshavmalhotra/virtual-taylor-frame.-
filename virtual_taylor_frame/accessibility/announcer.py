"""
Accessible Announcer that formats and dispatches messages to the speech and Braille engine
according to user-configured verbosity levels.
"""
from typing import Optional
from virtual_taylor_frame.accessibility.ao3_engine import AccessibilityEngine, AO3Engine
from virtual_taylor_frame.model.cell import Cell
from virtual_taylor_frame.model.frame import TaylorFrame
from virtual_taylor_frame.model.selection import SelectionRange
from virtual_taylor_frame.model.types import VerbosityLevel


class Announcer:
    """
    Central speech/Braille coordinator for the Virtual Taylor Frame.
    """

    def __init__(
        self,
        engine: Optional[AccessibilityEngine] = None,
        verbosity: VerbosityLevel = VerbosityLevel.NORMAL,
    ):
        self.engine: AccessibilityEngine = engine if engine is not None else AO3Engine()
        self.verbosity: VerbosityLevel = verbosity
        self.speech_enabled: bool = True
        self.braille_enabled: bool = True

    def output(self, text: str, interrupt: bool = True) -> None:
        """Send text to active speech and braille outputs."""
        if not text:
            return
        if self.speech_enabled:
            self.engine.speak(text, interrupt=interrupt)
        if self.braille_enabled:
            self.engine.braille(text)

    def cycle_verbosity(self) -> VerbosityLevel:
        """Cycle to next verbosity level and announce change."""
        self.verbosity = self.verbosity.next()
        self.output(f"Verbosity set to {self.verbosity.value.capitalize()}.", interrupt=True)
        return self.verbosity

    def set_verbosity(self, level: VerbosityLevel) -> None:
        self.verbosity = level
        self.output(f"Verbosity set to {self.verbosity.value.capitalize()}.", interrupt=True)

    def announce_navigation(
        self,
        direction: str,
        display_row: int,
        display_col: int,
        cell: Cell,
        is_jump: bool = False,
        entered_region: Optional[str] = None,
    ) -> None:
        """
        Announce cursor movement across the frame.
        """
        region_prefix = f"{entered_region} region. " if entered_region else ""
        prefix = region_prefix + (f"Jump {direction}. " if is_jump else f"{direction}. " if direction else "")
        content = cell.describe(self.verbosity, include_coords=False)

        if self.verbosity == VerbosityLevel.MINIMAL:
            if is_jump or direction in ("Up", "Down"):
                msg = f"Row {display_row}, column {display_col}. {content}"
            else:
                msg = f"Col {display_col}. {content}"
        elif self.verbosity == VerbosityLevel.NORMAL:
            msg = f"{prefix}Row {display_row}, column {display_col}. {content}"
        else:  # DETAILED
            msg = f"{prefix}Row {display_row}, column {display_col}. {cell.describe(VerbosityLevel.DETAILED, include_coords=False)}"

        self.output(msg, interrupt=True)

    def announce_cell_inspect(self, cell: Cell) -> None:
        """
        Full inspection of current cell (Space key).
        """
        msg = cell.describe(VerbosityLevel.DETAILED, include_coords=True)
        self.output(msg, interrupt=True)

    def announce_row(self, row_idx: int, frame: TaylorFrame) -> None:
        """
        Announce entire row as a continuous mathematical expression (F6).
        """
        desc = frame.describe_row(row_idx)
        self.output(desc, interrupt=True)

    def announce_column(self, col_idx: int, frame: TaylorFrame) -> None:
        """
        Announce entire column vertically (F7).
        """
        desc = frame.describe_column(col_idx)
        self.output(desc, interrupt=True)

    def announce_frame_summary(self, frame: TaylorFrame) -> None:
        """
        Announce comprehensive frame construction overview (F5).
        """
        if frame.regions:
            parts = []
            for region in frame.regions:
                lines = []
                for row in range(region.start_row, region.end_row + 1):
                    for seg in frame.describe_row(row).split("; "):
                        if seg and row >= region.start_row: lines.append(seg)
                parts.append(f"{region.name} region. " + (" ".join(lines) if lines else "Empty."))
            summary = " ".join(parts)
        else:
            summary = frame.summarize_frame()
        self.output(summary, interrupt=True)

    def announce_math_destination(self, frame: TaylorFrame, kind: str) -> None:
        cell = frame.get_current_cell()
        if kind == "number":
            end = cell.display_col
            while end < frame.cols and frame.get_cell(cell.row, end).is_occupied and frame.get_cell(cell.row, end).peg.symbol.isdigit(): end += 1
            span = f"columns {cell.display_col} to {end - 1}" if end > cell.display_col + 1 else f"column {cell.display_col}"
            self.output(f"Number {''.join(frame.get_cell(cell.row,c).peg.symbol for c in range(cell.col,end))}, row {cell.display_row}, {span}.")
        elif kind == "operator": self.output(f"{cell.peg.label}, row {cell.display_row}, column {cell.display_col}.")
        else: self.output(f"Expression, row {cell.display_row}, column {cell.display_col}.")

    def announce_region(self, frame: TaylorFrame, region) -> None:
        text = []
        for row in range(region.start_row, region.end_row + 1):
            for seg in frame.describe_row(row).split("; "):
                if seg: text.append(seg)
        coords = f"Rows {region.start_row + 1}-{region.end_row + 1}, columns {region.start_col + 1}-{region.end_col + 1}."
        self.output(f"{region.name} region. {coords} " + (" ".join(text) if text else "Empty."), interrupt=True)

    def announce_neighbors(self, row: int, col: int, frame: TaylorFrame) -> None:
        """
        Announce 4-way adjacent surrounding sockets (F8).
        """
        desc = frame.describe_neighbors(row, col)
        self.output(desc, interrupt=True)

    def announce_selection(self, selection: Optional[SelectionRange]) -> None:
        """
        Announce rectangular selection block updates.
        """
        if selection is None:
            self.output("Selection cleared.", interrupt=True)
        else:
            self.output(selection.describe(), interrupt=True)

    def announce_boundary(self, boundary_name: str) -> None:
        """Announce boundary hit."""
        self.output(f"Boundary: {boundary_name}.", interrupt=True)

    def announce_help_hint(self, message: str) -> None:
        """Announce instructional hint."""
        self.output(message, interrupt=False)
