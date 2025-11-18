"""
Keyboard shortcuts manager for the annotation toolkit GUI.

Provides centralized keyboard shortcut management and help overlay.
"""

from typing import Callable, Dict, List, Optional, Tuple
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QWidget,
    QFrame,
    QPushButton,
)


class ShortcutManager:
    """
    Manages keyboard shortcuts across the application.
    """

    def __init__(self):
        """Initialize the shortcut manager."""
        self.shortcuts: Dict[str, Dict[str, any]] = {}
        self._register_default_shortcuts()

    def _register_default_shortcuts(self):
        """Register default application shortcuts."""
        # Navigation shortcuts
        self.register(
            "Home",
            "Ctrl+H",
            "Navigate to home screen",
            category="Navigation"
        )

        # Tools
        self.register(
            "URL Dictionary to Clickables",
            "Ctrl+1",
            "Open URL Dictionary to Clickables tool",
            category="Tools"
        )
        self.register(
            "JSON Visualizer",
            "Ctrl+2",
            "Open JSON Visualizer tool",
            category="Tools"
        )
        self.register(
            "Text Cleaner",
            "Ctrl+3",
            "Open Text Cleaner tool",
            category="Tools"
        )
        self.register(
            "Conversation Generator",
            "Ctrl+4",
            "Open Conversation Generator tool",
            category="Tools"
        )
        self.register(
            "Text Collector",
            "Ctrl+5",
            "Open Text Collector tool",
            category="Tools"
        )

        # Application
        self.register(
            "Help",
            "F1",
            "Show keyboard shortcuts",
            category="Application"
        )
        self.register(
            "Quit",
            "Ctrl+Q",
            "Quit application",
            category="Application"
        )
        self.register(
            "Toggle Theme",
            "Ctrl+T",
            "Toggle between light and dark theme",
            category="Application"
        )

        # Edit actions
        self.register(
            "Undo",
            "Ctrl+Z",
            "Undo last action",
            category="Edit"
        )
        self.register(
            "Redo",
            "Ctrl+Shift+Z",
            "Redo last undone action",
            category="Edit"
        )

    def register(
        self,
        action: str,
        key_sequence: str,
        description: str,
        category: str = "General",
        callback: Optional[Callable] = None
    ):
        """
        Register a keyboard shortcut.

        Args:
            action: Action name/identifier
            key_sequence: Qt key sequence (e.g., "Ctrl+S")
            description: Human-readable description
            category: Shortcut category for organization
            callback: Optional callback function
        """
        self.shortcuts[action] = {
            "sequence": key_sequence,
            "description": description,
            "category": category,
            "callback": callback,
        }

    def get_shortcut(self, action: str) -> Optional[str]:
        """Get the key sequence for an action."""
        return self.shortcuts.get(action, {}).get("sequence")

    def get_all_shortcuts(self) -> Dict[str, List[Tuple[str, str, str]]]:
        """
        Get all shortcuts organized by category.

        Returns:
            Dict mapping category names to lists of (action, sequence, description) tuples
        """
        organized = {}
        for action, data in self.shortcuts.items():
            category = data["category"]
            if category not in organized:
                organized[category] = []
            organized[category].append((
                action,
                data["sequence"],
                data["description"]
            ))

        # Sort each category's shortcuts
        for category in organized:
            if category == "Tools":
                # Sort tools by their number (Ctrl+1, Ctrl+2, etc.)
                organized[category].sort(key=lambda x: x[1])  # Sort by sequence
            else:
                # Sort others alphabetically by action name
                organized[category].sort(key=lambda x: x[0])

        return organized

    def execute_shortcut(self, action: str) -> bool:
        """
        Execute the callback for a shortcut action.

        Args:
            action: Action name

        Returns:
            True if callback was executed, False otherwise
        """
        shortcut = self.shortcuts.get(action)
        if shortcut and shortcut.get("callback"):
            shortcut["callback"]()
            return True
        return False


class ShortcutHelpDialog(QDialog):
    """
    Dialog displaying all available keyboard shortcuts.
    """

    def __init__(self, shortcut_manager: ShortcutManager, parent=None):
        """
        Initialize the help dialog.

        Args:
            shortcut_manager: ShortcutManager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.shortcut_manager = shortcut_manager
        self.setWindowTitle("Keyboard Shortcuts")
        self.setMinimumSize(600, 500)
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("Keyboard Shortcuts")
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(header)

        # Description
        desc = QLabel("Use these keyboard shortcuts to navigate and work more efficiently.")
        desc.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #7f8c8d;
                margin-bottom: 10px;
            }
        """)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Scroll area for shortcuts
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)

        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(0, 0, 10, 0)

        # Get organized shortcuts
        shortcuts_by_category = self.shortcut_manager.get_all_shortcuts()

        # Display each category
        category_order = ["Navigation", "Tools", "Application"]
        for category in category_order:
            if category not in shortcuts_by_category:
                continue

            shortcuts = shortcuts_by_category[category]

            # Category header
            category_label = QLabel(category)
            category_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #34495e;
                    margin-top: 10px;
                    margin-bottom: 5px;
                }
            """)
            content_layout.addWidget(category_label)

            # Category shortcuts
            for action, sequence, description in shortcuts:
                shortcut_row = self._create_shortcut_row(sequence, description)
                content_layout.addWidget(shortcut_row)

        content_layout.addStretch()
        scroll.setWidget(content_widget)
        layout.addWidget(scroll, 1)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(40)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _create_shortcut_row(self, sequence: str, description: str) -> QFrame:
        """
        Create a row displaying a single shortcut.

        Args:
            sequence: Key sequence
            description: Shortcut description

        Returns:
            QFrame containing the shortcut row
        """
        row = QFrame()
        row.setFrameShape(QFrame.StyledPanel)
        row.setStyleSheet("""
            QFrame {
                background-color: rgba(52, 152, 219, 0.05);
                border-radius: 6px;
                padding: 8px;
            }
        """)

        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(12, 8, 12, 8)

        # Key sequence badge
        key_label = QLabel(sequence)
        key_label.setFixedHeight(28)
        key_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 4px 12px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        row_layout.addWidget(key_label)

        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #34495e;
            }
        """)
        row_layout.addWidget(desc_label, 1)

        return row

    def keyPressEvent(self, event):
        """Handle key press events - close on Escape or F1."""
        if event.key() in (Qt.Key_Escape, Qt.Key_F1):
            self.accept()
        else:
            super().keyPressEvent(event)
