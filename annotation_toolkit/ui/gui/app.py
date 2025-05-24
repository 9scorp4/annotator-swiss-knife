"""
Main GUI application for the annotation toolkit.

This module implements the main GUI application that integrates all the annotation tools.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt
from PyQt5.QtGui import QColor, QFont, QFontDatabase, QIcon, QPalette
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
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

        # Load custom fonts
        self._load_fonts()

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

        # Main layout with some padding
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Create header with navigation
        header_frame = QFrame()
        header_frame.setFrameShape(QFrame.StyledPanel)
        header_frame.setObjectName("headerFrame")
        header_frame.setMinimumHeight(60)  # Taller header for better visual presence

        # Add shadow effect to header
        header_shadow = QGraphicsDropShadowEffect()
        header_shadow.setBlurRadius(15)
        header_shadow.setXOffset(0)
        header_shadow.setYOffset(2)
        header_shadow.setColor(QColor(0, 0, 0, 50))
        header_frame.setGraphicsEffect(header_shadow)

        # Header layout with better spacing
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 5, 15, 5)

        # Home button with icon
        self.home_button = QPushButton(" Home")
        self.home_button.setIcon(QIcon.fromTheme("go-home", QIcon.fromTheme("home")))
        self.home_button.setIconSize(QSize(18, 18))
        self.home_button.clicked.connect(self._go_to_home)
        self.home_button.setCursor(Qt.PointingHandCursor)  # Change cursor on hover
        self.home_button.setObjectName("homeButton")  # For specific styling
        header_layout.addWidget(self.home_button)

        # Title with custom font
        title_font_size = self.config.get("ui", "font_size", default=14) + 2
        header_title = QLabel("Annotation Toolkit")
        header_title.setFont(QFont("Poppins", title_font_size, QFont.Bold))
        header_title.setAlignment(Qt.AlignCenter)
        header_title.setObjectName("headerTitle")
        header_layout.addWidget(header_title)

        # Empty widget for symmetry
        spacer = QWidget()
        spacer.setMinimumWidth(self.home_button.sizeHint().width())
        header_layout.addWidget(spacer)

        main_layout.addWidget(header_frame)

        # Content container with rounded corners and shadow
        content_container = QFrame()
        content_container.setObjectName("contentContainer")
        content_container.setFrameShape(QFrame.StyledPanel)
        content_container.setFrameShadow(QFrame.Raised)

        # Add shadow effect to content container
        content_shadow = QGraphicsDropShadowEffect()
        content_shadow.setBlurRadius(20)
        content_shadow.setXOffset(0)
        content_shadow.setYOffset(3)
        content_shadow.setColor(QColor(0, 0, 0, 40))
        content_container.setGraphicsEffect(content_shadow)

        # Content layout
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Create stacked widget to hold different tools
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("stackedWidget")

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

        content_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(content_container, 1)  # Give it stretch factor

        # Status bar with modern styling
        self.status_bar = QStatusBar()
        self.status_bar.setObjectName("statusBar")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Start with the main menu
        self.stacked_widget.setCurrentIndex(0)

        # Set up theme support - do this after all UI elements are created
        self._setup_theme()

    def _load_fonts(self) -> None:
        """
        Load custom fonts for the application.
        """
        # Try to load Poppins font if available
        # If not available, the system will fall back to default fonts
        try:
            # Check if Poppins is already available in the system
            font_db = QFontDatabase()
            fonts = font_db.families()
            if "Poppins" not in fonts:
                logger.debug("Poppins font not found in system, using default fonts")
        except Exception as e:
            logger.warning(f"Error loading custom fonts: {str(e)}")

    def _go_to_home(self) -> None:
        """
        Switch to the main menu with a smooth transition.
        """
        logger.info("Navigating to home/main menu")

        # Create a fade transition effect
        self.stacked_widget.setCurrentIndex(0)
        self.status_bar.showMessage("Main Menu")

    def switch_to_tool(self, tool_name: str) -> None:
        """
        Switch to the specified tool with a smooth transition.

        Args:
            tool_name (str): The name of the tool to switch to.

        Raises:
            ValueError: If the tool is not found.
        """
        logger.info(f"Switching to tool: {tool_name}")

        target_widget = None

        if tool_name == "Dictionary to Bullet List":
            target_widget = self.dict_widget
            logger.debug(f"Switching to Dictionary to Bullet List tool")
        elif tool_name == "JSON Visualizer":
            target_widget = self.json_widget
            logger.debug(f"Switching to JSON Visualizer tool")
        elif tool_name == "Text Cleaner":
            target_widget = self.text_cleaner_widget
            logger.debug(f"Switching to Text Cleaner tool")
        else:
            logger.error(f"Unknown tool: {tool_name}")
            raise ValueError(f"Unknown tool: {tool_name}")

        if target_widget:
            # Set the current widget
            self.stacked_widget.setCurrentWidget(target_widget)
            self.status_bar.showMessage(f"Using {tool_name}")

    def _setup_theme(self) -> None:
        """
        Set up the application theme based on system preferences.
        """
        logger.info("Setting up application theme")

        # Check if system is using dark mode
        palette = self.palette()
        if palette.color(QPalette.Window).lightness() < 128:
            logger.info("Dark mode detected, applying dark theme")
            self._apply_dark_theme()
        else:
            logger.info("Light mode detected, applying light theme")
            self._apply_light_theme()

    def _apply_dark_theme(self) -> None:
        """
        Apply dark theme to the application.
        """
        # Set dark theme for the entire application
        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #444444;
            }
            #headerFrame {
                background-color: #252525;
                border: none;
            }
            #contentContainer {
                background-color: #2d2d2d;
                border: 1px solid #444444;
            }
            #headerTitle, #mainTitle {
                color: #ffffff;
                font-weight: bold;
            }
            #mainDescription, #footerLabel, #statusLabel {
                color: #cccccc;
            }
            #sectionTitle, #fieldLabel {
                color: #ffffff;
                font-weight: bold;
            }
            #searchFrame {
                background-color: #2d2d2d;
                border-radius: 4px;
                border: 1px solid #444444;
            }
            #searchInput {
                border: none;
                padding: 4px;
                background-color: transparent;
                color: #ffffff;
            }
            #searchButton {
                background-color: #0d47a1;
                color: #ffffff;
                border-radius: 4px;
                padding: 4px 10px;
            }
            #searchButton:hover {
                background-color: #1565c0;
            }
            #separator {
                background-color: #444444;
            }
            QPushButton {
                background-color: #0d47a1;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0a3880;
            }
            #homeButton {
                background-color: #424242;
                color: #ffffff;
                border: none;
                font-weight: bold;
            }
            #homeButton:hover {
                background-color: #616161;
            }
            #homeButton:pressed {
                background-color: #212121;
            }
            QLabel {
                color: #ffffff;
                border: none;
            }
            QStatusBar {
                background-color: #252525;
                color: #ffffff;
            }
            QSplitter::handle {
                background-color: #444444;
            }
            QSplitter::handle:hover {
                background-color: #0d47a1;
            }
            QPlainTextEdit, QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444444;
                selection-background-color: #0d47a1;
                selection-color: #ffffff;
            }
            QListWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444444;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:hover {
                background-color: #3d3d3d;
            }
            QListWidget::item:selected {
                background-color: #0d47a1;
                color: #ffffff;
            }
            QComboBox {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444444;
                padding: 1px 18px 1px 3px;
                min-width: 6em;
            }
            QComboBox:hover {
                background-color: #3d3d3d;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left: 1px solid #444444;
            }
            QCheckBox {
                color: #ffffff;
            }
            QCheckBox::indicator {
                width: 13px;
                height: 13px;
                border: 1px solid #444444;
                background-color: #1e1e1e;
            }
            QCheckBox::indicator:checked {
                background-color: #0d47a1;
            }
        """
        )

    def _apply_light_theme(self) -> None:
        """
        Apply light theme to the application.
        """
        # Set light theme for the entire application
        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background-color: #f5f5f5;
                color: #212121;
            }
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
            }
            #headerFrame {
                background-color: #f8f8f8;
                border: none;
            }
            #contentContainer {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
            }
            #headerTitle, #mainTitle {
                color: #212121;
                font-weight: bold;
            }
            #mainDescription, #footerLabel, #statusLabel {
                color: #666666;
            }
            #sectionTitle, #fieldLabel {
                color: #212121;
                font-weight: bold;
            }
            #searchFrame {
                background-color: white;
                border-radius: 4px;
                border: 1px solid #cccccc;
            }
            #searchInput {
                border: none;
                padding: 4px;
                background-color: transparent;
                color: #212121;
            }
            #searchButton {
                background-color: #2196F3;
                color: white;
                border-radius: 4px;
                padding: 4px 10px;
            }
            #searchButton:hover {
                background-color: #1976D2;
            }
            #separator {
                background-color: #cccccc;
            }
            QPushButton {
                background-color: #2196F3;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            #homeButton {
                background-color: #e0e0e0;
                color: #212121;
                border: none;
                font-weight: bold;
            }
            #homeButton:hover {
                background-color: #d0d0d0;
            }
            #homeButton:pressed {
                background-color: #bdbdbd;
            }
            QLabel {
                color: #212121;
                border: none;
            }
            QStatusBar {
                background-color: #f8f8f8;
                color: #212121;
            }
            QSplitter::handle {
                background-color: #e0e0e0;
            }
            QSplitter::handle:hover {
                background-color: #2196F3;
            }
            QPlainTextEdit, QTextEdit {
                background-color: #ffffff;
                color: #212121;
                border: 1px solid #e0e0e0;
                selection-background-color: #bbdefb;
                selection-color: #212121;
            }
            QListWidget {
                background-color: #ffffff;
                color: #212121;
                border: 1px solid #e0e0e0;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
            QListWidget::item:selected {
                background-color: #bbdefb;
                color: #212121;
            }
            QComboBox {
                background-color: #ffffff;
                color: #212121;
                border: 1px solid #e0e0e0;
                padding: 1px 18px 1px 3px;
                min-width: 6em;
            }
            QComboBox:hover {
                background-color: #f5f5f5;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left: 1px solid #e0e0e0;
            }
            QCheckBox {
                color: #212121;
            }
            QCheckBox::indicator {
                width: 13px;
                height: 13px;
                border: 1px solid #e0e0e0;
                background-color: #ffffff;
            }
            QCheckBox::indicator:checked {
                background-color: #2196F3;
            }
        """
        )

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
