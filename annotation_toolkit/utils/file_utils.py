"""
File utility functions for the annotation toolkit.

This module provides functions for working with files, including
loading and saving data in various formats.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
import tempfile
import shutil
import chardet

import yaml

from .security import (
    default_path_validator,
    default_file_size_validator,
    default_input_sanitizer,
    generate_file_hash
)

from .errors import (
    ErrorCode,
    FileNotFoundError as ATFileNotFoundError,
    FileReadError,
    FileWriteError,
    IOError,
    ParsingError,
    TypeValidationError,
    ValueValidationError,
    ValidationError,
    safe_execute
)
from .security import FileSizeValidator
from contextlib import contextmanager
from .logger import logger


@contextmanager
def atomic_write(file_path: Union[str, Path], mode: str = 'w',
                 encoding: str = 'utf-8', backup: bool = False):
    """
    Context manager for atomic file writes.

    Writes to a temporary file and atomically replaces the target file
    only if the write succeeds. This prevents partial writes and corruption.

    Args:
        file_path: Path to the target file.
        mode: File mode ('w' for text, 'wb' for binary).
        encoding: Text encoding (ignored for binary mode).
        backup: If True, create a backup of the original file.

    Yields:
        File handle for writing.

    Example:
        with atomic_write('config.json') as f:
            json.dump(data, f)
    """
    file_path = Path(file_path)

    # Ensure directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Create backup if requested and file exists
    if backup and file_path.exists():
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        shutil.copy2(file_path, backup_path)

    # Create temporary file in the same directory (for atomic rename)
    temp_fd, temp_path = tempfile.mkstemp(
        dir=file_path.parent,
        prefix=f'.{file_path.name}.',
        suffix='.tmp'
    )

    try:
        # Open the temporary file
        if 'b' in mode:
            temp_file = os.fdopen(temp_fd, mode)
        else:
            temp_file = os.fdopen(temp_fd, mode, encoding=encoding)

        # Yield the file handle for writing
        yield temp_file

        # Ensure all data is written
        temp_file.flush()
        os.fsync(temp_file.fileno())
        temp_file.close()

        # Atomically replace the target file
        # On Unix, this is atomic. On Windows, we need to remove first.
        if os.name == 'nt' and file_path.exists():
            file_path.unlink()

        Path(temp_path).rename(file_path)

    except Exception:
        # Clean up temp file on error
        try:
            if not temp_file.closed:
                temp_file.close()
        except OSError as cleanup_err:
            logger.debug(f"Failed to close temp file during cleanup: {cleanup_err}")

        try:
            Path(temp_path).unlink()
        except OSError as cleanup_err:
            logger.debug(f"Failed to remove temp file during cleanup: {cleanup_err}")

        # Re-raise the original exception
        raise


def detect_file_encoding(file_path: Union[str, Path],
                         sample_size: int = 10240) -> Tuple[str, float]:
    """
    Detect the encoding of a file.

    Args:
        file_path: Path to the file.
        sample_size: Number of bytes to read for detection (default 10KB).

    Returns:
        Tuple of (encoding_name, confidence_score).

    Raises:
        FileNotFoundError: If the file doesn't exist.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise ATFileNotFoundError(
            str(file_path),
            suggestion="Ensure the file exists before detecting encoding"
        )

    # Read a sample from the file
    with open(file_path, 'rb') as f:
        raw_data = f.read(sample_size)

    # Detect encoding
    result = chardet.detect(raw_data)

    encoding = result.get('encoding', 'utf-8')
    confidence = result.get('confidence', 0.0)

    # Fallback to utf-8 if detection fails or confidence is too low
    if not encoding or confidence < 0.5:
        # Try UTF-8 first
        try:
            raw_data.decode('utf-8')
            encoding = 'utf-8'
            confidence = 1.0
        except UnicodeDecodeError:
            # Try common encodings
            for enc in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    raw_data.decode(enc)
                    encoding = enc
                    confidence = 0.8
                    break
                except UnicodeDecodeError:
                    continue
            else:
                # Last resort: use latin-1 (accepts all bytes)
                encoding = 'latin-1'
                confidence = 0.3

    return encoding, confidence


