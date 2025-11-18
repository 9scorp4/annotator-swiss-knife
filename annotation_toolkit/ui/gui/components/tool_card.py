"""
ToolCard component - Modern card-style button for tool selection.

Provides a glassmorphic card with tool icon, name, description, and keyboard shortcut.
"""

from typing import Optional
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QSize
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QFrame, QGraphicsDropShadowEffect
from PyQt5.QtGui import QFont, QColor, QCursor

from ..themes import ThemeManager


class ToolCard(QPushButton):
    """
    Glassmorphic card-style button for tool selection.

    Features:
    - Tool icon and name
    - Brief description
    - Keyboard shortcut badge
    - Hover animation with elevation
    - Theme-aware styling

    Args:
        tool_name: Display name of the tool
        description: Brief description of what the tool does
        icon: Emoji or unicode icon character
        shortcut: Keyboard shortcut text (e.g., "Ctrl+1")
        category: Tool category for filtering
        parent: Parent widget
    """

    # Signal emitted when card is clicked with tool name
    tool_selected = pyqtSignal(str)

    # Signal emitted when favorite is toggled
    favorite_toggled = pyqtSignal(str, bool)  # tool_name, is_favorite

    def __init__(
        self,
        tool_name: str,
        description: str,
        icon: str = "📄",
        shortcut: Optional[str] = None,
        category: str = "All",
        is_favorite: bool = False,
        usage_count: int = 0,
        last_used: Optional[str] = None,
        highlight: bool = False,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self.tool_name = tool_name
        self.description = description
        self.icon_char = icon
        self.shortcut_text = shortcut
        self.category = category
        self.is_favorite = is_favorite
        self.usage_count = usage_count
        self.last_used_time = last_used
        self.highlight = highlight  # For favorites section

        # Animation properties
        self._elevation = 0
        self._hover_animation: Optional[QPropertyAnimation] = None

        # Setup UI
        self._setup_ui()
        self._apply_theme()

        # Add drop shadow effect for depth
        self._setup_shadow_effect()

        # Connect to theme changes
        theme_manager = ThemeManager.instance()
        theme_manager.theme_changed.connect(self._apply_theme)

        # Set cursor
        self.setCursor(QCursor(Qt.PointingHandCursor))

        # Connect click signal
        self.clicked.connect(lambda: self.tool_selected.emit(self.tool_name))

    def _setup_ui(self) -> None:
        """Setup the card's UI components."""
        # Main layout with compact padding
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)  # Reduced from 20
        main_layout.setSpacing(10)  # Reduced from 12

        # Header: icon + shortcut badge + favorite button
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)  # Reduced from 12

        # Icon - compact size
        self.icon_label = QLabel(self.icon_char)
        icon_font = QFont()
        icon_font.setPointSize(36)  # Reduced from 42
        icon_font.setLetterSpacing(QFont.PercentageSpacing, 100)
        icon_font.setWordSpacing(0)
        self.icon_label.setFont(icon_font)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFixedSize(52, 52)  # Reduced from 64x64
        header_layout.addWidget(self.icon_label)

        header_layout.addStretch()

        # Favorite star button
        from PyQt5.QtWidgets import QToolButton
        self.star_button = QToolButton()
        self.star_button.setText("⭐" if self.is_favorite else "☆")
        star_font = QFont()
        star_font.setPointSize(16)
        star_font.setLetterSpacing(QFont.PercentageSpacing, 100)
        star_font.setWordSpacing(0)
        self.star_button.setFont(star_font)
        self.star_button.setFixedSize(24, 24)
        self.star_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.star_button.setToolTip("Add to favorites" if not self.is_favorite else "Remove from favorites")
        self.star_button.clicked.connect(self._toggle_favorite)
        header_layout.addWidget(self.star_button)

        # Shortcut badge (if provided)
        if self.shortcut_text:
            self.shortcut_badge = QLabel(self.shortcut_text)
            shortcut_font = QFont("monospace", 9)
            shortcut_font.setLetterSpacing(QFont.PercentageSpacing, 100)
            shortcut_font.setWordSpacing(0)
            self.shortcut_badge.setFont(shortcut_font)
            self.shortcut_badge.setAlignment(Qt.AlignCenter)
            self.shortcut_badge.setFixedHeight(20)
            self.shortcut_badge.setMinimumWidth(50)
            header_layout.addWidget(self.shortcut_badge)
        else:
            self.shortcut_badge = None

        main_layout.addLayout(header_layout)

        # Tool name - compact size
        self.name_label = QLabel(self.tool_name)
        name_font = QFont()
        name_font.setPointSize(14)  # Reduced from 16
        name_font.setWeight(QFont.Bold)
        name_font.setLetterSpacing(QFont.PercentageSpacing, 100)
        name_font.setWordSpacing(0)
        self.name_label.setFont(name_font)
        self.name_label.setWordWrap(True)
        self.name_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        main_layout.addWidget(self.name_label)

        # Description - compact size
        self.desc_label = QLabel(self.description)
        desc_font = QFont()
        desc_font.setPointSize(11)  # Reduced from 12
        desc_font.setLetterSpacing(QFont.PercentageSpacing, 100)
        desc_font.setWordSpacing(0)
        self.desc_label.setFont(desc_font)
        self.desc_label.setWordWrap(True)
        self.desc_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.desc_label.setMinimumHeight(45)  # Reduced from 50
        main_layout.addWidget(self.desc_label)

        main_layout.addStretch()

        # Usage statistics footer (if used)
        if self.usage_count > 0 or self.last_used_time:
            stats_layout = QHBoxLayout()
            stats_layout.setSpacing(8)

            if self.usage_count > 0:
                usage_label = QLabel(f"📊 {self.usage_count} uses")
                usage_font = QFont()
                usage_font.setPointSize(9)
                usage_font.setLetterSpacing(QFont.PercentageSpacing, 100)
                usage_font.setWordSpacing(0)
                usage_label.setFont(usage_font)
                stats_layout.addWidget(usage_label)

            if self.last_used_time:
                from datetime import datetime
                try:
                    last_used_dt = datetime.fromisoformat(self.last_used_time)
                    # Format as "2 days ago", "Today", etc.
                    time_diff = datetime.now() - last_used_dt
                    if time_diff.days == 0:
                        time_str = "Today"
                    elif time_diff.days == 1:
                        time_str = "Yesterday"
                    elif time_diff.days < 7:
                        time_str = f"{time_diff.days} days ago"
                    else:
                        time_str = last_used_dt.strftime("%b %d")

                    last_used_label = QLabel(f"🕒 {time_str}")
                    last_used_font = QFont()
                    last_used_font.setPointSize(9)
                    last_used_font.setLetterSpacing(QFont.PercentageSpacing, 100)
                    last_used_font.setWordSpacing(0)
                    last_used_label.setFont(last_used_font)
                    stats_layout.addWidget(last_used_label)
                except (ValueError, AttributeError):
                    pass

            stats_layout.addStretch()
            self.stats_widget = QWidget()
            self.stats_widget.setLayout(stats_layout)
            main_layout.addWidget(self.stats_widget)
        else:
            self.stats_widget = None

        # Set compact size for better space utilization
        self.setFixedSize(QSize(340, 240))  # Reduced from 400x280 for more compact layout

    def _setup_shadow_effect(self) -> None:
        """Add a subtle drop shadow effect to the card."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20 if self.highlight else 15)
        shadow.setXOffset(0)
        shadow.setYOffset(4 if self.highlight else 2)
        shadow.setColor(QColor(0, 0, 0, 40 if self.highlight else 30))
        self.setGraphicsEffect(shadow)

    def _toggle_favorite(self) -> None:
        """Toggle favorite status and emit signal."""
        # Stop event propagation to prevent card click
        self.is_favorite = not self.is_favorite
        self.star_button.setText("⭐" if self.is_favorite else "☆")
        self.star_button.setToolTip("Remove from favorites" if self.is_favorite else "Add to favorites")
        self.favorite_toggled.emit(self.tool_name, self.is_favorite)

    def set_favorite(self, is_favorite: bool) -> None:
        """
        Set favorite status programmatically.

        Args:
            is_favorite: True to mark as favorite
        """
        self.is_favorite = is_favorite
        self.star_button.setText("⭐" if is_favorite else "☆")
        self.star_button.setToolTip("Remove from favorites" if is_favorite else "Add to favorites")

    def _apply_theme(self) -> None:
        """Apply glassmorphic theme styling with enhanced visual effects."""
        theme = ThemeManager.instance().current_theme

        # Enhanced card background with better borders and shadows
        # Highlight favorites with accent border
        border_color = theme.accent_primary if self.highlight else theme.border_glass
        border_width = "2px" if self.highlight else "1px"

        base_style = f"""
            ToolCard {{
                background: {theme.surface_glass};
                border: {border_width} solid {border_color};
                border-radius: 16px;
                text-align: left;
                padding: 0px;
            }}
            ToolCard:hover {{
                background: {theme.surface_glass_elevated};
                border: 2px solid {theme.accent_primary};
            }}
            ToolCard:pressed {{
                background: {theme.background_glass_active};
                border: 2px solid {theme.accent_primary};
            }}
        """

        self.setStyleSheet(base_style)

        # Name label color
        self.name_label.setStyleSheet(f"color: {theme.text_primary}; background: transparent;")

        # Description color
        self.desc_label.setStyleSheet(f"color: {theme.text_secondary}; background: transparent;")

        # Icon color
        self.icon_label.setStyleSheet(f"color: {theme.accent_primary}; background: transparent;")

        # Star button
        self.star_button.setStyleSheet(f"""
            QToolButton {{
                background: transparent;
                border: none;
                color: {theme.warning_color if self.is_favorite else theme.text_tertiary};
            }}
            QToolButton:hover {{
                color: {theme.warning_color};
            }}
        """)

        # Shortcut badge
        if self.shortcut_badge:
            self.shortcut_badge.setStyleSheet(f"""
                QLabel {{
                    background: {theme.background_glass};
                    color: {theme.text_tertiary};
                    border: 1px solid {theme.border_subtle};
                    border-radius: 4px;
                    padding: 2px 6px;
                }}
            """)

        # Stats widget
        if self.stats_widget:
            self.stats_widget.setStyleSheet(f"""
                QLabel {{
                    color: {theme.text_tertiary};
                    background: transparent;
                }}
            """)

    def enterEvent(self, event) -> None:
        """Animate on mouse enter - enhance shadow."""
        super().enterEvent(event)
        self._animate_elevation(8)

    def leaveEvent(self, event) -> None:
        """Animate on mouse leave - reduce shadow."""
        super().leaveEvent(event)
        self._animate_elevation(0)

    def _animate_elevation(self, target_elevation: int) -> None:
        """
        Animate the card's shadow to simulate elevation change.

        Args:
            target_elevation: Target elevation level (0-10)
        """
        self._elevation = target_elevation

        # Update shadow effect for elevation
        if self.graphicsEffect():
            shadow = self.graphicsEffect()
            if target_elevation > 0:
                # Hover state - larger shadow
                shadow.setBlurRadius(30)
                shadow.setYOffset(8)
                shadow.setColor(QColor(0, 0, 0, 60))
            else:
                # Normal state
                shadow.setBlurRadius(20 if self.highlight else 15)
                shadow.setYOffset(4 if self.highlight else 2)
                shadow.setColor(QColor(0, 0, 0, 40 if self.highlight else 30))

    def sizeHint(self) -> QSize:
        """Return the preferred size of the card."""
        return QSize(340, 260)

    def matches_search(self, query: str) -> bool:
        """
        Check if this card matches a search query.

        Args:
            query: Search query string (case-insensitive)

        Returns:
            True if the tool name or description contains the query
        """
        query_lower = query.lower()
        return (
            query_lower in self.tool_name.lower() or
            query_lower in self.description.lower()
        )

    def matches_category(self, category: str) -> bool:
        """
        Check if this card matches a category filter.

        Args:
            category: Category name ("All" matches everything)

        Returns:
            True if the card belongs to this category
        """
        return category == "All" or self.category == category
