"""
Base widget class for annotation tools.

Provides common patterns and utilities for all tool widgets.
"""

from typing import Optional, Any
from abc import ABCMeta, abstractmethod

from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5.sip import wrappertype

from ..themes import ThemeManager
from ....utils import logger


# Create a metaclass that combines Qt's meta with ABC
class BaseToolMeta(wrappertype, ABCMeta):
    """Metaclass for BaseToolWidget that combines Qt and ABC metaclasses."""
    pass


class BaseToolWidget(QWidget, metaclass=BaseToolMeta):
    """
    Abstract base class for all annotation tool widgets.

    Provides common functionality:
    - Theme management and automatic theme updates
    - Error handling with user-friendly dialogs
    - Status updates
    - Common UI patterns

    Subclasses must implement:
    - _init_ui(): Initialize the widget's UI components
    - tool_name property: Return the name of the tool
    """

    # Signal emitted when tool processing is complete
    processing_complete = pyqtSignal(str)  # Result message

    # Signal emitted when an error occurs
    error_occurred = pyqtSignal(str)  # Error message

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the base tool widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Initialize theme manager connection
        self.theme_manager = ThemeManager.instance()
        self.theme_manager.theme_changed.connect(self._apply_theme)

        # Setup UI
        self._init_ui()

        # Apply initial theme
        self._apply_theme()

    @property
    @abstractmethod
    def tool_name(self) -> str:
        """
        Get the name of this tool.

        Returns:
            Tool name string
        """
        pass

    @abstractmethod
    def _init_ui(self) -> None:
        """
        Initialize the user interface.

        Must be implemented by subclasses to create all UI components.
        """
        pass

    def _apply_theme(self) -> None:
        """
        Apply current theme to the widget.

        Default implementation does nothing. Override to apply theme-specific styling.
        """
        pass

    def show_error(self, title: str, message: str, details: Optional[str] = None) -> None:
        """
        Show an error dialog to the user.

        Args:
            title: Error dialog title
            message: Main error message
            details: Optional detailed error information
        """
        logger.error(f"{self.tool_name}: {message}")

        full_message = message
        if details:
            full_message += f"\n\nDetails:\n{details}"

        QMessageBox.critical(self, title, full_message)
        self.error_occurred.emit(message)

    def show_warning(self, title: str, message: str) -> None:
        """
        Show a warning dialog to the user.

        Args:
            title: Warning dialog title
            message: Warning message
        """
        logger.warning(f"{self.tool_name}: {message}")
        QMessageBox.warning(self, title, message)

    def show_info(self, title: str, message: str) -> None:
        """
        Show an information dialog to the user.

        Args:
            title: Info dialog title
            message: Information message
        """
        logger.info(f"{self.tool_name}: {message}")
        QMessageBox.information(self, title, message)

    def confirm(self, title: str, message: str) -> bool:
        """
        Show a confirmation dialog and return the user's choice.

        Args:
            title: Confirmation dialog title
            message: Confirmation message

        Returns:
            True if user confirmed (clicked Yes), False otherwise
        """
        reply = QMessageBox.question(
            self,
            title,
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes

    def set_status(self, message: str, duration: int = 3000) -> None:
        """
        Set a temporary status message.

        Args:
            message: Status message to display
            duration: Duration in milliseconds (0 for permanent)

        Note: Subclasses with a status bar should override this method.
        """
        logger.debug(f"{self.tool_name}: {message}")

    def handle_error(self, error: Exception, context: str = "Operation") -> None:
        """
        Handle an exception with logging and user notification.

        Args:
            error: The exception that occurred
            context: Context description for the error
        """
        error_message = f"{context} failed"
        self.show_error(
            f"{self.tool_name} Error",
            error_message,
            str(error)
        )

    def get_current_theme(self):
        """
        Get the current theme object.

        Returns:
            Current theme instance
        """
        return self.theme_manager.current_theme

    def apply_glass_style(self, widget: QWidget, elevated: bool = False) -> None:
        """
        Apply glassmorphic styling to a widget.

        Args:
            widget: Widget to style
            elevated: Whether to use elevated glass style
        """
        theme = self.get_current_theme()

        bg_color = theme.surface_glass_elevated if elevated else theme.surface_glass

        widget.setStyleSheet(f"""
            QWidget {{
                background: {bg_color};
                border: 1px solid {theme.border_glass};
                border-radius: 8px;
            }}
        """)
