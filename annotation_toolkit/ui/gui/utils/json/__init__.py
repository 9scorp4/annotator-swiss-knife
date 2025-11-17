"""
JSON utilities for the annotation toolkit GUI.

This module provides utilities for JSON formatting, validation, and conversion.
"""

from .formatting import (
    format_json_string,
    minify_json_string,
    clean_json_string,
    format_xml_tags_in_json,
    detect_conversation_format,
    normalize_conversation_format,
)

__all__ = [
    "format_json_string",
    "minify_json_string",
    "clean_json_string",
    "format_xml_tags_in_json",
    "detect_conversation_format",
    "normalize_conversation_format",
]
