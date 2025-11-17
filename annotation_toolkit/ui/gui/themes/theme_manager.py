"""
Theme Manager for centralized theme switching and state management.

This module provides a singleton ThemeManager that handles theme switching,
persistence, and notifies all widgets when the theme changes.
"""

from enum import Enum
from typing import Optional
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPalette, QGuiApplication

from .glass_theme import GlassTheme, GlassDarkTheme, GlassLightTheme


class ThemeMode(Enum):
    """Available theme modes."""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"  # Follow system theme


class ThemeManager(QObject):
    """
    Singleton manager for application theming.

    Handles theme switching, persistence, and emits signals when theme changes
    so all widgets can update their stylesheets dynamically.

    Signals:
        theme_changed: Emitted when theme changes, passes new GlassTheme instance
    """

    # Singleton instance
    _instance: Optional['ThemeManager'] = None

    # Signal emitted when theme changes
    theme_changed = pyqtSignal(object)  # Emits GlassTheme instance

    def __new__(cls):
        """Ensure only one instance exists (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the theme manager (only runs once due to singleton)."""
        if self._initialized:
            return

        super().__init__()
        self._initialized = True

        # Create theme instances FIRST
        self._dark_theme = GlassDarkTheme()
        self._light_theme = GlassLightTheme()

        # Then set current mode and theme
        self._current_mode: ThemeMode = ThemeMode.AUTO
        self._current_theme: GlassTheme = self._create_theme_for_mode(ThemeMode.AUTO)

    @classmethod
    def instance(cls) -> 'ThemeManager':
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def current_theme(self) -> GlassTheme:
        """Get the current active theme."""
        return self._current_theme

    @property
    def current_mode(self) -> ThemeMode:
        """Get the current theme mode setting."""
        return self._current_mode

    @property
    def is_dark_mode(self) -> bool:
        """Check if currently in dark mode."""
        return self._current_theme.is_dark

    def set_theme_mode(self, mode: ThemeMode) -> None:
        """
        Set the theme mode and update the current theme.

        Args:
            mode: The theme mode to set (LIGHT, DARK, or AUTO)
        """
        if mode == self._current_mode:
            return  # No change

        self._current_mode = mode
        new_theme = self._create_theme_for_mode(mode)

        if new_theme != self._current_theme:
            self._current_theme = new_theme
            self.theme_changed.emit(self._current_theme)

    def set_dark_theme(self) -> None:
        """Set dark theme explicitly."""
        self.set_theme_mode(ThemeMode.DARK)

    def set_light_theme(self) -> None:
        """Set light theme explicitly."""
        self.set_theme_mode(ThemeMode.LIGHT)

    def set_auto_theme(self) -> None:
        """Set auto theme (follows system preference)."""
        self.set_theme_mode(ThemeMode.AUTO)

    def toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        if self._current_mode == ThemeMode.AUTO:
            # If in auto mode, switch to the opposite of current system theme
            if self._detect_system_dark_mode():
                self.set_light_theme()
            else:
                self.set_dark_theme()
        elif self._current_mode == ThemeMode.DARK:
            self.set_light_theme()
        else:
            self.set_dark_theme()

    def refresh_auto_theme(self) -> None:
        """
        Refresh the theme if in AUTO mode.

        Call this when system theme changes are detected.
        """
        if self._current_mode == ThemeMode.AUTO:
            new_theme = self._create_theme_for_mode(ThemeMode.AUTO)
            if new_theme.is_dark != self._current_theme.is_dark:
                self._current_theme = new_theme
                self.theme_changed.emit(self._current_theme)

    def _create_theme_for_mode(self, mode: ThemeMode) -> GlassTheme:
        """
        Create appropriate theme instance for the given mode.

        Args:
            mode: The theme mode

        Returns:
            GlassTheme instance (either dark or light)
        """
        if mode == ThemeMode.DARK:
            return self._dark_theme
        elif mode == ThemeMode.LIGHT:
            return self._light_theme
        else:  # AUTO
            if self._detect_system_dark_mode():
                return self._dark_theme
            else:
                return self._light_theme

    @staticmethod
    def _detect_system_dark_mode() -> bool:
        """
        Detect if system is using dark mode.

        Returns:
            bool: True if dark mode, False if light mode
        """
        try:
            # Try to get system palette
            app = QGuiApplication.instance()
            if app is not None:
                palette = app.palette()
                # Check if window background is dark
                bg_color = palette.color(QPalette.Window)
                # Calculate luminance
                luminance = (0.299 * bg_color.red() +
                           0.587 * bg_color.green() +
                           0.114 * bg_color.blue()) / 255.0
                # If luminance is less than 0.5, it's dark mode
                return luminance < 0.5
        except Exception:
            pass

        # Default to light mode if detection fails
        return False

    def get_theme_for_mode(self, mode: ThemeMode) -> GlassTheme:
        """
        Get theme instance for a specific mode without changing current theme.

        Args:
            mode: The theme mode to get

        Returns:
            GlassTheme instance
        """
        return self._create_theme_for_mode(mode)

    def save_preference(self, config_manager) -> None:
        """
        Save current theme preference to config.

        Args:
            config_manager: Application config manager instance
        """
        try:
            config_manager.set("ui", "theme", "mode", self._current_mode.value)
        except Exception as e:
            # Silently fail if config save fails
            print(f"Warning: Failed to save theme preference: {e}")

    def load_preference(self, config_manager) -> None:
        """
        Load theme preference from config.

        Args:
            config_manager: Application config manager instance
        """
        try:
            mode_str = config_manager.get("ui", "theme", "mode", default="auto")
            mode = ThemeMode(mode_str)
            self.set_theme_mode(mode)
        except Exception as e:
            # Silently fail and use default if load fails
            print(f"Warning: Failed to load theme preference: {e}")
            self.set_theme_mode(ThemeMode.AUTO)


# Convenience function for getting the theme manager
def get_theme_manager() -> ThemeManager:
    """
    Get the global ThemeManager instance.

    Returns:
        ThemeManager: The singleton theme manager
    """
    return ThemeManager.instance()


# Convenience function for getting current theme
def get_current_theme() -> GlassTheme:
    """
    Get the current active theme.

    Returns:
        GlassTheme: The current theme instance
    """
    return ThemeManager.instance().current_theme
