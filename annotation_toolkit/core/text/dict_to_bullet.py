"""
Dictionary to Bullet List conversion tool.

This module implements a tool for converting dictionary data to
formatted bullet lists with hyperlinks.
"""

import json
from typing import Dict, List, Optional, Tuple, Union

from ...core.base import TextAnnotationTool, ToolExecutionError
from ...utils import logger
from ...utils.text.formatting import dict_to_bullet_list, extract_url_title


class DictToBulletList(TextAnnotationTool):
    """
    Tool for converting dictionary data to bullet lists with hyperlinks.
    """

    def __init__(self, markdown_output: bool = True):
        """
        Initialize the Dictionary to Bullet List converter.

        Args:
            markdown_output (bool): Whether to output in markdown format.
                If True, URLs will be formatted as markdown links.
                If False, URLs will be formatted as plain text.
        """
        super().__init__()
        self._markdown_output = markdown_output
        logger.debug(
            f"DictToBulletList initialized with markdown_output={markdown_output}"
        )

    @property
    def name(self) -> str:
        """
        Return the name of the tool.

        Returns:
            str: The name of the tool.
        """
        return "Dictionary to Bullet List"

    @property
    def description(self) -> str:
        """
        Return a description of the tool.

        Returns:
            str: A description of the tool's functionality.
        """
        return "Converts dictionary data with URLs to formatted bullet lists with hyperlinks."

    def process_text(self, text: str) -> str:
        """
        Process a JSON string representing a dictionary.

        Args:
            text (str): JSON string representing a dictionary.

        Returns:
            str: A bullet list representation of the dictionary.

        Raises:
            ToolExecutionError: If the input is not valid JSON or not a dictionary.
        """
        logger.info("Processing JSON text to bullet list")
        logger.debug(f"Input text length: {len(text)} characters")

        try:
            logger.debug("Parsing JSON input")
            data = json.loads(text)

            if not isinstance(data, dict):
                error_msg = "Input must be a JSON object (dictionary)"
                logger.error(
                    f"Invalid input type: {type(data).__name__}, expected dict"
                )
                raise ToolExecutionError(error_msg)

            logger.debug(f"Successfully parsed JSON with {len(data)} keys")
            return self.process_dict(data)
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON: {str(e)}"
            logger.exception(f"JSON parsing error: {str(e)}")
            raise ToolExecutionError(error_msg)

    def process_dict(self, data: Dict[str, str]) -> str:
        """
        Process a dictionary and convert it to a bullet list.

        Args:
            data (Dict[str, str]): Dictionary with string keys and values.

        Returns:
            str: A bullet list representation of the dictionary.

        Raises:
            ToolExecutionError: If the input dictionary has non-string values.
        """
        logger.info(f"Converting dictionary with {len(data)} items to bullet list")
        logger.debug(f"Using markdown format: {self._markdown_output}")

        # Validate dictionary values
        for key, value in data.items():
            if not isinstance(value, str):
                error_msg = f"Dictionary values must be strings. Found non-string value for key '{key}'"
                logger.error(
                    f"Invalid value type for key '{key}': {type(value).__name__}, expected str"
                )
                raise ToolExecutionError(error_msg)

        result = dict_to_bullet_list(data, as_markdown=self._markdown_output)
        logger.debug(
            f"Successfully converted dictionary to bullet list ({len(result)} characters)"
        )
        return result

    def process_dict_to_items(self, data: Dict[str, str]) -> List[Tuple[str, str]]:
        """
        Process a dictionary and convert it to a list of (title, url) tuples.

        This is useful for creating clickable items in a GUI.

        Args:
            data (Dict[str, str]): Dictionary with string keys and values (URLs).

        Returns:
            List[Tuple[str, str]]: A list of (title, url) tuples.

        Raises:
            ToolExecutionError: If the input dictionary has non-string values.
        """
        logger.info(
            f"Converting dictionary with {len(data)} items to (title, url) tuples"
        )
        items = []
        url_count = 0

        for key, value in data.items():
            if not isinstance(value, str):
                error_msg = f"Dictionary values must be strings. Found non-string value for key '{key}'"
                logger.error(
                    f"Invalid value type for key '{key}': {type(value).__name__}, expected str"
                )
                raise ToolExecutionError(error_msg)

            # Check if value is a URL
            is_url = value.startswith(("http://", "https://"))

            if is_url:
                logger.debug(f"Extracting title for URL: {value}")
                title = extract_url_title(value)
                items.append((title, value))
                url_count += 1
            else:
                items.append((key, value))

        logger.debug(f"Created {len(items)} items, including {url_count} URLs")
        return items

    @property
    def markdown_output(self) -> bool:
        """
        Get the current markdown output setting.

        Returns:
            bool: The current markdown output setting.
        """
        return self._markdown_output

    @markdown_output.setter
    def markdown_output(self, value: bool) -> None:
        """
        Set the markdown output setting.

        Args:
            value (bool): Whether to output in markdown format.
        """
        logger.debug(f"Setting markdown_output to {value}")
        self._markdown_output = value
