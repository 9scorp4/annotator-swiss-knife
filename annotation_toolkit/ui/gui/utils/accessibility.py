"""
Accessibility utilities for the annotation toolkit GUI.

Provides focus indicators, ARIA-like labels, and keyboard navigation enhancements.
"""

from typing import Optional
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPalette

from ..themes import ThemeManager


class AccessibilityManager:
    """
    Manages accessibility features across the application.

    Features:
    - Focus indicators
    - Accessible names and descriptions
    - Keyboard navigation
    - Screen reader support
    - High contrast mode detection
    """

    @staticmethod
    def set_accessible_name(widget: QWidget, name: str) -> None:
        """
        Set accessible name for screen readers.

        Args:
            widget: Widget to label
            name: Accessible name
        """
        widget.setAccessibleName(name)

    @staticmethod
    def set_accessible_description(widget: QWidget, description: str) -> None:
        """
        Set accessible description for screen readers.

        Args:
            widget: Widget to describe
            description: Accessible description
        """
        widget.setAccessibleDescription(description)

    @staticmethod
    def enable_keyboard_focus(widget: QWidget) -> None:
        """
        Enable keyboard focus for a widget.

        Args:
            widget: Widget to enable focus for
        """
        widget.setFocusPolicy(Qt.StrongFocus)

    @staticmethod
    def apply_focus_indicator(widget: QWidget) -> None:
        """
        Apply visible focus indicator styling to a widget.

        Args:
            widget: Widget to add focus indicator to
        """
        theme = ThemeManager.instance().current_theme

        # Get current stylesheet or empty string
        current_style = widget.styleSheet() or ""

        # Add focus indicator styles
        focus_style = f"""
            {widget.__class__.__name__}:focus {{
                border: 2px solid {theme.accent_primary};
                outline: 2px solid {theme.accent_glow};
                outline-offset: 2px;
            }}
        """

        # Combine with existing styles
        widget.setStyleSheet(current_style + "\n" + focus_style)

    @staticmethod
    def set_widget_role(widget: QWidget, role: str) -> None:
        """
        Set widget role for accessibility (button, checkbox, etc.).

        Args:
            widget: Widget to set role for
            role: Role name
        """
        # Qt uses setAccessibleName with role prefix for this
        current_name = widget.accessibleName()
        if current_name:
            widget.setAccessibleName(f"{role}: {current_name}")
        else:
            widget.setAccessibleName(role)

    @staticmethod
    def is_high_contrast_mode() -> bool:
        """
        Check if system is in high contrast mode.

        Returns:
            True if high contrast mode is enabled
        """
        # Check system color scheme for high contrast indicators
        palette = QApplication.palette()

        # High contrast typically has very distinct foreground/background
        bg = palette.color(QPalette.Window)
        fg = palette.color(QPalette.WindowText)

        # Calculate contrast ratio
        bg_luminance = (0.299 * bg.red() + 0.587 * bg.green() + 0.114 * bg.blue()) / 255
        fg_luminance = (0.299 * fg.red() + 0.587 * fg.green() + 0.114 * fg.blue()) / 255

        # High contrast typically has ratio > 7:1
        if bg_luminance > fg_luminance:
            ratio = (bg_luminance + 0.05) / (fg_luminance + 0.05)
        else:
            ratio = (fg_luminance + 0.05) / (bg_luminance + 0.05)

        return ratio > 7.0


class AccessibleWidget:
    """
    Mixin to add accessibility features to widgets.

    Usage:
        class MyWidget(QWidget, AccessibleWidget):
            def __init__(self):
                super().__init__()
                self._init_accessibility("My Widget", "Description of my widget")
    """

    def _init_accessibility(
        self,
        accessible_name: str,
        accessible_description: Optional[str] = None,
        enable_focus: bool = True,
        add_focus_indicator: bool = True
    ) -> None:
        """
        Initialize accessibility features for this widget.

        Args:
            accessible_name: Name for screen readers
            accessible_description: Optional description
            enable_focus: Whether to enable keyboard focus
            add_focus_indicator: Whether to add visible focus indicator
        """
        # Set accessible properties
        AccessibilityManager.set_accessible_name(self, accessible_name)

        if accessible_description:
            AccessibilityManager.set_accessible_description(self, accessible_description)

        # Enable keyboard navigation
        if enable_focus:
            AccessibilityManager.enable_keyboard_focus(self)

        # Add visual focus indicator
        if add_focus_indicator:
            AccessibilityManager.apply_focus_indicator(self)


def make_accessible(
    widget: QWidget,
    name: str,
    description: Optional[str] = None,
    role: Optional[str] = None,
    enable_focus: bool = True,
    add_focus_indicator: bool = True
) -> None:
    """
    Make a widget accessible in one function call.

    Args:
        widget: Widget to make accessible
        name: Accessible name
        description: Optional description
        role: Optional ARIA-like role (button, checkbox, etc.)
        enable_focus: Whether to enable keyboard focus
        add_focus_indicator: Whether to add focus indicator
    """
    AccessibilityManager.set_accessible_name(widget, name)

    if description:
        AccessibilityManager.set_accessible_description(widget, description)

    if role:
        AccessibilityManager.set_widget_role(widget, role)

    if enable_focus:
        AccessibilityManager.enable_keyboard_focus(widget)

    if add_focus_indicator:
        AccessibilityManager.apply_focus_indicator(widget)


# Common accessibility shortcuts
def set_button_accessible(widget: QWidget, text: str, description: Optional[str] = None) -> None:
    """
    Make a button accessible.

    Args:
        widget: Button widget
        text: Button text
        description: Optional description of what button does
    """
    make_accessible(widget, text, description, role="button")


def set_input_accessible(widget: QWidget, label: str, description: Optional[str] = None) -> None:
    """
    Make an input field accessible.

    Args:
        widget: Input widget
        label: Input field label
        description: Optional description or placeholder
    """
    make_accessible(widget, label, description, role="textbox")


def set_checkbox_accessible(widget: QWidget, label: str, description: Optional[str] = None) -> None:
    """
    Make a checkbox accessible.

    Args:
        widget: Checkbox widget
        label: Checkbox label
        description: Optional description
    """
    make_accessible(widget, label, description, role="checkbox")


def set_list_accessible(widget: QWidget, label: str, description: Optional[str] = None) -> None:
    """
    Make a list widget accessible.

    Args:
        widget: List widget
        label: List label
        description: Optional description
    """
    make_accessible(widget, label, description, role="list")


def set_tab_accessible(widget: QWidget, tab_name: str, description: Optional[str] = None) -> None:
    """
    Make a tab accessible.

    Args:
        widget: Tab widget
        tab_name: Tab name
        description: Optional description
    """
    make_accessible(widget, tab_name, description, role="tab")
