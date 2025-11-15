"""
Comprehensive tests for color utility functions.

This module contains comprehensive tests for color utilities including:
- Hex to ANSI color conversion
- Color code validation
- Edge cases and boundary conditions
"""

import unittest

from annotation_toolkit.utils.color_utils import hex_to_ansi_color


class TestHexToAnsiColor(unittest.TestCase):
    """Test cases for hex_to_ansi_color function."""

    def test_convert_red(self):
        """Test converting red hex to ANSI."""
        result = hex_to_ansi_color("#FF0000")
        self.assertIn("\033[38;5;", result)
        self.assertIn("m", result)

    def test_convert_green(self):
        """Test converting green hex to ANSI."""
        result = hex_to_ansi_color("#00FF00")
        self.assertIn("\033[38;5;", result)
        self.assertIn("m", result)

    def test_convert_blue(self):
        """Test converting blue hex to ANSI."""
        result = hex_to_ansi_color("#0000FF")
        self.assertIn("\033[38;5;", result)
        self.assertIn("m", result)

    def test_convert_without_hash(self):
        """Test converting hex color without # prefix."""
        result = hex_to_ansi_color("FF0000")
        self.assertIn("\033[38;5;", result)

    def test_convert_with_hash(self):
        """Test converting hex color with # prefix."""
        result = hex_to_ansi_color("#FF0000")
        self.assertIn("\033[38;5;", result)

    def test_convert_black(self):
        """Test converting black (#000000)."""
        result = hex_to_ansi_color("#000000")
        # Black should map to color 16
        self.assertEqual(result, "\033[38;5;16m")

    def test_convert_white(self):
        """Test converting white (#FFFFFF)."""
        result = hex_to_ansi_color("#FFFFFF")
        # White should map to color 231 (16 + 36*5 + 6*5 + 5)
        self.assertEqual(result, "\033[38;5;231m")

    def test_convert_gray(self):
        """Test converting gray color."""
        result = hex_to_ansi_color("#808080")
        self.assertIn("\033[38;5;", result)
        self.assertIn("m", result)

    def test_convert_custom_color(self):
        """Test converting custom hex color."""
        result = hex_to_ansi_color("#3498db")
        self.assertIn("\033[38;5;", result)

    def test_ansi_format(self):
        """Test that output has correct ANSI escape sequence format."""
        result = hex_to_ansi_color("#FF0000")
        self.assertTrue(result.startswith("\033[38;5;"))
        self.assertTrue(result.endswith("m"))

    def test_color_code_in_range(self):
        """Test that color codes are in valid 256-color range."""
        test_colors = [
            "#000000",  # Black
            "#FFFFFF",  # White
            "#FF0000",  # Red
            "#00FF00",  # Green
            "#0000FF",  # Blue
            "#FFFF00",  # Yellow
            "#FF00FF",  # Magenta
            "#00FFFF",  # Cyan
        ]
        for hex_color in test_colors:
            result = hex_to_ansi_color(hex_color)
            # Extract the color code
            code = result.replace("\033[38;5;", "").replace("m", "")
            color_code = int(code)
            # Should be in range 16-231 (256-color palette)
            self.assertGreaterEqual(color_code, 16)
            self.assertLessEqual(color_code, 231)

    def test_same_color_produces_same_ansi(self):
        """Test that same color always produces same ANSI code."""
        color = "#FF5733"
        result1 = hex_to_ansi_color(color)
        result2 = hex_to_ansi_color(color)
        self.assertEqual(result1, result2)

    def test_lowercase_hex(self):
        """Test converting lowercase hex color."""
        result = hex_to_ansi_color("#ff0000")
        self.assertIn("\033[38;5;", result)

    def test_uppercase_hex(self):
        """Test converting uppercase hex color."""
        result = hex_to_ansi_color("#FF0000")
        self.assertIn("\033[38;5;", result)

    def test_mixed_case_hex(self):
        """Test converting mixed case hex color."""
        result = hex_to_ansi_color("#Ff0000")
        self.assertIn("\033[38;5;", result)

    def test_rgb_conversion_red_component(self):
        """Test that red component is correctly converted."""
        # Pure red should have high R value
        result = hex_to_ansi_color("#FF0000")
        code = int(result.replace("\033[38;5;", "").replace("m", ""))
        # Red contributes 36*5 = 180 to the code
        self.assertGreater(code, 16)

    def test_rgb_conversion_green_component(self):
        """Test that green component is correctly converted."""
        # Pure green should have high G value
        result = hex_to_ansi_color("#00FF00")
        code = int(result.replace("\033[38;5;", "").replace("m", ""))
        self.assertGreater(code, 16)

    def test_rgb_conversion_blue_component(self):
        """Test that blue component is correctly converted."""
        # Pure blue should have high B value
        result = hex_to_ansi_color("#0000FF")
        code = int(result.replace("\033[38;5;", "").replace("m", ""))
        self.assertGreater(code, 16)

    def test_intermediate_values(self):
        """Test intermediate color values."""
        # Test various shades
        test_cases = [
            "#7F0000",  # Dark red
            "#007F00",  # Dark green
            "#00007F",  # Dark blue
            "#7F7F7F",  # Gray
        ]
        for hex_color in test_cases:
            result = hex_to_ansi_color(hex_color)
            self.assertIn("\033[38;5;", result)
            code = int(result.replace("\033[38;5;", "").replace("m", ""))
            self.assertGreaterEqual(code, 16)
            self.assertLessEqual(code, 231)


class TestColorUtilsIntegration(unittest.TestCase):
    """Integration tests for color utilities."""

    def test_color_palette_coverage(self):
        """Test that various colors map to different ANSI codes."""
        colors = {
            "#000000": None,  # Black
            "#FF0000": None,  # Red
            "#00FF00": None,  # Green
            "#0000FF": None,  # Blue
            "#FFFFFF": None,  # White
        }
        
        for hex_color in colors:
            colors[hex_color] = hex_to_ansi_color(hex_color)
        
        # All colors should produce different ANSI codes
        ansi_codes = list(colors.values())
        unique_codes = set(ansi_codes)
        self.assertEqual(len(unique_codes), len(ansi_codes))

    def test_gradual_color_change(self):
        """Test that gradual color changes produce different codes."""
        # Test red gradient
        red_gradient = ["#330000", "#660000", "#990000", "#CC0000", "#FF0000"]
        codes = [hex_to_ansi_color(c) for c in red_gradient]
        
        # Should produce different codes for different shades
        self.assertGreater(len(set(codes)), 1)


if __name__ == "__main__":
    unittest.main()
