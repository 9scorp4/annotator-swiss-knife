"""
Tests for the JSON parser utilities.

This module contains tests for the JSON parser utilities in the
annotation_toolkit.utils.json.parser module.
"""

import unittest
from unittest.mock import patch, MagicMock

from annotation_toolkit.utils.json.parser import (
    parse_json,
    extract_json_from_text,
    is_valid_json
)
from annotation_toolkit.utils.errors import ParsingError


class TestJsonParser(unittest.TestCase):
    """Test cases for the JSON parser utilities."""

    def test_is_valid_json_valid(self):
        """Test is_valid_json with valid JSON."""
        valid_json = '{"key": "value", "number": 42, "list": [1, 2, 3]}'
        self.assertTrue(is_valid_json(valid_json))

    def test_is_valid_json_invalid(self):
        """Test is_valid_json with invalid JSON."""
        invalid_json = '{"key": "value", "unclosed": "string}'
        self.assertFalse(is_valid_json(invalid_json))

    def test_is_valid_json_empty(self):
        """Test is_valid_json with empty string."""
        self.assertFalse(is_valid_json(""))

    def test_is_valid_json_none(self):
        """Test is_valid_json with None."""
        self.assertFalse(is_valid_json(None))

    def test_parse_json_valid(self):
        """Test parse_json with valid JSON."""
        valid_json = '{"key": "value", "number": 42}'
        result = parse_json(valid_json)
        self.assertEqual(result, {"key": "value", "number": 42})

    def test_parse_json_invalid(self):
        """Test parse_json with invalid JSON."""
        invalid_json = '{"key": "value", "unclosed": "string}'
        with self.assertRaises(ParsingError):
            parse_json(invalid_json)

    def test_parse_json_empty(self):
        """Test parse_json with empty string."""
        with self.assertRaises(ParsingError):
            parse_json("")

    def test_parse_json_none(self):
        """Test parse_json with None."""
        with self.assertRaises(ParsingError):
            parse_json(None)

    def test_extract_json_from_text_simple(self):
        """Test extract_json_from_text with simple JSON embedded in text."""
        text = "Here is some JSON: {\"key\": \"value\"} and some more text."
        result = extract_json_from_text(text)
        self.assertEqual(result, {"key": "value"})

    def test_extract_json_from_text_complex(self):
        """Test extract_json_from_text with complex JSON embedded in text."""
        text = """
        Here is some complex JSON:
        {
            "key": "value",
            "number": 42,
            "list": [1, 2, 3],
            "nested": {
                "inner": "value"
            }
        }
        And some more text.
        """
        result = extract_json_from_text(text)
        self.assertEqual(
            result,
            {
                "key": "value",
                "number": 42,
                "list": [1, 2, 3],
                "nested": {
                    "inner": "value"
                }
            }
        )

    def test_extract_json_from_text_multiple(self):
        """Test extract_json_from_text with multiple JSON objects in text."""
        text = """
        Here is some JSON: {"first": "object"}
        And here is another: {"second": "object"}
        """
        # Should return the first valid JSON object found
        result = extract_json_from_text(text)
        self.assertEqual(result, {"first": "object"})

    def test_extract_json_from_text_no_json(self):
        """Test extract_json_from_text with no JSON in text."""
        text = "This text contains no valid JSON objects."
        with self.assertRaises(ParsingError):
            extract_json_from_text(text)

    def test_extract_json_from_text_invalid_json(self):
        """Test extract_json_from_text with invalid JSON in text."""
        text = "Here is some invalid JSON: {\"key\": \"unclosed}"
        with self.assertRaises(ParsingError):
            extract_json_from_text(text)


if __name__ == "__main__":
    unittest.main()
