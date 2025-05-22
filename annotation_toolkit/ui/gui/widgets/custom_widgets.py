"""
Custom widgets for the annotation toolkit GUI.

This module provides custom widget implementations that extend the standard PyQt widgets.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLineEdit, QTextEdit


class PlainLineEdit(QLineEdit):
    """
    A custom QLineEdit that handles pasted text properly.

    This class fixes an issue where pasted text would stack to the left,
    leaving the rest of the field blank.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the PlainLineEdit widget."""
        super().__init__(*args, **kwargs)

        # Set a monospace font for better text display
        self.setFont(QFont("Courier New", 10))

    def keyPressEvent(self, event):
        """
        Handle key press events.

        This overrides the default keyPressEvent to ensure proper text handling.

        Args:
            event: The key press event.
        """
        # Handle paste events specially
        if event.matches(Qt.KeySequence.Paste):
            # Get the clipboard text
            clipboard = self.createMimeDataFromSelection()
            text = clipboard.text()

            # Insert the text at the current cursor position
            self.insert(text)
        else:
            # For all other key events, use the default handler
            super().keyPressEvent(event)


class PlainTextEdit(QTextEdit):
    """
    A custom QTextEdit that provides plain text editing capabilities.

    This class extends QTextEdit to provide a simpler interface for plain text editing.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the PlainTextEdit widget."""
        super().__init__(*args, **kwargs)

        # Set a monospace font for better code display
        self.setFont(QFont("Courier New", 10))

        # Set to plain text mode
        self.setAcceptRichText(False)