def read_file_with_encoding_detection(file_path: Union[str, Path]) -> Tuple[str, str]:
    """
    Read a file with automatic encoding detection.

    Args:
        file_path: Path to the file.

    Returns:
        Tuple of (file_content, detected_encoding).

    Raises:
        FileNotFoundError: If the file doesn't exist.
        FileReadError: If the file cannot be read.
    """
    file_path = Path(file_path)
    file_path_str = str(file_path)

    if not file_path.exists():
        raise ATFileNotFoundError(
            file_path_str,
            suggestion="Verify the file path and ensure the file exists."
        )

    # Detect encoding
    encoding, confidence = detect_file_encoding(file_path)

    # Log detected encoding
    from .logger import get_logger
    logger = get_logger()
    logger.debug(f"Detected encoding for {file_path_str}: {encoding} (confidence: {confidence:.2f})")

    # Read file with detected encoding
    try:
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            content = f.read()
        return content, encoding
    except Exception as e:
        raise FileReadError(
            file_path_str,
            details={"error": str(e), "encoding": encoding},
            suggestion=f"Failed to read file with {encoding} encoding",
            cause=e
        )


def ensure_directory_exists(directory_path: Union[str, Path]) -> Path:
    """
    Ensure that a directory exists, creating it if necessary.

    Args:
        directory_path (Union[str, Path]): Path to the directory.

    Returns:
        Path: The path to the directory.
    """
    directory = Path(directory_path)
    os.makedirs(directory, exist_ok=True)
    return directory


def load_json(file_path: Union[str, Path], validate_path: bool = True,
              max_file_size: Optional[int] = None,
              detect_encoding: bool = True) -> Union[Dict, List]:
    """
    Load JSON data from a file with security validation and encoding detection.

    Args:
        file_path (Union[str, Path]): Path to the JSON file.
        validate_path: Whether to validate the path for security.
        max_file_size: Maximum file size in bytes. If None, uses default.
        detect_encoding: Whether to auto-detect file encoding.

    Returns:
        Union[Dict, List]: The loaded JSON data.

    Raises:
        FileNotFoundError: If the file does not exist.
        ParsingError: If the file is not valid JSON.
        ValidationError: If security validation fails.
    """
    # Validate path if requested
    if validate_path:
        file_path = default_path_validator.validate_file_extension(
            file_path, {'.json'}
        )

        # Check file size
        if max_file_size:
            validator = FileSizeValidator(max_file_size)
            validator.validate_file_size(file_path)
        else:
            default_file_size_validator.validate_file_size(file_path)

    file_path_str = str(file_path)

    # Detect encoding if requested
    encoding = 'utf-8'
    if detect_encoding:
        try:
            detected_encoding, confidence = detect_file_encoding(file_path)
            if confidence > 0.7:  # Use detected encoding only if confidence is high
                encoding = detected_encoding
        except Exception:
            # Fall back to UTF-8 if detection fails
            pass

    try:
        with open(file_path, "r", encoding=encoding) as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                # If decoding fails with detected encoding, try UTF-8 as fallback
                if encoding != 'utf-8':
                    try:
                        with open(file_path, "r", encoding="utf-8") as f2:
                            return json.load(f2)
                    except:
                        pass  # Continue with original error

                raise ParsingError(
                    f"Invalid JSON in file: {file_path_str}",
                    details={
                        "file_path": file_path_str,
                        "error_position": f"line {e.lineno}, column {e.colno}",
                        "error_message": e.msg,
                        "encoding": encoding
                    },
                    suggestion="Check the JSON syntax and ensure it's valid. Common issues include missing commas, unbalanced brackets, or invalid escape sequences.",
                    cause=e
                )
    except FileNotFoundError as e:
        raise ATFileNotFoundError(
            file_path_str,
            suggestion="Verify the file path and ensure the file exists.",
            cause=e
        )
    except PermissionError as e:
        raise FileReadError(
            file_path_str,
            details={"error": str(e)},
            suggestion="Check that you have permission to read this file.",
            cause=e
        )
    except Exception as e:
        raise FileReadError(
            file_path_str,
            details={"error": str(e)},
            cause=e
        )


