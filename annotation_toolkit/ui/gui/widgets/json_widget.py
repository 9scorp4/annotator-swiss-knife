"""
JSON Visualizer widget for the annotation toolkit GUI.

This module implements the widget for the JSON Visualizer tool.
"""

import json
import logging
import re
import sys
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QIcon, QTextCursor, QTextDocument
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ....adapters.file_storage import ConversationStorage
from ....config import Config
from ....core.base import ToolExecutionError
from ....core.conversation.visualizer import JsonVisualizer
from ....utils import logger
from ....utils.json.parser import parse_conversation_data, parse_json_string

from .custom_widgets import PlainLineEdit, PlainTextEdit
from .json_fixer import JsonFixer

# Get the configuration
config = Config()

# Configure a specific logger for JSON parsing
json_parser_logger = logging.getLogger("annotation_toolkit.json_parser")
json_parser_logger.setLevel(logging.DEBUG)

# Add a file handler to save detailed logs
try:
    # Create a logs directory if it doesn't exist
    logs_dir = Path.home() / "annotation_toolkit_data" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Create a file handler for JSON parsing logs
    json_log_file = logs_dir / "json_parser.log"
    file_handler = logging.FileHandler(json_log_file, mode="a")
    file_handler.setLevel(logging.DEBUG)

    # Create a formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    # Add the handler to the logger
    json_parser_logger.addHandler(file_handler)

    json_parser_logger.info("JSON parser logger initialized")
except Exception as e:
    logger.error(f"Failed to set up JSON parser logger: {str(e)}")


