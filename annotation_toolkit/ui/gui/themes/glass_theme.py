"""
Glassmorphism theme system with modern blur, transparency, and color palettes.

This module provides the core theme classes for the glassmorphism design system,
including color palettes with alpha channels, blur effects, gradients, and glow effects.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class BlurSettings:
    """Blur radius settings for glassmorphism effects."""
    NONE: int = 0
    SUBTLE: int = 5
    LIGHT: int = 10
    MEDIUM: int = 20
    STRONG: int = 30
    HEAVY: int = 50


@dataclass
class OpacitySettings:
    """Opacity/alpha values for transparency effects."""
    TRANSPARENT: float = 0.0
    BARELY_VISIBLE: float = 0.05
    VERY_LIGHT: float = 0.1
    LIGHT: float = 0.2
    MEDIUM_LIGHT: float = 0.4
    MEDIUM: float = 0.6
    MEDIUM_HEAVY: float = 0.8
    HEAVY: float = 0.9
    OPAQUE: float = 1.0


class GlassTheme(ABC):
    """
    Abstract base class for glassmorphism themes.

    Provides all color, blur, shadow, and effect properties needed
    for a consistent glassmorphic design across the application.
    """

    # Theme metadata
    @property
    @abstractmethod
    def name(self) -> str:
        """Theme name."""
        pass

    @property
    @abstractmethod
    def is_dark(self) -> bool:
        """Whether this is a dark theme."""
        pass

    # Background colors with alpha for glass effect
    @property
    @abstractmethod
    def background_primary(self) -> str:
        """Primary background color (solid)."""
        pass

    @property
    @abstractmethod
    def background_secondary(self) -> str:
        """Secondary background color (solid)."""
        pass

    @property
    @abstractmethod
    def background_glass(self) -> str:
        """Glassmorphic background with transparency."""
        pass

    @property
    @abstractmethod
    def background_glass_hover(self) -> str:
        """Glassmorphic background on hover."""
        pass

    @property
    @abstractmethod
    def background_glass_active(self) -> str:
        """Glassmorphic background when active/pressed."""
        pass

    # Surface colors (for cards, panels, etc.)
    @property
    @abstractmethod
    def surface_glass(self) -> str:
        """Glass surface for cards and panels."""
        pass

    @property
    @abstractmethod
    def surface_glass_elevated(self) -> str:
        """Elevated glass surface with more opacity."""
        pass

    # Text colors
    @property
    @abstractmethod
    def text_primary(self) -> str:
        """Primary text color."""
        pass

    @property
    @abstractmethod
    def text_secondary(self) -> str:
        """Secondary text color (dimmed)."""
        pass

    @property
    @abstractmethod
    def text_tertiary(self) -> str:
        """Tertiary text color (more dimmed)."""
        pass

    @property
    @abstractmethod
    def text_on_glass(self) -> str:
        """Text color optimized for glass surfaces."""
        pass

    # Border colors
    @property
    @abstractmethod
    def border_glass(self) -> str:
        """Border color for glass elements."""
        pass

    @property
    @abstractmethod
    def border_subtle(self) -> str:
        """Subtle border color."""
        pass

    @property
    @abstractmethod
    def border_focus(self) -> str:
        """Border color for focused elements."""
        pass

    # Accent colors (vibrant, for CTAs and highlights)
    @property
    @abstractmethod
    def accent_primary(self) -> str:
        """Primary accent color."""
        pass

    @property
    @abstractmethod
    def accent_primary_hover(self) -> str:
        """Primary accent on hover."""
        pass

    @property
    @abstractmethod
    def accent_primary_glow(self) -> str:
        """Glow effect for primary accent."""
        pass

    @property
    @abstractmethod
    def accent_secondary(self) -> str:
        """Secondary accent color."""
        pass

    # Semantic colors
    @property
    @abstractmethod
    def success_color(self) -> str:
        """Success/positive color."""
        pass

    @property
    @abstractmethod
    def success_glow(self) -> str:
        """Glow effect for success elements."""
        pass

    @property
    @abstractmethod
    def warning_color(self) -> str:
        """Warning/caution color."""
        pass

    @property
    @abstractmethod
    def warning_glow(self) -> str:
        """Glow effect for warning elements."""
        pass

    @property
    @abstractmethod
    def error_color(self) -> str:
        """Error/danger color."""
        pass

    @property
    @abstractmethod
    def error_glow(self) -> str:
        """Glow effect for error elements."""
        pass

    @property
    @abstractmethod
    def info_color(self) -> str:
        """Info/neutral color."""
        pass

    # Shadows for glassmorphism
    @property
    @abstractmethod
    def shadow_glass_light(self) -> str:
        """Light shadow for glass elements."""
        pass

    @property
    @abstractmethod
    def shadow_glass_medium(self) -> str:
        """Medium shadow for glass elements."""
        pass

    @property
    @abstractmethod
    def shadow_glass_heavy(self) -> str:
        """Heavy shadow for elevated glass elements."""
        pass

    @property
    @abstractmethod
    def shadow_glow_primary(self) -> str:
        """Glow shadow for primary elements."""
        pass

    @property
    @abstractmethod
    def shadow_glow_success(self) -> str:
        """Glow shadow for success elements."""
        pass

    # Gradients
    @property
    @abstractmethod
    def gradient_glass_bg(self) -> str:
        """Gradient for glass backgrounds."""
        pass

    @property
    @abstractmethod
    def gradient_accent(self) -> str:
        """Gradient for accent elements."""
        pass


class GlassDarkTheme(GlassTheme):
    """Dark mode glassmorphism theme with deep backgrounds and vibrant accents."""

    @property
    def name(self) -> str:
        return "Dark Glass"

    @property
    def is_dark(self) -> bool:
        return True

    # Dark backgrounds
    @property
    def background_primary(self) -> str:
        return "#0a0a0f"  # Very dark blue-black

    @property
    def background_secondary(self) -> str:
        return "#13131a"  # Dark blue-gray

    @property
    def background_glass(self) -> str:
        return "rgba(25, 25, 35, 0.7)"  # Semi-transparent dark with blur

    @property
    def background_glass_hover(self) -> str:
        return "rgba(35, 35, 50, 0.75)"

    @property
    def background_glass_active(self) -> str:
        return "rgba(45, 45, 60, 0.8)"

    # Dark surfaces
    @property
    def surface_glass(self) -> str:
        return "rgba(30, 30, 45, 0.6)"

    @property
    def surface_glass_elevated(self) -> str:
        return "rgba(40, 40, 55, 0.75)"

    # Dark text
    @property
    def text_primary(self) -> str:
        return "#f5f5f7"  # Off-white

    @property
    def text_secondary(self) -> str:
        return "#b8b8bd"  # Light gray

    @property
    def text_tertiary(self) -> str:
        return "#86868f"  # Medium gray

    @property
    def text_on_glass(self) -> str:
        return "#ffffff"  # Pure white for contrast on glass

    # Dark borders
    @property
    def border_glass(self) -> str:
        return "rgba(255, 255, 255, 0.12)"  # Subtle white border

    @property
    def border_subtle(self) -> str:
        return "rgba(255, 255, 255, 0.08)"

    @property
    def border_focus(self) -> str:
        return "rgba(99, 179, 237, 0.6)"  # Blue glow

    # Vibrant accents for dark mode
    @property
    def accent_primary(self) -> str:
        return "#63b3ed"  # Bright blue

    @property
    def accent_primary_hover(self) -> str:
        return "#7cc4f7"

    @property
    def accent_primary_glow(self) -> str:
        return "rgba(99, 179, 237, 0.4)"

    @property
    def accent_secondary(self) -> str:
        return "#9f7aea"  # Purple

    # Dark semantic colors
    @property
    def success_color(self) -> str:
        return "#48bb78"  # Bright green

    @property
    def success_glow(self) -> str:
        return "rgba(72, 187, 120, 0.3)"

    @property
    def warning_color(self) -> str:
        return "#f6ad55"  # Bright orange

    @property
    def warning_glow(self) -> str:
        return "rgba(246, 173, 85, 0.3)"

    @property
    def error_color(self) -> str:
        return "#fc8181"  # Bright red

    @property
    def error_glow(self) -> str:
        return "rgba(252, 129, 129, 0.3)"

    @property
    def info_color(self) -> str:
        return "#4fd1c5"  # Bright teal

    # Dark shadows
    @property
    def shadow_glass_light(self) -> str:
        return "0 2px 8px rgba(0, 0, 0, 0.3)"

    @property
    def shadow_glass_medium(self) -> str:
        return "0 4px 16px rgba(0, 0, 0, 0.4), 0 0 1px rgba(255, 255, 255, 0.1)"

    @property
    def shadow_glass_heavy(self) -> str:
        return "0 8px 32px rgba(0, 0, 0, 0.5), 0 0 2px rgba(255, 255, 255, 0.1)"

    @property
    def shadow_glow_primary(self) -> str:
        return "0 0 20px rgba(99, 179, 237, 0.3), 0 0 40px rgba(99, 179, 237, 0.1)"

    @property
    def shadow_glow_success(self) -> str:
        return "0 0 20px rgba(72, 187, 120, 0.3), 0 0 40px rgba(72, 187, 120, 0.1)"

    # Dark gradients
    @property
    def gradient_glass_bg(self) -> str:
        return "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(25, 25, 35, 0.8), stop:1 rgba(15, 15, 25, 0.6))"

    @property
    def gradient_accent(self) -> str:
        return "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #63b3ed, stop:1 #9f7aea)"


class GlassLightTheme(GlassTheme):
    """Light mode glassmorphism theme with bright backgrounds and soft accents."""

    @property
    def name(self) -> str:
        return "Light Glass"

    @property
    def is_dark(self) -> bool:
        return False

    # Light backgrounds
    @property
    def background_primary(self) -> str:
        return "#f7f9fc"  # Very light blue-gray

    @property
    def background_secondary(self) -> str:
        return "#ffffff"  # Pure white

    @property
    def background_glass(self) -> str:
        return "rgba(255, 255, 255, 0.65)"  # Semi-transparent white with blur

    @property
    def background_glass_hover(self) -> str:
        return "rgba(255, 255, 255, 0.75)"

    @property
    def background_glass_active(self) -> str:
        return "rgba(255, 255, 255, 0.85)"

    # Light surfaces
    @property
    def surface_glass(self) -> str:
        return "rgba(255, 255, 255, 0.55)"

    @property
    def surface_glass_elevated(self) -> str:
        return "rgba(255, 255, 255, 0.8)"

    # Light text
    @property
    def text_primary(self) -> str:
        return "#1a1a1f"  # Nearly black

    @property
    def text_secondary(self) -> str:
        return "#4a4a55"  # Dark gray

    @property
    def text_tertiary(self) -> str:
        return "#7a7a85"  # Medium gray

    @property
    def text_on_glass(self) -> str:
        return "#1a1a1f"  # Dark text on light glass

    # Light borders
    @property
    def border_glass(self) -> str:
        return "rgba(0, 0, 0, 0.08)"  # Subtle dark border

    @property
    def border_subtle(self) -> str:
        return "rgba(0, 0, 0, 0.05)"

    @property
    def border_focus(self) -> str:
        return "rgba(66, 153, 225, 0.5)"  # Blue glow

    # Refined accents for light mode
    @property
    def accent_primary(self) -> str:
        return "#4299e1"  # Vibrant blue

    @property
    def accent_primary_hover(self) -> str:
        return "#3182ce"

    @property
    def accent_primary_glow(self) -> str:
        return "rgba(66, 153, 225, 0.3)"

    @property
    def accent_secondary(self) -> str:
        return "#805ad5"  # Purple

    # Light semantic colors
    @property
    def success_color(self) -> str:
        return "#38a169"  # Green

    @property
    def success_glow(self) -> str:
        return "rgba(56, 161, 105, 0.25)"

    @property
    def warning_color(self) -> str:
        return "#dd6b20"  # Orange

    @property
    def warning_glow(self) -> str:
        return "rgba(221, 107, 32, 0.25)"

    @property
    def error_color(self) -> str:
        return "#e53e3e"  # Red

    @property
    def error_glow(self) -> str:
        return "rgba(229, 62, 62, 0.25)"

    @property
    def info_color(self) -> str:
        return "#319795"  # Teal

    # Light shadows (enhanced for visibility without blur)
    @property
    def shadow_glass_light(self) -> str:
        return "0 2px 12px rgba(0, 0, 0, 0.08), 0 1px 3px rgba(0, 0, 0, 0.06)"

    @property
    def shadow_glass_medium(self) -> str:
        return "0 4px 20px rgba(0, 0, 0, 0.12), 0 2px 6px rgba(0, 0, 0, 0.08)"

    @property
    def shadow_glass_heavy(self) -> str:
        return "0 10px 40px rgba(0, 0, 0, 0.15), 0 4px 12px rgba(0, 0, 0, 0.10)"

    @property
    def shadow_glow_primary(self) -> str:
        return "0 0 20px rgba(66, 153, 225, 0.2), 0 0 40px rgba(66, 153, 225, 0.08)"

    @property
    def shadow_glow_success(self) -> str:
        return "0 0 20px rgba(56, 161, 105, 0.2), 0 0 40px rgba(56, 161, 105, 0.08)"

    # Light gradients (enhanced for better visibility)
    @property
    def gradient_glass_bg(self) -> str:
        return "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffffff, stop:0.5 #f7f9fc, stop:1 #edf2f7)"

    @property
    def gradient_accent(self) -> str:
        return "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4299e1, stop:0.5 #5a67d8, stop:1 #805ad5)"


# Shared constants
class GlassConstants:
    """Shared constants for glassmorphism effects."""

    # Blur values (note: Qt doesn't support backdrop-filter, so these are for reference/CSS export)
    BLUR = BlurSettings()
    OPACITY = OpacitySettings()

    # Border radius
    BORDER_RADIUS_SM = "6px"
    BORDER_RADIUS_MD = "10px"
    BORDER_RADIUS_LG = "16px"
    BORDER_RADIUS_XL = "24px"
    BORDER_RADIUS_FULL = "9999px"

    # Spacing
    SPACING_XS = "4px"
    SPACING_SM = "8px"
    SPACING_MD = "12px"
    SPACING_LG = "16px"
    SPACING_XL = "24px"
    SPACING_XXL = "32px"
    SPACING_XXXL = "48px"

    # Animation durations (milliseconds)
    ANIMATION_FAST = 150
    ANIMATION_NORMAL = 250
    ANIMATION_SLOW = 400

    # Typography
    FONT_SIZE_XS = "11px"
    FONT_SIZE_SM = "12px"
    FONT_SIZE_BASE = "14px"
    FONT_SIZE_LG = "16px"
    FONT_SIZE_XL = "20px"
    FONT_SIZE_XXL = "24px"
    FONT_SIZE_XXXL = "32px"

    FONT_WEIGHT_NORMAL = 400
    FONT_WEIGHT_MEDIUM = 500
    FONT_WEIGHT_SEMIBOLD = 600
    FONT_WEIGHT_BOLD = 700
