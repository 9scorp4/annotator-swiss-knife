"""
Main menu widget for the annotation toolkit GUI.

This module implements the main menu widget that displays buttons for each tool.
"""

from typing import Dict, List, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ....core.base import AnnotationTool


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
        # Main layout
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Annotation Toolkit")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel("Select a tool to use:")
        desc_label.setFont(QFont("Arial", 14))
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)

        # Add some space
        layout.addSpacing(20)

        # Tool buttons container
        tools_layout = QVBoxLayout()

        # Define colors for the tool buttons
        colors = {
            "Dictionary to Bullet List": ("#4CAF50", "#45a049"),  # Green
            "JSON Visualizer": ("#2196F3", "#0b7dda"),  # Blue
            "Text Cleaner": ("#FF9800", "#e68a00"),  # Orange
        }

        # Add a button for each tool
        for tool_name, tool in self.tools.items():
            button = QPushButton(tool_name)
            button.setFont(QFont("Arial", 12))
            button.setMinimumHeight(60)

            # Set button color
            default_color, hover_color = colors.get(
                tool_name, ("#607D8B", "#546E7A")  # Default to gray if not found
            )

            button.setStyleSheet(
                f"QPushButton {{ background-color: {default_color}; color: white; border-radius: 5px; }}"
                f"QPushButton:hover {{ background-color: {hover_color}; }}"
            )

            # Add tool description as tooltip
            button.setToolTip(tool.description)

            # Connect button to switch_to_tool function
            button.clicked.connect(
                lambda checked, name=tool_name: self.main_app.switch_to_tool(name)
            )

            tools_layout.addWidget(button)

            # Add some space between buttons
            tools_layout.addSpacing(10)

        # Center the buttons
        tools_container = QWidget()
        tools_container.setLayout(tools_layout)
        tools_container.setMaximumWidth(400)

        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(tools_container)
        h_layout.addStretch()

        layout.addLayout(h_layout)
        layout.addStretch()

        # Footer
        footer_label = QLabel("© 2025 Nicolas Arias Garcia | Meta")
        footer_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer_label)
