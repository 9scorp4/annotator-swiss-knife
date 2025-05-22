"""
Main GUI application for the annotation toolkit.

This module implements the main GUI application that integrates all the annotation tools.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from ...config import Config
from ...core.base import AnnotationTool
from ...core.conversation.visualizer import JsonVisualizer
from ...core.text.dict_to_bullet import DictToBulletList
from ...core.text.text_cleaner import TextCleaner
from ...utils import logger
from .widgets.dict_widget import DictToBulletWidget
from .widgets.json_widget import JsonVisualizerWidget
from .widgets.main_menu import MainMenuWidget
from .widgets.text_cleaner_widget import TextCleanerWidget


class AnnotationToolkitApp(QMainWindow):
    """
    Main GUI application for the annotation toolkit.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the main application.

        Args:
            config (Optional[Config]): The configuration.
                If None, a default configuration is created.
        """
        super().__init__()
        logger.info("Initializing Annotation Toolkit GUI application")

        # Initialize configuration
        self.config = config or Config()
        logger.debug("Configuration initialized")

        # Set up tools
        self.tools = {}
        self._initialize_tools()

        # Set up UI
        self._init_ui()
        logger.info("GUI application initialized successfully")

    def _initialize_tools(self) -> None:
        """
        Initialize the annotation tools.
        """
        logger.info("Initializing annotation tools")

        # Initialize dictionary to bullet list tool
        dict_tool_enabled = self.config.get(
            "tools", "dict_to_bullet", "enabled", default=True
        )
        logger.debug(f"Dictionary to Bullet List tool enabled: {dict_tool_enabled}")

        if dict_tool_enabled:
            dict_tool = DictToBulletList()
            self.tools[dict_tool.name] = dict_tool
            logger.info(f"Initialized tool: {dict_tool.name}")

        # Initialize JSON visualizer tool
        json_tool_enabled = self.config.get(
            "tools", "json_visualizer", "enabled", default=True
        )
        logger.debug(f"JSON Visualizer tool enabled: {json_tool_enabled}")

        if json_tool_enabled:
            # Get color settings from config
            user_message_color = self.config.get(
                "tools",
                "conversation_visualizer",
                "user_message_color",
                default="#0d47a1",
            )
            ai_message_color = self.config.get(
                "tools",
                "conversation_visualizer",
                "ai_message_color",
                default="#33691e",
            )
            logger.debug(
                f"Using colors - user: {user_message_color}, AI: {ai_message_color}"
            )

            json_tool = JsonVisualizer(
                user_message_color=user_message_color, ai_message_color=ai_message_color
            )
            self.tools[json_tool.name] = json_tool
            logger.info(f"Initialized tool: {json_tool.name}")

        # Initialize Text Cleaner tool
        text_cleaner_enabled = self.config.get(
            "tools", "text_cleaner", "enabled", default=True
        )
        logger.debug(f"Text Cleaner tool enabled: {text_cleaner_enabled}")

        if text_cleaner_enabled:
            text_cleaner_tool = TextCleaner()
            self.tools[text_cleaner_tool.name] = text_cleaner_tool
            logger.info(f"Initialized tool: {text_cleaner_tool.name}")

        logger.info(f"Initialized {len(self.tools)} tools")

    def _init_ui(self) -> None:
        """
        Initialize the user interface.
        """
        logger.info("Initializing user interface")

        # Set window properties
        self.setWindowTitle("Annotation Toolkit")

        # Get window size from config
        width = self.config.get("ui", "window_size", "width", default=1000)
        height = self.config.get("ui", "window_size", "height", default=700)
        logger.debug(f"Setting window size: {width}x{height}")
        self.setGeometry(100, 100, width, height)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Create header with navigation
        header_frame = QFrame()
        header_frame.setFrameShape(QFrame.StyledPanel)
        header_frame.setStyleSheet("background-color: #f0f0f0;")
        header_layout = QHBoxLayout(header_frame)

        # Home button
        self.home_button = QPushButton("Home")
        self.home_button.clicked.connect(self._go_to_home)
        header_layout.addWidget(self.home_button)

        # Title
        title_font_size = self.config.get("ui", "font_size", default=12) + 2
        header_title = QLabel("Annotation Toolkit")
        header_title.setFont(QFont("Arial", title_font_size, QFont.Bold))
        header_title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(header_title)

        # Empty widget for symmetry
        spacer = QWidget()
        spacer.setMinimumWidth(self.home_button.sizeHint().width())
        header_layout.addWidget(spacer)

        main_layout.addWidget(header_frame)

        # Create stacked widget to hold different tools
        self.stacked_widget = QStackedWidget()

        # Add main menu
        self.main_menu = MainMenuWidget(self.tools, self)
        self.stacked_widget.addWidget(self.main_menu)

        # Add Dictionary to Bullet List tool widget
        if "Dictionary to Bullet List" in self.tools:
            self.dict_widget = DictToBulletWidget(
                self.tools["Dictionary to Bullet List"]
            )
            self.stacked_widget.addWidget(self.dict_widget)

        # Add JSON Visualizer tool widget
        if "JSON Visualizer" in self.tools:
            self.json_widget = JsonVisualizerWidget(self.tools["JSON Visualizer"])
            self.stacked_widget.addWidget(self.json_widget)

        # Add Text Cleaner tool widget
        if "Text Cleaner" in self.tools:
            self.text_cleaner_widget = TextCleanerWidget(self.tools["Text Cleaner"])
            self.stacked_widget.addWidget(self.text_cleaner_widget)

        main_layout.addWidget(self.stacked_widget)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Start with the main menu
        self.stacked_widget.setCurrentIndex(0)

    def _go_to_home(self) -> None:
        """
        Switch to the main menu.
        """
        logger.info("Navigating to home/main menu")
        self.stacked_widget.setCurrentIndex(0)
        self.status_bar.showMessage("Main Menu")

    def switch_to_tool(self, tool_name: str) -> None:
        """
        Switch to the specified tool.

        Args:
            tool_name (str): The name of the tool to switch to.

        Raises:
            ValueError: If the tool is not found.
        """
        logger.info(f"Switching to tool: {tool_name}")

        if tool_name == "Dictionary to Bullet List":
            self.stacked_widget.setCurrentWidget(self.dict_widget)
            self.status_bar.showMessage(f"Using {tool_name}")
            logger.debug(f"Switched to Dictionary to Bullet List tool")
        elif tool_name == "JSON Visualizer":
            self.stacked_widget.setCurrentWidget(self.json_widget)
            self.status_bar.showMessage(f"Using {tool_name}")
            logger.debug(f"Switched to JSON Visualizer tool")
        elif tool_name == "Text Cleaner":
            self.stacked_widget.setCurrentWidget(self.text_cleaner_widget)
            self.status_bar.showMessage(f"Using {tool_name}")
            logger.debug(f"Switched to Text Cleaner tool")
        else:
            logger.error(f"Unknown tool: {tool_name}")
            raise ValueError(f"Unknown tool: {tool_name}")

    def closeEvent(self, event) -> None:
        """
        Handle the window close event.

        Save the window size to the configuration.

        Args:
            event: The close event.
        """
        logger.info("Application closing")

        # Save window size to config
        width = self.width()
        height = self.height()
        logger.debug(f"Saving window size to config: {width}x{height}")
        self.config.set(width, "ui", "window_size", "width")
        self.config.set(height, "ui", "window_size", "height")

        # Continue with the close event
        logger.info("Application shutdown complete")
        super().closeEvent(event)


def run_application() -> None:
    """
    Run the application.
    """
    logger.info("Starting Annotation Toolkit GUI application")
    try:
        app = QApplication(sys.argv)
        window = AnnotationToolkitApp()
        window.show()
        logger.info("Application window displayed, entering main event loop")
        sys.exit(app.exec_())
    except Exception as e:
        logger.exception(f"Unhandled exception in GUI application: {str(e)}")
        raise


if __name__ == "__main__":
    run_application()
