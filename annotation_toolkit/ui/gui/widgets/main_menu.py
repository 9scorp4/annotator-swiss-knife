"""
Main menu widget for the annotation swiss knife GUI.

Modern card-based grid layout with search, categories, and recent tools.
"""

from typing import Dict, List, Optional, Set
from collections import deque
from datetime import datetime

from PyQt5.QtCore import Qt, QUrl, QSettings, QPropertyAnimation, QEasingCurve, QSize, QSequentialAnimationGroup, QParallelAnimationGroup, QTimer, pyqtProperty
from PyQt5.QtGui import QFont, QDesktopServices, QPixmap, QPainter, QTransform
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QFrame,
    QScrollArea,
    QComboBox,
    QGraphicsOpacityEffect,
)
from pathlib import Path

from ....core.base import AnnotationTool
from ..components import ToolCard, SearchBar, CategoryFilter, GlassButton
from ..themes import ThemeManager


class AnimatedLogoLabel(QLabel):
    """Custom QLabel with scale animation support."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._scale = 1.0

    @pyqtProperty(float)
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value
        # Apply scale transform
        transform = QTransform()
        transform.scale(value, value)
        self.setTransform(transform)

    def setTransform(self, transform):
        """Apply transform to the pixmap."""
        if self.pixmap() and not self.pixmap().isNull():
            original_pixmap = self.property("original_pixmap")
            if original_pixmap:
                # Scale the original pixmap
                size = original_pixmap.size()
                new_size = QSize(int(size.width() * self._scale), int(size.height() * self._scale))
                scaled = original_pixmap.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                super().setPixmap(scaled)

    def setPixmap(self, pixmap):
        """Override to store original pixmap."""
        self.setProperty("original_pixmap", pixmap)
        super().setPixmap(pixmap)


class MainMenuWidget(QWidget):
    """
    Modern main menu with card grid, search, and category filtering.

    Features:
    - Card-based grid layout (2-3 columns responsive)
    - Search bar with live filtering
    - Category tabs for tool organization
    - Recent tools section (last 3 used)
    - Keyboard shortcuts displayed on cards
    - Glassmorphic modern styling
    """

    # Tool metadata with categories, icons, and shortcuts
    TOOL_METADATA = {
        "URL Dictionary to Clickables": {
            "category": "Text",
            "icon": "📝",
            "shortcut": "Ctrl+1",
            "description": "Convert JSON dictionaries to formatted bullet lists with clickable links"
        },
        "JSON Visualizer": {
            "category": "JSON",
            "icon": "🔍",
            "shortcut": "Ctrl+2",
            "description": "Parse and visualize JSON data with conversation formatting and search"
        },
        "Text Cleaner": {
            "category": "Text",
            "icon": "🧹",
            "shortcut": "Ctrl+3",
            "description": "Clean text from markdown, JSON, and code artifacts for better readability"
        },
        "Conversation Generator": {
            "category": "Conversation",
            "icon": "💬",
            "shortcut": "Ctrl+4",
            "description": "Generate AI conversation JSON by copy-pasting prompts and responses (max 20 turns)"
        },
        "Text Collector": {
            "category": "Text",
            "icon": "📋",
            "shortcut": "Ctrl+5",
            "description": "Collect and organize text snippets from multiple fields into structured output"
        },
    }

    def __init__(self, tools: Dict[str, AnnotationTool], main_app):
        """
        Initialize the main menu widget.

        Args:
            tools: Dictionary of available tools
            main_app: The main application instance
        """
        super().__init__()

        self.tools = tools
        self.main_app = main_app

        # Recent tools tracking (max 3)
        self.recent_tools: deque = deque(maxlen=3)
        self._load_recent_tools()

        # Usage statistics tracking
        self.usage_counts: Dict[str, int] = {}
        self.last_used: Dict[str, str] = {}  # ISO format timestamps
        self._load_usage_statistics()

        # Favorite tools tracking
        self.favorite_tools: Set[str] = set()
        self._load_favorite_tools()

        # All tool cards
        self.tool_cards: List[ToolCard] = []

        # Current filter state
        self.current_search = ""
        self.current_category = "All"
        self.current_sort = "alphabetical"  # alphabetical, most_used, recently_used, favorites

        # Setup UI
        self._init_ui()

        # Apply theme
        self._apply_theme()

        # Connect to theme changes
        theme_manager = ThemeManager.instance()
        theme_manager.theme_changed.connect(self._apply_theme)

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        # Main scroll area for the entire menu
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Main content widget
        content = QWidget()
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(20, 20, 20, 20)  # Reduced from 30
        main_layout.setSpacing(18)  # Reduced from 24

        # ===== HERO BANNER =====
        hero_frame = QFrame()
        hero_frame.setObjectName("heroBanner")
        hero_frame.setMinimumHeight(220)

        # Add dramatic shadow to hero banner
        from PyQt5.QtWidgets import QGraphicsDropShadowEffect
        from PyQt5.QtGui import QColor
        hero_shadow = QGraphicsDropShadowEffect()
        hero_shadow.setBlurRadius(30)
        hero_shadow.setXOffset(0)
        hero_shadow.setYOffset(4)
        hero_shadow.setColor(QColor(0, 0, 0, 60))
        hero_frame.setGraphicsEffect(hero_shadow)

        hero_layout = QVBoxLayout(hero_frame)
        hero_layout.setContentsMargins(40, 30, 40, 30)
        hero_layout.setSpacing(16)

        # SVG Logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)

        # Load and render SVG logo
        logo_path = Path(__file__).parent.parent / "assets" / "logo.svg"
        if logo_path.exists():
            # Render SVG to pixmap with correct aspect ratio
            renderer = QSvgRenderer(str(logo_path))
            # Use SVG's native aspect ratio (280:160 = 1.75:1)
            pixmap = QPixmap(QSize(700, 400))
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()

            # Scale to fit nicely while preserving aspect ratio
            scaled_pixmap = pixmap.scaled(700, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)

            # Add subtle static glow
            from PyQt5.QtWidgets import QGraphicsDropShadowEffect
            from PyQt5.QtGui import QColor
            theme = ThemeManager.instance().current_theme
            logo_glow = QGraphicsDropShadowEffect()
            logo_glow.setBlurRadius(20)
            logo_glow.setXOffset(0)
            logo_glow.setYOffset(0)
            if theme.is_dark:
                logo_glow.setColor(QColor(99, 179, 237, 60))
            else:
                logo_glow.setColor(QColor(66, 153, 225, 40))
            logo_label.setGraphicsEffect(logo_glow)
        else:
            # Fallback to text if SVG not found
            logo_label.setText("ANNOTATION SWISS KNIFE")
            logo_font = QFont()
            logo_font.setPointSize(42)
            logo_font.setWeight(QFont.ExtraBold)
            logo_label.setFont(logo_font)

        self.logo_label = logo_label
        hero_layout.addWidget(logo_label)

        # Tagline/subtitle
        subtitle_label = QLabel("Professional Data Annotation Toolkit")
        subtitle_font = QFont()
        subtitle_font.setPointSize(14)
        subtitle_font.setWeight(QFont.Medium)
        subtitle_font.setLetterSpacing(QFont.PercentageSpacing, 102)
        subtitle_font.setWordSpacing(0)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("margin-top: 8px;")
        self.subtitle_label = subtitle_label
        hero_layout.addWidget(subtitle_label)

        main_layout.addWidget(hero_frame)

        # ===== SEARCH BAR =====
        self.search_bar = SearchBar(placeholder="Search tools...")
        self.search_bar.search_changed.connect(self._on_search_changed)
        self.search_bar.search_cleared.connect(self._on_search_cleared)
        main_layout.addWidget(self.search_bar)

        # ===== SORT & FILTER OPTIONS =====
        options_layout = QHBoxLayout()
        options_layout.setSpacing(12)

        # Sort label
        sort_label = QLabel("Sort by:")
        sort_font = QFont()
        sort_font.setPointSize(13)
        sort_font.setLetterSpacing(QFont.PercentageSpacing, 100)
        sort_font.setWordSpacing(0)
        sort_label.setFont(sort_font)
        options_layout.addWidget(sort_label)

        # Sort dropdown
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "Alphabetical",
            "Most Used",
            "Recently Used",
            "Favorites First"
        ])
        self.sort_combo.setMinimumWidth(150)
        self.sort_combo.currentTextChanged.connect(self._on_sort_changed)
        options_layout.addWidget(self.sort_combo)

        options_layout.addStretch()
        main_layout.addLayout(options_layout)

        # ===== CATEGORY FILTER =====
        categories = ["All", "Text", "JSON", "Conversation", "⭐ Favorites"]
        self.category_filter = CategoryFilter(categories=categories)
        self.category_filter.category_changed.connect(self._on_category_changed)
        main_layout.addWidget(self.category_filter)

        # Update category counts
        self._update_category_counts()

        # ===== FAVORITES SECTION =====
        favorites = [name for name in self.tools.keys() if name in self.favorite_tools]
        if favorites:
            fav_header = QLabel("⭐ Favorite Tools")
            fav_header_font = QFont()
            fav_header_font.setPointSize(16)  # Reduced from 20
            fav_header_font.setWeight(QFont.Bold)
            fav_header_font.setLetterSpacing(QFont.PercentageSpacing, 100)
            fav_header_font.setWordSpacing(0)
            fav_header.setFont(fav_header_font)
            fav_header.setStyleSheet("padding: 16px 0 10px 0;")  # Reduced padding
            main_layout.addWidget(fav_header)

            self.favorites_grid = QGridLayout()
            self.favorites_grid.setSpacing(14)  # Reduced from 20
            self.favorites_grid.setContentsMargins(0, 0, 0, 16)  # Reduced from 20
            main_layout.addLayout(self.favorites_grid)

            # Populate favorites
            self._populate_favorites()

        # ===== RECENT TOOLS SECTION =====
        if self.recent_tools and not favorites:  # Only show if no favorites
            recent_header = QLabel("📌 Recently Used")
            recent_header_font = QFont()
            recent_header_font.setPointSize(16)  # Reduced from 20
            recent_header_font.setWeight(QFont.Bold)
            recent_header_font.setLetterSpacing(QFont.PercentageSpacing, 100)
            recent_header_font.setWordSpacing(0)
            recent_header.setFont(recent_header_font)
            recent_header.setStyleSheet("padding: 16px 0 10px 0;")  # Reduced padding
            main_layout.addWidget(recent_header)

            self.recent_grid = QGridLayout()
            self.recent_grid.setSpacing(14)  # Reduced from 20
            self.recent_grid.setContentsMargins(0, 0, 0, 16)  # Reduced from 20
            main_layout.addLayout(self.recent_grid)

            # Populate recent tools
            self._populate_recent_tools()

        # ===== ALL TOOLS SECTION =====
        all_tools_header = QLabel("🛠️ All Tools")
        all_tools_header_font = QFont()
        all_tools_header_font.setPointSize(16)  # Reduced from 20
        all_tools_header_font.setWeight(QFont.Bold)
        all_tools_header_font.setLetterSpacing(QFont.PercentageSpacing, 100)
        all_tools_header_font.setWordSpacing(0)
        all_tools_header.setFont(all_tools_header_font)
        all_tools_header.setStyleSheet("padding: 16px 0 10px 0;")  # Reduced padding
        main_layout.addWidget(all_tools_header)

        # Tools grid (compact layout)
        self.tools_grid = QGridLayout()
        self.tools_grid.setSpacing(14)  # Reduced from 20
        self.tools_grid.setContentsMargins(0, 0, 0, 16)  # Reduced from 20
        self.tools_grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        main_layout.addLayout(self.tools_grid)

        # Populate tools grid
        self._populate_tools_grid()

        # Add stretch to push content to top
        main_layout.addStretch()

        # ===== FOOTER =====
        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(12)

        # Copyright
        copyright_label = QLabel("© 2025 Nicolas Arias Garcia")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_font = QFont()
        copyright_font.setPointSize(12)
        copyright_font.setLetterSpacing(QFont.PercentageSpacing, 100)  # Normal spacing
        copyright_font.setWordSpacing(0)  # No extra word spacing
        copyright_label.setFont(copyright_font)
        copyright_label.setStyleSheet("letter-spacing: 0px;")  # Ensure no letter spacing
        footer_layout.addWidget(copyright_label)

        # GitHub button
        github_layout = QHBoxLayout()
        github_layout.addStretch()

        github_button = GlassButton("🚀 Visit GitHub Profile", variant="primary", size="small")
        github_button.setToolTip("Check out my GitHub profile: @9scorp4")
        github_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/9scorp4")))
        github_layout.addWidget(github_button)

        github_layout.addStretch()
        footer_layout.addLayout(github_layout)

        main_layout.addLayout(footer_layout)

        # Set content widget to scroll area
        scroll.setWidget(content)

        # Main layout for this widget
        widget_layout = QVBoxLayout(self)
        widget_layout.setContentsMargins(0, 0, 0, 0)
        widget_layout.addWidget(scroll)

    def _populate_favorites(self) -> None:
        """Populate the favorites grid."""
        # Clear existing
        self._clear_layout(self.favorites_grid)

        # Get favorite tools
        favorites = [name for name in self.tools.keys() if name in self.favorite_tools]

        # Add favorite tool cards (3 per row)
        row, col = 0, 0
        max_cols = 3
        for tool_name in favorites:
            if tool_name in self.tools:
                card = self._create_tool_card(tool_name, highlight=True)
                self.favorites_grid.addWidget(card, row, col)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

    def _populate_recent_tools(self) -> None:
        """Populate the recent tools grid."""
        # Clear existing
        self._clear_layout(self.recent_grid)

        # Add recent tool cards (3 per row)
        row, col = 0, 0
        max_cols = 3
        for tool_name in self.recent_tools:
            if tool_name in self.tools:
                card = self._create_tool_card(tool_name)
                self.recent_grid.addWidget(card, row, col)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

    def _populate_tools_grid(self) -> None:
        """Populate the main tools grid with all tools."""
        # Clear existing cards
        self.tool_cards.clear()
        self._clear_layout(self.tools_grid)

        # Get sorted tool names
        tool_names = self._get_sorted_tool_names()

        # Create card for each tool
        row, col = 0, 0
        max_cols = 3  # 3 columns to fill horizontal space

        for tool_name in tool_names:
            card = self._create_tool_card(tool_name)
            self.tool_cards.append(card)

            self.tools_grid.addWidget(card, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        # Re-apply filters to show/hide cards
        self._apply_filters()

    def _get_sorted_tool_names(self) -> List[str]:
        """
        Get tool names sorted by current sort mode.

        Returns:
            List of sorted tool names
        """
        tool_names = list(self.tools.keys())

        if self.current_sort == "alphabetical":
            return sorted(tool_names)

        elif self.current_sort == "most_used":
            # Sort by usage count descending, then alphabetically
            return sorted(
                tool_names,
                key=lambda name: (-self.usage_counts.get(name, 0), name)
            )

        elif self.current_sort == "recently_used":
            # Sort by last used descending, then alphabetically
            def sort_key(name):
                last_used_str = self.last_used.get(name)
                if last_used_str:
                    try:
                        return (datetime.fromisoformat(last_used_str), name)
                    except (ValueError, AttributeError):
                        pass
                # Never used - put at end
                return (datetime.min, name)

            return sorted(tool_names, key=sort_key, reverse=True)

        elif self.current_sort == "favorites":
            # Favorites first, then alphabetically
            return sorted(
                tool_names,
                key=lambda name: (name not in self.favorite_tools, name)
            )

        else:
            return sorted(tool_names)

    def _create_tool_card(self, tool_name: str, highlight: bool = False) -> ToolCard:
        """
        Create a tool card for the given tool.

        Args:
            tool_name: Name of the tool
            highlight: Whether to highlight this card (for favorites section)

        Returns:
            ToolCard widget
        """
        # Get metadata or use defaults
        metadata = self.TOOL_METADATA.get(tool_name, {
            "category": "All",
            "icon": "📄",
            "shortcut": None,
            "description": self.tools[tool_name].description
        })

        # Get usage statistics
        usage_count = self.usage_counts.get(tool_name, 0)
        last_used = self.last_used.get(tool_name)
        is_favorite = tool_name in self.favorite_tools

        # Create card
        card = ToolCard(
            tool_name=tool_name,
            description=metadata["description"],
            icon=metadata["icon"],
            shortcut=metadata["shortcut"],
            category=metadata["category"],
            is_favorite=is_favorite,
            usage_count=usage_count,
            last_used=last_used,
            highlight=highlight
        )

        # Connect signals
        card.tool_selected.connect(self._on_tool_selected)
        card.favorite_toggled.connect(self._on_favorite_toggled)

        return card

    def _on_tool_selected(self, tool_name: str) -> None:
        """
        Handle tool selection.

        Args:
            tool_name: Name of selected tool
        """
        # Update usage statistics
        self.usage_counts[tool_name] = self.usage_counts.get(tool_name, 0) + 1
        self.last_used[tool_name] = datetime.now().isoformat()
        self._save_usage_statistics()

        # Add to recent tools
        self._add_recent_tool(tool_name)

        # Switch to tool in main app
        self.main_app.switch_to_tool(tool_name)

    def _on_favorite_toggled(self, tool_name: str, is_favorite: bool) -> None:
        """
        Handle favorite toggle.

        Args:
            tool_name: Name of tool
            is_favorite: True if now favorited
        """
        if is_favorite:
            self.favorite_tools.add(tool_name)
        else:
            self.favorite_tools.discard(tool_name)

        self._save_favorite_tools()
        self._update_category_counts()

    def _on_sort_changed(self, sort_text: str) -> None:
        """
        Handle sort option change.

        Args:
            sort_text: Display text of selected sort option
        """
        # Map display text to sort mode
        sort_map = {
            "Alphabetical": "alphabetical",
            "Most Used": "most_used",
            "Recently Used": "recently_used",
            "Favorites First": "favorites"
        }

        self.current_sort = sort_map.get(sort_text, "alphabetical")
        self._populate_tools_grid()

    def _add_recent_tool(self, tool_name: str) -> None:
        """
        Add a tool to recent tools list.

        Args:
            tool_name: Name of tool to add
        """
        # Remove if already exists (to move to front)
        if tool_name in self.recent_tools:
            self.recent_tools.remove(tool_name)

        # Add to front
        self.recent_tools.append(tool_name)

        # Save to settings
        self._save_recent_tools()

    def _load_recent_tools(self) -> None:
        """Load recent tools from QSettings."""
        settings = QSettings("AnnotationToolkit", "GUI")
        recent = settings.value("recent_tools", [])
        if isinstance(recent, list):
            self.recent_tools = deque(recent, maxlen=3)

    def _save_recent_tools(self) -> None:
        """Save recent tools to QSettings."""
        settings = QSettings("AnnotationToolkit", "GUI")
        settings.setValue("recent_tools", list(self.recent_tools))

    def _load_usage_statistics(self) -> None:
        """Load usage statistics from QSettings."""
        settings = QSettings("AnnotationToolkit", "GUI")
        self.usage_counts = settings.value("usage_counts", {})
        self.last_used = settings.value("last_used", {})

        # Ensure dicts (Qt sometimes returns wrong type)
        if not isinstance(self.usage_counts, dict):
            self.usage_counts = {}
        if not isinstance(self.last_used, dict):
            self.last_used = {}

    def _save_usage_statistics(self) -> None:
        """Save usage statistics to QSettings."""
        settings = QSettings("AnnotationToolkit", "GUI")
        settings.setValue("usage_counts", self.usage_counts)
        settings.setValue("last_used", self.last_used)

    def _load_favorite_tools(self) -> None:
        """Load favorite tools from QSettings."""
        settings = QSettings("AnnotationToolkit", "GUI")
        favorites = settings.value("favorite_tools", [])
        if isinstance(favorites, list):
            self.favorite_tools = set(favorites)
        else:
            self.favorite_tools = set()

    def _save_favorite_tools(self) -> None:
        """Save favorite tools to QSettings."""
        settings = QSettings("AnnotationToolkit", "GUI")
        settings.setValue("favorite_tools", list(self.favorite_tools))

    def _on_search_changed(self, query: str) -> None:
        """
        Handle search query change.

        Args:
            query: Search query string
        """
        self.current_search = query.lower()
        self._apply_filters()

    def _on_search_cleared(self) -> None:
        """Handle search cleared."""
        self.current_search = ""
        self._apply_filters()

    def _on_category_changed(self, category: str) -> None:
        """
        Handle category filter change.

        Args:
            category: Selected category name
        """
        self.current_category = category
        self._apply_filters()

    def _apply_filters(self) -> None:
        """Apply current search and category filters to tool cards."""
        visible_count = 0
        visible_cards = []

        for card in self.tool_cards:
            # Check search match
            search_match = (
                not self.current_search or
                card.matches_search(self.current_search)
            )

            # Check category match
            if self.current_category == "⭐ Favorites":
                category_match = card.is_favorite
            else:
                category_match = card.matches_category(self.current_category)

            # Determine if card should be visible
            should_show = search_match and category_match

            if should_show:
                visible_cards.append(card)
                visible_count += 1

        # Remove all cards from grid
        for i in reversed(range(self.tools_grid.count())):
            item = self.tools_grid.itemAt(i)
            if item.widget():
                self.tools_grid.removeItem(item)

        # Re-add only visible cards to grid, flowing from left to right
        max_cols = 3
        row, col = 0, 0
        for card in visible_cards:
            card.setVisible(True)
            self.tools_grid.addWidget(card, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        # Hide cards that don't match filters
        for card in self.tool_cards:
            if card not in visible_cards:
                card.setVisible(False)

        # Update category counts based on current search
        self._update_category_counts()

    def _update_category_counts(self) -> None:
        """Update tool counts for each category."""
        counts = {"All": 0, "Text": 0, "JSON": 0, "Conversation": 0, "⭐ Favorites": 0}

        for card in self.tool_cards:
            # Count if matches current search
            if not self.current_search or card.matches_search(self.current_search):
                counts["All"] += 1
                if card.category in counts:
                    counts[card.category] += 1
                if card.is_favorite:
                    counts["⭐ Favorites"] += 1

        # Update category filter counts
        self.category_filter.update_all_counts(counts)

    def _animate_title_entrance(self) -> None:
        """Add DRAMATIC fade-in, scale, and bounce animation for the logo (2000s style!)"""
        if hasattr(self, 'logo_label'):
            # Create opacity effect for logo
            logo_opacity = QGraphicsOpacityEffect()
            self.logo_label.setGraphicsEffect(logo_opacity)

            # Create animation group for simultaneous effects
            self.entrance_group = QParallelAnimationGroup()

            # 1. FADE IN animation
            fade_anim = QPropertyAnimation(logo_opacity, b"opacity")
            fade_anim.setDuration(1500)  # 1.5 seconds - very visible
            fade_anim.setStartValue(0.0)
            fade_anim.setEndValue(1.0)
            fade_anim.setEasingCurve(QEasingCurve.OutCubic)

            # 2. SCALE/ZOOM animation (starts small, grows to normal size with bounce)
            scale_anim = QPropertyAnimation(self.logo_label, b"scale")
            scale_anim.setDuration(1500)  # 1.5 seconds
            scale_anim.setStartValue(0.3)  # Start at 30% size
            scale_anim.setEndValue(1.0)   # End at 100% size
            scale_anim.setEasingCurve(QEasingCurve.OutBack)  # Bounce/overshoot effect!

            # Add both animations to group
            self.entrance_group.addAnimation(fade_anim)
            self.entrance_group.addAnimation(scale_anim)

            # Start the dramatic entrance!
            self.entrance_group.start()

            # After entrance, start pulsing effect
            self.entrance_group.finished.connect(self._start_pulse_animation)

    def _start_pulse_animation(self) -> None:
        """Start continuous subtle pulsing/breathing effect (2000s nostalgia!)"""
        if hasattr(self, 'logo_label'):
            # Add glow effect first
            self._add_logo_glow()

            # Create pulsing scale animation (subtle breathing)
            self.pulse_anim = QPropertyAnimation(self.logo_label, b"scale")
            self.pulse_anim.setDuration(2000)  # 2 second pulse cycle
            self.pulse_anim.setStartValue(1.0)
            self.pulse_anim.setKeyValueAt(0.5, 1.05)  # Grow to 105% at midpoint
            self.pulse_anim.setEndValue(1.0)  # Back to 100%
            self.pulse_anim.setEasingCurve(QEasingCurve.InOutSine)  # Smooth breathing
            self.pulse_anim.setLoopCount(-1)  # Loop forever!

            # Start pulsing
            self.pulse_anim.start()

    def _add_logo_glow(self) -> None:
        """Add glowing effect to logo (2000s WordArt style!)"""
        if hasattr(self, 'logo_label'):
            from PyQt5.QtWidgets import QGraphicsDropShadowEffect
            from PyQt5.QtGui import QColor

            theme = ThemeManager.instance().current_theme
            logo_glow = QGraphicsDropShadowEffect()
            logo_glow.setBlurRadius(30)  # Stronger glow
            logo_glow.setXOffset(0)
            logo_glow.setYOffset(0)

            if theme.is_dark:
                logo_glow.setColor(QColor(99, 179, 237, 100))  # Brighter glow
            else:
                logo_glow.setColor(QColor(66, 153, 225, 80))

            self.logo_label.setGraphicsEffect(logo_glow)

    def _clear_layout(self, layout: QGridLayout) -> None:
        """
        Clear all widgets from a layout.

        Args:
            layout: Layout to clear
        """
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _apply_theme(self) -> None:
        """Apply glassmorphic theme styling."""
        theme = ThemeManager.instance().current_theme

        # Style subtitle
        if hasattr(self, 'subtitle_label'):
            self.subtitle_label.setStyleSheet(f"""
                color: {theme.text_secondary};
                background: transparent;
            """)

        # Main widget background with hero banner styling
        self.setStyleSheet(f"""
            MainMenuWidget {{
                background: {theme.background_primary};
            }}
            QFrame#heroBanner {{
                background: {theme.gradient_glass_bg};
                border: 1px solid {theme.border_glass};
                border-radius: 16px;
                margin-bottom: 12px;
            }}
            QLabel {{
                color: {theme.text_primary};
                background: transparent;
            }}
            QScrollArea {{
                background: {theme.background_primary};
                border: none;
            }}
            QScrollArea > QWidget > QWidget {{
                background: {theme.background_primary};
            }}
            QWidget {{
                background: transparent;
            }}
            QComboBox {{
                background: {theme.surface_glass};
                color: {theme.text_primary};
                border: 1px solid {theme.border_glass};
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 11pt;
            }}
            QComboBox:hover {{
                border: 1px solid {theme.accent_primary};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 8px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: none;
                width: 0px;
                height: 0px;
            }}
            QComboBox QAbstractItemView {{
                background: {theme.surface_glass};
                color: {theme.text_primary};
                border: 1px solid {theme.border_glass};
                border-radius: 8px;
                selection-background-color: {theme.accent_primary};
                selection-color: {theme.text_primary};
                padding: 4px;
            }}
        """)
