"""
Conversation Generator widget for the annotation toolkit GUI.

This module implements the widget for the Conversation Generator tool.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ....config import Config
from ....core.conversation.generator import ConversationGenerator
from ....utils import logger
from .custom_widgets import PlainTextEdit

# Get the configuration
config = Config()


class ConversationGeneratorWidget(QWidget):
    """
    Widget for the Conversation Generator tool.
    """

    def __init__(self, tool: ConversationGenerator):
        """
        Initialize the Conversation Generator widget.

        Args:
            tool (ConversationGenerator): The Conversation Generator tool.
        """
        super().__init__()
        self.tool = tool
        self._init_ui()

    def _init_ui(self) -> None:
        """
        Initialize the user interface.
        """
        # Main layout with better spacing and margins
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)

        # Top controls in a styled frame
        controls_frame = QFrame()
        controls_frame.setObjectName("controlsFrame")

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

        # Turn counter
        self.turn_counter_label = QLabel(f"Turns: 0/{self.tool.max_turns}")
        self.turn_counter_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.turn_counter_label.setObjectName("sectionTitle")
        controls_layout.addWidget(self.turn_counter_label)

        controls_layout.addStretch(1)

        # Format selector
        format_label = QLabel("JSON Format:")
        format_label.setFont(QFont("Arial", 11, QFont.Bold))
        format_label.setObjectName("fieldLabel")
        controls_layout.addWidget(format_label)

        self.format_selector = QComboBox()
        self.format_selector.addItems(["Pretty", "Compact"])
        self.format_selector.currentTextChanged.connect(self._format_changed)
        controls_layout.addWidget(self.format_selector)

        # Clear all button
        self.clear_button = QPushButton(" Clear All")
        self.clear_button.setIcon(QIcon.fromTheme("edit-clear"))
        self.clear_button.setCursor(Qt.PointingHandCursor)
        self.clear_button.setStyleSheet(
            """
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c1170a;
            }
        """
        )
        self.clear_button.clicked.connect(self._clear_all)
        controls_layout.addWidget(self.clear_button)

        main_layout.addWidget(controls_frame)

        # Create a splitter for input and output sections
        splitter = QSplitter(Qt.Horizontal)
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

        # Left side: Input section
        input_widget = self._create_input_section()
        splitter.addWidget(input_widget)

        # Right side: Output section
        output_widget = self._create_output_section()
        splitter.addWidget(output_widget)

        # Set initial sizes
        splitter.setSizes([500, 500])

        main_layout.addWidget(splitter)

        # Status bar
        status_frame = QFrame()
        status_frame.setObjectName("statusFrame")
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(10, 5, 10, 5)

        self.status_label = QLabel("Ready to create conversation")
        self.status_label.setObjectName("statusLabel")
        status_layout.addWidget(self.status_label)

        main_layout.addWidget(status_frame)

    def _create_input_section(self) -> QWidget:
        """
        Create the input section for adding turns.

        Returns:
            QWidget: The input section widget.
        """
        input_widget = QFrame()
        input_widget.setObjectName("jsonInputFrame")

        # Add shadow
        input_shadow = QGraphicsDropShadowEffect()
        input_shadow.setBlurRadius(15)
        input_shadow.setXOffset(0)
        input_shadow.setYOffset(2)
        input_shadow.setColor(QColor(0, 0, 0, 30))
        input_widget.setGraphicsEffect(input_shadow)

        input_layout = QVBoxLayout(input_widget)
        input_layout.setContentsMargins(15, 15, 15, 15)
        input_layout.setSpacing(10)

        # Header
        header_label = QLabel("Add Conversation Turns")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_label.setObjectName("sectionTitle")
        input_layout.addWidget(header_label)

        # User message input
        user_label = QLabel("User Prompt:")
        user_label.setFont(QFont("Arial", 11, QFont.Bold))
        user_label.setObjectName("fieldLabel")
        input_layout.addWidget(user_label)

        self.user_input = PlainTextEdit()
        self.user_input.setFont(QFont("Arial", 11))
        self.user_input.setPlaceholderText("Paste the user's prompt here...")
        self.user_input.setFixedHeight(70)
        input_layout.addWidget(self.user_input)

        # Assistant message input
        assistant_label = QLabel("AI Response:")
        assistant_label.setFont(QFont("Arial", 11, QFont.Bold))
        assistant_label.setObjectName("fieldLabel")
        input_layout.addWidget(assistant_label)

        self.assistant_input = PlainTextEdit()
        self.assistant_input.setFont(QFont("Arial", 11))
        self.assistant_input.setPlaceholderText("Paste the AI's response here...")
        self.assistant_input.setFixedHeight(70)
        input_layout.addWidget(self.assistant_input)

        # Add turn button
        self.add_turn_button = QPushButton(" Add Turn")
        self.add_turn_button.setIcon(QIcon.fromTheme("list-add"))
        self.add_turn_button.setCursor(Qt.PointingHandCursor)
        self.add_turn_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """
        )
        self.add_turn_button.clicked.connect(self._add_turn)
        input_layout.addWidget(self.add_turn_button)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        input_layout.addWidget(separator)

        # Turn list header
        turns_label = QLabel("Added Turns:")
        turns_label.setFont(QFont("Arial", 11, QFont.Bold))
        turns_label.setObjectName("fieldLabel")
        input_layout.addWidget(turns_label)

        # Turn list
        self.turn_list = QListWidget()
        self.turn_list.setObjectName("turnList")
        input_layout.addWidget(self.turn_list)

        return input_widget

    def _create_output_section(self) -> QWidget:
        """
        Create the output section for displaying JSON.

        Returns:
            QWidget: The output section widget.
        """
        output_widget = QFrame()
        output_widget.setObjectName("displayFrame")

        # Add shadow
        output_shadow = QGraphicsDropShadowEffect()
        output_shadow.setBlurRadius(15)
        output_shadow.setXOffset(0)
        output_shadow.setYOffset(2)
        output_shadow.setColor(QColor(0, 0, 0, 30))
        output_widget.setGraphicsEffect(output_shadow)

        output_layout = QVBoxLayout(output_widget)
        output_layout.setContentsMargins(15, 15, 15, 15)
        output_layout.setSpacing(10)

        # Header
        header_label = QLabel("Generated JSON:")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_label.setObjectName("sectionTitle")
        output_layout.addWidget(header_label)

        # JSON display
        self.json_display = PlainTextEdit()
        self.json_display.setReadOnly(True)
        self.json_display.setFont(QFont("Courier New", 11))
        self.json_display.setPlaceholderText(
            "Add conversation turns to see the generated JSON here..."
        )
        output_layout.addWidget(self.json_display)

        # Copy button
        self.copy_button = QPushButton(" Copy JSON")
        self.copy_button.setIcon(QIcon.fromTheme("edit-copy"))
        self.copy_button.setCursor(Qt.PointingHandCursor)
        self.copy_button.setStyleSheet(
            """
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
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
        self.copy_button.clicked.connect(self._copy_json)
        output_layout.addWidget(self.copy_button)

        return output_widget

    def _add_turn(self) -> None:
        """
        Add a conversation turn from the input fields.
        """
        user_message = self.user_input.toPlainText().strip()
        assistant_message = self.assistant_input.toPlainText().strip()

        # Validate inputs
        if not user_message:
            QMessageBox.warning(
                self,
                "Empty Input",
                "Please enter a user prompt before adding a turn.",
            )
            return

        if not assistant_message:
            QMessageBox.warning(
                self,
                "Empty Input",
                "Please enter an AI response before adding a turn.",
            )
            return

        # Add the turn
        try:
            success = self.tool.add_turn(user_message, assistant_message)

            if success:
                # Clear input fields
                self.user_input.clear()
                self.assistant_input.clear()

                # Update UI
                self._update_turn_list()
                self._update_json_display()
                self._update_turn_counter()

                # Update status
                turn_count = self.tool.get_turn_count()
                self.status_label.setText(f"Turn {turn_count} added successfully")

                # Focus back on user input
                self.user_input.setFocus()

                logger.info(f"Turn added successfully. Total turns: {turn_count}")
            else:
                QMessageBox.warning(
                    self,
                    "Maximum Turns Reached",
                    f"Cannot add more turns. Maximum of {self.tool.max_turns} turns reached.",
                )
                logger.warning("Failed to add turn: maximum turns reached")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error adding turn: {str(e)}")
            logger.error(f"Error adding turn: {str(e)}")

    def _update_turn_list(self) -> None:
        """
        Update the turn list display.
        """
        self.turn_list.clear()

        turn_count = self.tool.get_turn_count()
        for i in range(turn_count):
            turn_data = self.tool.get_turn(i)
            if turn_data:
                user_msg, assistant_msg = turn_data

                # Truncate messages for display
                user_preview = (
                    user_msg[:50] + "..." if len(user_msg) > 50 else user_msg
                )
                assistant_preview = (
                    assistant_msg[:50] + "..."
                    if len(assistant_msg) > 50
                    else assistant_msg
                )

                # Create list item
                item_text = f"Turn {i + 1}\nUser: {user_preview}\nAI: {assistant_preview}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, i)  # Store turn index

                self.turn_list.addItem(item)

        # Add context menu for deletion
        self.turn_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.turn_list.customContextMenuRequested.connect(self._show_turn_context_menu)

    def _show_turn_context_menu(self, position) -> None:
        """
        Show context menu for turn list items.

        Args:
            position: The position where the menu was requested.
        """
        item = self.turn_list.itemAt(position)
        if item:
            from PyQt5.QtWidgets import QMenu

            menu = QMenu(self)

            delete_action = menu.addAction("Delete Turn")
            delete_action.triggered.connect(lambda: self._delete_turn(item))

            menu.exec_(self.turn_list.mapToGlobal(position))

    def _delete_turn(self, item: QListWidgetItem) -> None:
        """
        Delete a turn from the conversation.

        Args:
            item: The list widget item representing the turn.
        """
        turn_index = item.data(Qt.UserRole)

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete Turn",
            f"Are you sure you want to delete Turn {turn_index + 1}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            success = self.tool.remove_turn(turn_index)

            if success:
                self._update_turn_list()
                self._update_json_display()
                self._update_turn_counter()

                self.status_label.setText(f"Turn {turn_index + 1} deleted")
                logger.info(f"Turn {turn_index + 1} deleted successfully")
            else:
                QMessageBox.critical(
                    self, "Error", f"Failed to delete Turn {turn_index + 1}"
                )
                logger.error(f"Failed to delete turn {turn_index + 1}")

    def _update_json_display(self) -> None:
        """
        Update the JSON display with the current conversation.
        """
        pretty = self.format_selector.currentText() == "Pretty"
        json_str = self.tool.generate_json(pretty=pretty)
        self.json_display.setPlainText(json_str)

    def _update_turn_counter(self) -> None:
        """
        Update the turn counter display.
        """
        turn_count = self.tool.get_turn_count()
        self.turn_counter_label.setText(f"Turns: {turn_count}/{self.tool.max_turns}")

        # Update button state
        can_add = self.tool.can_add_turn()
        self.add_turn_button.setEnabled(can_add)

        if not can_add:
            self.add_turn_button.setText(" Maximum Turns Reached")
        else:
            self.add_turn_button.setText(" Add Turn")

    def _format_changed(self, format_text: str) -> None:
        """
        Handle format selector change.

        Args:
            format_text (str): The selected format text.
        """
        self._update_json_display()
        self.status_label.setText(f"Format changed to {format_text}")

    def _clear_all(self) -> None:
        """
        Clear all conversation turns after confirmation.
        """
        if self.tool.get_turn_count() == 0:
            QMessageBox.information(
                self, "No Turns", "There are no turns to clear."
            )
            return

        reply = QMessageBox.question(
            self,
            "Clear All Turns",
            "Are you sure you want to clear all conversation turns?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.tool.clear()
            self.user_input.clear()
            self.assistant_input.clear()
            self._update_turn_list()
            self._update_json_display()
            self._update_turn_counter()

            self.status_label.setText("All turns cleared")
            logger.info("All conversation turns cleared")

    def _copy_json(self) -> None:
        """
        Copy the JSON to clipboard.
        """
        json_text = self.json_display.toPlainText().strip()

        if not json_text or json_text == "[]":
            QMessageBox.warning(
                self,
                "No JSON",
                "There is no conversation JSON to copy. Add some turns first.",
            )
            return

        clipboard = QApplication.clipboard()
        clipboard.setText(json_text)

        QMessageBox.information(self, "Copied", "JSON copied to clipboard!")
        self.status_label.setText("JSON copied to clipboard")
        logger.info("Conversation JSON copied to clipboard")
