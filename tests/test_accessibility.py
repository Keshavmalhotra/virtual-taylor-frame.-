"""
Unit tests for the Accessibility layer and speech announcements.
"""
import pytest
from virtual_taylor_frame.model import (
    TaylorFrame,
    TaylorPeg,
    VerbosityLevel,
    SelectionRange,
)
from virtual_taylor_frame.accessibility import (
    MockSpeechEngine,
    Announcer,
)


class TestAnnouncer:
    @pytest.fixture
    def setup_announcer(self):
        engine = MockSpeechEngine()
        announcer = Announcer(engine=engine, verbosity=VerbosityLevel.NORMAL)
        frame = TaylorFrame(10, 10)
        return engine, announcer, frame

    def test_navigation_announcement_normal(self, setup_announcer):
        engine, announcer, frame = setup_announcer
        frame.place_peg(4, 7, TaylorPeg.from_symbol("7"))

        cell = frame.get_cell(4, 7)
        announcer.announce_navigation("Down", cell.display_row, cell.display_col, cell)

        assert len(engine.spoken_history) == 1
        spoken = engine.last_spoken
        assert "Down." in spoken
        assert "Row 5, column 8." in spoken
        assert "Number 7" in spoken

    def test_navigation_announcement_minimal(self, setup_announcer):
        engine, announcer, frame = setup_announcer
        announcer.verbosity = VerbosityLevel.MINIMAL
        frame.place_peg(0, 1, TaylorPeg.from_symbol("+"))

        cell = frame.get_cell(0, 1)
        announcer.announce_navigation("Right", cell.display_row, cell.display_col, cell)

        assert len(engine.spoken_history) == 1
        spoken = engine.last_spoken
        assert "Col 2. +" in spoken

    def test_navigation_announcement_detailed(self, setup_announcer):
        engine, announcer, frame = setup_announcer
        announcer.verbosity = VerbosityLevel.DETAILED
        frame.place_peg(2, 3, TaylorPeg.from_symbol("7"))

        cell = frame.get_cell(2, 3)
        announcer.announce_navigation("Up", cell.display_row, cell.display_col, cell)

        spoken = engine.last_spoken
        assert "Row 3, column 4." in spoken
        assert "West" in spoken or "270" in spoken

    def test_cell_inspect(self, setup_announcer):
        engine, announcer, frame = setup_announcer
        frame.place_peg(1, 2, TaylorPeg.from_symbol("x"))

        cell = frame.get_cell(1, 2)
        announcer.announce_cell_inspect(cell)

        spoken = engine.last_spoken
        assert "Row 2, column 3." in spoken
        assert "Variable x" in spoken
        assert "Algebraic" in spoken

    def test_row_and_column_announcements(self, setup_announcer):
        engine, announcer, frame = setup_announcer
        frame.place_peg(3, 0, TaylorPeg.from_symbol("1"))
        frame.place_peg(3, 1, TaylorPeg.from_symbol("+"))
        frame.place_peg(3, 2, TaylorPeg.from_symbol("2"))

        announcer.announce_row(3, frame)
        spoken_row = engine.last_spoken
        assert "Row 4:" in spoken_row
        assert "1 plus 2" in spoken_row or "1 + 2" in spoken_row

        announcer.announce_column(0, frame)
        spoken_col = engine.last_spoken
        assert "Column 1" in spoken_col
        assert "Row 4: Number 1" in spoken_col

    def test_frame_summary(self, setup_announcer):
        engine, announcer, frame = setup_announcer
        frame.place_peg(0, 0, TaylorPeg.from_symbol("9"))
        announcer.announce_frame_summary(frame)

        spoken = engine.last_spoken
        assert "Total objects: 1" in spoken
        assert "Row 1" in spoken

    def test_verbosity_cycling(self, setup_announcer):
        engine, announcer, frame = setup_announcer
        assert announcer.verbosity == VerbosityLevel.NORMAL

        v1 = announcer.cycle_verbosity()
        assert v1 == VerbosityLevel.DETAILED
        assert "Detailed" in engine.last_spoken

        v2 = announcer.cycle_verbosity()
        assert v2 == VerbosityLevel.MINIMAL
        assert "Minimal" in engine.last_spoken

        v3 = announcer.cycle_verbosity()
        assert v3 == VerbosityLevel.NORMAL
        assert "Normal" in engine.last_spoken

    def test_selection_announcement(self, setup_announcer):
        engine, announcer, frame = setup_announcer
        sel = SelectionRange(start_row=2, start_col=3, end_row=4, end_col=6)
        announcer.announce_selection(sel)
        assert "Selected 3 rows by 4 columns" in engine.last_spoken

        announcer.announce_selection(None)
        assert "Selection cleared" in engine.last_spoken
