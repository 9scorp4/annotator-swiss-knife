"""
Comprehensive tests for the error handler utilities.

This module contains comprehensive tests for the error handling utilities in the
annotation_toolkit.utils.error_handler module, including all decorators and utility functions.
"""

import unittest
from unittest.mock import patch, MagicMock, call

from annotation_toolkit.utils.error_handler import (
    with_error_handling,
    handle_errors,
    format_error_for_user,
    try_except_with_finally,
    catch_specific_exceptions,
    log_error_and_continue,
    create_error_boundary,
)
from annotation_toolkit.utils.errors import (
    AnnotationToolkitError,
    ErrorCode,
    ConfigurationError,
    ProcessingError,
    ValidationError,
)


class TestFormatErrorForUser(unittest.TestCase):
    """Test cases for format_error_for_user function."""

    @patch('annotation_toolkit.utils.errors.logger')
    def test_format_error_for_user_simple(self, mock_logger):
        """Test formatting a simple error message."""
        error = AnnotationToolkitError("Test error")
        message = format_error_for_user(error)
        self.assertEqual(message, "Test error")

    @patch('annotation_toolkit.utils.errors.logger')
    def test_format_error_for_user_with_suggestion(self, mock_logger):
        """Test formatting an error message with a suggestion."""
        error = AnnotationToolkitError("Test error", suggestion="Try this instead")
        message = format_error_for_user(error)
        self.assertEqual(message, "Test error\nSuggestion: Try this instead")

    @patch('annotation_toolkit.utils.errors.logger')
    def test_format_error_for_user_with_details(self, mock_logger):
        """Test formatting an error message with details."""
        error = AnnotationToolkitError(
            "Test error",
            details={"key": "value", "another_key": "another_value"}
        )
        message = format_error_for_user(error)
        self.assertEqual(message, "Test error\nDetails: key=value, another_key=another_value")

    @patch('annotation_toolkit.utils.errors.logger')
    def test_format_error_for_user_with_all(self, mock_logger):
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

    @patch('annotation_toolkit.utils.errors.logger')
    def test_format_error_for_user_with_unexpected_error(self, mock_logger):
        """Test that UNEXPECTED_ERROR code is not shown."""
        error = AnnotationToolkitError(
            "Test error",
            error_code=ErrorCode.UNEXPECTED_ERROR,
        )
        message = format_error_for_user(error)
        # Error code should not be shown for UNEXPECTED_ERROR
        self.assertEqual(message, "Test error")
        self.assertNotIn("Error code:", message)

    def test_format_error_for_user_with_standard_exception(self):
        """Test formatting a standard (non-toolkit) exception."""
        error = ValueError("Standard error")
        message = format_error_for_user(error)
        self.assertEqual(message, "An unexpected error occurred: Standard error")


class TestHandleErrorsDecorator(unittest.TestCase):
    """Test cases for handle_errors decorator."""

    def test_handle_errors_no_error(self):
        """Test handle_errors with no error."""
        @handle_errors
        def func():
            return "success"

        result = func()
        self.assertEqual(result, "success")

    def test_handle_errors_with_args_and_kwargs(self):
        """Test handle_errors preserves function arguments."""
        @handle_errors
        def func(a, b, c=10):
            return a + b + c

        result = func(1, 2, c=3)
        self.assertEqual(result, 6)

    @patch('annotation_toolkit.utils.errors.logger')
    def test_handle_errors_with_annotation_toolkit_error(self, mock_logger):
        """Test handle_errors with an AnnotationToolkitError."""
        @handle_errors
        def func():
            raise ConfigurationError("Test error")

        with self.assertRaises(ConfigurationError):
            func()

    @patch('annotation_toolkit.utils.errors.logger')
    def test_handle_errors_with_other_exception(self, mock_logger):
        """Test handle_errors with a non-AnnotationToolkitError exception."""
        @handle_errors
        def func():
            raise ValueError("Test error")

        with self.assertRaises(ProcessingError) as context:
            func()

        error = context.exception
        self.assertIn("func", error.message)
        self.assertIn("Test error", error.message)
        self.assertIsInstance(error.cause, ValueError)

    def test_handle_errors_preserves_metadata(self):
        """Test that handle_errors preserves function metadata."""
        @handle_errors
        def my_function():
            """My function docstring."""
            pass

        self.assertEqual(my_function.__name__, "my_function")
        self.assertEqual(my_function.__doc__, "My function docstring.")


