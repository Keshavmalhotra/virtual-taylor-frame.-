"""
Accessibility Output Engine interfacing with Accessible Output 3 / Accessible Output 2,
with fallback to Windows SAPI and mock engine for testing.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
import sys


class AccessibilityEngine(ABC):
    """Abstract interface for speech and Braille accessibility output."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the active accessibility output driver."""
        pass

    @abstractmethod
    def speak(self, text: str, interrupt: bool = True) -> None:
        """Speak text through screen reader or TTS."""
        pass

    @abstractmethod
    def braille(self, text: str) -> None:
        """Output text to refreshable Braille display if available."""
        pass


class AO3Engine(AccessibilityEngine):
    """
    Accessible Output engine that automatically detects active screen readers
    (NVDA, JAWS, System Access, Window-Eyes, Windows SAPI/Narrator).
    """

    def __init__(self):
        self._ao_output = None
        self._sapi_fallback = None
        self._init_engine()

    def _init_engine(self) -> None:
        try:
            import accessible_output2.outputs.auto
            self._ao_output = accessible_output2.outputs.auto.Auto()
        except Exception:
            self._ao_output = None

        # Prepare SAPI fallback if AO is not working or returns None driver
        if sys.platform == "win32":
            try:
                import win32com.client
                self._sapi_fallback = win32com.client.Dispatch("SAPI.SpVoice")
            except Exception:
                self._sapi_fallback = None

    @property
    def name(self) -> str:
        if self._ao_output is not None:
            try:
                ao_name = self._ao_output.name
                if ao_name:
                    return f"AO ({ao_name})"
            except Exception:
                pass
        if self._sapi_fallback is not None:
            return "Windows SAPI Fallback"
        return "None (Headless)"

    def speak(self, text: str, interrupt: bool = True) -> None:
        if not text or not text.strip():
            return
        cleaned = text.strip()
        spoken = False

        if self._ao_output is not None:
            try:
                self._ao_output.speak(cleaned, interrupt=interrupt)
                spoken = True
            except Exception:
                spoken = False

        if not spoken and self._sapi_fallback is not None:
            try:
                flags = 3 if interrupt else 1  # 3 = SVSFlagsAsync | SVSFPurgeBeforeSpeak
                self._sapi_fallback.Speak(cleaned, flags)
            except Exception:
                pass

    def braille(self, text: str) -> None:
        if not text or not text.strip():
            return
        if self._ao_output is not None:
            try:
                self._ao_output.braille(text.strip())
            except Exception:
                pass


class MockSpeechEngine(AccessibilityEngine):
    """
    In-memory mock speech engine for unit tests.
    Records all spoken and brailled strings.
    """

    def __init__(self):
        self.spoken_history: List[str] = []
        self.braille_history: List[str] = []

    @property
    def name(self) -> str:
        return "Mock Speech Engine"

    def speak(self, text: str, interrupt: bool = True) -> None:
        if text:
            self.spoken_history.append(text)

    def braille(self, text: str) -> None:
        if text:
            self.braille_history.append(text)

    @property
    def last_spoken(self) -> Optional[str]:
        return self.spoken_history[-1] if self.spoken_history else None

    @property
    def last_braille(self) -> Optional[str]:
        return self.braille_history[-1] if self.braille_history else None

    def clear(self) -> None:
        self.spoken_history.clear()
        self.braille_history.clear()
