"""
Comprehensive tests for JSON formatting utilities.

This module contains comprehensive tests for JSON formatting functions including:
- JSON prettification
- Conversation formatting (text and markdown)
- Color formatting integration
"""

import unittest
from unittest.mock import patch, MagicMock

from annotation_toolkit.utils.json.formatter import (
    prettify_json,
    format_conversation_as_text,
    format_conversation_as_markdown,
)


class TestPrettifyJson(unittest.TestCase):
    """Test cases for prettify_json function."""

    def test_prettify_json_dict(self):
        """Test prettifying a dictionary."""
        data = {"name": "John", "age": 30, "city": "New York"}
        result = prettify_json(data)

        self.assertIsInstance(result, str)
        self.assertIn("name", result)
        self.assertIn("John", result)
        # Check for default indentation
        self.assertIn("  ", result)

    def test_prettify_json_list(self):
        """Test prettifying a list."""
        data = [1, 2, 3, {"key": "value"}]
        result = prettify_json(data)

        self.assertIsInstance(result, str)
        self.assertIn("[", result)
        self.assertIn("]", result)

    def test_prettify_json_custom_indent(self):
        """Test prettifying with custom indentation."""
        data = {"key": "value"}
        result = prettify_json(data, indent=4)

        self.assertIn("    ", result)  # 4 spaces

    def test_prettify_json_unicode(self):
        """Test prettifying JSON with unicode characters."""
        data = {"message": "Hello 世界", "emoji": "😀"}
        result = prettify_json(data)

        # Should preserve unicode (ensure_ascii=False)
        self.assertIn("世界", result)
        self.assertIn("😀", result)

    def test_prettify_json_nested(self):
        """Test prettifying nested JSON structures."""
        data = {
            "level1": {
                "level2": {
                    "level3": "value"
                }
            }
        }
        result = prettify_json(data)

        self.assertIn("level1", result)
        self.assertIn("level2", result)
        self.assertIn("level3", result)

    def test_prettify_json_empty_dict(self):
        """Test prettifying empty dictionary."""
        data = {}
        result = prettify_json(data)
        self.assertEqual(result, "{}")

    def test_prettify_json_empty_list(self):
        """Test prettifying empty list."""
        data = []
        result = prettify_json(data)
        self.assertEqual(result, "[]")


class TestFormatConversationAsText(unittest.TestCase):
    """Test cases for format_conversation_as_text function."""

    def test_format_conversation_basic(self):
        """Test basic conversation formatting."""
        conversation = [
            {"role": "user", "content": "Hello!"},
            {"role": "ai", "content": "Hi there!"}
        ]

        result = format_conversation_as_text(conversation)

        self.assertIn("Message 1 (USER)", result)
        self.assertIn("Hello!", result)
        self.assertIn("Message 2 (AI)", result)
        self.assertIn("Hi there!", result)

    def test_format_conversation_without_colors(self):
        """Test formatting without colors."""
        conversation = [
            {"role": "user", "content": "Test message"}
        ]

        result = format_conversation_as_text(conversation, use_colors=False)

        # Should not contain ANSI escape codes
        self.assertNotIn("\033[", result)

    def test_format_conversation_with_colors(self):
        """Test formatting with colors enabled."""
        conversation = [
            {"role": "user", "content": "Test message"}
        ]

        result = format_conversation_as_text(
            conversation,
            user_message_color="#FF0000",
            use_colors=True
        )

        # Should contain ANSI escape codes
        self.assertIn("\033[", result)

    def test_format_conversation_empty(self):
        """Test formatting empty conversation."""
        conversation = []
        result = format_conversation_as_text(conversation)
        self.assertEqual(result, "")

    def test_format_conversation_missing_role(self):
        """Test formatting message with missing role."""
        conversation = [
            {"content": "Message without role"}
        ]

        result = format_conversation_as_text(conversation)
        self.assertIn("UNKNOWN", result)

    def test_format_conversation_missing_content(self):
        """Test formatting message with missing content."""
        conversation = [
            {"role": "user"}
        ]

        result = format_conversation_as_text(conversation)
        self.assertIn("USER", result)

    def test_format_conversation_multiline_content(self):
        """Test formatting message with multiline content."""
        conversation = [
            {"role": "user", "content": "Line 1\nLine 2\nLine 3"}
        ]

        result = format_conversation_as_text(conversation)
        self.assertIn("Line 1", result)
        self.assertIn("Line 2", result)
        self.assertIn("Line 3", result)

    def test_format_conversation_with_assistant_role(self):
        """Test formatting with 'assistant' role."""
        conversation = [
            {"role": "assistant", "content": "Assistant message"}
        ]

        result = format_conversation_as_text(conversation)
        self.assertIn("ASSISTANT", result)

    def test_format_conversation_case_insensitive_role(self):
        """Test that role is case-insensitive."""
        conversation = [
            {"role": "USER", "content": "Test"},
            {"role": "User", "content": "Test2"}
        ]

        result = format_conversation_as_text(conversation)
        # Both should be converted to uppercase
        self.assertEqual(result.count("(USER)"), 2)


