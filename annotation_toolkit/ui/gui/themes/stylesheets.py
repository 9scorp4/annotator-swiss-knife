"""
Centralized stylesheet generator for glassmorphism UI.

This module generates all Qt stylesheets from theme instances,
eliminating code duplication and ensuring consistency.
"""

from typing import Optional
from .glass_theme import GlassTheme, GlassConstants


class StylesheetGenerator:
    """
    Generates Qt stylesheets for all UI components using glassmorphism theme.

    This class centralizes all stylesheet generation, replacing hundreds of lines
    of duplicated inline CSS across the application.
    """

    def __init__(self, theme: GlassTheme):
        """
        Initialize the stylesheet generator with a theme.

        Args:
            theme: The GlassTheme instance to use for generation
        """
        self.theme = theme
        self.constants = GlassConstants()

    def generate_app_stylesheet(self) -> str:
        """
        Generate the main application stylesheet.

        This replaces the 492 lines of duplicated CSS in app.py.

        Returns:
            str: Complete application stylesheet
        """
        return f"""
        /* ===== MAIN APPLICATION ===== */
        QMainWindow {{
            background-color: {self.theme.background_primary};
            color: {self.theme.text_primary};
        }}

        /* ===== GLASS PANELS ===== */
        QFrame#headerFrame {{
            background: {self.theme.surface_glass_elevated};
            border: 1px solid {self.theme.border_glass};
            border-radius: {self.constants.BORDER_RADIUS_LG};
            padding: {self.constants.SPACING_LG};
        }}

        QFrame#contentContainer {{
            background: {self.theme.background_secondary};
            border: none;
        }}

        QFrame#glassPanel {{
            background: {self.theme.surface_glass};
            border: 1px solid {self.theme.border_glass};
            border-radius: {self.constants.BORDER_RADIUS_MD};
            padding: {self.constants.SPACING_LG};
        }}

        /* ===== LABELS ===== */
        QLabel {{
            color: {self.theme.text_primary};
            background: transparent;
            font-size: {self.constants.FONT_SIZE_BASE};
        }}

        QLabel#titleLabel {{
            color: {self.theme.text_primary};
            font-size: {self.constants.FONT_SIZE_XXL};
            font-weight: {self.constants.FONT_WEIGHT_BOLD};
        }}

        QLabel#subtitleLabel {{
            color: {self.theme.text_secondary};
            font-size: {self.constants.FONT_SIZE_LG};
            font-weight: {self.constants.FONT_WEIGHT_MEDIUM};
        }}

        QLabel#sectionLabel {{
            color: {self.theme.text_primary};
            font-size: {self.constants.FONT_SIZE_LG};
            font-weight: {self.constants.FONT_WEIGHT_SEMIBOLD};
        }}

        /* ===== TEXT INPUTS ===== */
        QPlainTextEdit, QTextEdit, QLineEdit {{
            background-color: {self.theme.background_glass};
            color: {self.theme.text_on_glass};
            border: 2px solid {self.theme.border_subtle};
            border-radius: {self.constants.BORDER_RADIUS_MD};
            padding: {self.constants.SPACING_MD};
            font-size: {self.constants.FONT_SIZE_BASE};
            selection-background-color: {self.theme.accent_primary};
            selection-color: {self.theme.text_on_glass};
        }}

        QPlainTextEdit:focus, QTextEdit:focus, QLineEdit:focus {{
            border-color: {self.theme.border_focus};
            background-color: {self.theme.background_glass_hover};
        }}

        QPlainTextEdit:disabled, QTextEdit:disabled, QLineEdit:disabled {{
            background-color: {self.theme.background_glass};
            color: {self.theme.text_tertiary};
            border-color: {self.theme.border_subtle};
        }}

        /* ===== COMBO BOX ===== */
        QComboBox {{
            background: {self.theme.background_glass};
            color: {self.theme.text_on_glass};
            border: 2px solid {self.theme.border_subtle};
            border-radius: {self.constants.BORDER_RADIUS_MD};
            padding: {self.constants.SPACING_SM} {self.constants.SPACING_MD};
            font-size: {self.constants.FONT_SIZE_BASE};
        }}

        QComboBox:hover {{
            background: {self.theme.background_glass_hover};
            border-color: {self.theme.border_glass};
        }}

        QComboBox:focus {{
            border-color: {self.theme.border_focus};
        }}

        QComboBox::drop-down {{
            border: none;
            padding-right: {self.constants.SPACING_SM};
        }}

        QComboBox QAbstractItemView {{
            background: {self.theme.surface_glass_elevated};
            color: {self.theme.text_on_glass};
            border: 1px solid {self.theme.border_glass};
            border-radius: {self.constants.BORDER_RADIUS_MD};
            selection-background-color: {self.theme.accent_primary};
            selection-color: {self.theme.text_on_glass};
        }}

        /* ===== CHECKBOXES ===== */
        QCheckBox {{
            color: {self.theme.text_primary};
            spacing: {self.constants.SPACING_SM};
            font-size: {self.constants.FONT_SIZE_BASE};
        }}

        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {self.theme.border_glass};
            border-radius: {self.constants.BORDER_RADIUS_SM};
            background: {self.theme.background_glass};
        }}

        QCheckBox::indicator:hover {{
            border-color: {self.theme.accent_primary};
            background: {self.theme.background_glass_hover};
        }}

        QCheckBox::indicator:checked {{
            background: {self.theme.accent_primary};
            border-color: {self.theme.accent_primary};
        }}

        /* ===== RADIO BUTTONS ===== */
        QRadioButton {{
            color: {self.theme.text_primary};
            spacing: {self.constants.SPACING_SM};
            font-size: {self.constants.FONT_SIZE_BASE};
        }}

        QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {self.theme.border_glass};
            border-radius: 9px;
            background: {self.theme.background_glass};
        }}

        QRadioButton::indicator:hover {{
            border-color: {self.theme.accent_primary};
            background: {self.theme.background_glass_hover};
        }}

        QRadioButton::indicator:checked {{
            background: {self.theme.accent_primary};
            border-color: {self.theme.accent_primary};
        }}

        /* ===== SCROLLBARS ===== */
        QScrollBar:vertical {{
            background: {self.theme.background_glass};
            width: 12px;
            border: none;
            border-radius: 6px;
            margin: 0px;
        }}

        QScrollBar::handle:vertical {{
            background: {self.theme.border_glass};
            min-height: 30px;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {self.theme.accent_primary};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        QScrollBar:horizontal {{
            background: {self.theme.background_glass};
            height: 12px;
            border: none;
            border-radius: 6px;
            margin: 0px;
        }}

        QScrollBar::handle:horizontal {{
            background: {self.theme.border_glass};
            min-width: 30px;
            border-radius: 6px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background: {self.theme.accent_primary};
        }}

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}

        /* ===== TABS ===== */
        QTabWidget::pane {{
            background: {self.theme.surface_glass};
            border: 1px solid {self.theme.border_glass};
            border-radius: {self.constants.BORDER_RADIUS_MD};
        }}

        QTabBar::tab {{
            background: {self.theme.background_glass};
            color: {self.theme.text_secondary};
            border: 1px solid {self.theme.border_subtle};
            border-bottom: none;
            border-top-left-radius: {self.constants.BORDER_RADIUS_MD};
            border-top-right-radius: {self.constants.BORDER_RADIUS_MD};
            padding: {self.constants.SPACING_SM} {self.constants.SPACING_LG};
            margin-right: 2px;
        }}

        QTabBar::tab:hover {{
            background: {self.theme.background_glass_hover};
            color: {self.theme.text_primary};
        }}

        QTabBar::tab:selected {{
            background: {self.theme.surface_glass};
            color: {self.theme.accent_primary};
            border-color: {self.theme.border_glass};
        }}

        /* ===== STATUS BAR ===== */
        QStatusBar {{
            background: {self.theme.surface_glass};
            color: {self.theme.text_secondary};
            border-top: 1px solid {self.theme.border_glass};
        }}

        /* ===== MENU BAR ===== */
        QMenuBar {{
            background: {self.theme.surface_glass_elevated};
            color: {self.theme.text_primary};
            border-bottom: 1px solid {self.theme.border_glass};
            padding: {self.constants.SPACING_XS};
        }}

        QMenuBar::item {{
            background: transparent;
            padding: {self.constants.SPACING_SM} {self.constants.SPACING_MD};
            border-radius: {self.constants.BORDER_RADIUS_SM};
        }}

        QMenuBar::item:selected {{
            background: {self.theme.background_glass_hover};
        }}

        QMenu {{
            background: {self.theme.surface_glass_elevated};
            color: {self.theme.text_primary};
            border: 1px solid {self.theme.border_glass};
            border-radius: {self.constants.BORDER_RADIUS_MD};
            padding: {self.constants.SPACING_SM};
        }}

        QMenu::item {{
            padding: {self.constants.SPACING_SM} {self.constants.SPACING_LG};
            border-radius: {self.constants.BORDER_RADIUS_SM};
        }}

        QMenu::item:selected {{
            background: {self.theme.accent_primary};
            color: {self.theme.text_on_glass};
        }}

        /* ===== TOOLTIPS ===== */
        QToolTip {{
            background: {self.theme.surface_glass_elevated};
            color: {self.theme.text_on_glass};
            border: 1px solid {self.theme.border_glass};
            border-radius: {self.constants.BORDER_RADIUS_MD};
            padding: {self.constants.SPACING_SM} {self.constants.SPACING_MD};
            font-size: {self.constants.FONT_SIZE_SM};
        }}

        /* ===== PROGRESS BAR ===== */
        QProgressBar {{
            background: {self.theme.background_glass};
            border: 1px solid {self.theme.border_subtle};
            border-radius: {self.constants.BORDER_RADIUS_SM};
            text-align: center;
            color: {self.theme.text_primary};
            font-size: {self.constants.FONT_SIZE_SM};
        }}

        QProgressBar::chunk {{
            background: {self.theme.gradient_accent};
            border-radius: {self.constants.BORDER_RADIUS_SM};
        }}
        """

    def generate_button_stylesheet(
        self,
        variant: str = "primary",
        size: str = "medium",
        full_width: bool = False
    ) -> str:
        """
        Generate button stylesheet with glassmorphic effect.

        Args:
            variant: Button variant (primary, secondary, success, danger, warning, ghost)
            size: Button size (small, medium, large)
            full_width: Whether button should take full width

        Returns:
            str: Qt stylesheet for button
        """
        # Determine colors based on variant
        if variant == "primary":
            bg_color = self.theme.accent_primary
            hover_color = self.theme.accent_primary_hover
            text_color = self.theme.text_on_glass
            glow = self.theme.accent_primary_glow
        elif variant == "secondary":
            bg_color = self.theme.accent_secondary
            hover_color = self.theme.accent_secondary
            text_color = self.theme.text_on_glass
            glow = "rgba(128, 90, 213, 0.3)"
        elif variant == "success":
            bg_color = self.theme.success_color
            hover_color = self.theme.success_color
            text_color = self.theme.text_on_glass
            glow = self.theme.success_glow
        elif variant == "danger":
            bg_color = self.theme.error_color
            hover_color = self.theme.error_color
            text_color = self.theme.text_on_glass
            glow = self.theme.error_glow
        elif variant == "warning":
            bg_color = self.theme.warning_color
            hover_color = self.theme.warning_color
            text_color = self.theme.text_on_glass
            glow = self.theme.warning_glow
        elif variant == "ghost":
            bg_color = "transparent"
            hover_color = self.theme.background_glass_hover
            text_color = self.theme.text_primary
            glow = "none"
        else:  # Default to primary
            bg_color = self.theme.accent_primary
            hover_color = self.theme.accent_primary_hover
            text_color = self.theme.text_on_glass
            glow = self.theme.accent_primary_glow

        # Determine size properties
        if size == "small":
            padding = f"{self.constants.SPACING_SM} {self.constants.SPACING_MD}"
            font_size = self.constants.FONT_SIZE_SM
            border_radius = self.constants.BORDER_RADIUS_SM
        elif size == "large":
            padding = f"{self.constants.SPACING_LG} {self.constants.SPACING_XXL}"
            font_size = self.constants.FONT_SIZE_LG
            border_radius = self.constants.BORDER_RADIUS_LG
        else:  # medium
            padding = f"{self.constants.SPACING_MD} {self.constants.SPACING_XL}"
            font_size = self.constants.FONT_SIZE_BASE
            border_radius = self.constants.BORDER_RADIUS_MD

        # Border for ghost variant
        border = f"2px solid {self.theme.border_glass}" if variant == "ghost" else "none"

        # Build stylesheet
        return f"""
        QPushButton {{
            background: {bg_color};
            color: {text_color};
            border: {border};
            border-radius: {border_radius};
            padding: {padding};
            font-size: {font_size};
            font-weight: {self.constants.FONT_WEIGHT_SEMIBOLD};
            min-width: {'100%' if full_width else '80px'};
        }}

        QPushButton:hover {{
            background: {hover_color};
            {f'border-color: {self.theme.accent_primary};' if variant == 'ghost' else ''}
        }}

        QPushButton:pressed {{
            background: {bg_color};
        }}

        QPushButton:disabled {{
            background: {self.theme.background_glass};
            color: {self.theme.text_tertiary};
            border-color: {self.theme.border_subtle};
        }}
        """

    def generate_glass_panel_stylesheet(
        self,
        elevated: bool = False,
        padding: Optional[str] = None
    ) -> str:
        """
        Generate stylesheet for glass panel/card.

        Args:
            elevated: Whether panel should be elevated (more opaque)
            padding: Custom padding, uses default if None

        Returns:
            str: Qt stylesheet for glass panel
        """
        bg = self.theme.surface_glass_elevated if elevated else self.theme.surface_glass
        pad = padding or self.constants.SPACING_LG

        return f"""
        QFrame {{
            background: {bg};
            border: 1px solid {self.theme.border_glass};
            border-radius: {self.constants.BORDER_RADIUS_LG};
            padding: {pad};
        }}
        """

    def generate_sidebar_stylesheet(self, collapsed: bool = False) -> str:
        """
        Generate stylesheet for sidebar with glassmorphic effect.

        Args:
            collapsed: Whether sidebar is in collapsed state

        Returns:
            str: Qt stylesheet for sidebar
        """
        width = "60px" if collapsed else "240px"

        return f"""
        QFrame#sidebar {{
            background: {self.theme.surface_glass_elevated};
            border-right: 1px solid {self.theme.border_glass};
            min-width: {width};
            max-width: {width};
        }}

        QPushButton#sidebarButton {{
            background: transparent;
            color: {self.theme.text_primary};
            border: none;
            border-radius: {self.constants.BORDER_RADIUS_MD};
            padding: {self.constants.SPACING_MD};
            text-align: left;
            font-size: {self.constants.FONT_SIZE_BASE};
            font-weight: {self.constants.FONT_WEIGHT_MEDIUM};
        }}

        QPushButton#sidebarButton:hover {{
            background: {self.theme.background_glass_hover};
        }}

        QPushButton#sidebarButton:checked {{
            background: {self.theme.accent_primary};
            color: {self.theme.text_on_glass};
        }}

        QLabel#sidebarLabel {{
            color: {self.theme.text_secondary};
            font-size: {self.constants.FONT_SIZE_SM};
            padding-left: {self.constants.SPACING_MD};
        }}
        """

    def generate_input_group_stylesheet(self) -> str:
        """
        Generate stylesheet for input groups (label + input).

        Returns:
            str: Qt stylesheet for input groups
        """
        return f"""
        QFrame.inputGroup {{
            background: transparent;
            border: none;
            padding: {self.constants.SPACING_SM} 0;
        }}

        QLabel.inputLabel {{
            color: {self.theme.text_secondary};
            font-size: {self.constants.FONT_SIZE_SM};
            font-weight: {self.constants.FONT_WEIGHT_MEDIUM};
            margin-bottom: {self.constants.SPACING_XS};
        }}
        """


def get_stylesheet_generator(theme: GlassTheme) -> StylesheetGenerator:
    """
    Convenience function to get a stylesheet generator.

    Args:
        theme: The theme to use

    Returns:
        StylesheetGenerator: Generator instance
    """
    return StylesheetGenerator(theme)
