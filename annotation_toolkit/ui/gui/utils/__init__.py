"""
Utilities for the GUI application.
"""

from .animations import (
    AnimationManager,
    fade_in,
    fade_out,
    fade_transition,
    slide_in,
    slide_out,
    animate_opacity,
    animate_geometry,
)

from .undo_redo import (
    UndoableCommand,
    UndoRedoManager,
    UndoRedoMixin,
)

from .auto_save import AutoSaveManager
from .session_manager import SessionManager

from .accessibility import (
    AccessibilityManager,
    AccessibleWidget,
    make_accessible,
    set_button_accessible,
    set_input_accessible,
    set_checkbox_accessible,
    set_list_accessible,
    set_tab_accessible,
)

__all__ = [
    # Animations
    'AnimationManager',
    'fade_in',
    'fade_out',
    'fade_transition',
    'slide_in',
    'slide_out',
    'animate_opacity',
    'animate_geometry',
    # Undo/Redo
    'UndoableCommand',
    'UndoRedoManager',
    'UndoRedoMixin',
    # State Management
    'AutoSaveManager',
    'SessionManager',
    # Accessibility
    'AccessibilityManager',
    'AccessibleWidget',
    'make_accessible',
    'set_button_accessible',
    'set_input_accessible',
    'set_checkbox_accessible',
    'set_list_accessible',
    'set_tab_accessible',
]
