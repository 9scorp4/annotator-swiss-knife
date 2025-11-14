"""
Tests for the Text Collector tool.

This module contains tests for the TextCollector class in the
annotation_toolkit.core.text.text_collector module.
"""

import unittest

from annotation_toolkit.core.text.text_collector import TextCollector
from annotation_toolkit.utils.errors import ProcessingError, TypeValidationError


class TestTextCollector(unittest.TestCase):
    """Test cases for the TextCollector class."""

    def setUp(self):
        """Set up test fixtures."""
        self.tool = TextCollector()
        self.test_list = ["text1", "text2", "text3"]
        self.test_dict = {"field1": "text1", "field2": "text2", "field3": "text3"}
        self.test_list_with_empty = ["text1", "", "text2", "   ", "text3"]

    def test_initialization(self):
        """Test that the tool initializes with the correct default values."""
        self.assertEqual(self.tool.name, "Text Collector")
        self.assertEqual(self.tool.max_fields, 20)
        self.assertTrue(self.tool.filter_empty)

        # Test with custom values
        tool = TextCollector(max_fields=10, filter_empty=False)
        self.assertEqual(tool.max_fields, 10)
        self.assertFalse(tool.filter_empty)

    def test_collect_from_list_valid(self):
        """Test collecting text from a valid list."""
        result = self.tool.collect_from_list(self.test_list)
        self.assertEqual(len(result), 3)
        self.assertEqual(result, ["text1", "text2", "text3"])

    def test_collect_from_list_with_empty_filtering(self):
        """Test collecting text from a list with empty strings, with filtering enabled."""
        result = self.tool.collect_from_list(self.test_list_with_empty)
        # Should filter out empty and whitespace-only strings
        self.assertEqual(len(result), 3)
        self.assertEqual(result, ["text1", "text2", "text3"])

    def test_collect_from_list_without_empty_filtering(self):
        """Test collecting text from a list with empty strings, with filtering disabled."""
        tool = TextCollector(filter_empty=False)
        result = tool.collect_from_list(self.test_list_with_empty)
        # Should keep all items including empty
        self.assertEqual(len(result), 5)
        self.assertEqual(result, ["text1", "", "text2", "   ", "text3"])

    def test_collect_from_list_invalid_type(self):
        """Test collecting from non-list input."""
        with self.assertRaises(TypeValidationError):
            self.tool.collect_from_list("not a list")

        with self.assertRaises(TypeValidationError):
            self.tool.collect_from_list({"dict": "not list"})

    def test_collect_from_list_non_string_items(self):
        """Test collecting from list with non-string items."""
        invalid_list = ["text1", 123, "text3"]
        with self.assertRaises(TypeValidationError):
            self.tool.collect_from_list(invalid_list)

    def test_collect_from_list_exceeds_max_fields(self):
        """Test collecting from list that exceeds max_fields."""
        tool = TextCollector(max_fields=2)
        long_list = ["text1", "text2", "text3"]
        with self.assertRaises(ProcessingError):
            tool.collect_from_list(long_list)

    def test_collect_from_dict_valid(self):
        """Test collecting text from a valid dictionary."""
        result = self.tool.collect_from_dict(self.test_dict)
        self.assertEqual(len(result), 3)
        # Note: dict order is preserved in Python 3.7+
        self.assertIn("text1", result)
        self.assertIn("text2", result)
        self.assertIn("text3", result)

    def test_collect_from_dict_with_empty_filtering(self):
        """Test collecting text from a dict with empty strings, with filtering enabled."""
        test_dict = {"field1": "text1", "field2": "", "field3": "text3", "field4": "   "}
        result = self.tool.collect_from_dict(test_dict)
        # Should filter out empty and whitespace-only strings
        self.assertEqual(len(result), 2)
        self.assertIn("text1", result)
        self.assertIn("text3", result)

    def test_collect_from_dict_invalid_type(self):
        """Test collecting from non-dict input."""
        with self.assertRaises(TypeValidationError):
            self.tool.collect_from_dict("not a dict")

        with self.assertRaises(TypeValidationError):
            self.tool.collect_from_dict(["list", "not", "dict"])

    def test_collect_from_dict_non_string_values(self):
        """Test collecting from dict with non-string values."""
        invalid_dict = {"field1": "text1", "field2": 123}
        with self.assertRaises(TypeValidationError):
            self.tool.collect_from_dict(invalid_dict)

    def test_collect_from_dict_exceeds_max_fields(self):
        """Test collecting from dict that exceeds max_fields."""
        tool = TextCollector(max_fields=2)
        large_dict = {"field1": "text1", "field2": "text2", "field3": "text3"}
        with self.assertRaises(ProcessingError):
            tool.collect_from_dict(large_dict)

    def test_process_json_with_list(self):
        """Test process_json with list input."""
        result = self.tool.process_json(self.test_list)
        self.assertEqual(len(result), 3)
        self.assertEqual(result, ["text1", "text2", "text3"])

    def test_process_json_with_dict(self):
        """Test process_json with dict input."""
        result = self.tool.process_json(self.test_dict)
        self.assertEqual(len(result), 3)
        self.assertIn("text1", result)
        self.assertIn("text2", result)
        self.assertIn("text3", result)

    def test_to_json_string_pretty(self):
        """Test converting to pretty JSON string."""
        text_items = ["text1", "text2", "text3"]
        json_str = self.tool.to_json_string(text_items, pretty=True)

        # Check that it's valid JSON
        import json
        parsed = json.loads(json_str)
        self.assertEqual(parsed, text_items)

        # Check that it's pretty formatted (has newlines)
        self.assertIn("\n", json_str)

    def test_to_json_string_compact(self):
        """Test converting to compact JSON string."""
        text_items = ["text1", "text2", "text3"]
        json_str = self.tool.to_json_string(text_items, pretty=False)

        # Check that it's valid JSON
        import json
        parsed = json.loads(json_str)
        self.assertEqual(parsed, text_items)

        # Compact format should not have newlines (except maybe in the data itself)
        # Check it's more compact than pretty version
        pretty_str = self.tool.to_json_string(text_items, pretty=True)
        self.assertLess(len(json_str), len(pretty_str))

    def test_empty_list_handling(self):
        """Test handling of completely empty list."""
        result = self.tool.process_json([])
        self.assertEqual(len(result), 0)
        self.assertEqual(result, [])

    def test_all_empty_strings_filtered(self):
        """Test that all empty strings are filtered out."""
        all_empty = ["", "   ", "\t", "\n"]
        result = self.tool.process_json(all_empty)
        self.assertEqual(len(result), 0)
        self.assertEqual(result, [])

    def test_whitespace_stripping(self):
        """Test that whitespace is stripped from strings."""
        whitespace_list = ["  text1  ", "\ttext2\t", "\ntext3\n"]
        result = self.tool.process_json(whitespace_list)
        self.assertEqual(result, ["text1", "text2", "text3"])

    def test_description_property(self):
        """Test the description property."""
        self.assertIsInstance(self.tool.description, str)
        self.assertIn("JSON", self.tool.description)
        self.assertIn("list", self.tool.description.lower())

    def test_max_fields_boundary(self):
        """Test behavior at max_fields boundary."""
        tool = TextCollector(max_fields=3)

        # Exactly at max should work
        exact_max = ["text1", "text2", "text3"]
        result = tool.process_json(exact_max)
        self.assertEqual(len(result), 3)

        # One over max should fail
        over_max = ["text1", "text2", "text3", "text4"]
        with self.assertRaises(ProcessingError):
            tool.process_json(over_max)


if __name__ == "__main__":
    unittest.main()