def save_json(data: Union[Dict, List], file_path: Union[str, Path],
              validate_path: bool = True, atomic: bool = True, **kwargs) -> None:
    """
    Save data to a JSON file with security validation and atomic writes.

    Args:
        data (Union[Dict, List]): The data to save.
        file_path (Union[str, Path]): Path to save the file.
        validate_path: Whether to validate the path for security.
        atomic: Whether to use atomic writes (recommended).
        **kwargs: Additional arguments to pass to json.dump.

    Raises:
        TypeValidationError: If the data is not a dictionary or list.
        FileWriteError: If there's an error writing to the file.
        ValidationError: If security validation fails.
    """
    # Validate path if requested
    if validate_path:
        file_path = default_path_validator.validate_file_extension(
            file_path, {'.json'}
        )

    file_path_str = str(file_path)

    # Validate input type
    if not isinstance(data, (dict, list)):
        raise TypeValidationError(
            "data",
            [dict, list],
            type(data),
            suggestion="Ensure you're passing a dictionary or list to save_json."
        )

    # Set default kwargs for consistent output
    kwargs.setdefault("indent", 2)
    kwargs.setdefault("ensure_ascii", False)

    try:
        # Ensure the directory exists
        directory = Path(file_path).parent
        ensure_directory_exists(directory)

        try:
            if atomic:
                with atomic_write(file_path, mode='w', encoding='utf-8') as f:
                    json.dump(data, f, **kwargs)
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, **kwargs)
        except TypeError as e:
            raise TypeValidationError(
                "data",
                "JSON-serializable object",
                type(data),
                details={"error": str(e)},
                suggestion="Ensure all values in your data structure are JSON-serializable (strings, numbers, booleans, lists, dictionaries, or null).",
                cause=e
            )
    except PermissionError as e:
        raise FileWriteError(
            file_path_str,
            details={"error": str(e)},
            suggestion="Check that you have permission to write to this file and directory.",
            cause=e
        )
    except Exception as e:
        raise FileWriteError(
            file_path_str,
            details={"error": str(e)},
            cause=e
        )


def load_yaml(file_path: Union[str, Path], validate_path: bool = True,
              max_file_size: Optional[int] = None) -> Dict:
    """
    Load YAML data from a file with security validation.

    Args:
        file_path (Union[str, Path]): Path to the YAML file.
        validate_path: Whether to validate the path for security.
        max_file_size: Maximum file size in bytes. If None, uses default.

    Returns:
        Dict: The loaded YAML data.

    Raises:
        FileNotFoundError: If the file does not exist.
        ParsingError: If the file is not valid YAML.
        ValidationError: If security validation fails.
    """
    # Validate path if requested
    if validate_path:
        file_path = default_path_validator.validate_file_extension(
            file_path, {'.yaml', '.yml'}
        )

        # Check file size
        if max_file_size:
            validator = FileSizeValidator(max_file_size)
            validator.validate_file_size(file_path)
        else:
            default_file_size_validator.validate_file_size(file_path)

    file_path_str = str(file_path)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError as e:
                # Extract line and column info if available
                line_info = ""
                if hasattr(e, 'problem_mark'):
                    line_info = f" at line {e.problem_mark.line+1}, column {e.problem_mark.column+1}"

                raise ParsingError(
                    f"Invalid YAML in file: {file_path_str}{line_info}",
                    details={
                        "file_path": file_path_str,
                        "error": str(e)
                    },
                    suggestion="Check the YAML syntax and ensure it's valid. Common issues include incorrect indentation, missing colons, or unbalanced quotes.",
                    cause=e
                )
    except FileNotFoundError as e:
        raise ATFileNotFoundError(
            file_path_str,
            suggestion="Verify the file path and ensure the file exists.",
            cause=e
        )
    except PermissionError as e:
        raise FileReadError(
            file_path_str,
            details={"error": str(e)},
            suggestion="Check that you have permission to read this file.",
            cause=e
        )
    except Exception as e:
        raise FileReadError(
            file_path_str,
            details={"error": str(e)},
            cause=e
        )


def save_yaml(data: Dict, file_path: Union[str, Path],
              validate_path: bool = True, atomic: bool = True) -> None:
    """
    Save data to a YAML file with security validation and atomic writes.

    Args:
        data (Dict): The data to save.
        file_path (Union[str, Path]): Path to save the file.
        validate_path: Whether to validate the path for security.
        atomic: Whether to use atomic writes (recommended).

    Raises:
        TypeValidationError: If the data is not a dictionary.
        FileWriteError: If there's an error writing to the file.
        ValidationError: If security validation fails.
    """
    # Validate path if requested
    if validate_path:
        file_path = default_path_validator.validate_file_extension(
            file_path, {'.yaml', '.yml'}
        )

    file_path_str = str(file_path)

    # Validate input type
    if not isinstance(data, dict):
        raise TypeValidationError(
            "data",
            dict,
            type(data),
            suggestion="Ensure you're passing a dictionary to save_yaml."
        )

    try:
        # Ensure the directory exists
        directory = Path(file_path).parent
        ensure_directory_exists(directory)

        try:
            if atomic:
                with atomic_write(file_path, mode='w', encoding='utf-8') as f:
                    yaml.dump(data, f, default_flow_style=False)
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    yaml.dump(data, f, default_flow_style=False)
        except yaml.YAMLError as e:
            raise ParsingError(
                f"Failed to serialize data to YAML: {str(e)}",
                details={"file_path": file_path_str},
                suggestion="Ensure all values in your data structure are YAML-serializable.",
                cause=e
            )
    except PermissionError as e:
        raise FileWriteError(
            file_path_str,
            details={"error": str(e)},
            suggestion="Check that you have permission to write to this file and directory.",
            cause=e
        )
    except Exception as e:
        raise FileWriteError(
            file_path_str,
            details={"error": str(e)},
            cause=e
        )


