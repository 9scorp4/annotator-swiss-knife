"""
Error handling module for the annotation toolkit.

This module provides a comprehensive error handling system with custom exception
classes, error codes, and utilities for creating detailed and actionable error messages.
"""

import inspect
import os
import sys
import traceback
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union

from .logger import get_logger

logger = get_logger()


class ErrorCode(Enum):
    """
    Enumeration of error codes for categorizing errors.

    Error codes are grouped by category:
    - 1000-1999: Configuration errors
    - 2000-2999: Input/validation errors
    - 3000-3999: Processing errors
    - 4000-4999: I/O errors
    - 5000-5999: External service errors
    - 9000-9999: Unexpected/internal errors
    """

    # Configuration errors (1000-1999)
    INVALID_CONFIGURATION = 1000
    MISSING_CONFIGURATION = 1001
    INCOMPATIBLE_CONFIGURATION = 1002
    CONFIGURATION_ERROR = 1003

    # Input/validation errors (2000-2999)
    INVALID_INPUT = 2000
    MISSING_REQUIRED_FIELD = 2001
    TYPE_ERROR = 2002
    VALUE_ERROR = 2003
    FORMAT_ERROR = 2004
    VALIDATION_ERROR = 2005

    # Processing errors (3000-3999)
    PROCESSING_ERROR = 3000
    TRANSFORMATION_ERROR = 3001
    PARSING_ERROR = 3002

    # I/O errors (4000-4999)
    FILE_NOT_FOUND = 4000
    PERMISSION_ERROR = 4001
    FILE_READ_ERROR = 4002
    FILE_WRITE_ERROR = 4003

    # External service errors (5000-5999)
    SERVICE_UNAVAILABLE = 5000
    SERVICE_TIMEOUT = 5001
    SERVICE_ERROR = 5002

    # Unexpected/internal errors (9000-9999)
    UNEXPECTED_ERROR = 9000
    INTERNAL_ERROR = 9001


class ErrorContext:
    """
    Class for storing context information about an error.

    This class collects information about where and why an error occurred,
    making it easier to diagnose and fix issues.
    """

    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        module: Optional[str] = None,
        function: Optional[str] = None,
        line_number: Optional[int] = None,
    ):
        """
        Initialize the error context.

        Args:
            error_code: The error code categorizing this error.
            message: A human-readable error message.
            details: Additional details about the error (e.g., input values).
            suggestion: A suggestion for how to fix the error.
            module: The module where the error occurred.
            function: The function where the error occurred.
            line_number: The line number where the error occurred.
        """
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.suggestion = suggestion

        # If location info not provided, try to determine it automatically
        if module is None or function is None or line_number is None:
            frame = inspect.currentframe()
            if frame:
                # Get the caller's frame (2 frames up from current)
                caller_frame = inspect.getouterframes(frame)[2]
                self.module = module or caller_frame.filename
                self.function = function or caller_frame.function
                self.line_number = line_number or caller_frame.lineno
                # Clean up to prevent reference cycles
                del frame
            else:
                self.module = module or "unknown"
                self.function = function or "unknown"
                self.line_number = line_number or 0
        else:
            self.module = module
            self.function = function
            self.line_number = line_number

        # Extract just the filename from the full path
        if os.path.isfile(self.module):
            self.module = os.path.basename(self.module)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the error context to a dictionary.

        Returns:
            A dictionary representation of the error context.
        """
        return {
            "error_code": {"code": self.error_code.value, "name": self.error_code.name},
            "message": self.message,
            "details": self.details,
            "suggestion": self.suggestion,
            "location": {
                "module": self.module,
                "function": self.function,
                "line_number": self.line_number,
            },
        }

    def __str__(self) -> str:
        """
        Get a string representation of the error context.

        Returns:
            A formatted string with error information.
        """
        result = f"[{self.error_code.value}] {self.error_code.name}: {self.message}"
        result += f" (in {self.module}:{self.function}, line {self.line_number})"

        if self.details:
            result += f"\nDetails: {self.details}"

        if self.suggestion:
            result += f"\nSuggestion: {self.suggestion}"

        return result


class AnnotationToolkitError(Exception):
    """
    Base exception class for all annotation toolkit errors.

    This class provides a consistent interface for all errors in the toolkit,
    with detailed context information to help diagnose and fix issues.
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.UNEXPECTED_ERROR,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        """
        Initialize the exception.

        Args:
            message: A human-readable error message.
            error_code: The error code categorizing this error.
            details: Additional details about the error (e.g., input values).
            suggestion: A suggestion for how to fix the error.
            cause: The underlying exception that caused this error, if any.
        """
        self.context = ErrorContext(
            error_code=error_code,
            message=message,
            details=details,
            suggestion=suggestion,
        )
        self.cause = cause

        # Log the error
        logger.error(str(self))
        if cause:
            logger.debug(f"Caused by: {str(cause)}")

        # Initialize the base Exception class
        super().__init__(str(self))

    @property
    def error_code(self) -> ErrorCode:
        """
        Get the error code from the context.

        Returns:
            The error code for this error.
        """
        return self.context.error_code

    @property
    def message(self) -> str:
        """
        Get the message from the context.

        Returns:
            The message for this error.
        """
        return self.context.message

    @property
    def details(self) -> Dict[str, Any]:
        """
        Get the details from the context.

        Returns:
            The details for this error.
        """
        return self.context.details

    @property
    def suggestion(self) -> Optional[str]:
        """
        Get the suggestion from the context.

        Returns:
            The suggestion for this error, or None if no suggestion is available.
        """
        return self.context.suggestion

    def __str__(self) -> str:
        """
        Get a string representation of the exception.

        Returns:
            A formatted string with error information.
        """
        return str(self.context)


