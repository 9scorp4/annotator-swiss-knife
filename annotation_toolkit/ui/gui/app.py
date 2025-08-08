"""
Main GUI application for the annotation swiss knife.

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
    Main GUI application for the annotation swiss knife.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the main application.

        Args:
            config (Optional[Config]): The configuration.
                If None, a default configuration is created.
        """
        super().__init__()
        logger.info("Initializing Annotation Swiss Knife GUI application")

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
        self.setWindowTitle("Annotation Swiss Knife")

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
        header_title = QLabel("Annotation Swiss Knife")
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
        # Set dark theme for the entire application with enhanced modern styling
        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #1a1a1a, stop: 1 #0f0f0f);
                color: #e8e8e8;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            QFrame {
                background-color: rgba(45, 45, 45, 0.95);
                border: 1px solid rgba(68, 68, 68, 0.6);
                border-radius: 12px;
            }
            #headerFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(40, 40, 40, 0.98), stop: 1 rgba(30, 30, 30, 0.98));
                border: none;
                border-radius: 15px;
                padding: 5px;
            }
            #contentContainer {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(45, 45, 45, 0.98), stop: 1 rgba(35, 35, 35, 0.98));
                border: 1px solid rgba(68, 68, 68, 0.4);
                border-radius: 15px;
            }
            #headerTitle, #mainTitle {
                color: #ffffff;
                font-weight: 600;
                text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
            }
            #mainDescription, #footerLabel, #statusLabel {
                color: #b8b8b8;
                font-weight: 400;
            }
            #sectionTitle, #fieldLabel {
                color: #ffffff;
                font-weight: 600;
                text-shadow: 0 1px 1px rgba(0, 0, 0, 0.2);
            }
            #searchFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(50, 50, 50, 0.9), stop: 1 rgba(40, 40, 40, 0.9));
                border-radius: 8px;
                border: 1px solid rgba(68, 68, 68, 0.5);
                padding: 2px;
            }
            #searchInput {
                border: none;
                padding: 8px 12px;
                background-color: transparent;
                color: #ffffff;
                font-size: 13px;
                border-radius: 6px;
            }
            #searchInput:focus {
                background-color: rgba(255, 255, 255, 0.05);
                outline: 2px solid rgba(33, 150, 243, 0.5);
            }
            #searchButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2196F3, stop: 1 #1976D2);
                color: #ffffff;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                border: none;
            }
            #searchButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #42A5F5, stop: 1 #1E88E5);
            }
            #searchButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #1976D2, stop: 1 #0D47A1);
            }
            #separator {
                background-color: rgba(68, 68, 68, 0.6);
                border-radius: 1px;
            }
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2196F3, stop: 1 #1976D2);
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
                min-height: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #42A5F5, stop: 1 #1E88E5);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #1976D2, stop: 1 #0D47A1);
            }
            QPushButton:focus {
                outline: 2px solid rgba(33, 150, 243, 0.5);
                outline-offset: 2px;
            }
            #homeButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(66, 66, 66, 0.9), stop: 1 rgba(48, 48, 48, 0.9));
                color: #ffffff;
                border: none;
                font-weight: 600;
                border-radius: 8px;
                padding: 8px 16px;
            }
            #homeButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(97, 97, 97, 0.9), stop: 1 rgba(66, 66, 66, 0.9));
                transform: translateY(-1px);
            }
            #homeButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(33, 33, 33, 0.9), stop: 1 rgba(24, 24, 24, 0.9));
                transform: translateY(0px);
            }
            QLabel {
                color: #e8e8e8;
                border: none;
            }
            QStatusBar {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(37, 37, 37, 0.95), stop: 1 rgba(25, 25, 25, 0.95));
                color: #b8b8b8;
                border-top: 1px solid rgba(68, 68, 68, 0.3);
                padding: 5px;
            }
            QSplitter::handle {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(68, 68, 68, 0.6), stop: 0.5 rgba(100, 100, 100, 0.8), stop: 1 rgba(68, 68, 68, 0.6));
                border-radius: 4px;
                margin: 2px;
            }
            QSplitter::handle:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(33, 150, 243, 0.6), stop: 0.5 rgba(33, 150, 243, 0.9), stop: 1 rgba(33, 150, 243, 0.6));
            }
            QPlainTextEdit, QTextEdit {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(30, 30, 30, 0.95), stop: 1 rgba(20, 20, 20, 0.95));
                color: #e8e8e8;
                border: 1px solid rgba(68, 68, 68, 0.5);
                border-radius: 8px;
                padding: 12px;
                selection-background-color: rgba(33, 150, 243, 0.3);
                selection-color: #ffffff;
                font-size: 13px;
                line-height: 1.4;
            }
            QPlainTextEdit:focus, QTextEdit:focus {
                border: 2px solid rgba(33, 150, 243, 0.6);
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(35, 35, 35, 0.95), stop: 1 rgba(25, 25, 25, 0.95));
            }
            QListWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(30, 30, 30, 0.95), stop: 1 rgba(20, 20, 20, 0.95));
                color: #e8e8e8;
                border: 1px solid rgba(68, 68, 68, 0.5);
                border-radius: 8px;
                padding: 5px;
                outline: none;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 6px;
                margin: 2px;
                border: none;
            }
            QListWidget::item:hover {
                background-color: rgba(61, 61, 61, 0.7);
                color: #ffffff;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(33, 150, 243, 0.8), stop: 1 rgba(25, 118, 210, 0.8));
                color: #ffffff;
            }
            QComboBox {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(30, 30, 30, 0.95), stop: 1 rgba(20, 20, 20, 0.95));
                color: #e8e8e8;
                border: 1px solid rgba(68, 68, 68, 0.5);
                border-radius: 6px;
                padding: 8px 18px 8px 12px;
                min-width: 6em;
                font-size: 13px;
            }
            QComboBox:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(61, 61, 61, 0.95), stop: 1 rgba(45, 45, 45, 0.95));
                border: 1px solid rgba(100, 100, 100, 0.7);
            }
            QComboBox:focus {
                border: 2px solid rgba(33, 150, 243, 0.6);
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid rgba(68, 68, 68, 0.5);
                border-radius: 0px 6px 6px 0px;
            }
            QComboBox::down-arrow {
                image: none;
                border: 2px solid #e8e8e8;
                border-top: none;
                border-right: none;
                width: 6px;
                height: 6px;
                transform: rotate(45deg);
                margin-top: -3px;
            }
            QCheckBox {
                color: #e8e8e8;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid rgba(68, 68, 68, 0.7);
                border-radius: 4px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(30, 30, 30, 0.95), stop: 1 rgba(20, 20, 20, 0.95));
            }
            QCheckBox::indicator:hover {
                border: 2px solid rgba(100, 100, 100, 0.8);
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(45, 45, 45, 0.95), stop: 1 rgba(35, 35, 35, 0.95));
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2196F3, stop: 1 #1976D2);
                border: 2px solid #1976D2;
            }
            QCheckBox::indicator:checked:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #42A5F5, stop: 1 #1E88E5);
            }
        """
        )

    def _apply_light_theme(self) -> None:
        """
        Apply light theme to the application.
        """
        # Set light theme for the entire application with enhanced modern styling
        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #fafafa, stop: 1 #f0f0f0);
                color: #1a1a1a;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border: 1px solid rgba(224, 224, 224, 0.6);
                border-radius: 12px;
            }
            #headerFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(255, 255, 255, 0.98), stop: 1 rgba(248, 248, 248, 0.98));
                border: none;
                border-radius: 15px;
                padding: 5px;
            }
            #contentContainer {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(255, 255, 255, 0.98), stop: 1 rgba(250, 250, 250, 0.98));
                border: 1px solid rgba(224, 224, 224, 0.4);
                border-radius: 15px;
            }
            #headerTitle, #mainTitle {
                color: #1a1a1a;
                font-weight: 600;
                text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8);
            }
            #mainDescription, #footerLabel, #statusLabel {
                color: #666666;
                font-weight: 400;
            }
            #sectionTitle, #fieldLabel {
                color: #1a1a1a;
                font-weight: 600;
                text-shadow: 0 1px 1px rgba(255, 255, 255, 0.5);
            }
            #searchFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(255, 255, 255, 0.9), stop: 1 rgba(248, 248, 248, 0.9));
                border-radius: 8px;
                border: 1px solid rgba(204, 204, 204, 0.5);
                padding: 2px;
            }
            #searchInput {
                border: none;
                padding: 8px 12px;
                background-color: transparent;
                color: #1a1a1a;
                font-size: 13px;
                border-radius: 6px;
            }
            #searchInput:focus {
                background-color: rgba(33, 150, 243, 0.05);
                outline: 2px solid rgba(33, 150, 243, 0.3);
            }
            #searchButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2196F3, stop: 1 #1976D2);
                color: #ffffff;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                border: none;
            }
            #searchButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #42A5F5, stop: 1 #1E88E5);
            }
            #searchButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #1976D2, stop: 1 #0D47A1);
            }
            #separator {
                background-color: rgba(204, 204, 204, 0.6);
                border-radius: 1px;
            }
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2196F3, stop: 1 #1976D2);
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
                min-height: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #42A5F5, stop: 1 #1E88E5);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #1976D2, stop: 1 #0D47A1);
            }
            QPushButton:focus {
                outline: 2px solid rgba(33, 150, 243, 0.5);
                outline-offset: 2px;
            }
            #homeButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(224, 224, 224, 0.9), stop: 1 rgba(208, 208, 208, 0.9));
                color: #1a1a1a;
                border: none;
                font-weight: 600;
                border-radius: 8px;
                padding: 8px 16px;
            }
            #homeButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(189, 189, 189, 0.9), stop: 1 rgba(158, 158, 158, 0.9));
                transform: translateY(-1px);
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
            }
            #homeButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(158, 158, 158, 0.9), stop: 1 rgba(117, 117, 117, 0.9));
                transform: translateY(0px);
            }
            QLabel {
                color: #1a1a1a;
                border: none;
            }
            QStatusBar {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(248, 248, 248, 0.95), stop: 1 rgba(240, 240, 240, 0.95));
                color: #666666;
                border-top: 1px solid rgba(224, 224, 224, 0.3);
                padding: 5px;
            }
            QSplitter::handle {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(224, 224, 224, 0.6), stop: 0.5 rgba(189, 189, 189, 0.8), stop: 1 rgba(224, 224, 224, 0.6));
                border-radius: 4px;
                margin: 2px;
            }
            QSplitter::handle:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(33, 150, 243, 0.6), stop: 0.5 rgba(33, 150, 243, 0.9), stop: 1 rgba(33, 150, 243, 0.6));
            }
            QPlainTextEdit, QTextEdit {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(255, 255, 255, 0.95), stop: 1 rgba(250, 250, 250, 0.95));
                color: #1a1a1a;
                border: 1px solid rgba(224, 224, 224, 0.5);
                border-radius: 8px;
                padding: 12px;
                selection-background-color: rgba(33, 150, 243, 0.2);
                selection-color: #1a1a1a;
                font-size: 13px;
                line-height: 1.4;
            }
            QPlainTextEdit:focus, QTextEdit:focus {
                border: 2px solid rgba(33, 150, 243, 0.6);
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(255, 255, 255, 0.98), stop: 1 rgba(248, 248, 248, 0.98));
            }
            QListWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(255, 255, 255, 0.95), stop: 1 rgba(250, 250, 250, 0.95));
                color: #1a1a1a;
                border: 1px solid rgba(224, 224, 224, 0.5);
                border-radius: 8px;
                padding: 5px;
                outline: none;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 6px;
                margin: 2px;
                border: none;
            }
            QListWidget::item:hover {
                background-color: rgba(245, 245, 245, 0.8);
                color: #1a1a1a;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(33, 150, 243, 0.8), stop: 1 rgba(25, 118, 210, 0.8));
                color: #ffffff;
            }
            QComboBox {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(255, 255, 255, 0.95), stop: 1 rgba(250, 250, 250, 0.95));
                color: #1a1a1a;
                border: 1px solid rgba(224, 224, 224, 0.5);
                border-radius: 6px;
                padding: 8px 18px 8px 12px;
                min-width: 6em;
                font-size: 13px;
            }
            QComboBox:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(245, 245, 245, 0.95), stop: 1 rgba(240, 240, 240, 0.95));
                border: 1px solid rgba(189, 189, 189, 0.7);
            }
            QComboBox:focus {
                border: 2px solid rgba(33, 150, 243, 0.6);
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid rgba(224, 224, 224, 0.5);
                border-radius: 0px 6px 6px 0px;
            }
            QComboBox::down-arrow {
                image: none;
                border: 2px solid #1a1a1a;
                border-top: none;
                border-right: none;
                width: 6px;
                height: 6px;
                transform: rotate(45deg);
                margin-top: -3px;
            }
            QCheckBox {
                color: #1a1a1a;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid rgba(224, 224, 224, 0.7);
                border-radius: 4px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(255, 255, 255, 0.95), stop: 1 rgba(250, 250, 250, 0.95));
            }
            QCheckBox::indicator:hover {
                border: 2px solid rgba(189, 189, 189, 0.8);
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(245, 245, 245, 0.95), stop: 1 rgba(240, 240, 240, 0.95));
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2196F3, stop: 1 #1976D2);
                border: 2px solid #1976D2;
            }
            QCheckBox::indicator:checked:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #42A5F5, stop: 1 #1E88E5);
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
    logger.info("Starting Annotation Swiss Knife GUI application")
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
