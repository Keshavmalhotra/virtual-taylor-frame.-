"""
Base classes for the Command pattern implementation in Virtual Taylor Frame.
"""
from abc import ABC, abstractmethod
from typing import Optional

from virtual_taylor_frame.model.frame import TaylorFrame
from virtual_taylor_frame.model.types import VerbosityLevel


class Command(ABC):
    """
    Abstract base command for all reversible operations on the mathematical Taylor Frame.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Short human-readable name of the command (e.g. 'Place 7')."""
        pass

    @abstractmethod
    def execute(self, frame: TaylorFrame) -> bool:
        """
        Execute the operation on the given Taylor Frame.
        Returns True if the operation caused a state change.
        """
        pass

    @abstractmethod
    def undo(self, frame: TaylorFrame) -> bool:
        """
        Revert the operation on the given Taylor Frame.
        Returns True if successfully reverted.
        """
        pass

    def redo(self, frame: TaylorFrame) -> bool:
        """
        Re-execute the operation. Defaults to execute(frame).
        """
        return self.execute(frame)

    @abstractmethod
    def get_announcement(self, frame: TaylorFrame, verbosity: VerbosityLevel) -> str:
        """
        Generate the accessible speech announcement upon successful execution.
        """
        pass

    def get_undo_announcement(self, frame: TaylorFrame, verbosity: VerbosityLevel) -> str:
        """
        Generate the speech announcement when this command is undone.
        """
        return f"Undone: {self.name}."

    def get_redo_announcement(self, frame: TaylorFrame, verbosity: VerbosityLevel) -> str:
        """
        Generate the speech announcement when this command is redone.
        """
        return f"Redone: {self.name}."