# Configuration Errors


class ConfigurationError(AnnotationToolkitError):
    """Base class for configuration-related errors."""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.INVALID_CONFIGURATION,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message, error_code, details, suggestion, cause)


class MissingConfigurationError(ConfigurationError):
    """Exception raised when a required configuration is missing."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            message,
            ErrorCode.MISSING_CONFIGURATION,
            details,
            suggestion
            or "Check the configuration file and ensure all required fields are present.",
            cause,
        )


class InvalidConfigurationError(ConfigurationError):
    """Exception raised when a configuration value is invalid."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            message,
            ErrorCode.INVALID_CONFIGURATION,
            details,
            suggestion
            or "Check the configuration values and ensure they meet the required format and constraints.",
            cause,
        )


# Input/Validation Errors


class ValidationError(AnnotationToolkitError):
    """Base class for input validation errors."""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.INVALID_INPUT,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message, error_code, details, suggestion, cause)


class MissingRequiredFieldError(ValidationError):
    """Exception raised when a required field is missing from the input."""

    def __init__(
        self,
        field_name: str,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            f"Missing required field: {field_name}",
            ErrorCode.MISSING_REQUIRED_FIELD,
            details,
            suggestion or f"Ensure the '{field_name}' field is provided in the input.",
            cause,
        )


class TypeValidationError(ValidationError):
    """Exception raised when an input value has the wrong type."""

    def __init__(
        self,
        field_name: str,
        expected_type: Union[Type, List[Type]],
        actual_type: Type,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        if isinstance(expected_type, list):
            expected_type_str = " or ".join([t.__name__ for t in expected_type])
        else:
            expected_type_str = expected_type.__name__

        super().__init__(
            f"Invalid type for '{field_name}': expected {expected_type_str}, got {actual_type.__name__}",
            ErrorCode.TYPE_ERROR,
            details,
            suggestion
            or f"Ensure the '{field_name}' field is of type {expected_type_str}.",
            cause,
        )


class ValueValidationError(ValidationError):
    """Exception raised when an input value is invalid."""

    def __init__(
        self,
        field_name: str,
        value: Any,
        constraint: str,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            f"Invalid value for '{field_name}': {value} (constraint: {constraint})",
            ErrorCode.VALUE_ERROR,
            details,
            suggestion
            or f"Ensure the '{field_name}' field meets the constraint: {constraint}.",
            cause,
        )


# Processing Errors


class ProcessingError(AnnotationToolkitError):
    """Base class for errors that occur during data processing."""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.PROCESSING_ERROR,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message, error_code, details, suggestion, cause)


class TransformationError(ProcessingError):
    """Exception raised when a data transformation fails."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            message, ErrorCode.TRANSFORMATION_ERROR, details, suggestion, cause
        )


class ToolExecutionError(ProcessingError):
    """Exception raised when a tool execution fails."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            message, ErrorCode.PROCESSING_ERROR, details, suggestion, cause
        )


class ParsingError(ProcessingError):
    """Exception raised when parsing data fails."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message, ErrorCode.PARSING_ERROR, details, suggestion, cause)


# I/O Errors


class IOError(AnnotationToolkitError):
    """Base class for input/output errors."""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.FILE_READ_ERROR,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message, error_code, details, suggestion, cause)


class FileNotFoundError(IOError):
    """Exception raised when a file is not found."""

    def __init__(
        self,
        file_path: str,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            f"File not found: {file_path}",
            ErrorCode.FILE_NOT_FOUND,
            details,
            suggestion or "Check that the file exists and the path is correct.",
            cause,
        )


class FileReadError(IOError):
    """Exception raised when reading a file fails."""

    def __init__(
        self,
        file_path: str,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            f"Failed to read file: {file_path}",
            ErrorCode.FILE_READ_ERROR,
            details,
            suggestion or "Check file permissions and that the file is not corrupted.",
            cause,
        )


class FileWriteError(IOError):
    """Exception raised when writing to a file fails."""

    def __init__(
        self,
        file_path: str,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            f"Failed to write to file: {file_path}",
            ErrorCode.FILE_WRITE_ERROR,
            details,
            suggestion or "Check file permissions and available disk space.",
            cause,
        )


class ResourceError(IOError):
    """Exception raised when a resource operation fails."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            message,
            ErrorCode.PROCESSING_ERROR,
            details,
            suggestion or "Ensure the resource is properly managed and not already disposed.",
            cause,
        )


