"""
Comprehensive tests for TextCleaner tool.
"""

import unittest
import json
from unittest.mock import patch, MagicMock

from annotation_toolkit.core.text.text_cleaner import TextCleaner
from annotation_toolkit.core.base import ToolExecutionError


class TestTextCleanerInitialization(unittest.TestCase):
    """Test cases for TextCleaner initialization."""

    def test_initialization_default(self):
        """Test initialization with default parameters."""
        cleaner = TextCleaner()
        self.assertEqual(cleaner.output_format, "markdown")

    def test_initialization_markdown_format(self):
        """Test initialization with markdown format."""
        cleaner = TextCleaner(output_format="markdown")
        self.assertEqual(cleaner.output_format, "markdown")

    def test_initialization_json_format(self):
        """Test initialization with JSON format."""
        cleaner = TextCleaner(output_format="json")
        self.assertEqual(cleaner.output_format, "json")

    def test_initialization_invalid_format_raises_error(self):
        """Test that invalid format raises ValueError."""
        with self.assertRaises(ValueError):
            TextCleaner(output_format="invalid")

    def test_name_property(self):
        """Test name property."""
        cleaner = TextCleaner()
        self.assertEqual(cleaner.name, "Text Cleaner")

    def test_description_property(self):
        """Test description property."""
        cleaner = TextCleaner()
        self.assertIsInstance(cleaner.description, str)
        self.assertIn("Clean", cleaner.description)


class TestTextCleanerCleanText(unittest.TestCase):
    """Test cases for clean_text method."""

    def setUp(self):
        """Set up test fixtures."""
        self.cleaner = TextCleaner()

    def test_clean_text_basic(self):
        """Test basic text cleaning."""
        text = "Hello world"
        result = self.cleaner.clean_text(text)
        self.assertEqual(result, "Hello world")

    def test_remove_code_blocks(self):
        """Test removing code blocks."""
        text = "```python\nprint('hello')\n```"
        result = self.cleaner.clean_text(text)
        self.assertNotIn("```", result)
        self.assertIn("print('hello')", result)

    def test_remove_code_blocks_with_language(self):
        """Test removing code blocks with language specifier."""
        text = "```javascript\nconsole.log('test');\n```"
        result = self.cleaner.clean_text(text)
        self.assertNotIn("```javascript", result)
        self.assertNotIn("```", result)

    def test_replace_escaped_newlines(self):
        """Test replacing escaped newlines."""
        text = "Line 1\\nLine 2\\nLine 3"
        result = self.cleaner.clean_text(text)
        self.assertIn("Line 1\nLine 2\nLine 3", result)

    def test_remove_excessive_newlines(self):
        """Test removing excessive newlines."""
        text = "Line 1\n\n\n\n\nLine 2"
        result = self.cleaner.clean_text(text)
        self.assertNotIn("\n\n\n", result)
        self.assertIn("\n\n", result)

    def test_remove_json_string_escaping(self):
        """Test removing JSON string escaping."""
        text = 'He said \\"Hello\\" to me'
        result = self.cleaner.clean_text(text)
        self.assertIn('He said "Hello" to me', result)

    def test_remove_markdown_bold(self):
        """Test removing markdown bold formatting."""
        text = "This is **bold text** here"
        result = self.cleaner.clean_text(text)
        self.assertEqual(result, "This is bold text here")

    def test_remove_markdown_italic(self):
        """Test removing markdown italic formatting."""
        text = "This is *italic text* here"
        result = self.cleaner.clean_text(text)
        self.assertEqual(result, "This is italic text here")

    def test_remove_markdown_bold_underscore(self):
        """Test removing markdown bold with underscores."""
        text = "This is __bold text__ here"
        result = self.cleaner.clean_text(text)
        self.assertEqual(result, "This is bold text here")

    def test_remove_markdown_italic_underscore(self):
        """Test removing markdown italic with underscores."""
        text = "This is _italic text_ here"
        result = self.cleaner.clean_text(text)
        self.assertEqual(result, "This is italic text here")

    def test_remove_html_tags(self):
        """Test removing HTML tags."""
        text = "This is <b>bold</b> and <i>italic</i> text"
        result = self.cleaner.clean_text(text)
        self.assertEqual(result, "This is bold and italic text")

    def test_complex_cleaning(self):
        """Test complex text cleaning with multiple artifacts."""
        text = '```python\\nprint(\\"Hello World\\")\\n```\\n\\n\\n**Bold** and *italic*'
        result = self.cleaner.clean_text(text)
        self.assertNotIn("```", result)
        self.assertNotIn("**", result)
        self.assertNotIn("*", result)
        self.assertIn("print", result)


