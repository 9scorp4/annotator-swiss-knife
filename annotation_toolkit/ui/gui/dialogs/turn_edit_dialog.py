"""
TurnEditDialog - Dialog for editing conversation turns.

Allows editing user and assistant messages in a conversation.
"""

from typing import Optional, Tuple

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QDialogButtonBox,
)

from ..components import GlassButton
from ..widgets.custom_widgets import PlainTextEdit
from ..themes import ThemeManager


class TurnEditDialog(QDialog):
    """
    Dialog for editing a conversation turn.

    Features:
    - Edit user message
    - Edit assistant response
    - Validation (non-empty messages)
    - Theme-aware styling
    - Keyboard shortcuts (Ctrl+Enter to save)
    """

    def __init__(
        self,
        user_message: str = "",
        assistant_response: str = "",
        turn_number: int = 1,
        parent=None
    ):
        """
        Initialize the turn edit dialog.

        Args:
            user_message: Initial user message
            assistant_response: Initial assistant response
            turn_number: Turn number in conversation
            parent: Parent widget
        """
        super().__init__(parent)

        self.user_message = user_message
        self.assistant_response = assistant_response
        self.turn_number = turn_number

        # Setup dialog
        self._init_ui()
        self._apply_theme()

        # Connect to theme changes
        theme_manager = ThemeManager.instance()
        theme_manager.theme_changed.connect(self._apply_theme)

        # Set focus to user input
        self.user_input.setFocus()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle(f"Edit Turn {self.turn_number}")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header
        header_label = QLabel(f"💬 Edit Conversation Turn {self.turn_number}")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header_label)

        # User message section
        user_label = QLabel("👤 User Message:")
        user_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(user_label)

        self.user_input = PlainTextEdit()
        self.user_input.setPlaceholderText("Enter user message...")
        self.user_input.setPlainText(self.user_message)
        self.user_input.setMinimumHeight(150)
        layout.addWidget(self.user_input)

        # Character count for user
        self.user_char_count = QLabel(self._get_char_count_text(self.user_message))
        self.user_char_count.setStyleSheet("font-size: 11px; color: gray;")
        layout.addWidget(self.user_char_count)

        # Connect user input to update character count
        self.user_input.textChanged.connect(self._update_user_char_count)

        # Assistant response section
        assistant_label = QLabel("🤖 Assistant Response:")
        assistant_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(assistant_label)

        self.assistant_input = PlainTextEdit()
        self.assistant_input.setPlaceholderText("Enter assistant response...")
        self.assistant_input.setPlainText(self.assistant_response)
        self.assistant_input.setMinimumHeight(150)
        layout.addWidget(self.assistant_input)

        # Character count for assistant
        self.assistant_char_count = QLabel(self._get_char_count_text(self.assistant_response))
        self.assistant_char_count.setStyleSheet("font-size: 11px; color: gray;")
        layout.addWidget(self.assistant_char_count)

        # Connect assistant input to update character count
        self.assistant_input.textChanged.connect(self._update_assistant_char_count)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = GlassButton("Cancel", variant="ghost", size="medium")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.save_button = GlassButton("💾 Save Changes", variant="primary", size="medium")
        self.save_button.clicked.connect(self._on_save)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

        # Hint label
        hint_label = QLabel("💡 Tip: Press Ctrl+Enter to save")
        hint_label.setStyleSheet("font-size: 11px; font-style: italic; color: gray;")
        layout.addWidget(hint_label)

    def _get_char_count_text(self, text: str) -> str:
        """
        Get character count text.

        Args:
            text: Text to count

        Returns:
            Formatted character count string
        """
        char_count = len(text)
        word_count = len(text.split()) if text.strip() else 0
        return f"📊 {char_count} characters, {word_count} words"

    def _update_user_char_count(self) -> None:
        """Update user message character count."""
        text = self.user_input.toPlainText()
        self.user_char_count.setText(self._get_char_count_text(text))

    def _update_assistant_char_count(self) -> None:
        """Update assistant response character count."""
        text = self.assistant_input.toPlainText()
        self.assistant_char_count.setText(self._get_char_count_text(text))

    def _on_save(self) -> None:
        """Handle save button click."""
        user_text = self.user_input.toPlainText().strip()
        assistant_text = self.assistant_input.toPlainText().strip()

        # Validate
        if not user_text:
            self.user_input.setFocus()
            # Visual feedback
            self.user_input.setStyleSheet("border: 2px solid red;")
            return

        if not assistant_text:
            self.assistant_input.setFocus()
            # Visual feedback
            self.assistant_input.setStyleSheet("border: 2px solid red;")
            return

        # Save and close
        self.user_message = user_text
        self.assistant_response = assistant_text
        self.accept()

    def get_turn_data(self) -> Tuple[str, str]:
        """
        Get the edited turn data.

        Returns:
            Tuple of (user_message, assistant_response)
        """
        return (self.user_message, self.assistant_response)

    def keyPressEvent(self, event) -> None:
        """
        Handle keyboard events.

        Args:
            event: Key event
        """
        # Ctrl+Enter to save
        if event.key() == Qt.Key_Return and event.modifiers() & Qt.ControlModifier:
            self._on_save()
            event.accept()
        # Escape to cancel
        elif event.key() == Qt.Key_Escape:
            self.reject()
            event.accept()
        else:
            super().keyPressEvent(event)

    def _apply_theme(self) -> None:
        """Apply glassmorphic theme styling."""
        theme = ThemeManager.instance().current_theme

        self.setStyleSheet(f"""
            QDialog {{
                background: {theme.background_primary};
            }}
            QLabel {{
                color: {theme.text_primary};
                background: transparent;
            }}
        """)
