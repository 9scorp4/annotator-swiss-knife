"""
CategoryFilter component - Tab-style category selector for filtering tools.

Provides glassmorphic category tabs with tool count badges.
"""

from typing import List, Optional, Dict
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QFont

from ..themes import ThemeManager


class CategoryButton(QPushButton):
    """
    Individual category button with active state and count badge.

    Args:
        category_name: Display name of the category
        count: Number of tools in this category
        is_active: Whether this category is currently selected
        parent: Parent widget
    """

    def __init__(
        self,
        category_name: str,
        count: int = 0,
        is_active: bool = False,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self.category_name = category_name
        self.tool_count = count
        self.is_active_cat = is_active

        self._setup_ui()
        self._apply_theme()

        # Connect to theme changes
        theme_manager = ThemeManager.instance()
        theme_manager.theme_changed.connect(self._apply_theme)

        # Set cursor
        self.setCursor(Qt.PointingHandCursor)

    def _setup_ui(self) -> None:
        """Setup the button's UI."""
        # Create label with count badge
        if self.tool_count > 0:
            text = f"{self.category_name} ({self.tool_count})"
        else:
            text = self.category_name

        self.setText(text)
        cat_font = QFont()
        cat_font.setPointSize(12)
        cat_font.setWeight(QFont.Bold if self.is_active_cat else QFont.Normal)
        cat_font.setLetterSpacing(QFont.PercentageSpacing, 100)
        cat_font.setWordSpacing(0)
        self.setFont(cat_font)
        self.setMinimumHeight(32)  # Reduced from 36
        self.setMinimumWidth(80)

    def _apply_theme(self) -> None:
        """Apply glassmorphic theme styling."""
        theme = ThemeManager.instance().current_theme

        if self.is_active_cat:
            # Active state
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {theme.accent_primary};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background: {theme.accent_primary_glow};
                }}
            """)
        else:
            # Inactive state
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {theme.surface_glass};
                    color: {theme.text_secondary};
                    border: 1px solid {theme.border_subtle};
                    border-radius: 6px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background: {theme.surface_glass_elevated};
                    color: {theme.text_primary};
                    border: 1px solid {theme.border_glass};
                }}
                QPushButton:pressed {{
                    background: {theme.background_glass_active};
                }}
            """)

    def set_active(self, active: bool) -> None:
        """
        Set the active state of this category button.

        Args:
            active: Whether this category is active
        """
        self.is_active_cat = active
        cat_font = QFont()
        cat_font.setPointSize(12)
        cat_font.setWeight(QFont.Bold if active else QFont.Normal)
        cat_font.setLetterSpacing(QFont.PercentageSpacing, 100)
        cat_font.setWordSpacing(0)
        self.setFont(cat_font)
        self._apply_theme()

    def update_count(self, count: int) -> None:
        """
        Update the tool count badge.

        Args:
            count: New tool count
        """
        self.tool_count = count
        if count > 0:
            self.setText(f"{self.category_name} ({count})")
        else:
            self.setText(self.category_name)


class CategoryFilter(QWidget):
    """
    Glassmorphic category filter with tab-style buttons.

    Features:
    - Multiple category buttons with count badges
    - Active state highlighting
    - Emits signal when category changes
    - Theme-aware styling

    Signals:
        category_changed: Emitted when a category is selected with category name
    """

    # Signal emitted when category selection changes
    category_changed = pyqtSignal(str)

    def __init__(
        self,
        categories: List[str] = None,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize the category filter.

        Args:
            categories: List of category names (first is default)
            parent: Parent widget
        """
        super().__init__(parent)

        # Default categories if none provided
        if categories is None:
            categories = ["All", "Text", "JSON", "Conversation"]

        self.categories = categories
        self.current_category = categories[0] if categories else "All"
        self.category_buttons: Dict[str, CategoryButton] = {}

        # Setup UI
        self._setup_ui()
        self._apply_theme()

        # Connect to theme changes
        theme_manager = ThemeManager.instance()
        theme_manager.theme_changed.connect(self._apply_theme)

    def _setup_ui(self) -> None:
        """Setup the category filter's UI components."""
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Create button for each category
        for category in self.categories:
            is_active = (category == self.current_category)
            button = CategoryButton(category, count=0, is_active=is_active)
            button.clicked.connect(lambda checked, cat=category: self._on_category_clicked(cat))

            self.category_buttons[category] = button
            layout.addWidget(button)

        # Add stretch to push buttons to the left
        layout.addStretch()

        # Set overall height
        self.setFixedHeight(42)  # Reduced from 48

    def _apply_theme(self) -> None:
        """Apply glassmorphic theme styling."""
        theme = ThemeManager.instance().current_theme

        self.setStyleSheet(f"""
            CategoryFilter {{
                background: transparent;
            }}
        """)

    def _on_category_clicked(self, category: str) -> None:
        """
        Handle category button click.

        Args:
            category: Name of clicked category
        """
        if category == self.current_category:
            return  # Already selected

        # Update active states
        for cat_name, button in self.category_buttons.items():
            button.set_active(cat_name == category)

        # Update current category
        self.current_category = category

        # Emit signal
        self.category_changed.emit(category)

    def set_category(self, category: str) -> None:
        """
        Set the active category programmatically.

        Args:
            category: Category name to activate
        """
        if category not in self.category_buttons:
            return

        self._on_category_clicked(category)

    def get_current_category(self) -> str:
        """
        Get the currently selected category.

        Returns:
            Current category name
        """
        return self.current_category

    def update_category_count(self, category: str, count: int) -> None:
        """
        Update the tool count for a category.

        Args:
            category: Category name
            count: New tool count
        """
        if category in self.category_buttons:
            self.category_buttons[category].update_count(count)

    def update_all_counts(self, counts: Dict[str, int]) -> None:
        """
        Update tool counts for all categories.

        Args:
            counts: Dictionary mapping category names to counts
        """
        for category, count in counts.items():
            self.update_category_count(category, count)
