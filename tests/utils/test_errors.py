"""
Comprehensive tests for the error handling system.

This module contains comprehensive tests for the error handling system including:
- ErrorCode enum
- ErrorContext class
- All custom exception classes
- Error handling utility functions
- Decorators and error handlers
"""

import unittest
from unittest.mock import patch, MagicMock, call
from typing import Any, Dict

from annotation_toolkit.utils.errors import (
    # Error codes
    ErrorCode,
    # Context
    ErrorContext,
    # Base exception
    AnnotationToolkitError,
    # Configuration errors
    ConfigurationError,
    MissingConfigurationError,
    InvalidConfigurationError,
    # Validation errors
    ValidationError,
    MissingRequiredFieldError,
    TypeValidationError,
    ValueValidationError,
    # Processing errors
    ProcessingError,
    TransformationError,
    ToolExecutionError,
    ParsingError,
    # I/O errors
    IOError,
    FileNotFoundError,
    FileReadError,
    FileWriteError,
    # Service errors
    ServiceError,
    ServiceUnavailableError,
    ServiceTimeoutError,
    # Utility functions
    handle_exception,
    safe_execute,
    format_exception,
    get_error_details,
)


class TestErrorCode(unittest.TestCase):
    """Test cases for the ErrorCode enum."""

    def test_error_code_values(self):
        """Test that error codes have the correct values."""
        # Configuration errors (1000-1999)
        self.assertEqual(ErrorCode.INVALID_CONFIGURATION.value, 1000)
        self.assertEqual(ErrorCode.MISSING_CONFIGURATION.value, 1001)
        self.assertEqual(ErrorCode.INCOMPATIBLE_CONFIGURATION.value, 1002)
        self.assertEqual(ErrorCode.CONFIGURATION_ERROR.value, 1003)

        # Input/validation errors (2000-2999)
        self.assertEqual(ErrorCode.INVALID_INPUT.value, 2000)
        self.assertEqual(ErrorCode.MISSING_REQUIRED_FIELD.value, 2001)
        self.assertEqual(ErrorCode.TYPE_ERROR.value, 2002)
        self.assertEqual(ErrorCode.VALUE_ERROR.value, 2003)
        self.assertEqual(ErrorCode.FORMAT_ERROR.value, 2004)

        # Processing errors (3000-3999)
        self.assertEqual(ErrorCode.PROCESSING_ERROR.value, 3000)
        self.assertEqual(ErrorCode.TRANSFORMATION_ERROR.value, 3001)
        self.assertEqual(ErrorCode.PARSING_ERROR.value, 3002)

        # I/O errors (4000-4999)
        self.assertEqual(ErrorCode.FILE_NOT_FOUND.value, 4000)
        self.assertEqual(ErrorCode.PERMISSION_ERROR.value, 4001)
        self.assertEqual(ErrorCode.FILE_READ_ERROR.value, 4002)
        self.assertEqual(ErrorCode.FILE_WRITE_ERROR.value, 4003)

        # External service errors (5000-5999)
        self.assertEqual(ErrorCode.SERVICE_UNAVAILABLE.value, 5000)
        self.assertEqual(ErrorCode.SERVICE_TIMEOUT.value, 5001)
        self.assertEqual(ErrorCode.SERVICE_ERROR.value, 5002)

        # Unexpected/internal errors (9000-9999)
        self.assertEqual(ErrorCode.UNEXPECTED_ERROR.value, 9000)
        self.assertEqual(ErrorCode.INTERNAL_ERROR.value, 9001)

    def test_error_code_names(self):
        """Test that error codes have the correct names."""
        self.assertEqual(ErrorCode.INVALID_CONFIGURATION.name, "INVALID_CONFIGURATION")
        self.assertEqual(ErrorCode.PROCESSING_ERROR.name, "PROCESSING_ERROR")
        self.assertEqual(ErrorCode.FILE_NOT_FOUND.name, "FILE_NOT_FOUND")
        self.assertEqual(ErrorCode.SERVICE_UNAVAILABLE.name, "SERVICE_UNAVAILABLE")
        self.assertEqual(ErrorCode.UNEXPECTED_ERROR.name, "UNEXPECTED_ERROR")

    def test_error_code_is_enum(self):
        """Test that ErrorCode is an enum."""
        from enum import Enum
        self.assertTrue(issubclass(ErrorCode, Enum))


