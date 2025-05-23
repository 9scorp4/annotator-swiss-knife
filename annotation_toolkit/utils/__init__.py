"""
Utilities module for the Annotation Toolkit.

This package provides utility functions and helper classes used across the toolkit,
including file operations, formatting utilities, logging, and other common functionality.
"""

from .logger import get_logger, logger, Logger
from .errors import (
    # Base error classes
    ErrorCode,
    ErrorContext,
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
    get_error_details
)
from .error_handler import (
    # Error handling functions
    handle_errors,
    try_except_with_finally,
    format_error_for_user,
    log_error_and_continue,

    # Decorators
    with_error_handling,
    catch_specific_exceptions,
    create_error_boundary
)
