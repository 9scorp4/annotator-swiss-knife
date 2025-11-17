"""
Theme and color palette constants for the GUI application.

This module provides a centralized color palette and theme system
for consistent styling across all widgets.

DEPRECATED: This module is kept for backward compatibility.
New code should use the glassmorphism theme system in themes/
"""

from typing import Dict

# Import new glassmorphism theme system
try:
    from .themes import ThemeManager, StylesheetGenerator
    _GLASSMORPHISM_AVAILABLE = True
except ImportError:
    _GLASSMORPHISM_AVAILABLE = False


class ColorPalette:
    """Modern, accessible color palette for the application."""

    # Primary colors (blues) - Darker for better contrast with white text
    PRIMARY = "#1e40af"  # Darker blue for better contrast (WCAG AAA)
    PRIMARY_HOVER = "#2563eb"  # Slightly lighter on hover
    PRIMARY_PRESSED = "#1e3a8a"  # Even darker when pressed
    PRIMARY_LIGHT = "#3b82f6"

    # Success colors (greens)
    SUCCESS = "#10b981"  # Refined green
    SUCCESS_HOVER = "#059669"
    SUCCESS_PRESSED = "#047857"
    SUCCESS_LIGHT = "#34d399"

    # Danger colors (reds)
    DANGER = "#ef4444"  # Softer red
    DANGER_HOVER = "#dc2626"
    DANGER_PRESSED = "#b91c1c"
    DANGER_LIGHT = "#f87171"

    # Warning colors (oranges)
    WARNING = "#f59e0b"  # Better orange
    WARNING_HOVER = "#d97706"
    WARNING_PRESSED = "#b45309"
    WARNING_LIGHT = "#fbbf24"

    # Neutral colors (grays)
    GRAY_50 = "#f9fafb"
    GRAY_100 = "#f3f4f6"
    GRAY_200 = "#e5e7eb"
    GRAY_300 = "#d1d5db"
    GRAY_400 = "#9ca3af"
    GRAY_500 = "#6b7280"
    GRAY_600 = "#4b5563"
    GRAY_700 = "#374151"
    GRAY_800 = "#1f2937"
    GRAY_900 = "#111827"

    # Dark mode colors
    DARK_BG_PRIMARY = "#1f2937"
    DARK_BG_SECONDARY = "#111827"
    DARK_BG_TERTIARY = "#374151"
    DARK_TEXT_PRIMARY = "#f9fafb"
    DARK_TEXT_SECONDARY = "#d1d5db"

    # Light mode colors
    LIGHT_BG_PRIMARY = "#ffffff"
    LIGHT_BG_SECONDARY = "#f9fafb"
    LIGHT_BG_TERTIARY = "#f3f4f6"
    LIGHT_TEXT_PRIMARY = "#111827"
    LIGHT_TEXT_SECONDARY = "#6b7280"

    # Semantic colors
    INFO = "#3b82f6"
    INFO_HOVER = "#2563eb"


class Shadows:
    """Shadow definitions for consistent depth."""

    SMALL = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    MEDIUM = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    LARGE = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    EXTRA_LARGE = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"


class Spacing:
    """Consistent spacing scale."""

    XS = "4px"
    SM = "8px"
    MD = "12px"
    LG = "16px"
    XL = "20px"
    XXL = "24px"
    XXXL = "32px"


class BorderRadius:
    """Consistent border radius values."""

    SM = "4px"
    MD = "6px"
    LG = "8px"
    XL = "12px"
    FULL = "9999px"


def get_button_style(
    bg_color: str,
    hover_color: str,
    pressed_color: str,
    text_color: str = "#ffffff",
    border_radius: str = BorderRadius.MD,
    padding: str = "10px 16px",
) -> str:
    """
    Generate consistent button stylesheet.

    Args:
        bg_color: Background color
        hover_color: Hover state color
        pressed_color: Pressed state color
        text_color: Text color (default: white)
        border_radius: Border radius (default: 6px)
        padding: Padding (default: 10px 16px)

    Returns:
        str: Qt stylesheet for button
    """
    return f"""
        QPushButton {{
            background-color: {bg_color};
            color: {text_color};
            border: none;
            border-radius: {border_radius};
            padding: {padding};
            font-weight: 600;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: {hover_color};
        }}
        QPushButton:pressed {{
            background-color: {pressed_color};
        }}
        QPushButton:disabled {{
            background-color: {ColorPalette.GRAY_300};
            color: {ColorPalette.GRAY_500};
        }}
    """