class TestTextCleanerProcessText(unittest.TestCase):
    """Test cases for process_text method."""

    def test_process_text_markdown_format(self):
        """Test processing text with markdown output."""
        cleaner = TextCleaner(output_format="markdown")
        text = "```\nHello world\n```"
        result = cleaner.process_text(text)

        self.assertIn("# Cleaned Text", result)
        self.assertIn("## Original Text", result)
        self.assertIn("## Cleaned Text (Editable)", result)
        self.assertIn("Hello world", result)

    def test_process_text_json_format(self):
        """Test processing text with JSON output."""
        cleaner = TextCleaner(output_format="json")
        text = "**Bold text**"
        result = cleaner.process_text(text)

        # Should be valid JSON
        parsed = json.loads(result)
        self.assertIn("original_text", parsed)
        self.assertIn("cleaned_text", parsed)
        self.assertIn("instructions", parsed)
        self.assertEqual(parsed["original_text"], text)

    def test_process_text_error_handling(self):
        """Test error handling in process_text."""
        cleaner = TextCleaner()

        # Mock clean_text to raise an exception
        with patch.object(cleaner, 'clean_text', side_effect=Exception("Test error")):
            with self.assertRaises(ToolExecutionError):
                cleaner.process_text("test")


class TestTextCleanerFormatAsMarkdown(unittest.TestCase):
    """Test cases for format_as_markdown method."""

    def setUp(self):
        """Set up test fixtures."""
        self.cleaner = TextCleaner()

    def test_format_as_markdown_structure(self):
        """Test markdown format structure."""
        cleaned = "Clean text"
        original = "**Original text**"
        result = self.cleaner.format_as_markdown(cleaned, original)

        self.assertIn("# Cleaned Text", result)
        self.assertIn("## Original Text", result)
        self.assertIn("## Cleaned Text (Editable)", result)
        self.assertIn("## How to Use", result)
        self.assertIn(cleaned, result)
        self.assertIn(original, result)

    def test_format_as_markdown_contains_instructions(self):
        """Test that markdown format contains usage instructions."""
        result = self.cleaner.format_as_markdown("clean", "original")

        self.assertIn("Edit the cleaned text", result)
        self.assertIn("Transform Back", result)
        self.assertIn("computer-readable format", result)


class TestTextCleanerFormatAsJson(unittest.TestCase):
    """Test cases for format_as_json method."""

    def setUp(self):
        """Set up test fixtures."""
        self.cleaner = TextCleaner()

    def test_format_as_json_valid_json(self):
        """Test that output is valid JSON."""
        cleaned = "Clean text"
        original = "Original text"
        result = self.cleaner.format_as_json(cleaned, original)

        # Should parse without error
        parsed = json.loads(result)
        self.assertIsInstance(parsed, dict)

    def test_format_as_json_contains_fields(self):
        """Test that JSON contains required fields."""
        cleaned = "Clean text"
        original = "Original text"
        result = self.cleaner.format_as_json(cleaned, original)

        parsed = json.loads(result)
        self.assertIn("original_text", parsed)
        self.assertIn("cleaned_text", parsed)
        self.assertIn("instructions", parsed)

    def test_format_as_json_correct_values(self):
        """Test that JSON contains correct values."""
        cleaned = "Clean text"
        original = "Original text"
        result = self.cleaner.format_as_json(cleaned, original)

        parsed = json.loads(result)
        self.assertEqual(parsed["original_text"], original)
        self.assertEqual(parsed["cleaned_text"], cleaned)

    def test_format_as_json_pretty_printed(self):
        """Test that JSON is pretty-printed."""
        result = self.cleaner.format_as_json("clean", "original")
        # Pretty-printed JSON should have newlines
        self.assertIn("\n", result)


