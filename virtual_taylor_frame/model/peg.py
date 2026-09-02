"""
Mathematical representation of a Taylor Frame peg (type).
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any

from virtual_taylor_frame.model.types import (
    PegType,
    PegEnd,
    PegOrientation,
    VerbosityLevel,
    TAYLOR_MAPPINGS,
    SYMBOL_TO_PEG,
    SYMBOL_ALIASES,
)


@dataclass(frozen=True)
class TaylorPeg:
    """
    Immutable value object representing a single Taylor peg placed in a cell.
    """
    peg_type: PegType
    peg_end: PegEnd
    orientation: PegOrientation
    symbol: str
    label: str
    braille: str
    description: str

    @classmethod
    def from_state(
        cls,
        peg_type: PegType,
        peg_end: PegEnd,
        orientation: PegOrientation,
    ) -> "TaylorPeg":
        """
        Create a TaylorPeg instance resolved from type, end, and orientation.
        """
        mapping_key = (peg_type, peg_end, orientation)
        if mapping_key in TAYLOR_MAPPINGS:
            symbol, label, braille, desc = TAYLOR_MAPPINGS[mapping_key]
        else:
            symbol = "?"
            label = f"Unknown peg ({peg_type.value}, {peg_end.value}, {orientation.value}°)"
            braille = "⠿"
            desc = label

        return cls(
            peg_type=peg_type,
            peg_end=peg_end,
            orientation=orientation,
            symbol=symbol,
            label=label,
            braille=braille,
            description=desc,
        )

    @classmethod
    def from_symbol(cls, symbol: str) -> Optional["TaylorPeg"]:
        """
        Construct a TaylorPeg from a mathematical symbol/character.
        Handles aliases automatically.
        """
        resolved_sym = SYMBOL_ALIASES.get(symbol, symbol)
        if resolved_sym in SYMBOL_TO_PEG:
            peg_type, peg_end, orientation = SYMBOL_TO_PEG[resolved_sym]
            return cls.from_state(peg_type, peg_end, orientation)
        return None

    def rotate_cw(self) -> "TaylorPeg":
        """Return a new peg rotated 45 degrees clockwise."""
        new_orientation = self.orientation.next_cw()
        return TaylorPeg.from_state(self.peg_type, self.peg_end, new_orientation)

    def rotate_ccw(self) -> "TaylorPeg":
        """Return a new peg rotated 45 degrees counter-clockwise."""
        new_orientation = self.orientation.next_ccw()
        return TaylorPeg.from_state(self.peg_type, self.peg_end, new_orientation)

    def flip_end(self) -> "TaylorPeg":
        """
        Flip the physical peg upside down (invert ends) preserving current orientation.
        """
        if self.peg_type == PegType.ARITHMETIC:
            new_end = (
                PegEnd.END_B_DOTS
                if self.peg_end == PegEnd.END_A_BAR
                else PegEnd.END_A_BAR
            )
        else:
            new_end = (
                PegEnd.END_B_ALGEBRA
                if self.peg_end == PegEnd.END_A_ALGEBRA
                else PegEnd.END_A_ALGEBRA
            )
        return TaylorPeg.from_state(self.peg_type, new_end, self.orientation)

    def toggle_type(self) -> "TaylorPeg":
        """
        Switch between Arithmetic and Algebraic peg family.
        """
        if self.peg_type == PegType.ARITHMETIC:
            new_type = PegType.ALGEBRAIC
            new_end = (
                PegEnd.END_A_ALGEBRA
                if self.peg_end == PegEnd.END_A_BAR
                else PegEnd.END_B_ALGEBRA
            )
        else:
            new_type = PegType.ARITHMETIC
            new_end = (
                PegEnd.END_A_BAR
                if self.peg_end == PegEnd.END_A_ALGEBRA
                else PegEnd.END_B_DOTS
            )
        return TaylorPeg.from_state(new_type, new_end, self.orientation)

    def describe(self, verbosity: VerbosityLevel = VerbosityLevel.NORMAL) -> str:
        """
        Generate screen reader accessible description for this peg.
        """
        if verbosity == VerbosityLevel.MINIMAL:
            return self.symbol
        elif verbosity == VerbosityLevel.NORMAL:
            return self.label
        else:  # DETAILED
            return (
                f"{self.label} (Symbol: '{self.symbol}', {self.peg_type.friendly_name} Type, "
                f"{self.peg_end.friendly_name}, {self.orientation.value}° {self.orientation.compass_name})"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize peg to dictionary for .tframe JSON format."""
        return {
            "type": self.peg_type.value,
            "end": self.peg_end.value,
            "orientation_deg": self.orientation.value,
            "symbol": self.symbol,
            "label": self.label,
            "braille": self.braille,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaylorPeg":
        """Deserialize peg from dictionary."""
        peg_type = PegType(data.get("type", PegType.ARITHMETIC.value))
        peg_end = PegEnd(data.get("end", PegEnd.END_A_BAR.value))
        orientation = PegOrientation.from_angle(data.get("orientation_deg", 0))
        return cls.from_state(peg_type, peg_end, orientation)
