"""
Custom widgets for the annotation toolkit GUI.

This module provides custom widget implementations that extend the standard PyQt widgets
with enhanced styling, better user experience, and modern visual effects.
"""

from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QPalette, QKeySequence
from PyQt5.QtWidgets import QApplication, QLineEdit, QTextEdit


class PlainLineEdit(QLineEdit):
    """
    A custom QLineEdit that handles pasted text properly with enhanced styling.

    This class fixes an issue where pasted text would stack to the left,
    leaving the rest of the field blank. It also provides better visual feedback
    and modern styling.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the PlainLineEdit widget."""
        super().__init__(*args, **kwargs)

        # Set a modern monospace font for better text display
        self.setFont(QFont("SF Mono", 11) if self._is_mac() else QFont("Consolas", 11))

        # Set minimum height for better visual presence
        self.setMinimumHeight(35)

        # Add padding and modern styling
        self.setStyleSheet(
            """
            QLineEdit {
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 13px;
                line-height: 1.4;
            }
        """
        )

    def _is_mac(self):
        """Check if running on macOS."""
        import platform

        return platform.system() == "Darwin"

    def keyPressEvent(self, event):
        """
        Handle key press events with improved paste handling.

        This overrides the default keyPressEvent to ensure proper text handling.

        Args:
            event: The key press event.
        """
        # Handle paste events specially
        if event.matches(QKeySequence.Paste):
            # Get the clipboard text
            clipboard = QApplication.clipboard()
            text = clipboard.text()

            # Insert the text at the current cursor position
            self.insert(text)
        else:
            # For all other key events, use the default handler
            super().keyPressEvent(event)

    def focusInEvent(self, event):
        """Handle focus in event with visual feedback."""
        super().focusInEvent(event)
        # Add subtle animation or visual feedback here if needed

    def focusOutEvent(self, event):
        """Handle focus out event."""
        super().focusOutEvent(event)


