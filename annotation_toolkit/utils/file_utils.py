"""
File utility functions for the annotation toolkit.

This module provides functions for working with files, including
loading and saving data in various formats.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from .errors import (
    ErrorCode,
    FileNotFoundError as ATFileNotFoundError,
    FileReadError,
    FileWriteError,
    IOError,
    ParsingError,
    TypeValidationError,
    ValueValidationError,
    safe_execute
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


def load_json(file_path: Union[str, Path]) -> Union[Dict, List]:
    """
    Load JSON data from a file.

    Args:
        file_path (Union[str, Path]): Path to the JSON file.

    Returns:
        Union[Dict, List]: The loaded JSON data.

    Raises:
        FileNotFoundError: If the file does not exist.
        ParsingError: If the file is not valid JSON.
    """
    file_path_str = str(file_path)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                raise ParsingError(
                    f"Invalid JSON in file: {file_path_str}",
                    details={
                        "file_path": file_path_str,
                        "error_position": f"line {e.lineno}, column {e.colno}",
                        "error_message": e.msg
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


def save_json(data: Union[Dict, List], file_path: Union[str, Path], **kwargs) -> None:
    """
    Save data to a JSON file.

    Args:
        data (Union[Dict, List]): The data to save.
        file_path (Union[str, Path]): Path to save the file.
        **kwargs: Additional arguments to pass to json.dump.

    Raises:
        TypeValidationError: If the data is not a dictionary or list.
        FileWriteError: If there's an error writing to the file.
    """
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


def load_yaml(file_path: Union[str, Path]) -> Dict:
    """
    Load YAML data from a file.

    Args:
        file_path (Union[str, Path]): Path to the YAML file.

    Returns:
        Dict: The loaded YAML data.

    Raises:
        FileNotFoundError: If the file does not exist.
        ParsingError: If the file is not valid YAML.
    """
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


def save_yaml(data: Dict, file_path: Union[str, Path]) -> None:
    """
    Save data to a YAML file.

    Args:
        data (Dict): The data to save.
        file_path (Union[str, Path]): Path to save the file.

    Raises:
        TypeValidationError: If the data is not a dictionary.
        FileWriteError: If there's an error writing to the file.
    """
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
