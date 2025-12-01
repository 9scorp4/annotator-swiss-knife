"""
Font management utilities for consistent UI typography.

This module provides a centralized FontManager class that handles
platform-specific font selection and provides consistent font access
across all UI components.
"""

import platform
from typing import Optional, List, Dict

from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import QApplication

from ....utils import logger


# Platform-specific font preferences
PLATFORM_FONTS: Dict[str, Dict[str, List[str]]] = {
    "Darwin": {  # macOS
        "ui": ["SF Pro Display", "SF Pro Text", "Helvetica Neue", ".AppleSystemUIFont", "Arial"],
        "code": ["SF Mono", "Menlo", "Monaco", "Courier New"],
    },
    "Windows": {
        "ui": ["Segoe UI", "Calibri", "Arial"],
        "code": ["Cascadia Code", "Cascadia Mono", "Consolas", "Courier New"],
    },
    "Linux": {
        "ui": ["Ubuntu", "Roboto", "Noto Sans", "DejaVu Sans", "Arial"],
        "code": ["Ubuntu Mono", "Fira Code", "DejaVu Sans Mono", "Courier New"],
    },
}

# Default fallbacks
DEFAULT_UI_FONT = "Arial"
DEFAULT_CODE_FONT = "Courier New"


class FontManager:
    """
    Centralized font management for consistent UI typography.

    This class provides a singleton-style interface for accessing fonts
    throughout the application, ensuring consistent typography across
    all UI components with platform-appropriate font selection.

    Usage:
        # Initialize once at app startup
        FontManager.initialize()

        # Get fonts anywhere in the app
        label.setFont(FontManager.get_font(size=14, bold=True))
        code_edit.setFont(FontManager.get_code_font())
    """

    # Selected font families (set during initialization)
    _ui_font_family: str = DEFAULT_UI_FONT
    _code_font_family: str = DEFAULT_CODE_FONT
    _initialized: bool = False

    # Font size constants for consistent sizing
    SIZE_XS = 9      # Extra small (badges, tooltips)
    SIZE_SM = 11     # Small (secondary text, captions)
    SIZE_BASE = 12   # Base size (body text)
    SIZE_MD = 13     # Medium (emphasized body text)
    SIZE_LG = 14     # Large (subheadings, important text)
    SIZE_XL = 16     # Extra large (section headers)
    SIZE_XXL = 18    # Double extra large (page titles)
    SIZE_ICON = 36   # Icon size for tool cards

    @classmethod
    def initialize(cls, platform_override: Optional[str] = None) -> None:
        """
        Initialize the FontManager with platform-specific fonts.

        This should be called once during application startup, before
        any UI components are created.

        Args:
            platform_override: Optional platform name override for testing.
                             Use "Darwin", "Windows", or "Linux".
        """
        if cls._initialized:
            logger.debug("FontManager already initialized")
            return

        system = platform_override or platform.system()
        logger.debug(f"Initializing FontManager for platform: {system}")

        # Get available fonts from Qt
        try:
            font_db = QFontDatabase()
            available_fonts = set(font_db.families())
        except Exception as e:
            logger.warning(f"Could not query font database: {e}")
            available_fonts = set()

        # Get platform-specific font preferences
        font_prefs = PLATFORM_FONTS.get(system, PLATFORM_FONTS["Linux"])

        # Select UI font
        cls._ui_font_family = cls._select_available_font(
            font_prefs["ui"],
            available_fonts,
            DEFAULT_UI_FONT
        )
        logger.debug(f"Selected UI font: {cls._ui_font_family}")

        # Select code font
        cls._code_font_family = cls._select_available_font(
            font_prefs["code"],
            available_fonts,
            DEFAULT_CODE_FONT
        )
        logger.debug(f"Selected code font: {cls._code_font_family}")

        cls._initialized = True
        logger.info(f"FontManager initialized: UI={cls._ui_font_family}, Code={cls._code_font_family}")

    @classmethod
    def _select_available_font(
        cls,
        preferences: List[str],
        available: set,
        fallback: str
    ) -> str:
        """
        Select the first available font from a preference list.

        Args:
            preferences: List of font names in order of preference.
            available: Set of available font names on the system.
            fallback: Fallback font if none of the preferences are available.

        Returns:
            The name of the selected font.
        """
        for font in preferences:
            # Check exact match or if it starts with special prefix
            if font in available or font.startswith("."):
                return font

        return fallback

    @classmethod
    def get_font(
        cls,
        size: int = None,
        bold: bool = False,
        italic: bool = False,
        weight: int = None
    ) -> QFont:
        """
        Get a UI font with the specified attributes.

        Args:
            size: Font size in points. Defaults to SIZE_BASE (12).
            bold: Whether the font should be bold.
            italic: Whether the font should be italic.
            weight: Specific font weight (overrides bold if set).
                   Use QFont.Light, QFont.Normal, QFont.Medium,
                   QFont.DemiBold, QFont.Bold, QFont.Black.

        Returns:
            A QFont configured with the specified attributes.
        """
        cls._ensure_initialized()

        if size is None:
            size = cls.SIZE_BASE

        font = QFont(cls._ui_font_family, size)

        if weight is not None:
            font.setWeight(weight)
        elif bold:
            font.setBold(True)

        if italic:
            font.setItalic(True)

        return font

    @classmethod
    def get_heading_font(cls, level: int = 1) -> QFont:
        """
        Get a heading font for the specified level.

        Args:
            level: Heading level (1-3). Level 1 is largest.
                  1 = XXL Bold (18pt)
                  2 = XL Bold (16pt)
                  3 = LG Bold (14pt)

        Returns:
            A QFont configured for the heading level.
        """
        sizes = {
            1: cls.SIZE_XXL,
            2: cls.SIZE_XL,
            3: cls.SIZE_LG,
        }
        size = sizes.get(level, cls.SIZE_LG)
        return cls.get_font(size=size, bold=True)

    @classmethod
    def get_code_font(cls, size: int = None) -> QFont:
        """
        Get a monospace font for code or JSON display.

        Args:
            size: Font size in points. Defaults to SIZE_BASE (12).

        Returns:
            A QFont configured for code display.
        """
        cls._ensure_initialized()

        if size is None:
            size = cls.SIZE_BASE

        font = QFont(cls._code_font_family, size)
        font.setStyleHint(QFont.Monospace)
        return font

    @classmethod
    def get_font_family(cls) -> str:
        """
        Get the selected UI font family name.

        Returns:
            The name of the selected UI font family.
        """
        cls._ensure_initialized()
        return cls._ui_font_family

    @classmethod
    def get_code_font_family(cls) -> str:
        """
        Get the selected monospace font family name.

        Returns:
            The name of the selected code font family.
        """
        cls._ensure_initialized()
        return cls._code_font_family

    @classmethod
    def is_initialized(cls) -> bool:
        """
        Check if the FontManager has been initialized.

        Returns:
            True if initialized, False otherwise.
        """
        return cls._initialized

    @classmethod
    def reset(cls) -> None:
        """
        Reset the FontManager to uninitialized state.

        This is primarily useful for testing.
        """
        cls._ui_font_family = DEFAULT_UI_FONT
        cls._code_font_family = DEFAULT_CODE_FONT
        cls._initialized = False

    @classmethod
    def _ensure_initialized(cls) -> None:
        """
        Ensure the FontManager is initialized, initializing if needed.

        This allows lazy initialization if initialize() wasn't called explicitly.
        """
        if not cls._initialized:
            cls.initialize()

    @classmethod
    def set_application_font(cls) -> None:
        """
        Set the global application font.

        This should be called after initialize() to set the default
        font for all Qt widgets.
        """
        cls._ensure_initialized()

        app = QApplication.instance()
        if app:
            app_font = cls.get_font()
            app_font.setLetterSpacing(QFont.PercentageSpacing, 100)
            app_font.setWordSpacing(0)
            app.setFont(app_font)
            logger.debug("Set application-wide font")