def get_file_extension(file_path: Union[str, Path]) -> str:
    """
    Get the extension of a file.

    Args:
        file_path (Union[str, Path]): Path to the file.

    Returns:
        str: The file extension without the dot.
    """
    return Path(file_path).suffix.lstrip(".")


def is_json_file(file_path: Union[str, Path]) -> bool:
    """
    Check if a file is a JSON file based on its extension.

    Args:
        file_path (Union[str, Path]): Path to the file.

    Returns:
        bool: True if the file is a JSON file, False otherwise.
    """
    return get_file_extension(file_path).lower() == "json"


def is_yaml_file(file_path: Union[str, Path]) -> bool:
    """
    Check if a file is a YAML file based on its extension.

    Args:
        file_path (Union[str, Path]): Path to the file.

    Returns:
        bool: True if the file is a YAML file, False otherwise.
    """
    ext = get_file_extension(file_path).lower()
    return ext in ("yaml", "yml")


def load_data_file(file_path: Union[str, Path]) -> Any:
    """
    Load data from a file based on its extension.

    Supports JSON and YAML files.

    Args:
        file_path (Union[str, Path]): Path to the file.

    Returns:
        Any: The loaded data.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueValidationError: If the file format is not supported.
        FileReadError: If there's an error reading the file.
        ParsingError: If there's an error parsing the file content.
    """
    file_path = Path(file_path)
    file_path_str = str(file_path)

    if not file_path.exists():
        raise ATFileNotFoundError(
            file_path_str,
            suggestion="Verify the file path and ensure the file exists."
        )

    if is_json_file(file_path):
        return load_json(file_path)
    elif is_yaml_file(file_path):
        return load_yaml(file_path)
    else:
        extension = get_file_extension(file_path)
        raise ValueValidationError(
            "file_extension",
            extension,
            "must be json, yaml, or yml",
            details={"file_path": file_path_str},
            suggestion="Use a supported file format (JSON or YAML) or implement a custom loader for this file type."
        )


def save_data_file(data: Any, file_path: Union[str, Path]) -> None:
    """
    Save data to a file based on its extension.

    Supports JSON and YAML files.

    Args:
        data (Any): The data to save.
        file_path (Union[str, Path]): Path to save the file.

    Raises:
        ValueValidationError: If the file format is not supported.
        TypeValidationError: If the data type is not compatible with the file format.
        FileWriteError: If there's an error writing to the file.
    """
    file_path = Path(file_path)
    file_path_str = str(file_path)

    if is_json_file(file_path):
        save_json(data, file_path)
    elif is_yaml_file(file_path):
        save_yaml(data, file_path)
    else:
        extension = get_file_extension(file_path)
        raise ValueValidationError(
            "file_extension",
            extension,
            "must be json, yaml, or yml",
            details={"file_path": file_path_str},
            suggestion="Use a supported file format (JSON or YAML) or implement a custom saver for this file type."
        )


def list_files(
    directory: Union[str, Path], extension: Optional[str] = None
) -> List[Path]:
    """
    List all files in a directory with an optional filter by extension.

    Args:
        directory (Union[str, Path]): The directory to list files from.
        extension (Optional[str]): Filter files by this extension.
            If None, all files are returned.

    Returns:
        List[Path]: A list of paths to the files.

    Raises:
        FileNotFoundError: If the directory does not exist.
        FileReadError: If there's an error reading the directory.
    """
    directory = Path(directory)
    directory_str = str(directory)

    try:
        if not directory.exists():
            raise ATFileNotFoundError(
                directory_str,
                details={"type": "directory"},
                suggestion="Verify the directory path and ensure it exists."
            )

        try:
            if extension:
                # Ensure extension starts with a dot
                if not extension.startswith("."):
                    extension = f".{extension}"
                return [f for f in directory.glob(f"*{extension}")]
            else:
                return [f for f in directory.glob("*") if f.is_file()]
        except Exception as e:
            raise FileReadError(
                directory_str,
                details={"error": str(e), "type": "directory"},
                suggestion="Check permissions and ensure the path is a valid directory.",
                cause=e
            )
    except PermissionError as e:
        raise FileReadError(
            directory_str,
            details={"error": str(e), "type": "directory"},
            suggestion="Check that you have permission to read this directory.",
            cause=e
        )
