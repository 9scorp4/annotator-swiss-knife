"""
GlassButton component - Enhanced glassmorphic button.

Provides a modern button with glassmorphic styling and animations.
"""

from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QColor

from ..themes import ThemeManager


class GlassButton(QPushButton):
    """
    Glassmorphic button with hover animations and theme support.
    """

    def __init__(self, text="", variant="primary", size="medium", parent=None):
        super().__init__(text, parent)
        self.variant = variant
        self.size_variant = size

        self.setCursor(Qt.PointingHandCursor)
        self._apply_style()

        # Connect to theme changes
        theme_manager = ThemeManager.instance()
        theme_manager.theme_changed.connect(self._apply_style)

    def _apply_style(self):
        """Apply glassmorphic styling with theme support."""
        # Get current theme
        theme = ThemeManager.instance().current_theme

        # Size variants
        sizes = {
            "small": {"height": 32, "padding": "6px 12px", "font": "12px"},
            "medium": {"height": 40, "padding": "8px 16px", "font": "13px"},
            "large": {"height": 48, "padding": "12px 24px", "font": "14px"},
        }

        size_style = sizes.get(self.size_variant, sizes["medium"])
        self.setFixedHeight(size_style["height"])

        # Color variants using theme
        if self.variant == "primary":
            bg_color = theme.accent_primary
            hover_color = theme.accent_primary_hover
            text_color = "#ffffff"  # Always white for primary buttons
            border = "none"
        elif self.variant == "success":
            bg_color = theme.success_color
            hover_color = theme.success_color
            text_color = "#ffffff"  # Always white for success buttons
            border = "none"
        elif self.variant == "danger":
            bg_color = theme.error_color
            hover_color = theme.error_color
            text_color = "#ffffff"  # Always white for danger buttons
            border = "none"
        elif self.variant == "warning":
            bg_color = theme.warning_color
            hover_color = theme.warning_color
            text_color = "#ffffff"  # Always white for warning buttons
            border = "none"
        elif self.variant == "ghost":
            bg_color = "transparent"
            hover_color = theme.background_glass_hover
            text_color = theme.text_primary
            border = f"2px solid {theme.border_glass}"
        else:  # Default to primary
            bg_color = theme.accent_primary
            hover_color = theme.accent_primary_hover
            text_color = "#ffffff"  # Always white for default buttons
            border = "none"

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: {border};
                border-radius: 6px;
                padding: {size_style['padding']};
                font-size: {size_style['font']};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                {f'border-color: {theme.accent_primary};' if self.variant == 'ghost' else ''}
            }}
            QPushButton:pressed {{
                background-color: {theme.background_glass_active if self.variant == 'ghost' else bg_color};
            }}
            QPushButton:disabled {{
                background-color: {theme.background_glass};
                color: {theme.text_tertiary};
                border-color: {theme.border_subtle};
            }}
        """)