class TestWithErrorHandlingDecorator(unittest.TestCase):
    """Test cases for with_error_handling decorator."""

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

    @patch('annotation_toolkit.utils.errors.logger')
    def test_with_error_handling_decorator_with_error(self, mock_logger):
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

    @patch('annotation_toolkit.utils.errors.logger')
    def test_with_error_handling_decorator_with_annotation_toolkit_error(self, mock_logger):
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

    @patch('annotation_toolkit.utils.errors.logger')
    def test_with_error_handling_with_func_name_template(self, mock_logger):
        """Test with_error_handling with {func_name} template in message."""
        decorator = with_error_handling(
            error_message="Error in {func_name}"
        )

        @decorator
        def my_special_function():
            raise ValueError("Test")

        with self.assertRaises(ProcessingError) as context:
            my_special_function()

        error = context.exception
        self.assertEqual(error.message, "Error in my_special_function")

    @patch('annotation_toolkit.utils.errors.logger')
    def test_with_error_handling_with_details(self, mock_logger):
        """Test with_error_handling with custom details."""
        decorator = with_error_handling(
            error_code=ErrorCode.PROCESSING_ERROR,
            details={"operation": "test", "context": "unit_test"}
        )

        @decorator
        def func():
            raise ValueError("Test")

        with self.assertRaises(ProcessingError) as context:
            func()

        error = context.exception
        self.assertEqual(error.details["operation"], "test")
        self.assertEqual(error.details["context"], "unit_test")

    def test_with_error_handling_preserves_metadata(self):
        """Test that with_error_handling preserves function metadata."""
        decorator = with_error_handling()

        @decorator
        def my_function():
            """My function docstring."""
            pass

        self.assertEqual(my_function.__name__, "my_function")
        self.assertEqual(my_function.__doc__, "My function docstring.")


class TestTryExceptWithFinally(unittest.TestCase):
    """Test cases for try_except_with_finally function."""

    def test_try_except_with_finally_success(self):
        """Test try_except_with_finally with successful function."""
        def try_func():
            return "success"

        result = try_except_with_finally(try_func)
        self.assertEqual(result, "success")

    def test_try_except_with_finally_with_args(self):
        """Test try_except_with_finally with function arguments."""
        def try_func(a, b):
            return a + b

        result = try_except_with_finally(try_func, None, None, 2, 3)
        self.assertEqual(result, 5)

    def test_try_except_with_finally_with_kwargs(self):
        """Test try_except_with_finally with keyword arguments."""
        def try_func(a, b=10):
            return a * b

        result = try_except_with_finally(try_func, None, None, 5, b=3)
        self.assertEqual(result, 15)

    def test_try_except_with_finally_with_exception(self):
        """Test try_except_with_finally with exception handling."""
        def try_func():
            raise ValueError("Test error")

        def except_func(exc):
            return f"Handled: {str(exc)}"

        result = try_except_with_finally(try_func, except_func)
        self.assertEqual(result, "Handled: Test error")

    def test_try_except_with_finally_with_finally_block(self):
        """Test try_except_with_finally with finally block."""
        finally_called = []

        def try_func():
            return "success"

        def finally_func():
            finally_called.append(True)

        result = try_except_with_finally(try_func, finally_func=finally_func)
        self.assertEqual(result, "success")
        self.assertEqual(finally_called, [True])

    def test_try_except_with_finally_with_all_blocks(self):
        """Test try_except_with_finally with all blocks."""
        finally_called = []

        def try_func():
            raise ValueError("Test")

        def except_func(exc):
            return "handled"

        def finally_func():
            finally_called.append(True)

        result = try_except_with_finally(try_func, except_func, finally_func)
        self.assertEqual(result, "handled")
        self.assertEqual(finally_called, [True])

    def test_try_except_with_finally_finally_runs_on_success(self):
        """Test that finally block runs even on success."""
        finally_called = []

        def try_func():
            return "success"

        def finally_func():
            finally_called.append(True)

        try_except_with_finally(try_func, finally_func=finally_func)
        self.assertTrue(finally_called)

    def test_try_except_with_finally_no_except_handler(self):
        """Test try_except_with_finally without except handler returns None on error."""
        def try_func():
            raise ValueError("Test")

        result = try_except_with_finally(try_func)
        self.assertIsNone(result)