class JsonVisualizerWidget(QWidget):
    """
    Widget for the JSON Visualizer tool.
    """

    def __init__(self, tool: JsonVisualizer):
        """
        Initialize the JSON Visualizer widget.

        Args:
            tool (JsonVisualizer): The JSON Visualizer tool.
        """
        super().__init__()
        self.tool = tool
        self.conversation = []

        # Search state tracking
        self.search_matches = []  # List of match indices
        self.current_match_index = -1  # Current match being displayed
        self.last_search_text = ""  # Last searched text
        self.last_case_sensitive = False  # Last case sensitivity setting

        # Initialize file storage
        data_dir = Path.home() / "annotation_toolkit_data"
        self.storage = ConversationStorage(data_dir)

        self._init_ui()

    def _init_ui(self) -> None:
        """
        Initialize the user interface.
        """
        # Main layout with better spacing and margins
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)

        # Top controls in a styled frame - theme-aware
        controls_frame = QFrame()
        controls_frame.setObjectName("controlsFrame")
        # We'll let the app-wide theme handle the background color for better dark mode compatibility

        # Add shadow to controls frame
        controls_shadow = QGraphicsDropShadowEffect()
        controls_shadow.setBlurRadius(15)
        controls_shadow.setXOffset(0)
        controls_shadow.setYOffset(2)
        controls_shadow.setColor(QColor(0, 0, 0, 30))
        controls_frame.setGraphicsEffect(controls_shadow)

        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(10, 8, 10, 8)
        controls_layout.setSpacing(10)

        # File operations group
        file_ops_layout = QHBoxLayout()
        file_ops_layout.setSpacing(8)

        # Load button with icon and modern styling
        self.load_button = QPushButton(" Load from File")
        self.load_button.setIcon(
            QIcon.fromTheme("document-open", QIcon.fromTheme("folder-open"))
        )
        self.load_button.setCursor(Qt.PointingHandCursor)
        self.load_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """
        )
        self.load_button.clicked.connect(self._load_conversation)
        file_ops_layout.addWidget(self.load_button)

        # Save button with icon and modern styling
        self.save_button = QPushButton(" Save Conversation")
        self.save_button.setIcon(QIcon.fromTheme("document-save"))
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.setStyleSheet(
            """
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:pressed {
                background-color: #0a6fc2;
            }
        """
        )
        self.save_button.clicked.connect(self._save_conversation)
        file_ops_layout.addWidget(self.save_button)

        controls_layout.addLayout(file_ops_layout)

        # Add a separator - theme-aware
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setObjectName("separator")  # Let app-wide theme handle color
        controls_layout.addWidget(separator)

        # Format selector with better styling - theme-aware
        format_label = QLabel("Format:")
        format_label.setFont(QFont("Arial", 11, QFont.Bold))
        format_label.setObjectName("fieldLabel")  # Let app-wide theme handle color
        controls_layout.addWidget(format_label)

        self.format_selector = QComboBox()
        self.format_selector.addItems(["Text", "Markdown"])
        # We'll let the app-wide theme handle the styling for better dark mode compatibility
        self.format_selector.currentTextChanged.connect(self._format_changed)
        controls_layout.addWidget(self.format_selector)

        # Debug logging checkbox - theme-aware
        self.debug_checkbox = QCheckBox("Debug Logging")
        # We'll let the app-wide theme handle the styling for better dark mode compatibility
        self.debug_checkbox.setChecked(
            config.get("tools", "json_fixer", "debug_logging", default=False)
        )
        self.debug_checkbox.stateChanged.connect(self._toggle_debug_logging)
        controls_layout.addWidget(self.debug_checkbox)

        # Search controls with better styling
        controls_layout.addStretch(1)

        search_frame = QFrame()
        search_frame.setObjectName("searchFrame")  # Let app-wide theme handle styling
        search_inner_layout = QHBoxLayout(search_frame)
        search_inner_layout.setContentsMargins(8, 2, 8, 2)
        search_inner_layout.setSpacing(5)

        search_label = QLabel("Search:")
        search_label.setFont(QFont("Arial", 11, QFont.Bold))
        search_label.setObjectName("fieldLabel")  # Let app-wide theme handle color
        search_inner_layout.addWidget(search_label)

        self.search_input = PlainLineEdit()
        self.search_input.setObjectName(
            "searchInput"
        )  # Let app-wide theme handle styling
        self.search_input.returnPressed.connect(self._search_text)
        self.search_input.textChanged.connect(self._on_search_text_changed)

        from PyQt5.QtGui import QKeySequence

        # Add keyboard shortcuts for search navigation
        from PyQt5.QtWidgets import QShortcut

        # F3 for next match
        next_shortcut = QShortcut(QKeySequence("F3"), self)
        next_shortcut.activated.connect(self._next_match)

        # Shift+F3 for previous match
        prev_shortcut = QShortcut(QKeySequence("Shift+F3"), self)
        prev_shortcut.activated.connect(self._previous_match)

        # Ctrl+F to focus search input
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(self._focus_search)

        # Escape to clear search
        escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        escape_shortcut.activated.connect(self._clear_search)
        search_inner_layout.addWidget(self.search_input)

        search_button = QPushButton("Search")
        search_button.setCursor(Qt.PointingHandCursor)
        search_button.setObjectName("searchButton")  # Let app-wide theme handle styling
        search_button.clicked.connect(self._search_text)
        search_inner_layout.addWidget(search_button)

        # Navigation buttons for multiple matches
        self.prev_button = QPushButton("◀")
        self.prev_button.setToolTip("Previous match")
        self.prev_button.setCursor(Qt.PointingHandCursor)
        self.prev_button.setEnabled(False)
        self.prev_button.setFixedSize(30, 30)
        self.prev_button.clicked.connect(self._previous_match)
        search_inner_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("▶")
        self.next_button.setToolTip("Next match")
        self.next_button.setCursor(Qt.PointingHandCursor)
        self.next_button.setEnabled(False)
        self.next_button.setFixedSize(30, 30)
        self.next_button.clicked.connect(self._next_match)
        search_inner_layout.addWidget(self.next_button)

        # Match counter label
        self.match_counter_label = QLabel("")
        self.match_counter_label.setFont(QFont("Arial", 10))
        self.match_counter_label.setObjectName("matchCounter")
        search_inner_layout.addWidget(self.match_counter_label)

        controls_layout.addWidget(search_frame)

        self.case_sensitive = QCheckBox("Case Sensitive")
        self.case_sensitive.stateChanged.connect(self._on_case_sensitive_changed)
        # We'll let the app-wide theme handle the styling for better dark mode compatibility
        controls_layout.addWidget(self.case_sensitive)

        main_layout.addWidget(controls_frame)

        # Create a splitter for the JSON input and conversation display with better styling
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(8)
        splitter.setStyleSheet(
            """
            QSplitter::handle {
                background-color: #e0e0e0;
                border-radius: 4px;
            }
            QSplitter::handle:hover {
                background-color: #2196F3;
            }
        """
        )

        # JSON input section with card-like styling - theme-aware
        json_widget = QFrame()
        json_widget.setObjectName("jsonInputFrame")
        # We'll let the app-wide theme handle the background color for better dark mode compatibility

        # Add shadow to JSON input frame
        json_shadow = QGraphicsDropShadowEffect()
        json_shadow.setBlurRadius(15)
        json_shadow.setXOffset(0)
        json_shadow.setYOffset(2)
        json_shadow.setColor(QColor(0, 0, 0, 30))
        json_widget.setGraphicsEffect(json_shadow)

        json_layout = QVBoxLayout(json_widget)
        json_layout.setContentsMargins(15, 15, 15, 15)
        json_layout.setSpacing(10)

        json_header = QHBoxLayout()
        json_label = QLabel("Paste JSON Data:")
        json_label.setFont(QFont("Arial", 14, QFont.Bold))
        json_label.setObjectName("sectionTitle")  # Let app-wide theme handle color
        json_header.addWidget(json_label)

        # Generate button with modern styling
        self.generate_button = QPushButton(" Generate Visualization")
        self.generate_button.setIcon(QIcon.fromTheme("view-refresh"))
        self.generate_button.setCursor(Qt.PointingHandCursor)
        self.generate_button.setStyleSheet(
            """
            QPushButton {
                background-color: #673AB7;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5E35B1;
            }
            QPushButton:pressed {
                background-color: #512DA8;
            }
        """
        )
        self.generate_button.clicked.connect(self._generate_from_input)
        json_header.addWidget(self.generate_button)

        json_layout.addLayout(json_header)

        # JSON input text area with better styling - theme-aware
        self.json_input = PlainTextEdit()
        self.json_input.setFont(QFont("Courier New", 11))
        # We'll let the app-wide theme handle the styling for better dark mode compatibility
        self.json_input.setPlaceholderText(
            """Paste your JSON data here.
For conversations, use format:
{
  "chat_history": [
    {"content": "Hello!", "role": "user"},
    {"content": "Hi there!", "role": "ai"}
  ]
}

