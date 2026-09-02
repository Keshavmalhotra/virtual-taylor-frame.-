"""
Comprehensive unit tests for the Taylor Frame mathematical model.
"""
import pytest
from virtual_taylor_frame.model import (
    PegOrientation,
    PegEnd,
    PegType,
    VerbosityLevel,
    TaylorPeg,
    Cell,
    TaylorFrame,
    SelectionRange,
    ClipboardBlock,
    ExpressionAnalyzer,
    TAYLOR_MAPPINGS,
)


class TestPegTypesAndMappings:
    def test_orientation_cycle(self):
        o = PegOrientation.N_0
        assert o.next_cw() == PegOrientation.NE_45
        assert o.next_cw().next_cw() == PegOrientation.E_90
        assert o.next_ccw() == PegOrientation.NW_315

    def test_orientation_from_angle(self):
        assert PegOrientation.from_angle(0) == PegOrientation.N_0
        assert PegOrientation.from_angle(45) == PegOrientation.NE_45
        assert PegOrientation.from_angle(90) == PegOrientation.E_90
        assert PegOrientation.from_angle(180) == PegOrientation.S_180
        assert PegOrientation.from_angle(270) == PegOrientation.W_270
        assert PegOrientation.from_angle(360) == PegOrientation.N_0
        assert PegOrientation.from_angle(405) == PegOrientation.NE_45

    def test_arithmetic_end_a_digits_1_to_8(self):
        expected_digits = [
            (PegOrientation.N_0, "1"),
            (PegOrientation.NE_45, "2"),
            (PegOrientation.E_90, "3"),
            (PegOrientation.SE_135, "4"),
            (PegOrientation.S_180, "5"),
            (PegOrientation.SW_225, "6"),
            (PegOrientation.W_270, "7"),
            (PegOrientation.NW_315, "8"),
        ]
        for orientation, digit in expected_digits:
            peg = TaylorPeg.from_state(PegType.ARITHMETIC, PegEnd.END_A_BAR, orientation)
            assert peg.symbol == digit
            assert peg.peg_type == PegType.ARITHMETIC
            assert peg.peg_end == PegEnd.END_A_BAR

    def test_arithmetic_end_b_operators_and_9_0(self):
        expected_symbols = [
            (PegOrientation.N_0, "9"),
            (PegOrientation.NE_45, "0"),
            (PegOrientation.E_90, "+"),
            (PegOrientation.SE_135, "-"),
            (PegOrientation.S_180, "*"),
            (PegOrientation.SW_225, "/"),
            (PegOrientation.W_270, "="),
            (PegOrientation.NW_315, "."),
        ]
        for orientation, sym in expected_symbols:
            peg = TaylorPeg.from_state(PegType.ARITHMETIC, PegEnd.END_B_DOTS, orientation)
            assert peg.symbol == sym

    def test_from_symbol_lookup(self):
        peg_7 = TaylorPeg.from_symbol("7")
        assert peg_7 is not None
        assert peg_7.symbol == "7"
        assert peg_7.orientation == PegOrientation.W_270
        assert peg_7.peg_end == PegEnd.END_A_BAR

        peg_plus = TaylorPeg.from_symbol("+")
        assert peg_plus is not None
        assert peg_plus.symbol == "+"
        assert peg_plus.orientation == PegOrientation.E_90
        assert peg_plus.peg_end == PegEnd.END_B_DOTS

        peg_x = TaylorPeg.from_symbol("x")
        assert peg_x is not None
        assert peg_x.symbol == "x"
        assert peg_x.peg_type == PegType.ALGEBRAIC

    def test_peg_rotations_and_flips(self):
        # Start with digit 1 (N_0)
        peg = TaylorPeg.from_symbol("1")
        assert peg.symbol == "1"

        # Rotate clockwise -> 2 (NE_45)
        peg_cw = peg.rotate_cw()
        assert peg_cw.symbol == "2"
        assert peg_cw.orientation == PegOrientation.NE_45

        # Flip end -> 9 (N_0 on End B)
        peg_flipped = peg.flip_end()
        assert peg_flipped.symbol == "9"
        assert peg_flipped.peg_end == PegEnd.END_B_DOTS

        # Toggle type -> Algebraic
        peg_alg = peg.toggle_type()
        assert peg_alg.peg_type == PegType.ALGEBRAIC

    def test_peg_descriptions(self):
        peg = TaylorPeg.from_symbol("7")
        assert peg.describe(VerbosityLevel.MINIMAL) == "7"
        assert "7" in peg.describe(VerbosityLevel.NORMAL)
        assert "West" in peg.describe(VerbosityLevel.DETAILED)


