"""
Unit tests for undo/redo system.

This module tests UndoableCommand, UndoRedoManager, and UndoRedoMixin
for tracking and reverting user actions.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QObject

from annotation_toolkit.ui.gui.utils.undo_redo import (
    UndoableCommand,
    UndoRedoManager,
    UndoRedoMixin
)


class TestUndoableCommand(unittest.TestCase):
    """Test UndoableCommand class."""

    def test_undoable_command_initialization(self):
        """Test UndoableCommand initializes correctly."""
        do_func = Mock()
        undo_func = Mock()
        data = {"key": "value"}

        command = UndoableCommand("Test Action", do_func, undo_func, data)

        self.assertEqual(command.text(), "Test Action")
        self.assertEqual(command.do_func, do_func)
        self.assertEqual(command.undo_func, undo_func)
        self.assertEqual(command.data, data)

    def test_undoable_command_with_no_data(self):
        """Test UndoableCommand with no data parameter."""
        do_func = Mock()
        undo_func = Mock()

        command = UndoableCommand("Test Action", do_func, undo_func)

        self.assertEqual(command.data, {})

    def test_redo_calls_do_func(self):
        """Test redo calls the do function."""
        do_func = Mock()
        undo_func = Mock()
        data = {"value": 42}

        command = UndoableCommand("Test", do_func, undo_func, data)
        command.redo()

        do_func.assert_called_once_with(data)

    def test_undo_calls_undo_func(self):
        """Test undo calls the undo function."""
        do_func = Mock()
        undo_func = Mock()
        data = {"value": 42}

        command = UndoableCommand("Test", do_func, undo_func, data)
        command.undo()

        undo_func.assert_called_once_with(data)

    def test_redo_handles_exception(self):
        """Test redo handles exceptions gracefully."""
        def failing_func(data):
            raise ValueError("Test error")

        undo_func = Mock()
        command = UndoableCommand("Test", failing_func, undo_func)

        # Should not raise exception
        command.redo()

    def test_undo_handles_exception(self):
        """Test undo handles exceptions gracefully."""
        do_func = Mock()

        def failing_func(data):
            raise ValueError("Test error")

        command = UndoableCommand("Test", do_func, failing_func)

        # Should not raise exception
        command.undo()


class TestUndoRedoManagerInit(unittest.TestCase):
    """Test UndoRedoManager initialization."""

    def test_undo_redo_manager_initialization(self):
        """Test UndoRedoManager initializes correctly."""
        manager = UndoRedoManager()

        self.assertIsNotNone(manager.stack)

    def test_undo_redo_manager_with_parent(self):
        """Test UndoRedoManager with parent QObject."""
        parent = QObject()
        manager = UndoRedoManager(parent)

        self.assertEqual(manager.parent(), parent)

    def test_undo_redo_manager_initial_state(self):
        """Test UndoRedoManager initial state."""
        manager = UndoRedoManager()

        self.assertFalse(manager.can_undo())
        self.assertFalse(manager.can_redo())
        self.assertTrue(manager.is_clean())
        self.assertEqual(manager.count(), 0)
        self.assertEqual(manager.index(), 0)


class TestUndoRedoManagerPush(unittest.TestCase):
    """Test UndoRedoManager push functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = UndoRedoManager()

    def test_push_command(self):
        """Test pushing a command onto the stack."""
        do_func = Mock()
        undo_func = Mock()

        self.manager.push("Test Action", do_func, undo_func)

        self.assertEqual(self.manager.count(), 1)
        self.assertTrue(self.manager.can_undo())

    def test_push_executes_command(self):
        """Test pushing a command executes it."""
        do_func = Mock()
        undo_func = Mock()
        data = {"value": 42}

        self.manager.push("Test Action", do_func, undo_func, data)

        # Command is executed when pushed
        do_func.assert_called_once_with(data)

    def test_push_multiple_commands(self):
        """Test pushing multiple commands."""
        do_func = Mock()
        undo_func = Mock()

        self.manager.push("Action 1", do_func, undo_func)
        self.manager.push("Action 2", do_func, undo_func)
        self.manager.push("Action 3", do_func, undo_func)

        self.assertEqual(self.manager.count(), 3)

    def test_push_with_data(self):
        """Test pushing command with data payload."""
        do_func = Mock()
        undo_func = Mock()
        data = {"old": 1, "new": 2}

        self.manager.push("Change Value", do_func, undo_func, data)

        do_func.assert_called_once_with(data)


