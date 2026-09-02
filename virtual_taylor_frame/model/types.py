"""
Core types, enumerations, and symbol mappings for the Virtual Taylor Frame.
"""
from enum import Enum, IntEnum
from typing import Dict, Tuple, Optional, List


class PegOrientation(IntEnum):
    """
    The 8 rotational orientations of a peg in an octagonal socket (in degrees).
    0° is North (Up), moving clockwise in 45° increments.
    """
    N_0 = 0
    NE_45 = 45
    E_90 = 90
    SE_135 = 135
    S_180 = 180
    SW_225 = 225
    W_270 = 270
    NW_315 = 315

    def next_cw(self) -> "PegOrientation":
        """Return the next orientation 45 degrees clockwise."""
        members = list(PegOrientation)
        idx = members.index(self)
        return members[(idx + 1) % len(members)]

    def next_ccw(self) -> "PegOrientation":
        """Return the next orientation 45 degrees counter-clockwise."""
        members = list(PegOrientation)
        idx = members.index(self)
        return members[(idx - 1) % len(members)]

    @classmethod
    def from_angle(cls, angle: int) -> "PegOrientation":
        """Resolve angle modulo 360 to the nearest 45 degree orientation."""
        normalized = ((int(angle) % 360) // 45) * 45
        for member in cls:
            if member.value == normalized:
                return member
        return cls.N_0

    @property
    def compass_name(self) -> str:
        names = {
            0: "North (Up)",
            45: "North-East",
            90: "East (Right)",
            135: "South-East",
            180: "South (Down)",
            225: "South-West",
            270: "West (Left)",
            315: "North-West",
        }
        return names.get(self.value, f"{self.value}°")

    @property
    def short_compass(self) -> str:
        names = {
            0: "N",
            45: "NE",
            90: "E",
            135: "SE",
            180: "S",
            225: "SW",
            270: "W",
            315: "NW",
        }
        return names.get(self.value, f"{self.value}°")


class PegEnd(str, Enum):
    """The tactile end of the peg currently inserted facing upwards."""
    END_A_BAR = "END_A_BAR"          # Arithmetic: Single raised bar / line
    END_B_DOTS = "END_B_DOTS"        # Arithmetic: Two raised dots / points
    END_A_ALGEBRA = "END_A_ALGEBRA"  # Algebraic: V-angle / variable ridge
    END_B_ALGEBRA = "END_B_ALGEBRA"  # Algebraic: Double ridge / symbol notch

    @property
    def friendly_name(self) -> str:
        names = {
            PegEnd.END_A_BAR: "End A (Raised Bar)",
            PegEnd.END_B_DOTS: "End B (Two Dots)",
            PegEnd.END_A_ALGEBRA: "Algebra End A (Angle)",
            PegEnd.END_B_ALGEBRA: "Algebra End B (Double Bar)",
        }
        return names.get(self, self.value)


class PegType(str, Enum):
    """The family of peg."""
    ARITHMETIC = "ARITHMETIC"
    ALGEBRAIC = "ALGEBRAIC"

    @property
    def friendly_name(self) -> str:
        return "Arithmetic" if self == PegType.ARITHMETIC else "Algebraic"


class VerbosityLevel(str, Enum):
    """Speech and accessibility verbosity mode."""
    MINIMAL = "minimal"
    NORMAL = "normal"
    DETAILED = "detailed"

    def next(self) -> "VerbosityLevel":
        order = [VerbosityLevel.MINIMAL, VerbosityLevel.NORMAL, VerbosityLevel.DETAILED]
        idx = order.index(self)
        return order[(idx + 1) % len(order)]


# Mathematical definition specifications:
# Map (PegType, PegEnd, PegOrientation) -> (Symbol, Spoken Label, Braille Char, Speech Description)
TAYLOR_MAPPINGS: Dict[Tuple[PegType, PegEnd, PegOrientation], Tuple[str, str, str, str]] = {
    # Arithmetic End A (Bar): Digits 1 to 8
    (PegType.ARITHMETIC, PegEnd.END_A_BAR, PegOrientation.N_0): ("1", "Number 1", "⠼⠁", "Digit 1"),
    (PegType.ARITHMETIC, PegEnd.END_A_BAR, PegOrientation.NE_45): ("2", "Number 2", "⠼⠃", "Digit 2"),
    (PegType.ARITHMETIC, PegEnd.END_A_BAR, PegOrientation.E_90): ("3", "Number 3", "⠼⠉", "Digit 3"),
    (PegType.ARITHMETIC, PegEnd.END_A_BAR, PegOrientation.SE_135): ("4", "Number 4", "⠼⠙", "Digit 4"),
    (PegType.ARITHMETIC, PegEnd.END_A_BAR, PegOrientation.S_180): ("5", "Number 5", "⠼⠑", "Digit 5"),
    (PegType.ARITHMETIC, PegEnd.END_A_BAR, PegOrientation.SW_225): ("6", "Number 6", "⠼⠋", "Digit 6"),
    (PegType.ARITHMETIC, PegEnd.END_A_BAR, PegOrientation.W_270): ("7", "Number 7", "⠼⠛", "Digit 7"),
    (PegType.ARITHMETIC, PegEnd.END_A_BAR, PegOrientation.NW_315): ("8", "Number 8", "⠼⠓", "Digit 8"),

    # Arithmetic End B (Two Dots): 9, 0, +, -, *, /, =, .
    (PegType.ARITHMETIC, PegEnd.END_B_DOTS, PegOrientation.N_0): ("9", "Number 9", "⠼⠊", "Digit 9"),
    (PegType.ARITHMETIC, PegEnd.END_B_DOTS, PegOrientation.NE_45): ("0", "Number 0", "⠼⠚", "Digit 0"),
    (PegType.ARITHMETIC, PegEnd.END_B_DOTS, PegOrientation.E_90): ("+", "Plus", "⠬", "Plus sign"),
    (PegType.ARITHMETIC, PegEnd.END_B_DOTS, PegOrientation.SE_135): ("-", "Minus", "⠤", "Minus sign"),
    (PegType.ARITHMETIC, PegEnd.END_B_DOTS, PegOrientation.S_180): ("*", "Times", "⠡", "Multiplication sign"),
    (PegType.ARITHMETIC, PegEnd.END_B_DOTS, PegOrientation.SW_225): ("/", "Divided by", "⠌", "Division sign"),
    (PegType.ARITHMETIC, PegEnd.END_B_DOTS, PegOrientation.W_270): ("=", "Equals", "⠿", "Equals sign"),
    (PegType.ARITHMETIC, PegEnd.END_B_DOTS, PegOrientation.NW_315): (".", "Decimal point", "⠨", "Decimal point / fraction bar"),

    # Algebraic End A (Angle / Variables): x, y, z, a, b, c, d, e
    (PegType.ALGEBRAIC, PegEnd.END_A_ALGEBRA, PegOrientation.N_0): ("x", "Variable x", "⠭", "Variable x"),
    (PegType.ALGEBRAIC, PegEnd.END_A_ALGEBRA, PegOrientation.NE_45): ("y", "Variable y", "⠽", "Variable y"),
    (PegType.ALGEBRAIC, PegEnd.END_A_ALGEBRA, PegOrientation.E_90): ("z", "Variable z", "⠵", "Variable z"),
    (PegType.ALGEBRAIC, PegEnd.END_A_ALGEBRA, PegOrientation.SE_135): ("a", "Letter a", "⠁", "Letter a"),
    (PegType.ALGEBRAIC, PegEnd.END_A_ALGEBRA, PegOrientation.S_180): ("b", "Letter b", "⠃", "Letter b"),
    (PegType.ALGEBRAIC, PegEnd.END_A_ALGEBRA, PegOrientation.SW_225): ("c", "Letter c", "⠉", "Letter c"),
    (PegType.ALGEBRAIC, PegEnd.END_A_ALGEBRA, PegOrientation.W_270): ("d", "Letter d", "⠙", "Letter d"),
    (PegType.ALGEBRAIC, PegEnd.END_A_ALGEBRA, PegOrientation.NW_315): ("e", "Letter e", "⠑", "Letter e"),

    # Algebraic End B (Double Ridge / Symbols): (, ), ^, √, comma, colon, semicolon, underscore (line)
    (PegType.ALGEBRAIC, PegEnd.END_B_ALGEBRA, PegOrientation.N_0): ("(", "Open parenthesis", "⠷", "Open parenthesis"),
    (PegType.ALGEBRAIC, PegEnd.END_B_ALGEBRA, PegOrientation.NE_45): (")", "Close parenthesis", "⠾", "Close parenthesis"),
    (PegType.ALGEBRAIC, PegEnd.END_B_ALGEBRA, PegOrientation.E_90): ("^", "Power", "⠘", "Superscript / exponent"),
    (PegType.ALGEBRAIC, PegEnd.END_B_ALGEBRA, PegOrientation.SE_135): ("√", "Square root", "⠜", "Square root radical"),
    (PegType.ALGEBRAIC, PegEnd.END_B_ALGEBRA, PegOrientation.S_180): (",", "Comma", "⠂", "Comma separator"),
    (PegType.ALGEBRAIC, PegEnd.END_B_ALGEBRA, PegOrientation.SW_225): (";", "Semicolon", "⠆", "Semicolon"),
    (PegType.ALGEBRAIC, PegEnd.END_B_ALGEBRA, PegOrientation.W_270): (":", "Ratio / Colon", "⠒", "Ratio colon"),
    (PegType.ALGEBRAIC, PegEnd.END_B_ALGEBRA, PegOrientation.NW_315): ("_", "Horizontal line", "⠒⠒", "Horizontal fraction line"),
}

# Reverse mapping: Char/Symbol -> (PegType, PegEnd, PegOrientation)
SYMBOL_TO_PEG: Dict[str, Tuple[PegType, PegEnd, PegOrientation]] = {}

# Alternate symbol aliases (e.g. 'x' vs 'X', '×' vs '*', '÷' vs '/')
SYMBOL_ALIASES: Dict[str, str] = {
    "X": "x",
    "Y": "y",
    "Z": "z",
    "A": "a",
    "B": "b",
    "C": "c",
    "D": "d",
    "E": "e",
    "×": "*",
    "÷": "/",
    "−": "-",
    "–": "-",
    "—": "-",
    "r": "√",
    "R": "√",
    "[": "(",
    "]": ")",
    "{": "(",
    "}": ")",
}

for key, (sym, _, _, _) in TAYLOR_MAPPINGS.items():
    if sym not in SYMBOL_TO_PEG:
        SYMBOL_TO_PEG[sym] = key
