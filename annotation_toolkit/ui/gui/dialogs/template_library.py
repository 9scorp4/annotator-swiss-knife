"""
TemplateLibrary - Dialog for managing conversation templates.

Allows saving, loading, and deleting conversation templates.
"""

from typing import List, Dict, Optional
import json
from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal, QSettings
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QInputDialog,
)

from ..components import GlassButton
from ..themes import ThemeManager


class TemplateLibrary(QDialog):
    """
    Dialog for managing conversation templates.

    Features:
    - Load template from library
    - Save current conversation as template
    - Delete templates
    - Template metadata (name, description, turn count)
    - Theme-aware styling

    Signals:
        template_selected: Emitted when a template is selected with template data
    """

    # Signal emitted when template is selected
    template_selected = pyqtSignal(list)  # List of conversation turns

    def __init__(self, current_conversation: Optional[List[Dict]] = None, parent=None):
        """
        Initialize the template library dialog.

        Args:
            current_conversation: Current conversation to save as template
            parent: Parent widget
        """
        super().__init__(parent)

        self.current_conversation = current_conversation or []
        self.templates_dir = Path.home() / "annotation_toolkit_data" / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # Setup dialog
        self._init_ui()
        self._load_templates()
        self._apply_theme()

        # Connect to theme changes
        theme_manager = ThemeManager.instance()
        theme_manager.theme_changed.connect(self._apply_theme)

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle("Conversation Template Library")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header
        header_label = QLabel("📚 Conversation Template Library")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header_label)

        # Description
        desc_label = QLabel(
            "Save frequently used conversation patterns as templates for quick reuse."
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Template list
        list_label = QLabel("Available Templates:")
        list_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(list_label)

        self.template_list = QListWidget()
        self.template_list.setAlternatingRowColors(True)
        self.template_list.itemDoubleClicked.connect(self._on_template_double_clicked)
        layout.addWidget(self.template_list)

        # Buttons
        button_layout = QHBoxLayout()

        # Left side buttons
        self.save_button = GlassButton("💾 Save Current", variant="success", size="medium")
        self.save_button.setToolTip("Save current conversation as a template")
        self.save_button.clicked.connect(self._save_template)
        self.save_button.setEnabled(bool(self.current_conversation))
        button_layout.addWidget(self.save_button)

        self.delete_button = GlassButton("🗑️ Delete", variant="danger", size="medium")
        self.delete_button.setToolTip("Delete selected template")
        self.delete_button.clicked.connect(self._delete_template)
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)

        button_layout.addStretch()

        # Right side buttons
        self.load_button = GlassButton("📂 Load", variant="primary", size="medium")
        self.load_button.setToolTip("Load selected template")
        self.load_button.clicked.connect(self._load_template)
        self.load_button.setEnabled(False)
        button_layout.addWidget(self.load_button)

        self.close_button = GlassButton("Close", variant="ghost", size="medium")
        self.close_button.clicked.connect(self.reject)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

        # Connect selection change
        self.template_list.itemSelectionChanged.connect(self._on_selection_changed)

    def _load_templates(self) -> None:
        """Load templates from disk."""
        self.template_list.clear()

        # Find all template files
        template_files = list(self.templates_dir.glob("*.json"))

        if not template_files:
            # Add placeholder
            item = QListWidgetItem("No templates saved yet")
            item.setFlags(Qt.NoItemFlags)  # Make it non-selectable
            self.template_list.addItem(item)
            return

        for template_file in sorted(template_files):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)

                # Extract metadata
                name = template_data.get('name', template_file.stem)
                description = template_data.get('description', '')
                turns = template_data.get('turns', [])
                turn_count = len(turns)

                # Create list item
                display_text = f"{name} ({turn_count} turns)"
                if description:
                    display_text += f"\n  {description}"

                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, str(template_file))
                self.template_list.addItem(item)

            except Exception as e:
                # Skip invalid template files
                continue

    def _save_template(self) -> None:
        """Save current conversation as a template."""
        if not self.current_conversation:
            QMessageBox.warning(
                self,
                "No Conversation",
                "No conversation to save as template."
            )
            return

        # Ask for template name
        name, ok = QInputDialog.getText(
            self,
            "Save Template",
            "Enter template name:",
            text=f"Template {len(list(self.templates_dir.glob('*.json'))) + 1}"
        )

        if not ok or not name.strip():
            return

        name = name.strip()

        # Ask for description (optional)
        description, ok = QInputDialog.getText(
            self,
            "Template Description",
            "Enter description (optional):",
        )

        if not ok:
            return

        # Create template data
        template_data = {
            'name': name,
            'description': description.strip() if description else '',
            'turns': self.current_conversation,
            'turn_count': len(self.current_conversation)
        }

        # Save to file
        filename = f"{name.replace(' ', '_').lower()}.json"
        filepath = self.templates_dir / filename

        # Check if exists
        if filepath.exists():
            reply = QMessageBox.question(
                self,
                "Overwrite Template",
                f"Template '{name}' already exists. Overwrite?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply != QMessageBox.Yes:
                return

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)

            QMessageBox.information(
                self,
                "Success",
                f"Template '{name}' saved successfully!"
            )

            # Reload templates
            self._load_templates()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save template:\n{str(e)}"
            )

    def _load_template(self) -> None:
        """Load selected template."""
        selected_items = self.template_list.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        template_file = item.data(Qt.UserRole)

        if not template_file:
            return

        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)

            turns = template_data.get('turns', [])

            if not turns:
                QMessageBox.warning(
                    self,
                    "Empty Template",
                    "This template contains no conversation turns."
                )
                return

            # Emit signal with template data
            self.template_selected.emit(turns)
            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Load Error",
                f"Failed to load template:\n{str(e)}"
            )

    def _delete_template(self) -> None:
        """Delete selected template."""
        selected_items = self.template_list.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        template_file = item.data(Qt.UserRole)

        if not template_file:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete Template",
            f"Are you sure you want to delete this template?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            Path(template_file).unlink()

            QMessageBox.information(
                self,
                "Success",
                "Template deleted successfully!"
            )

            # Reload templates
            self._load_templates()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Delete Error",
                f"Failed to delete template:\n{str(e)}"
            )

    def _on_template_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle template double-click (loads template)."""
        if item.data(Qt.UserRole):  # Only if it's a real template
            self._load_template()

    def _on_selection_changed(self) -> None:
        """Handle selection change in template list."""
        has_selection = bool(self.template_list.selectedItems())
        is_valid = False

        if has_selection:
            item = self.template_list.selectedItems()[0]
            is_valid = bool(item.data(Qt.UserRole))

        self.load_button.setEnabled(is_valid)
        self.delete_button.setEnabled(is_valid)

    def _apply_theme(self) -> None:
        """Apply glassmorphic theme styling."""
        theme = ThemeManager.instance().current_theme

        self.setStyleSheet(f"""
            QDialog {{
                background: {theme.background_primary};
            }}
            QLabel {{
                color: {theme.text_primary};
                background: transparent;
            }}
            QListWidget {{
                background: {theme.background_secondary};
                color: {theme.text_primary};
                border: 1px solid {theme.border_glass};
                border-radius: 6px;
                padding: 8px;
            }}
            QListWidget::item {{
                padding: 12px;
                border-radius: 4px;
            }}
            QListWidget::item:selected {{
                background: {theme.accent_primary};
                color: white;
            }}
            QListWidget::item:hover {{
                background: {theme.background_glass_hover};
            }}
        """)