class TestCatchSpecificExceptions(unittest.TestCase):
    """Test cases for catch_specific_exceptions decorator."""

    def test_catch_specific_exceptions_no_error(self):
        """Test catch_specific_exceptions with no error."""
        @catch_specific_exceptions({ValueError: lambda e: "handled_value_error"})
        def func():
            return "success"

        result = func()
        self.assertEqual(result, "success")

    def test_catch_specific_exceptions_catches_value_error(self):
        """Test catch_specific_exceptions catches ValueError."""
        @catch_specific_exceptions({ValueError: lambda e: "handled_value_error"})
        def func():
            raise ValueError("Test error")

        result = func()
        self.assertEqual(result, "handled_value_error")

    def test_catch_specific_exceptions_catches_multiple_types(self):
        """Test catch_specific_exceptions with multiple exception types."""
        handlers = {
            ValueError: lambda e: "value_error",
            KeyError: lambda e: "key_error",
            TypeError: lambda e: "type_error",
        }

        @catch_specific_exceptions(handlers)
        def func1():
            raise ValueError("Test")

        @catch_specific_exceptions(handlers)
        def func2():
            raise KeyError("Test")

        @catch_specific_exceptions(handlers)
        def func3():
            raise TypeError("Test")

        self.assertEqual(func1(), "value_error")
        self.assertEqual(func2(), "key_error")
        self.assertEqual(func3(), "type_error")

    def test_catch_specific_exceptions_unhandled_exception(self):
        """Test catch_specific_exceptions with unhandled exception type."""
        @catch_specific_exceptions({ValueError: lambda e: "handled"})
        def func():
            raise KeyError("Test error")

        with self.assertRaises(KeyError):
            func()

    def test_catch_specific_exceptions_handler_receives_exception(self):
        """Test that exception handlers receive the exception object."""
        received_exception = []

        @catch_specific_exceptions({
            ValueError: lambda e: received_exception.append(e) or "handled"
        })
        def func():
            raise ValueError("Custom message")

        result = func()
        self.assertEqual(result, "handled")
        self.assertEqual(len(received_exception), 1)
        self.assertIsInstance(received_exception[0], ValueError)
        self.assertEqual(str(received_exception[0]), "Custom message")

    def test_catch_specific_exceptions_with_inheritance(self):
        """Test catch_specific_exceptions respects exception inheritance."""
        # Exception is base class of ValueError
        @catch_specific_exceptions({Exception: lambda e: "handled_base"})
        def func():
            raise ValueError("Test")

        result = func()
        self.assertEqual(result, "handled_base")


class TestLogErrorAndContinue(unittest.TestCase):
    """Test cases for log_error_and_continue function."""

    @patch('annotation_toolkit.utils.error_handler.logger')
    @patch('annotation_toolkit.utils.errors.logger')
    def test_log_error_and_continue_with_toolkit_error(self, mock_errors_logger, mock_handler_logger):
        """Test log_error_and_continue with AnnotationToolkitError."""
        error = ProcessingError("Test error")
        log_error_and_continue(error)
        mock_handler_logger.error.assert_called_once()

    @patch('annotation_toolkit.utils.error_handler.logger')
    @patch('annotation_toolkit.utils.errors.logger')
    def test_log_error_and_continue_with_context(self, mock_errors_logger, mock_handler_logger):
        """Test log_error_and_continue with context string."""
        error = ProcessingError("Test error")
        log_error_and_continue(error, context="processing file")
        call_args = mock_handler_logger.error.call_args[0][0]
        self.assertIn("while processing file", call_args)

    @patch('annotation_toolkit.utils.error_handler.logger')
    def test_log_error_and_continue_with_standard_exception(self, mock_logger):
        """Test log_error_and_continue with standard exception."""
        error = ValueError("Test error")
        log_error_and_continue(error)
        mock_logger.error.assert_called_once()
        mock_logger.debug.assert_called_once()

    @patch('annotation_toolkit.utils.error_handler.logger')
    def test_log_error_and_continue_without_context(self, mock_logger):
        """Test log_error_and_continue without context."""
        error = ValueError("Test error")
        log_error_and_continue(error, context=None)
        call_args = mock_logger.error.call_args[0][0]
        self.assertNotIn("while", call_args)


