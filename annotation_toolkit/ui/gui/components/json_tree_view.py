"""
JsonTreeView component - Tree widget for hierarchical JSON visualization.

Provides expandable/collapsible tree view for JSON data with search and copy features.
"""

from typing import Any, Dict, List, Optional, Union
import json

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QMenu,
    QApplication,
    QHeaderView,
)
from PyQt5.QtGui import QFont, QColor, QCursor

from ..themes import ThemeManager
from ..utils.fonts import FontManager


class JsonTreeView(QTreeWidget):
    """
    Tree widget for displaying JSON data hierarchically.

    Features:
    - Expandable/collapsible nodes
    - Type indicators (object, array, string, number, boolean, null)
    - Search highlighting
    - Copy value context menu
    - Theme-aware styling
    - Keyboard navigation

    Signals:
        item_selected: Emitted when an item is selected with its path
    """

    # Signal emitted when item is selected (path, value)
    item_selected = pyqtSignal(str, object)

    # Type icons/indicators
    TYPE_INDICATORS = {
        "object": "{ }",
        "array": "[ ]",
        "string": '"abc"',
        "number": "123",
        "boolean": "T/F",
        "null": "null",
    }

    def __init__(self, parent: Optional[Any] = None):
        """
        Initialize the JSON tree view.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Store original JSON data
        self.json_data: Optional[Union[Dict, List]] = None

        # Setup tree widget
        self._setup_ui()

        # Apply theme
        self._apply_theme()

        # Connect to theme changes
        theme_manager = ThemeManager.instance()
        theme_manager.theme_changed.connect(self._apply_theme)

        # Connect selection signal
        self.itemClicked.connect(self._on_item_clicked)

        # Context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _setup_ui(self) -> None:
        """Setup the tree widget UI."""
        # Set columns
        self.setColumnCount(3)
        self.setHeaderLabels(["Key/Index", "Value", "Type"])

        # Set column widths
        header = self.header()
        header.setStretchLastSection(False)
        header.resizeSection(0, 200)  # Key
        header.resizeSection(1, 300)  # Value
        header.resizeSection(2, 80)   # Type

        # Enable sorting
        self.setSortingEnabled(False)  # Disable to maintain JSON order

        # Set alternating row colors
        self.setAlternatingRowColors(True)

        # Set selection mode
        self.setSelectionMode(QTreeWidget.SingleSelection)

        # Set font
        self.setFont(FontManager.get_code_font(size=10))

    def load_json(self, data: Union[Dict, List, str]) -> None:
        """
        Load JSON data into the tree view.

        Args:
            data: JSON data (dict, list, or JSON string)
        """
        # Clear existing items
        self.clear()

        # Parse JSON string if needed
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                # Add error item
                error_item = QTreeWidgetItem(self)
                error_item.setText(0, "Error")
                error_item.setText(1, f"Invalid JSON: {str(e)}")
                error_item.setText(2, "error")
                return

        # Store data
        self.json_data = data

        # Build tree
        if isinstance(data, dict):
            self._add_dict_items(self.invisibleRootItem(), data)
        elif isinstance(data, list):
            self._add_list_items(self.invisibleRootItem(), data)
        else:
            # Single value
            item = QTreeWidgetItem(self)
            item.setText(0, "root")
            self._set_value_columns(item, data)

        # Expand first level
        self.expandToDepth(0)

    def _add_dict_items(
        self, parent: QTreeWidgetItem, data: Dict, path: str = ""
    ) -> None:
        """
        Add dictionary items to the tree.

        Args:
            parent: Parent tree item
            data: Dictionary data
            path: Current path in JSON structure
        """
        for key, value in data.items():
            item = QTreeWidgetItem(parent)
            item.setText(0, str(key))

            # Store path
            current_path = f"{path}.{key}" if path else key
            item.setData(0, Qt.UserRole, current_path)

            # Add value based on type
            if isinstance(value, dict):
                item.setText(1, f"{{...}} ({len(value)} items)")
                item.setText(2, self.TYPE_INDICATORS["object"])
                self._add_dict_items(item, value, current_path)
            elif isinstance(value, list):
                item.setText(1, f"[...] ({len(value)} items)")
                item.setText(2, self.TYPE_INDICATORS["array"])
                self._add_list_items(item, value, current_path)
            else:
                self._set_value_columns(item, value)
                item.setData(0, Qt.UserRole + 1, value)  # Store actual value

    def _add_list_items(
        self, parent: QTreeWidgetItem, data: List, path: str = ""
    ) -> None:
        """
        Add list items to the tree.

        Args:
            parent: Parent tree item
            data: List data
            path: Current path in JSON structure
        """
        for index, value in enumerate(data):
            item = QTreeWidgetItem(parent)
            item.setText(0, f"[{index}]")

            # Store path
            current_path = f"{path}[{index}]" if path else f"[{index}]"
            item.setData(0, Qt.UserRole, current_path)

            # Add value based on type
            if isinstance(value, dict):
                item.setText(1, f"{{...}} ({len(value)} items)")
                item.setText(2, self.TYPE_INDICATORS["object"])
                self._add_dict_items(item, value, current_path)
            elif isinstance(value, list):
                item.setText(1, f"[...] ({len(value)} items)")
                item.setText(2, self.TYPE_INDICATORS["array"])
                self._add_list_items(item, value, current_path)
            else:
                self._set_value_columns(item, value)
                item.setData(0, Qt.UserRole + 1, value)  # Store actual value

    def _set_value_columns(self, item: QTreeWidgetItem, value: Any) -> None:
        """
        Set value and type columns for a tree item.

        Args:
            item: Tree widget item
            value: Value to display
        """
        if isinstance(value, str):
            # Truncate long strings
            display_value = value if len(value) <= 100 else value[:97] + "..."
            item.setText(1, f'"{display_value}"')
            item.setText(2, self.TYPE_INDICATORS["string"])
        elif isinstance(value, bool):
            item.setText(1, str(value).lower())
            item.setText(2, self.TYPE_INDICATORS["boolean"])
        elif isinstance(value, (int, float)):
            item.setText(1, str(value))
            item.setText(2, self.TYPE_INDICATORS["number"])
        elif value is None:
            item.setText(1, "null")
            item.setText(2, self.TYPE_INDICATORS["null"])
        else:
            item.setText(1, str(value))
            item.setText(2, "unknown")

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """
        Handle item click.

        Args:
            item: Clicked item
            column: Clicked column
        """
        path = item.data(0, Qt.UserRole)
        value = item.data(0, Qt.UserRole + 1)

        if path:
            self.item_selected.emit(path, value)

    def _show_context_menu(self, position) -> None:
        """
        Show context menu at position.

        Args:
            position: Menu position
        """
        item = self.itemAt(position)
        if not item:
            return

        menu = QMenu(self)

        # Copy value action
        copy_value_action = menu.addAction("Copy Value")
        copy_path_action = menu.addAction("Copy Path")
        menu.addSeparator()
        expand_all_action = menu.addAction("Expand All Children")
        collapse_all_action = menu.addAction("Collapse All Children")

        # Execute menu
        action = menu.exec_(self.viewport().mapToGlobal(position))

        if action == copy_value_action:
            self._copy_value(item)
        elif action == copy_path_action:
            self._copy_path(item)
        elif action == expand_all_action:
            self._expand_all_children(item)
        elif action == collapse_all_action:
            self._collapse_all_children(item)

    def _copy_value(self, item: QTreeWidgetItem) -> None:
        """
        Copy item value to clipboard.

        Args:
            item: Tree item
        """
        value = item.text(1)
        QApplication.clipboard().setText(value)

    def _copy_path(self, item: QTreeWidgetItem) -> None:
        """
        Copy item path to clipboard.

        Args:
            item: Tree item
        """
        path = item.data(0, Qt.UserRole)
        if path:
            QApplication.clipboard().setText(path)

    def _expand_all_children(self, item: QTreeWidgetItem) -> None:
        """
        Expand all children of an item.

        Args:
            item: Tree item
        """
        item.setExpanded(True)
        for i in range(item.childCount()):
            self._expand_all_children(item.child(i))

    def _collapse_all_children(self, item: QTreeWidgetItem) -> None:
        """
        Collapse all children of an item.

        Args:
            item: Tree item
        """
        for i in range(item.childCount()):
            self._collapse_all_children(item.child(i))
        item.setExpanded(False)

    def search(self, query: str, case_sensitive: bool = False) -> int:
        """
        Search for items matching query and highlight them.

        Args:
            query: Search query
            case_sensitive: Whether search is case-sensitive

        Returns:
            Number of matches found
        """
        if not query:
            self._clear_search_highlighting()
            return 0

        # Clear previous highlighting
        self._clear_search_highlighting()

        # Search and highlight
        matches = 0
        iterator = QTreeWidgetItemIterator(self)

        while iterator.value():
            item = iterator.value()

            # Check all columns
            match_found = False
            for col in range(self.columnCount()):
                text = item.text(col)

                if case_sensitive:
                    if query in text:
                        match_found = True
                        break
                else:
                    if query.lower() in text.lower():
                        match_found = True
                        break

            # Highlight match
            if match_found:
                self._highlight_item(item)
                matches += 1

                # Expand to show match
                parent = item.parent()
                while parent:
                    parent.setExpanded(True)
                    parent = parent.parent()

            iterator += 1

        return matches

    def _highlight_item(self, item: QTreeWidgetItem) -> None:
        """
        Highlight a tree item.

        Args:
            item: Tree item to highlight
        """
        theme = ThemeManager.instance().current_theme
        highlight_color = QColor(theme.accent_primary)
        highlight_color.setAlpha(50)  # Semi-transparent

        for col in range(self.columnCount()):
            item.setBackground(col, highlight_color)

    def _clear_search_highlighting(self) -> None:
        """Clear all search highlighting."""
        iterator = QTreeWidgetItemIterator(self)

        while iterator.value():
            item = iterator.value()
            for col in range(self.columnCount()):
                item.setBackground(col, QColor(0, 0, 0, 0))  # Transparent
            iterator += 1

    def expand_all(self) -> None:
        """Expand all tree items."""
        self.expandAll()

    def collapse_all(self) -> None:
        """Collapse all tree items."""
        self.collapseAll()

    def _apply_theme(self) -> None:
        """Apply glassmorphic theme styling."""
        theme = ThemeManager.instance().current_theme

        self.setStyleSheet(f"""
            QTreeWidget {{
                background: {theme.background_secondary};
                color: {theme.text_primary};
                border: 1px solid {theme.border_glass};
                border-radius: 6px;
                alternate-background-color: {theme.surface_glass};
            }}
            QTreeWidget::item {{
                padding: 4px;
                border: none;
            }}
            QTreeWidget::item:selected {{
                background: {theme.accent_primary};
                color: white;
            }}
            QTreeWidget::item:hover {{
                background: {theme.background_glass_hover};
            }}
            QTreeWidget::branch {{
                background: transparent;
            }}
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {{
                border-image: none;
                image: none;
            }}
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {{
                border-image: none;
                image: none;
            }}
            QHeaderView::section {{
                background: {theme.surface_glass};
                color: {theme.text_primary};
                padding: 6px;
                border: 1px solid {theme.border_subtle};
                font-weight: bold;
            }}
        """)
