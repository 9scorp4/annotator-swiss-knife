"""
Text Collector tool.

This module implements a tool for collecting text from multiple fields
and outputting them as a JSON list. It filters out empty or whitespace-only entries.
"""

import json
from typing import Any, Dict, List, Union

from ...core.base import JsonAnnotationTool
from ...utils import logger
from ...utils.errors import ErrorCode, ProcessingError, TypeValidationError


class TextCollector(JsonAnnotationTool):
    """
    Tool for collecting text fields into a JSON list.

    This tool takes multiple text inputs (from various sources like text fields,
    file lines, or JSON data) and collects them into a single JSON array.
    Empty or whitespace-only entries are automatically filtered out.
    """

    DEFAULT_MAX_FIELDS = 20

    def __init__(self, max_fields: int = DEFAULT_MAX_FIELDS, filter_empty: bool = True):
        """
        Initialize the Text Collector.

        Args:
            max_fields (int): Maximum number of text fields to collect.
                Default is 20.
            filter_empty (bool): Whether to filter out empty/whitespace-only text.
                Default is True.
        """
        super().__init__()
        self._max_fields = max_fields
        self._filter_empty = filter_empty
        logger.debug(
            f"TextCollector initialized with max_fields={max_fields}, filter_empty={filter_empty}"
        )

    @property
    def name(self) -> str:
        """
        Return the name of the tool.

        Returns:
            str: The name of the tool.
        """
        return "Text Collector"

    @property
    def description(self) -> str:
        """
        Return a description of the tool.

        Returns:
            str: A description of the tool's functionality.
        """
        return "Collects text from multiple fields and outputs them as a JSON list."

    @property
    def max_fields(self) -> int:
        """
        Get the maximum number of fields allowed.

        Returns:
            int: Maximum number of fields.
        """
        return self._max_fields

    @property
    def filter_empty(self) -> bool:
        """
        Get whether empty filtering is enabled.

        Returns:
            bool: True if empty strings are filtered out.
        """
        return self._filter_empty

    def collect_from_list(self, text_list: List[str]) -> List[str]:
        """
        Collect text from a list of strings.

        Args:
            text_list (List[str]): List of text strings to collect.

        Returns:
            List[str]: Collected text items (filtered if filter_empty is True).

        Raises:
            TypeValidationError: If input is not a list or contains non-string items.
            ProcessingError: If the list exceeds max_fields limit.
        """
        logger.info(f"Collecting text from list with {len(text_list)} items")

        # Validate input type
        if not isinstance(text_list, list):
            raise TypeValidationError(
                "text_list",
                list,
                type(text_list),
                suggestion="Input must be a list of strings."
            )

        # Check max fields limit
        if len(text_list) > self._max_fields:
            raise ProcessingError(
                f"Number of text items ({len(text_list)}) exceeds maximum allowed ({self._max_fields})",
                error_code=ErrorCode.INVALID_INPUT,
                suggestion=f"Limit the number of text items to {self._max_fields} or less."
            )

        # Validate and collect items
        collected = []
        for i, item in enumerate(text_list):
            # Validate each item is a string
            if not isinstance(item, str):
                raise TypeValidationError(
                    f"text_list[{i}]",
                    str,
                    type(item),
                    suggestion="All items in the list must be strings."
                )

            # Filter empty if enabled
            if self._filter_empty:
                if item.strip():  # Only add non-empty strings
                    collected.append(item.strip())
            else:
                collected.append(item)

        logger.debug(f"Collected {len(collected)} text items (filtered: {self._filter_empty})")
        return collected

    def collect_from_dict(self, text_dict: Dict[str, str]) -> List[str]:
        """
        Collect text from a dictionary of key-value pairs.

        Args:
            text_dict (Dict[str, str]): Dictionary with text values.

        Returns:
            List[str]: Collected text values (filtered if filter_empty is True).

        Raises:
            TypeValidationError: If input is not a dict or contains non-string values.
            ProcessingError: If the dict exceeds max_fields limit.
        """
        logger.info(f"Collecting text from dict with {len(text_dict)} fields")

        # Validate input type
        if not isinstance(text_dict, dict):
            raise TypeValidationError(
                "text_dict",
                dict,
                type(text_dict),
                suggestion="Input must be a dictionary with string values."
            )

        # Check max fields limit
        if len(text_dict) > self._max_fields:
            raise ProcessingError(
                f"Number of text fields ({len(text_dict)}) exceeds maximum allowed ({self._max_fields})",
                error_code=ErrorCode.INVALID_INPUT,
                suggestion=f"Limit the number of text fields to {self._max_fields} or less."
            )

        # Validate and collect values
        collected = []
        for key, value in text_dict.items():
            # Validate each value is a string
            if not isinstance(value, str):
                raise TypeValidationError(
                    f"text_dict['{key}']",
                    str,
                    type(value),
                    suggestion=f"All values in the dictionary must be strings. Field '{key}' has type {type(value).__name__}."
                )

            # Filter empty if enabled
            if self._filter_empty:
                if value.strip():  # Only add non-empty strings
                    collected.append(value.strip())
            else:
                collected.append(value)

        logger.debug(f"Collected {len(collected)} text values (filtered: {self._filter_empty})")
        return collected

    def process_json(self, json_data: Union[Dict, List]) -> List[str]:
        """
        Process JSON input and return a list of collected text items.

        This implements the JsonAnnotationTool interface.

        Args:
            json_data: The input JSON data. Can be:
                - List of strings: ["text1", "text2", ...]
                - Dict with string values: {"field1": "text1", "field2": "text2", ...}

        Returns:
            List[str]: Collected text items as a JSON-serializable list.

        Raises:
            TypeValidationError: If input format is invalid.
            ProcessingError: If processing fails or limits are exceeded.
        """
        logger.info("Processing JSON data through process_json interface")

        # Handle list input
        if isinstance(json_data, list):
            return self.collect_from_list(json_data)

        # Handle dict input
        elif isinstance(json_data, dict):
            return self.collect_from_dict(json_data)

        # Should not reach here due to base class validation
        else:
            raise TypeValidationError(
                "json_data",
                [list, dict],
                type(json_data),
                suggestion="Input must be either a list of strings or a dictionary with string values."
            )

    def to_json_string(self, text_items: List[str], pretty: bool = True) -> str:
        """
        Convert collected text items to a JSON string.

        Args:
            text_items (List[str]): List of text items to convert.
            pretty (bool): If True, generate pretty-printed JSON.
                If False, generate compact JSON.

        Returns:
            str: JSON string representation of the text list.
        """
        logger.debug(f"Converting {len(text_items)} items to JSON string (pretty={pretty})")

        if pretty:
            json_str = json.dumps(text_items, indent=2, ensure_ascii=False)
        else:
            json_str = json.dumps(text_items, ensure_ascii=False)

        logger.debug(f"JSON generated: {len(json_str)} characters")
        return json_str
