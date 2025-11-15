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
    is_valid_json,
    parse_json_string,
    clean_json_string,
    escape_control_characters,
    fix_common_json_issues,
    extract_chat_history,
    parse_conversation_data,
    parse_text_conversation,
    fix_xml_tags_in_content,
    is_valid_chat_message,
    normalize_chat_message,
)
from annotation_toolkit.utils.errors import ParsingError


class TestParseJsonString(unittest.TestCase):
    """Test cases for parse_json_string function."""

    def test_parse_valid_json(self):
        """Test parsing valid JSON."""
        json_str = '{"key": "value", "number": 42}'
        result = parse_json_string(json_str)
        self.assertEqual(result, {"key": "value", "number": 42})

    def test_parse_with_trailing_comma(self):
        """Test parsing JSON with trailing comma."""
        json_str = '{"key": "value",}'
        result = parse_json_string(json_str)
        self.assertIsNotNone(result)
        self.assertEqual(result.get("key"), "value")

    def test_parse_with_comments(self):
        """Test parsing JSON with embedded comments."""
        json_str = '{"key": "value" /* comment */}'
        result = parse_json_string(json_str)
        self.assertEqual(result.get("key"), "value")

    def test_parse_with_code_blocks(self):
        """Test parsing JSON wrapped in code blocks."""
        json_str = '```\n{"key": "value"}\n```'
        result = parse_json_string(json_str)
        self.assertEqual(result, {"key": "value"})

    def test_parse_with_unicode_issues(self):
        """Test parsing JSON with Unicode line separators."""
        json_str = '{"key":\u2028"value"}'
        result = parse_json_string(json_str)
        self.assertEqual(result.get("key"), "value")


class TestCleanJsonString(unittest.TestCase):
    """Test cases for clean_json_string function."""

    def test_clean_with_code_blocks(self):
        """Test cleaning JSON with code blocks."""
        json_str = '```json\n{"key": "value"}\n```'
        result = clean_json_string(json_str)
        self.assertIn('{"key": "value"}', result)
        self.assertNotIn('```', result)

    def test_clean_with_trailing_commas_object(self):
        """Test cleaning JSON with trailing comma in object."""
        json_str = '{"key": "value",}'
        result = clean_json_string(json_str)
        self.assertNotIn(',}', result)

    def test_clean_with_trailing_commas_array(self):
        """Test cleaning JSON with trailing comma in array."""
        json_str = '[1, 2, 3,]'
        result = clean_json_string(json_str)
        self.assertNotIn(',]', result)

    def test_clean_with_line_comments(self):
        """Test cleaning JSON with line comments."""
        json_str = '{"key": "value"} // comment\n{"key2": "value2"}'
        result = clean_json_string(json_str)
        self.assertNotIn('//', result)

    def test_clean_with_block_comments(self):
        """Test cleaning JSON with block comments."""
        json_str = '{"key": "value" /* comment */}'
        result = clean_json_string(json_str)
        self.assertNotIn('/*', result)

    def test_clean_with_zero_width_space(self):
        """Test cleaning JSON with zero-width space."""
        json_str = '{"key":\u200b"value"}'
        result = clean_json_string(json_str)
        self.assertNotIn('\u200b', result)

    def test_clean_with_bom(self):
        """Test cleaning JSON with BOM."""
        json_str = '\ufeff{"key": "value"}'
        result = clean_json_string(json_str)
        self.assertNotIn('\ufeff', result)

    def test_clean_with_control_characters(self):
        """Test cleaning JSON with control characters."""
        json_str = '{"key": "value\x00\x01"}'
        result = clean_json_string(json_str)
        # Control chars should be escaped
        self.assertNotIn('\x00', result)

    def test_clean_with_latin_encoding_issues(self):
        """Test cleaning JSON with Latin encoding issues."""
        json_str = '{"name": "Jos√©"}'
        result = clean_json_string(json_str)
        self.assertIn('José', result)


