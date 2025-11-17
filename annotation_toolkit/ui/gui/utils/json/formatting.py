"""
JSON formatting utilities for the GUI.

This module provides functions for formatting, cleaning, and converting JSON data.
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple, Union


def format_json_string(
    data: Union[str, Dict, List],
    indent: int = 2,
    ensure_ascii: bool = False
) -> str:
    """
    Format JSON data with indentation (pretty-print).

    Args:
        data: JSON data (string, dict, or list)
        indent: Number of spaces for indentation
        ensure_ascii: Whether to escape non-ASCII characters

    Returns:
        Formatted JSON string

    Raises:
        json.JSONDecodeError: If the input string is not valid JSON
    """
    # Parse if string
    if isinstance(data, str):
        data = json.loads(data)

    return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)


def minify_json_string(data: Union[str, Dict, List]) -> str:
    """
    Minify JSON data by removing all whitespace.

    Args:
        data: JSON data (string, dict, or list)

    Returns:
        Minified JSON string (single line)

    Raises:
        json.JSONDecodeError: If the input string is not valid JSON
    """
    # Parse if string
    if isinstance(data, str):
        data = json.loads(data)

    return json.dumps(data, separators=(',', ':'))


def clean_json_string(text: str) -> str:
    """
    Clean JSON string by removing common issues.

    Handles:
    - Trailing non-JSON characters
    - Leading/trailing whitespace
    - BOM characters
    - Common escape sequence issues

    Args:
        text: JSON string to clean

    Returns:
        Cleaned JSON string
    """
    # Remove BOM if present
    text = text.lstrip('\ufeff')

    # Strip leading/trailing whitespace
    text = text.strip()

    # Remove trailing non-JSON characters after last }
    match = re.search(r'(.*[}\]])\s*[^\s{}[\],:"\'0-9a-zA-Z_-]*$', text)
    if match:
        text = match.group(1)

    # Fix common quote issues (smart quotes)
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")

    return text


def format_xml_tags_in_json(text: str, max_line_length: int = 80) -> str:
    """
    Format XML tags within JSON strings for better readability.

    Finds XML-like tags in JSON strings and formats them with proper indentation
    and line breaks.

    Args:
        text: JSON text containing XML tags
        max_line_length: Maximum line length before breaking

    Returns:
        JSON text with formatted XML tags
    """
    def format_xml_content(match: re.Match) -> str:
        """Format the XML content within a match."""
        content = match.group(1)

        # Don't format if content is short
        if len(content) < max_line_length:
            return match.group(0)

        # Add line breaks after tags
        formatted = re.sub(r'(<[^>]+>)', r'\1\n', content)

        # Indent nested tags
        lines = formatted.split('\n')
        indent_level = 0
        result_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Decrease indent for closing tags
            if line.startswith('</'):
                indent_level = max(0, indent_level - 1)

            # Add indented line
            result_lines.append('  ' * indent_level + line)

            # Increase indent for opening tags (not self-closing)
            if line.startswith('<') and not line.startswith('</') and not line.endswith('/>'):
                indent_level += 1

        formatted_content = '\\n'.join(result_lines)
        return f'"{formatted_content}"'

    # Find strings containing XML-like tags
    pattern = r'"([^"]*<[^>]+>[^"]*)"'
    return re.sub(pattern, format_xml_content, text)


def detect_conversation_format(data: Union[Dict, List]) -> str:
    """
    Detect the format of conversation JSON data.

    Supported formats:
    - "standard": [{"role": "user", "content": "..."}, ...]
    - "chat_history": {"chat_history": [...]}
    - "message_v2": [{"source": "user", "version": "message_v2", "body": "..."}, ...]
    - "unknown": Format not recognized

    Args:
        data: Parsed JSON data

    Returns:
        Format name as string
    """
    # Check for chat_history format
    if isinstance(data, dict) and "chat_history" in data:
        return "chat_history"

    # Check for list formats
    if isinstance(data, list) and len(data) > 0:
        first_item = data[0]

        # Standard format
        if isinstance(first_item, dict):
            if "role" in first_item and "content" in first_item:
                return "standard"

            # Message_v2 format
            if "source" in first_item and "version" in first_item:
                if first_item.get("version") == "message_v2":
                    return "message_v2"

    return "unknown"


def normalize_conversation_format(
    data: Union[Dict, List],
    target_format: str = "standard"
) -> List[Dict[str, str]]:
    """
    Normalize conversation data to a standard format.

    Args:
        data: Conversation data in any supported format
        target_format: Target format (default: "standard")

    Returns:
        List of conversation turns in standard format

    Raises:
        ValueError: If format is not supported
    """
    current_format = detect_conversation_format(data)

    # Already in target format
    if current_format == target_format:
        return data if isinstance(data, list) else []

    # Convert from chat_history format
    if current_format == "chat_history":
        if isinstance(data, dict) and "chat_history" in data:
            return normalize_conversation_format(
                data["chat_history"],
                target_format
            )

    # Convert from message_v2 format
    if current_format == "message_v2":
        result = []
        for item in data:
            if isinstance(item, dict):
                role = item.get("source", "user")
                # Map source to standard role
                if role not in ["user", "assistant", "system"]:
                    role = "user"  # Default to user

                content = item.get("body", "") or item.get("content", "")

                result.append({
                    "role": role,
                    "content": content
                })
        return result

    # Unknown format
    if current_format == "unknown":
        # Try to extract something meaningful
        if isinstance(data, list):
            result = []
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    # Try to find content
                    content = (
                        item.get("content") or
                        item.get("text") or
                        item.get("message") or
                        item.get("body") or
                        str(item)
                    )

                    # Try to find role
                    role = (
                        item.get("role") or
                        item.get("source") or
                        ("assistant" if i % 2 == 1 else "user")
                    )

                    result.append({
                        "role": role,
                        "content": content
                    })
            return result

    # Return empty list if conversion fails
    return []


def validate_json_syntax(text: str) -> Tuple[bool, Optional[str]]:
    """
    Validate JSON syntax and return detailed error information.

    Args:
        text: JSON string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        json.loads(text)
        return (True, None)
    except json.JSONDecodeError as e:
        error_msg = f"Line {e.lineno}, column {e.colno}: {e.msg}"
        return (False, error_msg)
    except Exception as e:
        return (False, str(e))


