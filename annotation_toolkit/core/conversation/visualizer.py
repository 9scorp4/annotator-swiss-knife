"""
JSON visualization tool.

This module implements a tool for visualizing and formatting JSON data
including conversation data and other JSON structures.
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from ...core.base import JsonAnnotationTool, ToolExecutionError
from ...utils import logger
from ...utils.json.formatter import (
    format_conversation_as_markdown,
    format_conversation_as_text,
    prettify_json,
)
from ...utils.json.parser import parse_conversation_data


class JsonVisualizer(JsonAnnotationTool):
    """
    Tool for visualizing and formatting JSON data.
    """

    def __init__(
        self,
        output_format: str = "text",
        user_message_color: Optional[str] = None,
        ai_message_color: Optional[str] = None,
    ):
        """
        Initialize the JSON Visualizer.

        Args:
            output_format (str): The output format. Either "text" or "markdown".
            user_message_color (Optional[str]): Hex color code for user messages.
            ai_message_color (Optional[str]): Hex color code for AI messages.

        Raises:
            ValueError: If the output format is not supported.
        """
        super().__init__()
        logger.debug(f"Initializing JsonVisualizer with output_format={output_format}")

        if output_format not in ["text", "markdown"]:
            logger.error(f"Invalid output format: {output_format}")
            raise ValueError("Output format must be either 'text' or 'markdown'")

        self._output_format = output_format
        self._user_message_color = user_message_color
        self._ai_message_color = ai_message_color

        logger.debug(
            f"JsonVisualizer initialized with user_message_color={user_message_color}, ai_message_color={ai_message_color}"
        )

    @property
    def name(self) -> str:
        """
        Return the name of the tool.

        Returns:
            str: The name of the tool.
        """
        return "JSON Visualizer"

    @property
    def description(self) -> str:
        """
        Return a description of the tool.

        Returns:
            str: A description of the tool's functionality.
        """
        return "Visualizes and formats JSON data including conversations and other JSON structures."

    def process_json(self, json_data: Union[Dict, List]) -> str:
        """
        Process JSON data for visualization.

        Args:
            json_data (Union[Dict, List]): The JSON data to process.

        Returns:
            str: The formatted JSON data.

        Raises:
            ToolExecutionError: If the JSON data cannot be processed.
        """
        logger.info("Processing JSON data for visualization")

        try:
            # First try to process as conversation data
            try:
                logger.debug("Attempting to parse as conversation data")
                conversation = parse_conversation_data(json_data)
                logger.info(
                    f"Successfully parsed conversation with {len(conversation)} messages"
                )
                return self.format_conversation(conversation)
            except ValueError:
                # If not a conversation, format as generic JSON
                logger.debug("Not a conversation format, formatting as generic JSON")
                return self.format_generic_json(json_data)
        except Exception as e:
            logger.exception(f"Error processing JSON data: {str(e)}")
            raise ToolExecutionError(str(e))

    def format_generic_json(self, json_data: Union[Dict, List]) -> str:
        """
        Format generic JSON data with proper indentation and key highlighting.

        Args:
            json_data (Union[Dict, List]): The JSON data to format.

        Returns:
            str: The formatted JSON string.
        """
        logger.info(f"Formatting generic JSON data using format: {self._output_format}")

        if self._output_format == "markdown":
            # For markdown, we use a structured representation with HTML formatting
            logger.debug("Creating structured JSON representation with HTML formatting")
            formatted = self._create_structured_json_markdown(json_data)
        else:
            # For text format, we create a structured representation with indentation
            logger.debug("Creating structured JSON representation with text formatting")
            formatted = self._create_structured_json_text(json_data)

        logger.debug(f"Formatted JSON data ({len(formatted)} characters)")
        return formatted

    def _create_structured_json_text(
        self, json_data: Any, indent_level: int = 0
    ) -> str:
        """
        Create a structured text representation of JSON data.

        Args:
            json_data: The JSON data to format.
            indent_level: The current indentation level.

        Returns:
            str: A structured text representation of the JSON data.
        """
        indent = "  " * indent_level
        result = []

        if isinstance(json_data, dict):
            if not json_data:
                return f"{indent}{{}}"

            result.append(f"{indent}{{")
            for i, (key, value) in enumerate(json_data.items()):
                comma = "" if i == len(json_data) - 1 else ","
                if isinstance(value, (dict, list)):
                    result.append(f'{indent}  "{key}": ')
                    result.append(
                        self._create_structured_json_text(value, indent_level + 1)
                        + comma
                    )
                else:
                    # Format the value, handling XML tags if needed
                    if isinstance(value, str) and re.search(
                        r"<[A-Za-z_][A-Za-z0-9_]*>.*?</[A-Za-z_][A-Za-z0-9_]*>", value
                    ):
                        # For strings with XML tags, use direct formatting
                        # First, find all XML tag pairs and their content
                        pattern = r"(<([A-Za-z_][A-Za-z0-9_]*)>)(.*?)(</\2>)"

                        # Format the string with XML tags directly using a raw string
                        # This ensures that the newlines are preserved in the output
                        formatted_value = self._format_xml_tags_raw(value)
                        value_str = formatted_value
                    else:
                        value_str = json.dumps(value)
                    result.append(f'{indent}  "{key}": {value_str}{comma}')
            result.append(f"{indent}}}")

        elif isinstance(json_data, list):
            if not json_data:
                return f"{indent}[]"

            result.append(f"{indent}[")
            for i, item in enumerate(json_data):
                comma = "" if i == len(json_data) - 1 else ","
                if isinstance(item, (dict, list)):
                    result.append(
                        self._create_structured_json_text(item, indent_level + 1)
                        + comma
                    )
                else:
                    # Format the item, handling XML tags if needed
                    if isinstance(item, str) and re.search(
                        r"<[A-Za-z_][A-Za-z0-9_]*>.*?</[A-Za-z_][A-Za-z0-9_]*>", item
                    ):
                        # For strings with XML tags, use special formatting
                        item_str = self._format_text_with_xml_tags(item)
                    else:
                        item_str = json.dumps(item)
                    result.append(f"{indent}  {item_str}{comma}")
            result.append(f"{indent}]")

        else:
            # For primitive types
            if isinstance(json_data, str) and re.search(
                r"<[A-Za-z_][A-Za-z0-9_]*>.*?</[A-Za-z_][A-Za-z0-9_]*>", json_data
            ):
                # For strings with XML tags, use special formatting
                return f"{indent}{self._format_text_with_xml_tags(json_data)}"
            else:
                return f"{indent}{json.dumps(json_data)}"

        return "\n".join(result)

    def _format_text_with_xml_tags(self, text: str) -> str:
        """
        Format a string with XML tags for text display.
        Formats XML tags with the tag on its own line, content indented, and closing tag on its own line.

        Args:
            text: The string containing XML tags.

        Returns:
            str: A formatted string with XML tags made visible and structured.
        """
        # First, escape any existing quotes in the text
        escaped_text = text.replace('"', '\\"')

        # Find all XML tag pairs and their content
        pattern = r"(<([A-Za-z_][A-Za-z0-9_]*)>)(.*?)(</\2>)"

        def format_xml_block(match):
            open_tag = match.group(1)
            tag_name = match.group(2)
            content = match.group(3)
            close_tag = match.group(4)

            # Format the opening tag, content, and closing tag with proper structure
            # Use literal newlines and indentation for direct text display
            formatted = f"\\n{open_tag}\\n        {content}\\n{close_tag}"

            return formatted

        # Replace each XML block with its formatted version
        formatted_text = re.sub(
            pattern, format_xml_block, escaped_text, flags=re.DOTALL
        )

        # Handle any remaining individual tags (self-closing or unpaired)
        remaining_pattern = r"(</?[A-Za-z_][A-Za-z0-9_]*>)"
        formatted_text = re.sub(remaining_pattern, r"\1", formatted_text)

        # Return the text in quotes
        return f'"{formatted_text}"'

    def _create_structured_json_markdown(self, json_data: Any) -> str:
        """
        Create a structured markdown representation of JSON data with HTML formatting.

        Args:
            json_data: The JSON data to format.

        Returns:
            str: A structured HTML representation of the JSON data.
        """
        # Start with a code block for better rendering
        result = ["```json"]

        # Add the prettified JSON
        result.append(prettify_json(json_data, indent=2))

        # Close the code block
        result.append("```")

        # Add a structured view with collapsible sections
        result.append("\n### Structured View\n")
        result.append(self._create_html_json_view(json_data))

        return "\n".join(result)

    def _create_html_json_view(self, json_data: Any, level: int = 0) -> str:
        """
        Create an HTML representation of JSON data with collapsible sections.

        Args:
            json_data: The JSON data to format.
            level: The current nesting level.

        Returns:
            str: An HTML representation of the JSON data.
        """
        indent = "&nbsp;&nbsp;" * level
        result = []

        if isinstance(json_data, dict):
            if not json_data:
                return f"{indent}{{}}"

            result.append(f"{indent}{{")
            for key, value in json_data.items():
                key_html = (
                    f"<span style='color: #0d47a1; font-weight: bold;'>\"{key}\"</span>"
                )

                if isinstance(value, (dict, list)):
                    result.append(
                        f"{indent}&nbsp;&nbsp;{key_html}: {self._create_html_json_view(value, level + 1)}"
                    )
                else:
                    value_html = self._format_json_value(value)
                    result.append(f"{indent}&nbsp;&nbsp;{key_html}: {value_html}")
            result.append(f"{indent}}}")

        elif isinstance(json_data, list):
            if not json_data:
                return f"{indent}[]"

            result.append(f"{indent}[")
            for i, item in enumerate(json_data):
                if isinstance(item, (dict, list)):
                    result.append(
                        f"{indent}&nbsp;&nbsp;{self._create_html_json_view(item, level + 1)}"
                    )
                else:
                    value_html = self._format_json_value(item)
                    result.append(f"{indent}&nbsp;&nbsp;{value_html}")
            result.append(f"{indent}]")

        else:
            # For primitive types
            return self._format_json_value(json_data)

        return "<br>".join(result)

    def _format_json_value(self, value: Any) -> str:
        """
        Format a JSON value with appropriate HTML styling.

        Args:
            value: The value to format.

        Returns:
            str: An HTML-formatted representation of the value.
        """
        if isinstance(value, str):
            # Check if the string contains XML-like tags
            if re.search(
                r"<[A-Za-z_][A-Za-z0-9_]*>.*?</[A-Za-z_][A-Za-z0-9_]*>", value
            ):
                # Format the string with XML tags highlighted
                formatted_value = self._format_string_with_xml_tags(value)
                return f"<span style='color: #2e7d32;'>\"{formatted_value}\"</span>"
            else:
                return f"<span style='color: #2e7d32;'>\"{value}\"</span>"
        elif isinstance(value, bool):
            return f"<span style='color: #0277bd;'>{str(value).lower()}</span>"
        elif value is None:
            return f"<span style='color: #757575;'>null</span>"
        elif isinstance(value, (int, float)):
            return f"<span style='color: #d32f2f;'>{value}</span>"
        else:
            return str(value)

    def _format_string_with_xml_tags(self, text: str) -> str:
        """
        Format a string that contains XML-like tags to make them visible.
        Formats XML tags with the tag on its own line, content indented, and closing tag on its own line.

        Args:
            text: The string containing XML tags.

        Returns:
            str: A formatted string with highlighted and structured XML tags.
        """
        # First, find all XML tag pairs and their content
        pattern = r"(<([A-Za-z_][A-Za-z0-9_]*)>)(.*?)(</\2>)"

        def format_xml_block(match):
            open_tag = match.group(1)
            tag_name = match.group(2)
            content = match.group(3)
            close_tag = match.group(4)

            # Format the opening tag, content, and closing tag with explicit HTML structure
            # Use a very simple approach with pre-formatted text to ensure proper display
            formatted = f"""<pre style="margin: 0; padding: 0;">