class TestErrorContext(unittest.TestCase):
    """Test cases for the ErrorContext class."""

    def test_error_context_initialization(self):
        """Test basic ErrorContext initialization."""
        context = ErrorContext(
            error_code=ErrorCode.PROCESSING_ERROR,
            message="Test error message",
        )
        self.assertEqual(context.error_code, ErrorCode.PROCESSING_ERROR)
        self.assertEqual(context.message, "Test error message")
        self.assertEqual(context.details, {})
        self.assertIsNone(context.suggestion)

    def test_error_context_with_all_fields(self):
        """Test ErrorContext initialization with all fields."""
        details = {"key1": "value1", "key2": 123}
        context = ErrorContext(
            error_code=ErrorCode.INVALID_INPUT,
            message="Test message",
            details=details,
            suggestion="Try this instead",
            module="test_module.py",
            function="test_function",
            line_number=42,
        )
        self.assertEqual(context.error_code, ErrorCode.INVALID_INPUT)
        self.assertEqual(context.message, "Test message")
        self.assertEqual(context.details, details)
        self.assertEqual(context.suggestion, "Try this instead")
        self.assertEqual(context.module, "test_module.py")
        self.assertEqual(context.function, "test_function")
        self.assertEqual(context.line_number, 42)

    def test_error_context_auto_location(self):
        """Test that ErrorContext automatically captures location information."""
        context = ErrorContext(
            error_code=ErrorCode.PROCESSING_ERROR,
            message="Test error",
        )
        # Should have captured some location information
        self.assertIsNotNone(context.module)
        self.assertIsNotNone(context.function)
        self.assertIsNotNone(context.line_number)

    def test_error_context_to_dict(self):
        """Test converting ErrorContext to dictionary."""
        details = {"key": "value"}
        context = ErrorContext(
            error_code=ErrorCode.FILE_READ_ERROR,
            message="Test error",
            details=details,
            suggestion="Check permissions",
            module="test.py",
            function="test_func",
            line_number=10,
        )
        result = context.to_dict()

        self.assertEqual(result["error_code"]["code"], 4002)
        self.assertEqual(result["error_code"]["name"], "FILE_READ_ERROR")
        self.assertEqual(result["message"], "Test error")
        self.assertEqual(result["details"], details)
        self.assertEqual(result["suggestion"], "Check permissions")
        self.assertEqual(result["location"]["module"], "test.py")
        self.assertEqual(result["location"]["function"], "test_func")
        self.assertEqual(result["location"]["line_number"], 10)

    def test_error_context_str(self):
        """Test string representation of ErrorContext."""
        context = ErrorContext(
            error_code=ErrorCode.PROCESSING_ERROR,
            message="Test error",
            details={"key": "value"},
            suggestion="Try again",
            module="test.py",
            function="func",
            line_number=5,
        )
        result = str(context)

        self.assertIn("[3000]", result)
        self.assertIn("PROCESSING_ERROR", result)
        self.assertIn("Test error", result)
        self.assertIn("test.py:func", result)
        self.assertIn("line 5", result)
        self.assertIn("Details:", result)
        self.assertIn("Suggestion: Try again", result)

    def test_error_context_str_minimal(self):
        """Test string representation with minimal fields."""
        context = ErrorContext(
            error_code=ErrorCode.INVALID_INPUT,
            message="Simple error",
            module="test.py",
            function="func",
            line_number=1,
        )
        result = str(context)

        self.assertIn("[2000]", result)
        self.assertIn("INVALID_INPUT", result)
        self.assertIn("Simple error", result)
        self.assertNotIn("Details:", result)
        self.assertNotIn("Suggestion:", result)


