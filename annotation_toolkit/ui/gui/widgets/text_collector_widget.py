"""
Text Collector widget for the annotation toolkit GUI.

This module implements the widget for the Text Collector tool.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QIcon
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
)

from ....config import Config
from ....core.text.text_collector import TextCollector
from ....utils import logger
from .custom_widgets import PlainTextEdit
from ..theme import (
    ColorPalette,
    Spacing,
    BorderRadius,
    get_success_button_style,
    get_danger_button_style,
    get_primary_button_style,
    get_warning_button_style,
)

# Get the configuration
config = Config()


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
        self._init_ui()

        # Add initial fields (start with 3)
        for _ in range(3):
            self._add_field()

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
        controls_frame.setStyleSheet(f"""
            #controlsFrame {{
                background-color: {ColorPalette.GRAY_50};
                border: 1px solid {ColorPalette.GRAY_200};
                border-radius: {BorderRadius.LG};
                padding: {Spacing.LG};
            }}
        """)

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
        self.field_counter_label.setStyleSheet(f"""
            QLabel {{
                color: {ColorPalette.GRAY_700};
                padding: 4px 8px;
                background-color: {ColorPalette.GRAY_100};
                border-radius: {BorderRadius.MD};
            }}
        """)
        controls_layout.addWidget(self.field_counter_label)

        controls_layout.addStretch(1)

        # Add field button with modern style
        self.add_field_button = QPushButton(" Add Field")
        self.add_field_button.setIcon(QIcon.fromTheme("list-add"))
        self.add_field_button.setCursor(Qt.PointingHandCursor)
        self.add_field_button.setFixedHeight(34)  # Reduced height
        self.add_field_button.setStyleSheet(get_success_button_style())
        self.add_field_button.clicked.connect(self._add_field)
        controls_layout.addWidget(self.add_field_button)

        # Clear all button with modern style
        self.clear_button = QPushButton(" Clear All")
        self.clear_button.setIcon(QIcon.fromTheme("edit-clear"))
        self.clear_button.setCursor(Qt.PointingHandCursor)
        self.clear_button.setFixedHeight(34)  # Reduced height
        self.clear_button.setStyleSheet(get_danger_button_style())
        self.clear_button.clicked.connect(self._clear_all)
        controls_layout.addWidget(self.clear_button)

        # Add controls frame with no stretch - takes minimum height only
        main_layout.addWidget(controls_frame, 0)

        # Create a splitter for input and output sections
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(10)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {ColorPalette.GRAY_300};
                border-radius: 5px;
                margin: 2px 0px;
            }}
            QSplitter::handle:hover {{
                background-color: {ColorPalette.PRIMARY};
            }}
        """)

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
        input_widget.setStyleSheet(f"""
            #jsonInputFrame {{
                background-color: {ColorPalette.LIGHT_BG_PRIMARY};
                border: 1px solid {ColorPalette.GRAY_200};
                border-radius: {BorderRadius.XL};
                padding: {Spacing.XL};
            }}
        """)

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
        header_label.setStyleSheet(f"""
            QLabel {{
                color: {ColorPalette.GRAY_900};
                padding: 8px 0px;
                border-bottom: 2px solid {ColorPalette.PRIMARY};
            }}
        """)
        input_layout.addWidget(header_label)

        # Scrollable area for text fields
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {ColorPalette.GRAY_100};
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {ColorPalette.GRAY_400};
                border-radius: 6px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {ColorPalette.GRAY_500};
            }}
        """)

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
        output_widget.setStyleSheet(f"""
            #displayFrame {{
                background-color: {ColorPalette.LIGHT_BG_PRIMARY};
                border: 1px solid {ColorPalette.GRAY_200};
                border-radius: {BorderRadius.XL};
                padding: {Spacing.XL};
            }}
        """)

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
        header_label.setStyleSheet(f"""
            QLabel {{
                color: {ColorPalette.GRAY_900};
                padding: 8px 0px;
                border-bottom: 2px solid {ColorPalette.PRIMARY};
            }}
        """)
        output_layout.addWidget(header_label)

        # JSON display with modern styling
        self.json_display = PlainTextEdit()
        self.json_display.setReadOnly(True)
        self.json_display.setFont(QFont("Courier New", 12))
        self.json_display.setPlaceholderText(
            "Add text to fields and click 'Generate JSON' to see output here..."
        )
        self.json_display.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {ColorPalette.GRAY_50};
                color: {ColorPalette.GRAY_900};
                border: 2px solid {ColorPalette.GRAY_200};
                border-radius: {BorderRadius.LG};
                padding: {Spacing.LG};
                font-size: 13px;
                line-height: 1.6;
            }}
        """)
        output_layout.addWidget(self.json_display)

        # Button row with modern styling
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        # Generate JSON button
        self.generate_button = QPushButton(" Generate JSON")
        self.generate_button.setIcon(QIcon.fromTheme("system-run"))
        self.generate_button.setCursor(Qt.PointingHandCursor)
        self.generate_button.setFixedHeight(38)  # Slightly reduced height
        self.generate_button.setStyleSheet(get_primary_button_style())
        self.generate_button.clicked.connect(self._generate_json)
        button_layout.addWidget(self.generate_button)

        # Copy button
        self.copy_button = QPushButton(" Copy JSON")
        self.copy_button.setIcon(QIcon.fromTheme("edit-copy"))
        self.copy_button.setCursor(Qt.PointingHandCursor)
        self.copy_button.setFixedHeight(38)  # Slightly reduced height
        self.copy_button.setStyleSheet(get_warning_button_style())
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

        # Create field container with modern styling
        field_frame = QFrame()
        field_frame.setObjectName("fieldFrame")
        field_frame.setStyleSheet(f"""
            #fieldFrame {{
                background-color: {ColorPalette.GRAY_50};
                border: 2px solid {ColorPalette.GRAY_200};
                border-radius: {BorderRadius.LG};
                padding: 10px;
            }}
            #fieldFrame:hover {{
                border-color: {ColorPalette.GRAY_300};
                background-color: {ColorPalette.LIGHT_BG_PRIMARY};
            }}
        """)
        field_layout = QHBoxLayout(field_frame)
        field_layout.setContentsMargins(8, 8, 8, 8)
        field_layout.setSpacing(10)

        # Field number label with badge style
        field_num = len(self.text_fields) + 1
        num_label = QLabel(f"{field_num}")
        num_label.setFont(QFont("Arial", 13, QFont.Bold))
        num_label.setFixedSize(38, 38)
        num_label.setAlignment(Qt.AlignCenter)
        num_label.setStyleSheet(f"""
            QLabel {{
                background-color: {ColorPalette.PRIMARY};
                color: white;
                border-radius: 19px;
                font-weight: bold;
            }}
        """)
        field_layout.addWidget(num_label)

        # Text input with better styling
        text_input = PlainTextEdit()
        text_input.setFont(QFont("Arial", 12))
        text_input.setPlaceholderText(f"Enter text for field {field_num}...")
        text_input.setFixedHeight(70)  # Slightly taller for better usability
        text_input.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: white;
                color: {ColorPalette.GRAY_900};
                border: 2px solid {ColorPalette.GRAY_200};
                border-radius: {BorderRadius.MD};
                padding: 8px 12px;
                font-size: 13px;
            }}
            QPlainTextEdit:focus {{
                border-color: {ColorPalette.PRIMARY};
            }}
        """)
        field_layout.addWidget(text_input)

        # Remove button with modern styling
        remove_btn = QPushButton("×")
        remove_btn.setFont(QFont("Arial", 18, QFont.Bold))
        remove_btn.setFixedSize(36, 36)
        remove_btn.setCursor(Qt.PointingHandCursor)
        remove_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ColorPalette.DANGER_LIGHT};
                color: white;
                border: none;
                border-radius: 18px;
                padding: 0px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {ColorPalette.DANGER};
            }}
            QPushButton:pressed {{
                background-color: {ColorPalette.DANGER_PRESSED};
            }}
        """)
        remove_btn.clicked.connect(lambda: self._remove_field(field_frame))
        field_layout.addWidget(remove_btn)

        # Store reference
        field_data = {
            'frame': field_frame,
            'input': text_input,
            'label': num_label,
            'button': remove_btn
        }
        self.text_fields.append(field_data)

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
        Renumber all fields after a removal.
        """
        for i, field_data in enumerate(self.text_fields):
            field_num = i + 1
            field_data['label'].setText(f"{field_num}")
            field_data['input'].setPlaceholderText(f"Enter text for field {field_num}...")

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
