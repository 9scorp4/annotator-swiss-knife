"""
ErrorBanner component for inline error display.

Replaces QMessageBox with elegant inline error messages.
"""

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtGui import QFont
from ..utils.animations import animate_opacity
from ..utils.fonts import FontManager


class ErrorBanner(QFrame):
    """
    Inline error banner with auto-dismiss and animations.
    """

    closed = pyqtSignal()

    def __init__(self, message: str, error_type: str = "error", auto_dismiss: int = 0, parent=None):
        """
        Initialize error banner.

        Args:
            message: Error message to display
            error_type: Type of message ("error", "warning", "info", "success")
            auto_dismiss: Auto-dismiss after N milliseconds (0 = no auto-dismiss)
            parent: Parent widget
        """
        super().__init__(parent)
        self.message = message
        self.error_type = error_type
        self.auto_dismiss = auto_dismiss

        self._init_ui()

        # Auto-dismiss timer
        if self.auto_dismiss > 0:
            QTimer.singleShot(self.auto_dismiss, self.dismiss)

    def _init_ui(self):
        """Initialize the UI."""
        self.setObjectName("errorBanner")

        # Color scheme based on type
        colors = {
            "error": {"bg": "#FEE2E2", "border": "#DC2626", "text": "#991B1B"},
            "warning": {"bg": "#FEF3C7", "border": "#F59E0B", "text": "#92400E"},
            "info": {"bg": "#DBEAFE", "border": "#3B82F6", "text": "#1E40AF"},
            "success": {"bg": "#D1FAE5", "border": "#10B981", "text": "#065F46"},
        }

        color = colors.get(self.error_type, colors["error"])

        self.setStyleSheet(f"""
            #errorBanner {{
                background-color: {color['bg']};
                border-left: 4px solid {color['border']};
                border-radius: 6px;
                padding: 12px 16px;
            }}
        """)

        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # Icon
        icon_label = QLabel(self._get_icon())
        icon_label.setFont(FontManager.get_font(size=FontManager.SIZE_XL))
        icon_label.setStyleSheet(f"color: {color['border']};")
        layout.addWidget(icon_label)

        # Message
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(f"color: {color['text']}; font-size: 13px;")
        layout.addWidget(message_label, 1)

        # Close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {color['text']};
                font-size: 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: rgba(0, 0, 0, 0.1);
                border-radius: 4px;
            }}
        """)
        close_btn.clicked.connect(self.dismiss)
        layout.addWidget(close_btn)

    def _get_icon(self) -> str:
        """Get icon for error type."""
        icons = {
            "error": "✖",
            "warning": "⚠",
            "info": "ℹ",
            "success": "✓",
        }
        return icons.get(self.error_type, "!")

    def dismiss(self):
        """Dismiss the banner with fade animation."""
        # Fade out
        animate_opacity(
            self,
            from_opacity=1.0,
            to_opacity=0.0,
            duration=200,
            on_finished=self._on_dismissed
        )

    def _on_dismissed(self):
        """Called when dismiss animation completes."""
        self.closed.emit()
        self.deleteLater()
