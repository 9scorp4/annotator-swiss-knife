"""
Dictionary to Bullet List widget for the annotation toolkit GUI.

This module implements the widget for the Dictionary to Bullet List tool.
"""

import json
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
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
from .custom_widgets import PlainTextEdit


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

        # Initialize file storage
        data_dir = Path.home() / "annotation_toolkit_data"
        self.storage = DictionaryStorage(data_dir)

        self._init_ui()

    def _init_ui(self) -> None:
        """
        Initialize the user interface.
        """
        # Main layout
        main_layout = QVBoxLayout(self)

        # Create a splitter for input and output panes
        splitter = QSplitter(Qt.Horizontal)

        # Input section
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)

        input_label = QLabel("Input Dictionary (JSON format):")
        input_label.setFont(QFont("Arial", 12))
        self.input_text = PlainTextEdit()
        self.input_text.setPlaceholderText(
            'Paste your dictionary here in JSON format, e.g.:\n{\n    "1": "https://www.example.com/page1",\n    "2": "https://www.example.com/page2"\n}'
        )

        # Button container
        button_layout = QHBoxLayout()

        # Load button
        load_btn = QPushButton("Load From File")
        load_btn.clicked.connect(self._load_from_file)
        button_layout.addWidget(load_btn)

        # Sample data button
        sample_btn = QPushButton("Load Sample Data")
        sample_btn.clicked.connect(self._load_sample_data)
        button_layout.addWidget(sample_btn)

        # Convert button
        convert_btn = QPushButton("Convert to Bullet List")
        convert_btn.clicked.connect(self._convert)
        convert_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; font-weight: bold;"
        )
        button_layout.addWidget(convert_btn)

        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_text)
        input_layout.addLayout(button_layout)

        # Output section
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)

        # Clickable list section
        clickable_label = QLabel("Clickable Links (double-click to open):")
        clickable_label.setFont(QFont("Arial", 12))

        # Use QListWidget for clickable items
        self.link_list = QListWidget()
        self.link_list.setFont(QFont("Arial", 10))
        self.link_list.itemDoubleClicked.connect(self._open_url)

        # Markdown output section (combined with copy button)
        markdown_section = QWidget()
        markdown_layout = QHBoxLayout(markdown_section)

        # Main markdown content area
        markdown_container = QWidget()
        markdown_content_layout = QVBoxLayout(markdown_container)

        markdown_label = QLabel("Markdown Output:")
        markdown_label.setFont(QFont("Arial", 12))
        self.output_text = PlainTextEdit()
        self.output_text.setReadOnly(True)

        markdown_content_layout.addWidget(markdown_label)
        markdown_content_layout.addWidget(self.output_text)

        # Markdown button area
        markdown_button_container = QWidget()
        markdown_button_layout = QVBoxLayout(markdown_button_container)
        markdown_button_layout.addStretch()

        # Copy markdown button
        copy_md_btn = QPushButton("Copy\nMarkdown")
        copy_md_btn.clicked.connect(self._copy_markdown)
        copy_md_btn.setMinimumHeight(50)

        # Save markdown button
        save_md_btn = QPushButton("Save\nMarkdown")
        save_md_btn.clicked.connect(self._save_markdown)
        save_md_btn.setMinimumHeight(50)

        markdown_button_layout.addWidget(copy_md_btn)
        markdown_button_layout.addWidget(save_md_btn)
        markdown_button_layout.addStretch()

        # Add to markdown section
        markdown_layout.addWidget(markdown_container, 85)  # 85% of width
        markdown_layout.addWidget(markdown_button_container, 15)  # 15% of width

        output_layout.addWidget(clickable_label)
        output_layout.addWidget(self.link_list, 50)  # 50% of height
        output_layout.addWidget(markdown_section, 50)  # 50% of height

        # Add widgets to splitter
        splitter.addWidget(input_widget)
        splitter.addWidget(output_widget)

        # Add splitter to main layout
        main_layout.addWidget(splitter)

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
