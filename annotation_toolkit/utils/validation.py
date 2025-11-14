"""
Streaming validation utilities.

This module provides validators for processing large files and data streams
without loading everything into memory.
"""

import json
import re
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum

from .logger import get_logger
from .errors import ValidationError, ParsingError
from .streaming import StreamingJSONParser
from .security import default_file_size_validator

logger = get_logger()


class ValidationSeverity(Enum):
    """Validation message severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationMessage:
    """A validation message."""
    severity: ValidationSeverity
    message: str
    location: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class ValidationResult:
    """Result of a validation operation."""

    def __init__(self):
        """Initialize validation result."""
        self.messages: List[ValidationMessage] = []
        self.is_valid = True

    def add_error(self, message: str, location: Optional[str] = None,
                  details: Optional[Dict[str, Any]] = None):
        """Add an error message."""
        self.messages.append(ValidationMessage(
            ValidationSeverity.ERROR, message, location, details
        ))
        self.is_valid = False

    def add_warning(self, message: str, location: Optional[str] = None,
                   details: Optional[Dict[str, Any]] = None):
        """Add a warning message."""
        self.messages.append(ValidationMessage(
            ValidationSeverity.WARNING, message, location, details
        ))

    def add_info(self, message: str, location: Optional[str] = None,
                details: Optional[Dict[str, Any]] = None):
        """Add an info message."""
        self.messages.append(ValidationMessage(
            ValidationSeverity.INFO, message, location, details
        ))

    @property
    def errors(self) -> List[ValidationMessage]:
        """Get all error messages."""
        return [msg for msg in self.messages if msg.severity == ValidationSeverity.ERROR]

    @property
    def warnings(self) -> List[ValidationMessage]:
        """Get all warning messages."""
        return [msg for msg in self.messages if msg.severity == ValidationSeverity.WARNING]

    def __bool__(self) -> bool:
        """Return True if validation passed."""
        return self.is_valid


class StreamingValidator:
    """Base class for streaming validators."""

    def __init__(self, max_errors: int = 100):
        """
        Initialize streaming validator.

        Args:
            max_errors: Maximum number of errors before stopping validation.
        """
        self.max_errors = max_errors

    def validate(self, data_stream: Iterator[Any]) -> ValidationResult:
        """
        Validate a data stream.

        Args:
            data_stream: Iterator of data items to validate.

        Returns:
            Validation result.
        """
        result = ValidationResult()
        error_count = 0

        for i, item in enumerate(data_stream):
            if error_count >= self.max_errors:
                result.add_warning(
                    f"Validation stopped after {self.max_errors} errors",
                    location=f"item_{i}"
                )
                break

            item_result = self.validate_item(item, i)
            result.messages.extend(item_result.messages)

            if not item_result.is_valid:
                result.is_valid = False
                error_count += len(item_result.errors)

        return result

    def validate_item(self, item: Any, index: int) -> ValidationResult:
        """
        Validate a single item.

        Args:
            item: The item to validate.
            index: The item index in the stream.

        Returns:
            Validation result for the item.
        """
        raise NotImplementedError("Subclasses must implement validate_item")


class JsonStreamingValidator(StreamingValidator):
    """Validator for JSON data streams."""

    def __init__(self, schema: Optional[Dict[str, Any]] = None,
                 required_fields: Optional[List[str]] = None,
                 max_errors: int = 100):
        """
        Initialize JSON streaming validator.

        Args:
            schema: JSON schema for validation (simple field type validation).
            required_fields: List of required field names.
            max_errors: Maximum number of errors before stopping.
        """
        super().__init__(max_errors)
        self.schema = schema or {}
        self.required_fields = required_fields or []

    def validate_file(self, file_path: Union[str, Path]) -> ValidationResult:
        """
        Validate a JSON file using streaming.

        Args:
            file_path: Path to the JSON file.

        Returns:
            Validation result.
        """
        file_path = Path(file_path)
        result = ValidationResult()

        # Check file size
        try:
            default_file_size_validator.validate_file_size(file_path)
        except Exception as e:
            result.add_error(f"File size validation failed: {str(e)}")
            return result

        # Stream parse the file
        parser = StreamingJSONParser()

        try:
            if self._is_json_array_file(file_path):
                # Parse as array of items
                data_stream = parser.parse_array_items(file_path)
                return self.validate(data_stream)
            else:
                # Parse as single object
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        return self.validate_item(data, 0)
                    except json.JSONDecodeError as e:
                        result.add_error(
                            f"Invalid JSON: {str(e)}",
                            location=f"line_{e.lineno}_col_{e.colno}"
                        )
                        return result

        except Exception as e:
            result.add_error(f"Error reading file: {str(e)}")
            return result

    def validate_item(self, item: Any, index: int) -> ValidationResult:
        """
        Validate a single JSON item.

        Args:
            item: The JSON item to validate.
            index: The item index.

        Returns:
            Validation result.
        """
        result = ValidationResult()
        location = f"item_{index}"

        # Check if item is a dictionary
        if not isinstance(item, dict):
            result.add_error(
                f"Expected object, got {type(item).__name__}",
                location=location
            )
            return result

        # Check required fields
        for field in self.required_fields:
            if field not in item:
                result.add_error(
                    f"Missing required field: {field}",
                    location=f"{location}.{field}"
                )

        # Validate against schema
        for field, expected_type in self.schema.items():
            if field in item:
                actual_value = item[field]
                if not self._validate_type(actual_value, expected_type):
                    result.add_error(
                        f"Field '{field}' has wrong type. Expected {expected_type}, got {type(actual_value).__name__}",
                        location=f"{location}.{field}"
                    )

        return result

    def _validate_type(self, value: Any, expected_type: Any) -> bool:
        """Validate value type against expected type."""
        if expected_type == 'string':
            return isinstance(value, str)
        elif expected_type == 'number':
            return isinstance(value, (int, float))
        elif expected_type == 'boolean':
            return isinstance(value, bool)
        elif expected_type == 'array':
            return isinstance(value, list)
        elif expected_type == 'object':
            return isinstance(value, dict)
        elif expected_type == 'null':
            return value is None
        elif isinstance(expected_type, type):
            return isinstance(value, expected_type)
        else:
            return True  # Unknown type, accept anything

    def _is_json_array_file(self, file_path: Path) -> bool:
        """Check if JSON file contains an array at root level."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Read first non-whitespace character
                while True:
                    char = f.read(1)
                    if not char:
                        return False
                    if not char.isspace():
                        return char == '['
        except Exception:
            return False


