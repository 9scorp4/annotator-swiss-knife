"""
Text Cleaning Tool.

This module implements a tool for cleaning text from markdown/JSON/code artifacts
and presenting a clean version that can be edited and then transformed back.
"""

import json
import re
from typing import Dict, List, Optional, Tuple, Union

from ...core.base import TextAnnotationTool, ToolExecutionError
from ...utils import logger


class TextCleaner(TextAnnotationTool):
    """
    Tool for cleaning text from markdown/JSON/code artifacts and presenting a clean version
    that can be edited and then transformed back.
    """

    def __init__(self, output_format: str = "markdown"):
        """
        Initialize the Text Cleaner.

        Args:
            output_format (str): The output format. Either "markdown" or "json".
                If "markdown", the cleaned text will be formatted as markdown.
                If "json", the cleaned text will be formatted as JSON.
        """
        super().__init__()
        if output_format not in ["markdown", "json"]:
            logger.error(f"Invalid output format: {output_format}")
            raise ValueError("Output format must be either 'markdown' or 'json'")

        self._output_format = output_format
        logger.debug(f"TextCleaner initialized with output_format={output_format}")

    @property
    def name(self) -> str:
        """
        Return the name of the tool.

        Returns:
            str: The name of the tool.
        """
        return "Text Cleaner"

    @property
    def description(self) -> str:
        """
        Return a description of the tool.

        Returns:
            str: A description of the tool's functionality.
        """
        return "Cleans text from markdown/JSON/code artifacts and presents a clean version that can be edited and then transformed back."

    def process_text(self, text: str) -> str:
        """
        Process text by cleaning it from markdown/JSON/code artifacts.

        Args:
            text (str): The text to clean.

        Returns:
            str: The cleaned text.
        """
        logger.info("Cleaning text from artifacts")
        logger.debug(f"Input text length: {len(text)} characters")

        try:
            # Clean the text
            cleaned_text = self.clean_text(text)

            # Format the output based on the selected format
            if self._output_format == "json":
                result = self.format_as_json(cleaned_text, text)
            else:  # markdown
                result = self.format_as_markdown(cleaned_text, text)

            logger.debug(f"Successfully cleaned text ({len(result)} characters)")
            return result
        except Exception as e:
            logger.exception(f"Error cleaning text: {str(e)}")
            raise ToolExecutionError(f"Error cleaning text: {str(e)}")

    def clean_text(self, text: str) -> str:
        """
        Clean text from markdown/JSON/code artifacts.

        Args:
            text (str): The text to clean.

        Returns:
            str: The cleaned text.
        """
        logger.debug("Cleaning text from artifacts")

        # Remove backticks and code block markers
        text = re.sub(r"```[a-zA-Z]*\n|```", "", text)

        # Replace escaped newlines with actual newlines
        text = text.replace("\\n", "\n")

        # Remove extra newlines (more than 2 consecutive)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Remove JSON string escaping
        text = text.replace('\\"', '"')

        # Remove markdown formatting
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)  # Bold
        text = re.sub(r"\*(.*?)\*", r"\1", text)  # Italic
        text = re.sub(r"__(.*?)__", r"\1", text)  # Bold
        text = re.sub(r"_(.*?)_", r"\1", text)  # Italic

        # Remove HTML tags
        text = re.sub(r"<[^>]*>", "", text)

        logger.debug(f"Text cleaned, new length: {len(text)} characters")
        return text

    def format_as_markdown(self, cleaned_text: str, original_text: str) -> str:
        """
        Format the cleaned text as markdown.

        Args:
            cleaned_text (str): The cleaned text.
            original_text (str): The original text.

        Returns:
            str: The formatted markdown.
        """
        logger.debug("Formatting cleaned text as markdown")

        result = [
            "# Cleaned Text",
            "",
            "Below is the cleaned version of the text. You can edit this text and then use the 'Transform Back' button to convert it back to a format readable by a computer.",
            "",
            "## Original Text",
            "```",
            original_text,
            "```",
            "",
            "## Cleaned Text (Editable)",
            "",
            cleaned_text,
            "",
            "## How to Use",
            "",
            "1. Edit the cleaned text above as needed",
            "2. Click the 'Transform Back' button to convert it back to a computer-readable format",
            "3. Copy the transformed text for use in your application",
        ]

        return "\n".join(result)

    def format_as_json(self, cleaned_text: str, original_text: str) -> str:
        """
        Format the cleaned text as JSON.

        Args:
            cleaned_text (str): The cleaned text.
            original_text (str): The original text.

        Returns:
            str: The formatted JSON.
        """
        logger.debug("Formatting cleaned text as JSON")

        result = {
            "original_text": original_text,
            "cleaned_text": cleaned_text,
            "instructions": "Edit the cleaned_text field and then use the 'Transform Back' function to convert it back to a computer-readable format.",
        }

        return json.dumps(result, indent=2)

    def transform_back(self, cleaned_text: str, format_type: str = "code") -> str:
        """
        Transform the cleaned text back to a computer-readable format.

        Args:
            cleaned_text (str): The cleaned text to transform.
            format_type (str): The format type to transform to. Options:
                - "code": Escape newlines and quotes for use in code
                - "json": Format for JSON strings
                - "markdown": Format as markdown

        Returns:
            str: The transformed text.
        """
        logger.info(f"Transforming cleaned text back to {format_type} format")
        logger.debug(f"Input text length: {len(cleaned_text)} characters")

        if format_type == "code":
            # First escape backslashes to prevent double-escaping issues
            transformed = cleaned_text.replace("\\", "\\\\")

            # Then escape newlines and quotes
            transformed = transformed.replace("\n", "\\n").replace('"', '\\"')

            logger.debug("Transformed text for code usage")
            return transformed

        elif format_type == "json":
            # Format for JSON strings
            transformed = json.dumps(cleaned_text)
            logger.debug("Transformed text for JSON usage")
            return transformed

        elif format_type == "markdown":
            # Format as markdown
            # This is a simple implementation - could be enhanced with more markdown features
            lines = cleaned_text.split("\n")
            transformed_lines = []

            for line in lines:
                # Check if line is a heading
                if line.strip().startswith("#"):
                    transformed_lines.append(line)
                # Check if line is a list item
                elif line.strip().startswith("- ") or line.strip().startswith("* "):
                    transformed_lines.append(line)
                # Check if line is empty
                elif not line.strip():
                    transformed_lines.append("")
                # Regular paragraph
                else:
                    transformed_lines.append(line)

            transformed = "\n".join(transformed_lines)
            logger.debug("Transformed text for markdown usage")
            return transformed

        else:
            logger.error(f"Invalid format type: {format_type}")
            raise ValueError(
                f"Invalid format type: {format_type}. Must be one of: code, json, markdown"
            )

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
            value (str): The output format. Either "markdown" or "json".

        Raises:
            ValueError: If the output format is not supported.
        """
        logger.debug(f"Setting output format to: {value}")

        if value not in ["markdown", "json"]:
            logger.error(f"Invalid output format: {value}")
            raise ValueError("Output format must be either 'markdown' or 'json'")

        self._output_format = value
        logger.debug(f"Output format set to: {value}")
