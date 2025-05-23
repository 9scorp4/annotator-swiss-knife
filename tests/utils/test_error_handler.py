"""
Tests for the error handling utilities.

This module contains tests for the error handling utilities in the
annotation_toolkit.utils.error_handler module.
"""

import unittest
from unittest.mock import patch, MagicMock

from annotation_toolkit.utils.error_handler import (
    with_error_handling,
    handle_errors,
    format_error_for_user
)
from annotation_toolkit.utils.errors import (
    AnnotationToolkitError,
    ErrorCode,
    ConfigurationError,
    ProcessingError
)


class TestErrorHandler(unittest.TestCase):
    """Test cases for the error handling utilities."""

    def test_format_error_for_user_simple(self):
        """Test formatting a simple error message."""
        error = AnnotationToolkitError("Test error")
        message = format_error_for_user(error)
        self.assertEqual(message, "Test error")

    def test_format_error_for_user_with_suggestion(self):
        """Test formatting an error message with a suggestion."""
        error = AnnotationToolkitError("Test error", suggestion="Try this instead")
        message = format_error_for_user(error)
        self.assertEqual(message, "Test error\nSuggestion: Try this instead")

    def test_format_error_for_user_with_details(self):
        """Test formatting an error message with details."""
        error = AnnotationToolkitError(
            "Test error",
            details={"key": "value", "another_key": "another_value"}
        )
        message = format_error_for_user(error)
        self.assertEqual(message, "Test error\nDetails: key=value, another_key=another_value")

    def test_format_error_for_user_with_all(self):
        """Test formatting an error message with all optional fields."""
        error = AnnotationToolkitError(
            "Test error",
            error_code=ErrorCode.CONFIGURATION_ERROR,
            details={"key": "value"},
            suggestion="Try this instead"
        )
        message = format_error_for_user(error)
        self.assertEqual(
            message,
            "Test error (Error code: CONFIGURATION_ERROR)\n"
            "Details: key=value\n"
            "Suggestion: Try this instead"
        )

    def test_handle_errors_no_error(self):
        """Test handle_errors with no error."""
        @handle_errors
        def func():
            return "success"

        result = func()
        self.assertEqual(result, "success")

    def test_handle_errors_with_annotation_toolkit_error(self):
        """Test handle_errors with an AnnotationToolkitError."""
        @handle_errors
        def func():
            raise ConfigurationError("Test error")

        with self.assertRaises(ConfigurationError):
            func()

    def test_handle_errors_with_other_exception(self):
        """Test handle_errors with a non-AnnotationToolkitError exception."""
        @handle_errors
        def func():
            raise ValueError("Test error")

        with self.assertRaises(ProcessingError):
            func()

    def test_with_error_handling_decorator_no_error(self):
        """Test with_error_handling decorator with no error."""
        decorator = with_error_handling(
            error_code=ErrorCode.PROCESSING_ERROR,
            error_message="Error in function",
            suggestion="Try again"
        )

        @decorator
        def func():
            return "success"

        result = func()
        self.assertEqual(result, "success")

    def test_with_error_handling_decorator_with_error(self):
        """Test with_error_handling decorator with an error."""
        decorator = with_error_handling(
            error_code=ErrorCode.PROCESSING_ERROR,
            error_message="Error in function",
            suggestion="Try again"
        )

        @decorator
        def func():
            raise ValueError("Original error")

        with self.assertRaises(ProcessingError) as context:
            func()

        error = context.exception
        self.assertEqual(error.message, "Error in function")
        self.assertEqual(error.error_code, ErrorCode.PROCESSING_ERROR)
        self.assertEqual(error.suggestion, "Try again")
        self.assertIsInstance(error.cause, ValueError)
        self.assertEqual(str(error.cause), "Original error")

    def test_with_error_handling_decorator_with_annotation_toolkit_error(self):
        """Test with_error_handling decorator with an AnnotationToolkitError."""
        decorator = with_error_handling(
            error_code=ErrorCode.PROCESSING_ERROR,
            error_message="Error in function",
            suggestion="Try again"
        )

        @decorator
        def func():
            raise ConfigurationError(
                "Original error",
                error_code=ErrorCode.CONFIGURATION_ERROR,
                suggestion="Original suggestion"
            )

        # The original AnnotationToolkitError should be re-raised without modification
        with self.assertRaises(ConfigurationError) as context:
            func()

        error = context.exception
        self.assertEqual(error.context.message, "Original error")
        self.assertEqual(error.error_code, ErrorCode.CONFIGURATION_ERROR)
        self.assertEqual(error.suggestion, "Original suggestion")


if __name__ == "__main__":
    unittest.main()
