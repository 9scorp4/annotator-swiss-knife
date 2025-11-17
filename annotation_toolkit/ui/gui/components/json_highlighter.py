"""
JsonHighlighter component - Syntax highlighter for JSON text.

Provides theme-aware syntax highlighting for JSON with proper color coding.
"""

from typing import Optional
import re

from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import (
    QSyntaxHighlighter,
    QTextCharFormat,
    QColor,
    QFont,
    QTextDocument,
)

from ..themes import ThemeManager


class JsonHighlighter(QSyntaxHighlighter):
    """
    Syntax highlighter for JSON documents.

    Highlights:
    - Keys (property names in quotes before colons)
    - String values
    - Numbers (integers and floats)
    - Booleans (true, false)
    - Null values
    - Brackets and braces
    - Commas and colons

    Colors are theme-aware and update when theme changes.
    """

    def __init__(self, document: Optional[QTextDocument] = None):
        """
        Initialize the JSON syntax highlighter.

        Args:
            document: QTextDocument to apply highlighting to
        """
        super().__init__(document)

        # Formatting rules
        self.highlighting_rules = []

        # Connect to theme changes
        theme_manager = ThemeManager.instance()
        theme_manager.theme_changed.connect(self._update_theme)

        # Initialize formats with current theme
        self._update_theme()

    def _update_theme(self) -> None:
        """Update highlighting formats based on current theme."""
        theme = ThemeManager.instance().current_theme

        # Define colors based on theme
        if theme.is_dark:
            # Dark theme colors - vibrant but readable
            self.color_key = "#79c0ff"  # Light blue for keys
            self.color_string = "#a5d6a7"  # Light green for strings
            self.color_number = "#f8b26a"  # Orange for numbers
            self.color_boolean = "#ea9a97"  # Pink for booleans
            self.color_null = "#b392f0"  # Purple for null
            self.color_bracket = "#8b949e"  # Gray for brackets
            self.color_punctuation = "#6e7681"  # Darker gray for punctuation
        else:
            # Light theme colors - darker for contrast
            self.color_key = "#0550ae"  # Dark blue for keys
            self.color_string = "#0a3069"  # Dark blue-gray for strings
            self.color_number = "#953800"  # Dark orange for numbers
            self.color_boolean = "#8250df"  # Purple for booleans
            self.color_null = "#8250df"  # Purple for null
            self.color_bracket = "#24292f"  # Black for brackets
            self.color_punctuation = "#57606a"  # Gray for punctuation

        # Clear existing rules
        self.highlighting_rules.clear()

        # Create formats
        self._create_formats()

    def _create_formats(self) -> None:
        """Create text formats and highlighting rules."""
        # Key format (property names: "key":)
        key_format = QTextCharFormat()
        key_format.setForeground(QColor(self.color_key))
        key_format.setFontWeight(QFont.Bold)
        # Match quoted strings followed by colon
        self.highlighting_rules.append(
            (QRegExp(r'"[^"\\]*(\\.[^"\\]*)*"\s*:'), key_format)
        )

        # String value format
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(self.color_string))
        # Match quoted strings NOT followed by colon
        self.highlighting_rules.append(
            (QRegExp(r':\s*"[^"\\]*(\\.[^"\\]*)*"'), string_format)
        )
        # Also match strings in arrays
        self.highlighting_rules.append(
            (QRegExp(r'\[\s*"[^"\\]*(\\.[^"\\]*)*"'), string_format)
        )
        self.highlighting_rules.append(
            (QRegExp(r',\s*"[^"\\]*(\\.[^"\\]*)*"'), string_format)
        )

        # Number format (integers and floats, including negative and scientific notation)
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(self.color_number))
        self.highlighting_rules.append(
            (QRegExp(r'\b-?\d+\.?\d*([eE][+-]?\d+)?\b'), number_format)
        )

        # Boolean format (true, false)
        boolean_format = QTextCharFormat()
        boolean_format.setForeground(QColor(self.color_boolean))
        boolean_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((QRegExp(r'\btrue\b'), boolean_format))
        self.highlighting_rules.append((QRegExp(r'\bfalse\b'), boolean_format))

        # Null format
        null_format = QTextCharFormat()
        null_format.setForeground(QColor(self.color_null))
        null_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((QRegExp(r'\bnull\b'), null_format))

        # Brackets and braces
        bracket_format = QTextCharFormat()
        bracket_format.setForeground(QColor(self.color_bracket))
        bracket_format.setFontWeight(QFont.Bold)
        for char in ['\\{', '\\}', '\\[', '\\]']:
            self.highlighting_rules.append((QRegExp(char), bracket_format))

        # Punctuation (commas, colons)
        punctuation_format = QTextCharFormat()
        punctuation_format.setForeground(QColor(self.color_punctuation))
        self.highlighting_rules.append((QRegExp(r'[,:]'), punctuation_format))

    def highlightBlock(self, text: str) -> None:
        """
        Apply syntax highlighting to a block of text.

        Args:
            text: Text block to highlight
        """
        # Apply each highlighting rule
        for pattern, format in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)

            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)


