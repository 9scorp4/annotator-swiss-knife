"""
Unit tests for the XML formatter module.

This module tests XML formatting functionality including tag formatting,
validation, extraction, and conversion to different output formats.
"""

import unittest
from html import escape

from annotation_toolkit.utils.xml.formatter import (
    XmlFormatter,
    format_xml_tags,
    parse_xml_content
)


class TestXmlFormatterInit(unittest.TestCase):
    """Test XmlFormatter initialization."""

    def test_formatter_default_initialization(self):
        """Test formatter with default parameters."""
        formatter = XmlFormatter()

        self.assertEqual(formatter.indent_size, 4)
        self.assertEqual(formatter.max_line_length, 120)
        self.assertIsNotNone(formatter._tag_pattern)
        self.assertIsNotNone(formatter._single_tag_pattern)

    def test_formatter_custom_indent_size(self):
        """Test formatter with custom indent size."""
        formatter = XmlFormatter(indent_size=2)

        self.assertEqual(formatter.indent_size, 2)

    def test_formatter_custom_max_line_length(self):
        """Test formatter with custom max line length."""
        formatter = XmlFormatter(max_line_length=80)

        self.assertEqual(formatter.max_line_length, 80)

    def test_formatter_custom_parameters(self):
        """Test formatter with all custom parameters."""
        formatter = XmlFormatter(indent_size=8, max_line_length=100)

        self.assertEqual(formatter.indent_size, 8)
        self.assertEqual(formatter.max_line_length, 100)


class TestFormatXmlInText(unittest.TestCase):
    """Test format_xml_in_text method."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = XmlFormatter()

    def test_format_simple_xml_tag(self):
        """Test formatting simple XML tag."""
        text = "<tag>content</tag>"
        result = self.formatter.format_xml_in_text(text)

        self.assertIn("<tag>", result)
        self.assertIn("</tag>", result)
        self.assertIn("content", result)

    def test_format_quoted_xml(self):
        """Test formatting quoted XML with preserve_quotes."""
        text = '"<tag>content</tag>"'
        result = self.formatter.format_xml_in_text(text, preserve_quotes=True)

        self.assertTrue(result.startswith('"'))
        self.assertTrue(result.endswith('"'))
        self.assertIn("<tag>", result)
        self.assertIn("content", result)

    def test_format_quoted_xml_without_preserve(self):
        """Test formatting quoted XML without preserve_quotes."""
        text = '"<tag>content</tag>"'
        result = self.formatter.format_xml_in_text(text, preserve_quotes=False)

        # Should treat quotes as part of content
        self.assertIn('"', result)

    def test_format_nested_xml_tags(self):
        """Test formatting nested XML tags."""
        text = "<outer><inner>content</inner></outer>"
        result = self.formatter.format_xml_in_text(text)

        self.assertIn("<outer>", result)
        self.assertIn("<inner>", result)
        self.assertIn("</inner>", result)
        self.assertIn("</outer>", result)

    def test_format_long_content_wraps(self):
        """Test that long content is wrapped."""
        long_content = "a" * 150  # Longer than default max_line_length
        text = f"<tag>{long_content}</tag>"
        result = self.formatter.format_xml_in_text(text)

        # Should contain newlines for wrapping
        self.assertIn("\n", result)

    def test_format_short_content_inline(self):
        """Test that short content stays inline."""
        text = "<tag>short</tag>"
        result = self.formatter.format_xml_in_text(text)

        # Should not wrap short content
        self.assertEqual(result, "<tag>short</tag>")

    def test_format_empty_tag(self):
        """Test formatting empty XML tag."""
        text = "<tag></tag>"
        result = self.formatter.format_xml_in_text(text)

        self.assertIn("<tag>", result)
        self.assertIn("</tag>", result)


class TestFormatXmlInHtml(unittest.TestCase):
    """Test format_xml_in_html method."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = XmlFormatter()

    def test_format_xml_for_html_display(self):
        """Test formatting XML for HTML display."""
        text = "<tag>content</tag>"
        result = self.formatter.format_xml_in_html(text)

        # Should contain HTML formatting
        self.assertIn("<pre", result)
        self.assertIn("<span", result)
        self.assertIn("style=", result)

    def test_html_formatting_escapes_entities(self):
        """Test that HTML entities are escaped."""
        text = "<tag>content with < and > symbols</tag>"
        result = self.formatter.format_xml_in_html(text)

        # Tags should be escaped in output
        escaped_lt = escape("<")
        escaped_gt = escape(">")
        self.assertIn(escaped_lt, result)
        self.assertIn(escaped_gt, result)

    def test_html_formatting_includes_color_styling(self):
        """Test that HTML output includes color styling."""
        text = "<tag>content</tag>"
        result = self.formatter.format_xml_in_html(text)

        # Should include color style
        self.assertIn("color:", result)
        self.assertIn("#9c27b0", result)  # Purple color for tags

    def test_html_formatting_with_nested_tags(self):
        """Test HTML formatting with nested tags."""
        text = "<outer><inner>content</inner></outer>"
        result = self.formatter.format_xml_in_html(text)

        self.assertIn("<pre", result)
        # Escaped tags should be present
        self.assertIn(escape("<outer>"), result)
        self.assertIn(escape("<inner>"), result)


