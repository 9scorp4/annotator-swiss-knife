"""
Conversation Generator widget for the annotation toolkit GUI.

Modern widget with drag-to-reorder, edit capabilities, templates, and live preview.
"""

from typing import List, Dict, Optional, Tuple
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QColor, QFont, QIcon, QDrag
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
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
    QMenu,
    QTabWidget,
)

from ....core.conversation.generator import ConversationGenerator
from ....utils import logger
from ..components.text_widgets import PlainTextEdit
from ..components import GlassButton, ConversationPreview
from ..dialogs import TurnEditDialog, TemplateLibrary
from ..themes import ThemeManager


class DraggableTurnListWidget(QListWidget):
    """
    Custom QListWidget with drag-and-drop reordering support.
    """

    def __init__(self, parent=None):
        """
        Initialize the draggable turn list widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setDragDropMode(QListWidget.InternalMove)
        self.setSelectionMode(QListWidget.SingleSelection)
        self.setDefaultDropAction(Qt.MoveAction)

    def dropEvent(self, event):
        """
        Handle drop event to reorder turns.

        Args:
            event: Drop event
        """
        # Get the source and destination indices
        source_item = self.currentItem()
        source_index = self.row(source_item)

        # Let the default drop happen
        super().dropEvent(event)

        # Get the new index after drop
        dest_index = self.row(source_item)

        # Notify parent widget of the reorder
        if hasattr(self.parent(), '_on_turns_reordered'):
            parent_widget = self.parent()
            while parent_widget and not hasattr(parent_widget, '_on_turns_reordered'):
                parent_widget = parent_widget.parent()
            if parent_widget:
                parent_widget._on_turns_reordered(source_index, dest_index)


class ConversationGeneratorWidget(QWidget):
    """
    Modern widget for the Conversation Generator tool.

    Features:
    - Drag-to-reorder conversation turns
    - Edit existing turns via double-click or context menu
    - Save/load conversation templates
    - Live preview pane with text and JSON views
    - Glassmorphic theme integration
    - Enhanced UI with modern components
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
        self._apply_theme()

        # Connect to theme changes
        theme_manager = ThemeManager.instance()
        theme_manager.theme_changed.connect(self._apply_theme)

    def _init_ui(self) -> None:
        """
        Initialize the user interface.
        """
        # Main layout with better spacing and margins
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Header with title and controls
        header_layout = QHBoxLayout()

        # Title
        title_label = QLabel("💬 Conversation Generator")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Turn counter
        self.turn_counter_label = QLabel(f"0/{self.tool.max_turns} turns")
        self.turn_counter_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_layout.addWidget(self.turn_counter_label)

        main_layout.addLayout(header_layout)

        # Top controls bar
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)

        # Template library button
        self.template_button = GlassButton("📚 Templates", variant="ghost", size="medium")
        self.template_button.setToolTip("Save/load conversation templates")
        self.template_button.clicked.connect(self._open_template_library)
        controls_layout.addWidget(self.template_button)

        # Format selector
        format_label = QLabel("JSON Format:")
        format_label.setStyleSheet("font-weight: bold;")
        controls_layout.addWidget(format_label)

        self.format_selector = QComboBox()
        self.format_selector.addItems(["Pretty", "Compact"])
        self.format_selector.currentTextChanged.connect(self._format_changed)
        controls_layout.addWidget(self.format_selector)

        controls_layout.addStretch()

        # Clear all button
        self.clear_button = GlassButton("🗑️ Clear All", variant="danger", size="medium")
        self.clear_button.setToolTip("Clear all conversation turns")
        self.clear_button.clicked.connect(self._clear_all)
        controls_layout.addWidget(self.clear_button)

        main_layout.addLayout(controls_layout)

        # Create a splitter for three-column layout
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(8)

        # Left: Input section
        input_widget = self._create_input_section()
        splitter.addWidget(input_widget)

        # Middle: Turn list
        turns_widget = self._create_turns_section()
        splitter.addWidget(turns_widget)

        # Right: Preview pane
        self.preview_pane = ConversationPreview()
        splitter.addWidget(self.preview_pane)

        # Set initial sizes (40% input, 30% turns, 30% preview)
        splitter.setSizes([400, 300, 300])

        main_layout.addWidget(splitter)

        # Status bar
        self.status_label = QLabel("Ready to create conversation")
        self.status_label.setStyleSheet("font-size: 12px; color: gray; padding: 8px;")
        main_layout.addWidget(self.status_label)

    def _create_input_section(self) -> QWidget:
        """
        Create the input section for adding turns.

        Returns:
            QWidget: The input section widget.
        """
        input_widget = QFrame()
        input_widget.setObjectName("inputSection")

        input_layout = QVBoxLayout(input_widget)
        input_layout.setContentsMargins(16, 16, 16, 16)
        input_layout.setSpacing(12)

        # Header
        header_label = QLabel("➕ Add New Turn")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        input_layout.addWidget(header_label)

        # User message input
        user_label = QLabel("👤 User Message:")
        user_label.setStyleSheet("font-weight: bold;")
        input_layout.addWidget(user_label)

        self.user_input = PlainTextEdit()
        self.user_input.setPlaceholderText("Enter the user's message...")
        self.user_input.setMinimumHeight(100)
        self.user_input.setObjectName("userInput")
        self.user_input.textChanged.connect(self._validate_inputs)
        input_layout.addWidget(self.user_input)

        # User character count
        self.user_char_label = QLabel("0 characters")
        self.user_char_label.setStyleSheet("font-size: 11px; color: gray;")
        input_layout.addWidget(self.user_char_label)

        # Assistant message input
        assistant_label = QLabel("🤖 Assistant Response:")
        assistant_label.setStyleSheet("font-weight: bold;")
        input_layout.addWidget(assistant_label)

        self.assistant_input = PlainTextEdit()
        self.assistant_input.setPlaceholderText("Enter the assistant's response...")
        self.assistant_input.setMinimumHeight(100)
        self.assistant_input.setObjectName("assistantInput")
        self.assistant_input.textChanged.connect(self._validate_inputs)
        input_layout.addWidget(self.assistant_input)

        # Assistant character count
        self.assistant_char_label = QLabel("0 characters")
        self.assistant_char_label.setStyleSheet("font-size: 11px; color: gray;")
        input_layout.addWidget(self.assistant_char_label)

        # Add turn button
        self.add_turn_button = GlassButton("➕ Add Turn", variant="primary", size="large")
        self.add_turn_button.setToolTip("Add this turn to the conversation (Ctrl+Enter)")
        self.add_turn_button.clicked.connect(self._add_turn)
        self.add_turn_button.setEnabled(False)  # Initially disabled until input is valid
        input_layout.addWidget(self.add_turn_button)

        # Hint
        hint_label = QLabel("💡 Tip: Double-click a turn to edit it, or drag to reorder")
        hint_label.setStyleSheet("font-size: 11px; font-style: italic; color: gray;")
        hint_label.setWordWrap(True)
        input_layout.addWidget(hint_label)

        input_layout.addStretch()

        return input_widget

    def _create_turns_section(self) -> QWidget:
        """
        Create the turns list section.

        Returns:
            QWidget: The turns section widget.
        """
        turns_widget = QFrame()
        turns_widget.setObjectName("turnsSection")

        turns_layout = QVBoxLayout(turns_widget)
        turns_layout.setContentsMargins(16, 16, 16, 16)
        turns_layout.setSpacing(12)

        # Header
        header_label = QLabel("📝 Conversation Turns")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        turns_layout.addWidget(header_label)

        # Turn list with drag-and-drop support
        self.turn_list = DraggableTurnListWidget(self)
        self.turn_list.setObjectName("turnList")
        self.turn_list.itemDoubleClicked.connect(self._edit_turn_item)
        self.turn_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.turn_list.customContextMenuRequested.connect(self._show_turn_context_menu)
        turns_layout.addWidget(self.turn_list)

        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        self.insert_button = GlassButton("⬆️ Insert Before", variant="success", size="medium")
        self.insert_button.setToolTip("Insert a new turn before the selected turn")
        self.insert_button.clicked.connect(self._insert_before_selected)
        self.insert_button.setEnabled(False)
        buttons_layout.addWidget(self.insert_button)

        self.edit_button = GlassButton("✏️ Edit", variant="primary", size="medium")
        self.edit_button.setToolTip("Edit selected turn")
        self.edit_button.clicked.connect(self._edit_selected_turn)
        self.edit_button.setEnabled(False)
        buttons_layout.addWidget(self.edit_button)

        self.delete_button = GlassButton("🗑️ Delete", variant="danger", size="medium")
        self.delete_button.setToolTip("Delete selected turn")
        self.delete_button.clicked.connect(self._delete_selected_turn)
        self.delete_button.setEnabled(False)
        buttons_layout.addWidget(self.delete_button)

        turns_layout.addLayout(buttons_layout)

        # Connect selection change to update button states
        self.turn_list.itemSelectionChanged.connect(self._on_turn_selection_changed)

        return turns_widget

    def _validate_inputs(self) -> None:
        """
        Validate input fields and update visual feedback in real-time.
        """
        theme = ThemeManager.instance().current_theme

        # Get text from inputs
        user_text = self.user_input.toPlainText().strip()
        assistant_text = self.assistant_input.toPlainText().strip()

        # Update character counts
        user_char_count = len(user_text)
        assistant_char_count = len(assistant_text)

        self.user_char_label.setText(f"{user_char_count} character{'s' if user_char_count != 1 else ''}")
        self.assistant_char_label.setText(f"{assistant_char_count} character{'s' if assistant_char_count != 1 else ''}")

        # Validate and update styling
        user_valid = len(user_text) > 0
        assistant_valid = len(assistant_text) > 0
        both_valid = user_valid and assistant_valid
        can_add = both_valid and self.tool.can_add_turn()

        # Update user input styling
        if user_text:  # Has content
            user_border_color = theme.success_color if user_valid else theme.text_secondary
            self.user_char_label.setStyleSheet(f"font-size: 11px; color: {theme.success_color};")
        else:  # Empty
            user_border_color = theme.border_subtle
            self.user_char_label.setStyleSheet(f"font-size: 11px; color: {theme.text_tertiary};")

        self.user_input.setStyleSheet(f"""
            QPlainTextEdit {{
                border: 2px solid {user_border_color};
                border-radius: 6px;
                padding: 8px;
                background: {theme.background_secondary};
                color: {theme.text_primary};
            }}
        """)

        # Update assistant input styling
        if assistant_text:  # Has content
            assistant_border_color = theme.success_color if assistant_valid else theme.text_secondary
            self.assistant_char_label.setStyleSheet(f"font-size: 11px; color: {theme.success_color};")
        else:  # Empty
            assistant_border_color = theme.border_subtle
            self.assistant_char_label.setStyleSheet(f"font-size: 11px; color: {theme.text_tertiary};")

        self.assistant_input.setStyleSheet(f"""
            QPlainTextEdit {{
                border: 2px solid {assistant_border_color};
                border-radius: 6px;
                padding: 8px;
                background: {theme.background_secondary};
                color: {theme.text_primary};
            }}
        """)

        # Update add button state
        self.add_turn_button.setEnabled(can_add)

        if not can_add and both_valid and not self.tool.can_add_turn():
            # Max turns reached
            self.add_turn_button.setToolTip(f"Maximum of {self.tool.max_turns} turns reached")
        else:
            self.add_turn_button.setToolTip("Add this turn to the conversation (Ctrl+Enter)")

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
                "Please enter a user message before adding a turn.",
            )
            self.user_input.setFocus()
            return

        if not assistant_message:
            QMessageBox.warning(
                self,
                "Empty Input",
                "Please enter an assistant response before adding a turn.",
            )
            self.assistant_input.setFocus()
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
                self._update_preview()
                self._update_turn_counter()

                # Update status
                turn_count = self.tool.get_turn_count()
                self.status_label.setText(f"✅ Turn {turn_count} added successfully")

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
                    user_msg[:60] + "..." if len(user_msg) > 60 else user_msg
                )
                assistant_preview = (
                    assistant_msg[:60] + "..."
                    if len(assistant_msg) > 60
                    else assistant_msg
                )

                # Create list item with icon
                item_text = f"Turn {i + 1}\n👤 {user_preview}\n🤖 {assistant_preview}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, i)  # Store turn index

                self.turn_list.addItem(item)

    def _update_preview(self) -> None:
        """
        Update the preview pane with current conversation.
        """
        # Get conversation data in standard format
        conversation = []
        turn_count = self.tool.get_turn_count()

        for i in range(turn_count):
            turn_data = self.tool.get_turn(i)
            if turn_data:
                user_msg, assistant_msg = turn_data
                conversation.append({"role": "user", "content": user_msg})
                conversation.append({"role": "assistant", "content": assistant_msg})

        self.preview_pane.update_preview(conversation)

    def _update_turn_counter(self) -> None:
        """
        Update the turn counter display.
        """
        turn_count = self.tool.get_turn_count()
        self.turn_counter_label.setText(f"{turn_count}/{self.tool.max_turns} turns")

        # Update button state
        can_add = self.tool.can_add_turn()
        self.add_turn_button.setEnabled(can_add)

        if not can_add:
            self.add_turn_button.setText("❌ Maximum Turns Reached")
        else:
            self.add_turn_button.setText("➕ Add Turn")

    def _on_turn_selection_changed(self) -> None:
        """
        Handle turn selection change to update button states.
        """
        has_selection = bool(self.turn_list.selectedItems())
        self.insert_button.setEnabled(has_selection)
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def _edit_turn_item(self, item: QListWidgetItem) -> None:
        """
        Edit a turn via double-click.

        Args:
            item: The list widget item that was double-clicked
        """
        turn_index = item.data(Qt.UserRole)
        self._edit_turn(turn_index)

    def _edit_selected_turn(self) -> None:
        """
        Edit the currently selected turn.
        """
        selected_items = self.turn_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            turn_index = item.data(Qt.UserRole)
            self._edit_turn(turn_index)

    def _edit_turn(self, turn_index: int) -> None:
        """
        Open the edit dialog for a specific turn.

        Args:
            turn_index: Index of the turn to edit
        """
        turn_data = self.tool.get_turn(turn_index)
        if not turn_data:
            QMessageBox.warning(self, "Error", "Could not load turn data")
            return

        user_msg, assistant_msg = turn_data

        # Open edit dialog
        dialog = TurnEditDialog(
            user_message=user_msg,
            assistant_response=assistant_msg,
            turn_number=turn_index + 1,
            parent=self
        )

        if dialog.exec_() == TurnEditDialog.Accepted:
            # Get edited data
            new_user_msg, new_assistant_msg = dialog.get_turn_data()

            # Update the turn
            success = self.tool.update_turn(turn_index, new_user_msg, new_assistant_msg)

            if success:
                self._update_turn_list()
                self._update_preview()
                self.status_label.setText(f"✅ Turn {turn_index + 1} updated successfully")
                logger.info(f"Turn {turn_index + 1} updated successfully")
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to update Turn {turn_index + 1}"
                )
                logger.error(f"Failed to update turn {turn_index + 1}")

    def _show_turn_context_menu(self, position) -> None:
        """
        Show context menu for turn list items.

        Args:
            position: The position where the menu was requested.
        """
        item = self.turn_list.itemAt(position)
        if item:
            menu = QMenu(self)

            insert_before_action = menu.addAction("⬆️ Insert Before")
            insert_before_action.triggered.connect(lambda: self._insert_turn(item, before=True))

            insert_after_action = menu.addAction("⬇️ Insert After")
            insert_after_action.triggered.connect(lambda: self._insert_turn(item, before=False))

            menu.addSeparator()

            edit_action = menu.addAction("✏️ Edit Turn")
            edit_action.triggered.connect(lambda: self._edit_turn_item(item))

            menu.addSeparator()

            delete_action = menu.addAction("🗑️ Delete Turn")
            delete_action.triggered.connect(lambda: self._delete_turn(item))

            menu.exec_(self.turn_list.mapToGlobal(position))

    def _delete_selected_turn(self) -> None:
        """
        Delete the currently selected turn.
        """
        selected_items = self.turn_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            self._delete_turn(item)

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
                self._update_preview()
                self._update_turn_counter()

                self.status_label.setText(f"🗑️ Turn {turn_index + 1} deleted")
                logger.info(f"Turn {turn_index + 1} deleted successfully")
            else:
                QMessageBox.critical(
                    self, "Error", f"Failed to delete Turn {turn_index + 1}"
                )
                logger.error(f"Failed to delete turn {turn_index + 1}")

    def _insert_before_selected(self) -> None:
        """
        Insert a new turn before the currently selected turn.
        """
        selected_items = self.turn_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            self._insert_turn(item, before=True)

    def _insert_turn(self, item: QListWidgetItem, before: bool = True) -> None:
        """
        Insert a new turn before or after an existing turn.

        Args:
            item: The list widget item representing the reference turn
            before: If True, insert before the reference turn; if False, insert after
        """
        turn_index = item.data(Qt.UserRole)
        insert_index = turn_index if before else turn_index + 1

        # Open dialog to get new turn content
        dialog = TurnEditDialog(
            user_message="",
            assistant_response="",
            turn_number=insert_index + 1,
            parent=self
        )
        dialog.setWindowTitle(f"Insert Turn at Position {insert_index + 1}")

        if dialog.exec_() == QDialog.Accepted:
            user_message, assistant_message = dialog.get_messages()

            # Insert the turn
            try:
                success = self.tool.insert_turn(insert_index, user_message, assistant_message)

                if success:
                    # Update UI
                    self._update_turn_list()
                    self._update_preview()
                    self._update_turn_counter()

                    position_text = "before" if before else "after"
                    self.status_label.setText(
                        f"✅ Turn inserted {position_text} Turn {turn_index + 1}"
                    )
                    logger.info(f"Turn inserted at position {insert_index}")
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Failed to insert turn at position {insert_index + 1}. "
                        f"Maximum of {self.tool.max_turns} turns allowed."
                    )
                    logger.error(f"Failed to insert turn at position {insert_index}")
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to insert turn: {str(e)}"
                )
                logger.error(f"Error inserting turn: {str(e)}")

    def _on_turns_reordered(self, source_index: int, dest_index: int) -> None:
        """
        Handle turn reordering via drag-and-drop.

        Args:
            source_index: Original index of the dragged turn
            dest_index: New index after drop
        """
        if source_index == dest_index:
            return

        try:
            # Get the turn data
            turn_data = self.tool.get_turn(source_index)
            if not turn_data:
                return

            user_msg, assistant_msg = turn_data

            # Remove from old position
            self.tool.remove_turn(source_index)

            # Calculate new position (accounting for the removal)
            if dest_index > source_index:
                dest_index -= 1

            # Insert at new position
            self.tool.insert_turn(dest_index, user_msg, assistant_msg)

            # Update UI
            self._update_turn_list()
            self._update_preview()

            self.status_label.setText(f"📌 Turn moved from position {source_index + 1} to {dest_index + 1}")
            logger.info(f"Turn reordered: {source_index} → {dest_index}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error reordering turns: {str(e)}")
            logger.error(f"Error reordering turns: {str(e)}")
            # Refresh the list to ensure consistency
            self._update_turn_list()

    def _open_template_library(self) -> None:
        """
        Open the template library dialog.
        """
        # Get current conversation for saving
        conversation = []
        turn_count = self.tool.get_turn_count()

        for i in range(turn_count):
            turn_data = self.tool.get_turn(i)
            if turn_data:
                user_msg, assistant_msg = turn_data
                conversation.append({"role": "user", "content": user_msg})
                conversation.append({"role": "assistant", "content": assistant_msg})

        # Open template library
        dialog = TemplateLibrary(current_conversation=conversation, parent=self)
        dialog.template_selected.connect(self._load_template)
        dialog.exec_()

    def _load_template(self, template_turns: List[Dict]) -> None:
        """
        Load a template into the conversation generator.

        Args:
            template_turns: List of conversation turns from template
        """
        # Confirm if there are existing turns
        if self.tool.get_turn_count() > 0:
            reply = QMessageBox.question(
                self,
                "Load Template",
                "Loading a template will replace the current conversation. Continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply != QMessageBox.Yes:
                return

        try:
            # Clear existing conversation
            self.tool.clear()

            # Load template turns
            for turn in template_turns:
                role = turn.get("role", "")
                content = turn.get("content", "")

                if role == "user":
                    # Store user message temporarily
                    user_message = content
                elif role == "assistant" and user_message:
                    # Add complete turn
                    self.tool.add_turn(user_message, content)
                    user_message = None

            # Update UI
            self._update_turn_list()
            self._update_preview()
            self._update_turn_counter()

            turn_count = self.tool.get_turn_count()
            self.status_label.setText(f"📚 Template loaded with {turn_count} turns")
            logger.info(f"Template loaded with {turn_count} turns")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading template: {str(e)}")
            logger.error(f"Error loading template: {str(e)}")

    def _format_changed(self, format_text: str) -> None:
        """
        Handle format selector change.

        Args:
            format_text (str): The selected format text.
        """
        self._update_preview()
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
            self._update_preview()
            self._update_turn_counter()

            self.status_label.setText("🗑️ All turns cleared")
            logger.info("All conversation turns cleared")

    def _apply_theme(self) -> None:
        """
        Apply glassmorphic theme styling.
        """
        theme = ThemeManager.instance().current_theme

        self.setStyleSheet(f"""
            ConversationGeneratorWidget {{
                background: {theme.background_primary};
            }}
            QLabel {{
                color: {theme.text_primary};
                background: transparent;
            }}
            QFrame#inputSection, QFrame#turnsSection {{
                background: {theme.background_secondary};
                border: 1px solid {theme.border_glass};
                border-radius: 8px;
                padding: 8px;
            }}
            QComboBox {{
                background: {theme.surface_glass};
                color: {theme.text_primary};
                border: 1px solid {theme.border_subtle};
                border-radius: 6px;
                padding: 6px 12px;
                min-width: 100px;
            }}
            QComboBox:hover {{
                background: {theme.surface_glass_elevated};
                border-color: {theme.accent_primary};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background: {theme.background_secondary};
                color: {theme.text_primary};
                border: 1px solid {theme.border_glass};
                border-radius: 6px;
                selection-background-color: {theme.accent_primary};
            }}
            QListWidget#turnList {{
                background: {theme.background_primary};
                color: {theme.text_primary};
                border: 1px solid {theme.border_glass};
                border-radius: 6px;
                padding: 8px;
            }}
            QListWidget#turnList::item {{
                background: {theme.surface_glass};
                border: 1px solid {theme.border_subtle};
                border-radius: 6px;
                padding: 12px;
                margin: 4px;
            }}
            QListWidget#turnList::item:selected {{
                background: {theme.accent_primary};
                color: white;
                border-color: {theme.accent_primary};
            }}
            QListWidget#turnList::item:hover {{
                background: {theme.surface_glass_elevated};
                border-color: {theme.accent_secondary};
            }}
            QSplitter::handle {{
                background: {theme.border_glass};
            }}
            QSplitter::handle:hover {{
                background: {theme.accent_primary};
            }}
        """)

    def keyPressEvent(self, event) -> None:
        """
        Handle keyboard events.

        Args:
            event: Key event
        """
        # Ctrl+Enter to add turn
        if event.key() == Qt.Key_Return and event.modifiers() & Qt.ControlModifier:
            if self.add_turn_button.isEnabled():
                self._add_turn()
            event.accept()
        else:
            super().keyPressEvent(event)