OR any valid JSON data:
{
  "name": "John Doe",
  "age": 30,
  "isActive": true,
  "address": {
    "street": "123 Main St",
    "city": "Anytown"
  }
}"""
        )
        json_layout.addWidget(self.json_input)

        splitter.addWidget(json_widget)

        # Conversation display widget with card-like styling - theme-aware
        display_widget = QFrame()
        display_widget.setObjectName("displayFrame")
        # We'll let the app-wide theme handle the background color for better dark mode compatibility

        # Add shadow to display frame
        display_shadow = QGraphicsDropShadowEffect()
        display_shadow.setBlurRadius(15)
        display_shadow.setXOffset(0)
        display_shadow.setYOffset(2)
        display_shadow.setColor(QColor(0, 0, 0, 30))
        display_widget.setGraphicsEffect(display_shadow)

        display_layout = QVBoxLayout(display_widget)
        display_layout.setContentsMargins(15, 15, 15, 15)
        display_layout.setSpacing(10)

        display_label = QLabel("JSON Display:")
        display_label.setFont(QFont("Arial", 14, QFont.Bold))
        display_label.setObjectName("sectionTitle")  # Let app-wide theme handle color
        display_layout.addWidget(display_label)

        # Text display area with better styling - theme-aware
        self.text_display = PlainTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setFont(QFont("Arial", 12))
        # We'll let the app-wide theme handle the styling for better dark mode compatibility
        display_layout.addWidget(self.text_display)

        # Add copy button for display with modern styling
        copy_button = QPushButton(" Copy Formatted JSON")
        copy_button.setIcon(QIcon.fromTheme("edit-copy"))
        copy_button.setCursor(Qt.PointingHandCursor)
        copy_button.setStyleSheet(
            """
            QPushButton {
                background-color: #FF9800;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #EF6C00;
            }
        """
        )
        copy_button.clicked.connect(self._copy_conversation)
        display_layout.addWidget(copy_button)

        splitter.addWidget(display_widget)

        # Set initial sizes of the splitter
        splitter.setSizes([300, 500])

        main_layout.addWidget(splitter)

        # Status bar with modern styling - theme-aware
        status_frame = QFrame()
        status_frame.setObjectName("statusFrame")
        # We'll let the app-wide theme handle the styling for better dark mode compatibility
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(10, 5, 10, 5)

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName(
            "statusLabel"
        )  # Let app-wide theme handle color
        status_layout.addWidget(self.status_label)

        main_layout.addWidget(status_frame)

    def _format_changed(self, format_text: str) -> None:
        """
        Handle format selector change.

        Args:
            format_text (str): The selected format text.
        """
        self.tool.output_format = format_text.lower()

        # Update the display if we have a conversation
        if self.conversation:
            self._display_conversation()

    def _toggle_debug_logging(self, state: int) -> None:
        """
        Toggle debug logging for the JSON fixer.

        Args:
            state (int): The checkbox state (Qt.Checked or Qt.Unchecked).
        """
        debug_enabled = state == Qt.Checked

        # Update the configuration
        config.set(debug_enabled, "tools", "json_fixer", "debug_logging")

        # Update the logger level
        if debug_enabled:
            json_parser_logger.setLevel(logging.DEBUG)
            for handler in json_parser_logger.handlers:
                handler.setLevel(logging.DEBUG)
            self.status_label.setText("Debug logging enabled")
            json_parser_logger.debug("Debug logging enabled via UI")
        else:
            json_parser_logger.setLevel(logging.INFO)
            for handler in json_parser_logger.handlers:
                handler.setLevel(logging.INFO)
            self.status_label.setText("Debug logging disabled")
            json_parser_logger.info("Debug logging disabled via UI")

    def _display_conversation(self) -> None:
        """
        Display the conversation or JSON data.
        """
        # Clear the display
        self.text_display.clear()

        if not self.conversation:
            self.text_display.append("No JSON data to display.")
            return

        # Determine if we're dealing with conversation data or generic JSON
        is_conversation = isinstance(self.conversation, list) and all(
            isinstance(msg, dict) and "role" in msg and "content" in msg
            for msg in self.conversation
        )

        if is_conversation:
            # Format the conversation
            formatted = self.tool.format_conversation(self.conversation)

            # Set the text based on the output format
            if self.tool.output_format == "markdown":
                # For markdown, use HTML rendering to display colors
                html_content = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; }}
                        h2 {{ margin-top: 20px; margin-bottom: 5px; }}
                        div {{ margin-bottom: 15px; }}
                    </style>
                </head>
                <body>
                    {formatted}
                </body>
                </html>
                """
                self.text_display.setHtml(html_content)
            else:
                # For text format, we'll create HTML with the appropriate colors
                self._display_conversation_text_format(formatted)

            # Show status message for conversation
            self.status_label.setText(
                f"Displaying conversation with {len(self.conversation)} messages"
            )
        else:
            # Format generic JSON data
            formatted = self.tool.format_generic_json(self.conversation)

            # Set the text based on the output format
            if self.tool.output_format == "markdown":
                # For markdown, use HTML rendering
                html_content = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; }}
                        pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; }}
                        code {{ font-family: 'Courier New', monospace; }}
                        .key {{ color: #00FFFF; font-weight: bold; }}
                        .string {{ color: #00FF7F; }}
                        .number {{ color: #FF69B4; }}
                        .boolean {{ color: #FFFF00; }}
                        .null {{ color: #757575; }}
                    </style>
                </head>
                <body>
                    {formatted}
                </body>
                </html>
                """
                self.text_display.setHtml(html_content)
            else:
                # Set the plain text first
                self.text_display.setPlainText(formatted)

                # Then post-process to format XML tags if needed
                if "<" in formatted and ">" in formatted:
                    self._post_process_xml_tags()

            # Show status message for generic JSON
            if isinstance(self.conversation, dict):
                self.status_label.setText(
                    f"Displaying JSON object with {len(self.conversation)} keys"
                )
            elif isinstance(self.conversation, list):
                self.status_label.setText(
                    f"Displaying JSON array with {len(self.conversation)} items"
                )
            else:
                self.status_label.setText("Displaying JSON data")

    def _display_conversation_text_format(self, formatted: str) -> None:
        """
        Display conversation in text format with HTML styling.

        Args:
            formatted (str): The formatted conversation text.
        """
        # Get the color values from the tool
        user_color = self.tool.user_message_color or "#00FFFF"
        ai_color = self.tool.ai_message_color or "#00FF7F"

        # Split the text into lines
        lines = formatted.split("\n")

        # Create HTML content with appropriate colors and styling
        html_content = """
        <html>
        <head>
            <style>
                body {
                    font-family: monospace;
                    line-height: 1.4;
                }
                .message-header {
                    font-weight: bold;
                    padding: 5px;
                    border-radius: 4px;
                    margin-top: 10px;
                }
                .message-content {
                    margin-left: 20px;
                    padding: 8px;
                    border-radius: 4px;
                    margin-bottom: 5px;
                }
            </style>
        </head>
        <body>
        """

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check if this is a message header line
            if line.startswith("Message ") and " (USER):" in line:
                # User message header with enhanced styling
                html_content += f"<div class='message-header' style='color: {user_color}; background-color: rgba(66, 133, 244, 0.1);'>{line}</div>"

                # Add the content lines until we hit an empty line that marks the end of the message
                i += 1
                current_paragraph = []

                while i < len(lines):
                    # If we hit an empty line within the content, it's a paragraph break
                    if (
                        not lines[i]
                        and i + 1 < len(lines)
                        and lines[i + 1]
                        and not lines[i + 1].startswith("Message ")
                    ):
                        # End the current paragraph if there's content
                        if current_paragraph:
                            paragraph_text = " ".join(current_paragraph)
                            html_content += f"<p class='message-content' style='color: {user_color}; background-color: rgba(66, 133, 244, 0.05);'>{paragraph_text}</p>"
                            current_paragraph = []
                        i += 1  # Skip the empty line
                    # If we hit the end of the message
                    elif not lines[i] or lines[i].startswith("Message "):
                        # End the current paragraph if there's content
                        if current_paragraph:
                            paragraph_text = " ".join(current_paragraph)
                            html_content += f"<p class='message-content' style='color: {user_color}; background-color: rgba(66, 133, 244, 0.05);'>{paragraph_text}</p>"
                        break
                    else:
                        # Add to current paragraph
                        current_paragraph.append(lines[i])
                        i += 1

            elif line.startswith("Message ") and (
                " (ASSISTANT):" in line or " (AI):" in line
            ):
                # AI message header with enhanced styling
                html_content += f"<div class='message-header' style='color: {ai_color}; background-color: rgba(52, 168, 83, 0.1);'>{line}</div>"

                # Add the content lines until we hit an empty line that marks the end of the message
                i += 1
                current_paragraph = []

                while i < len(lines):
                    # If we hit an empty line within the content, it's a paragraph break
                    if (
                        not lines[i]
                        and i + 1 < len(lines)
                        and lines[i + 1]
                        and not lines[i + 1].startswith("Message ")
                    ):
                        # End the current paragraph if there's content
                        if current_paragraph:
                            paragraph_text = " ".join(current_paragraph)
                            html_content += f"<p class='message-content' style='color: {ai_color}; background-color: rgba(52, 168, 83, 0.05);'>{paragraph_text}</p>"
                            current_paragraph = []
                        i += 1  # Skip the empty line
                    # If we hit the end of the message
                    elif not lines[i] or lines[i].startswith("Message "):
                        # End the current paragraph if there's content
                        if current_paragraph:
                            paragraph_text = " ".join(current_paragraph)
                            html_content += f"<p class='message-content' style='color: {ai_color}; background-color: rgba(52, 168, 83, 0.05);'>{paragraph_text}</p>"
                        break
                    else:
                        # Add to current paragraph
                        current_paragraph.append(lines[i])
                        i += 1

            else:
                # Regular line
                html_content += f"<div>{line}</div>"
                i += 1

        html_content += "</body></html>"
        self.text_display.setHtml(html_content)

    def _search_text(self) -> None:
        """
        Search for text in the conversation and initialize navigation.
        """
        search_text = self.search_input.text().strip()
        if not search_text:
            self._clear_search()
            return

        if not self.conversation:
            QMessageBox.information(self, "No Data", "There is no JSON data to search.")
            return

        # Perform the search
        self._perform_search(search_text, self.case_sensitive.isChecked())

    def _perform_search(self, search_text: str, case_sensitive: bool) -> None:
        """
        Perform the actual search and update the UI.

        Args:
            search_text: The text to search for
            case_sensitive: Whether the search should be case-sensitive
        """
        # Store search parameters
        self.last_search_text = search_text
        self.last_case_sensitive = case_sensitive

        # Find all matches in the displayed text
        self.search_matches = self._find_all_matches(search_text, case_sensitive)

        if not self.search_matches:
            # No matches found
            self.current_match_index = -1
            self._update_search_ui()
            self.status_label.setText(f"No matches found for '{search_text}'")
            QMessageBox.information(
                self, "No Matches", f"No matches found for '{search_text}'"
            )
            return

        # Start with the first match
        self.current_match_index = 0
        self._update_search_ui()
        self._highlight_current_match()

        # Update status
        self.status_label.setText(
            f"Found {len(self.search_matches)} matches for '{search_text}'"
        )

    def _find_all_matches(self, search_text: str, case_sensitive: bool) -> List[int]:
        """
        Find all matches of the search text in the displayed content.

        Args:
            search_text: The text to search for
            case_sensitive: Whether the search should be case-sensitive

        Returns:
            List of character positions where matches were found
        """
        matches = []
        text_content = self.text_display.toPlainText()

        if not case_sensitive:
            search_text = search_text.lower()
            text_content = text_content.lower()

        start = 0
        while True:
            pos = text_content.find(search_text, start)
            if pos == -1:
                break
            matches.append(pos)
            start = pos + 1

        return matches

    def _highlight_current_match(self) -> None:
        """
        Highlight the current match in the text display.
        """
        if self.current_match_index < 0 or self.current_match_index >= len(
            self.search_matches
        ):
            return

        # Get the position of the current match
        match_pos = self.search_matches[self.current_match_index]

        # Create a cursor and move it to the match position
        cursor = self.text_display.textCursor()
        cursor.setPosition(match_pos)
        cursor.setPosition(
            match_pos + len(self.last_search_text), QTextCursor.KeepAnchor
        )

        # Set the cursor to select the match
        self.text_display.setTextCursor(cursor)

        # Ensure the match is visible
        self.text_display.ensureCursorVisible()

    def _update_search_ui(self) -> None:
        """
        Update the search UI elements based on current search state.
        """
        has_matches = len(self.search_matches) > 0
        has_multiple_matches = len(self.search_matches) > 1

        # Enable/disable navigation buttons
        self.prev_button.setEnabled(has_multiple_matches)
        self.next_button.setEnabled(has_multiple_matches)

        # Update match counter
        if has_matches:
            current_display = self.current_match_index + 1
            total_matches = len(self.search_matches)
            self.match_counter_label.setText(f"{current_display}/{total_matches}")
        else:
            self.match_counter_label.setText("")

    def _previous_match(self) -> None:
        """
        Navigate to the previous search match.
        """
        if not self.search_matches:
            return

        self.current_match_index = (self.current_match_index - 1) % len(
            self.search_matches
        )
        self._update_search_ui()
        self._highlight_current_match()

    def _next_match(self) -> None:
        """
        Navigate to the next search match.
        """
        if not self.search_matches:
            return

        self.current_match_index = (self.current_match_index + 1) % len(
            self.search_matches
        )
        self._update_search_ui()
        self._highlight_current_match()

    def _on_search_text_changed(self) -> None:
        """
        Handle search text changes - clear search if text is empty.
        """
        if not self.search_input.text().strip():
            self._clear_search()

    def _on_case_sensitive_changed(self) -> None:
        """
        Handle case sensitivity changes - re-search if we have search text.
        """
        search_text = self.search_input.text().strip()
        if search_text:
            self._perform_search(search_text, self.case_sensitive.isChecked())

    def _clear_search(self) -> None:
        """
        Clear the current search state.
        """
        self.search_matches = []
        self.current_match_index = -1
        self.last_search_text = ""
        self.last_case_sensitive = False
        self._update_search_ui()

        # Clear any text selection
        cursor = self.text_display.textCursor()
        cursor.clearSelection()
        self.text_display.setTextCursor(cursor)

    def _focus_search(self) -> None:
        """
        Focus the search input field and select all text.
        """
        self.search_input.setFocus()
        self.search_input.selectAll()

    def _clean_json_input(self, text: str) -> str:
        """
        Clean JSON input text to handle common formatting issues.

        Args:
            text: The input text to clean.

        Returns:
            str: Cleaned JSON text.
        """
        # Check if the input is a code block with backticks
        if text.startswith("```") and text.endswith("```"):
            # Extract content from code block
            lines = text.split("\n")
            if len(lines) > 2:  # At least 3 lines (opening, content, closing)
                # Remove first and last lines (backticks)
                text = "\n".join(lines[1:-1])
            else:
                # Just remove backticks if it's a single line
                text = text.strip("`")

        # Check if the input is wrapped in §§§ (another common format)
        elif text.startswith("§§§") and text.endswith("§§§"):
            # Extract content from between §§§ markers
            lines = text.split("\n")
            if len(lines) > 2:  # At least 3 lines (opening, content, closing)
                # Remove first and last lines (§§§)
                text = "\n".join(lines[1:-1])
            else:
                # Just remove §§§ if it's a single line
                text = text.strip("§")

        # Handle potential Unicode issues
        text = text.replace("\u2028", " ").replace("\u2029", " ")

        # Handle potential trailing commas in objects and arrays
        text = re.sub(r",\s*}", "}", text)
        text = re.sub(r",\s*]", "]", text)

        # Handle potential JavaScript-style comments
        text = re.sub(r"//.*?\n", "\n", text)
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)

        # Handle special characters that might cause issues
        text = text.replace("\u200b", "")  # Zero-width space
        text = text.replace("\ufeff", "")  # Zero-width no-break space (BOM)

        # Fix common encoding issues with Latin characters
        text = text.replace("√≠", "í")
        text = text.replace("√≥", "ó")
        text = text.replace("√°", "á")
        text = text.replace("√©", "é")
        text = text.replace("√±", "ñ")
        text = text.replace("√∫", "ú")
        text = text.replace("√º", "ü")
        text = text.replace("√Å", "Á")
        text = text.replace("√â", "É")
        text = text.replace("√ç", "Í")
        text = text.replace("√ì", "Ó")
        text = text.replace("√ö", "Ú")
        text = text.replace("√±", "ñ")
        text = text.replace("√ë", "Ñ")

        # Try to handle the case where there might be a Unicode character at the end
        # that's causing the "Extra data" error
        problematic_chars = ["›", "»", "«", """, """, "„", "‟", "‹", "❯", "❮"]
        for char in problematic_chars:
            if char in text:
                # Split at the problematic character and take only the valid part
                text = text.split(char)[0]

        return text.strip()

    def _generate_from_input(self) -> None:
        """
        Generate visualization from the JSON input.
        """
        json_text = self.json_input.toPlainText().strip()
        if not json_text:
            QMessageBox.warning(
                self, "Empty Input", "Please paste JSON data into the input field."
            )
            return

        try:
            # Use our new JSON parser module
            from ....utils.json.parser import parse_conversation_data, parse_json_string

            self.status_label.setText("Parsing JSON data...")

            try:
                # Parse the JSON string
                parsed_json = parse_json_string(json_text)
                self.status_label.setText("JSON parsed successfully")

                # Try to extract conversation data
                try:
                    self.conversation = parse_conversation_data(parsed_json)
                    self.status_label.setText(
                        f"Displaying conversation with {len(self.conversation)} messages"
                    )
                except ValueError:
                    # If not a conversation, use as generic JSON
                    self.conversation = parsed_json
                    if isinstance(parsed_json, dict):
                        self.status_label.setText(
                            f"Displaying JSON object with {len(parsed_json)} keys"
                        )
                    elif isinstance(parsed_json, list):
                        self.status_label.setText(
                            f"Displaying JSON array with {len(parsed_json)} items"
                        )
                    else:
                        self.status_label.setText("Displaying JSON data")

                # Display the JSON data
                self._display_conversation()

            except json.JSONDecodeError as e:
                # If parsing fails, show a detailed error message
                error_msg = f"Invalid JSON format: {str(e)}\n\n"

                # If we have position information, show the context around the error
                if hasattr(e, "pos") and e.pos > 0:
                    start_pos = max(0, e.pos - 20)
                    end_pos = min(len(json_text), e.pos + 20)
                    context = json_text[start_pos:end_pos]
                    error_msg += f"Error near: ...{context}..."

                QMessageBox.critical(self, "JSON Error", error_msg)
                self.status_label.setText(f"JSON Error: {str(e)}")

        except ToolExecutionError as e:
            QMessageBox.critical(self, "Error", str(e))
            self.status_label.setText(f"Tool Error: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error processing input: {str(e)}")
            self.status_label.setText(f"Processing Error: {str(e)}")

    def _handle_special_json_cases(self, text: str) -> str:
        """
        Handle special JSON cases that might cause parsing issues.

        Args:
            text: The input text to process.

        Returns:
            str: Processed JSON text.
        """
        original_text = text
        json_parser_logger.debug(
            f"Starting _handle_special_json_cases with text: {text[:100]}..."
        )

        # Check if the text ends with a non-JSON character
        # This is a common issue when copying JSON from various sources
        match = re.search(r'(.*})\s*[^\s{}[\],:"\'0-9a-zA-Z_-]*$', text)
        if match:
            text = match.group(1)
            json_parser_logger.debug("Removed trailing non-JSON characters")

        # Check for unescaped control characters
        for i in range(32):
            if i not in (9, 10, 13):  # Tab, LF, CR are allowed
                text = text.replace(chr(i), "")

        # Log the text before fixing quotes
        json_parser_logger.debug(
            f"Text after removing control characters: {text[:100]}..."
        )

        # Fix the specific error with missing comma - this is the most specific pattern
        if '"content":"You are Meta AI""' in text:
            json_parser_logger.info(
                'Found specific pattern: content":"You are Meta AI""'
            )
            text = text.replace(
                '"content":"You are Meta AI""', '"content":"You are Meta AI",'
            )
            json_parser_logger.debug("Fixed missing comma after 'You are Meta AI'")

        # More general pattern for missing commas between quoted values
        text = re.sub(r'("(?:[^"\\]|\\.)*")("(?:[^"\\]|\\.)*":)', r"\1,\2", text)

        # Fix missing quotes around string values
        # Look for patterns like "content":You are Meta AI and add quotes
        # This pattern is more aggressive and will catch more cases
        text = re.sub(
            r'"([^"]+)":\s*([^"{}\[\],\s][^{}\[\],]*?)(?=,|\}|\]|$)', r'"\1":"\2"', text
        )
        json_parser_logger.debug("Applied general pattern for missing quotes")

        # Add a more specific pattern for the exact error we're seeing
        text = re.sub(
            r'"content":You are Meta AI"', r'"content":"You are Meta AI"', text
        )

        # Fix the specific error with missing comma
        text = re.sub(
            r'"content":"You are Meta AI""', r'"content":"You are Meta AI","', text
        )

        # Fix another variant of the missing comma issue
        text = re.sub(
            r'"content":"You are Meta AI"([^,])',
            r'"content":"You are Meta AI",\1',
            text,
        )

        # Fix the specific error pattern that's causing the issue
        if '"content":"You are Meta AI""' in text:
            # Log the exact pattern we found
            json_parser_logger.info(
                'Found problematic pattern: content":"You are Meta AI""'
            )
            # Replace with the correct version (with comma)
            text = text.replace(
                '"content":"You are Meta AI""', '"content":"You are Meta AI",'
            )
            json_parser_logger.info("Fixed missing comma after 'You are Meta AI'")

        # More general pattern to catch any field with unquoted values
        text = re.sub(
            r'"([^"]+)":\s*([A-Za-z][^,}\]]*?)(?=,|\}|\]|$)', r'"\1":"\2"', text
        )

        # Specific pattern for content field with unquoted values
        text = re.sub(
            r'"content":([^"{}\[\],\s][^,}\]]*?)(?=,|\}|\]|$)', r'"content":"\1"', text
        )

        # Fix issues with missing commas between fields
        text = re.sub(r'""([^"]+)":', r'",""\1":', text)

        # Fix missing commas between fields (more general pattern)
        text = re.sub(r'"([^"]+)"\s*"([^"]+)":', r'"\1","\2":', text)

        # Log the text after fixing quotes
        json_parser_logger.debug(
            f"Text after fixing quotes and commas: {text[:100]}..."
        )

        # Handle potential issues with XML tags in JSON strings
        # Escape any < and > characters that might be causing issues
        # But only if they're not already part of a properly escaped string
        def escape_xml_tags(match):
            content = match.group(1)
            # Don't escape already escaped tags
            if "\\<" in content or "\\>" in content:
                return match.group(0)
            # Escape < and > in the content
            content = content.replace("<", "\\u003C").replace(">", "\\u003E")
            return f'"{content}"'

        # Replace content in string literals
        text = re.sub(
            r'"([^"\\]*(?:\\.[^"\\]*)*)"', escape_xml_tags, text, flags=re.DOTALL
        )

        # Handle problematic characters at the end of the JSON
        problematic_chars = ["›", "»", "«", """, """, "„", "‟", "‹", "❯", "❮"]
        for char in problematic_chars:
            if text.endswith(char):
                text = text[:-1]
                json_parser_logger.debug(
                    f"Removed problematic character at end: {char}"
                )

        # Try to fix common JSON syntax errors
        # Remove trailing commas in objects and arrays
        text = re.sub(r",\s*}", "}", text)
        text = re.sub(r",\s*]", "]", text)

        # Handle potential issues with Unicode characters
        text = "".join(c for c in text if ord(c) >= 32 or c in "\n\r\t")

        # Special case for the specific pattern that's causing issues
        # Look for patterns like "urje su venta $$9000" and escape the dollar signs
        text = re.sub(r"(\w+\s+\w+\s+)\$\$(\d+)", r"\1\\$\\$\2", text)

        # Handle special characters that might cause parsing issues
        # Escape dollar signs that aren't already escaped
        text = text.replace("$$", "\\$\\$")

        # Handle other special characters that might cause issues
        special_chars = ["$", "\\\\", "'"]
        for char in special_chars:
            # Only escape if not already escaped
            if char == "\\\\":
                # Special handling for backslash which needs extra escaping
                text = re.sub(r"(?<!\\)\\(?!\\)", r"\\\\", text)
            else:
                # For other characters
                text = re.sub(f"(?<!\\\\){re.escape(char)}", f"\\\\{char}", text)

        # Fix specific issue with unterminated strings
        # Look for strings that might be missing closing quotes
        text = re.sub(r'"([^"\\]*(?:\\.[^"\\]*)*)$', r'\1"', text)

        # Log if changes were made
        if text != original_text:
            json_parser_logger.info("Text was modified by _handle_special_json_cases")
            # Log a sample of the changes
            if len(original_text) > 200:
                json_parser_logger.debug(
                    f"Original sample: {original_text[:100]}...{original_text[-100:]}"
                )
                json_parser_logger.debug(
                    f"Modified sample: {text[:100]}...{text[-100:]}"
                )
            else:
                json_parser_logger.debug(f"Original: {original_text}")
                json_parser_logger.debug(f"Modified: {text}")

        return text

    def _load_conversation(self) -> None:
        """
        Load conversation from a file.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open JSON File", "", "JSON Files (*.json);;All Files (*)"
        )

        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            # Update the JSON input field with file content
            self.json_input.setText(file_content)

            # Generate visualization from loaded file
            self._generate_from_input()

            self.status_label.setText(f"Loaded JSON data from {Path(file_path).name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load file: {str(e)}")
            self.status_label.setText(f"Error loading JSON data: {str(e)}")

    def _save_conversation(self) -> None:
        """
        Save conversation to a file.
        """
        if not self.conversation:
            QMessageBox.warning(self, "No Data", "There is no JSON data to save.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save JSON File", "", "JSON Files (*.json);;All Files (*)"
        )

        if not file_path:
            return

        try:
            # Save the JSON data
            with open(file_path, "w", encoding="utf-8") as f:
                # If it's a conversation, wrap it in chat_history
                if isinstance(self.conversation, list) and all(
                    isinstance(msg, dict) for msg in self.conversation
                ):
                    json.dump(
                        {"chat_history": self.conversation},
                        f,
                        indent=2,
                        ensure_ascii=False,
                    )
                else:
                    # Otherwise save as is
                    json.dump(
                        self.conversation,
                        f,
                        indent=2,
                        ensure_ascii=False,
                    )

            QMessageBox.information(
                self, "Saved", f"JSON data saved to {Path(file_path).name}"
            )
            self.status_label.setText(f"Saved JSON data to {Path(file_path).name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
            self.status_label.setText(f"Error saving conversation: {str(e)}")

    def _process_json_with_xml_tags(self, json_text: str) -> str:
        """
        Process JSON text to properly display XML tags in the format:
        <TAG>
                {{content}}
        </TAG>

        Args:
            json_text: The JSON text to process.

        Returns:
            str: Processed text with properly formatted XML tags.
        """
        try:
            # First, unescape the JSON string to get the actual content
            processed_text = json_text

            # Replace escaped quotes with actual quotes
            processed_text = processed_text.replace('\\"', '"')

            # Replace escaped newlines with actual newlines
            processed_text = processed_text.replace("\\n", "\n")

            # Use a manual approach to find and format XML tags
            # This is more robust than regex for complex nested structures
            result = []
            i = 0
            while i < len(processed_text):
                # Look for opening tag
                open_tag_start = processed_text.find("<", i)
                if open_tag_start == -1:
                    # No more tags, add the rest of the text
                    result.append(processed_text[i:])
                    break

                # Add text before the tag
                result.append(processed_text[i:open_tag_start])

                # Find the end of the opening tag
                open_tag_end = processed_text.find(">", open_tag_start)
                if open_tag_end == -1:
                    # Malformed tag, just add it as is
                    result.append(processed_text[open_tag_start:])
                    break

                # Extract the tag name
                tag_name = processed_text[open_tag_start + 1 : open_tag_end]

                # Look for the closing tag
                close_tag_start = processed_text.find(f"</{tag_name}>", open_tag_end)
                if close_tag_start == -1:
                    # No closing tag, just add the opening tag as is
                    result.append(processed_text[open_tag_start : open_tag_end + 1])
                    i = open_tag_end + 1
                    continue

                # Extract the content between tags
                content = processed_text[open_tag_end + 1 : close_tag_start]

                # Format with explicit newlines and indentation
                formatted_tag = f"<{tag_name}>\n        {content}\n</{tag_name}>"
                result.append(formatted_tag)

                # Move past the closing tag
                i = close_tag_start + len(f"</{tag_name}>")

            return "".join(result)

        except Exception as e:
            # If there's an error, log it and return the original text
            print(f"Error processing XML tags: {str(e)}")
            return json_text

    def _post_process_xml_tags(self) -> None:
        """
        Post-process the text display to format XML tags in the desired format:
        <TAG>
                {{content}}
        </TAG>

        This method directly modifies the text in the display widget.
        """
        # Get the current text from the display
        current_text = self.text_display.toPlainText()

        # Create a new string with formatted XML tags
        formatted_text = ""
        i = 0

        # Process the text character by character to find and format XML tags
        while i < len(current_text):
            # Look for opening tag
            open_tag_start = current_text.find("<", i)
            if open_tag_start == -1:
                # No more tags, add the rest of the text
                formatted_text += current_text[i:]
                break

            # Add text before the tag
            formatted_text += current_text[i:open_tag_start]

            # Find the end of the opening tag
            open_tag_end = current_text.find(">", open_tag_start)
            if open_tag_end == -1:
                # Malformed tag, just add it as is
                formatted_text += current_text[open_tag_start:]
                break

            # Extract the tag name
            tag_name = current_text[open_tag_start + 1 : open_tag_end]

            # Skip if this doesn't look like a valid XML tag name
            if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", tag_name):
                formatted_text += current_text[open_tag_start : open_tag_end + 1]
                i = open_tag_end + 1
                continue

            # Look for the closing tag - use a regex to handle multi-line content
            pattern = f"</{re.escape(tag_name)}>"
            match = re.search(pattern, current_text[open_tag_end:], re.DOTALL)

            if not match:
                # No closing tag, just add the opening tag as is
                formatted_text += current_text[open_tag_start : open_tag_end + 1]
                i = open_tag_end + 1
                continue

            # Calculate the position of the closing tag
            close_tag_start = open_tag_end + match.start()
            close_tag_end = open_tag_end + match.end()

            # Extract the content between tags
            content = current_text[open_tag_end + 1 : close_tag_start]

            # Format with explicit newlines and indentation (11 spaces)
            formatted_text += f"<{tag_name}>\n           {content}\n</{tag_name}>"

            # Move past the closing tag
            i = close_tag_end

        # Update the text display with the formatted text
        if formatted_text != current_text:
            self.text_display.setPlainText(formatted_text)

            # Force a repaint to ensure the changes are visible
            self.text_display.repaint()

    def _copy_conversation(self) -> None:
        """
        Copy the conversation display to the clipboard.
        """
        if not self.text_display.toPlainText():
            QMessageBox.warning(self, "No Content", "There is no JSON data to copy.")
            return

        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_display.toPlainText())

        QMessageBox.information(self, "Copied", "Formatted JSON copied to clipboard!")
