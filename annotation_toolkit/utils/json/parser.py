"""
JSON parsing utilities for the annotation toolkit.

This module provides functions for parsing and fixing JSON data,
with a focus on chat history formats.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Union

# Configure a specific logger for JSON parsing
logger = logging.getLogger("annotation_toolkit.json_parser")


def parse_json_string(json_str: str) -> Any:
    """
    Parse a JSON string, handling common issues.

    Args:
        json_str: The JSON string to parse.

    Returns:
        The parsed JSON data.

    Raises:
        json.JSONDecodeError: If the JSON string cannot be parsed.
    """
    # Clean the input string
    cleaned_str = clean_json_string(json_str)

    try:
        # Try to parse the cleaned string
        return json.loads(cleaned_str)
    except json.JSONDecodeError as e:
        logger.debug(f"Failed to parse cleaned JSON: {e}")

        # Try to fix common issues
        fixed_str = fix_common_json_issues(cleaned_str)

        try:
            # Try to parse the fixed string
            return json.loads(fixed_str)
        except json.JSONDecodeError as e:
            # If still failing, try the chat history fixer
            logger.debug(f"Failed to parse fixed JSON: {e}")

            if '"chat_history"' in fixed_str:
                logger.debug("Attempting to use chat history fixer")
                try:
                    from ...chat_history_fixer import fix_chat_history_json

                    fixed_json = fix_chat_history_json(fixed_str)

                    if fixed_json:
                        if isinstance(fixed_json, str):
                            return json.loads(fixed_json)
                        else:
                            return fixed_json
                except (ImportError, Exception) as e:
                    logger.debug(f"Chat history fixer failed: {e}")

            # If all else fails, raise the original error
            raise


def clean_json_string(json_str: str) -> str:
    """
    Clean a JSON string by removing common issues.

    Args:
        json_str: The JSON string to clean.

    Returns:
        The cleaned JSON string.
    """
    # Remove leading/trailing whitespace
    cleaned = json_str.strip()

    # Remove code block markers if present
    if cleaned.startswith("```") and cleaned.endswith("```"):
        lines = cleaned.split("\n")
        if len(lines) > 2:
            cleaned = "\n".join(lines[1:-1])
        else:
            cleaned = cleaned.strip("`")

    # Handle potential Unicode issues
    cleaned = cleaned.replace("\u2028", " ").replace("\u2029", " ")

    # Handle potential trailing commas in objects and arrays
    cleaned = re.sub(r",\s*}", "}", cleaned)
    cleaned = re.sub(r",\s*]", "]", cleaned)

    # Handle potential JavaScript-style comments
    cleaned = re.sub(r"//.*?\n", "\n", cleaned)
    cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL)

    # Handle special characters that might cause issues
    cleaned = cleaned.replace("\u200b", "")  # Zero-width space
    cleaned = cleaned.replace("\ufeff", "")  # Zero-width no-break space (BOM)

    # Handle control characters (ASCII 0-31)
    cleaned = escape_control_characters(cleaned)

    # Fix common encoding issues with Latin characters
    cleaned = cleaned.replace("√≠", "í")
    cleaned = cleaned.replace("√≥", "ó")
    cleaned = cleaned.replace("√°", "á")
    cleaned = cleaned.replace("√©", "é")
    cleaned = cleaned.replace("√±", "ñ")
    cleaned = cleaned.replace("√∫", "ú")
    cleaned = cleaned.replace("√º", "ü")
    cleaned = cleaned.replace("√Å", "Á")
    cleaned = cleaned.replace("√â", "É")
    cleaned = cleaned.replace("√ç", "Í")
    cleaned = cleaned.replace("√ì", "Ó")
    cleaned = cleaned.replace("√ö", "Ú")
    cleaned = cleaned.replace("√±", "ñ")
    cleaned = cleaned.replace("√ë", "Ñ")

    return cleaned


def escape_control_characters(json_str: str) -> str:
    """
    Escape or remove control characters in a JSON string.

    Control characters (ASCII 0-31) are not allowed in JSON strings
    unless they are properly escaped.

    Args:
        json_str: The JSON string that may contain control characters.

    Returns:
        The JSON string with control characters properly escaped.
    """
    result = ""
    for char in json_str:
        # Check if the character is a control character (ASCII 0-31)
        if ord(char) < 32:
            # Handle common control characters
            if char == "\n":
                result += "\\n"
            elif char == "\r":
                result += "\\r"
            elif char == "\t":
                result += "\\t"
            elif char == "\b":
                result += "\\b"
            elif char == "\f":
                result += "\\f"
            else:
                # For other control characters, use Unicode escape sequence
                result += f"\\u{ord(char):04x}"
        else:
            result += char

    return result


def fix_common_json_issues(json_str: str) -> str:
    """
    Fix common JSON syntax issues.

    Args:
        json_str: The JSON string to fix.

    Returns:
        The fixed JSON string.
    """
    # Fix unescaped dollar signs (common in price values)
    json_str = json_str.replace("$$", "\\$\\$")

    # Fix missing quotes around string values
    json_str = re.sub(
        r'"([^"]+)":\s*([^"{}\[\],\s][^{}\[\],]*?)(?=,|\}|\]|$)', r'"\1":"\2"', json_str
    )

    # Fix missing commas between fields
    json_str = re.sub(r'"([^"]+)"\s*"([^"]+)":', r'"\1","\2":', json_str)

    # Fix issues with XML tags in JSON strings
    # Escape any < and > characters that might be causing issues
    def escape_xml_tags(match):
        content = match.group(1)
        # Don't escape already escaped tags
        if "\\<" in content or "\\>" in content:
            return match.group(0)
        # Escape < and > in the content
        content = content.replace("<", "\\u003C").replace(">", "\\u003E")
        return f'"{content}"'

    # Replace content in string literals
    json_str = re.sub(
        r'"([^"\\]*(?:\\.[^"\\]*)*)"', escape_xml_tags, json_str, flags=re.DOTALL
    )

    return json_str


def extract_chat_history(data: Any) -> List[Dict[str, str]]:
    """
    Extract chat history from parsed JSON data.

    Args:
        data: The parsed JSON data.

    Returns:
        A list of chat messages.

    Raises:
        ValueError: If the data does not contain a valid chat history.
    """
    logger.debug(f"Extracting chat history from data of type: {type(data).__name__}")

    # If data is a dictionary with a chat_history key
    if isinstance(data, dict) and "chat_history" in data:
        logger.debug("Found chat_history key in dictionary")
        chat_history = data["chat_history"]

        if isinstance(chat_history, list):
            logger.debug(f"chat_history is a list with {len(chat_history)} items")

            # Validate that all messages have role and content
            valid_messages = []
            for i, msg in enumerate(chat_history):
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    # Create a new message with just role and content
                    valid_messages.append(
                        {"role": msg["role"], "content": msg["content"]}
                    )
                else:
                    logger.warning(f"Message {i} is not valid: {msg}")

            if valid_messages:
                logger.debug(f"Extracted {len(valid_messages)} valid messages")
                return valid_messages

    # If data is a list of messages
    elif isinstance(data, list):
        logger.debug(f"Data is a list with {len(data)} items")

        # Validate that all items are messages with role and content
        valid_messages = []
        for i, msg in enumerate(data):
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                # Create a new message with just role and content
                valid_messages.append({"role": msg["role"], "content": msg["content"]})
            else:
                logger.warning(f"Item {i} is not a valid message: {msg}")

        if valid_messages:
            logger.debug(f"Extracted {len(valid_messages)} valid messages")
            return valid_messages

    # If we get here, we couldn't extract a valid chat history
    logger.error("No message-like structures found in data")
    raise ValueError("Not a conversation format")


def parse_conversation_data(data: Union[str, Dict, List]) -> List[Dict[str, str]]:
    """
    Parse conversation data from various formats.

    Args:
        data: The data to parse. Can be a JSON string, a dictionary, or a list.

    Returns:
        A list of chat messages.

    Raises:
        ValueError: If the data does not contain a valid conversation.
    """
    logger.info(f"Parsing conversation data of type: {type(data).__name__}")

    # If data is a string, try to parse it as JSON
    if isinstance(data, str):
        logger.debug("Data is a string, attempting to parse as JSON")
        try:
            parsed_data = parse_json_string(data)
            return extract_chat_history(parsed_data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse string as JSON: {e}")
            # If JSON parsing fails, try to parse as text conversation
            try:
                logger.debug("Attempting to parse as text conversation")
                return parse_text_conversation(data)
            except ValueError as e:
                logger.error(f"Failed to parse as text conversation: {e}")
                raise ValueError(f"Invalid conversation format: {e}")

    # If data is already a dictionary or list, try to extract chat history
    elif isinstance(data, (dict, list)):
        try:
            return extract_chat_history(data)
        except ValueError as e:
            logger.error(f"Failed to extract chat history: {e}")
            raise

    # If data is neither a string, dict, nor list, it's invalid
    else:
        logger.error(f"Unsupported data type: {type(data).__name__}")
        raise ValueError(f"Unsupported data type: {type(data).__name__}")


def parse_text_conversation(text: str) -> List[Dict[str, str]]:
    """
    Parse conversation from a text format.

    Expected format:
    ```
    Message 1 (ROLE):
    Content of message 1

    Message 2 (ROLE):
    Content of message 2
    ```

    Args:
        text: The text to parse.

    Returns:
        A list of conversation messages.

    Raises:
        ValueError: If the text does not have the expected format.
    """
    logger.info("Parsing conversation from text format")
    logger.debug(f"Text length: {len(text)} characters")

    # Define a regex pattern to match message headers
    header_pattern = r"Message\s+\d+\s+\(([A-Za-z]+)\):"
    logger.debug(f"Using regex pattern: {header_pattern}")

    # Split the text by message headers
    parts = re.split(header_pattern, text)
    logger.debug(f"Split text into {len(parts)} parts")

    # parts[0] is any text before the first header (should be empty)
    # parts[1] is the role of the first message
    # parts[2] is the content of the first message
    # parts[3] is the role of the second message
    # parts[4] is the content of the second message
    # And so on...

    if len(parts) < 3 or len(parts) % 2 == 0:
        logger.error(f"Invalid conversation format: got {len(parts)} parts")
        raise ValueError("Invalid conversation format")

    messages = []

    for i in range(1, len(parts), 2):
        role = parts[i].lower()
        content = parts[i + 1].strip()
        logger.debug(
            f"Extracted message with role: {role}, content length: {len(content)}"
        )
        messages.append({"role": role, "content": content})

    logger.info(f"Successfully parsed {len(messages)} messages from text")
    return messages


def fix_xml_tags_in_content(content: str) -> str:
    """
    Fix XML-like tags in content to ensure they don't break JSON parsing.

    Args:
        content: The content string that may contain XML tags.

    Returns:
        The content with properly escaped XML tags.
    """
    if "<" not in content or ">" not in content:
        return content

    # Check if the content contains XML-like tags
    xml_pattern = r"<([A-Za-z_][A-Za-z0-9_]*)>(.*?)</\1>"

    # If there are XML tags, ensure they're properly formatted
    if re.search(xml_pattern, content, re.DOTALL):
        # No need to escape properly formatted XML tags
        return content

    # For potentially problematic tags, escape < and >
    content = content.replace("<", "\\u003C").replace(">", "\\u003E")

    return content


def is_valid_chat_message(msg: Dict) -> bool:
    """
    Check if a dictionary is a valid chat message.

    Args:
        msg: The dictionary to check.

    Returns:
        True if the dictionary is a valid chat message, False otherwise.
    """
    if not isinstance(msg, dict):
        return False

    # Check if it has role and content keys
    if "role" not in msg or "content" not in msg:
        return False

    # Check if role and content are strings
    if not isinstance(msg["role"], str) or not isinstance(msg["content"], str):
        return False

    return True


def normalize_chat_message(msg: Dict) -> Dict[str, str]:
    """
    Normalize a chat message to ensure it has the expected format.

    Args:
        msg: The message to normalize.

    Returns:
        A normalized message with role and content keys.
    """
    if is_valid_chat_message(msg):
        return {"role": msg["role"], "content": msg["content"]}

    # Try to extract role and content from other fields
    role = None
    content = None

    # Try to determine the role
    for key in ["role", "source", "user", "assistant", "system", "ai"]:
        if key in msg and isinstance(msg[key], str):
            role = msg[key]
            if role in ["user", "assistant", "system", "ai"]:
                break

    # Try to determine the content
    for key in ["content", "body", "text", "message", "value"]:
        if key in msg and isinstance(msg[key], str):
            content = msg[key]
            break

    if role and content:
        return {"role": role, "content": content}

    raise ValueError("Could not normalize message")
