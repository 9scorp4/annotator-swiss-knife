"""
Error handler module for the annotation toolkit.

This module provides functions for handling errors in a consistent way across the application,
including formatting error messages, logging errors, and providing suggestions for resolving issues.
"""

import sys
import traceback
from typing import Any, Callable, cast, Dict, List, Optional, Type, TypeVar, Union

from .errors import (
    AnnotationToolkitError,
    ErrorCode,
    format_exception,
    get_error_details,
    handle_exception,
    ProcessingError,
    safe_execute,
)
from .logger import get_logger

logger = get_logger()

# Type variable for generic function return type
T = TypeVar("T")


def handle_errors(func):
    """
    Decorator that handles errors raised by the decorated function.

    This decorator catches exceptions raised by the function and:
    - Passes through AnnotationToolkitError instances unchanged
    - Wraps other exceptions in a ProcessingError

    Args:
        func: The function to decorate.

    Returns:
        The decorated function.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AnnotationToolkitError:
            # Pass through our custom errors unchanged
            raise
        except Exception as exc:
            # Wrap other exceptions in a ProcessingError
            raise ProcessingError(f"Error in {func.__name__}: {str(exc)}", cause=exc)

    # Preserve the original function's metadata
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__module__ = func.__module__

    return wrapper


def try_except_with_finally(
    try_func: Callable[..., T],
    except_func: Optional[Callable[[Exception], Any]] = None,
    finally_func: Optional[Callable[[], Any]] = None,
    *args: Any,
    **kwargs: Any,
) -> Optional[T]:
    """
    Execute a function with try/except/finally blocks.

    This function provides a cleaner way to handle try/except/finally patterns
    in a functional style.

    Args:
        try_func: The function to execute in the try block.
        except_func: The function to execute in the except block if an exception occurs.
            It receives the exception as an argument.
        finally_func: The function to execute in the finally block.
        *args: Positional arguments to pass to try_func.
        **kwargs: Keyword arguments to pass to try_func.

    Returns:
        The result of try_func, or None if an exception occurs and except_func doesn't return a value.
    """
    result = None
    try:
        result = try_func(*args, **kwargs)
    except Exception as exc:
        if except_func:
            result = except_func(exc)
    finally:
        if finally_func:
            finally_func()
    return result


def catch_specific_exceptions(
    exceptions_map: Dict[Type[Exception], Callable[[Exception], Any]]
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Create a decorator that catches specific exceptions and handles them with custom handlers.

    Args:
        exceptions_map: A dictionary mapping exception types to handler functions.
            Each handler function should accept the exception as its only argument.

    Returns:
        A decorator function.

    Example:
        ```python
        @catch_specific_exceptions({
            ValueError: lambda e: print(f"Value error: {e}"),
            KeyError: lambda e: print(f"Key error: {e}")
        })
        def my_function(x):
            # Function implementation
            pass
        ```
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                # Find the most specific exception type that matches
                for exc_type, handler in exceptions_map.items():
                    if isinstance(exc, exc_type):
                        return cast(T, handler(exc))
                # If no handler matches, re-raise the exception
                raise

        return wrapper

    return decorator


def format_error_for_user(exc: Exception) -> str:
    """
    Format an exception into a user-friendly error message.

    This function takes an exception and formats it into a message that is
    suitable for displaying to end users. It includes the error message,
    suggestions for resolving the issue, and any other relevant information.

    Args:
        exc: The exception to format.

    Returns:
        A user-friendly error message.
    """
    if isinstance(exc, AnnotationToolkitError):
        # For our custom errors, create a user-friendly message
        message = exc.context.message

        # Add error code if available and not the default UNEXPECTED_ERROR
        if (
            exc.context.error_code
            and exc.context.error_code != ErrorCode.UNEXPECTED_ERROR
        ):
            message += f" (Error code: {exc.context.error_code.name})"

        # Add details if available
        if exc.context.details:
            details_str = ", ".join(f"{k}={v}" for k, v in exc.context.details.items())
            message += f"\nDetails: {details_str}"

        # Add suggestion if available
        if exc.context.suggestion:
            message += f"\nSuggestion: {exc.context.suggestion}"

        return message
    else:
        # For standard exceptions, provide a generic message
        return f"An unexpected error occurred: {str(exc)}"


def log_error_and_continue(exc: Exception, context: Optional[str] = None) -> None:
    """
    Log an error and continue execution.

    This function logs an error with appropriate context information but
    doesn't interrupt program flow. It's useful for non-critical errors
    where the program can continue despite the error.

    Args:
        exc: The exception to log.
        context: Additional context information about where the error occurred.
    """
    context_str = f" while {context}" if context else ""

    if isinstance(exc, AnnotationToolkitError):
        logger.error(f"Error{context_str}: {exc}")
    else:
        logger.error(f"Unexpected error{context_str}: {str(exc)}")
        logger.debug(
            "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        )


def with_error_handling(
    error_code: ErrorCode = ErrorCode.UNEXPECTED_ERROR,
    error_message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    suggestion: Optional[str] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Create a decorator that adds error handling to a function.

    This decorator wraps a function with error handling code that catches
    exceptions, logs them, and re-raises them as AnnotationToolkitError
    instances with additional context information.

    Args:
        error_code: The error code to use if an exception occurs.
        error_message: A custom error message template to use if an exception occurs.
            Can include '{func_name}' which will be replaced with the function name.
        details: Additional details to include in the error.
        suggestion: A suggestion for how to fix the error.

    Returns:
        A decorator function.

    Example:
        ```python
        @with_error_handling(
            error_code=ErrorCode.PROCESSING_ERROR,
            error_message="Error processing data",
            suggestion="Check the input data format"
        )
        def process_data(data):
            # Function implementation
            pass
        ```
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Format the error message if a template was provided
            formatted_error_message = error_message
            if error_message and "{func_name}" in error_message:
                formatted_error_message = error_message.format(func_name=func.__name__)

            try:
                return func(*args, **kwargs)
            except Exception as exc:
                # Don't wrap AnnotationToolkitError instances
                if isinstance(exc, AnnotationToolkitError):
                    raise

                # Create a new ProcessingError with the provided context
                raise ProcessingError(
                    formatted_error_message or f"Error in {func.__name__}: {str(exc)}",
                    error_code,
                    details,
                    suggestion,
                    exc,
                )

        # Preserve the original function's metadata
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__

        return wrapper

    return decorator


def create_error_boundary(
    fallback_value: T, error_handler: Optional[Callable[[Exception], Any]] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Create a decorator that provides an error boundary around a function.

    This decorator catches any exceptions thrown by the decorated function
    and returns a fallback value instead. It can also execute an optional
    error handler function.

    Args:
        fallback_value: The value to return if an exception occurs.
        error_handler: An optional function to call when an exception occurs.
            It receives the exception as its only argument.

    Returns:
        A decorator function.

    Example:
        ```python
        @create_error_boundary(
            fallback_value=[],
            error_handler=lambda e: print(f"Error: {e}")
        )
        def get_data():
            # Function implementation that might raise an exception
            pass
        ```
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                # Log the error
                log_error_and_continue(exc, f"executing {func.__name__}")

                # Call the error handler if provided
                if error_handler:
                    error_handler(exc)

                # Return the fallback value
                return fallback_value

        # Preserve the original function's metadata
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__

        return wrapper

    return decorator
