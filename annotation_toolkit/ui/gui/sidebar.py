"""
Collapsible sidebar navigation for the annotation toolkit GUI.

This module implements a modern collapsible sidebar for tool navigation.
"""

from PyQt5.QtCore import Qt, QPropertyAnimation, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QWidget,
)

from .theme import ColorPalette, BorderRadius, Spacing


class SidebarButton(QPushButton):
    """Custom button for sidebar navigation."""

    def __init__(self, tool_name: str, icon_text: str = "●", parent=None):
        super().__init__(parent)
        self.tool_name = tool_name
        self.icon_text = icon_text
        self.is_active = False

        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(50)

        # Create layout for icon and label
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # Icon label
        self.icon_label = QLabel(icon_text)
        self.icon_label.setFont(QFont("Arial", 16))
        self.icon_label.setFixedSize(24, 24)
        self.icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.icon_label)

        # Text label
        self.text_label = QLabel(tool_name)
        self.text_label.setFont(QFont("Arial", 13))
        layout.addWidget(self.text_label)
        layout.addStretch()

        self._update_style()

    def set_active(self, active: bool):
        """Set the active state of the button."""
        self.is_active = active
        self.setChecked(active)
        self._update_style()

    def hide_text(self):
        """Hide the text label for collapsed state."""
        self.text_label.hide()

    def show_text(self):
        """Show the text label for expanded state."""
        self.text_label.show()

    def enterEvent(self, event):
        """Animate button on mouse enter."""
        if not self.is_active:
            # Subtle scale effect on hover
            from PyQt5.QtCore import QPropertyAnimation, QRect, QEasingCurve
            current_geo = self.geometry()
            # Small scale increase (2px on each side)
            target_geo = QRect(
                current_geo.x() - 2,
                current_geo.y() - 1,
                current_geo.width() + 4,
                current_geo.height() + 2
            )
            self.hover_animation = QPropertyAnimation(self, b"geometry")
            self.hover_animation.setDuration(150)
            self.hover_animation.setStartValue(current_geo)
            self.hover_animation.setEndValue(target_geo)
            self.hover_animation.setEasingCurve(QEasingCurve.OutCubic)
            self.hover_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Animate button on mouse leave."""
        if not self.is_active and hasattr(self, 'hover_animation'):
            # Return to original size
            from PyQt5.QtCore import QPropertyAnimation, QRect, QEasingCurve
            current_geo = self.geometry()
            target_geo = QRect(
                current_geo.x() + 2,
                current_geo.y() + 1,
                current_geo.width() - 4,
                current_geo.height() - 2
            )
            self.leave_animation = QPropertyAnimation(self, b"geometry")
            self.leave_animation.setDuration(150)
            self.leave_animation.setStartValue(current_geo)
            self.leave_animation.setEndValue(target_geo)
            self.leave_animation.setEasingCurve(QEasingCurve.InCubic)
            self.leave_animation.start()
        super().leaveEvent(event)

    def _update_style(self):
        """Update button styling based on state."""
        if self.is_active:
            bg_color = ColorPalette.PRIMARY
            text_color = "#FFFFFF"  # Pure white for maximum contrast
            icon_color = "#FFFFFF"  # Pure white for maximum contrast
        else:
            bg_color = "transparent"
            text_color = ColorPalette.GRAY_900  # Darker for better contrast
            icon_color = ColorPalette.GRAY_700

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border: none;
                border-radius: {BorderRadius.LG};
                text-align: left;
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: {ColorPalette.GRAY_100 if not self.is_active else ColorPalette.PRIMARY_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {ColorPalette.GRAY_200 if not self.is_active else ColorPalette.PRIMARY_PRESSED};
            }}
        """)

        # Set label styles with transparent backgrounds
        self.text_label.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-weight: {'bold' if self.is_active else 'normal'};
                background-color: transparent;
                border: none;
            }}
        """)
        self.icon_label.setStyleSheet(f"""
            QLabel {{
                color: {icon_color};
                background-color: transparent;
                border: none;
            }}
        """)


class CollapsibleSidebar(QFrame):
    """Collapsible sidebar for navigation between tools."""

    # Signal emitted when a tool is selected
    tool_selected = pyqtSignal(str)

    def __init__(self, tools: dict, parent=None):
        super().__init__(parent)
        self.tools = tools
        self.is_collapsed = False
        self.buttons = {}
        self.active_button = None

        self._init_ui()

    def _init_ui(self):
        """Initialize the sidebar UI."""
        self.setObjectName("sidebar")
        self.setFixedWidth(220)  # Expanded width
        self.setStyleSheet(f"""
            #sidebar {{
                background-color: {ColorPalette.LIGHT_BG_PRIMARY};
                border-right: 2px solid {ColorPalette.GRAY_200};
            }}
        """)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(8)

        # Toggle button at top
        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.setFont(QFont("Arial", 18))
        self.toggle_btn.setFixedHeight(44)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ColorPalette.GRAY_100};
                border: none;
                border-radius: {BorderRadius.LG};
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: {ColorPalette.GRAY_200};
            }}
        """)
        self.toggle_btn.clicked.connect(self.toggle_collapse)
        layout.addWidget(self.toggle_btn)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background-color: {ColorPalette.GRAY_200}; max-height: 1px;")
        layout.addWidget(separator)

        # Tool icons mapping
        tool_icons = {
            "Dictionary to Bullet List": "📝",
            "Text Cleaner": "✨",
            "JSON Visualizer": "👁",
            "Conversation Generator": "💬",
            "Text Collector": "📋"
        }

        # Create buttons for each tool
        for tool_name in self.tools.keys():
            icon = tool_icons.get(tool_name, "●")
            btn = SidebarButton(tool_name, icon)
            btn.clicked.connect(lambda checked, name=tool_name: self._on_tool_selected(name))
            self.buttons[tool_name] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # Home button at bottom
        self.home_btn = SidebarButton("Home", "🏠")
        self.home_btn.clicked.connect(lambda: self._on_tool_selected("Home"))
        layout.addWidget(self.home_btn)

    def _on_tool_selected(self, tool_name: str):
        """Handle tool selection from button clicks."""
        # Update active state (this will emit signal)
        self._update_active_button(tool_name)

        # Emit signal
        self.tool_selected.emit(tool_name)

    def _update_active_button(self, tool_name: str):
        """Update the active button state without emitting signals."""
        # Update active state
        if self.active_button:
            self.active_button.set_active(False)

        if tool_name == "Home":
            self.home_btn.set_active(True)
            self.active_button = self.home_btn
        else:
            self.buttons[tool_name].set_active(True)
            self.active_button = self.buttons[tool_name]

    def toggle_collapse(self):
        """Toggle between collapsed and expanded states."""
        if self.is_collapsed:
            self.expand()
        else:
            self.collapse()

    def collapse(self):
        """Collapse the sidebar to icon-only mode with smooth animation."""
        from PyQt5.QtCore import QEasingCurve, QTimer

        self.is_collapsed = True

        # Animate width from 220 to 70
        self.width_animation = QPropertyAnimation(self, b"maximumWidth")
        self.width_animation.setDuration(250)
        self.width_animation.setStartValue(220)
        self.width_animation.setEndValue(70)
        self.width_animation.setEasingCurve(QEasingCurve.InOutCubic)

        # Also animate minimum width to ensure proper resizing
        self.min_width_animation = QPropertyAnimation(self, b"minimumWidth")
        self.min_width_animation.setDuration(250)
        self.min_width_animation.setStartValue(220)
        self.min_width_animation.setEndValue(70)
        self.min_width_animation.setEasingCurve(QEasingCurve.InOutCubic)

        # Hide text labels halfway through animation
        def hide_text_halfway():
            for btn in self.buttons.values():
                btn.hide_text()
            self.home_btn.hide_text()

        QTimer.singleShot(125, hide_text_halfway)

        # Update toggle button
        self.toggle_btn.setText("▶")

        # Start animations
        self.width_animation.start()
        self.min_width_animation.start()

    def expand(self):
        """Expand the sidebar to show icons and text with smooth animation."""
        from PyQt5.QtCore import QEasingCurve

        self.is_collapsed = False

        # Show text labels immediately
        for btn in self.buttons.values():
            btn.show_text()
        self.home_btn.show_text()

        # Animate width from 70 to 220
        self.width_animation = QPropertyAnimation(self, b"maximumWidth")
        self.width_animation.setDuration(250)
        self.width_animation.setStartValue(70)
        self.width_animation.setEndValue(220)
        self.width_animation.setEasingCurve(QEasingCurve.InOutCubic)

        # Also animate minimum width
        self.min_width_animation = QPropertyAnimation(self, b"minimumWidth")
        self.min_width_animation.setDuration(250)
        self.min_width_animation.setStartValue(70)
        self.min_width_animation.setEndValue(220)
        self.min_width_animation.setEasingCurve(QEasingCurve.InOutCubic)

        # Update toggle button
        self.toggle_btn.setText("☰")

        # Start animations
        self.width_animation.start()
        self.min_width_animation.start()

    def set_active_tool(self, tool_name: str):
        """Set the active tool programmatically without emitting signals."""
        self._update_active_button(tool_name)