class TestCreateErrorBoundary(unittest.TestCase):
    """Test cases for create_error_boundary decorator."""

    def test_create_error_boundary_no_error(self):
        """Test create_error_boundary with successful function."""
        @create_error_boundary(fallback_value="fallback")
        def func():
            return "success"

        result = func()
        self.assertEqual(result, "success")

    @patch('annotation_toolkit.utils.error_handler.logger')
    def test_create_error_boundary_with_error(self, mock_logger):
        """Test create_error_boundary returns fallback on error."""
        @create_error_boundary(fallback_value="fallback")
        def func():
            raise ValueError("Test error")

        result = func()
        self.assertEqual(result, "fallback")

    @patch('annotation_toolkit.utils.error_handler.logger')
    def test_create_error_boundary_with_error_handler(self, mock_logger):
        """Test create_error_boundary calls error handler."""
        handler_called = []

        def error_handler(exc):
            handler_called.append(exc)

        @create_error_boundary(fallback_value=[], error_handler=error_handler)
        def func():
            raise ValueError("Test error")

        result = func()
        self.assertEqual(result, [])
        self.assertEqual(len(handler_called), 1)
        self.assertIsInstance(handler_called[0], ValueError)

    @patch('annotation_toolkit.utils.error_handler.logger')
    def test_create_error_boundary_with_complex_fallback(self, mock_logger):
        """Test create_error_boundary with complex fallback value."""
        fallback = {"status": "error", "data": None}

        @create_error_boundary(fallback_value=fallback)
        def func():
            raise ValueError("Test")

        result = func()
        self.assertEqual(result, fallback)

    @patch('annotation_toolkit.utils.error_handler.logger')
    def test_create_error_boundary_logs_error(self, mock_logger):
        """Test that create_error_boundary logs errors."""
        @create_error_boundary(fallback_value=None)
        def my_func():
            raise ValueError("Test error")

        my_func()
        mock_logger.error.assert_called()
        call_args = mock_logger.error.call_args[0][0]
        self.assertIn("my_func", call_args)

    def test_create_error_boundary_preserves_metadata(self):
        """Test that create_error_boundary preserves function metadata."""
        @create_error_boundary(fallback_value=None)
        def my_function():
            """My function docstring."""
            pass

        self.assertEqual(my_function.__name__, "my_function")
        self.assertEqual(my_function.__doc__, "My function docstring.")


class TestErrorHandlerIntegration(unittest.TestCase):
    """Integration tests for error handler decorators."""

    @patch('annotation_toolkit.utils.errors.logger')
    def test_combining_decorators(self, mock_logger):
        """Test combining multiple error handling decorators."""
        @handle_errors
        @with_error_handling(error_code=ErrorCode.PROCESSING_ERROR)
        def func():
            raise ValueError("Test")

        with self.assertRaises(ProcessingError):
            func()

    @patch('annotation_toolkit.utils.error_handler.logger')
    def test_error_boundary_around_handle_errors(self, mock_logger):
        """Test error boundary around handle_errors decorator."""
        @create_error_boundary(fallback_value="safe")
        @handle_errors
        def func():
            raise ValueError("Test")

        result = func()
        self.assertEqual(result, "safe")


if __name__ == "__main__":
    unittest.main()
