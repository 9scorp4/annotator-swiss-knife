"""
Main menu widget for the annotation toolkit GUI.

This module implements the main menu widget that displays buttons for each tool.
"""

from typing import Dict, List, Optional

from PyQt5.QtCore import QEasingCurve, QPoint, QPropertyAnimation, QSize, Qt
from PyQt5.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ....core.base import AnnotationTool


class ToolButton(QPushButton):
    """
    Custom button for tools with enhanced visual effects.
    """

    def __init__(
        self,
        text,
        icon_name=None,
        color="#4CAF50",
        hover_color="#45a049",
        dark_color=None,
        dark_hover_color=None,
    ):
        """
        Initialize the tool button.

        Args:
            text (str): Button text
            icon_name (str, optional): Icon name
            color (str): Default button color for light theme
            hover_color (str): Button color on hover for light theme
            dark_color (str, optional): Button color for dark theme
            dark_hover_color (str, optional): Button color on hover for dark theme
        """
        super().__init__(text)
        self.default_color = color
        self.hover_color = hover_color
        self.dark_color = dark_color or color
        self.dark_hover_color = dark_hover_color or hover_color
        self.setFont(QFont("Poppins", 12))
        self.setMinimumHeight(70)
        self.setCursor(Qt.PointingHandCursor)

        # We'll use the palette to determine if we're in dark mode
        is_dark_mode = self.palette().window().color().lightness() < 128

        # Choose colors based on theme
        button_color = self.dark_color if is_dark_mode else self.default_color
        button_hover_color = self.dark_hover_color if is_dark_mode else self.hover_color

        # Set button style
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {button_color};
                color: white;
                border-radius: 8px;
                padding: 10px 15px;
                text-align: left;
                padding-left: 20px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {button_hover_color};
            }}
            QPushButton:pressed {{
                background-color: {button_hover_color};
                padding-top: 12px;
            }}
            """
        )

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(shadow)

        # Set size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


class MainMenuWidget(QWidget):
    """
    Main menu widget with buttons for each tool.
    """

    def __init__(self, tools: Dict[str, AnnotationTool], main_app):
        """
        Initialize the main menu widget.

        Args:
            tools (Dict[str, AnnotationTool]): Dictionary of available tools.
            main_app: The main application.
        """
        super().__init__()
        self.tools = tools
        self.main_app = main_app

        self._init_ui()

    def _init_ui(self) -> None:
        """
        Initialize the user interface.
        """
        # Main layout with better spacing
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 40, 30, 30)
        layout.setSpacing(20)

        # Header container with background
        header_container = QFrame()
        header_container.setObjectName("headerContainer")
        header_container.setStyleSheet(
            """
            #headerContainer {
                background-color: rgba(0, 0, 0, 0.03);
                border-radius: 15px;
                padding: 10px;
            }
            """
        )
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(20, 20, 20, 20)
        header_layout.setSpacing(10)

        # Title with modern font - theme-aware
        title_label = QLabel("Annotation Toolkit")
        title_label.setFont(QFont("Poppins", 28, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("mainTitle")  # Let app-wide theme handle color
        header_layout.addWidget(title_label)

        # Description with subtle styling - theme-aware
        desc_label = QLabel("Select a tool to use:")
        desc_label.setFont(QFont("Poppins", 14))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setObjectName("mainDescription")  # Let app-wide theme handle color
        header_layout.addWidget(desc_label)

        layout.addWidget(header_container)

        # Tool buttons container with card-like appearance that works in both themes
        tools_container = QFrame()
        tools_container.setObjectName("toolsContainer")
        # We'll let the app-wide theme handle the styling for better dark mode compatibility

        # Add shadow to tools container
        tools_shadow = QGraphicsDropShadowEffect()
        tools_shadow.setBlurRadius(20)
        tools_shadow.setXOffset(0)
        tools_shadow.setYOffset(5)
        tools_shadow.setColor(QColor(0, 0, 0, 30))
        tools_container.setGraphicsEffect(tools_shadow)

        tools_layout = QVBoxLayout(tools_container)
        tools_layout.setContentsMargins(20, 20, 20, 20)
        tools_layout.setSpacing(15)

        # Define colors for the tool buttons - more vibrant and modern
        colors = {
            "Dictionary to Bullet List": ("#4CAF50", "#3d9c40"),  # Green
            "JSON Visualizer": ("#2196F3", "#1a7fd1"),  # Blue
            "Text Cleaner": ("#FF9800", "#e68a00"),  # Orange
        }

        # Add a button for each tool
        for tool_name, tool in self.tools.items():
            default_color, hover_color = colors.get(
                tool_name, ("#607D8B", "#546E7A")  # Default to gray if not found
            )

            # Create custom tool button with theme-aware styling but keep original colors
            button = ToolButton(
                text=tool_name,
                color=default_color,
                hover_color=hover_color,
                dark_color=default_color,  # Keep original color in dark theme
                dark_hover_color=hover_color,  # Keep original hover color in dark theme
            )

            # Add tool description as tooltip with better formatting
            button.setToolTip(f"<b>{tool_name}</b><br>{tool.description}")

            # Connect button to switch_to_tool function
            button.clicked.connect(
                lambda checked, name=tool_name: self.main_app.switch_to_tool(name)
            )

            tools_layout.addWidget(button)

        # Center the tools container
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(tools_container)
        h_layout.addStretch()

        layout.addLayout(h_layout)
        layout.addStretch()

        # Footer with modern styling
        footer_container = QFrame()
        footer_container.setObjectName("footerContainer")
        footer_container.setStyleSheet(
            """
            #footerContainer {
                background-color: rgba(0, 0, 0, 0.03);
                border-radius: 10px;
                padding: 5px;
            }
            """
        )
        footer_layout = QVBoxLayout(footer_container)
        footer_layout.setContentsMargins(10, 10, 10, 10)

        footer_label = QLabel("© 2025 Nicolas Arias Garcia | Meta")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setObjectName("footerLabel")  # Let app-wide theme handle color
        footer_label.setFont(QFont("Arial", 12))
        footer_layout.addWidget(footer_label)

        layout.addWidget(footer_container)