class ConversationValidator(JsonStreamingValidator):
    """Validator specifically for conversation data."""

    def __init__(self, max_errors: int = 100):
        """Initialize conversation validator."""
        super().__init__(
            schema={
                'role': 'string',
                'content': 'string'
            },
            required_fields=['role', 'content'],
            max_errors=max_errors
        )

    def validate_item(self, item: Any, index: int) -> ValidationResult:
        """
        Validate a conversation message.

        Args:
            item: The message to validate.
            index: The message index.

        Returns:
            Validation result.
        """
        result = super().validate_item(item, index)
        location = f"message_{index}"

        if isinstance(item, dict):
            # Validate role values
            role = item.get('role')
            if role and role not in ['user', 'assistant', 'system', 'human', 'ai']:
                result.add_warning(
                    f"Unusual role value: '{role}'. Expected: user, assistant, system, human, or ai",
                    location=f"{location}.role"
                )

            # Validate content
            content = item.get('content')
            if content is not None:
                if not isinstance(content, str):
                    result.add_error(
                        f"Content must be a string, got {type(content).__name__}",
                        location=f"{location}.content"
                    )
                elif len(content.strip()) == 0:
                    result.add_warning(
                        "Empty content",
                        location=f"{location}.content"
                    )

        return result


class TextStreamingValidator(StreamingValidator):
    """Validator for text content."""

    def __init__(self, max_line_length: int = 10000,
                 encoding: str = 'utf-8',
                 max_errors: int = 100):
        """
        Initialize text streaming validator.

        Args:
            max_line_length: Maximum allowed line length.
            encoding: Expected text encoding.
            max_errors: Maximum number of errors before stopping.
        """
        super().__init__(max_errors)
        self.max_line_length = max_line_length
        self.encoding = encoding

    def validate_file(self, file_path: Union[str, Path]) -> ValidationResult:
        """
        Validate a text file line by line.

        Args:
            file_path: Path to the text file.

        Returns:
            Validation result.
        """
        file_path = Path(file_path)
        result = ValidationResult()

        try:
            with open(file_path, 'r', encoding=self.encoding, errors='replace') as f:
                line_number = 0
                for line in f:
                    line_number += 1
                    line_result = self.validate_line(line, line_number)
                    result.messages.extend(line_result.messages)

                    if not line_result.is_valid:
                        result.is_valid = False

                    # Check error limit
                    error_count = len([msg for msg in result.messages
                                     if msg.severity == ValidationSeverity.ERROR])
                    if error_count >= self.max_errors:
                        result.add_warning(
                            f"Validation stopped after {self.max_errors} errors",
                            location=f"line_{line_number}"
                        )
                        break

        except UnicodeDecodeError as e:
            result.add_error(
                f"Encoding error: {str(e)}",
                location=f"byte_{e.start}"
            )
        except Exception as e:
            result.add_error(f"Error reading file: {str(e)}")

        return result

    def validate_line(self, line: str, line_number: int) -> ValidationResult:
        """
        Validate a single line of text.

        Args:
            line: The line to validate.
            line_number: The line number.

        Returns:
            Validation result.
        """
        result = ValidationResult()
        location = f"line_{line_number}"

        # Check line length
        if len(line) > self.max_line_length:
            result.add_warning(
                f"Line exceeds maximum length ({len(line)} > {self.max_line_length})",
                location=location
            )

        # Check for control characters
        control_chars = [char for char in line if ord(char) < 32 and char not in '\n\r\t']
        if control_chars:
            result.add_warning(
                f"Line contains control characters: {[ord(c) for c in control_chars]}",
                location=location
            )

        return result

    def validate_item(self, item: str, index: int) -> ValidationResult:
        """Validate a text item (alias for validate_line)."""
        return self.validate_line(item, index + 1)


def validate_json_file(file_path: Union[str, Path],
                      schema: Optional[Dict[str, Any]] = None,
                      required_fields: Optional[List[str]] = None) -> ValidationResult:
    """
    Convenience function to validate a JSON file.

    Args:
        file_path: Path to the JSON file.
        schema: JSON schema for validation.
        required_fields: List of required field names.

    Returns:
        Validation result.
    """
    validator = JsonStreamingValidator(schema, required_fields)
    return validator.validate_file(file_path)


def validate_conversation_file(file_path: Union[str, Path]) -> ValidationResult:
    """
    Convenience function to validate a conversation file.

    Args:
        file_path: Path to the conversation file.

    Returns:
        Validation result.
    """
    validator = ConversationValidator()
    return validator.validate_file(file_path)


def validate_text_file(file_path: Union[str, Path],
                      max_line_length: int = 10000,
                      encoding: str = 'utf-8') -> ValidationResult:
    """
    Convenience function to validate a text file.

    Args:
        file_path: Path to the text file.
        max_line_length: Maximum allowed line length.
        encoding: Expected text encoding.

    Returns:
        Validation result.
    """
    validator = TextStreamingValidator(max_line_length, encoding)
    return validator.validate_file(file_path)