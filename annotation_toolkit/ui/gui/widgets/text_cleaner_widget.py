"""
Text Cleaner widget for the annotation toolkit GUI.

This module implements the widget for the Text Cleaner tool.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QButtonGroup,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ....core.base import ToolExecutionError
from ....core.text.text_cleaner import TextCleaner
from ....utils import logger
from ..components.text_widgets import PlainTextEdit
from ..theme import (
    ColorPalette,
    Spacing,
    BorderRadius,
    get_success_button_style,
    get_primary_button_style,
    get_warning_button_style,
)
from ..themes import ThemeManager
from ..utils.fonts import FontManager


class TextCleanerWidget(QWidget):
    """
    Widget for the Text Cleaner tool.
    """

    def __init__(self, tool: TextCleaner):
        """
        Initialize the Text Cleaner widget.

        Args:
            tool (TextCleaner): The Text Cleaner tool.
        """
        super().__init__()
        self.tool = tool
        self.original_text = ""
        self.cleaned_text = ""

        # Initialize theme manager
        self.theme_manager = ThemeManager.instance()

        self._init_ui()

        # Apply initial theme
        self._apply_theme()

        # Connect to theme changes
        self.theme_manager.theme_changed.connect(self._apply_theme)

    def _init_ui(self) -> None:
        """
        Initialize the user interface.
        """
        # Main layout with better spacing and margins
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)

        # Create a splitter for input and output panes with better styling
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(8)
        # Styling will be applied by _apply_theme()

        # Input section with card-like styling - theme-aware
        input_widget = QFrame()
        input_widget.setObjectName("inputFrame")
        # We'll let the app-wide theme handle the background color for better dark mode compatibility

        # Add shadow to input frame
        input_shadow = QGraphicsDropShadowEffect()
        input_shadow.setBlurRadius(15)
        input_shadow.setXOffset(0)
        input_shadow.setYOffset(2)
        input_shadow.setColor(QColor(0, 0, 0, 30))
        input_widget.setGraphicsEffect(input_shadow)

        input_layout = QVBoxLayout(input_widget)
        input_layout.setContentsMargins(15, 15, 15, 15)
        input_layout.setSpacing(10)

        input_label = QLabel("Input Text (with markdown/JSON/code artifacts):")
        input_label.setFont(FontManager.get_font(size=FontManager.SIZE_BASE, bold=True))
        input_label.setObjectName("sectionTitle")  # Let app-wide theme handle color

        self.input_text = PlainTextEdit()
        self.input_text.setFont(FontManager.get_code_font())
        # We'll let the app-wide theme handle the styling for better dark mode compatibility
        self.input_text.setPlaceholderText(
            "Enter text here. You can use markdown, JSON, and code artifacts.\n\nExample:\n\n`This is a sample text\n\nwith artifacts.\n*This text is in bold.*\n\nThis is a newline:\n\nThis is a code block:\n```\nimport pandas as pd\nimport numpy as np```"
        )

        # Button container with better styling - theme-aware
        button_frame = QFrame()
        button_frame.setObjectName("buttonFrame")
        # We'll let the app-wide theme handle the background color for better dark mode compatibility
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(10, 8, 10, 8)
        button_layout.setSpacing(10)

        # Load button with icon and modern styling
        load_btn = QPushButton(" Load From File")
        load_btn.setIcon(
            QIcon.fromTheme("document-open", QIcon.fromTheme("folder-open"))
        )
        load_btn.setCursor(Qt.PointingHandCursor)
        load_btn.setStyleSheet(
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
        load_btn.clicked.connect(self._load_from_file)
        button_layout.addWidget(load_btn)

        # Sample data button with icon and modern styling
        sample_btn = QPushButton(" Load Sample Data")
        sample_btn.setIcon(QIcon.fromTheme("document-new"))
        sample_btn.setCursor(Qt.PointingHandCursor)
        sample_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #FF9800;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
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
        sample_btn.clicked.connect(self._load_sample_data)
        button_layout.addWidget(sample_btn)

        # Clean button with icon and modern styling
        clean_btn = QPushButton(" Clean Text")
        clean_btn.setIcon(QIcon.fromTheme("edit-clear"))
        clean_btn.setCursor(Qt.PointingHandCursor)
        clean_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #673AB7;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #5E35B1;
            }
            QPushButton:pressed {
                background-color: #512DA8;
            }
        """
        )
        clean_btn.clicked.connect(self._clean_text)
        button_layout.addWidget(clean_btn)

        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_text)
        input_layout.addWidget(button_frame)

        # Output section with card-like styling - theme-aware
        output_widget = QFrame()
        output_widget.setObjectName("outputFrame")
        # We'll let the app-wide theme handle the background color for better dark mode compatibility

        # Add shadow to output frame
        output_shadow = QGraphicsDropShadowEffect()
        output_shadow.setBlurRadius(15)
        output_shadow.setXOffset(0)
        output_shadow.setYOffset(2)
        output_shadow.setColor(QColor(0, 0, 0, 30))
        output_widget.setGraphicsEffect(output_shadow)

        output_layout = QVBoxLayout(output_widget)
        output_layout.setContentsMargins(15, 15, 15, 15)
        output_layout.setSpacing(10)

        # Cleaned text section with better styling
        cleaned_label = QLabel("Cleaned Text (editable):")
        cleaned_label.setFont(FontManager.get_font(size=FontManager.SIZE_BASE, bold=True))
        cleaned_label.setObjectName("sectionTitle")  # Let app-wide theme handle color

        self.cleaned_text_edit = PlainTextEdit()
        self.cleaned_text_edit.setFont(FontManager.get_font())
        # We'll let the app-wide theme handle the styling for better dark mode compatibility
        self.cleaned_text_edit.setPlaceholderText(
            "Cleaned text will appear here. You can edit it before transforming back."
        )

        # Generate output button with icon and modern styling
        generate_btn = QPushButton(" Generate Output (Code Format)")
        generate_btn.setIcon(QIcon.fromTheme("document-export"))
        generate_btn.setCursor(Qt.PointingHandCursor)
        generate_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """
        )
        generate_btn.setMinimumHeight(45)
        generate_btn.clicked.connect(self._transform_back)

        # Transformed output section with better styling
        transformed_label = QLabel("Transformed Output:")
        transformed_label.setFont(FontManager.get_font(size=FontManager.SIZE_BASE, bold=True))
        transformed_label.setObjectName(
            "sectionTitle"
        )  # Let app-wide theme handle color

        self.transformed_text = PlainTextEdit()
        self.transformed_text.setReadOnly(True)
        self.transformed_text.setFont(FontManager.get_code_font())
        # We'll let the app-wide theme handle the styling for better dark mode compatibility
        self.transformed_text.setPlaceholderText("Transformed text will appear here")

        # Button container for transformed text with better styling - theme-aware
        transformed_button_frame = QFrame()
        transformed_button_frame.setObjectName("transformedButtonFrame")
        # We'll let the app-wide theme handle the background color for better dark mode compatibility
        transformed_button_layout = QHBoxLayout(transformed_button_frame)
        transformed_button_layout.setContentsMargins(10, 8, 10, 8)
        transformed_button_layout.setSpacing(10)

        # Copy button with icon and modern styling
        copy_btn = QPushButton(" Copy Transformed Text")
        copy_btn.setIcon(QIcon.fromTheme("edit-copy"))
        copy_btn.setCursor(Qt.PointingHandCursor)
        copy_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #607D8B;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #546E7A;
            }
            QPushButton:pressed {
                background-color: #455A64;
            }
        """
        )
        copy_btn.clicked.connect(self._copy_transformed)
        transformed_button_layout.addWidget(copy_btn)

        # Save button with icon and modern styling
        save_btn = QPushButton(" Save Transformed Text")
        save_btn.setIcon(QIcon.fromTheme("document-save"))
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #009688;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00897B;
            }
            QPushButton:pressed {
                background-color: #00796B;
            }
        """
        )
        save_btn.clicked.connect(self._save_transformed)
        transformed_button_layout.addWidget(save_btn)

        # Add all components to output layout
        output_layout.addWidget(cleaned_label)
        output_layout.addWidget(self.cleaned_text_edit, 40)  # 40% of height
        output_layout.addWidget(generate_btn)
        output_layout.addWidget(transformed_label)
        output_layout.addWidget(self.transformed_text, 40)  # 40% of height
        output_layout.addWidget(transformed_button_frame)

        # Add widgets to splitter
        self.splitter.addWidget(input_widget)
        self.splitter.addWidget(output_widget)

        # Add splitter to main layout
        main_layout.addWidget(self.splitter)

    def _load_sample_data(self) -> None:
        """
        Load sample data into the input text area.
        """
        sample_text = "`This is a sample text\\n\\nwith artifacts.\\n*This text is in bold.*\\n\\nThis is a newline:\\n\\nThis is a code block:\\n```\\nimport pandas as pd\\nimport numpy as np`"
        self.input_text.setText(sample_text)

    def _load_from_file(self) -> None:
        """
        Load text data from a file.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Text File",
            "",
            "Text Files (*.txt);;JSON Files (*.json);;Markdown Files (*.md);;All Files (*)",
        )

        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = f.read()

            self.input_text.setText(data)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load file: {str(e)}")

    def _clean_text(self) -> None:
        """
        Clean the input text from markdown/JSON/code artifacts.
        """
        try:
            # Get input text
            input_text = self.input_text.toPlainText()

            if not input_text.strip():
                QMessageBox.warning(
                    self, "Empty Input", "Please enter some text to clean."
                )
                return

            # Store the original text
            self.original_text = input_text

            # Clean the text
            self.cleaned_text = self.tool.clean_text(input_text)

            # Update the cleaned text area
            self.cleaned_text_edit.setText(self.cleaned_text)

            # Clear the transformed text area
            self.transformed_text.clear()

        except ToolExecutionError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"An unexpected error occurred: {str(e)}"
            )

    def _transform_back(self) -> None:
        """
        Transform the cleaned text back to code format.
        """
        try:
            # Get the cleaned text (possibly edited by the user)
            cleaned_text = self.cleaned_text_edit.toPlainText()

            if not cleaned_text.strip():
                QMessageBox.warning(
                    self, "Empty Input", "Please clean some text first."
                )
                return

            # Always use code format
            format_type = "code"
            logger.debug(f"Using format: {format_type}")

            # Transform the text
            transformed = self.tool.transform_back(cleaned_text, format_type)

            logger.debug(f"Transformed text length: {len(transformed)}")

            # Update the transformed text area
            self.transformed_text.setText(transformed)

            # Ensure the text is visible
            self.transformed_text.repaint()

        except ToolExecutionError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"An unexpected error occurred: {str(e)}"
            )

    def _copy_transformed(self) -> None:
        """
        Copy the transformed text to the clipboard.
        """
        transformed_text = self.transformed_text.toPlainText()

        if not transformed_text:
            QMessageBox.warning(
                self, "No Content", "There is no transformed text to copy."
            )
            return

        clipboard = QApplication.clipboard()
        clipboard.setText(transformed_text)

        # Show a temporary message
        QMessageBox.information(self, "Copied", "Transformed text copied to clipboard!")

    def _save_transformed(self) -> None:
        """
        Save the transformed text to a file.
        """
        transformed_text = self.transformed_text.toPlainText()

        if not transformed_text:
            QMessageBox.warning(
                self, "No Content", "There is no transformed text to save."
            )
            return

        # Always use code format
        format_type = "code"
        file_extension = ".txt"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Transformed Text",
            f"transformed{file_extension}",
            f"Text Files (*{file_extension});;All Files (*)",
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(transformed_text)

            QMessageBox.information(
                self, "Saved", f"Transformed text saved to {file_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")

    def _apply_theme(self) -> None:
        """Apply current theme to splitter."""
        theme = self.theme_manager.current_theme

        # Apply splitter styling
        self.splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {theme.border_glass};
                border-radius: 4px;
            }}
            QSplitter::handle:hover {{
                background-color: {theme.accent_primary};
            }}
        """)