class TestUndoRedoManagerUndo(unittest.TestCase):
    """Test UndoRedoManager undo functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = UndoRedoManager()

    def test_undo_when_nothing_to_undo(self):
        """Test undo does nothing when stack is empty."""
        # Should not raise error
        self.manager.undo()

        self.assertFalse(self.manager.can_undo())

    def test_undo_calls_undo_func(self):
        """Test undo calls the undo function."""
        do_func = Mock()
        undo_func = Mock()

        self.manager.push("Test", do_func, undo_func)
        self.manager.undo()

        undo_func.assert_called_once()

    def test_undo_decrements_index(self):
        """Test undo decrements the stack index."""
        do_func = Mock()
        undo_func = Mock()

        self.manager.push("Test", do_func, undo_func)
        initial_index = self.manager.index()

        self.manager.undo()

        self.assertEqual(self.manager.index(), initial_index - 1)

    def test_undo_multiple_times(self):
        """Test undoing multiple commands."""
        do_func = Mock()
        undo_func = Mock()

        self.manager.push("Action 1", do_func, undo_func)
        self.manager.push("Action 2", do_func, undo_func)
        self.manager.push("Action 3", do_func, undo_func)

        self.manager.undo()
        self.manager.undo()

        # Should have undone 2 times
        self.assertEqual(undo_func.call_count, 2)


class TestUndoRedoManagerRedo(unittest.TestCase):
    """Test UndoRedoManager redo functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = UndoRedoManager()

    def test_redo_when_nothing_to_redo(self):
        """Test redo does nothing when nothing to redo."""
        # Should not raise error
        self.manager.redo()

        self.assertFalse(self.manager.can_redo())

    def test_redo_after_undo(self):
        """Test redo after undo."""
        do_func = Mock()
        undo_func = Mock()

        self.manager.push("Test", do_func, undo_func)
        self.manager.undo()

        do_func.reset_mock()  # Clear previous call from push
        self.manager.redo()

        # Redo should call do_func again
        do_func.assert_called_once()

    def test_redo_increments_index(self):
        """Test redo increments the stack index."""
        do_func = Mock()
        undo_func = Mock()

        self.manager.push("Test", do_func, undo_func)
        self.manager.undo()

        index_before_redo = self.manager.index()
        self.manager.redo()

        self.assertEqual(self.manager.index(), index_before_redo + 1)

    def test_redo_multiple_times(self):
        """Test redoing multiple commands."""
        do_func = Mock()
        undo_func = Mock()

        self.manager.push("Action 1", do_func, undo_func)
        self.manager.push("Action 2", do_func, undo_func)

        self.manager.undo()
        self.manager.undo()

        do_func.reset_mock()
        self.manager.redo()
        self.manager.redo()

        # Should have redone 2 times
        self.assertEqual(do_func.call_count, 2)

    def test_push_after_undo_clears_redo_stack(self):
        """Test pushing a new command after undo clears redo stack."""
        do_func = Mock()
        undo_func = Mock()

        self.manager.push("Action 1", do_func, undo_func)
        self.manager.push("Action 2", do_func, undo_func)
        self.manager.undo()

        # Can redo at this point
        self.assertTrue(self.manager.can_redo())

        # Push new command
        self.manager.push("Action 3", do_func, undo_func)

        # Can no longer redo
        self.assertFalse(self.manager.can_redo())