class PlainTextEdit(QTextEdit):
    """
    A custom QTextEdit that provides enhanced plain text editing capabilities.

    This class extends QTextEdit to provide a simpler interface for plain text editing
    with modern styling, better typography, and improved user experience.
    """

    # Signal emitted when text changes with a delay (for performance)
    textChangedDelayed = pyqtSignal()

    def __init__(self, *args, **kwargs):
        """Initialize the PlainTextEdit widget."""
        super().__init__(*args, **kwargs)

        # Set a modern monospace font for better code display
        self.setFont(QFont("SF Mono", 12) if self._is_mac() else QFont("Consolas", 12))

        # Set to plain text mode
        self.setAcceptRichText(False)

        # Set minimum height for better visual presence
        self.setMinimumHeight(150)

        # Enable word wrap for better text flow
        self.setLineWrapMode(QTextEdit.WidgetWidth)

        # Set up delayed text change signal for performance
        self._text_change_timer = QTimer()
        self._text_change_timer.setSingleShot(True)
        self._text_change_timer.timeout.connect(self.textChangedDelayed.emit)
        self.textChanged.connect(self._on_text_changed)

        # Add modern styling with better typography
        self.setStyleSheet(
            """
            QTextEdit {
                font-size: 13px;
                line-height: 1.5;
                padding: 12px;
                border-radius: 8px;
            }
        """
        )

        # Set tab stop width for better code formatting
        self.setTabStopWidth(40)  # 4 spaces equivalent

    def _is_mac(self):
        """Check if running on macOS."""
        import platform

        return platform.system() == "Darwin"

    def _on_text_changed(self):
        """Handle text change with delay for performance."""
        self._text_change_timer.stop()
        self._text_change_timer.start(300)  # 300ms delay

    def insertFromMimeData(self, source):
        """
        Handle paste operations with better text processing.

        Args:
            source: The mime data source.
        """
        # Get the text from the mime data
        text = source.text()

        # Process the text to handle common formatting issues
        text = self._process_pasted_text(text)

        # Insert the processed text
        cursor = self.textCursor()
        cursor.insertText(text)

    def _process_pasted_text(self, text):
        """
        Process pasted text to handle common formatting issues.

        Args:
            text (str): The text to process.

        Returns:
            str: The processed text.
        """
        # Remove carriage returns that can cause display issues
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Handle smart quotes and other special characters
        replacements = {
            '"': '"',  # Left double quotation mark
            '"': '"',  # Right double quotation mark
            """: "'",  # Left single quotation mark
            """: "'",  # Right single quotation mark
            "–": "-",  # En dash
            "—": "--",  # Em dash
            "…": "...",  # Horizontal ellipsis
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        return text

    def keyPressEvent(self, event):
        """
        Handle key press events with enhanced functionality.

        Args:
            event: The key press event.
        """
        # Handle Tab key for proper indentation
        if event.key() == Qt.Key_Tab:
            cursor = self.textCursor()
            cursor.insertText("    ")  # Insert 4 spaces
            return

        # Handle Shift+Tab for unindentation
        if event.key() == Qt.Key_Backtab:
            cursor = self.textCursor()
            cursor.select(cursor.LineUnderCursor)
            line = cursor.selectedText()
            if line.startswith("    "):
                cursor.insertText(line[4:])
            elif line.startswith("\t"):
                cursor.insertText(line[1:])
            return

        # Handle Ctrl+A (Select All) properly
        if event.matches(QKeySequence.SelectAll):
            self.selectAll()
            return

        # Default handling for other keys
        super().keyPressEvent(event)

    def focusInEvent(self, event):
        """Handle focus in event with visual feedback."""
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        """Handle focus out event."""
        super().focusOutEvent(event)

    def wheelEvent(self, event):
        """
        Handle wheel events for better scrolling with Ctrl+Wheel zoom.

        Args:
            event: The wheel event.
        """
        # Handle Ctrl+Wheel for font size adjustment
        if event.modifiers() == Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self._increase_font_size()
            else:
                self._decrease_font_size()
            event.accept()
            return

        # Default wheel handling
        super().wheelEvent(event)

    def _increase_font_size(self):
        """Increase the font size."""
        font = self.font()
        size = font.pointSize()
        if size < 24:  # Maximum font size
            font.setPointSize(size + 1)
            self.setFont(font)

    def _decrease_font_size(self):
        """Decrease the font size."""
        font = self.font()
        size = font.pointSize()
        if size > 8:  # Minimum font size
            font.setPointSize(size - 1)
            self.setFont(font)

    def setPlaceholderText(self, text):
        """
        Set placeholder text with better formatting.

        Args:
            text (str): The placeholder text.
        """
        # Store the placeholder text
        self._placeholder_text = text

        # If the widget is empty, show the placeholder
        if not self.toPlainText():
            self._show_placeholder()

    def _show_placeholder(self):
        """Show the placeholder text."""
        if hasattr(self, "_placeholder_text"):
            # Set the placeholder text with a lighter color
            self.setPlainText(self._placeholder_text)

            # Make the text appear as placeholder (lighter)
            palette = self.palette()
            palette.setColor(QPalette.Text, QColor(128, 128, 128))
            self.setPalette(palette)

            # Mark as showing placeholder
            self._showing_placeholder = True

    def _hide_placeholder(self):
        """Hide the placeholder text."""
        if hasattr(self, "_showing_placeholder") and self._showing_placeholder:
            self.clear()

            # Restore normal text color
            palette = self.palette()
            palette.setColor(QPalette.Text, self.palette().color(QPalette.WindowText))
            self.setPalette(palette)

            self._showing_placeholder = False

    def focusInEvent(self, event):
        """Handle focus in event to hide placeholder."""
        self._hide_placeholder()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        """Handle focus out event to show placeholder if empty."""
        if not self.toPlainText():
            self._show_placeholder()
        super().focusOutEvent(event)