class TestFormatConversationAsMarkdown(unittest.TestCase):
    """Test cases for format_conversation_as_markdown function."""

    def test_format_conversation_markdown_basic(self):
        """Test basic markdown formatting."""
        conversation = [
            {"role": "user", "content": "Hello!"},
            {"role": "ai", "content": "Hi there!"}
        ]

        result = format_conversation_as_markdown(conversation)

        self.assertIn("## Message 1 (USER)", result)
        self.assertIn("Hello!", result)
        self.assertIn("## Message 2 (AI)", result)
        self.assertIn("Hi there!", result)

    def test_format_conversation_markdown_with_colors(self):
        """Test markdown formatting with colors."""
        conversation = [
            {"role": "user", "content": "Test"}
        ]

        result = format_conversation_as_markdown(
            conversation,
            user_message_color="#FF0000"
        )

        self.assertIn("color: #FF0000", result)
        self.assertIn("<span", result)

    def test_format_conversation_markdown_empty(self):
        """Test markdown formatting of empty conversation."""
        conversation = []
        result = format_conversation_as_markdown(conversation)
        self.assertEqual(result, "")

    def test_format_conversation_markdown_with_xml_tags(self):
        """Test markdown formatting with XML-like tags."""
        conversation = [
            {"role": "user", "content": "<thinking>This is a thought</thinking>"}
        ]

        result = format_conversation_as_markdown(conversation)

        # Should format XML tags
        self.assertIn("thinking", result)

    def test_format_conversation_markdown_without_xml(self):
        """Test markdown formatting without XML tags."""
        conversation = [
            {"role": "user", "content": "Just plain text"}
        ]

        result = format_conversation_as_markdown(conversation)
        self.assertIn("Just plain text", result)

    def test_format_conversation_markdown_ai_color(self):
        """Test markdown with AI message color."""
        conversation = [
            {"role": "ai", "content": "AI response"}
        ]

        result = format_conversation_as_markdown(
            conversation,
            ai_message_color="#0000FF"
        )

        self.assertIn("color: #0000FF", result)

    def test_format_conversation_markdown_both_colors(self):
        """Test markdown with both user and AI colors."""
        conversation = [
            {"role": "user", "content": "User message"},
            {"role": "ai", "content": "AI message"}
        ]

        result = format_conversation_as_markdown(
            conversation,
            user_message_color="#FF0000",
            ai_message_color="#0000FF"
        )

        self.assertIn("#FF0000", result)
        self.assertIn("#0000FF", result)

    def test_format_conversation_markdown_missing_role(self):
        """Test markdown formatting with missing role."""
        conversation = [
            {"content": "No role"}
        ]

        result = format_conversation_as_markdown(conversation)
        self.assertIn("UNKNOWN", result)

    def test_format_conversation_markdown_complex_xml(self):
        """Test markdown with nested XML tags."""
        conversation = [
            {"role": "user", "content": "<outer>Content<inner>Nested</inner></outer>"}
        ]

        result = format_conversation_as_markdown(conversation)
        # Should handle XML tags
        self.assertIn("outer", result)


class TestIntegration(unittest.TestCase):
    """Integration tests for JSON formatting utilities."""

    def test_prettify_and_format_conversation(self):
        """Test prettifying conversation JSON and then formatting it."""
        conversation_json = [
            {"role": "user", "content": "Hello"},
            {"role": "ai", "content": "Hi"}
        ]

        # Prettify the JSON
        pretty = prettify_json(conversation_json)
        self.assertIn("role", pretty)

        # Format as text
        text = format_conversation_as_text(conversation_json)
        self.assertIn("Hello", text)

        # Format as markdown
        markdown = format_conversation_as_markdown(conversation_json)
        self.assertIn("##", markdown)

    def test_format_same_conversation_different_outputs(self):
        """Test formatting same conversation in different formats."""
        conversation = [
            {"role": "user", "content": "Test message"}
        ]

        text = format_conversation_as_text(conversation)
        markdown = format_conversation_as_markdown(conversation)
        json_str = prettify_json(conversation)

        # All should contain the content
        self.assertIn("Test message", text)
        self.assertIn("Test message", markdown)
        self.assertIn("Test message", json_str)

        # But formats should differ
        self.assertIn("##", markdown)
        self.assertNotIn("##", text)
        self.assertIn("[", json_str)


if __name__ == "__main__":
    unittest.main()