# External Service Errors


class ServiceError(AnnotationToolkitError):
    """Base class for errors related to external services."""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.SERVICE_ERROR,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message, error_code, details, suggestion, cause)


class ServiceUnavailableError(ServiceError):
    """Exception raised when an external service is unavailable."""

    def __init__(
        self,
        service_name: str,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            f"Service unavailable: {service_name}",
            ErrorCode.SERVICE_UNAVAILABLE,
            details,
            suggestion
            or f"Check that the {service_name} service is running and accessible.",
            cause,
        )


class ServiceTimeoutError(ServiceError):
    """Exception raised when a request to an external service times out."""

    def __init__(
        self,
        service_name: str,
        timeout: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        timeout_str = f" after {timeout} seconds" if timeout is not None else ""
        super().__init__(
            f"Service timeout: {service_name}{timeout_str}",
            ErrorCode.SERVICE_TIMEOUT,
            details,
            suggestion
            or f"Check the {service_name} service status or increase the timeout.",
            cause,
        )


# Utility functions


def handle_exception(
    exc: Exception,
    error_code: ErrorCode = ErrorCode.UNEXPECTED_ERROR,
    message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    suggestion: Optional[str] = None,
) -> AnnotationToolkitError:
    """
    Handle an exception by wrapping it in an appropriate AnnotationToolkitError.

    Args:
        exc: The exception to handle.
        error_code: The error code to use for the new exception.
        message: A custom error message. If None, uses str(exc).
        details: Additional details about the error.
        suggestion: A suggestion for how to fix the error.

    Returns:
        An AnnotationToolkitError that wraps the original exception.
    """
    if isinstance(exc, AnnotationToolkitError):
        # If it's already an AnnotationToolkitError, just return it
        return exc

    # Create a new AnnotationToolkitError that wraps the original exception
    return AnnotationToolkitError(
        message or str(exc), error_code, details, suggestion, exc
    )


def safe_execute(
    func: callable,
    *args,
    error_code: ErrorCode = ErrorCode.UNEXPECTED_ERROR,
    error_message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    suggestion: Optional[str] = None,
    **kwargs,
) -> Any:
    """
    Execute a function safely, catching and handling any exceptions.

    Args:
        func: The function to execute.
        *args: Positional arguments to pass to the function.
        error_code: The error code to use if an exception occurs.
        error_message: A custom error message to use if an exception occurs.
        details: Additional details to include in the error.
        suggestion: A suggestion for how to fix the error.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        The result of the function call.

    Raises:
        AnnotationToolkitError: If an exception occurs during function execution.
    """
    try:
        return func(*args, **kwargs)
    except Exception as exc:
        # Generate a default error message if none was provided
        if error_message is None:
            error_message = f"Error executing {func.__name__}: {str(exc)}"

        # Add function arguments to details if not already present
        if details is None:
            details = {}
        if "args" not in details:
            # Only include simple types in details to avoid circular references
            safe_args = []
            for arg in args:
                if isinstance(arg, (str, int, float, bool, type(None))):
                    safe_args.append(arg)
                else:
                    safe_args.append(f"{type(arg).__name__} instance")
            details["args"] = safe_args

        # Wrap the exception in an AnnotationToolkitError and raise it
        raise handle_exception(exc, error_code, error_message, details, suggestion)


def format_exception(exc: Exception) -> str:
    """
    Format an exception into a detailed string representation.

    Args:
        exc: The exception to format.

    Returns:
        A formatted string with exception details and traceback.
    """
    if isinstance(exc, AnnotationToolkitError):
        # For our custom errors, include the context information
        result = str(exc)
        if exc.cause:
            result += f"\n\nCaused by: {str(exc.cause)}"
            if not isinstance(exc.cause, AnnotationToolkitError):
                # Include traceback for non-custom exceptions
                tb = "".join(
                    traceback.format_exception(
                        type(exc.cause), exc.cause, exc.cause.__traceback__
                    )
                )
                result += f"\n\nTraceback:\n{tb}"
    else:
        # For standard exceptions, include the traceback
        result = f"{type(exc).__name__}: {str(exc)}"
        tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        result += f"\n\nTraceback:\n{tb}"

    return result


def get_error_details(exc: Exception) -> Dict[str, Any]:
    """
    Get detailed information about an exception as a dictionary.

    Args:
        exc: The exception to get details for.

    Returns:
        A dictionary with exception details.
    """
    if isinstance(exc, AnnotationToolkitError):
        # For our custom errors, return the context as a dictionary
        result = exc.context.to_dict()
        if exc.cause:
            result["cause"] = {
                "type": type(exc.cause).__name__,
                "message": str(exc.cause),
            }
    else:
        # For standard exceptions, create a basic dictionary
        result = {
            "error_code": {
                "code": ErrorCode.UNEXPECTED_ERROR.value,
                "name": ErrorCode.UNEXPECTED_ERROR.name,
            },
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exception(type(exc), exc, exc.__traceback__),
        }

    return result