class TestAnnotationToolkitError(unittest.TestCase):
    """Test cases for the base AnnotationToolkitError class."""

    @patch('annotation_toolkit.utils.errors.logger')
    def test_basic_initialization(self, mock_logger):
        """Test basic error initialization."""
        error = AnnotationToolkitError("Test error")
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.error_code, ErrorCode.UNEXPECTED_ERROR)
        self.assertEqual(error.details, {})
        self.assertIsNone(error.suggestion)
        self.assertIsNone(error.cause)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_initialization_with_all_fields(self, mock_logger):
        """Test error initialization with all fields."""
        cause = ValueError("Original error")
        details = {"field": "value"}
        error = AnnotationToolkitError(
            message="Test error",
            error_code=ErrorCode.PROCESSING_ERROR,
            details=details,
            suggestion="Fix it",
            cause=cause,
        )
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.error_code, ErrorCode.PROCESSING_ERROR)
        self.assertEqual(error.details, details)
        self.assertEqual(error.suggestion, "Fix it")
        self.assertEqual(error.cause, cause)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_error_logging(self, mock_logger):
        """Test that errors are logged on creation."""
        error = AnnotationToolkitError("Test error")
        mock_logger.error.assert_called_once()

    @patch('annotation_toolkit.utils.errors.logger')
    def test_error_logging_with_cause(self, mock_logger):
        """Test that cause is logged in debug mode."""
        cause = ValueError("Original error")
        error = AnnotationToolkitError("Test error", cause=cause)
        mock_logger.error.assert_called_once()
        mock_logger.debug.assert_called_once()
        debug_call = mock_logger.debug.call_args[0][0]
        self.assertIn("Original error", debug_call)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_error_properties(self, mock_logger):
        """Test error properties."""
        details = {"key": "value"}
        error = AnnotationToolkitError(
            message="Test",
            error_code=ErrorCode.FILE_NOT_FOUND,
            details=details,
            suggestion="Check path",
        )
        # Test property accessors
        self.assertEqual(error.error_code, ErrorCode.FILE_NOT_FOUND)
        self.assertEqual(error.message, "Test")
        self.assertEqual(error.details, details)
        self.assertEqual(error.suggestion, "Check path")

    @patch('annotation_toolkit.utils.errors.logger')
    def test_error_str_representation(self, mock_logger):
        """Test string representation of error."""
        error = AnnotationToolkitError(
            message="Test error",
            error_code=ErrorCode.PROCESSING_ERROR,
        )
        result = str(error)
        self.assertIn("PROCESSING_ERROR", result)
        self.assertIn("Test error", result)


class TestConfigurationErrors(unittest.TestCase):
    """Test cases for configuration error classes."""

    @patch('annotation_toolkit.utils.errors.logger')
    def test_configuration_error(self, mock_logger):
        """Test ConfigurationError initialization."""
        error = ConfigurationError("Config error")
        self.assertEqual(error.message, "Config error")
        self.assertEqual(error.error_code, ErrorCode.INVALID_CONFIGURATION)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_configuration_error_custom_code(self, mock_logger):
        """Test ConfigurationError with custom error code."""
        error = ConfigurationError(
            "Config error", error_code=ErrorCode.MISSING_CONFIGURATION
        )
        self.assertEqual(error.error_code, ErrorCode.MISSING_CONFIGURATION)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_missing_configuration_error(self, mock_logger):
        """Test MissingConfigurationError."""
        error = MissingConfigurationError("Missing field 'api_key'")
        self.assertEqual(error.error_code, ErrorCode.MISSING_CONFIGURATION)
        self.assertIsNotNone(error.suggestion)
        self.assertIn("configuration file", error.suggestion)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_missing_configuration_error_custom_suggestion(self, mock_logger):
        """Test MissingConfigurationError with custom suggestion."""
        error = MissingConfigurationError(
            "Missing field", suggestion="Add the field to config.yaml"
        )
        self.assertEqual(error.suggestion, "Add the field to config.yaml")

    @patch('annotation_toolkit.utils.errors.logger')
    def test_invalid_configuration_error(self, mock_logger):
        """Test InvalidConfigurationError."""
        error = InvalidConfigurationError("Invalid value for 'timeout'")
        self.assertEqual(error.error_code, ErrorCode.INVALID_CONFIGURATION)
        self.assertIsNotNone(error.suggestion)