def get_primary_button_style() -> str:
    """Get stylesheet for primary action buttons (with glassmorphism if available)."""
    if _GLASSMORPHISM_AVAILABLE:
        try:
            theme = ThemeManager.instance().current_theme
            generator = StylesheetGenerator(theme)
            return generator.generate_button_stylesheet(variant="primary", size="medium")
        except Exception:
            pass  # Fall back to legacy style

    return get_button_style(
        ColorPalette.PRIMARY,
        ColorPalette.PRIMARY_HOVER,
        ColorPalette.PRIMARY_PRESSED
    )


def get_success_button_style() -> str:
    """Get stylesheet for success/add buttons (with glassmorphism if available)."""
    if _GLASSMORPHISM_AVAILABLE:
        try:
            theme = ThemeManager.instance().current_theme
            generator = StylesheetGenerator(theme)
            return generator.generate_button_stylesheet(variant="success", size="medium")
        except Exception:
            pass  # Fall back to legacy style

    return get_button_style(
        ColorPalette.SUCCESS,
        ColorPalette.SUCCESS_HOVER,
        ColorPalette.SUCCESS_PRESSED
    )


def get_danger_button_style() -> str:
    """Get stylesheet for danger/delete buttons (with glassmorphism if available)."""
    if _GLASSMORPHISM_AVAILABLE:
        try:
            theme = ThemeManager.instance().current_theme
            generator = StylesheetGenerator(theme)
            return generator.generate_button_stylesheet(variant="danger", size="medium")
        except Exception:
            pass  # Fall back to legacy style

    return get_button_style(
        ColorPalette.DANGER,
        ColorPalette.DANGER_HOVER,
        ColorPalette.DANGER_PRESSED
    )


def get_warning_button_style() -> str:
    """Get stylesheet for warning/caution buttons (with glassmorphism if available)."""
    if _GLASSMORPHISM_AVAILABLE:
        try:
            theme = ThemeManager.instance().current_theme
            generator = StylesheetGenerator(theme)
            return generator.generate_button_stylesheet(variant="warning", size="medium")
        except Exception:
            pass  # Fall back to legacy style

    return get_button_style(
        ColorPalette.WARNING,
        ColorPalette.WARNING_HOVER,
        ColorPalette.WARNING_PRESSED
    )


def get_frame_style(is_dark: bool = False, elevated: bool = False) -> str:
    """
    Get stylesheet for frames/containers (with glassmorphism if available).

    Args:
        is_dark: Whether to use dark theme colors (deprecated when using glassmorphism)
        elevated: Whether frame should be elevated (more opaque)

    Returns:
        str: Qt stylesheet for frames
    """
    if _GLASSMORPHISM_AVAILABLE:
        try:
            theme = ThemeManager.instance().current_theme
            generator = StylesheetGenerator(theme)
            return generator.generate_glass_panel_stylesheet(elevated=elevated)
        except Exception:
            pass  # Fall back to legacy style

    if is_dark:
        bg_color = ColorPalette.DARK_BG_TERTIARY
        border_color = ColorPalette.GRAY_700
    else:
        bg_color = ColorPalette.LIGHT_BG_PRIMARY
        border_color = ColorPalette.GRAY_200

    return f"""
        QFrame {{
            background-color: {bg_color};
            border: 1px solid {border_color};
            border-radius: {BorderRadius.LG};
            padding: {Spacing.LG};
        }}
    """


def get_text_input_style(is_dark: bool = False) -> str:
    """
    Get stylesheet for text input fields.

    Args:
        is_dark: Whether to use dark theme colors

    Returns:
        str: Qt stylesheet for text inputs
    """
    if is_dark:
        bg_color = ColorPalette.DARK_BG_SECONDARY
        text_color = ColorPalette.DARK_TEXT_PRIMARY
        border_color = ColorPalette.GRAY_600
        focus_border = ColorPalette.PRIMARY
    else:
        bg_color = ColorPalette.LIGHT_BG_PRIMARY
        text_color = ColorPalette.LIGHT_TEXT_PRIMARY
        border_color = ColorPalette.GRAY_300
        focus_border = ColorPalette.PRIMARY

    return f"""
        QPlainTextEdit, QTextEdit {{
            background-color: {bg_color};
            color: {text_color};
            border: 2px solid {border_color};
            border-radius: {BorderRadius.MD};
            padding: {Spacing.MD};
            font-size: 13px;
        }}
        QPlainTextEdit:focus, QTextEdit:focus {{
            border-color: {focus_border};
        }}
    """
