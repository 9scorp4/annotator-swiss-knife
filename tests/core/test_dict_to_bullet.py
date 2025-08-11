"""
Tests for the Dictionary to Bullet List conversion tool.

This module contains tests for the DictToBulletList class in the
annotation_toolkit.core.text.dict_to_bullet module.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from annotation_toolkit.core.text.dict_to_bullet import DictToBulletList
from annotation_toolkit.utils.errors import ToolExecutionError


class TestDictToBulletList(unittest.TestCase):
    """Test cases for the DictToBulletList class."""

    def setUp(self):
        """Set up test fixtures."""
        self.tool = DictToBulletList()
        self.test_dict = {
            "Item 1": "Value 1",
            "Item 2": "https://example.com",
            "Item 3": "Value 3",
        }
        self.test_json = json.dumps(self.test_dict)

    def test_initialization(self):
        """Test that the tool initializes with the correct default values."""
        self.assertEqual(self.tool.name, "Dictionary to Bullet List")
        self.assertTrue(self.tool.markdown_output)

        # Test with markdown_output=False
        tool = DictToBulletList(markdown_output=False)
        self.assertFalse(tool.markdown_output)

    def test_process_text_valid_json(self):
        """Test processing valid JSON text."""
        result = self.tool.process_text(self.test_json)
        self.assertIn("Item 1", result)
        self.assertIn("Value 1", result)
        self.assertIn("Item 2", result)
        self.assertIn("https://example.com", result)

    def test_process_text_invalid_json(self):
        """Test processing invalid JSON text."""
        with self.assertRaises(ToolExecutionError):
            self.tool.process_text("{invalid json")

    def test_process_text_non_dict_json(self):
        """Test processing JSON that doesn't represent a dictionary."""
        with self.assertRaises(ToolExecutionError):
            self.tool.process_text(json.dumps(["not", "a", "dict"]))

    def test_process_dict_valid(self):
        """Test processing a valid dictionary."""
        result = self.tool.process_dict(self.test_dict)
        self.assertIn("Item 1", result)
        self.assertIn("Value 1", result)
        self.assertIn("Item 2", result)
        self.assertIn("https://example.com", result)

    def test_process_dict_non_string_values(self):
        """Test processing a dictionary with non-string values."""
        invalid_dict = {"Item 1": "Value 1", "Item 2": 123}  # Non-string value
        with self.assertRaises(ToolExecutionError):
            self.tool.process_dict(invalid_dict)

    def test_markdown_output_setting(self):
        """Test changing the markdown_output setting."""
        self.assertTrue(self.tool.markdown_output)
        self.tool.markdown_output = False
        self.assertFalse(self.tool.markdown_output)

    def test_process_dict_to_items(self):
        """Test converting a dictionary to a list of (title, url) tuples."""
        with patch(
            "annotation_toolkit.core.text.dict_to_bullet.extract_url_title",
            return_value="Example Website",
        ):
            items = self.tool.process_dict_to_items(self.test_dict)
            self.assertEqual(len(items), 3)

            # Check non-URL item
            self.assertEqual(items[0], ("Item 1", "Value 1"))

            # Check URL item
            self.assertEqual(items[1], ("Example Website", "https://example.com"))

            # Check another non-URL item
            self.assertEqual(items[2], ("Item 3", "Value 3"))

    def test_process_dict_to_items_non_string_values(self):
        """Test processing a dictionary with non-string values for items."""
        invalid_dict = {"Item 1": "Value 1", "Item 2": 123}  # Non-string value
        with self.assertRaises(ToolExecutionError):
            self.tool.process_dict_to_items(invalid_dict)


if __name__ == "__main__":
    unittest.main()
