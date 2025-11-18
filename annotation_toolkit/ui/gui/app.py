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
from ...core.conversation.generator import ConversationGenerator
from ...core.conversation.visualizer import JsonVisualizer
from ...core.text.dict_to_bullet import DictToBulletList
from ...core.text.text_cleaner import TextCleaner
from ...core.text.text_collector import TextCollector
from ...di import ConfigInterface, DIContainer, LoggerInterface
from ...di.bootstrap import (
    bootstrap_application,
    get_tool_instances,
    validate_container_configuration,
)
from ...utils import logger
from .widgets.conversation_generator_widget import ConversationGeneratorWidget
from .widgets.dict_widget import DictToBulletWidget
from .widgets.json_widget import JsonVisualizerWidget
from .widgets.main_menu import MainMenuWidget
from .widgets.text_cleaner_widget import TextCleanerWidget
from .widgets.text_collector_widget import TextCollectorWidget
from .sidebar import CollapsibleSidebar
from .themes import ThemeManager, StylesheetGenerator
from .utils.shortcuts import ShortcutManager, ShortcutHelpDialog
from .utils.auto_save import AutoSaveManager
from .utils.session_manager import SessionManager


class AnnotationToolkitApp(QMainWindow):
    """
    Main GUI application for the annotation swiss knife.
    """

    def __init__(
        self, config: Optional[Config] = None, container: Optional[DIContainer] = None
    ):
        """
        Initialize the main application.

        Args:
            config (Optional[Config]): The configuration.
                If None, a default configuration is created.
            container (Optional[DIContainer]): The DI container.
                If None, a new container will be bootstrapped.
        """
        super().__init__()
        logger.info("Initializing Annotation Swiss Knife GUI application")

        # Load fonts early to prevent loading delays and set application font
        self._load_fonts()

        # Set the application font globally to prevent Qt from looking for other fonts
        app_font = QFont(getattr(self, "selected_font_family", "Arial"), 12)
        app_font.setLetterSpacing(QFont.PercentageSpacing, 100)  # Ensure normal letter spacing
        app_font.setWordSpacing(0)  # Ensure normal word spacing
        QApplication.instance().setFont(app_font)

        # Initialize configuration only once
        if config is not None:
            self.config = config
            logger.debug("Using provided configuration")
        else:
            self.config = Config()
            logger.info("Using default configuration")
            logger.info("Configuration initialized successfully")

        # Initialize or use provided DI container
        if container is None:
            logger.info("Bootstrapping DI container")
            self.container = bootstrap_application(self.config)

            # Validate container configuration
            if not validate_container_configuration(self.container):
                raise RuntimeError("DI container validation failed")

            logger.info("DI container initialized and validated successfully")
        else:
            logger.info("Using provided DI container")
            self.container = container

        # Set up tools using dependency injection
        self.tools = {}
        self._initialize_tools()

        # Initialize session manager
        self.session_manager = SessionManager()

        # Initialize auto-save manager
        self.auto_save_manager = AutoSaveManager(interval_seconds=60)

        # Set up UI
        self._init_ui()

        # Restore window state from previous session
        self.session_manager.restore_window_state(self)

        # Set up keyboard shortcuts
        self._setup_shortcuts()

        # Start auto-save
        self.auto_save_manager.start()

        logger.info("GUI application initialized successfully")

    def _initialize_tools(self) -> None:
        """
        Initialize the annotation tools using dependency injection.
        """
        logger.info("Initializing annotation tools using DI container")

        try:
            # Get tool instances from the DI container
            self.tools = get_tool_instances(self.container)

            logger.info(f"Successfully initialized {len(self.tools)} tools via DI:")
            for tool_name in self.tools:
                logger.debug(f"  - {tool_name}")

        except Exception as e:
            logger.error(f"Failed to initialize tools via DI container: {e}")

            # Fallback to manual initialization if DI fails
            logger.warning("Falling back to manual tool initialization")
            self._initialize_tools_fallback()

    def _initialize_tools_fallback(self) -> None:
        """
        Fallback method to initialize tools manually if DI fails.

        This method preserves the original tool initialization logic
        as a safety net.
        """
        logger.info("Initializing annotation tools (fallback mode)")

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
                default="#00FFFF",
            )
            ai_message_color = self.config.get(
                "tools",
                "conversation_visualizer",
                "ai_message_color",
                default="#00FF7F",
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

        # Initialize Conversation Generator tool
        conv_gen_enabled = self.config.get(
            "tools", "conversation_generator", "enabled", default=True
        )
        logger.debug(f"Conversation Generator tool enabled: {conv_gen_enabled}")

        if conv_gen_enabled:
            max_turns = self.config.get(
                "tools", "conversation_generator", "max_turns", default=20
            )
            conv_gen_tool = ConversationGenerator(max_turns=max_turns)
            self.tools[conv_gen_tool.name] = conv_gen_tool
            logger.info(f"Initialized tool: {conv_gen_tool.name}")

        logger.info(f"Initialized {len(self.tools)} tools (fallback mode)")

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

        # Main layout - horizontal to accommodate sidebar
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create sidebar
        self.sidebar = CollapsibleSidebar(self.tools, self)
        self.sidebar.tool_selected.connect(self._on_sidebar_tool_selected)
        main_layout.addWidget(self.sidebar)

        # Right side: header and content
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(12)

        # Simplified header with just the title
        header_frame = QFrame()
        header_frame.setFrameShape(QFrame.StyledPanel)
        header_frame.setObjectName("headerFrame")
        header_frame.setFixedHeight(50)  # Compact header

        # Add subtle shadow to header
        header_shadow = QGraphicsDropShadowEffect()
        header_shadow.setBlurRadius(10)
        header_shadow.setXOffset(0)
        header_shadow.setYOffset(2)
        header_shadow.setColor(QColor(0, 0, 0, 30))
        header_frame.setGraphicsEffect(header_shadow)

        # Header layout
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 8, 20, 8)

        # Title
        title_font_size = self.config.get("ui", "font_size", default=14) + 2
        header_title = QLabel("Annotation Swiss Knife")
        header_title.setFont(
            QFont(self.selected_font_family, title_font_size, QFont.Bold)
        )
        header_title.setAlignment(Qt.AlignCenter)
        header_title.setObjectName("headerTitle")
        header_layout.addWidget(header_title)

        right_layout.addWidget(header_frame)

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

        # Add URL Dictionary to Clickables tool widget
        if "URL Dictionary to Clickables" in self.tools:
            self.dict_widget = DictToBulletWidget(
                self.tools["URL Dictionary to Clickables"]
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

        # Add Conversation Generator tool widget
        if "Conversation Generator" in self.tools:
            self.conv_gen_widget = ConversationGeneratorWidget(
                self.tools["Conversation Generator"]
            )
            self.stacked_widget.addWidget(self.conv_gen_widget)

        # Add Text Collector tool widget
        if "Text Collector" in self.tools:
            self.text_collector_widget = TextCollectorWidget(
                self.tools["Text Collector"]
            )
            self.stacked_widget.addWidget(self.text_collector_widget)

        content_layout.addWidget(self.stacked_widget)
        right_layout.addWidget(content_container, 1)  # Give it stretch factor

        # Add right widget to main layout
        main_layout.addWidget(right_widget, 1)  # Content takes remaining space

        # Status bar with modern styling
        self.status_bar = QStatusBar()
        self.status_bar.setObjectName("statusBar")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Start with the main menu
        self.stacked_widget.setCurrentIndex(0)
        self.sidebar.set_active_tool("Home")

        # Set up theme support - do this after all UI elements are created
        self._setup_theme()

    def _load_fonts(self) -> None:
        """
        Load custom fonts for the application.
        """
        # Use system fonts to avoid the 157ms font loading delay
        # Preference order: system-specific fonts that are commonly available
        try:
            font_db = QFontDatabase()
            available_fonts = font_db.families()

            # Define font preference order based on platform
            import platform

            system = platform.system()

            if system == "Darwin":  # macOS
                preferred_fonts = [
                    "SF Pro Display",
                    "Helvetica Neue",
                    ".AppleSystemUIFont",
                    "Arial",
                ]
            elif system == "Windows":
                preferred_fonts = ["Segoe UI", "Calibri", "Arial"]
            else:  # Linux and others
                preferred_fonts = ["Ubuntu", "Roboto", "DejaVu Sans", "Arial"]

            # Find the first available preferred font
            self.selected_font_family = None
            for font in preferred_fonts:
                if font in available_fonts or font.startswith(
                    "-"
                ):  # -apple-system is special
                    self.selected_font_family = font
                    logger.debug(f"Using font family: {font}")
                    break

            if not self.selected_font_family:
                self.selected_font_family = "Arial"  # Fallback to Arial
                logger.debug("Using fallback font: Arial")

        except Exception as e:
            logger.warning(f"Error loading custom fonts: {str(e)}")
            self.selected_font_family = "Arial"

    def _on_sidebar_tool_selected(self, tool_name: str):
        """
        Handle tool selection from sidebar.

        Args:
            tool_name: Name of the selected tool or "Home"
        """
        logger.info(f"Sidebar: Selected {tool_name}")

        if tool_name == "Home":
            self.stacked_widget.setCurrentIndex(0)
            self.status_bar.showMessage("Main Menu")
        else:
            self.switch_to_tool(tool_name)

    def _go_to_home(self) -> None:
        """
        Switch to the main menu with a smooth transition.
        """
        logger.info("Navigating to home/main menu")

        # Update sidebar
        self.sidebar.set_active_tool("Home")
        # Switch to main menu
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

        if tool_name == "URL Dictionary to Clickables":
            target_widget = self.dict_widget
            logger.debug(f"Switching to URL Dictionary to Clickables tool")
        elif tool_name == "JSON Visualizer":
            target_widget = self.json_widget
            logger.debug(f"Switching to JSON Visualizer tool")
        elif tool_name == "Text Cleaner":
            target_widget = self.text_cleaner_widget
            logger.debug(f"Switching to Text Cleaner tool")
        elif tool_name == "Conversation Generator":
            target_widget = self.conv_gen_widget
            logger.debug(f"Switching to Conversation Generator tool")
        elif tool_name == "Text Collector":
            target_widget = self.text_collector_widget
            logger.debug(f"Switching to Text Collector tool")
        else:
            logger.error(f"Unknown tool: {tool_name}")
            raise ValueError(f"Unknown tool: {tool_name}")

        if target_widget:
            # Switch to the target widget
            # Note: Fade animations removed due to rendering issues with QGraphicsOpacityEffect
            # on complex widgets with layouts. Opacity effects interfere with child widget rendering.
            self.stacked_widget.setCurrentWidget(target_widget)

            self.status_bar.showMessage(f"Using {tool_name}")
            # Update sidebar active state
            self.sidebar.set_active_tool(tool_name)
    def _setup_theme(self) -> None:
        """
        Set up the glassmorphism theme system with dynamic theme switching.
        """
        logger.info("Initializing glassmorphism theme system")

        # Initialize theme manager
        self.theme_manager = ThemeManager.instance()

        # Load theme preference from config
        self.theme_manager.load_preference(self.config)

        # Connect to theme change signal for dynamic updates
        self.theme_manager.theme_changed.connect(self._on_theme_changed)

        # Apply initial theme
        self._apply_current_theme()

        logger.info(f"Theme system initialized - Mode: {self.theme_manager.current_mode.value}, "
                   f"Is Dark: {self.theme_manager.is_dark_mode}")

    def _apply_current_theme(self) -> None:
        """
        Apply the current theme from ThemeManager using StylesheetGenerator.
        """
        theme = self.theme_manager.current_theme
        generator = StylesheetGenerator(theme)

        # Generate and apply main application stylesheet
        app_stylesheet = generator.generate_app_stylesheet()
        self.setStyleSheet(app_stylesheet)

        # Update sidebar stylesheet if it exists
        if hasattr(self, 'sidebar') and self.sidebar:
            sidebar_stylesheet = generator.generate_sidebar_stylesheet(
                collapsed=getattr(self.sidebar, '_collapsed', False)
            )
            self.sidebar.setStyleSheet(sidebar_stylesheet)

        logger.debug(f"Applied {'dark' if theme.is_dark else 'light'} glassmorphism theme")

    def _on_theme_changed(self, new_theme) -> None:
        """
        Handle theme changes from ThemeManager.

        Args:
            new_theme: The new GlassTheme instance
        """
        logger.info(f"Theme changed to: {new_theme.name}")
        self._apply_current_theme()

        # Save theme preference
        self.theme_manager.save_preference(self.config)

    def _setup_shortcuts(self) -> None:
        """
        Set up keyboard shortcuts and register callbacks.
        """
        logger.info("Setting up keyboard shortcuts")
        self.shortcut_manager = ShortcutManager()

        # Register callbacks for shortcuts
        self.shortcut_manager.shortcuts["Home"]["callback"] = lambda: self.sidebar.home_btn.click()
        self.shortcut_manager.shortcuts["Toggle Theme"]["callback"] = self.toggle_theme
        self.shortcut_manager.shortcuts["Help"]["callback"] = self.show_shortcut_help
        self.shortcut_manager.shortcuts["Quit"]["callback"] = self.close

        # Register tool shortcuts
        if "Dictionary to Bullet List" in self.tools:
            self.shortcut_manager.shortcuts["Dictionary to Bullet List"]["callback"] = \
                lambda: self.switch_to_tool("Dictionary to Bullet List")

        if "JSON Visualizer" in self.tools:
            self.shortcut_manager.shortcuts["JSON Visualizer"]["callback"] = \
                lambda: self.switch_to_tool("JSON Visualizer")

        if "Text Cleaner" in self.tools:
            self.shortcut_manager.shortcuts["Text Cleaner"]["callback"] = \
                lambda: self.switch_to_tool("Text Cleaner")

        if "Conversation Generator" in self.tools:
            self.shortcut_manager.shortcuts["Conversation Generator"]["callback"] = \
                lambda: self.switch_to_tool("Conversation Generator")

        if "Text Collector" in self.tools:
            self.shortcut_manager.shortcuts["Text Collector"]["callback"] = \
                lambda: self.switch_to_tool("Text Collector")

        logger.info(f"Registered {len(self.shortcut_manager.shortcuts)} keyboard shortcuts")

    def show_shortcut_help(self) -> None:
        """Show the keyboard shortcuts help dialog."""
        dialog = ShortcutHelpDialog(self.shortcut_manager, self)
        dialog.exec_()

    def keyPressEvent(self, event) -> None:
        """
        Handle keyboard shortcuts.

        Args:
            event: The key press event
        """
        # Check for F1 (help)
        if event.key() == Qt.Key_F1:
            self.show_shortcut_help()
            event.accept()
            return

        # Check for Ctrl+Q (quit)
        if event.key() == Qt.Key_Q and event.modifiers() == Qt.ControlModifier:
            self.close()
            event.accept()
            return

        # Check for Ctrl+H (home)
        if event.key() == Qt.Key_H and event.modifiers() == Qt.ControlModifier:
            self.sidebar.home_btn.click()
            event.accept()
            return

        # Check for Ctrl+T (toggle theme)
        if event.key() == Qt.Key_T and event.modifiers() == Qt.ControlModifier:
            self.toggle_theme()
            event.accept()
            return

        # Check for Ctrl+1-5 (tool shortcuts)
        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_1 and "Dictionary to Bullet List" in self.tools:
                self.switch_to_tool("Dictionary to Bullet List")
                event.accept()
                return
            elif event.key() == Qt.Key_2 and "JSON Visualizer" in self.tools:
                self.switch_to_tool("JSON Visualizer")
                event.accept()
                return
            elif event.key() == Qt.Key_3 and "Text Cleaner" in self.tools:
                self.switch_to_tool("Text Cleaner")
                event.accept()
                return
            elif event.key() == Qt.Key_4 and "Conversation Generator" in self.tools:
                self.switch_to_tool("Conversation Generator")
                event.accept()
                return
            elif event.key() == Qt.Key_5 and "Text Collector" in self.tools:
                self.switch_to_tool("Text Collector")
                event.accept()
                return

        # Pass unhandled events to parent
        super().keyPressEvent(event)

    def toggle_theme(self) -> None:
        """
        Toggle between light and dark themes.

        This method can be called from menu actions or keyboard shortcuts.
        """
        self.theme_manager.toggle_theme()


    def closeEvent(self, event) -> None:
        """
        Handle the window close event.

        Save window state, session data, and perform cleanup.

        Args:
            event: The close event.
        """
        logger.info("Application closing")

        # Stop auto-save
        if hasattr(self, 'auto_save_manager'):
            self.auto_save_manager.stop()

        # Save window state to session
        if hasattr(self, 'session_manager'):
            self.session_manager.save_window_state(self)

        # Save window size to config (legacy)
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