class ConversationHighlighter(QSyntaxHighlighter):
    """
    Specialized syntax highlighter for conversation JSON.

    Highlights role names (user, assistant, system) and conversation structure
    in addition to standard JSON syntax.
    """

    def __init__(self, document: Optional[QTextDocument] = None):
        """
        Initialize the conversation syntax highlighter.

        Args:
            document: QTextDocument to apply highlighting to
        """
        super().__init__(document)

        # Formatting rules
        self.highlighting_rules = []

        # Connect to theme changes
        theme_manager = ThemeManager.instance()
        theme_manager.theme_changed.connect(self._update_theme)

        # Initialize formats with current theme
        self._update_theme()

    def _update_theme(self) -> None:
        """Update highlighting formats based on current theme."""
        theme = ThemeManager.instance().current_theme

        # Define colors based on theme
        if theme.is_dark:
            # Dark theme colors
            self.color_role_user = "#79c0ff"  # Light blue
            self.color_role_assistant = "#a5d6a7"  # Light green
            self.color_role_system = "#f8b26a"  # Orange
            self.color_content = "#c9d1d9"  # Light gray
            self.color_key = "#8b949e"  # Gray
        else:
            # Light theme colors
            self.color_role_user = "#0550ae"  # Dark blue
            self.color_role_assistant = "#1a7f37"  # Dark green
            self.color_role_system = "#953800"  # Dark orange
            self.color_content = "#24292f"  # Black
            self.color_key = "#57606a"  # Gray

        # Clear existing rules
        self.highlighting_rules.clear()

        # Create formats
        self._create_formats()

    def _create_formats(self) -> None:
        """Create text formats and highlighting rules."""
        # Role: user
        user_format = QTextCharFormat()
        user_format.setForeground(QColor(self.color_role_user))
        user_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append(
            (QRegExp(r'"role"\s*:\s*"user"'), user_format)
        )

        # Role: assistant
        assistant_format = QTextCharFormat()
        assistant_format.setForeground(QColor(self.color_role_assistant))
        assistant_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append(
            (QRegExp(r'"role"\s*:\s*"assistant"'), assistant_format)
        )

        # Role: system
        system_format = QTextCharFormat()
        system_format.setForeground(QColor(self.color_role_system))
        system_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append(
            (QRegExp(r'"role"\s*:\s*"system"'), system_format)
        )

        # Content key
        content_key_format = QTextCharFormat()
        content_key_format.setForeground(QColor(self.color_key))
        content_key_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append(
            (QRegExp(r'"content"\s*:'), content_key_format)
        )

        # Apply base JSON highlighting as well
        base_highlighter = JsonHighlighter()
        base_highlighter._update_theme()
        self.highlighting_rules.extend(base_highlighter.highlighting_rules)

    def highlightBlock(self, text: str) -> None:
        """
        Apply syntax highlighting to a block of text.

        Args:
            text: Text block to highlight
        """
        # Apply each highlighting rule
        for pattern, format in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)

            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)