<span style="color: #9c27b0; font-weight: bold;">{open_tag}</span>
        {content}
<span style="color: #9c27b0; font-weight: bold;">{close_tag}</span>
</pre>"""

            return formatted

        # Replace each XML block with its formatted version
        formatted = re.sub(pattern, format_xml_block, text, flags=re.DOTALL)

        # Handle any remaining individual tags (self-closing or unpaired)
        remaining_pattern = r"(</?[A-Za-z_][A-Za-z0-9_]*>)"
        formatted = re.sub(
            remaining_pattern,
            r'<span style="color: #9c27b0; font-weight: bold;">\1</span>',
            formatted,
        )

        return formatted

    def parse_conversation_data(
        self, data: Union[str, Dict, List]
    ) -> List[Dict[str, str]]:
        """
        Parse conversation data from various formats.

        Args:
            data (Union[str, Dict, List]): The data to parse.
                Can be a JSON string, a dictionary with a "chat_history" key,
                or a list of message dictionaries.

        Returns:
            List[Dict[str, str]]: A list of conversation messages.

        Raises:
            ToolExecutionError: If the data does not have the expected format.
        """
        logger.info(f"Parsing conversation data of type: {type(data).__name__}")

        try:
            # Use our new JSON parser module
            from ...utils.json.parser import parse_conversation_data as parser_function

            # Call the parser function from our new module
            return parser_function(data)
        except ValueError as e:
            logger.error(f"Error parsing conversation data: {str(e)}")
            raise ToolExecutionError(str(e))

    def parse_text_conversation(self, text: str) -> List[Dict[str, str]]:
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
            text (str): The text to parse.

        Returns:
            List[Dict[str, str]]: A list of conversation messages.

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

    def format_conversation(
        self, conversation: List[Dict[str, str]], use_colors: bool = False
    ) -> str:
        """
        Format a conversation based on the output format.

        Args:
            conversation (List[Dict[str, str]]): The conversation to format.
            use_colors (bool): Whether to use ANSI color codes in text output.
                Set to False by default to avoid artifacts in terminals that don't support ANSI colors.

        Returns:
            str: The formatted conversation.
        """
        logger.info(
            f"Formatting conversation with {len(conversation)} messages as {self._output_format}"
        )
        logger.debug(f"Using colors: {use_colors}")

        if self._output_format == "markdown":
            logger.debug("Using markdown formatter")
            result = format_conversation_as_markdown(
                conversation,
                user_message_color=self._user_message_color,
                ai_message_color=self._ai_message_color,
            )
        else:
            logger.debug("Using text formatter")
            result = format_conversation_as_text(
                conversation,
                user_message_color=self._user_message_color,
                ai_message_color=self._ai_message_color,
                use_colors=use_colors,
            )

        logger.debug(f"Formatted conversation ({len(result)} characters)")
        return result

    def search_conversation(
        self,
        conversation: List[Dict[str, str]],
        search_text: str,
        case_sensitive: bool = False,
    ) -> List[int]:
        """
        Search for text in a conversation.

        Args:
            conversation (List[Dict[str, str]]): The conversation to search.
            search_text (str): The text to search for.
            case_sensitive (bool): Whether the search should be case-sensitive.

        Returns:
            List[int]: A list of message indices that contain the search text.
        """
        logger.info(f"Searching conversation for text: '{search_text}'")
        logger.debug(
            f"Case sensitive: {case_sensitive}, Messages to search: {len(conversation)}"
        )

        if not search_text:
            logger.debug("Empty search text, returning empty result")
            return []

        matches = []

        for i, message in enumerate(conversation):
            content = message.get("content", "")

            if case_sensitive:
                if search_text in content:
                    logger.debug(f"Found case-sensitive match in message {i}")
                    matches.append(i)
            else:
                if search_text.lower() in content.lower():
                    logger.debug(f"Found case-insensitive match in message {i}")
                    matches.append(i)

        logger.info(f"Found {len(matches)} matches for '{search_text}'")
        return matches

    @property
    def output_format(self) -> str:
        """
        Get the current output format.

        Returns:
            str: The current output format.
        """
        return self._output_format

    @output_format.setter
    def output_format(self, value: str) -> None:
        """
        Set the output format.

        Args:
            value (str): The output format. Either "text" or "markdown".

        Raises:
            ValueError: If the output format is not supported.
        """
        logger.debug(f"Setting output format to: {value}")

        if value not in ["text", "markdown"]:
            logger.error(f"Invalid output format: {value}")
            raise ValueError("Output format must be either 'text' or 'markdown'")

        self._output_format = value
        logger.debug(f"Output format set to: {value}")

    @property
    def user_message_color(self) -> Optional[str]:
        """
        Get the user message color.

        Returns:
            Optional[str]: The user message color.
        """
        return self._user_message_color

    @user_message_color.setter
    def user_message_color(self, value: Optional[str]) -> None:
        """
        Set the user message color.

        Args:
            value (Optional[str]): The user message color.
        """
        logger.debug(f"Setting user message color to: {value}")
        self._user_message_color = value

    @property
    def ai_message_color(self) -> Optional[str]:
        """
        Get the AI message color.

        Returns:
            Optional[str]: The AI message color.
        """
        return self._ai_message_color

    @ai_message_color.setter
    def ai_message_color(self, value: Optional[str]) -> None:
        """
        Set the AI message color.

        Args:
            value (Optional[str]): The AI message color.
        """
        logger.debug(f"Setting AI message color to: {value}")
        self._ai_message_color = value

    def _format_xml_tags_raw(self, text: str) -> str:
        """
        Format XML tags in a raw string format that preserves newlines and indentation.

        Args:
            text: The string containing XML tags.

        Returns:
            str: A properly formatted JSON string with XML tags.
        """
        # Find all XML tag pairs and their content
        pattern = r"(<([A-Za-z_][A-Za-z0-9_]*)>)(.*?)(</\2>)"

        # Create a new string with formatted XML tags
        result = ""
        last_end = 0

        # Process each XML tag match
        for match in re.finditer(pattern, text, re.DOTALL):
            # Add any text before this match
            if match.start() > last_end:
                result += text[last_end : match.start()]

            # Extract the components
            open_tag = match.group(1)
            content = match.group(3)
            close_tag = match.group(4)

            # Add the formatted version with explicit newlines and indentation
            result += f"{open_tag}\n        {content}\n{close_tag}"

            # Update the last end position
            last_end = match.end()

        # Add any remaining text
        if last_end < len(text):
            result += text[last_end:]

        # Return the text as a properly escaped JSON string
        # Use raw string to ensure newlines are preserved
        return json.dumps(result, ensure_ascii=False)
