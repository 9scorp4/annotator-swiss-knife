"""
Undo/Redo system for tool widgets.

Provides a QUndoStack-based system for tracking and reverting user actions.
"""

from typing import Any, Callable, Optional, Dict
from PyQt5.QtWidgets import QUndoStack, QUndoCommand
from PyQt5.QtCore import QObject, pyqtSignal

from ....utils import logger


class UndoableCommand(QUndoCommand):
    """
    Generic undoable command that wraps do/undo functions.

    Features:
    - Execute and undo via callbacks
    - Descriptive text for undo history
    - Data payload for state restoration
    """

    def __init__(
        self,
        text: str,
        do_func: Callable,
        undo_func: Callable,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize undoable command.

        Args:
            text: Description of the action (e.g., "Add Turn", "Delete Field")
            do_func: Function to execute the action
            undo_func: Function to undo the action
            data: Optional data payload for state restoration
        """
        super().__init__(text)
        self.do_func = do_func
        self.undo_func = undo_func
        self.data = data or {}

    def redo(self) -> None:
        """Execute the action."""
        try:
            self.do_func(self.data)
            logger.debug(f"Executed: {self.text()}")
        except Exception as e:
            logger.error(f"Failed to execute {self.text()}: {e}")

    def undo(self) -> None:
        """Undo the action."""
        try:
            self.undo_func(self.data)
            logger.debug(f"Undone: {self.text()}")
        except Exception as e:
            logger.error(f"Failed to undo {self.text()}: {e}")


class UndoRedoManager(QObject):
    """
    Manages undo/redo operations for a widget.

    Features:
    - QUndoStack-based command history
    - Keyboard shortcuts (Ctrl+Z, Ctrl+Shift+Z)
    - State change notifications
    - Undo/redo availability signals
    - Command history with descriptions
    """

    # Signals
    can_undo_changed = pyqtSignal(bool, str)  # can_undo, description
    can_redo_changed = pyqtSignal(bool, str)  # can_redo, description
    clean_changed = pyqtSignal(bool)  # is_clean (no unsaved changes)

    def __init__(self, parent: Optional[QObject] = None):
        """
        Initialize undo/redo manager.

        Args:
            parent: Parent QObject
        """
        super().__init__(parent)

        # Create undo stack
        self.stack = QUndoStack(self)

        # Connect signals
        self.stack.canUndoChanged.connect(self._on_can_undo_changed)
        self.stack.canRedoChanged.connect(self._on_can_redo_changed)
        self.stack.cleanChanged.connect(self.clean_changed.emit)

        logger.debug("UndoRedoManager initialized")

    def push(
        self,
        text: str,
        do_func: Callable,
        undo_func: Callable,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Push a new undoable command onto the stack.

        Args:
            text: Description of the action
            do_func: Function to execute the action
            undo_func: Function to undo the action
            data: Optional data payload
        """
        command = UndoableCommand(text, do_func, undo_func, data)
        self.stack.push(command)

    def undo(self) -> None:
        """Undo the last action."""
        if self.stack.canUndo():
            self.stack.undo()

    def redo(self) -> None:
        """Redo the last undone action."""
        if self.stack.canRedo():
            self.stack.redo()

    def clear(self) -> None:
        """Clear the undo/redo history."""
        self.stack.clear()
        logger.debug("Undo/redo history cleared")

    def set_clean(self) -> None:
        """Mark the current state as clean (saved)."""
        self.stack.setClean()

    def is_clean(self) -> bool:
        """
        Check if the state is clean (no unsaved changes).

        Returns:
            True if clean
        """
        return self.stack.isClean()

    def can_undo(self) -> bool:
        """
        Check if undo is available.

        Returns:
            True if can undo
        """
        return self.stack.canUndo()

    def can_redo(self) -> bool:
        """
        Check if redo is available.

        Returns:
            True if can redo
        """
        return self.stack.canRedo()

    def undo_text(self) -> str:
        """
        Get description of action that will be undone.

        Returns:
            Undo action description
        """
        return self.stack.undoText()

    def redo_text(self) -> str:
        """
        Get description of action that will be redone.

        Returns:
            Redo action description
        """
        return self.stack.redoText()

    def count(self) -> int:
        """
        Get number of commands in the stack.

        Returns:
            Command count
        """
        return self.stack.count()

    def index(self) -> int:
        """
        Get current index in the stack.

        Returns:
            Current index
        """
        return self.stack.index()

    def _on_can_undo_changed(self, can_undo: bool) -> None:
        """Handle can undo state change."""
        text = self.undo_text() if can_undo else ""
        self.can_undo_changed.emit(can_undo, text)

    def _on_can_redo_changed(self, can_redo: bool) -> None:
        """Handle can redo state change."""
        text = self.redo_text() if can_redo else ""
        self.can_redo_changed.emit(can_redo, text)


class UndoRedoMixin:
    """
    Mixin class to add undo/redo functionality to widgets.

    Usage:
        class MyWidget(QWidget, UndoRedoMixin):
            def __init__(self):
                super().__init__()
                self._init_undo_redo()

            def some_action(self):
                old_value = self.value
                new_value = self.calculate_new_value()

                self.undo_manager.push(
                    "Change Value",
                    lambda d: setattr(self, 'value', d['new']),
                    lambda d: setattr(self, 'value', d['old']),
                    {'old': old_value, 'new': new_value}
                )
                self.value = new_value
    """

    def _init_undo_redo(self) -> None:
        """Initialize undo/redo manager."""
        self.undo_manager = UndoRedoManager(self)

        # Connect to update UI
        self.undo_manager.can_undo_changed.connect(self._on_undo_state_changed)
        self.undo_manager.can_redo_changed.connect(self._on_redo_state_changed)

    def _on_undo_state_changed(self, can_undo: bool, text: str) -> None:
        """
        Handle undo state change.

        Override this method to update UI elements (e.g., menu items, buttons).

        Args:
            can_undo: Whether undo is available
            text: Description of action to undo
        """
        pass

    def _on_redo_state_changed(self, can_redo: bool, text: str) -> None:
        """
        Handle redo state change.

        Override this method to update UI elements.

        Args:
            can_redo: Whether redo is available
            text: Description of action to redo
        """
        pass