class TestValidationErrors(unittest.TestCase):
    """Test cases for validation error classes."""

    @patch('annotation_toolkit.utils.errors.logger')
    def test_validation_error(self, mock_logger):
        """Test base ValidationError."""
        error = ValidationError("Validation failed")
        self.assertEqual(error.error_code, ErrorCode.INVALID_INPUT)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_missing_required_field_error(self, mock_logger):
        """Test MissingRequiredFieldError."""
        error = MissingRequiredFieldError("username")
        self.assertIn("username", error.message)
        self.assertEqual(error.error_code, ErrorCode.MISSING_REQUIRED_FIELD)
        self.assertIn("username", error.suggestion)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_missing_required_field_with_details(self, mock_logger):
        """Test MissingRequiredFieldError with details."""
        details = {"expected_fields": ["username", "password"]}
        error = MissingRequiredFieldError("username", details=details)
        self.assertEqual(error.details, details)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_type_validation_error_single_type(self, mock_logger):
        """Test TypeValidationError with single expected type."""
        error = TypeValidationError("age", int, str)
        self.assertIn("age", error.message)
        self.assertIn("int", error.message)
        self.assertIn("str", error.message)
        self.assertEqual(error.error_code, ErrorCode.TYPE_ERROR)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_type_validation_error_multiple_types(self, mock_logger):
        """Test TypeValidationError with multiple expected types."""
        error = TypeValidationError("value", [int, float], str)
        self.assertIn("value", error.message)
        self.assertIn("int", error.message)
        self.assertIn("float", error.message)
        self.assertIn("or", error.message)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_value_validation_error(self, mock_logger):
        """Test ValueValidationError."""
        error = ValueValidationError("age", -5, "must be positive")
        self.assertIn("age", error.message)
        self.assertIn("-5", error.message)
        self.assertIn("must be positive", error.message)
        self.assertEqual(error.error_code, ErrorCode.VALUE_ERROR)


class TestProcessingErrors(unittest.TestCase):
    """Test cases for processing error classes."""

    @patch('annotation_toolkit.utils.errors.logger')
    def test_processing_error(self, mock_logger):
        """Test base ProcessingError."""
        error = ProcessingError("Processing failed")
        self.assertEqual(error.error_code, ErrorCode.PROCESSING_ERROR)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_processing_error_with_cause(self, mock_logger):
        """Test ProcessingError with cause."""
        cause = ValueError("Invalid data")
        error = ProcessingError("Processing failed", cause=cause)
        self.assertEqual(error.cause, cause)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_transformation_error(self, mock_logger):
        """Test TransformationError."""
        error = TransformationError("Failed to transform data")
        self.assertEqual(error.error_code, ErrorCode.TRANSFORMATION_ERROR)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_tool_execution_error(self, mock_logger):
        """Test ToolExecutionError."""
        error = ToolExecutionError("Tool failed to execute")
        self.assertEqual(error.error_code, ErrorCode.PROCESSING_ERROR)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_parsing_error(self, mock_logger):
        """Test ParsingError."""
        error = ParsingError("Failed to parse JSON")
        self.assertEqual(error.error_code, ErrorCode.PARSING_ERROR)


class TestIOErrors(unittest.TestCase):
    """Test cases for I/O error classes."""

    @patch('annotation_toolkit.utils.errors.logger')
    def test_io_error(self, mock_logger):
        """Test base IOError."""
        error = IOError("I/O operation failed")
        self.assertEqual(error.error_code, ErrorCode.FILE_READ_ERROR)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_file_not_found_error(self, mock_logger):
        """Test FileNotFoundError."""
        error = FileNotFoundError("/path/to/file.txt")
        self.assertIn("/path/to/file.txt", error.message)
        self.assertEqual(error.error_code, ErrorCode.FILE_NOT_FOUND)
        self.assertIn("path is correct", error.suggestion)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_file_read_error(self, mock_logger):
        """Test FileReadError."""
        error = FileReadError("/path/to/file.txt")
        self.assertIn("/path/to/file.txt", error.message)
        self.assertEqual(error.error_code, ErrorCode.FILE_READ_ERROR)
        self.assertIn("permissions", error.suggestion)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_file_write_error(self, mock_logger):
        """Test FileWriteError."""
        error = FileWriteError("/path/to/file.txt")
        self.assertIn("/path/to/file.txt", error.message)
        self.assertEqual(error.error_code, ErrorCode.FILE_WRITE_ERROR)
        self.assertIn("disk space", error.suggestion)


