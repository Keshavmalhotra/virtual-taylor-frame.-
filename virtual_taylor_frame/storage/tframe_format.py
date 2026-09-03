"""
Native .tframe file format handler with schema validation, format versioning, and persistence.
"""
import json
import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

from virtual_taylor_frame.model.frame import TaylorFrame


FORMAT_NAME = "TaylorFrame"
CURRENT_FORMAT_VERSION = "1.0.0"
APP_NAME = "Virtual Taylor Frame"
APP_VERSION = "0.1.0"


class TFrameError(Exception):
    """Base exception for .tframe file operations."""
    pass


class InvalidTFrameError(TFrameError):
    """Raised when file structure is malformed or invalid JSON."""
    pass


class IncompatibleVersionError(TFrameError):
    """Raised when file format version is unsupported."""
    pass


class TFrameStorage:
    """
    Handles saving and loading native .tframe files.
    """

    @staticmethod
    def save(
        filepath: str,
        frame: TaylorFrame,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Save TaylorFrame to a .tframe file.
        """
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        path = Path(filepath)

        doc: Dict[str, Any] = {
            "format_name": FORMAT_NAME,
            "format_version": CURRENT_FORMAT_VERSION,
            "app_name": APP_NAME,
            "app_version": APP_VERSION,
            "saved_at": now_iso,
            "metadata": metadata or {
                "title": path.stem,
                "notes": "",
            },
            **frame.to_dict(),
        }

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(doc, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise TFrameError(f"Failed to save {filepath}: {e}") from e

    @staticmethod
    def load(filepath: str) -> Tuple[TaylorFrame, Dict[str, Any]]:
        """
        Load a .tframe file and return the instantiated TaylorFrame and file metadata.
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                doc = json.load(f)
        except json.JSONDecodeError as e:
            raise InvalidTFrameError(f"Malformed JSON in {filepath}: {e}") from e
        except Exception as e:
            raise TFrameError(f"Failed to read file {filepath}: {e}") from e

        if not isinstance(doc, dict):
            raise InvalidTFrameError("Root JSON structure must be an object.")

        fmt_name = doc.get("format_name")
        if fmt_name != FORMAT_NAME:
            raise InvalidTFrameError(
                f"Invalid format identifier '{fmt_name}'. Expected '{FORMAT_NAME}'."
            )

        fmt_version = doc.get("format_version", "1.0.0")
        major_ver = fmt_version.split(".")[0]
        if major_ver != "1":
            raise IncompatibleVersionError(
                f"Unsupported format version {fmt_version}. Only 1.x is supported."
            )

        try:
            frame = TaylorFrame.from_dict(doc)
        except Exception as e:
            raise InvalidTFrameError(f"Failed to reconstruct frame from data: {e}") from e

        metadata = doc.get("metadata", {})
        return frame, metadata