def extract_json_from_text(text: str) -> Optional[str]:
    """
    Extract JSON from text that may contain non-JSON content.

    Looks for JSON objects {} or arrays [] in the text.

    Args:
        text: Text potentially containing JSON

    Returns:
        Extracted JSON string, or None if not found
    """
    # Try to find JSON object
    obj_match = re.search(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', text, re.DOTALL)
    if obj_match:
        return obj_match.group(0)

    # Try to find JSON array
    arr_match = re.search(r'\[(?:[^\[\]]|(?:\[[^\[\]]*\]))*\]', text, re.DOTALL)
    if arr_match:
        return arr_match.group(0)

    return None


def count_json_elements(data: Union[Dict, List]) -> Dict[str, int]:
    """
    Count various elements in JSON data.

    Args:
        data: Parsed JSON data

    Returns:
        Dictionary with counts of different elements
    """
    counts = {
        "objects": 0,
        "arrays": 0,
        "strings": 0,
        "numbers": 0,
        "booleans": 0,
        "nulls": 0,
        "total_keys": 0,
    }

    def count_recursive(item: Any) -> None:
        """Recursively count elements."""
        if isinstance(item, dict):
            counts["objects"] += 1
            counts["total_keys"] += len(item)
            for value in item.values():
                count_recursive(value)
        elif isinstance(item, list):
            counts["arrays"] += 1
            for value in item:
                count_recursive(value)
        elif isinstance(item, str):
            counts["strings"] += 1
        elif isinstance(item, bool):
            counts["booleans"] += 1
        elif isinstance(item, (int, float)):
            counts["numbers"] += 1
        elif item is None:
            counts["nulls"] += 1

    count_recursive(data)
    return counts


def get_json_summary(data: Union[str, Dict, List]) -> str:
    """
    Get a human-readable summary of JSON data.

    Args:
        data: JSON data (string, dict, or list)

    Returns:
        Summary string
    """
    # Parse if string
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return "Invalid JSON"

    # Get counts
    counts = count_json_elements(data)

    # Build summary
    summary_parts = []

    if isinstance(data, dict):
        summary_parts.append(f"Object with {len(data)} top-level keys")
    elif isinstance(data, list):
        summary_parts.append(f"Array with {len(data)} items")

    if counts["total_keys"] > 0:
        summary_parts.append(f"{counts['total_keys']} total keys")

    if counts["objects"] > 1:
        summary_parts.append(f"{counts['objects']} nested objects")

    if counts["arrays"] > 0:
        summary_parts.append(f"{counts['arrays']} arrays")

    return ", ".join(summary_parts) if summary_parts else "Empty JSON"
