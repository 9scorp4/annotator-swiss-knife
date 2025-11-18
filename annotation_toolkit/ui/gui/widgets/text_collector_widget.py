"""
Text Collector widget for the annotation toolkit GUI.

This module implements the widget for the Text Collector tool.
"""

import json
from pathlib import Path
from typing import List, Dict

from PyQt5.QtCore import Qt, QMimeData, QPoint
from PyQt5.QtGui import QColor, QFont, QIcon, QDrag
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
    QInputDialog,
    QFileDialog,
)

from ....core.text.text_collector import TextCollector
from ....utils import logger
from ..components.text_widgets import PlainTextEdit
from ..components.draggable_field import DraggableFieldFrame
from ..themes import ThemeManager, StylesheetGenerator
from ..components import GlassButton


class TextCollectorWidget(QWidget):
    """
    Widget for the Text Collector tool.
    """

    def __init__(self, tool: TextCollector):
        """
        Initialize the Text Collector widget.

        Args:
            tool (TextCollector): The Text Collector tool.
        """
        super().__init__()
        self.tool = tool
        self.text_fields = []  # List to store text field widgets

        # Initialize theme
        self.theme_manager = ThemeManager.instance()
        self.generator = StylesheetGenerator(self.theme_manager.current_theme)

        # Initialize templates directory
        self.templates_dir = Path.home() / "annotation_toolkit_data" / "text_collector_templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        self._init_ui()

        # Add initial fields (start with 3)
        for _ in range(3):
            self._add_field()

        # Apply theme and connect to theme changes
        self._apply_theme()
        self.theme_manager.theme_changed.connect(self._on_theme_changed)

    def _init_ui(self) -> None:
        """
        Initialize the user interface.
        """
        # Main layout with compact spacing to maximize central area
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 10)  # Reduced margins
        main_layout.setSpacing(10)  # Reduced spacing

        # Top controls in a styled frame
        controls_frame = QFrame()
        controls_frame.setObjectName("controlsFrame")
        self.controls_frame = controls_frame  # Store reference for theme application

        # Add shadow to controls frame
        controls_shadow = QGraphicsDropShadowEffect()
        controls_shadow.setBlurRadius(20)
        controls_shadow.setXOffset(0)
        controls_shadow.setYOffset(3)
        controls_shadow.setColor(QColor(0, 0, 0, 40))
        controls_frame.setGraphicsEffect(controls_shadow)

        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(10, 6, 10, 6)  # Reduced padding
        controls_layout.setSpacing(10)

        # Field counter with better typography
        self.field_counter_label = QLabel(f"Fields: 0/{self.tool.max_fields}")
        self.field_counter_label.setFont(QFont("Arial", 13, QFont.Bold))
        controls_layout.addWidget(self.field_counter_label)

        controls_layout.addStretch(1)

        # Add field button
        self.add_field_button = GlassButton("✚ Add Field", variant="success", size="medium")
        self.add_field_button.clicked.connect(self._add_field)
        controls_layout.addWidget(self.add_field_button)

        # Bulk import button
        self.bulk_import_button = GlassButton("📥 Bulk Import", variant="primary", size="medium")
        self.bulk_import_button.clicked.connect(self._bulk_import)
        controls_layout.addWidget(self.bulk_import_button)

        # Template buttons
        self.save_template_button = GlassButton("💾 Save Template", variant="ghost", size="medium")
        self.save_template_button.clicked.connect(self._save_template)
        controls_layout.addWidget(self.save_template_button)

        self.load_template_button = GlassButton("📂 Load Template", variant="ghost", size="medium")
        self.load_template_button.clicked.connect(self._load_template)
        controls_layout.addWidget(self.load_template_button)

        # Clear all button
        self.clear_button = GlassButton("🗑 Clear All", variant="danger", size="medium")
        self.clear_button.clicked.connect(self._clear_all)
        controls_layout.addWidget(self.clear_button)

        # Add controls frame with no stretch - takes minimum height only
        main_layout.addWidget(controls_frame, 0)

        # Create a splitter for input and output sections
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(10)
        self.splitter = splitter  # Store reference for theme application

        # Left side: Input section
        input_widget = self._create_input_section()
        splitter.addWidget(input_widget)

        # Right side: Output section
        output_widget = self._create_output_section()
        splitter.addWidget(output_widget)

        # Set initial sizes
        splitter.setSizes([500, 500])

        # Add splitter with stretch factor to fill available vertical space
        main_layout.addWidget(splitter, 1)

        # Status bar with compact spacing (no stretch factor - takes minimum space)
        status_frame = QFrame()
        status_frame.setObjectName("statusFrame")
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(10, 3, 10, 3)  # Reduced padding

        self.status_label = QLabel("Ready to collect text")
        self.status_label.setObjectName("statusLabel")
        status_layout.addWidget(self.status_label)

        main_layout.addWidget(status_frame, 0)  # No stretch - minimum height only

    def _create_input_section(self) -> QWidget:
        """
        Create the input section for text fields.

        Returns:
            QWidget: The input section widget.
        """
        input_widget = QFrame()
        input_widget.setObjectName("jsonInputFrame")
        self.input_widget = input_widget  # Store reference for theme application

        # Add shadow
        input_shadow = QGraphicsDropShadowEffect()
        input_shadow.setBlurRadius(20)
        input_shadow.setXOffset(0)
        input_shadow.setYOffset(3)
        input_shadow.setColor(QColor(0, 0, 0, 40))
        input_widget.setGraphicsEffect(input_shadow)

        input_layout = QVBoxLayout(input_widget)
        input_layout.setContentsMargins(14, 14, 14, 14)  # Reduced padding
        input_layout.setSpacing(12)

        # Header with better styling
        header_label = QLabel("Text Fields")
        header_label.setFont(QFont("Arial", 15, QFont.Bold))
        self.input_header_label = header_label  # Store reference for theme application
        input_layout.addWidget(header_label)

        # Scrollable area for text fields
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area = scroll_area  # Store reference for theme application

        # Container for text fields
        self.fields_container = QWidget()
        self.fields_layout = QVBoxLayout(self.fields_container)
        self.fields_layout.setContentsMargins(0, 0, 0, 0)
        self.fields_layout.setSpacing(12)
        self.fields_layout.addStretch()

        scroll_area.setWidget(self.fields_container)
        input_layout.addWidget(scroll_area)

        return input_widget

    def _create_output_section(self) -> QWidget:
        """
        Create the output section for displaying JSON.

        Returns:
            QWidget: The output section widget.
        """
        output_widget = QFrame()
        output_widget.setObjectName("displayFrame")
        self.output_widget = output_widget  # Store reference for theme application

        # Add shadow
        output_shadow = QGraphicsDropShadowEffect()
        output_shadow.setBlurRadius(20)
        output_shadow.setXOffset(0)
        output_shadow.setYOffset(3)
        output_shadow.setColor(QColor(0, 0, 0, 40))
        output_widget.setGraphicsEffect(output_shadow)

        output_layout = QVBoxLayout(output_widget)
        output_layout.setContentsMargins(14, 14, 14, 14)  # Reduced padding
        output_layout.setSpacing(12)

        # Header with better styling
        header_label = QLabel("Generated JSON:")
        header_label.setFont(QFont("Arial", 15, QFont.Bold))
        # Styling applied in _apply_static_theme()
        output_layout.addWidget(header_label)

        # JSON display with modern styling
        self.json_display = PlainTextEdit()
        self.json_display.setReadOnly(True)
        self.json_display.setFont(QFont("Courier New", 12))
        self.json_display.setPlaceholderText(
            "Add text to fields and click 'Generate JSON' to see output here..."
        )
        # Styling applied in _apply_static_theme()
        output_layout.addWidget(self.json_display)

        # Button row with modern styling
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        # Generate JSON button
        self.generate_button = GlassButton("⚡ Generate JSON", variant="primary", size="large")
        self.generate_button.clicked.connect(self._generate_json)
        button_layout.addWidget(self.generate_button)

        # Copy button
        self.copy_button = GlassButton("📋 Copy JSON", variant="warning", size="large")
        self.copy_button.clicked.connect(self._copy_json)
        button_layout.addWidget(self.copy_button)

        output_layout.addLayout(button_layout)

        return output_widget

    def _add_field(self) -> None:
        """
        Add a new text field to the input section.
        """
        # Check if we've reached the maximum
        if len(self.text_fields) >= self.tool.max_fields:
            QMessageBox.warning(
                self,
                "Maximum Fields Reached",
                f"Cannot add more fields. Maximum of {self.tool.max_fields} fields allowed.",
            )
            return

        # Create draggable field container
        field_frame = DraggableFieldFrame(self.fields_container, reorder_callback=self._reorder_fields)
        field_frame.setObjectName("fieldFrame")
        field_layout = QHBoxLayout(field_frame)
        field_layout.setContentsMargins(8, 8, 8, 8)
        field_layout.setSpacing(10)

        # Add drag indicator (for reordering)
        drag_indicator = field_frame.drag_indicator
        field_layout.addWidget(drag_indicator)

        # Field number label
        field_num = len(self.text_fields) + 1
        num_label = QLabel(f"{field_num}")
        num_label.setFont(QFont("Arial", 13, QFont.Bold))
        num_label.setFixedSize(38, 38)
        num_label.setAlignment(Qt.AlignCenter)
        field_layout.addWidget(num_label)

        # Text input
        text_input = PlainTextEdit()
        text_input.setFont(QFont("Arial", 12))
        text_input.setPlaceholderText(f"Enter text for field {field_num}...")
        text_input.setFixedHeight(70)
        field_layout.addWidget(text_input)

        # Remove button
        remove_btn = QPushButton("×")
        remove_btn.setFont(QFont("Arial", 18, QFont.Bold))
        remove_btn.setFixedSize(36, 36)
        remove_btn.setCursor(Qt.PointingHandCursor)
        remove_btn.clicked.connect(lambda: self._remove_field(field_frame))
        field_layout.addWidget(remove_btn)

        # Store reference
        field_data = {
            'frame': field_frame,
            'input': text_input,
            'label': num_label,
            'button': remove_btn,
            'drag_indicator': drag_indicator
        }
        self.text_fields.append(field_data)

        # Apply theme to the new field
        self._apply_field_theme(field_data)

        # Add to layout (before the stretch)
        self.fields_layout.insertWidget(self.fields_layout.count() - 1, field_frame)

        # Update counter and button state
        self._update_field_counter()
        self.status_label.setText(f"Field {field_num} added")
        logger.debug(f"Text field {field_num} added")

    def _remove_field(self, field_frame: QFrame) -> None:
        """
        Remove a text field from the input section.

        Args:
            field_frame: The field frame to remove.
        """
        # Don't allow removing if only one field remains
        if len(self.text_fields) <= 1:
            QMessageBox.warning(
                self,
                "Cannot Remove",
                "At least one text field must remain.",
            )
            return

        # Find and remove the field
        for i, field_data in enumerate(self.text_fields):
            if field_data['frame'] == field_frame:
                # Remove from layout and delete widget
                self.fields_layout.removeWidget(field_frame)
                field_frame.deleteLater()

                # Remove from list
                self.text_fields.pop(i)

                # Renumber remaining fields
                self._renumber_fields()

                # Update counter
                self._update_field_counter()
                self.status_label.setText(f"Field removed")
                logger.debug(f"Text field removed, {len(self.text_fields)} fields remaining")
                break

    def _renumber_fields(self) -> None:
        """
        Renumber all fields after a removal or reorder.
        """
        for i, field_data in enumerate(self.text_fields):
            field_num = i + 1
            field_data['label'].setText(f"{field_num}")
            field_data['input'].setPlaceholderText(f"Enter text for field {field_num}...")

    def _reorder_fields(self, source_index: int, target_index: int) -> None:
        """
        Reorder fields via drag and drop.

        Args:
            source_index: Index of the field being dragged
            target_index: Index where the field should be dropped
        """
        if source_index == target_index:
            return

        # Adjust indices if we're accounting for the stretch widget at the end
        # The stretch is always at the last position in the layout
        actual_count = self.fields_layout.count() - 1  # Subtract the stretch

        # Bounds checking
        if source_index < 0 or source_index >= actual_count:
            return
        if target_index < 0 or target_index >= actual_count:
            return

        # Move in the list
        field_data = self.text_fields.pop(source_index)
        self.text_fields.insert(target_index, field_data)

        # Move in the layout
        widget = field_data['frame']
        self.fields_layout.removeWidget(widget)
        self.fields_layout.insertWidget(target_index, widget)

        # Renumber all fields
        self._renumber_fields()

        # Update status
        self.status_label.setText(f"Field reordered: {source_index + 1} → {target_index + 1}")
        logger.debug(f"Field reordered from position {source_index + 1} to {target_index + 1}")

    def _update_field_counter(self) -> None:
        """
        Update the field counter display.
        """
        field_count = len(self.text_fields)
        self.field_counter_label.setText(f"Fields: {field_count}/{self.tool.max_fields}")

        # Update add button state
        can_add = field_count < self.tool.max_fields
        self.add_field_button.setEnabled(can_add)

        if not can_add:
            self.add_field_button.setText(" Maximum Fields Reached")
        else:
            self.add_field_button.setText(" Add Field")

    def _generate_json(self) -> None:
        """
        Generate JSON from the text fields.
        """
        try:
            # Collect text from all fields
            text_items = []
            for field_data in self.text_fields:
                text = field_data['input'].toPlainText().strip()
                text_items.append(text)

            logger.info(f"Collecting {len(text_items)} text items")

            # Process through the tool (which filters empty items)
            collected_items = self.tool.process_json(text_items)
            logger.debug(f"Collected {len(collected_items)} non-empty items")

            # Convert to JSON string
            json_str = self.tool.to_json_string(collected_items, pretty=True)

            # Display output
            self.json_display.setPlainText(json_str)

            # Update status
            self.status_label.setText(
                f"JSON generated: {len(collected_items)} items from {len(text_items)} fields"
            )
            logger.info(f"JSON generated successfully with {len(collected_items)} items")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating JSON: {str(e)}")
            logger.error(f"Error generating JSON: {str(e)}")

    def _copy_json(self) -> None:
        """
        Copy the JSON to clipboard.
        """
        json_text = self.json_display.toPlainText().strip()

        if not json_text or json_text == "[]":
            QMessageBox.warning(
                self,
                "No JSON",
                "There is no JSON to copy. Generate JSON first.",
            )
            return

        clipboard = QApplication.clipboard()
        clipboard.setText(json_text)

        QMessageBox.information(self, "Copied", "JSON copied to clipboard!")
        self.status_label.setText("JSON copied to clipboard")
        logger.info("JSON copied to clipboard")

    def _clear_all(self) -> None:
        """
        Clear all text fields after confirmation.
        """
        reply = QMessageBox.question(
            self,
            "Clear All Fields",
            "Are you sure you want to clear all text fields?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # Clear all text inputs
            for field_data in self.text_fields:
                field_data['input'].clear()

            # Clear JSON display
            self.json_display.clear()

            self.status_label.setText("All fields cleared")
            logger.info("All text fields cleared")

    def _save_template(self) -> None:
        """Save current fields as a template."""
        # Get field values
        field_values = []
        for field_data in self.text_fields:
            text = field_data['input'].toPlainText().strip()
            field_values.append(text)

        # Check if there's content to save
        if not any(field_values):
            QMessageBox.warning(
                self,
                "No Content",
                "Please add some text to the fields before saving a template.",
            )
            return

        # Ask for template name
        template_name, ok = QInputDialog.getText(
            self,
            "Save Template",
            "Enter a name for this template:",
            text="My Template"
        )

        if not ok or not template_name.strip():
            return

        template_name = template_name.strip()

        # Create template data
        template_data = {
            "name": template_name,
            "field_count": len(field_values),
            "fields": field_values
        }

        # Save to file
        template_file = self.templates_dir / f"{template_name}.json"

        # Check if file exists
        if template_file.exists():
            reply = QMessageBox.question(
                self,
                "Template Exists",
                f"A template named '{template_name}' already exists. Overwrite it?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return

        try:
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)

            QMessageBox.information(
                self,
                "Template Saved",
                f"Template '{template_name}' has been saved successfully!",
            )
            self.status_label.setText(f"Template '{template_name}' saved")
            logger.info(f"Template saved: {template_name}")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save template: {str(e)}",
            )
            logger.error(f"Failed to save template: {str(e)}")

    def _load_template(self) -> None:
        """Load a template and populate fields."""
        # Get list of available templates
        template_files = list(self.templates_dir.glob("*.json"))

        if not template_files:
            QMessageBox.information(
                self,
                "No Templates",
                "No templates found. Save a template first!",
            )
            return

        # Create list of template names
        template_names = [f.stem for f in template_files]

        # Ask user to select a template
        template_name, ok = QInputDialog.getItem(
            self,
            "Load Template",
            "Select a template to load:",
            template_names,
            0,
            False
        )

        if not ok or not template_name:
            return

        # Load template file
        template_file = self.templates_dir / f"{template_name}.json"

        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)

            fields = template_data.get("fields", [])

            if not fields:
                QMessageBox.warning(
                    self,
                    "Empty Template",
                    "This template has no field data.",
                )
                return

            # Clear existing fields (but leave at least one)
            while len(self.text_fields) > 1:
                field_data = self.text_fields[-1]
                self._remove_field(field_data['frame'])

            # Add fields if needed
            while len(self.text_fields) < len(fields):
                self._add_field()

            # Populate fields
            for i, text in enumerate(fields):
                if i < len(self.text_fields):
                    self.text_fields[i]['input'].setPlainText(text)

            QMessageBox.information(
                self,
                "Template Loaded",
                f"Template '{template_name}' loaded successfully!",
            )
            self.status_label.setText(f"Template '{template_name}' loaded")
            logger.info(f"Template loaded: {template_name}")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load template: {str(e)}",
            )
            logger.error(f"Failed to load template: {str(e)}")

    def _bulk_import(self) -> None:
        """Import multiple items at once from clipboard or file."""
        # Ask user how they want to import
        reply = QMessageBox.question(
            self,
            "Bulk Import",
            "Choose import method:\n\n"
            "• Yes - Import from File (one item per line)\n"
            "• No - Paste from Clipboard\n"
            "• Cancel - Abort",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.No,
        )

        if reply == QMessageBox.Cancel:
            return

        items = []

        if reply == QMessageBox.Yes:
            # Import from file
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select File to Import",
                str(Path.home()),
                "Text Files (*.txt);;All Files (*.*)"
            )

            if not file_path:
                return

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    items = [line.strip() for line in f if line.strip()]

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to read file: {str(e)}",
                )
                logger.error(f"Failed to read file for bulk import: {str(e)}")
                return

        else:
            # Import from clipboard
            clipboard = QApplication.clipboard()
            text = clipboard.text().strip()

            if not text:
                QMessageBox.warning(
                    self,
                    "Empty Clipboard",
                    "Clipboard is empty. Copy some text first (one item per line).",
                )
                return

            # Split by lines
            items = [line.strip() for line in text.split('\n') if line.strip()]

        if not items:
            QMessageBox.warning(
                self,
                "No Items",
                "No items found to import.",
            )
            return

        # Check max fields limit
        if len(items) > self.tool.max_fields:
            reply = QMessageBox.question(
                self,
                "Too Many Items",
                f"You're trying to import {len(items)} items, but the maximum is {self.tool.max_fields}.\n\n"
                f"Import only the first {self.tool.max_fields} items?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )

            if reply != QMessageBox.Yes:
                return

            items = items[:self.tool.max_fields]

        # Clear existing fields (but keep at least one)
        while len(self.text_fields) > 1:
            field_data = self.text_fields[-1]
            self._remove_field(field_data['frame'])

        # Add fields if needed
        while len(self.text_fields) < len(items):
            self._add_field()

        # Populate fields
        for i, text in enumerate(items):
            if i < len(self.text_fields):
                self.text_fields[i]['input'].setPlainText(text)

        QMessageBox.information(
            self,
            "Import Complete",
            f"Successfully imported {len(items)} items!",
        )
        self.status_label.setText(f"Imported {len(items)} items")
        logger.info(f"Bulk imported {len(items)} items")

    def _on_theme_changed(self, new_theme) -> None:
        """Handle theme change."""
        self.generator = StylesheetGenerator(new_theme)
        self._apply_theme()

    def _apply_theme(self) -> None:
        """Apply the current theme to all widgets."""
        theme = self.theme_manager.current_theme

        # Main widget background
        self.setStyleSheet(f"""
            QWidget {{
                background: {theme.background_primary};
            }}
        """)

        # Apply theme to static elements
        self._apply_static_theme()

        # Update all text fields
        for field_data in self.text_fields:
            self._apply_field_theme(field_data)

    def _apply_static_theme(self) -> None:
        """Apply theme to static UI elements."""
        theme = self.theme_manager.current_theme

        # Controls frame
        if hasattr(self, 'controls_frame'):
            self.controls_frame.setStyleSheet(f"""
                QFrame {{
                    background: {theme.surface_glass};
                    border: 1px solid {theme.border_glass};
                    border-radius: 12px;
                    padding: 16px;
                }}
            """)

        # Field counter label
        if hasattr(self, 'field_counter_label'):
            self.field_counter_label.setStyleSheet(f"""
                QLabel {{
                    color: {theme.text_primary};
                    padding: 4px 8px;
                    background: {theme.background_glass};
                    border: 1px solid {theme.border_glass};
                    border-radius: 8px;
                }}
            """)

        # Splitter
        if hasattr(self, 'splitter'):
            self.splitter.setStyleSheet(f"""
                QSplitter::handle {{
                    background: {theme.border_glass};
                    border-radius: 5px;
                    margin: 2px 0px;
                }}
                QSplitter::handle:hover {{
                    background: {theme.accent_primary};
                }}
            """)

        # Input/output widgets
        for widget in [getattr(self, 'input_widget', None), getattr(self, 'output_widget', None)]:
            if widget:
                widget.setStyleSheet(f"""
                    QFrame {{
                        background: {theme.surface_glass};
                        border: 1px solid {theme.border_glass};
                        border-radius: 16px;
                        padding: 16px;
                    }}
                """)

        # Header labels
        for label in [getattr(self, 'input_header_label', None), getattr(self, 'output_header_label', None)]:
            if label:
                label.setStyleSheet(f"""
                    QLabel {{
                        color: {theme.text_primary};
                        padding: 8px 0px;
                        border-bottom: 2px solid {theme.accent_primary};
                        background: transparent;
                    }}
                """)

        # Scroll area
        if hasattr(self, 'scroll_area'):
            self.scroll_area.setStyleSheet(f"""
                QScrollArea {{
                    background: transparent;
                    border: none;
                }}
                QScrollBar:vertical {{
                    background: {theme.background_glass};
                    width: 12px;
                    border-radius: 6px;
                    margin: 0px;
                }}
                QScrollBar::handle:vertical {{
                    background: {theme.border_glass};
                    border-radius: 6px;
                    min-height: 30px;
                }}
                QScrollBar::handle:vertical:hover {{
                    background: {theme.accent_primary};
                }}
            """)

        # JSON display
        if hasattr(self, 'json_display'):
            self.json_display.setStyleSheet(f"""
                QPlainTextEdit {{
                    background: {theme.background_primary};
                    color: {theme.text_primary};
                    border: 2px solid {theme.border_glass};
                    border-radius: 12px;
                    padding: 12px;
                    font-size: 13px;
                }}
            """)

        # Status label
        if hasattr(self, 'status_label'):
            self.status_label.setStyleSheet(f"""
                QLabel {{
                    color: {theme.text_secondary};
                    background: transparent;
                }}
            """)

    def _apply_field_theme(self, field_data: dict) -> None:
        """
        Apply theme to a single field.

        Args:
            field_data: Field data dictionary
        """
        theme = self.theme_manager.current_theme

        # Field frame
        field_data['frame'].setStyleSheet(f"""
            QFrame {{
                background: {theme.surface_glass};
                border: 2px solid {theme.border_glass};
                border-radius: 12px;
                padding: 10px;
            }}
            QFrame:hover {{
                border-color: {theme.accent_primary};
                background: {theme.surface_glass_elevated};
            }}
        """)

        # Drag indicator
        field_data['drag_indicator'].setStyleSheet(f"""
            QLabel {{
                color: {theme.text_tertiary};
                background: transparent;
                padding: 4px;
            }}
            QLabel:hover {{
                color: {theme.accent_primary};
            }}
        """)

        # Field number label
        field_data['label'].setStyleSheet(f"""
            QLabel {{
                background: {theme.accent_primary};
                color: white;
                border-radius: 19px;
                font-weight: bold;
            }}
        """)

        # Text input
        field_data['input'].setStyleSheet(f"""
            QPlainTextEdit {{
                background: {theme.background_primary};
                color: {theme.text_primary};
                border: 2px solid {theme.border_glass};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            }}
            QPlainTextEdit:focus {{
                border-color: {theme.accent_primary};
            }}
        """)

        # Remove button
        field_data['button'].setStyleSheet(f"""
            QPushButton {{
                background: {theme.error_color};
                color: white;
                border: none;
                border-radius: 18px;
                padding: 0px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {theme.error_glow};
            }}
            QPushButton:pressed {{
                background: {theme.error_color};
            }}
        """)
