"""
Color utility functions for the annotation toolkit.

This module provides functions for working with colors.
"""


def hex_to_ansi_color(hex_color: str) -> str:
    """
    Convert a hex color code to the closest ANSI color code.

    Args:
        hex_color (str): The hex color code (e.g., "#FF0000").

    Returns:
        str: The ANSI color code.
    """
    # Remove the # if present
    if hex_color.startswith("#"):
        hex_color = hex_color[1:]

    # Convert hex to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    # Use 8-bit color (256 colors)
    # This is a simplified conversion that maps RGB to the 256-color space
    ansi_r = int(r / 255 * 5)
    ansi_g = int(g / 255 * 5)
    ansi_b = int(b / 255 * 5)

    # Calculate the color code (16 + 36*r + 6*g + b)
    color_code = 16 + (36 * ansi_r) + (6 * ansi_g) + ansi_b

    # Return the ANSI escape sequence
    return f"\033[38;5;{color_code}m"
