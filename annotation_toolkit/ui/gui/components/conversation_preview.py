"""
ConversationPreview - Live preview pane for conversation data.

Shows formatted preview of conversation as it's being built.
"""

from typing import List, Dict
import json

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QApplication, QMessageBox

from .glass_button import GlassButton
from .json_highlighter import ConversationHighlighter
from .text_widgets import PlainTextEdit
from ..themes import ThemeManager


class ConversationPreview(QWidget):
    """
    Live preview pane for conversation data.

    Features:
    - Formatted text view
    - Syntax-highlighted JSON view
    - Auto-updates when conversation changes
    - Theme-aware styling
    - Turn count display
    """

    def __init__(self, parent=None):
        """
        Initialize the conversation preview.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.conversation_data: List[Dict] = []

        # Setup UI
        self._init_ui()
        self._apply_theme()

        # Connect to theme changes
        theme_manager = ThemeManager.instance()
        theme_manager.theme_changed.connect(self._apply_theme)

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Header with title and copy button
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        self.header_label = QLabel("📺 Live Preview")
        self.header_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_layout.addWidget(self.header_label)

        header_layout.addStretch()

        # Copy button
        self.copy_button = GlassButton("📋 Copy JSON", variant="primary", size="small")
        self.copy_button.setToolTip("Copy JSON to clipboard")
        self.copy_button.clicked.connect(self._copy_json_to_clipboard)
        self.copy_button.setEnabled(False)  # Initially disabled
        header_layout.addWidget(self.copy_button)

        layout.addLayout(header_layout)

        # Turn count
        self.turn_count_label = QLabel("No turns yet")
        self.turn_count_label.setStyleSheet("font-size: 12px; color: gray;")
        layout.addWidget(self.turn_count_label)

        # Tab widget for different views
        self.tab_widget = QTabWidget()

        # Formatted text view
        self.text_view = PlainTextEdit()
        self.text_view.setReadOnly(True)
        self.text_view.setPlaceholderText("Conversation preview will appear here...")
        self.tab_widget.addTab(self.text_view, "📄 Text")

        # JSON view with syntax highlighting
        self.json_view = PlainTextEdit()
        self.json_view.setReadOnly(True)
        self.json_view.setPlaceholderText("JSON preview will appear here...")
        self.highlighter = ConversationHighlighter(self.json_view.document())
        self.tab_widget.addTab(self.json_view, "{ } JSON")

        layout.addWidget(self.tab_widget)

    def update_preview(self, conversation: List[Dict]) -> None:
        """
        Update the preview with new conversation data.

        Args:
            conversation: List of conversation turns
        """
        self.conversation_data = conversation

        # Update turn count
        turn_count = len(conversation)
        if turn_count == 0:
            self.turn_count_label.setText("No turns yet")
            self.copy_button.setEnabled(False)
        elif turn_count == 1:
            self.turn_count_label.setText("1 turn")
            self.copy_button.setEnabled(True)
        else:
            self.turn_count_label.setText(f"{turn_count} turns")
            self.copy_button.setEnabled(True)

        # Update text view
        self._update_text_view()

        # Update JSON view
        self._update_json_view()

    def _update_text_view(self) -> None:
        """Update the formatted text view."""
        if not self.conversation_data:
            self.text_view.setPlainText("")
            return

        lines = []
        lines.append("=" * 60)
        lines.append("CONVERSATION PREVIEW")
        lines.append("=" * 60)
        lines.append("")

        for i, turn in enumerate(self.conversation_data, 1):
            role = turn.get("role", "unknown")
            content = turn.get("content", "")

            # Turn header
            lines.append(f"Turn {i}: {role.upper()}")
            lines.append("-" * 60)
            lines.append(content)
            lines.append("")

        self.text_view.setPlainText("\n".join(lines))

    def _update_json_view(self) -> None:
        """Update the JSON view."""
        if not self.conversation_data:
            self.json_view.setPlainText("")
            return

        # Format JSON with indentation
        json_str = json.dumps(self.conversation_data, indent=2, ensure_ascii=False)
        self.json_view.setPlainText(json_str)

    def clear_preview(self) -> None:
        """Clear the preview."""
        self.conversation_data = []
        self.text_view.setPlainText("")
        self.json_view.setPlainText("")
        self.turn_count_label.setText("No turns yet")
        self.copy_button.setEnabled(False)

    def _copy_json_to_clipboard(self) -> None:
        """Copy the JSON to clipboard."""
        if not self.conversation_data:
            QMessageBox.information(
                self,
                "No Content",
                "There is no conversation data to copy."
            )
            return

        # Get the JSON text
        json_str = json.dumps(self.conversation_data, indent=2, ensure_ascii=False)

        # Copy to clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(json_str)

        # Show feedback
        QMessageBox.information(
            self,
            "Copied",
            f"JSON copied to clipboard!\n\n{len(json_str)} characters"
        )

    def get_conversation_summary(self) -> str:
        """
        Get a summary of the current conversation.

        Returns:
            Summary string
        """
        if not self.conversation_data:
            return "Empty conversation"

        turn_count = len(self.conversation_data)
        total_chars = sum(len(turn.get("content", "")) for turn in self.conversation_data)
        total_words = sum(len(turn.get("content", "").split()) for turn in self.conversation_data)

        return f"{turn_count} turns, {total_words} words, {total_chars} characters"

    def _apply_theme(self) -> None:
        """Apply glassmorphic theme styling."""
        theme = ThemeManager.instance().current_theme

        self.setStyleSheet(f"""
            ConversationPreview {{
                background: {theme.background_secondary};
                border: 1px solid {theme.border_glass};
                border-radius: 8px;
                padding: 12px;
            }}
            QLabel {{
                color: {theme.text_primary};
                background: transparent;
            }}
            QTabWidget::pane {{
                border: 1px solid {theme.border_glass};
                border-radius: 6px;
                background: {theme.background_primary};
            }}
            QTabBar::tab {{
                background: {theme.surface_glass};
                color: {theme.text_secondary};
                padding: 6px 12px;
                border: 1px solid {theme.border_subtle};
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }}
            QTabBar::tab:selected {{
                background: {theme.accent_primary};
                color: white;
            }}
            QTabBar::tab:hover {{
                background: {theme.surface_glass_elevated};
            }}
        """)