class TestTextCleanerTransformBack(unittest.TestCase):
    """Test cases for transform_back method."""

    def setUp(self):
        """Set up test fixtures."""
        self.cleaner = TextCleaner()

    def test_transform_back_code_format(self):
        """Test transforming back to code format."""
        text = 'Line 1\nLine 2\n"Quote"'
        result = self.cleaner.transform_back(text, format_type="code")

        self.assertIn("\\n", result)
        self.assertIn('\\"', result)

    def test_transform_back_code_escapes_backslashes(self):
        """Test that backslashes are escaped for code format."""
        text = "Path\\to\\file"
        result = self.cleaner.transform_back(text, format_type="code")

        self.assertIn("\\\\", result)

    def test_transform_back_code_escapes_newlines(self):
        """Test that newlines are escaped for code format."""
        text = "Line 1\nLine 2"
        result = self.cleaner.transform_back(text, format_type="code")

        self.assertIn("\\n", result)
        self.assertNotIn("\n", result.replace("\\n", ""))

    def test_transform_back_code_escapes_quotes(self):
        """Test that quotes are escaped for code format."""
        text = 'He said "Hello"'
        result = self.cleaner.transform_back(text, format_type="code")

        self.assertIn('\\"', result)

    def test_transform_back_json_format(self):
        """Test transforming back to JSON format."""
        text = "Some text\nwith newlines"
        result = self.cleaner.transform_back(text, format_type="json")

        # Should be valid JSON string
        parsed = json.loads(result)
        self.assertEqual(parsed, text)

    def test_transform_back_markdown_format(self):
        """Test transforming back to markdown format."""
        text = "# Heading\n\nParagraph\n\n- List item"
        result = self.cleaner.transform_back(text, format_type="markdown")

        self.assertIn("# Heading", result)
        self.assertIn("- List item", result)
        self.assertIn("Paragraph", result)

    def test_transform_back_markdown_preserves_headings(self):
        """Test that markdown format preserves headings."""
        text = "# Title\n## Subtitle"
        result = self.cleaner.transform_back(text, format_type="markdown")

        self.assertIn("# Title", result)
        self.assertIn("## Subtitle", result)

    def test_transform_back_markdown_preserves_lists(self):
        """Test that markdown format preserves list items."""
        text = "- Item 1\n* Item 2"
        result = self.cleaner.transform_back(text, format_type="markdown")

        self.assertIn("- Item 1", result)
        self.assertIn("* Item 2", result)

    def test_transform_back_invalid_format_raises_error(self):
        """Test that invalid format raises ValueError."""
        with self.assertRaises(ValueError):
            self.cleaner.transform_back("text", format_type="invalid")


class TestTextCleanerOutputFormatProperty(unittest.TestCase):
    """Test cases for output_format property."""

    def test_get_output_format(self):
        """Test getting output format."""
        cleaner = TextCleaner(output_format="markdown")
        self.assertEqual(cleaner.output_format, "markdown")

    def test_set_output_format_markdown(self):
        """Test setting output format to markdown."""
        cleaner = TextCleaner(output_format="json")
        cleaner.output_format = "markdown"
        self.assertEqual(cleaner.output_format, "markdown")

    def test_set_output_format_json(self):
        """Test setting output format to JSON."""
        cleaner = TextCleaner(output_format="markdown")
        cleaner.output_format = "json"
        self.assertEqual(cleaner.output_format, "json")

    def test_set_output_format_invalid_raises_error(self):
        """Test that setting invalid format raises ValueError."""
        cleaner = TextCleaner()
        with self.assertRaises(ValueError):
            cleaner.output_format = "invalid"


class TestTextCleanerIntegration(unittest.TestCase):
    """Integration tests for TextCleaner."""

    def test_clean_and_transform_back_roundtrip(self):
        """Test cleaning and transforming back preserves content."""
        cleaner = TextCleaner()
        original = "Line 1\nLine 2\nLine 3"

        # Clean the text
        cleaned = cleaner.clean_text(original)

        # Transform back to code format
        transformed = cleaner.transform_back(cleaned, format_type="code")

        # Should be escapable back to similar structure
        self.assertIn("\\n", transformed)

    def test_process_with_both_output_formats(self):
        """Test processing text with both output formats."""
        text = "```\n**Bold text**\n```"

        # Test markdown format
        cleaner_md = TextCleaner(output_format="markdown")
        result_md = cleaner_md.process_text(text)
        self.assertIn("# Cleaned Text", result_md)

        # Test JSON format
        cleaner_json = TextCleaner(output_format="json")
        result_json = cleaner_json.process_text(text)
        parsed = json.loads(result_json)
        self.assertIn("cleaned_text", parsed)

    def test_complex_text_workflow(self):
        """Test complete workflow with complex text."""
        cleaner = TextCleaner(output_format="json")

        # Complex text with multiple artifacts
        text = '```python\nprint(\\"Hello World\\")\\n```\n\n**Important:** This is *emphasized*\n\n<b>HTML bold</b>'

        # Process the text
        result = cleaner.process_text(text)

        # Verify it's valid JSON
        parsed = json.loads(result)

        # Verify cleaning worked
        cleaned = parsed["cleaned_text"]
        self.assertNotIn("```", cleaned)
        self.assertNotIn("**", cleaned)
        self.assertNotIn("<b>", cleaned)
        self.assertIn("print", cleaned)
        self.assertIn("Important", cleaned)
        self.assertIn("emphasized", cleaned)

    def test_output_format_switching(self):
        """Test switching output format dynamically."""
        cleaner = TextCleaner(output_format="markdown")
        text = "Test text"

        # Process with markdown
        result1 = cleaner.process_text(text)
        self.assertIn("# Cleaned Text", result1)

        # Switch to JSON
        cleaner.output_format = "json"
        result2 = cleaner.process_text(text)
        parsed = json.loads(result2)
        self.assertIn("cleaned_text", parsed)


if __name__ == "__main__":
    unittest.main()
