"""
JSON Visualizer widget for the annotation toolkit GUI (Refactored v2).

Modern implementation using JsonHighlighter, JsonTreeView, and formatting utilities.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ....adapters.file_storage import ConversationStorage
from ....config import Config
from ....core.conversation.visualizer import JsonVisualizer
from ....utils import logger
from ....utils.json.parser import parse_conversation_data, parse_json_string

from ..components import (
    GlassButton,
    JsonHighlighter,
    ConversationHighlighter,
    JsonTreeView,
)
from ..themes import ThemeManager
from ..utils.json.formatting import (
    format_json_string,
    minify_json_string,
    clean_json_string,
    detect_conversation_format,
    normalize_conversation_format,
    validate_json_syntax,
    get_json_summary,
)
from .custom_widgets import PlainTextEdit, PlainLineEdit
from .json_fixer import JsonFixer


# Configure logger
json_parser_logger = logging.getLogger("annotation_toolkit.json_parser")
json_parser_logger.setLevel(logging.DEBUG)

# Setup file handler
try:
    logs_dir = Path.home() / "annotation_toolkit_data" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    json_log_file = logs_dir / "json_parser.log"

    file_handler = logging.FileHandler(json_log_file, mode="a")
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    json_parser_logger.addHandler(file_handler)
except Exception as e:
    logger.error(f"Failed to set up JSON parser logger: {str(e)}")


class JsonVisualizerWidget(QWidget):
    """
    Modern JSON Visualizer widget with syntax highlighting and tree view.

    Features:
    - Syntax-highlighted text view
    - Hierarchical tree view
    - Format/Minify buttons
    - JSON fixer integration
    - Multiple conversation formats support
    - Search with F3/Shift+F3
    - Theme-aware styling
    """

    def __init__(self, tool: JsonVisualizer):
        """
        Initialize the JSON Visualizer widget.

        Args:
            tool: The JsonVisualizer tool instance
        """
        super().__init__()

        self.tool = tool
        self.conversation: List[Dict] = []
        self.current_format = "Text"

        # Initialize file storage
        data_dir = Path.home() / "annotation_toolkit_data"
        self.storage = ConversationStorage(data_dir)

        # Setup UI
        self._init_ui()

        # Apply theme
        self._apply_theme()

        # Connect to theme changes
        theme_manager = ThemeManager.instance()
        theme_manager.theme_changed.connect(self._apply_theme)

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # ===== TOP CONTROLS =====
        controls_layout = self._create_controls()
        layout.addLayout(controls_layout)

        # ===== INPUT SECTION =====
        input_label = QLabel("📥 Input JSON:")
        input_label.setFont(self.font())
        layout.addWidget(input_label)

        self.input_text = PlainTextEdit()
        self.input_text.setPlaceholderText(
            "Paste your JSON here...\n"
            "Supports: conversations, chat histories, generic JSON"
        )
        self.input_text.setMinimumHeight(150)
        layout.addWidget(self.input_text)

        # Input controls row
        input_controls = QHBoxLayout()
        input_controls.setSpacing(8)

        # Generate button
        self.generate_button = GlassButton("🔄 Process JSON", variant="primary", size="medium")
        self.generate_button.clicked.connect(self._generate_from_input)
        input_controls.addWidget(self.generate_button)

        # Fix JSON button
        self.fix_json_button = GlassButton("🔧 Fix JSON", variant="warning", size="medium")
        self.fix_json_button.setToolTip("Automatically repair malformed JSON")
        self.fix_json_button.clicked.connect(self._fix_json)
        input_controls.addWidget(self.fix_json_button)

        # Format button
        self.format_button = GlassButton("✨ Format", variant="ghost", size="medium")
        self.format_button.setToolTip("Pretty-print JSON with indentation")
        self.format_button.clicked.connect(self._format_input)
        input_controls.addWidget(self.format_button)

        # Minify button
        self.minify_button = GlassButton("📦 Minify", variant="ghost", size="medium")
        self.minify_button.setToolTip("Remove all whitespace")
        self.minify_button.clicked.connect(self._minify_input)
        input_controls.addWidget(self.minify_button)

        input_controls.addStretch()
        layout.addLayout(input_controls)

        # ===== OUTPUT SECTION =====
        output_header = QHBoxLayout()

        output_label = QLabel("📤 Output:")
        output_label.setFont(self.font())
        output_header.addWidget(output_label)

        output_header.addStretch()

        # Format selector
        format_label = QLabel("View:")
        output_header.addWidget(format_label)

        self.format_selector = QComboBox()
        self.format_selector.addItems(["Text", "Markdown", "JSON"])
        self.format_selector.currentTextChanged.connect(self._format_changed)
        output_header.addWidget(self.format_selector)

        # Debug logging checkbox
        self.debug_checkbox = QCheckBox("Debug Logging")
        self.debug_checkbox.setToolTip("Enable detailed JSON parsing logs")
        self.debug_checkbox.stateChanged.connect(self._toggle_debug_logging)
        output_header.addWidget(self.debug_checkbox)

        layout.addLayout(output_header)

        # Tab widget for different views
        self.view_tabs = QTabWidget()

        # Text/Markdown view tab
        self.output_display = PlainTextEdit()
        self.output_display.setReadOnly(True)

        # Add syntax highlighter
        self.text_highlighter = ConversationHighlighter(self.output_display.document())

        self.view_tabs.addTab(self.output_display, "📄 Text View")

        # Tree view tab
        self.tree_view = JsonTreeView()
        self.tree_view.item_selected.connect(self._on_tree_item_selected)
        self.view_tabs.addTab(self.tree_view, "🌳 Tree View")

        # Raw JSON tab
        self.json_display = PlainTextEdit()
        self.json_display.setReadOnly(True)
        self.json_highlighter = JsonHighlighter(self.json_display.document())
        self.view_tabs.addTab(self.json_display, "{ } Raw JSON")

        layout.addWidget(self.view_tabs)

        # ===== SEARCH SECTION =====
        search_layout = self._create_search_controls()
        layout.addLayout(search_layout)

        # ===== BOTTOM CONTROLS =====
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(8)

        # Copy button
        self.copy_button = GlassButton("📋 Copy", variant="ghost", size="small")
        self.copy_button.clicked.connect(self._copy_output)
        bottom_layout.addWidget(self.copy_button)

        # Export button
        self.export_button = GlassButton("📤 Export", variant="ghost", size="small")
        self.export_button.setToolTip("Export to Markdown or plain text")
        self.export_button.clicked.connect(self._export_output)
        bottom_layout.addWidget(self.export_button)

        # Summary label
        self.summary_label = QLabel("")
        bottom_layout.addWidget(self.summary_label)

        bottom_layout.addStretch()
        layout.addLayout(bottom_layout)

    def _create_controls(self) -> QHBoxLayout:
        """Create top control buttons."""
        controls = QHBoxLayout()
        controls.setSpacing(8)

        # Load button
        self.load_button = GlassButton("📂 Load", variant="success", size="small")
        self.load_button.clicked.connect(self._load_conversation)
        controls.addWidget(self.load_button)

        # Save button
        self.save_button = GlassButton("💾 Save", variant="primary", size="small")
        self.save_button.clicked.connect(self._save_conversation)
        controls.addWidget(self.save_button)

        controls.addStretch()
        return controls

    def _create_search_controls(self) -> QHBoxLayout:
        """Create search controls."""
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)

        # Search input
        search_label = QLabel("🔍 Search:")
        search_layout.addWidget(search_label)

        self.search_input = PlainLineEdit()
        self.search_input.setPlaceholderText("Search in output... (F3/Shift+F3 to navigate)")
        self.search_input.setMaximumWidth(300)
        self.search_input.returnPressed.connect(self._search_text)
        search_layout.addWidget(self.search_input)

        # Case sensitive checkbox
        self.case_checkbox = QCheckBox("Case sensitive")
        search_layout.addWidget(self.case_checkbox)

        # Regex checkbox
        self.regex_checkbox = QCheckBox("Regex")
        self.regex_checkbox.setToolTip("Enable regular expression search")
        search_layout.addWidget(self.regex_checkbox)

        # Previous/Next buttons
        self.prev_button = GlassButton("⬆ Prev", variant="ghost", size="small")
        self.prev_button.clicked.connect(self._previous_match)
        search_layout.addWidget(self.prev_button)

        self.next_button = GlassButton("⬇ Next", variant="ghost", size="small")
        self.next_button.clicked.connect(self._next_match)
        search_layout.addWidget(self.next_button)

        # Match counter
        self.match_label = QLabel("")
        search_layout.addWidget(self.match_label)

        search_layout.addStretch()
        return search_layout

    def _generate_from_input(self) -> None:
        """Process JSON input and display results."""
        input_text = self.input_text.toPlainText().strip()

        if not input_text:
            QMessageBox.warning(self, "Empty Input", "Please enter some JSON data.")
            return

        try:
            # Clean input
            cleaned_text = clean_json_string(input_text)

            # Validate JSON
            is_valid, error = validate_json_syntax(cleaned_text)
            if not is_valid:
                # Show error in summary with prominent styling
                self.summary_label.setStyleSheet("""
                    QLabel {
                        background-color: #ff4444;
                        color: white;
                        padding: 8px;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                """)
                self.summary_label.setText(f"❌ JSON Error: {error}")

                QMessageBox.critical(
                    self,
                    "Invalid JSON",
                    f"JSON syntax error:\n{error}\n\nTry using the 'Fix JSON' button."
                )
                return
            else:
                # Clear error styling on success
                self.summary_label.setStyleSheet("")
                self.summary_label.setText("")

            # Parse JSON
            data = json.loads(cleaned_text)

            # Detect format
            format_type = detect_conversation_format(data)
            json_parser_logger.info(f"Detected format: {format_type}")

            # Normalize to standard format if it's a conversation
            if format_type != "unknown":
                self.conversation = normalize_conversation_format(data)
            else:
                self.conversation = data if isinstance(data, list) else [data]

            # Display results
            self._display_conversation()

            # Update summary
            summary = get_json_summary(data)
            self.summary_label.setText(f"📊 {summary}")

        except Exception as e:
            json_parser_logger.error(f"Error processing JSON: {str(e)}")
            QMessageBox.critical(
                self,
                "Processing Error",
                f"Failed to process JSON:\n{str(e)}"
            )

    def _display_conversation(self) -> None:
        """Display conversation in all views."""
        if not self.conversation:
            return

        try:
            # Format for text display
            formatted = self.tool.process_json(self.conversation)

            # Update text view
            current_format = self.format_selector.currentText()
            if current_format == "Markdown":
                # Convert to markdown
                markdown = self._convert_to_markdown(self.conversation)
                self.output_display.setPlainText(markdown)
            else:
                self.output_display.setPlainText(formatted)

            # Update tree view
            self.tree_view.load_json(self.conversation)

            # Update raw JSON view
            json_str = format_json_string(self.conversation, indent=2)
            self.json_display.setPlainText(json_str)

        except Exception as e:
            logger.error(f"Error displaying conversation: {str(e)}")
            QMessageBox.critical(self, "Display Error", f"Failed to display conversation:\n{str(e)}")

    def _convert_to_markdown(self, conversation: List[Dict]) -> str:
        """Convert conversation to markdown format."""
        lines = []
        for i, turn in enumerate(conversation, 1):
            role = turn.get("role", "unknown")
            content = turn.get("content", "")

            # Add header
            lines.append(f"## Turn {i}: {role.upper()}")
            lines.append("")
            lines.append(content)
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _format_changed(self, format_text: str) -> None:
        """Handle format selector change."""
        self.current_format = format_text
        if self.conversation:
            self._display_conversation()

    def _toggle_debug_logging(self, state: int) -> None:
        """Toggle debug logging."""
        if state == Qt.Checked:
            json_parser_logger.setLevel(logging.DEBUG)
        else:
            json_parser_logger.setLevel(logging.INFO)

    def _format_input(self) -> None:
        """Format (pretty-print) the input JSON."""
        input_text = self.input_text.toPlainText().strip()
        if not input_text:
            return

        try:
            formatted = format_json_string(input_text, indent=2)
            self.input_text.setPlainText(formatted)
        except Exception as e:
            QMessageBox.warning(self, "Format Error", f"Cannot format JSON:\n{str(e)}")

    def _minify_input(self) -> None:
        """Minify the input JSON."""
        input_text = self.input_text.toPlainText().strip()
        if not input_text:
            return

        try:
            minified = minify_json_string(input_text)
            self.input_text.setPlainText(minified)
        except Exception as e:
            QMessageBox.warning(self, "Minify Error", f"Cannot minify JSON:\n{str(e)}")

    def _fix_json(self) -> None:
        """Fix malformed JSON using JsonFixer."""
        input_text = self.input_text.toPlainText().strip()
        if not input_text:
            return

        # Check if already valid
        is_valid, _ = validate_json_syntax(input_text)
        if is_valid:
            QMessageBox.information(
                self,
                "JSON Valid",
                "The JSON is already valid. No fixes needed!"
            )
            return

        try:
            # Attempt to fix
            fixer = JsonFixer()
            fixed_json = fixer.fix(input_text)

            # Validate fixed JSON
            is_valid, error = validate_json_syntax(fixed_json)
            if not is_valid:
                raise ValueError(f"Could not fix JSON: {error}")

            # Show preview
            reply = QMessageBox.question(
                self,
                "JSON Fixed",
                f"Original: {len(input_text)} chars\n"
                f"Fixed: {len(fixed_json)} chars\n\n"
                "Apply fixes?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.input_text.setPlainText(fixed_json)
                # Auto-process
                self._generate_from_input()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Fix Failed",
                f"Could not fix JSON:\n{str(e)}"
            )

    def _load_conversation(self) -> None:
        """Load conversation from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Conversation",
            str(Path.home()),
            "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.input_text.setPlainText(content)
                    self._generate_from_input()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Load Error",
                    f"Failed to load file:\n{str(e)}"
                )

    def _save_conversation(self) -> None:
        """Save conversation to file."""
        if not self.conversation:
            QMessageBox.warning(self, "No Data", "No conversation to save.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Conversation",
            str(Path.home() / "conversation.json"),
            "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.conversation, f, indent=2, ensure_ascii=False)

                QMessageBox.information(
                    self,
                    "Success",
                    f"Conversation saved to:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Save Error",
                    f"Failed to save file:\n{str(e)}"
                )

    def _copy_output(self) -> None:
        """Copy current output to clipboard."""
        current_tab = self.view_tabs.currentIndex()

        if current_tab == 0:  # Text view
            text = self.output_display.toPlainText()
        elif current_tab == 1:  # Tree view
            text = json.dumps(self.conversation, indent=2)
        else:  # JSON view
            text = self.json_display.toPlainText()

        QApplication.clipboard().setText(text)
        self.summary_label.setText("✓ Copied to clipboard!")

    def _export_output(self) -> None:
        """Export current output to file (Markdown or plain text)."""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QRadioButton, QButtonGroup, QDialogButtonBox

        # Create export dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Export Conversation")
        dialog.setModal(True)
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(16)

        # Header
        header = QLabel("📤 Choose Export Format")
        header.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(header)

        # Format options
        format_group = QButtonGroup(dialog)

        markdown_radio = QRadioButton("Markdown (.md)")
        markdown_radio.setChecked(True)
        markdown_radio.setToolTip("Export as formatted Markdown with headers and code blocks")
        format_group.addButton(markdown_radio, 0)
        layout.addWidget(markdown_radio)

        plaintext_radio = QRadioButton("Plain Text (.txt)")
        plaintext_radio.setToolTip("Export as plain text")
        format_group.addButton(plaintext_radio, 1)
        layout.addWidget(plaintext_radio)

        json_radio = QRadioButton("JSON (.json)")
        json_radio.setToolTip("Export as formatted JSON")
        format_group.addButton(json_radio, 2)
        layout.addWidget(json_radio)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # Show dialog
        if dialog.exec_() == QDialog.Accepted:
            selected_format = format_group.checkedId()

            # Get filename
            if selected_format == 0:  # Markdown
                filename, _ = QFileDialog.getSaveFileName(
                    self, "Export as Markdown", "", "Markdown Files (*.md);;All Files (*)"
                )
                if filename:
                    self._export_as_markdown(filename)
            elif selected_format == 1:  # Plain text
                filename, _ = QFileDialog.getSaveFileName(
                    self, "Export as Plain Text", "", "Text Files (*.txt);;All Files (*)"
                )
                if filename:
                    self._export_as_plaintext(filename)
            else:  # JSON
                filename, _ = QFileDialog.getSaveFileName(
                    self, "Export as JSON", "", "JSON Files (*.json);;All Files (*)"
                )
                if filename:
                    self._export_as_json(filename)

    def _export_as_markdown(self, filename: str) -> None:
        """Export conversation as Markdown."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# Conversation Export\n\n")

                if self.conversation:
                    for i, msg in enumerate(self.conversation, 1):
                        role = msg.get("role", "unknown")
                        content = msg.get("content", "")

                        if role == "user":
                            f.write(f"## 👤 User (Message {i})\n\n")
                        else:
                            f.write(f"## 🤖 Assistant (Message {i})\n\n")

                        f.write(f"{content}\n\n")
                        f.write("---\n\n")
                else:
                    f.write(self.output_display.toPlainText())

            self.summary_label.setText(f"✓ Exported to {filename}")
            logger.info(f"Exported conversation as Markdown to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export:\n{str(e)}")

    def _export_as_plaintext(self, filename: str) -> None:
        """Export conversation as plain text."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Conversation Export\n")
                f.write("=" * 50 + "\n\n")

                if self.conversation:
                    for i, msg in enumerate(self.conversation, 1):
                        role = msg.get("role", "unknown")
                        content = msg.get("content", "")

                        f.write(f"[{role.upper()}] Message {i}:\n")
                        f.write(f"{content}\n\n")
                        f.write("-" * 50 + "\n\n")
                else:
                    f.write(self.output_display.toPlainText())

            self.summary_label.setText(f"✓ Exported to {filename}")
            logger.info(f"Exported conversation as plain text to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export:\n{str(e)}")

    def _export_as_json(self, filename: str) -> None:
        """Export conversation as JSON."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                if self.conversation:
                    json.dump(self.conversation, f, indent=2, ensure_ascii=False)
                else:
                    f.write(self.json_display.toPlainText())

            self.summary_label.setText(f"✓ Exported to {filename}")
            logger.info(f"Exported conversation as JSON to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export:\n{str(e)}")

    def _search_text(self) -> None:
        """Search in output with regex support."""
        import re
        from PyQt5.QtGui import QTextCursor, QTextDocument

        search_text = self.search_input.text()
        if not search_text:
            self.match_label.setText("")
            return

        # Build search flags
        flags = QTextDocument.FindFlags()
        if self.case_checkbox.isChecked():
            flags |= QTextDocument.FindCaseSensitively

        # Search in current view
        current_tab = self.view_tabs.currentIndex()
        if current_tab == 0:  # Text view
            cursor = self.output_display.textCursor()
            cursor.movePosition(QTextCursor.Start)
            self.output_display.setTextCursor(cursor)

            if self.regex_checkbox.isChecked():
                # Regex search
                try:
                    pattern = re.compile(search_text,
                                       re.IGNORECASE if not self.case_checkbox.isChecked() else 0)
                    text = self.output_display.toPlainText()
                    matches = list(pattern.finditer(text))

                    if matches:
                        # Highlight first match
                        first_match = matches[0]
                        cursor.setPosition(first_match.start())
                        cursor.setPosition(first_match.end(), QTextCursor.KeepAnchor)
                        self.output_display.setTextCursor(cursor)
                        self.match_label.setText(f"✓ Found {len(matches)} match{'es' if len(matches) != 1 else ''}")
                    else:
                        self.match_label.setText("✗ Not found")
                except re.error as e:
                    self.match_label.setText(f"✗ Invalid regex: {str(e)}")
            else:
                # Normal search
                found = self.output_display.find(search_text, flags)
                if found:
                    # Count total matches
                    text = self.output_display.toPlainText()
                    if self.case_checkbox.isChecked():
                        count = text.count(search_text)
                    else:
                        count = text.lower().count(search_text.lower())
                    self.match_label.setText(f"✓ Found {count} match{'es' if count != 1 else ''}")
                else:
                    self.match_label.setText("✗ Not found")

    def _previous_match(self) -> None:
        """Go to previous search match."""
        from PyQt5.QtGui import QTextDocument

        search_text = self.search_input.text()
        if not search_text:
            return

        flags = QTextDocument.FindBackward
        if self.case_checkbox.isChecked():
            flags |= QTextDocument.FindCaseSensitively

        if self.regex_checkbox.isChecked():
            # For regex, we'd need more complex logic - just use normal search
            self.output_display.find(search_text, flags)
        else:
            self.output_display.find(search_text, flags)

    def _next_match(self) -> None:
        """Go to next search match."""
        from PyQt5.QtGui import QTextDocument

        search_text = self.search_input.text()
        if not search_text:
            return

        flags = QTextDocument.FindFlags()
        if self.case_checkbox.isChecked():
            flags |= QTextDocument.FindCaseSensitively

        if self.regex_checkbox.isChecked():
            # For regex, we'd need more complex logic - just use normal search
            self.output_display.find(search_text, flags)
        else:
            self.output_display.find(search_text, flags)

    def _on_tree_item_selected(self, path: str, value: Any) -> None:
        """Handle tree item selection."""
        self.summary_label.setText(f"Selected: {path}")

    def _apply_theme(self) -> None:
        """Apply glassmorphic theme styling."""
        theme = ThemeManager.instance().current_theme

        self.setStyleSheet(f"""
            JsonVisualizerWidget {{
                background: {theme.background_primary};
            }}
            QLabel {{
                color: {theme.text_primary};
            }}
            QTabWidget::pane {{
                border: 1px solid {theme.border_glass};
                border-radius: 6px;
                background: {theme.background_secondary};
            }}
            QTabBar::tab {{
                background: {theme.surface_glass};
                color: {theme.text_secondary};
                padding: 8px 16px;
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

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        # F3 for next match
        if event.key() == Qt.Key_F3:
            if event.modifiers() & Qt.ShiftModifier:
                self._previous_match()
            else:
                self._next_match()
            event.accept()
        else:
            super().keyPressEvent(event)
