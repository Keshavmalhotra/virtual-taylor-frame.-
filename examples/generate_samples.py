"""
Script to generate sample .tframe examples for testing and demonstration.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from virtual_taylor_frame.model.frame import TaylorFrame
from virtual_taylor_frame.model.peg import TaylorPeg
from virtual_taylor_frame.storage.tframe_format import TFrameStorage


def generate_samples():
    examples_dir = Path("examples")
    examples_dir.mkdir(exist_ok=True)

    # 1. Simple Arithmetic
    frame1 = TaylorFrame(20, 30)
    # Row 3: 7 + 3 = 1 0
    pegs1 = [("7", 4), ("+", 6), ("3", 8), ("=", 10), ("1", 12), ("0", 13)]
    for sym, c in pegs1:
        frame1.place_peg(2, c, TaylorPeg.from_symbol(sym))

    # Row 5: 9 * 4 = 3 6
    pegs2 = [("9", 4), ("*", 6), ("4", 8), ("=", 10), ("3", 12), ("6", 13)]
    for sym, c in pegs2:
        frame1.place_peg(4, c, TaylorPeg.from_symbol(sym))

    TFrameStorage.save(
        str(examples_dir / "simple_arithmetic.tframe"),
        frame1,
        metadata={"title": "Basic Arithmetic Expressions", "notes": "Addition and multiplication rows."},
    )

    # 2. Column Addition
    frame2 = TaylorFrame(20, 30)
    # Row 3:   4 2 8
    # Row 4: + 1 3 5
    # Row 5: _ _ _ _
    # Row 6:   5 6 3
    col_pegs = [
        (2, 6, "4"), (2, 7, "2"), (2, 8, "8"),
        (3, 4, "+"), (3, 6, "1"), (3, 7, "3"), (3, 8, "5"),
        (4, 4, "_"), (4, 5, "_"), (4, 6, "_"), (4, 7, "_"), (4, 8, "_"),
        (5, 6, "5"), (5, 7, "6"), (5, 8, "3"),
    ]
    for r, c, sym in col_pegs:
        frame2.place_peg(r, c, TaylorPeg.from_symbol(sym))

    TFrameStorage.save(
        str(examples_dir / "column_addition.tframe"),
        frame2,
        metadata={"title": "Column Addition 428 + 135", "notes": "Vertical column alignment practice."},
    )

    # 3. Algebra Equation
    frame3 = TaylorFrame(20, 30)
    # Row 4: 2 x + 5 = 1 5
    # Row 6: 2 x = 1 0
    # Row 8: x = 5
    alg_pegs = [
        (3, 4, "2"), (3, 5, "x"), (3, 7, "+"), (3, 9, "5"), (3, 11, "="), (3, 13, "1"), (3, 14, "5"),
        (5, 4, "2"), (5, 5, "x"), (5, 11, "="), (5, 13, "1"), (5, 14, "0"),
        (7, 5, "x"), (7, 11, "="), (7, 14, "5"),
    ]
    for r, c, sym in alg_pegs:
        frame3.place_peg(r, c, TaylorPeg.from_symbol(sym))

    TFrameStorage.save(
        str(examples_dir / "linear_equation.tframe"),
        frame3,
        metadata={"title": "Linear Equation: 2x + 5 = 15", "notes": "Step-by-step linear equation resolution."},
    )

    print("Sample .tframe files successfully generated in examples/")


if __name__ == "__main__":
    generate_samples()