class TestTaylorFrameModel:
    def test_frame_initialization(self):
        frame = TaylorFrame(rows=20, cols=30)
        assert frame.rows == 20
        assert frame.cols == 30
        assert frame.cursor_row == 0
        assert frame.cursor_col == 0
        assert frame.display_cursor_row == 1
        assert frame.display_cursor_col == 1
        assert frame.count_occupied() == 0

    def test_invalid_dimensions(self):
        with pytest.raises(ValueError):
            TaylorFrame(rows=0, cols=10)
        with pytest.raises(ValueError):
            TaylorFrame(rows=10, cols=-1)

    def test_cursor_navigation_and_clamping(self):
        frame = TaylorFrame(rows=10, cols=10)
        # Move within bounds
        assert frame.move_cursor(2, 3) is True
        assert (frame.cursor_row, frame.cursor_col) == (2, 3)

        # Move beyond upper left
        frame.set_cursor(0, 0)
        assert frame.move_cursor(-1, -1) is False
        assert (frame.cursor_row, frame.cursor_col) == (0, 0)

        # Move beyond bottom right
        frame.set_cursor(9, 9)
        assert frame.move_cursor(5, 5) is False
        assert (frame.cursor_row, frame.cursor_col) == (9, 9)

    def test_place_and_remove_pegs(self):
        frame = TaylorFrame(rows=10, cols=10)
        peg7 = TaylorPeg.from_symbol("7")

        old = frame.place_peg(4, 5, peg7)
        assert old is None
        assert frame.count_occupied() == 1
        assert frame.get_cell(4, 5).is_occupied is True
        assert frame.get_cell(4, 5).peg.symbol == "7"

        # Replace peg
        peg3 = TaylorPeg.from_symbol("3")
        old = frame.place_peg(4, 5, peg3)
        assert old.symbol == "7"
        assert frame.get_cell(4, 5).peg.symbol == "3"

        # Remove peg
        removed = frame.remove_peg(4, 5)
        assert removed.symbol == "3"
        assert frame.count_occupied() == 0
        assert frame.get_cell(4, 5).is_occupied is False

    def test_jump_to_next_occupied(self):
        frame = TaylorFrame(rows=10, cols=10)
        frame.place_peg(0, 5, TaylorPeg.from_symbol("1"))
        frame.place_peg(5, 0, TaylorPeg.from_symbol("2"))

        # Jump right from (0,0) to (0,5)
        frame.set_cursor(0, 0)
        assert frame.jump_to_next_occupied(0, 1) is True
        assert (frame.cursor_row, frame.cursor_col) == (0, 5)

        # Jump down from (0,0) to (5,0)
        frame.set_cursor(0, 0)
        assert frame.jump_to_next_occupied(1, 0) is True
        assert (frame.cursor_row, frame.cursor_col) == (5, 0)

    def test_neighbor_inspection(self):
        frame = TaylorFrame(rows=10, cols=10)
        frame.place_peg(3, 5, TaylorPeg.from_symbol("1"))  # North
        frame.place_peg(5, 5, TaylorPeg.from_symbol("2"))  # South
        frame.place_peg(4, 6, TaylorPeg.from_symbol("+"))  # East

        desc = frame.describe_neighbors(4, 5)
        assert "North: Number 1" in desc
        assert "South: Number 2" in desc
        assert "East: Plus" in desc
        assert "West: empty" in desc

    def test_clear_row_and_clear_all(self):
        frame = TaylorFrame(rows=10, cols=10)
        frame.place_peg(2, 0, TaylorPeg.from_symbol("1"))
        frame.place_peg(2, 1, TaylorPeg.from_symbol("2"))
        frame.place_peg(3, 0, TaylorPeg.from_symbol("3"))

        cleared = frame.clear_row(2)
        assert len(cleared) == 2
        assert frame.count_occupied() == 1

        cleared_all = frame.clear_all()
        assert len(cleared_all) == 1
        assert frame.count_occupied() == 0

    def test_serialization_round_trip(self):
        frame = TaylorFrame(rows=15, cols=25)
        frame.place_peg(4, 7, TaylorPeg.from_symbol("7"))
        frame.place_peg(4, 8, TaylorPeg.from_symbol("+"))
        frame.place_peg(4, 9, TaylorPeg.from_symbol("3"))
        frame.set_cursor(4, 9)

        data = frame.to_dict()
        restored = TaylorFrame.from_dict(data)

        assert restored.rows == 15
        assert restored.cols == 25
        assert restored.cursor_row == 4
        assert restored.cursor_col == 9
        assert restored.count_occupied() == 3
        assert restored.get_cell(4, 7).peg.symbol == "7"
        assert restored.get_cell(4, 8).peg.symbol == "+"
        assert restored.get_cell(4, 9).peg.symbol == "3"


class TestExpressionAnalyzer:
    def test_horizontal_row_expression(self):
        frame = TaylorFrame(rows=10, cols=10)
        # Place "7 + 3 = 10"
        pegs = ["7", "+", "3", "=", "1", "0"]
        for idx, sym in enumerate(pegs):
            frame.place_peg(3, idx, TaylorPeg.from_symbol(sym))

        desc = frame.describe_row(3)
        assert "7 + 3 = 10" in desc or "7 plus 3 equals 1 0" in desc

    def test_full_frame_summary(self):
        frame = TaylorFrame(rows=20, cols=30)
        summary_empty = frame.summarize_frame()
        assert "completely empty" in summary_empty

        frame.place_peg(4, 7, TaylorPeg.from_symbol("7"))
        frame.place_peg(4, 8, TaylorPeg.from_symbol("+"))
        frame.place_peg(4, 9, TaylorPeg.from_symbol("3"))

        summary = frame.summarize_frame()
        assert "Total objects: 3" in summary
        assert "Row 5" in summary
