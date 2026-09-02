"""
Subtle earcon sound cues for spatial boundary feedback and interaction confirmations.
"""
import sys
from typing import Optional


class AudioCues:
    """
    Provides optional audio feedback cues (earcons).
    Safely handles platform limitations without blocking.
    """

    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    def _play_tone(self, frequency: int, duration_ms: int) -> None:
        if not self.enabled:
            return
        if sys.platform == "win32":
            try:
                import winsound
                winsound.Beep(frequency, duration_ms)
            except Exception:
                pass

    def play_boundary(self) -> None:
        """Boundary warning cue."""
        self._play_tone(220, 50)

    def play_place(self) -> None:
        """Object placed confirmation cue."""
        self._play_tone(880, 40)

    def play_remove(self) -> None:
        """Object removed cue."""
        self._play_tone(440, 40)

    def play_clear(self) -> None:
        """Clear all cue."""
        self._play_tone(330, 80)
