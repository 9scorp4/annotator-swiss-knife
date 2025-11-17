"""
GlassButton component - Enhanced glassmorphic button.

Provides a modern button with glassmorphic styling and animations.
"""

from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QColor


class GlassButton(QPushButton):
    """
    Glassmorphic button with hover animations.
    """

    def __init__(self, text="", variant="primary", size="medium", parent=None):
        super().__init__(text, parent)
        self.variant = variant
        self.size_variant = size

        self.setCursor(Qt.PointingHandCursor)
        self._apply_style()

    def _apply_style(self):
        """Apply glassmorphic styling."""
        # Size variants
        sizes = {
            "small": {"height": 32, "padding": "6px 12px", "font": "12px"},
            "medium": {"height": 40, "padding": "8px 16px", "font": "13px"},
            "large": {"height": 48, "padding": "12px 24px", "font": "14px"},
        }

        size_style = sizes.get(self.size_variant, sizes["medium"])
        self.setFixedHeight(size_style["height"])

        # Color variants
        colors = {
            "primary": {"bg": "#4299e1", "hover": "#3182ce", "press": "#2c5282"},
            "success": {"bg": "#38a169", "hover": "#2f855a", "press": "#276749"},
            "danger": {"bg": "#e53e3e", "hover": "#c53030", "press": "#9b2c2c"},
            "warning": {"bg": "#dd6b20", "hover": "#c05621", "press": "#9c4221"},
            "ghost": {"bg": "transparent", "hover": "rgba(0,0,0,0.05)", "press": "rgba(0,0,0,0.1)"},
        }

        color = colors.get(self.variant, colors["primary"])

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color['bg']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: {size_style['padding']};
                font-size: {size_style['font']};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color['hover']};
            }}
            QPushButton:pressed {{
                background-color: {color['press']};
            }}
            QPushButton:disabled {{
                background-color: #cbd5e0;
                color: #a0aec0;
            }}
        """)
