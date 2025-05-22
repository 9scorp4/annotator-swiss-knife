"""
JSON utilities for the annotation toolkit.

This module provides functions and classes for parsing, fixing, and formatting JSON data.
"""

from .formatter import (
    format_conversation_as_markdown,
    format_conversation_as_text,
    prettify_json,
)
from .parser import (
    clean_json_string,
    escape_control_characters,
    extract_chat_history,
    fix_common_json_issues,
    fix_xml_tags_in_content,
    is_valid_chat_message,
    normalize_chat_message,
    parse_conversation_data,
    parse_json_string,
    parse_text_conversation,
)

__all__ = [
    # Parser functions
    "parse_json_string",
    "clean_json_string",
    "escape_control_characters",
    "fix_common_json_issues",
    "extract_chat_history",
    "parse_conversation_data",
    "parse_text_conversation",
    "fix_xml_tags_in_content",
    "is_valid_chat_message",
    "normalize_chat_message",
    # Formatter functions
    "prettify_json",
    "format_conversation_as_text",
    "format_conversation_as_markdown",
]
