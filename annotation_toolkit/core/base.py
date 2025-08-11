"""
Base classes and interfaces for annotation tools.

This module defines the abstract base classes and interfaces that all annotation tools
in the toolkit should implement. These classes establish a consistent API for all tools
regardless of their specific functionality.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from ..utils import logger
from ..utils.errors import ErrorCode, ProcessingError, safe_execute, TypeValidationError


class AnnotationTool(ABC):
    """
    Abstract base class for all annotation tools.

    All annotation tools must implement this interface to be compatible
    with the toolkit's core architecture.
    """

    def __init__(self):
        """Initialize the annotation tool."""
        logger.debug(f"Initializing annotation tool: {self.__class__.__name__}")

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the name of the annotation tool.

        Returns:
            str: The name of the tool.
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        Return a description of what the tool does.

        Returns:
            str: A description of the tool's functionality.
        """
        pass

    @abstractmethod
    def process(self, data: Any) -> Any:
        """
        Process the input data and return the annotated result.

        Args:
            data: The input data to process.

        Returns:
            The processed/annotated data.
        """
        pass


class TextAnnotationTool(AnnotationTool):
    """
    Base class for annotation tools that work with text data.
    """

    @abstractmethod
    def process_text(self, text: str) -> str:
        """
        Process text input and return annotated text.

        Args:
            text (str): The input text to process.

        Returns:
            str: The processed/annotated text.
        """
        pass

    def process(self, data: Any) -> str:
        """
        Implementation of the process method for text annotation tools.

        Args:
            data: The input data, which will be converted to string.

        Returns:
            str: The processed text.
        """
        tool_name = self.__class__.__name__
        logger.info(f"{tool_name}: Processing text data")
        try:
            result = self.process_text(str(data))
            logger.debug(f"{tool_name}: Text processing completed successfully")
            return result
        except Exception as e:
            logger.exception(f"{tool_name}: Error processing text data: {str(e)}")
            raise ProcessingError(
                f"Error processing text data: {str(e)}",
                error_code=ErrorCode.PROCESSING_ERROR,
                details={"tool": tool_name, "data_type": type(data).__name__},
                suggestion="Check the input text format and ensure it's compatible with this tool.",
                cause=e,
            )


class JsonAnnotationTool(AnnotationTool):
    """
    Base class for annotation tools that work with JSON data.
    """

    @abstractmethod
    def process_json(self, json_data: Union[Dict, List]) -> Any:
        """
        Process JSON input and return annotated data.

        Args:
            json_data (Union[Dict, List]): The input JSON data to process.

        Returns:
            The processed/annotated data.
        """
        pass

    def process(self, data: Any) -> Any:
        """
        Implementation of the process method for JSON annotation tools.

        Args:
            data: The input data, which should be a JSON-compatible object.

        Returns:
            The processed data.
        """
        tool_name = self.__class__.__name__
        logger.info(f"{tool_name}: Processing JSON data")

        if not isinstance(data, (dict, list)):
            raise TypeValidationError(
                "input_data",
                [dict, list],
                type(data),
                details={"tool": tool_name},
                suggestion="Ensure you're passing a valid JSON object (dictionary or list) to this tool.",
            )

        try:
            result = self.process_json(data)
            logger.debug(f"{tool_name}: JSON processing completed successfully")
            return result
        except Exception as e:
            logger.exception(f"{tool_name}: Error processing JSON data: {str(e)}")
            raise ProcessingError(
                f"Error processing JSON data: {str(e)}",
                error_code=ErrorCode.PROCESSING_ERROR,
                details={"tool": tool_name, "data_type": type(data).__name__},
                suggestion="Check the JSON structure and ensure it meets the requirements for this tool.",
                cause=e,
            )


# Import the configuration error from the errors module
from ..utils.errors import (
    ConfigurationError as ToolConfigurationError,
    ToolExecutionError,
)
