"""
SearchBar component - Modern search input with clear button and live filtering.

Provides a glassmorphic search bar with fuzzy filtering capabilities.
"""

from typing import Optional
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt5.QtGui import QFont

from ..themes import ThemeManager


class SearchBar(QWidget):
    """
    Glassmorphic search bar with live filtering and clear button.

    Features:
    - Live search with debouncing (300ms delay)
    - Clear button to reset search
    - Search icon indicator
    - Placeholder text
    - Theme-aware styling
    - Keyboard shortcuts (Escape to clear)

    Signals:
        search_changed: Emitted when search query changes (after debounce)
        search_cleared: Emitted when search is cleared
    """

    # Signal emitted when search query changes (debounced)
    search_changed = pyqtSignal(str)

    # Signal emitted when search is cleared
    search_cleared = pyqtSignal()

    def __init__(
        self,
        placeholder: str = "Search tools...",
        debounce_ms: int = 300,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize the search bar.

        Args:
            placeholder: Placeholder text to show when empty
            debounce_ms: Milliseconds to wait before emitting search_changed
            parent: Parent widget
        """
        super().__init__(parent)

        self.placeholder_text = placeholder
        self.debounce_delay = debounce_ms

        # Debounce timer for search input
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._emit_search_changed)

        # Setup UI
        self._setup_ui()
        self._apply_theme()

        # Connect to theme changes
        theme_manager = ThemeManager.instance()
        theme_manager.theme_changed.connect(self._apply_theme)

    def _setup_ui(self) -> None:
        """Setup the search bar's UI components."""
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Search icon
        self.search_icon = QLabel("🔍")
        self.search_icon.setFont(QFont("", 14))
        self.search_icon.setFixedSize(24, 24)
        self.search_icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.search_icon)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.placeholder_text)
        self.search_input.setFont(QFont("", 13))
        self.search_input.setMinimumHeight(40)
        self.search_input.setClearButtonEnabled(False)  # We'll use our own
        self.search_input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.search_input, stretch=1)

        # Clear button
        self.clear_button = QPushButton("✕")
        self.clear_button.setFont(QFont("", 12))
        self.clear_button.setFixedSize(32, 32)
        self.clear_button.setCursor(Qt.PointingHandCursor)
        self.clear_button.clicked.connect(self.clear_search)
        self.clear_button.setVisible(False)  # Hide until there's text
        layout.addWidget(self.clear_button)

        # Set overall height
        self.setFixedHeight(48)

    def _apply_theme(self) -> None:
        """Apply glassmorphic theme styling."""
        theme = ThemeManager.instance().current_theme

        # Container background
        self.setStyleSheet(f"""
            SearchBar {{
                background: {theme.surface_glass};
                border: 1px solid {theme.border_glass};
                border-radius: 8px;
                padding: 4px 8px;
            }}
        """)

        # Search icon
        self.search_icon.setStyleSheet(f"""
            QLabel {{
                color: {theme.text_tertiary};
                background: transparent;
            }}
        """)

        # Search input
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                color: {theme.text_primary};
                border: none;
                padding: 6px;
                font-size: 13px;
            }}
            QLineEdit::placeholder {{
                color: {theme.text_tertiary};
            }}
            QLineEdit:focus {{
                background: {theme.background_glass_hover};
                border-radius: 4px;
            }}
        """)

        # Clear button
        self.clear_button.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {theme.text_secondary};
                border: none;
                border-radius: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {theme.background_glass_hover};
                color: {theme.text_primary};
            }}
            QPushButton:pressed {{
                background: {theme.background_glass_active};
            }}
        """)

    def _on_text_changed(self, text: str) -> None:
        """
        Handle text change in search input.

        Args:
            text: Current search text
        """
        # Show/hide clear button
        self.clear_button.setVisible(bool(text))

        # Update search icon
        if text:
            self.search_icon.setText("🔎")  # Magnifying glass with dot (searching)
        else:
            self.search_icon.setText("🔍")  # Normal magnifying glass

        # Restart debounce timer
        self._debounce_timer.stop()
        self._debounce_timer.start(self.debounce_delay)

    def _emit_search_changed(self) -> None:
        """Emit search_changed signal after debounce delay."""
        query = self.search_input.text()
        self.search_changed.emit(query)

    def clear_search(self) -> None:
        """Clear the search input and emit search_cleared signal."""
        self.search_input.clear()
        self.search_input.setFocus()
        self.search_cleared.emit()

    def get_query(self) -> str:
        """
        Get the current search query.

        Returns:
            Current search text
        """
        return self.search_input.text()

    def set_query(self, query: str) -> None:
        """
        Set the search query programmatically.

        Args:
            query: Search text to set
        """
        self.search_input.setText(query)

    def focus_search(self) -> None:
        """Give focus to the search input."""
        self.search_input.setFocus()
        self.search_input.selectAll()

    def keyPressEvent(self, event) -> None:
        """
        Handle keyboard events.

        Args:
            event: Key event
        """
        # Escape key clears search
        if event.key() == Qt.Key_Escape:
            self.clear_search()
            event.accept()
        else:
            super().keyPressEvent(event)
