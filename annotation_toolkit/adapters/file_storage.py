"""
File storage adapter for the annotation toolkit.

This module provides abstractions for storing and retrieving files.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..utils.file_utils import ensure_directory_exists, load_data_file, save_data_file
from ..utils.errors import (
    ErrorCode,
    FileNotFoundError as ATFileNotFoundError,
    FileReadError,
    FileWriteError,
    TypeValidationError,
    ValueValidationError
)
from ..utils.error_handler import with_error_handling


class FileStorage:
    """
    File storage adapter for saving and loading data files.
    """

    def __init__(self, base_directory: Union[str, Path]):
        """
        Initialize the file storage adapter.

        Args:
            base_directory (Union[str, Path]): The base directory for storing files.
        """
        self.base_directory = ensure_directory_exists(base_directory)

    def get_directory(self, subdirectory: Optional[str] = None) -> Path:
        """
        Get a directory path, creating it if it doesn't exist.

        Args:
            subdirectory (Optional[str]): A subdirectory under the base directory.
                If None, the base directory is returned.

        Returns:
            Path: The directory path.
        """
        if subdirectory:
            directory = self.base_directory / subdirectory
            return ensure_directory_exists(directory)
        else:
            return self.base_directory

    @with_error_handling(
        error_code=ErrorCode.FILE_WRITE_ERROR,
        error_message="Error saving data to file",
        suggestion="Check that the file format is supported and you have permission to write to the specified location."
    )
    def save_data(
        self, data: Any, filename: str, subdirectory: Optional[str] = None
    ) -> Path:
        """
        Save data to a file.

        Args:
            data (Any): The data to save.
            filename (str): The name of the file.
            subdirectory (Optional[str]): A subdirectory under the base directory.
                If None, the file is saved in the base directory.

        Returns:
            Path: The path to the saved file.

        Raises:
            ValueValidationError: If the file format is not supported.
            FileWriteError: If there's an error writing to the file.
        """
        directory = self.get_directory(subdirectory)
        file_path = directory / filename

        save_data_file(data, file_path)

        return file_path

    @with_error_handling(
        error_code=ErrorCode.FILE_READ_ERROR,
        error_message="Error loading data from file",
        suggestion="Check that the file exists, is in a supported format, and you have permission to read it."
    )
    def load_data(self, filename: str, subdirectory: Optional[str] = None) -> Any:
        """
        Load data from a file.

        Args:
            filename (str): The name of the file.
            subdirectory (Optional[str]): A subdirectory under the base directory.
                If None, the file is loaded from the base directory.

        Returns:
            Any: The loaded data.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueValidationError: If the file format is not supported.
            FileReadError: If there's an error reading the file.
        """
        directory = self.get_directory(subdirectory)
        file_path = directory / filename

        return load_data_file(file_path)

    @with_error_handling(
        error_code=ErrorCode.FILE_READ_ERROR,
        error_message="Error listing files",
        suggestion="Check that the directory exists and you have permission to read it."
    )
    def list_files(
        self, extension: Optional[str] = None, subdirectory: Optional[str] = None
    ) -> List[Path]:
        """
        List files in a directory.

        Args:
            extension (Optional[str]): Filter files by this extension.
                If None, all files are returned.
            subdirectory (Optional[str]): A subdirectory under the base directory.
                If None, files in the base directory are listed.

        Returns:
            List[Path]: A list of file paths.

        Raises:
            FileNotFoundError: If the directory does not exist.
            FileReadError: If there's an error reading the directory.
        """
        directory = self.get_directory(subdirectory)

        if extension:
            # Ensure extension starts with a dot
            if not extension.startswith("."):
                extension = f".{extension}"
            return [f for f in directory.glob(f"*{extension}")]
        else:
            return [f for f in directory.glob("*") if f.is_file()]

    def save_with_timestamp(
        self,
        data: Any,
        prefix: str,
        extension: str = "json",
        subdirectory: Optional[str] = None,
    ) -> Path:
        """
        Save data to a file with a timestamp in the filename.

        Args:
            data (Any): The data to save.
            prefix (str): A prefix for the filename.
            extension (str): The file extension (without the dot).
            subdirectory (Optional[str]): A subdirectory under the base directory.
                If None, the file is saved in the base directory.

        Returns:
            Path: The path to the saved file.

        Raises:
            ValueError: If the file format is not supported.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.{extension}"

        return self.save_data(data, filename, subdirectory)

    def file_exists(self, filename: str, subdirectory: Optional[str] = None) -> bool:
        """
        Check if a file exists.

        Args:
            filename (str): The name of the file.
            subdirectory (Optional[str]): A subdirectory under the base directory.
                If None, the file is checked in the base directory.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        directory = self.get_directory(subdirectory)
        file_path = directory / filename

        return file_path.exists()

    @with_error_handling(
        error_code=ErrorCode.FILE_WRITE_ERROR,
        error_message="Error deleting file",
        suggestion="Check that the file exists and you have permission to delete it."
    )
    def delete_file(self, filename: str, subdirectory: Optional[str] = None) -> None:
        """
        Delete a file.

        Args:
            filename (str): The name of the file.
            subdirectory (Optional[str]): A subdirectory under the base directory.
                If None, the file is deleted from the base directory.

        Raises:
            FileNotFoundError: If the file does not exist.
            FileWriteError: If there's an error deleting the file.
        """
        directory = self.get_directory(subdirectory)
        file_path = directory / filename
        file_path_str = str(file_path)

        if not file_path.exists():
            raise ATFileNotFoundError(
                file_path_str,
                suggestion=f"The file '{filename}' does not exist in the specified directory."
            )

        try:
            file_path.unlink()
        except PermissionError as e:
            raise FileWriteError(
                file_path_str,
                details={"error": str(e)},
                suggestion="Check that you have permission to delete this file.",
                cause=e
            )
        except Exception as e:
            raise FileWriteError(
                file_path_str,
                details={"error": str(e)},
                suggestion="An unexpected error occurred while deleting the file.",
                cause=e
            )


class ConversationStorage(FileStorage):
    """
    Specialized file storage for conversation data.
    """

    def __init__(self, base_directory: Union[str, Path]):
        """
        Initialize the conversation storage.

        Args:
            base_directory (Union[str, Path]): The base directory for storing files.
        """
        super().__init__(base_directory)
        self.conversations_dir = "conversations"
        ensure_directory_exists(self.base_directory / self.conversations_dir)

    def save_conversation(
        self, conversation: List[Dict[str, str]], filename: Optional[str] = None
    ) -> Path:
        """
        Save a conversation to a file.

        Args:
            conversation (List[Dict[str, str]]): The conversation to save.
            filename (Optional[str]): The name of the file.
                If None, a timestamped filename is generated.

        Returns:
            Path: The path to the saved file.

        Raises:
            ValueError: If the file format is not supported.
        """
        data = {"chat_history": conversation}

        if filename:
            return self.save_data(data, filename, self.conversations_dir)
        else:
            return self.save_with_timestamp(
                data, "conversation", "json", self.conversations_dir
            )

    @with_error_handling(
        error_code=ErrorCode.PARSING_ERROR,
        error_message="Error loading conversation",
        suggestion="Check that the file contains a valid conversation format."
    )
    def load_conversation(self, filename: str) -> List[Dict[str, str]]:
        """
        Load a conversation from a file.

        Args:
            filename (str): The name of the file.

        Returns:
            List[Dict[str, str]]: The loaded conversation.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueValidationError: If the file format is not supported or the data is invalid.
            FileReadError: If there's an error reading the file.
        """
        data = self.load_data(filename, self.conversations_dir)

        if isinstance(data, dict) and "chat_history" in data:
            return data["chat_history"]
        elif isinstance(data, list):
            # Check if the data is a valid conversation
            for i, msg in enumerate(data):
                if not isinstance(msg, dict):
                    raise TypeValidationError(
                        f"message[{i}]",
                        dict,
                        type(msg),
                        suggestion="Each message in a conversation must be a dictionary."
                    )
                if "content" not in msg:
                    raise ValueValidationError(
                        f"message[{i}]",
                        msg,
                        "must contain 'content' field",
                        suggestion="Each message must have a 'content' field."
                    )
                if "role" not in msg:
                    raise ValueValidationError(
                        f"message[{i}]",
                        msg,
                        "must contain 'role' field",
                        suggestion="Each message must have a 'role' field."
                    )
            return data
        else:
            raise ValueValidationError(
                "conversation",
                data,
                "must be a list of messages or a dictionary with a 'chat_history' field",
                suggestion="Ensure the file contains a valid conversation format."
            )

    def list_conversations(self) -> List[Path]:
        """
        List all conversation files.

        Returns:
            List[Path]: A list of conversation file paths.
        """
        return self.list_files("json", self.conversations_dir)


class DictionaryStorage(FileStorage):
    """
    Specialized file storage for dictionary data.
    """

    def __init__(self, base_directory: Union[str, Path]):
        """
        Initialize the dictionary storage.

        Args:
            base_directory (Union[str, Path]): The base directory for storing files.
        """
        super().__init__(base_directory)
        self.dictionaries_dir = "dictionaries"
        ensure_directory_exists(self.base_directory / self.dictionaries_dir)

    def save_dictionary(
        self, dictionary: Dict[str, str], filename: Optional[str] = None
    ) -> Path:
        """
        Save a dictionary to a file.

        Args:
            dictionary (Dict[str, str]): The dictionary to save.
            filename (Optional[str]): The name of the file.
                If None, a timestamped filename is generated.

        Returns:
            Path: The path to the saved file.

        Raises:
            ValueError: If the file format is not supported.
        """
        if filename:
            return self.save_data(dictionary, filename, self.dictionaries_dir)
        else:
            return self.save_with_timestamp(
                dictionary, "dictionary", "json", self.dictionaries_dir
            )

    @with_error_handling(
        error_code=ErrorCode.PARSING_ERROR,
        error_message="Error loading dictionary",
        suggestion="Check that the file contains a valid dictionary format."
    )
    def load_dictionary(self, filename: str) -> Dict[str, str]:
        """
        Load a dictionary from a file.

        Args:
            filename (str): The name of the file.

        Returns:
            Dict[str, str]: The loaded dictionary.

        Raises:
            FileNotFoundError: If the file does not exist.
            TypeValidationError: If the data is not a dictionary.
            ValueValidationError: If the dictionary values are not strings.
            FileReadError: If there's an error reading the file.
        """
        data = self.load_data(filename, self.dictionaries_dir)

        if not isinstance(data, dict):
            raise TypeValidationError(
                "dictionary",
                dict,
                type(data),
                suggestion="The file must contain a valid JSON dictionary."
            )

        # Ensure all values are strings
        for key, value in data.items():
            if not isinstance(value, str):
                raise TypeValidationError(
                    f"dictionary['{key}']",
                    str,
                    type(value),
                    suggestion="All dictionary values must be strings."
                )

        return data

    def list_dictionaries(self) -> List[Path]:
        """
        List all dictionary files.

        Returns:
            List[Path]: A list of dictionary file paths.
        """
        return self.list_files("json", self.dictionaries_dir)