class TestFormatXmlInJson(unittest.TestCase):
    """Test format_xml_in_json method."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = XmlFormatter()

    def test_format_xml_for_json(self):
        """Test formatting XML for JSON."""
        text = "<tag>content</tag>"
        result = self.formatter.format_xml_in_json(text)

        # Should be quoted
        self.assertTrue(result.startswith('"'))
        self.assertTrue(result.endswith('"'))

    def test_json_formatting_escapes_quotes(self):
        """Test that quotes are escaped in JSON output."""
        text = 'content with "quotes"'
        result = self.formatter.format_xml_in_json(text)

        # Quotes should be escaped
        self.assertIn('\\"', result)

    def test_json_formatting_includes_newlines(self):
        """Test that JSON formatting includes newlines for structure."""
        text = "<tag>content</tag>"
        result = self.formatter.format_xml_in_json(text)

        # Should include escaped newlines
        self.assertIn('\\n', result)

    def test_json_formatting_with_indentation(self):
        """Test JSON formatting includes indentation."""
        text = "<tag>content</tag>"
        formatter = XmlFormatter(indent_size=4)
        result = formatter.format_xml_in_json(text)

        # Should include spaces for indentation (escaped in JSON string)
        self.assertIn('    ', result)  # 4 spaces


class TestValidateXmlTags(unittest.TestCase):
    """Test validate_xml_tags method."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = XmlFormatter()

    def test_validate_properly_paired_tags(self):
        """Test validation of properly paired tags."""
        text = "<tag>content</tag>"
        is_valid, errors = self.formatter.validate_xml_tags(text)

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_nested_tags(self):
        """Test validation of nested tags."""
        text = "<outer><inner>content</inner></outer>"
        is_valid, errors = self.formatter.validate_xml_tags(text)

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_multiple_tags(self):
        """Test validation of multiple tag pairs."""
        text = "<tag1>content1</tag1><tag2>content2</tag2>"
        is_valid, errors = self.formatter.validate_xml_tags(text)

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_unclosed_tag(self):
        """Test detection of unclosed tag."""
        text = "<tag>content"
        is_valid, errors = self.formatter.validate_xml_tags(text)

        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        self.assertIn("Unclosed tag", errors[0])

    def test_validate_closing_tag_without_opening(self):
        """Test detection of closing tag without opening."""
        text = "content</tag>"
        is_valid, errors = self.formatter.validate_xml_tags(text)

        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        self.assertIn("without opening tag", errors[0])

    def test_validate_mismatched_tags(self):
        """Test detection of mismatched tags."""
        text = "<tag1>content</tag2>"
        is_valid, errors = self.formatter.validate_xml_tags(text)

        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
        self.assertIn("Mismatched tags", errors[0])

    def test_validate_multiple_errors(self):
        """Test detection of multiple errors."""
        text = "<tag1>content</tag2><tag3>"
        is_valid, errors = self.formatter.validate_xml_tags(text)

        self.assertFalse(is_valid)
        self.assertGreaterEqual(len(errors), 2)  # At least 2 errors

    def test_validate_empty_text(self):
        """Test validation of empty text."""
        text = ""
        is_valid, errors = self.formatter.validate_xml_tags(text)

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)


