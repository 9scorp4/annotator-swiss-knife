"""
Tests for the text formatting utilities.

This module contains tests for the text formatting utilities in the
annotation_toolkit.utils.text.formatting module.
"""

import unittest
from unittest.mock import patch, MagicMock

from annotation_toolkit.utils.text.formatting import (
    dict_to_bullet_list,
    extract_url_title
)


class TestTextFormatting(unittest.TestCase):
    """Test cases for the text formatting utilities."""

    def test_dict_to_bullet_list_plain(self):
        """Test dict_to_bullet_list with plain text values."""
        data = {
            "Item 1": "Value 1",
            "Item 2": "Value 2",
            "Item 3": "Value 3"
        }
        result = dict_to_bullet_list(data, as_markdown=False)
        expected = "- **Item 1**: Value 1\n- **Item 2**: Value 2\n- **Item 3**: Value 3"
        self.assertEqual(result, expected)

    def test_dict_to_bullet_list_markdown(self):
        """Test dict_to_bullet_list with URLs in markdown mode."""
        data = {
            "Item 1": "Value 1",
            "Item 2": "https://example.com",
            "Item 3": "Value 3"
        }

        # Mock extract_url_title to return a predictable value
        with patch('annotation_toolkit.utils.text.formatting.extract_url_title',
                  return_value="Example Website"):
            result = dict_to_bullet_list(data, as_markdown=True)
            expected = "- **Item 1**: Value 1\n- **Item 2**: [Example Website](https://example.com)\n- **Item 3**: Value 3"
            self.assertEqual(result, expected)

    def test_dict_to_bullet_list_urls_plain(self):
        """Test dict_to_bullet_list with URLs in plain text mode."""
        data = {
            "Item 1": "Value 1",
            "Item 2": "https://example.com",
            "Item 3": "Value 3"
        }
        result = dict_to_bullet_list(data, as_markdown=False)
        expected = "- **Item 1**: Value 1\n- **Item 2**: https://example.com\n- **Item 3**: Value 3"
        self.assertEqual(result, expected)

    def test_dict_to_bullet_list_empty(self):
        """Test dict_to_bullet_list with an empty dictionary."""
        data = {}
        result = dict_to_bullet_list(data)
        self.assertEqual(result, "")

    @patch('urllib.request.urlopen')
    def test_extract_url_title_success(self, mock_urlopen):
        """Test extract_url_title when URL fetch succeeds."""
        # Mock the response from urlopen
        mock_response = MagicMock()
        mock_response.read.return_value = b'<html><head><title>Test Page Title</title></head><body></body></html>'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        url = "https://example.com"
        title = extract_url_title(url)
        self.assertEqual(title, "Test Page Title")

    @patch('urllib.request.urlopen')
    def test_extract_url_title_long_title(self, mock_urlopen):
        """Test extract_url_title with a long title."""
        # Mock the response from urlopen with a long title
        long_title = "This is a very long title that should be truncated because it exceeds the maximum length"
        mock_response = MagicMock()
        mock_response.read.return_value = f'<html><head><title>{long_title}</title></head><body></body></html>'.encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response

        url = "https://example.com"
        title = extract_url_title(url)
        self.assertEqual(title, "This is a very long title that should be truncated...")

    @patch('urllib.request.urlopen')
    def test_extract_url_title_no_title(self, mock_urlopen):
        """Test extract_url_title when the page has no title."""
        # Mock the response from urlopen with no title
        mock_response = MagicMock()
        mock_response.read.return_value = b'<html><head></head><body></body></html>'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        url = "https://example.com"
        title = extract_url_title(url)
        self.assertEqual(title, "example.com")

    @patch('urllib.request.urlopen', side_effect=Exception("Connection error"))
    def test_extract_url_title_connection_error(self, mock_urlopen):
        """Test extract_url_title when URL fetch fails."""
        url = "https://example.com"
        title = extract_url_title(url)
        self.assertEqual(title, "example.com")

    def test_extract_url_title_with_path(self):
        """Test extract_url_title with a URL that has a path."""
        # Mock urlopen to avoid actual network requests
        with patch('urllib.request.urlopen', side_effect=Exception("Connection error")):
            url = "https://example.com/some-page-name"
            title = extract_url_title(url)
            self.assertEqual(title, "example.com: Some Page Name")

    def test_extract_url_title_with_www(self):
        """Test extract_url_title with a URL that has www prefix."""
        # Mock urlopen to avoid actual network requests
        with patch('urllib.request.urlopen', side_effect=Exception("Connection error")):
            url = "https://www.example.com"
            title = extract_url_title(url)
            self.assertEqual(title, "example.com")


if __name__ == "__main__":
    unittest.main()
