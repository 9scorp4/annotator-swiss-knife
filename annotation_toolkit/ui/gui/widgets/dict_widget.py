"""
Dictionary to Bullet List widget for the annotation toolkit GUI.

This module implements the widget for the Dictionary to Bullet List tool.
"""

import json
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ....adapters.file_storage import DictionaryStorage
from ....core.base import ToolExecutionError
from ....core.text.dict_to_bullet import DictToBulletList
from ..components.text_widgets import PlainTextEdit
from ..theme import (
    ColorPalette,
    Spacing,
    BorderRadius,
    get_success_button_style,
    get_warning_button_style,
    get_primary_button_style,
)
from ..themes import ThemeManager, StylesheetGenerator


class DictToBulletWidget(QWidget):
    """
    Widget for the Dictionary to Bullet List tool.
    """

    def __init__(self, tool: DictToBulletList):
        """
        Initialize the Dictionary to Bullet List widget.

        Args:
            tool (DictToBulletList): The Dictionary to Bullet List tool.
        """
        super().__init__()
        self.tool = tool
        self.urls = {}  # Store URLs for list items

        # Initialize theme manager
        self.theme_manager = ThemeManager.instance()

        # Initialize file storage
        data_dir = Path.home() / "annotation_toolkit_data"
        self.storage = DictionaryStorage(data_dir)

        self._init_ui()

        # Apply initial theme
        self._apply_theme()

        # Connect to theme changes
        self.theme_manager.theme_changed.connect(self._apply_theme)

    def _init_ui(self) -> None:
        """
        Initialize the user interface.
        """
        # Main layout with compact spacing to maximize central area
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(10)

        # Create a splitter for input and output panes with modern styling
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(10)
        # Styling will be applied by _apply_theme()

        # Input section with modern styling
        self.input_widget = QFrame()
        self.input_widget.setObjectName("jsonInputFrame")
        # Styling will be applied by _apply_theme()

        # Add shadow to input frame
        input_shadow = QGraphicsDropShadowEffect()
        input_shadow.setBlurRadius(20)
        input_shadow.setXOffset(0)
        input_shadow.setYOffset(3)
        input_shadow.setColor(QColor(0, 0, 0, 40))
        self.input_widget.setGraphicsEffect(input_shadow)

        input_layout = QVBoxLayout(self.input_widget)
        input_layout.setContentsMargins(14, 14, 14, 14)
        input_layout.setSpacing(12)

        self.input_label = QLabel("Input Dictionary (JSON format):")
        self.input_label.setFont(QFont("Arial", 15, QFont.Bold))
        self.input_label.setObjectName("sectionLabel")
        # Styling will be applied by _apply_theme()

        self.input_text = PlainTextEdit()
        self.input_text.setFont(QFont("Courier New", 12))
        self.input_text.setPlaceholderText(
            'Paste your dictionary here in JSON format, e.g.:\n{\n    "1": "https://www.example.com/page1",\n    "2": "https://www.example.com/page2"\n}'
        )

        # Button container with modern styling
        button_frame = QFrame()
        button_frame.setObjectName("buttonFrame")
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 8, 0, 0)
        button_layout.setSpacing(10)

        # Load button with modern styling
        load_btn = QPushButton(" Load From File")
        load_btn.setIcon(QIcon.fromTheme("document-open", QIcon.fromTheme("folder-open")))
        load_btn.setCursor(Qt.PointingHandCursor)
        load_btn.setFixedHeight(38)
        load_btn.setStyleSheet(get_success_button_style())
        load_btn.clicked.connect(self._load_from_file)
        button_layout.addWidget(load_btn)

        # Sample data button with modern styling
        sample_btn = QPushButton(" Load Sample Data")
        sample_btn.setIcon(QIcon.fromTheme("document-new"))
        sample_btn.setCursor(Qt.PointingHandCursor)
        sample_btn.setFixedHeight(38)
        sample_btn.setStyleSheet(get_warning_button_style())
        sample_btn.clicked.connect(self._load_sample_data)
        button_layout.addWidget(sample_btn)

        # Convert button with modern styling
        convert_btn = QPushButton(" Convert to Bullet List")
        convert_btn.setIcon(QIcon.fromTheme("view-list-bullet"))
        convert_btn.setCursor(Qt.PointingHandCursor)
        convert_btn.setFixedHeight(38)
        convert_btn.setStyleSheet(get_primary_button_style())
        convert_btn.clicked.connect(self._convert)
        button_layout.addWidget(convert_btn)

        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_text)
        input_layout.addWidget(button_frame)

        # Output section with modern styling
        self.output_widget = QFrame()
        self.output_widget.setObjectName("displayFrame")
        # Styling will be applied by _apply_theme()

        # Add shadow to output frame
        output_shadow = QGraphicsDropShadowEffect()
        output_shadow.setBlurRadius(20)
        output_shadow.setXOffset(0)
        output_shadow.setYOffset(3)
        output_shadow.setColor(QColor(0, 0, 0, 40))
        self.output_widget.setGraphicsEffect(output_shadow)

        output_layout = QVBoxLayout(self.output_widget)
        output_layout.setContentsMargins(14, 14, 14, 14)
        output_layout.setSpacing(12)

        # Clickable list section with modern styling
        self.clickable_label = QLabel("Clickable Links (double-click to open):")
        self.clickable_label.setFont(QFont("Arial", 15, QFont.Bold))
        self.clickable_label.setObjectName("sectionLabel")
        # Styling will be applied by _apply_theme()

        # Use QListWidget for clickable items with better styling - theme-aware
        self.link_list = QListWidget()
        self.link_list.setFont(QFont("Arial", 11))
        # We'll let the app-wide theme handle the styling for better dark mode compatibility
        self.link_list.setCursor(Qt.PointingHandCursor)
        self.link_list.itemDoubleClicked.connect(self._open_url)

        # Markdown output section with better styling - theme-aware
        markdown_section = QFrame()
        markdown_section.setObjectName("markdownSection")
        # We'll let the app-wide theme handle the background color for better dark mode compatibility
        markdown_layout = QHBoxLayout(markdown_section)
        markdown_layout.setContentsMargins(10, 10, 10, 10)
        markdown_layout.setSpacing(10)

        # Main markdown content area with better styling - theme-aware
        markdown_container = QFrame()
        markdown_container.setObjectName("markdownContainer")
        # We'll let the app-wide theme handle the background color for better dark mode compatibility
        markdown_content_layout = QVBoxLayout(markdown_container)
        markdown_content_layout.setContentsMargins(10, 10, 10, 10)
        markdown_content_layout.setSpacing(8)

        self.markdown_label = QLabel("Markdown Output:")
        self.markdown_label.setFont(QFont("Arial", 13, QFont.Bold))
        self.markdown_label.setObjectName("subsectionLabel")
        # Styling will be applied by _apply_theme()

        self.output_text = PlainTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Courier New", 12))
        # We'll let the app-wide theme handle the styling for better dark mode compatibility

        markdown_content_layout.addWidget(self.markdown_label)
        markdown_content_layout.addWidget(self.output_text)

        # Markdown button area with better styling
        markdown_button_container = QFrame()
        markdown_button_container.setObjectName("markdownButtonContainer")
        markdown_button_layout = QVBoxLayout(markdown_button_container)
        markdown_button_layout.setContentsMargins(5, 5, 5, 5)
        markdown_button_layout.setSpacing(10)
        markdown_button_layout.addStretch()

        # Copy markdown button with modern styling
        copy_md_btn = QPushButton(" Copy\nMarkdown")
        copy_md_btn.setIcon(QIcon.fromTheme("edit-copy"))
        copy_md_btn.setCursor(Qt.PointingHandCursor)
        copy_md_btn.setMinimumHeight(50)
        copy_md_btn.setStyleSheet(get_primary_button_style())
        copy_md_btn.clicked.connect(self._copy_markdown)

        # Save markdown button with modern styling
        save_md_btn = QPushButton(" Save\nMarkdown")
        save_md_btn.setIcon(QIcon.fromTheme("document-save"))
        save_md_btn.setCursor(Qt.PointingHandCursor)
        save_md_btn.setMinimumHeight(50)
        save_md_btn.setStyleSheet(get_success_button_style())
        save_md_btn.clicked.connect(self._save_markdown)

        markdown_button_layout.addWidget(copy_md_btn)
        markdown_button_layout.addWidget(save_md_btn)
        markdown_button_layout.addStretch()

        # Add to markdown section
        markdown_layout.addWidget(markdown_container, 85)  # 85% of width
        markdown_layout.addWidget(markdown_button_container, 15)  # 15% of width

        output_layout.addWidget(self.clickable_label)
        output_layout.addWidget(self.link_list, 50)  # 50% of height
        output_layout.addWidget(markdown_section, 50)  # 50% of height

        # Add widgets to splitter
        self.splitter.addWidget(self.input_widget)
        self.splitter.addWidget(self.output_widget)

        # Add splitter to main layout with stretch factor to fill available space
        main_layout.addWidget(self.splitter, 1)

    def _load_sample_data(self) -> None:
        """
        Load sample data into the input text area.
        """
        sample_dict = {
            "1": "https://www.example.com/page1",
            "2": "https://www.example.com/page2",
            "3": "https://www.example.com/page3",
            "4": "https://www.example.com/page4",
            "5": "https://www.example.com/page5",
            "6": "https://www.example.com/page6",
            "7": "https://www.example.com/page7",
        }
        self.input_text.setText(json.dumps(sample_dict, indent=4))

    def _load_from_file(self) -> None:
        """
        Load dictionary data from a file.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Dictionary File", "", "JSON Files (*.json);;All Files (*)"
        )

        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.input_text.setText(json.dumps(data, indent=4))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load file: {str(e)}")

    def _copy_markdown(self) -> None:
        """
        Copy the markdown output to the clipboard.
        """
        clipboard = QApplication.clipboard()
        clipboard.setText(self.output_text.toPlainText())

        # Show a temporary message
        QMessageBox.information(self, "Copied", "Markdown copied to clipboard!")

    def _save_markdown(self) -> None:
        """
        Save the markdown output to a file.
        """
        if not self.output_text.toPlainText():
            QMessageBox.warning(
                self, "No Content", "There is no markdown content to save."
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Markdown File",
            "",
            "Markdown Files (*.md);;Text Files (*.txt);;All Files (*)",
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.output_text.toPlainText())

            QMessageBox.information(self, "Saved", f"Markdown saved to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")

    def _open_url(self, item: QListWidgetItem) -> None:
        """
        Open the URL associated with the clicked list item.

        Args:
            item (QListWidgetItem): The clicked list item.
        """
        index = self.link_list.row(item)
        if index in self.urls:
            url = self.urls[index]
            try:
                webbrowser.open(url)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not open URL: {str(e)}")

    def _convert(self) -> None:
        """
        Convert the input dictionary to a bullet list.
        """
        try:
            # Get input text
            input_json = self.input_text.toPlainText()

            if not input_json.strip():
                QMessageBox.warning(self, "Empty Input", "Please enter some JSON data.")
                return

            # Parse JSON
            input_dict = json.loads(input_json)

            # Ensure it's a dictionary
            if not isinstance(input_dict, dict):
                QMessageBox.warning(
                    self, "Invalid Input", "Input must be a JSON object (dictionary)."
                )
                return

            # Convert to bullet list
            bullet_list = self.tool.process_text(input_json)

            # Get clickable items
            items = self.tool.process_dict_to_items(input_dict)

            # Update the output
            self.output_text.setText(bullet_list)

            # Update the clickable list
            self.link_list.clear()
            self.urls = {}

            for index, (title, url) in enumerate(items):
                item = QListWidgetItem(f"• {title}")
                self.link_list.addItem(item)
                self.urls[index] = url

            # Save dictionary to storage
            try:
                self.storage.save_dictionary(input_dict)
            except Exception as e:
                # Just log this error, don't show to user since it's not critical
                print(f"Error saving dictionary: {str(e)}")

        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Invalid JSON", f"Could not parse JSON: {str(e)}")
        except ToolExecutionError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"An unexpected error occurred: {str(e)}"
            )

    def _apply_theme(self) -> None:
        """Apply current theme to all widgets."""
        theme = self.theme_manager.current_theme

        # Apply splitter styling
        self.splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {theme.border_glass};
                border-radius: 5px;
                margin: 2px 0px;
            }}
            QSplitter::handle:hover {{
                background-color: {theme.accent_primary};
            }}
        """)

        # Apply input widget styling
        self.input_widget.setStyleSheet(f"""
            #jsonInputFrame {{
                background: {theme.surface_glass};
                border: 1px solid {theme.border_glass};
                border-radius: 16px;
                padding: 20px;
            }}
        """)

        # Apply output widget styling
        self.output_widget.setStyleSheet(f"""
            #displayFrame {{
                background: {theme.surface_glass};
                border: 1px solid {theme.border_glass};
                border-radius: 16px;
                padding: 20px;
            }}
        """)

        # Apply label styling
        for label in [self.input_label, self.clickable_label]:
            label.setStyleSheet(f"""
                QLabel {{
                    color: {theme.text_primary};
                    padding: 8px 0px;
                    border-bottom: 2px solid {theme.accent_primary};
                    background: transparent;
                }}
            """)

        # Apply subsection label styling
        self.markdown_label.setStyleSheet(f"""
            QLabel {{
                color: {theme.text_primary};
                padding: 4px 0px;
                background: transparent;
            }}
        """)