class TestUndoRedoManagerClear(unittest.TestCase):
    """Test UndoRedoManager clear functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = UndoRedoManager()

    def test_clear_empties_stack(self):
        """Test clear empties the undo stack."""
        do_func = Mock()
        undo_func = Mock()

        self.manager.push("Action 1", do_func, undo_func)
        self.manager.push("Action 2", do_func, undo_func)

        self.manager.clear()

        self.assertEqual(self.manager.count(), 0)
        self.assertFalse(self.manager.can_undo())
        self.assertFalse(self.manager.can_redo())

    def test_clear_resets_clean_state(self):
        """Test clear resets clean state."""
        do_func = Mock()
        undo_func = Mock()

        self.manager.push("Action", do_func, undo_func)
        self.manager.set_clean()

        self.manager.clear()

        # After clear, should be clean
        self.assertTrue(self.manager.is_clean())


class TestUndoRedoManagerCleanState(unittest.TestCase):
    """Test UndoRedoManager clean state functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = UndoRedoManager()

    def test_is_clean_initially_true(self):
        """Test is_clean returns True initially."""
        self.assertTrue(self.manager.is_clean())

    def test_push_marks_not_clean(self):
        """Test pushing a command marks state as not clean."""
        do_func = Mock()
        undo_func = Mock()

        self.manager.push("Test", do_func, undo_func)

        self.assertFalse(self.manager.is_clean())

    def test_set_clean_marks_clean(self):
        """Test set_clean marks state as clean."""
        do_func = Mock()
        undo_func = Mock()

        self.manager.push("Test", do_func, undo_func)
        self.manager.set_clean()

        self.assertTrue(self.manager.is_clean())

    def test_clean_state_after_undo_to_clean_point(self):
        """Test state becomes clean after undoing to clean point."""
        do_func = Mock()
        undo_func = Mock()

        self.manager.push("Test", do_func, undo_func)
        self.manager.set_clean()

        self.manager.push("Another", do_func, undo_func)
        self.assertFalse(self.manager.is_clean())

        # Undo to clean point
        self.manager.undo()
        self.assertTrue(self.manager.is_clean())


class TestUndoRedoManagerText(unittest.TestCase):
    """Test UndoRedoManager text descriptions."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = UndoRedoManager()

    def test_undo_text_empty_when_nothing_to_undo(self):
        """Test undo_text is empty when nothing to undo."""
        text = self.manager.undo_text()

        self.assertEqual(text, "")

    def test_undo_text_returns_action_description(self):
        """Test undo_text returns action description."""
        do_func = Mock()
        undo_func = Mock()

        self.manager.push("Test Action", do_func, undo_func)

        text = self.manager.undo_text()

        self.assertEqual(text, "Test Action")

    def test_redo_text_empty_when_nothing_to_redo(self):
        """Test redo_text is empty when nothing to redo."""
        text = self.manager.redo_text()

        self.assertEqual(text, "")

    def test_redo_text_after_undo(self):
        """Test redo_text after undo."""
        do_func = Mock()
        undo_func = Mock()

        self.manager.push("Test Action", do_func, undo_func)
        self.manager.undo()

        text = self.manager.redo_text()

        self.assertEqual(text, "Test Action")


class TestUndoRedoManagerSignals(unittest.TestCase):
    """Test UndoRedoManager signal emissions."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = UndoRedoManager()

    def test_can_undo_changed_signal_emitted(self):
        """Test can_undo_changed signal is emitted."""
        signal_received = []
        self.manager.can_undo_changed.connect(
            lambda can_undo, text: signal_received.append((can_undo, text))
        )

        do_func = Mock()
        undo_func = Mock()
        self.manager.push("Test", do_func, undo_func)

        # Signal should have been emitted
        self.assertGreater(len(signal_received), 0)
        self.assertTrue(signal_received[-1][0])  # can_undo = True
        self.assertEqual(signal_received[-1][1], "Test")

    def test_can_redo_changed_signal_emitted(self):
        """Test can_redo_changed signal is emitted."""
        signal_received = []
        self.manager.can_redo_changed.connect(
            lambda can_redo, text: signal_received.append((can_redo, text))
        )

        do_func = Mock()
        undo_func = Mock()
        self.manager.push("Test", do_func, undo_func)
        self.manager.undo()

        # Signal should have been emitted
        self.assertGreater(len(signal_received), 0)
        self.assertTrue(signal_received[-1][0])  # can_redo = True

    def test_clean_changed_signal_emitted(self):
        """Test clean_changed signal is emitted."""
        signal_received = []
        self.manager.clean_changed.connect(
            lambda is_clean: signal_received.append(is_clean)
        )

        do_func = Mock()
        undo_func = Mock()
        self.manager.push("Test", do_func, undo_func)

        # Signal should have been emitted (state changed to not clean)
        self.assertGreater(len(signal_received), 0)
        self.assertFalse(signal_received[-1])


