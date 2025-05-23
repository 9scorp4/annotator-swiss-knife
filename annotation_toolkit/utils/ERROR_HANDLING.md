# Error Handling System

This document provides an overview of the error handling system in the Annotation Toolkit and guidelines for using it effectively.

## Overview

The error handling system consists of:

1. **Custom Exception Classes**: A hierarchy of exception classes for different types of errors
2. **Error Codes**: Enumerated error codes for categorizing errors
3. **Error Context**: Additional information about errors, including suggestions for resolution
4. **Error Handling Utilities**: Functions and decorators for handling errors consistently

## Custom Exception Classes

All custom exceptions inherit from `AnnotationToolkitError`, which provides a consistent interface for error handling. The exception hierarchy is organized by error category:

```
AnnotationToolkitError
├── ConfigurationError
│   ├── MissingConfigurationError
│   └── InvalidConfigurationError
├── ValidationError
│   ├── MissingRequiredFieldError
│   ├── TypeValidationError
│   └── ValueValidationError
├── ProcessingError
│   ├── TransformationError
│   └── ParsingError
├── IOError
│   ├── FileNotFoundError
│   ├── FileReadError
│   └── FileWriteError
└── ServiceError
    ├── ServiceUnavailableError
    └── ServiceTimeoutError
```

## Error Codes

Error codes are defined in the `ErrorCode` enum and are grouped by category:

- **1000-1999**: Configuration errors
- **2000-2999**: Input/validation errors
- **3000-3999**: Processing errors
- **4000-4999**: I/O errors
- **5000-5999**: External service errors
- **9000-9999**: Unexpected/internal errors

## Using the Error Handling System

### Raising Custom Exceptions

```python
from annotation_toolkit.utils import TypeValidationError

def process_data(data):
    if not isinstance(data, dict):
        raise TypeValidationError(
            "data",
            dict,
            type(data),
            suggestion="Ensure you're passing a dictionary to process_data."
        )
    # Process the data...
```

### Using Error Handling Decorators

The `with_error_handling` decorator automatically catches exceptions and wraps them in `AnnotationToolkitError` instances:

```python
from annotation_toolkit.utils import with_error_handling, ErrorCode

@with_error_handling(
    error_code=ErrorCode.PROCESSING_ERROR,
    error_message="Error processing data",
    suggestion="Check the input data format"
)
def process_data(data):
    # Function implementation that might raise exceptions
    pass
```

The `create_error_boundary` decorator catches exceptions and returns a fallback value:

```python
from annotation_toolkit.utils import create_error_boundary

@create_error_boundary(
    fallback_value=[],
    error_handler=lambda e: print(f"Error: {e}")
)
def get_data():
    # Function implementation that might raise exceptions
    pass
```

### Safe Function Execution

The `handle_errors` function executes a function and handles any errors that occur:

```python
from annotation_toolkit.utils import handle_errors, ErrorCode

result = handle_errors(
    process_data,
    data,
    error_code=ErrorCode.PROCESSING_ERROR,
    error_message="Error processing data",
    suggestion="Check the input data format",
    exit_on_error=False,
    default_return={}
)
```

### Functional Error Handling

The `try_except_with_finally` function provides a cleaner way to handle try/except/finally patterns:

```python
from annotation_toolkit.utils import try_except_with_finally

def try_func():
    # Function that might raise an exception
    return process_data(data)

def except_func(exc):
    # Handle the exception
    print(f"Error: {exc}")
    return {}

def finally_func():
    # Clean up resources
    close_resources()

result = try_except_with_finally(try_func, except_func, finally_func)
```

### Handling Specific Exceptions

The `catch_specific_exceptions` decorator catches specific exceptions and handles them with custom handlers:

```python
from annotation_toolkit.utils import catch_specific_exceptions
from annotation_toolkit.utils import ValidationError, ProcessingError

@catch_specific_exceptions({
    ValidationError: lambda e: print(f"Validation error: {e}"),
    ProcessingError: lambda e: print(f"Processing error: {e}")
})
def process_data(data):
    # Function implementation that might raise exceptions
    pass
```

## Best Practices

1. **Use Specific Exception Types**: Choose the most specific exception type for the error you're handling.
2. **Include Suggestions**: Always include a suggestion for how to fix the error when raising exceptions.
3. **Add Context**: Include relevant context information in the error details.
4. **Handle Errors at the Right Level**: Handle errors at the level where you have enough context to provide a meaningful response.
5. **Log Errors**: Ensure errors are properly logged for debugging purposes.
6. **Provide User-Friendly Messages**: Use `format_error_for_user` to create user-friendly error messages.

## Example: Handling File Operations

```python
from annotation_toolkit.utils import (
    with_error_handling,
    ErrorCode,
    FileNotFoundError,
    FileReadError
)

@with_error_handling(
    error_code=ErrorCode.FILE_READ_ERROR,
    suggestion="Check that the file exists and you have permission to read it."
)
def read_config_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError as e:
        raise FileNotFoundError(
            file_path,
            suggestion=f"The configuration file '{file_path}' does not exist. "
                      f"Please create it or specify a different file path."
        )
    except PermissionError as e:
        raise FileReadError(
            file_path,
            details={"error": str(e)},
            suggestion=f"You don't have permission to read '{file_path}'. "
                      f"Check the file permissions."
        )
```