class TestExtractXmlContent(unittest.TestCase):
    """Test extract_xml_content method."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = XmlFormatter()

    def test_extract_single_tag_content(self):
        """Test extraction of single tag content."""
        text = "<tag>content</tag>"
        results = self.formatter.extract_xml_content(text)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['tag_name'], 'tag')
        self.assertEqual(results[0]['content'], 'content')
        self.assertEqual(results[0]['full_match'], '<tag>content</tag>')

    def test_extract_multiple_tags(self):
        """Test extraction of multiple tags."""
        text = "<tag1>content1</tag1><tag2>content2</tag2>"
        results = self.formatter.extract_xml_content(text)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['tag_name'], 'tag1')
        self.assertEqual(results[0]['content'], 'content1')
        self.assertEqual(results[1]['tag_name'], 'tag2')
        self.assertEqual(results[1]['content'], 'content2')

    def test_extract_nested_tags(self):
        """Test extraction of nested tags."""
        text = "<outer><inner>content</inner></outer>"
        results = self.formatter.extract_xml_content(text)

        # Should extract outer tag with inner tags as content
        self.assertGreater(len(results), 0)
        # The outer tag should be extracted
        outer_result = [r for r in results if r['tag_name'] == 'outer']
        self.assertEqual(len(outer_result), 1)

    def test_extract_content_with_whitespace(self):
        """Test extraction trims whitespace from content."""
        text = "<tag>  content  </tag>"
        results = self.formatter.extract_xml_content(text)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['content'], 'content')  # Whitespace trimmed

    def test_extract_empty_content(self):
        """Test extraction of empty tag."""
        text = "<tag></tag>"
        results = self.formatter.extract_xml_content(text)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['content'], '')

    def test_extract_no_tags(self):
        """Test extraction when no tags present."""
        text = "just plain text"
        results = self.formatter.extract_xml_content(text)

        self.assertEqual(len(results), 0)


class TestWrapText(unittest.TestCase):
    """Test _wrap_text private method."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = XmlFormatter()

    def test_wrap_short_text(self):
        """Test wrapping text shorter than max width."""
        text = "short text"
        lines = self.formatter._wrap_text(text, 50)

        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], "short text")

    def test_wrap_long_text(self):
        """Test wrapping text longer than max width."""
        text = "this is a very long text that should be wrapped to multiple lines"
        lines = self.formatter._wrap_text(text, 20)

        self.assertGreater(len(lines), 1)
        for line in lines:
            self.assertLessEqual(len(line), 20 + 10)  # Some tolerance for word boundaries

    def test_wrap_single_long_word(self):
        """Test wrapping with single word longer than max width."""
        text = "verylongwordthatcannotbewrapped"
        lines = self.formatter._wrap_text(text, 10)

        # Should still create a line even if word is longer
        self.assertGreater(len(lines), 0)

    def test_wrap_empty_text(self):
        """Test wrapping empty text."""
        text = ""
        lines = self.formatter._wrap_text(text, 50)

        self.assertEqual(len(lines), 0)

    def test_wrap_preserves_words(self):
        """Test that wrapping doesn't break words."""
        text = "hello world this is a test"
        lines = self.formatter._wrap_text(text, 15)

        for line in lines:
            # Each line should contain complete words
            self.assertNotIn("hel lo", line)  # Word shouldn't be broken


class TestFormatXmlTagsConvenience(unittest.TestCase):
    """Test format_xml_tags convenience function."""

    def test_format_xml_tags_default_text(self):
        """Test format_xml_tags with default text output."""
        text = "<tag>content</tag>"
        result = format_xml_tags(text)

        self.assertIn("<tag>", result)
        self.assertIn("content", result)

    def test_format_xml_tags_html_output(self):
        """Test format_xml_tags with HTML output."""
        text = "<tag>content</tag>"
        result = format_xml_tags(text, output_format='html')

        self.assertIn("<pre", result)
        self.assertIn("<span", result)

    def test_format_xml_tags_json_output(self):
        """Test format_xml_tags with JSON output."""
        text = "<tag>content</tag>"
        result = format_xml_tags(text, output_format='json')

        self.assertTrue(result.startswith('"'))
        self.assertTrue(result.endswith('"'))

    def test_format_xml_tags_custom_indent(self):
        """Test format_xml_tags with custom indent size."""
        text = "<tag>content</tag>"
        result = format_xml_tags(text, indent_size=8)

        # Function should accept custom indent
        self.assertIsNotNone(result)

    def test_format_xml_tags_invalid_format(self):
        """Test format_xml_tags with invalid output format."""
        text = "<tag>content</tag>"
        result = format_xml_tags(text, output_format='invalid')

        # Should default to text format
        self.assertIn("<tag>", result)


