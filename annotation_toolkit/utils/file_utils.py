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
        json.JSONDecodeError: If the file is not valid JSON.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: Union[Dict, List], file_path: Union[str, Path], **kwargs) -> None:
    """
    Save data to a JSON file.

    Args:
        data (Union[Dict, List]): The data to save.
        file_path (Union[str, Path]): Path to save the file.
        **kwargs: Additional arguments to pass to json.dump.

    Raises:
        TypeError: If the data is not JSON-serializable.
    """
    # Set default kwargs for consistent output
    kwargs.setdefault("indent", 2)
    kwargs.setdefault("ensure_ascii", False)

    # Ensure the directory exists
    directory = Path(file_path).parent
    ensure_directory_exists(directory)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, **kwargs)


def load_yaml(file_path: Union[str, Path]) -> Dict:
    """
    Load YAML data from a file.

    Args:
        file_path (Union[str, Path]): Path to the YAML file.

    Returns:
        Dict: The loaded YAML data.

    Raises:
        FileNotFoundError: If the file does not exist.
        yaml.YAMLError: If the file is not valid YAML.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(data: Dict, file_path: Union[str, Path]) -> None:
    """
    Save data to a YAML file.

    Args:
        data (Dict): The data to save.
        file_path (Union[str, Path]): Path to save the file.

    Raises:
        yaml.YAMLError: If the data is not YAML-serializable.
    """
    # Ensure the directory exists
    directory = Path(file_path).parent
    ensure_directory_exists(directory)

    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False)


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
        ValueError: If the file format is not supported.
        FileNotFoundError: If the file does not exist.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if is_json_file(file_path):
        return load_json(file_path)
    elif is_yaml_file(file_path):
        return load_yaml(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")


def save_data_file(data: Any, file_path: Union[str, Path]) -> None:
    """
    Save data to a file based on its extension.

    Supports JSON and YAML files.

    Args:
        data (Any): The data to save.
        file_path (Union[str, Path]): Path to save the file.

    Raises:
        ValueError: If the file format is not supported.
    """
    file_path = Path(file_path)

    if is_json_file(file_path):
        save_json(data, file_path)
    elif is_yaml_file(file_path):
        save_yaml(data, file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")


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
    """
    directory = Path(directory)

    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    if extension:
        # Ensure extension starts with a dot
        if not extension.startswith("."):
            extension = f".{extension}"
        return [f for f in directory.glob(f"*{extension}")]
    else:
        return [f for f in directory.glob("*") if f.is_file()]