class TestEscapeControlCharacters(unittest.TestCase):
    """Test cases for escape_control_characters function."""

    def test_escape_null_byte(self):
        """Test escaping null byte."""
        text = "Hello\x00World"
        result = escape_control_characters(text)
        self.assertIn('\\u0000', result)
        self.assertNotIn('\x00', result)

    def test_preserve_newline(self):
        """Test that newlines are escaped."""
        text = "Line1\nLine2"
        result = escape_control_characters(text)
        self.assertIn('\\n', result)

    def test_preserve_tab(self):
        """Test that tabs are escaped."""
        text = "Col1\tCol2"
        result = escape_control_characters(text)
        self.assertIn('\\t', result)

    def test_preserve_carriage_return(self):
        """Test that carriage returns are escaped."""
        text = "Line1\rLine2"
        result = escape_control_characters(text)
        self.assertIn('\\r', result)

    def test_escape_backspace(self):
        """Test escaping backspace."""
        text = "Text\bBackspace"
        result = escape_control_characters(text)
        self.assertIn('\\b', result)

    def test_escape_form_feed(self):
        """Test escaping form feed."""
        text = "Page1\fPage2"
        result = escape_control_characters(text)
        self.assertIn('\\f', result)

    def test_normal_text_unchanged(self):
        """Test that normal text is unchanged."""
        text = "Normal text with no control characters"
        result = escape_control_characters(text)
        # Should have escaped versions if newlines/tabs were present
        self.assertIsInstance(result, str)


class TestFixCommonJsonIssues(unittest.TestCase):
    """Test cases for fix_common_json_issues function."""

    def test_fix_double_dollar_signs(self):
        """Test fixing double dollar signs."""
        json_str = '{"price": "$$10"}'
        result = fix_common_json_issues(json_str)
        self.assertIn('\\$\\$', result)

    def test_fix_xml_tags_in_strings(self):
        """Test fixing XML tags in strings."""
        json_str = '{"content": "<thinking>thought</thinking>"}'
        result = fix_common_json_issues(json_str)
        # XML tags should be escaped
        self.assertIsInstance(result, str)


class TestExtractChatHistory(unittest.TestCase):
    """Test cases for extract_chat_history function."""

    def test_extract_from_dict_with_chat_history_key(self):
        """Test extracting from dict with chat_history key."""
        data = {
            "chat_history": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi"}
            ]
        }
        result = extract_chat_history(data)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["role"], "user")
        self.assertEqual(result[0]["content"], "Hello")

    def test_extract_from_list_of_messages(self):
        """Test extracting from list of messages."""
        data = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"}
        ]
        result = extract_chat_history(data)
        self.assertEqual(len(result), 2)

    def test_extract_filters_invalid_messages(self):
        """Test that invalid messages are filtered out."""
        data = [
            {"role": "user", "content": "Valid"},
            {"invalid": "message"},
            {"role": "assistant", "content": "Also valid"}
        ]
        result = extract_chat_history(data)
        self.assertEqual(len(result), 2)

    def test_extract_from_invalid_data_raises_error(self):
        """Test that invalid data raises ValueError."""
        with self.assertRaises(ValueError):
            extract_chat_history({"invalid": "data"})

    def test_extract_preserves_only_role_and_content(self):
        """Test that extraction preserves only role and content."""
        data = [
            {"role": "user", "content": "Hello", "timestamp": "2024-01-01"}
        ]
        result = extract_chat_history(data)
        self.assertEqual(set(result[0].keys()), {"role", "content"})


class TestParseConversationData(unittest.TestCase):
    """Test cases for parse_conversation_data function."""

    def test_parse_json_string(self):
        """Test parsing conversation from JSON string."""
        json_str = '[{"role": "user", "content": "Hello"}]'
        result = parse_conversation_data(json_str)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["role"], "user")

    def test_parse_dict_with_chat_history(self):
        """Test parsing conversation from dict."""
        data = {
            "chat_history": [
                {"role": "user", "content": "Hello"}
            ]
        }
        result = parse_conversation_data(data)
        self.assertEqual(len(result), 1)

    def test_parse_list_of_messages(self):
        """Test parsing conversation from list."""
        data = [{"role": "user", "content": "Hello"}]
        result = parse_conversation_data(data)
        self.assertEqual(len(result), 1)

    def test_parse_text_conversation_fallback(self):
        """Test falling back to text conversation parser."""
        text = "Message 1 (user):\nHello\n\nMessage 2 (assistant):\nHi"
        result = parse_conversation_data(text)
        self.assertEqual(len(result), 2)

    def test_parse_invalid_type_raises_error(self):
        """Test that invalid type raises ValueError."""
        with self.assertRaises(ValueError):
            parse_conversation_data(123)