class TestUndoRedoMixin(unittest.TestCase):
    """Test UndoRedoMixin functionality."""

    def test_init_undo_redo_creates_manager(self):
        """Test _init_undo_redo creates UndoRedoManager."""
        class TestWidget(QWidget, UndoRedoMixin):
            def __init__(self):
                super().__init__()
                self._init_undo_redo()

        widget = TestWidget()

        self.assertIsInstance(widget.undo_manager, UndoRedoManager)
        widget.close()

    def test_undo_redo_mixin_signals_connected(self):
        """Test mixin connects to undo/redo signals."""
        class TestWidget(QWidget, UndoRedoMixin):
            def __init__(self):
                super().__init__()
                self.undo_state_changed_called = False
                self.redo_state_changed_called = False
                self._init_undo_redo()

            def _on_undo_state_changed(self, can_undo, text):
                self.undo_state_changed_called = True

            def _on_redo_state_changed(self, can_redo, text):
                self.redo_state_changed_called = True

        widget = TestWidget()

        # Trigger signals by pushing a command
        do_func = Mock()
        undo_func = Mock()
        widget.undo_manager.push("Test", do_func, undo_func)

        # Signals should have triggered callbacks
        self.assertTrue(widget.undo_state_changed_called)

        widget.close()

    def test_undo_redo_mixin_integration(self):
        """Test full integration of UndoRedoMixin."""
        class TestWidget(QWidget, UndoRedoMixin):
            def __init__(self):
                super().__init__()
                self.value = 0
                self._init_undo_redo()

            def set_value(self, new_value):
                old_value = self.value

                self.undo_manager.push(
                    "Change Value",
                    lambda d: setattr(self, 'value', d['new']),
                    lambda d: setattr(self, 'value', d['old']),
                    {'old': old_value, 'new': new_value}
                )

        widget = TestWidget()
        widget.set_value(42)

        # Value should be changed
        self.assertEqual(widget.value, 42)

        # Undo
        widget.undo_manager.undo()
        self.assertEqual(widget.value, 0)

        # Redo
        widget.undo_manager.redo()
        self.assertEqual(widget.value, 42)

        widget.close()


class TestUndoRedoIntegration(unittest.TestCase):
    """Integration tests for undo/redo system."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = UndoRedoManager()

    def test_complete_undo_redo_workflow(self):
        """Test complete undo/redo workflow."""
        state = {"value": 0}

        def increment(data):
            state["value"] += data["amount"]

        def decrement(data):
            state["value"] -= data["amount"]

        # Push several commands
        self.manager.push("Increment by 5", increment, decrement, {"amount": 5})
        self.assertEqual(state["value"], 5)

        self.manager.push("Increment by 3", increment, decrement, {"amount": 3})
        self.assertEqual(state["value"], 8)

        self.manager.push("Increment by 2", increment, decrement, {"amount": 2})
        self.assertEqual(state["value"], 10)

        # Undo twice
        self.manager.undo()
        self.assertEqual(state["value"], 8)

        self.manager.undo()
        self.assertEqual(state["value"], 5)

        # Redo once
        self.manager.redo()
        self.assertEqual(state["value"], 8)

        # Push new command (should clear redo stack)
        self.manager.push("Increment by 1", increment, decrement, {"amount": 1})
        self.assertEqual(state["value"], 9)
        self.assertFalse(self.manager.can_redo())


if __name__ == "__main__":
    unittest.main()
