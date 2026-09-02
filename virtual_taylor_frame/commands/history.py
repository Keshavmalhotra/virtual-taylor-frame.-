"""
Undo/Redo command history manager for the Virtual Taylor Frame.
"""
from typing import List, Optional, Tuple, Callable
from virtual_taylor_frame.commands.base import Command
from virtual_taylor_frame.model.frame import TaylorFrame
from virtual_taylor_frame.model.types import VerbosityLevel


class UndoRedoManager:
    """
    Manages undo/redo stacks and tracks document modification state.
    """

    def __init__(self, max_depth: int = 200):
        self.max_depth = max_depth
        self._undo_stack: List[Command] = []
        self._redo_stack: List[Command] = []
        self._clean_marker: int = 0
        self._listeners: List[Callable[[], None]] = []

    def add_listener(self, callback: Callable[[], None]) -> None:
        if callback not in self._listeners:
            self._listeners.append(callback)

    def _notify(self) -> None:
        for listener in self._listeners:
            try:
                listener()
            except Exception:
                pass

    @property
    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    @property
    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    @property
    def undo_action_name(self) -> Optional[str]:
        return self._undo_stack[-1].name if self._undo_stack else None

    @property
    def redo_action_name(self) -> Optional[str]:
        return self._redo_stack[-1].name if self._redo_stack else None

    @property
    def is_dirty(self) -> bool:
        return len(self._undo_stack) != self._clean_marker

    def mark_clean(self) -> None:
        """Mark current history state as clean (e.g. after file save/load)."""
        self._clean_marker = len(self._undo_stack)
        self._notify()

    def execute_command(
        self,
        command: Command,
        frame: TaylorFrame,
        verbosity: VerbosityLevel = VerbosityLevel.NORMAL,
    ) -> Tuple[bool, str]:
        """
        Execute command on frame, add to undo stack, clear redo stack, and return speech announcement.
        """
        success = command.execute(frame)
        if success:
            self._undo_stack.append(command)
            if len(self._undo_stack) > self.max_depth:
                self._undo_stack.pop(0)
                if self._clean_marker > 0:
                    self._clean_marker -= 1
            self._redo_stack.clear()
            announcement = command.get_announcement(frame, verbosity)
            self._notify()
            return True, announcement
        return False, "Action could not be completed."

    def undo(
        self,
        frame: TaylorFrame,
        verbosity: VerbosityLevel = VerbosityLevel.NORMAL,
    ) -> Tuple[bool, str]:
        """
        Undo the most recent command on the frame.
        """
        if not self.can_undo:
            return False, "Nothing to undo."

        command = self._undo_stack.pop()
        success = command.undo(frame)
        if success:
            self._redo_stack.append(command)
            announcement = command.get_undo_announcement(frame, verbosity)
            self._notify()
            return True, announcement
        return False, "Undo failed."

    def redo(
        self,
        frame: TaylorFrame,
        verbosity: VerbosityLevel = VerbosityLevel.NORMAL,
    ) -> Tuple[bool, str]:
        """
        Redo the most recently undone command on the frame.
        """
        if not self.can_redo:
            return False, "Nothing to redo."

        command = self._redo_stack.pop()
        success = command.redo(frame)
        if success:
            self._undo_stack.append(command)
            announcement = command.get_redo_announcement(frame, verbosity)
            self._notify()
            return True, announcement
        return False, "Redo failed."

    def clear(self) -> None:
        """Reset undo and redo stacks."""
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._clean_marker = 0
        self._notify()