class TestParseTextConversation(unittest.TestCase):
    """Test cases for parse_text_conversation function."""

    def test_parse_simple_conversation(self):
        """Test parsing simple text conversation."""
        text = "Message 1 (user):\nHello\n\nMessage 2 (assistant):\nHi there"
        result = parse_text_conversation(text)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["role"], "user")
        self.assertEqual(result[0]["content"], "Hello")

    def test_parse_conversation_with_multiline_content(self):
        """Test parsing conversation with multiline content."""
        text = "Message 1 (user):\nLine 1\nLine 2\n\nMessage 2 (assistant):\nResponse"
        result = parse_text_conversation(text)
        self.assertEqual(len(result), 2)
        self.assertIn("Line 1", result[0]["content"])

    def test_parse_invalid_format_raises_error(self):
        """Test that invalid format raises ValueError."""
        with self.assertRaises(ValueError):
            parse_text_conversation("No message format here")


class TestFixXmlTagsInContent(unittest.TestCase):
    """Test cases for fix_xml_tags_in_content function."""

    def test_fix_properly_formatted_xml_tags(self):
        """Test that properly formatted XML tags are preserved."""
        content = "<thinking>This is a thought</thinking>"
        result = fix_xml_tags_in_content(content)
        # Properly formatted tags should be preserved
        self.assertIn("thinking", result)

    def test_fix_malformed_xml_tags(self):
        """Test fixing malformed XML tags."""
        content = "<unclosed tag"
        result = fix_xml_tags_in_content(content)
        # Should escape the tags
        self.assertIsInstance(result, str)

    def test_no_xml_tags_unchanged(self):
        """Test that content without XML tags is unchanged."""
        content = "Just plain text"
        result = fix_xml_tags_in_content(content)
        self.assertEqual(result, content)

    def test_nested_xml_tags(self):
        """Test handling nested XML tags."""
        content = "<outer><inner>Content</inner></outer>"
        result = fix_xml_tags_in_content(content)
        self.assertIn("outer", result)


class TestIsValidChatMessage(unittest.TestCase):
    """Test cases for is_valid_chat_message function."""

    def test_valid_message(self):
        """Test validation of valid message."""
        message = {"role": "user", "content": "Hello"}
        self.assertTrue(is_valid_chat_message(message))

    def test_missing_role(self):
        """Test validation fails for missing role."""
        message = {"content": "Hello"}
        self.assertFalse(is_valid_chat_message(message))

    def test_missing_content(self):
        """Test validation fails for missing content."""
        message = {"role": "user"}
        self.assertFalse(is_valid_chat_message(message))

    def test_non_string_role(self):
        """Test validation fails for non-string role."""
        message = {"role": 123, "content": "Hello"}
        self.assertFalse(is_valid_chat_message(message))

    def test_non_string_content(self):
        """Test validation fails for non-string content."""
        message = {"role": "user", "content": 123}
        self.assertFalse(is_valid_chat_message(message))

    def test_non_dict_message(self):
        """Test validation fails for non-dict."""
        self.assertFalse(is_valid_chat_message("not a dict"))
        self.assertFalse(is_valid_chat_message(None))


class TestNormalizeChatMessage(unittest.TestCase):
    """Test cases for normalize_chat_message function."""

    def test_normalize_valid_message(self):
        """Test normalizing already valid message."""
        message = {"role": "user", "content": "Hello"}
        result = normalize_chat_message(message)
        self.assertEqual(result, {"role": "user", "content": "Hello"})

    def test_normalize_with_source_field(self):
        """Test normalizing message with 'source' instead of 'role'."""
        message = {"source": "user", "content": "Hello"}
        result = normalize_chat_message(message)
        self.assertEqual(result["role"], "user")

    def test_normalize_with_body_field(self):
        """Test normalizing message with 'body' instead of 'content'."""
        message = {"role": "user", "body": "Hello"}
        result = normalize_chat_message(message)
        self.assertEqual(result["content"], "Hello")

    def test_normalize_with_text_field(self):
        """Test normalizing message with 'text' field."""
        message = {"role": "user", "text": "Hello"}
        result = normalize_chat_message(message)
        self.assertEqual(result["content"], "Hello")

    def test_normalize_invalid_message_raises_error(self):
        """Test that invalid message raises ValueError."""
        with self.assertRaises(ValueError):
            normalize_chat_message({"invalid": "message"})


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