class TestServiceErrors(unittest.TestCase):
    """Test cases for service error classes."""

    @patch('annotation_toolkit.utils.errors.logger')
    def test_service_error(self, mock_logger):
        """Test base ServiceError."""
        error = ServiceError("Service error")
        self.assertEqual(error.error_code, ErrorCode.SERVICE_ERROR)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_service_unavailable_error(self, mock_logger):
        """Test ServiceUnavailableError."""
        error = ServiceUnavailableError("API")
        self.assertIn("API", error.message)
        self.assertEqual(error.error_code, ErrorCode.SERVICE_UNAVAILABLE)
        self.assertIn("API", error.suggestion)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_service_timeout_error(self, mock_logger):
        """Test ServiceTimeoutError without timeout value."""
        error = ServiceTimeoutError("Database")
        self.assertIn("Database", error.message)
        self.assertEqual(error.error_code, ErrorCode.SERVICE_TIMEOUT)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_service_timeout_error_with_timeout(self, mock_logger):
        """Test ServiceTimeoutError with timeout value."""
        error = ServiceTimeoutError("Database", timeout=30.0)
        self.assertIn("Database", error.message)
        self.assertIn("30", error.message)
        self.assertEqual(error.error_code, ErrorCode.SERVICE_TIMEOUT)


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for error utility functions."""

    @patch('annotation_toolkit.utils.errors.logger')
    def test_handle_exception_with_annotation_toolkit_error(self, mock_logger):
        """Test handle_exception with AnnotationToolkitError."""
        original_error = ProcessingError("Test error")
        result = handle_exception(original_error)
        # Should return the same error
        self.assertIs(result, original_error)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_handle_exception_with_standard_exception(self, mock_logger):
        """Test handle_exception with standard exception."""
        original_error = ValueError("Test error")
        result = handle_exception(original_error)
        # Should wrap in AnnotationToolkitError
        self.assertIsInstance(result, AnnotationToolkitError)
        self.assertEqual(result.cause, original_error)
        self.assertIn("Test error", result.message)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_handle_exception_with_custom_message(self, mock_logger):
        """Test handle_exception with custom message."""
        original_error = ValueError("Original")
        result = handle_exception(
            original_error,
            error_code=ErrorCode.PROCESSING_ERROR,
            message="Custom message",
            details={"key": "value"},
            suggestion="Fix it",
        )
        self.assertEqual(result.message, "Custom message")
        self.assertEqual(result.error_code, ErrorCode.PROCESSING_ERROR)
        self.assertEqual(result.details, {"key": "value"})
        self.assertEqual(result.suggestion, "Fix it")

    @patch('annotation_toolkit.utils.errors.logger')
    def test_safe_execute_success(self, mock_logger):
        """Test safe_execute with successful function."""
        def successful_func(x, y):
            return x + y

        result = safe_execute(successful_func, 2, 3)
        self.assertEqual(result, 5)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_safe_execute_with_exception(self, mock_logger):
        """Test safe_execute with function that raises exception."""
        def failing_func():
            raise ValueError("Test error")

        with self.assertRaises(AnnotationToolkitError) as context:
            safe_execute(failing_func)

        error = context.exception
        self.assertIsInstance(error.cause, ValueError)
        self.assertIn("failing_func", error.message)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_safe_execute_with_custom_error_details(self, mock_logger):
        """Test safe_execute with custom error details."""
        def failing_func(x):
            raise ValueError("Error")

        with self.assertRaises(AnnotationToolkitError) as context:
            safe_execute(
                failing_func,
                42,
                error_code=ErrorCode.PROCESSING_ERROR,
                error_message="Custom error message",
                details={"custom": "detail"},
                suggestion="Try this",
            )

        error = context.exception
        self.assertEqual(error.message, "Custom error message")
        self.assertEqual(error.error_code, ErrorCode.PROCESSING_ERROR)
        self.assertEqual(error.suggestion, "Try this")
        # Should include both custom details and args
        self.assertIn("custom", error.details)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_safe_execute_with_kwargs(self, mock_logger):
        """Test safe_execute with keyword arguments."""
        def func_with_kwargs(a, b=10):
            return a * b

        result = safe_execute(func_with_kwargs, 5, b=3)
        self.assertEqual(result, 15)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_safe_execute_includes_args_in_details(self, mock_logger):
        """Test that safe_execute includes function args in error details."""
        def failing_func(x, y):
            raise ValueError("Error")

        with self.assertRaises(AnnotationToolkitError) as context:
            safe_execute(failing_func, "test", 123)

        error = context.exception
        self.assertIn("args", error.details)
        # Should include simple types
        self.assertIn("test", error.details["args"])
        self.assertIn(123, error.details["args"])

    @patch('annotation_toolkit.utils.errors.logger')
    def test_safe_execute_with_complex_args(self, mock_logger):
        """Test safe_execute with complex argument types."""
        def failing_func(obj):
            raise ValueError("Error")

        class CustomClass:
            pass

        with self.assertRaises(AnnotationToolkitError) as context:
            safe_execute(failing_func, CustomClass())

        error = context.exception
        # Complex types should be represented as type names
        self.assertIn("args", error.details)
        args_repr = str(error.details["args"])
        self.assertIn("CustomClass", args_repr)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_format_exception_with_annotation_toolkit_error(self, mock_logger):
        """Test format_exception with AnnotationToolkitError."""
        error = ProcessingError("Test error")
        result = format_exception(error)
        self.assertIn("Test error", result)
        self.assertIn("PROCESSING_ERROR", result)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_format_exception_with_cause(self, mock_logger):
        """Test format_exception with error that has a cause."""
        cause = ValueError("Original error")
        error = ProcessingError("Wrapper error", cause=cause)
        result = format_exception(error)
        self.assertIn("Wrapper error", result)
        self.assertIn("Caused by:", result)
        self.assertIn("Original error", result)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_format_exception_with_standard_exception(self, mock_logger):
        """Test format_exception with standard exception."""
        error = ValueError("Test error")
        result = format_exception(error)
        self.assertIn("ValueError", result)
        self.assertIn("Test error", result)
        self.assertIn("Traceback:", result)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_get_error_details_with_annotation_toolkit_error(self, mock_logger):
        """Test get_error_details with AnnotationToolkitError."""
        details_dict = {"key": "value"}
        error = ProcessingError("Test", details=details_dict, suggestion="Fix")
        result = get_error_details(error)

        self.assertEqual(result["message"], "Test")
        self.assertEqual(result["error_code"]["code"], ErrorCode.PROCESSING_ERROR.value)
        self.assertEqual(result["error_code"]["name"], "PROCESSING_ERROR")
        self.assertEqual(result["details"], details_dict)
        self.assertEqual(result["suggestion"], "Fix")
        self.assertIn("location", result)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_get_error_details_with_cause(self, mock_logger):
        """Test get_error_details with error that has a cause."""
        cause = ValueError("Original")
        error = ProcessingError("Wrapper", cause=cause)
        result = get_error_details(error)

        self.assertIn("cause", result)
        self.assertEqual(result["cause"]["type"], "ValueError")
        self.assertEqual(result["cause"]["message"], "Original")

    @patch('annotation_toolkit.utils.errors.logger')
    def test_get_error_details_with_standard_exception(self, mock_logger):
        """Test get_error_details with standard exception."""
        error = ValueError("Test error")
        result = get_error_details(error)

        self.assertEqual(result["type"], "ValueError")
        self.assertEqual(result["message"], "Test error")
        self.assertEqual(result["error_code"]["code"], ErrorCode.UNEXPECTED_ERROR.value)
        self.assertIn("traceback", result)


class TestErrorContextFilenameExtraction(unittest.TestCase):
    """Test cases for ErrorContext filename extraction."""

    @patch('annotation_toolkit.utils.errors.logger')
    def test_error_context_extracts_filename_from_path(self, mock_logger):
        """Test that ErrorContext extracts just the filename from full path."""
        import tempfile
        import os

        # Create a temporary file to get a real path
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tf:
            temp_path = tf.name

        try:
            context = ErrorContext(
                error_code=ErrorCode.PROCESSING_ERROR,
                message="Test",
                module=temp_path,
                function="test",
                line_number=1,
            )
            # Should extract just the filename, not the full path
            self.assertEqual(context.module, os.path.basename(temp_path))
            self.assertNotIn("/", context.module)
            self.assertNotIn("\\", context.module)
        finally:
            os.unlink(temp_path)


class TestErrorInheritance(unittest.TestCase):
    """Test cases for error class inheritance."""

    def test_all_errors_inherit_from_base(self):
        """Test that all custom errors inherit from AnnotationToolkitError."""
        error_classes = [
            ConfigurationError,
            MissingConfigurationError,
            InvalidConfigurationError,
            ValidationError,
            MissingRequiredFieldError,
            TypeValidationError,
            ValueValidationError,
            ProcessingError,
            TransformationError,
            ToolExecutionError,
            ParsingError,
            IOError,
            FileNotFoundError,
            FileReadError,
            FileWriteError,
            ServiceError,
            ServiceUnavailableError,
            ServiceTimeoutError,
        ]

        for error_class in error_classes:
            self.assertTrue(issubclass(error_class, AnnotationToolkitError))

    def test_all_errors_are_exceptions(self):
        """Test that all errors are Exception subclasses."""
        error_classes = [
            AnnotationToolkitError,
            ConfigurationError,
            ValidationError,
            ProcessingError,
            IOError,
            ServiceError,
        ]

        for error_class in error_classes:
            self.assertTrue(issubclass(error_class, Exception))


if __name__ == "__main__":
    unittest.main()