class TestParseXmlContentConvenience(unittest.TestCase):
    """Test parse_xml_content convenience function."""

    def test_parse_xml_content_single_tag(self):
        """Test parse_xml_content with single tag."""
        text = "<tag>content</tag>"
        results = parse_xml_content(text)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['tag_name'], 'tag')
        self.assertEqual(results[0]['content'], 'content')

    def test_parse_xml_content_multiple_tags(self):
        """Test parse_xml_content with multiple tags."""
        text = "<tag1>content1</tag1><tag2>content2</tag2>"
        results = parse_xml_content(text)

        self.assertEqual(len(results), 2)

    def test_parse_xml_content_no_tags(self):
        """Test parse_xml_content with no tags."""
        text = "plain text"
        results = parse_xml_content(text)

        self.assertEqual(len(results), 0)


class TestXmlFormatterEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = XmlFormatter()

    def test_format_malformed_xml(self):
        """Test formatting malformed XML."""
        text = "<tag>content<tag>"
        result = self.formatter.format_xml_in_text(text)

        # Should not raise error, just return result
        self.assertIsNotNone(result)

    def test_format_xml_with_special_characters(self):
        """Test formatting XML with special characters."""
        text = "<tag>content with & and < symbols</tag>"
        result = self.formatter.format_xml_in_text(text)

        self.assertIn("&", result)
        self.assertIn("<", result)

    def test_format_xml_with_unicode(self):
        """Test formatting XML with unicode characters."""
        text = "<tag>unicode: ñ, é, 中文, 🎉</tag>"
        result = self.formatter.format_xml_in_text(text)

        self.assertIn("unicode", result)
        self.assertIn("🎉", result)

    def test_format_very_long_tag_name(self):
        """Test formatting with very long tag name."""
        long_tag = "a" * 100
        text = f"<{long_tag}>content</{long_tag}>"
        result = self.formatter.format_xml_in_text(text)

        self.assertIn(long_tag, result)

    def test_format_xml_with_newlines_in_content(self):
        """Test formatting XML with newlines in content."""
        text = "<tag>line1\nline2\nline3</tag>"
        result = self.formatter.format_xml_in_text(text)

        self.assertIn("line1", result)
        self.assertIn("line2", result)
        self.assertIn("line3", result)

    def test_validate_xml_with_numeric_tag_names(self):
        """Test validation rejects tags starting with numbers."""
        # XML tag names cannot start with numbers
        text = "<123tag>content</123tag>"
        # The pattern should not match tags starting with numbers
        results = self.formatter.extract_xml_content(text)

        # Should not extract invalid tag names
        self.assertEqual(len(results), 0)

    def test_format_xml_with_self_closing_tags(self):
        """Test handling of self-closing tags (edge case)."""
        # Self-closing tags are not fully supported by the tag_pattern
        text = "<tag/>"
        results = self.formatter.extract_xml_content(text)

        # Self-closing tags won't be extracted by the paired tag pattern
        self.assertEqual(len(results), 0)


class TestXmlFormatterIntegration(unittest.TestCase):
    """Integration tests for XML formatter."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = XmlFormatter(indent_size=4, max_line_length=100)

    def test_format_and_validate_workflow(self):
        """Test formatting followed by validation."""
        text = "<outer><inner>content</inner></outer>"

        # Format
        formatted = self.formatter.format_xml_in_text(text)

        # Validate original
        is_valid, errors = self.formatter.validate_xml_tags(text)

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_extract_and_format_workflow(self):
        """Test extracting content and formatting it."""
        text = "<tag>content</tag>"

        # Extract
        extracted = self.formatter.extract_xml_content(text)

        # Format the extracted content
        self.assertEqual(len(extracted), 1)
        content = extracted[0]['content']
        self.assertEqual(content, 'content')

    def test_complex_nested_xml_formatting(self):
        """Test formatting complex nested XML structure."""
        text = """<response>
            <status>success</status>
            <data>
                <item>value1</item>
                <item>value2</item>
            </data>
        </response>"""

        # Should handle complex structure
        formatted = self.formatter.format_xml_in_text(text)
        is_valid, errors = self.formatter.validate_xml_tags(text)

        self.assertIsNotNone(formatted)
        self.assertTrue(is_valid)

    def test_all_output_formats_for_same_input(self):
        """Test converting same input to all output formats."""
        text = "<tag>test content</tag>"

        text_format = self.formatter.format_xml_in_text(text)
        html_format = self.formatter.format_xml_in_html(text)
        json_format = self.formatter.format_xml_in_json(text)

        # All should contain the original content
        self.assertIn("test content", text_format)
        self.assertIn("test content", html_format)
        self.assertIn("test content", json_format)

        # But formats should be different
        self.assertNotEqual(text_format, html_format)
        self.assertNotEqual(text_format, json_format)
        self.assertNotEqual(html_format, json_format)


if __name__ == "__main__":
    unittest.main()
