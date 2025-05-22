"""
JSON formatting utilities for the annotation toolkit.

This module provides functions for formatting JSON data,
including conversation data and other JSON structures.
"""

import json
import re
from typing import Any, Dict, List, Optional, Union

# Import hex_to_ansi_color from color_utils
from ..color_utils import hex_to_ansi_color


def prettify_json(json_data: Union[Dict, List], indent: int = 2) -> str:
    """
    Convert JSON data to a pretty-printed string.

    Args:
        json_data (Union[Dict, List]): The JSON data to prettify.
        indent (int): The indentation level.

    Returns:
        str: A pretty-printed JSON string.

    Raises:
        TypeError: If the data is not JSON-serializable.
    """
    return json.dumps(json_data, indent=indent, ensure_ascii=False)


def format_conversation_as_text(
    conversation: List[Dict[str, str]],
    user_message_color: Optional[str] = None,
    ai_message_color: Optional[str] = None,
    use_colors: bool = False,
) -> str:
    """
    Format a conversation as plain text with optional color formatting.

    Args:
        conversation (List[Dict[str, str]]): The conversation to format.
        user_message_color (Optional[str]): Hex color code for user messages.
        ai_message_color (Optional[str]): Hex color code for AI messages.
        use_colors (bool): Whether to use ANSI color codes in the output.
            Set to False if the terminal doesn't support ANSI colors.

    Returns:
        str: The formatted conversation text.
    """
    result = []
    reset_color = "\033[0m"

    for i, message in enumerate(conversation):
        role = message.get("role", "unknown").lower()
        content = message.get("content", "")

        # Apply color based on role if colors are provided and use_colors is True
        color_code = ""
        if use_colors:
            if role == "user" and user_message_color:
                color_code = hex_to_ansi_color(user_message_color)
            elif role == "ai" and ai_message_color:
                color_code = hex_to_ansi_color(ai_message_color)

        role_display = role.upper()

        if color_code:
            result.append(f"{color_code}Message {i+1} ({role_display}):{reset_color}")
            result.append(f"{color_code}{content}{reset_color}")
        else:
            result.append(f"Message {i+1} ({role_display}):")
            result.append(content)

        result.append("")  # Empty line between messages

    return "\n".join(result)


def format_conversation_as_markdown(
    conversation: List[Dict[str, str]],
    user_message_color: Optional[str] = None,
    ai_message_color: Optional[str] = None,
) -> str:
    """
    Format a conversation as markdown with optional color formatting.

    Args:
        conversation (List[Dict[str, str]]): The conversation to format.
        user_message_color (Optional[str]): Hex color code for user messages.
        ai_message_color (Optional[str]): Hex color code for AI messages.

    Returns:
        str: The formatted conversation markdown.
    """
    result = []

    for i, message in enumerate(conversation):
        role = message.get("role", "unknown").lower()
        content = message.get("content", "")
        role_display = role.upper()

        # Apply color based on role if colors are provided
        if role == "user" and user_message_color:
            result.append(
                f"## <span style='color: {user_message_color};'>Message {i+1} ({role_display})</span>"
            )
        elif role == "ai" and ai_message_color:
            result.append(
                f"## <span style='color: {ai_message_color};'>Message {i+1} ({role_display})</span>"
            )
        else:
            result.append(f"## Message {i+1} ({role_display})")

        result.append("")  # Empty line

        # Format XML-like tags in content if present
        if "<" in content and ">" in content:
            # Check for XML-like tags
            xml_pattern = r"(<([A-Za-z_][A-Za-z0-9_]*)>)(.*?)(</\2>)"

            # Function to format XML tags in HTML
            def format_xml_tag(match):
                open_tag = match.group(1)
                tag_name = match.group(2)
                content = match.group(3)
                close_tag = match.group(4)

                return f"""<pre style="margin: 0; padding: 0;">
<span style="color: #9c27b0; font-weight: bold;">{open_tag}</span>
        {content}
<span style="color: #9c27b0; font-weight: bold;">{close_tag}</span>
</pre>"""

            # Replace XML tags with formatted HTML
            content = re.sub(xml_pattern, format_xml_tag, content, flags=re.DOTALL)

        # Apply color to content as well
        if role == "user" and user_message_color:
            result.append(f"<div style='color: {user_message_color};'>{content}</div>")
        elif role == "ai" and ai_message_color:
            result.append(f"<div style='color: {ai_message_color};'>{content}</div>")
        else:
            result.append(content)

        result.append("")  # Empty line between messages

    return "\n".join(result)
