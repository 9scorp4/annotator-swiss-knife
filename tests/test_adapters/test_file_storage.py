"""
Unit tests for the file storage adapters.

This module tests FileStorage, ConversationStorage, and DictionaryStorage
classes for file operations, error handling, and specialized data management.
"""

import json
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

from annotation_toolkit.adapters.file_storage import (
    FileStorage,
    ConversationStorage,
    DictionaryStorage
)
from annotation_toolkit.utils.errors import (
    FileNotFoundError as ATFileNotFoundError,
    FileReadError,
    FileWriteError,
    TypeValidationError,
    ValueValidationError
)


def setUpModule():
    """Set up module-level mocks for path validation."""
    global path_validator_patcher
    # Mock the path validator to bypass security restrictions in tests
    path_validator_patcher = patch('annotation_toolkit.utils.file_utils.default_path_validator')
    mock_validator = path_validator_patcher.start()
    # Configure mock to pass through paths unchanged
    mock_validator.validate_file_extension.side_effect = lambda path, exts: Path(path)
    mock_validator.validate_path.side_effect = lambda path: Path(path)


def tearDownModule():
    """Tear down module-level mocks."""
    global path_validator_patcher
    path_validator_patcher.stop()


class TestFileStorageInit(unittest.TestCase):
    """Test FileStorage initialization."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_file_storage_")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_file_storage_initialization(self):
        """Test FileStorage initializes with base directory."""
        storage = FileStorage(self.test_dir)

        self.assertEqual(storage.base_directory, Path(self.test_dir))
        self.assertTrue(os.path.exists(storage.base_directory))

    def test_file_storage_creates_directory_if_not_exists(self):
        """Test FileStorage creates base directory if it doesn't exist."""
        new_dir = os.path.join(self.test_dir, "new_storage")
        self.assertFalse(os.path.exists(new_dir))

        storage = FileStorage(new_dir)

        self.assertTrue(os.path.exists(new_dir))
        self.assertEqual(storage.base_directory, Path(new_dir))

    def test_file_storage_accepts_path_object(self):
        """Test FileStorage accepts Path object as base directory."""
        path_obj = Path(self.test_dir)
        storage = FileStorage(path_obj)

        self.assertEqual(storage.base_directory, path_obj)


class TestFileStorageGetDirectory(unittest.TestCase):
    """Test FileStorage get_directory method."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_file_storage_")
        self.storage = FileStorage(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_get_directory_without_subdirectory(self):
        """Test get_directory returns base directory when no subdirectory."""
        directory = self.storage.get_directory()

        self.assertEqual(directory, Path(self.test_dir))

    def test_get_directory_with_subdirectory(self):
        """Test get_directory creates and returns subdirectory."""
        subdirectory = "subdir"
        directory = self.storage.get_directory(subdirectory)

        expected_path = Path(self.test_dir) / subdirectory
        self.assertEqual(directory, expected_path)
        self.assertTrue(os.path.exists(directory))

    def test_get_directory_creates_nested_subdirectories(self):
        """Test get_directory creates nested subdirectories."""
        subdirectory = "level1/level2/level3"
        directory = self.storage.get_directory(subdirectory)

        expected_path = Path(self.test_dir) / subdirectory
        self.assertEqual(directory, expected_path)
        self.assertTrue(os.path.exists(directory))


class TestFileStorageSaveData(unittest.TestCase):
    """Test FileStorage save_data method."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_file_storage_")
        self.storage = FileStorage(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_save_data_json(self):
        """Test saving JSON data."""
        data = {"key": "value", "number": 42}
        filename = "test.json"

        file_path = self.storage.save_data(data, filename)

        self.assertTrue(os.path.exists(file_path))
        self.assertEqual(file_path, Path(self.test_dir) / filename)

        # Verify content
        with open(file_path, 'r') as f:
            loaded_data = json.load(f)
        self.assertEqual(loaded_data, data)

    def test_save_data_rejects_unsupported_extension(self):
        """Test that save_data rejects unsupported file extensions."""
        data = "This is test text content"
        filename = "test.txt"

        # Should raise ValueValidationError for unsupported extension
        with self.assertRaises(ValueValidationError):
            self.storage.save_data(data, filename)

    def test_save_data_in_subdirectory(self):
        """Test saving data in subdirectory."""
        data = {"test": "data"}
        filename = "test.json"
        subdirectory = "subdir"

        file_path = self.storage.save_data(data, filename, subdirectory)

        expected_path = Path(self.test_dir) / subdirectory / filename
        self.assertEqual(file_path, expected_path)
        self.assertTrue(os.path.exists(file_path))

    def test_save_data_overwrites_existing_file(self):
        """Test that save_data overwrites existing file."""
        filename = "test.json"
        data1 = {"version": 1}
        data2 = {"version": 2}

        # Save first version
        file_path = self.storage.save_data(data1, filename)

        # Save second version
        file_path = self.storage.save_data(data2, filename)

        # Verify content is updated
        with open(file_path, 'r') as f:
            loaded_data = json.load(f)
        self.assertEqual(loaded_data, data2)


class TestFileStorageLoadData(unittest.TestCase):
    """Test FileStorage load_data method."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_file_storage_")
        self.storage = FileStorage(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_load_data_json(self):
        """Test loading JSON data."""
        data = {"key": "value", "number": 42}
        filename = "test.json"

        # Save data first
        self.storage.save_data(data, filename)

        # Load and verify
        loaded_data = self.storage.load_data(filename)
        self.assertEqual(loaded_data, data)

    def test_load_data_rejects_unsupported_extension(self):
        """Test that load_data rejects unsupported file extensions."""
        filename = "test.txt"

        # Create a text file manually (bypass save_data)
        with open(os.path.join(self.test_dir, filename), 'w') as f:
            f.write("test content")

        # Should raise ValueValidationError for unsupported extension
        with self.assertRaises(ValueValidationError):
            self.storage.load_data(filename)

    def test_load_data_from_subdirectory(self):
        """Test loading data from subdirectory."""
        data = {"test": "data"}
        filename = "test.json"
        subdirectory = "subdir"

        # Save in subdirectory first
        self.storage.save_data(data, filename, subdirectory)

        # Load from subdirectory
        loaded_data = self.storage.load_data(filename, subdirectory)
        self.assertEqual(loaded_data, data)

    def test_load_data_file_not_found_raises_error(self):
        """Test loading non-existent file raises error."""
        with self.assertRaises(ATFileNotFoundError):
            self.storage.load_data("nonexistent.json")


class TestFileStorageListFiles(unittest.TestCase):
    """Test FileStorage list_files method."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_file_storage_")
        self.storage = FileStorage(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_list_files_in_empty_directory(self):
        """Test listing files in empty directory."""
        files = self.storage.list_files()

        self.assertEqual(len(files), 0)

    def test_list_all_files(self):
        """Test listing all files without filter."""
        # Create test files
        self.storage.save_data({"test": 1}, "file1.json")
        self.storage.save_data({"test": 2}, "file2.json")
        # Create a txt file manually (not supported by save_data)
        with open(os.path.join(self.test_dir, "file3.txt"), 'w') as f:
            f.write("text")

        files = self.storage.list_files()

        self.assertEqual(len(files), 3)

    def test_list_files_with_extension_filter(self):
        """Test listing files with extension filter."""
        # Create test files
        self.storage.save_data({"test": 1}, "file1.json")
        self.storage.save_data({"test": 2}, "file2.json")
        # Create a txt file manually (not supported by save_data)
        with open(os.path.join(self.test_dir, "file3.txt"), 'w') as f:
            f.write("text")

        json_files = self.storage.list_files(extension=".json")
        txt_files = self.storage.list_files(extension=".txt")

        self.assertEqual(len(json_files), 2)
        self.assertEqual(len(txt_files), 1)

    def test_list_files_extension_without_dot(self):
        """Test listing files with extension filter without dot prefix."""
        self.storage.save_data({"test": 1}, "file.json")

        files = self.storage.list_files(extension="json")

        self.assertEqual(len(files), 1)

    def test_list_files_in_subdirectory(self):
        """Test listing files in subdirectory."""
        subdirectory = "subdir"
        self.storage.save_data({"test": 1}, "file1.json", subdirectory)
        self.storage.save_data({"test": 2}, "file2.json", subdirectory)

        files = self.storage.list_files(subdirectory=subdirectory)

        self.assertEqual(len(files), 2)

    def test_list_files_excludes_directories(self):
        """Test that list_files excludes directories."""
        # Create files
        self.storage.save_data({"test": 1}, "file.json")

        # Create subdirectory
        os.makedirs(os.path.join(self.test_dir, "subdir"))

        files = self.storage.list_files()

        # Should only include file, not directory
        self.assertEqual(len(files), 1)


class TestFileStorageSaveWithTimestamp(unittest.TestCase):
    """Test FileStorage save_with_timestamp method."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_file_storage_")
        self.storage = FileStorage(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_save_with_timestamp_creates_timestamped_file(self):
        """Test save_with_timestamp creates file with timestamp."""
        data = {"test": "data"}
        prefix = "backup"

        file_path = self.storage.save_with_timestamp(data, prefix)

        # Verify file exists
        self.assertTrue(os.path.exists(file_path))

        # Verify filename format: prefix_YYYYMMDD_HHMMSS.extension
        filename = file_path.name
        self.assertTrue(filename.startswith(prefix))
        self.assertTrue(filename.endswith(".json"))

        # Verify timestamp format (YYYYMMDD_HHMMSS)
        import re
        pattern = rf"{prefix}_\d{{8}}_\d{{6}}\.json"
        self.assertTrue(re.match(pattern, filename))

    def test_save_with_timestamp_custom_extension(self):
        """Test save_with_timestamp with custom extension (yaml)."""
        data = {"test": "data"}
        prefix = "log"
        extension = "yaml"

        file_path = self.storage.save_with_timestamp(data, prefix, extension)

        self.assertTrue(file_path.name.endswith(".yaml"))

    def test_save_with_timestamp_in_subdirectory(self):
        """Test save_with_timestamp in subdirectory."""
        data = {"test": "data"}
        prefix = "backup"
        subdirectory = "backups"

        file_path = self.storage.save_with_timestamp(
            data, prefix, subdirectory=subdirectory
        )

        expected_parent = Path(self.test_dir) / subdirectory
        self.assertEqual(file_path.parent, expected_parent)


class TestFileStorageFileExists(unittest.TestCase):
    """Test FileStorage file_exists method."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_file_storage_")
        self.storage = FileStorage(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_file_exists_returns_true_for_existing_file(self):
        """Test file_exists returns True for existing file."""
        filename = "test.json"
        self.storage.save_data({"test": "data"}, filename)

        self.assertTrue(self.storage.file_exists(filename))

    def test_file_exists_returns_false_for_nonexistent_file(self):
        """Test file_exists returns False for non-existent file."""
        self.assertFalse(self.storage.file_exists("nonexistent.json"))

    def test_file_exists_in_subdirectory(self):
        """Test file_exists checks subdirectory."""
        filename = "test.json"
        subdirectory = "subdir"
        self.storage.save_data({"test": "data"}, filename, subdirectory)

        self.assertTrue(self.storage.file_exists(filename, subdirectory))
        self.assertFalse(self.storage.file_exists(filename))  # Not in base dir


class TestFileStorageDeleteFile(unittest.TestCase):
    """Test FileStorage delete_file method."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_file_storage_")
        self.storage = FileStorage(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_delete_file_removes_existing_file(self):
        """Test delete_file removes existing file."""
        filename = "test.json"
        self.storage.save_data({"test": "data"}, filename)

        self.assertTrue(self.storage.file_exists(filename))
        self.storage.delete_file(filename)
        self.assertFalse(self.storage.file_exists(filename))

    def test_delete_file_from_subdirectory(self):
        """Test delete_file removes file from subdirectory."""
        filename = "test.json"
        subdirectory = "subdir"
        self.storage.save_data({"test": "data"}, filename, subdirectory)

        self.storage.delete_file(filename, subdirectory)
        self.assertFalse(self.storage.file_exists(filename, subdirectory))

    def test_delete_nonexistent_file_raises_error(self):
        """Test deleting non-existent file raises error."""
        with self.assertRaises(ATFileNotFoundError):
            self.storage.delete_file("nonexistent.json")


class TestConversationStorage(unittest.TestCase):
    """Test ConversationStorage class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_conversation_storage_")
        self.storage = ConversationStorage(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_conversation_storage_initialization(self):
        """Test ConversationStorage initializes with conversations directory."""
        self.assertEqual(self.storage.base_directory, Path(self.test_dir))
        self.assertEqual(self.storage.conversations_dir, "conversations")

        # Verify conversations directory is created
        conversations_path = Path(self.test_dir) / "conversations"
        self.assertTrue(os.path.exists(conversations_path))

    def test_save_conversation_with_filename(self):
        """Test saving conversation with specified filename."""
        conversation = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        filename = "test_conversation.json"

        file_path = self.storage.save_conversation(conversation, filename)

        self.assertTrue(os.path.exists(file_path))
        self.assertEqual(file_path.name, filename)

        # Verify content structure
        with open(file_path, 'r') as f:
            data = json.load(f)
        self.assertIn("chat_history", data)
        self.assertEqual(data["chat_history"], conversation)

    def test_save_conversation_with_auto_filename(self):
        """Test saving conversation with auto-generated timestamped filename."""
        conversation = [
            {"role": "user", "content": "Hello"}
        ]

        file_path = self.storage.save_conversation(conversation)

        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(file_path.name.startswith("conversation_"))
        self.assertTrue(file_path.name.endswith(".json"))

    def test_load_conversation_with_chat_history_format(self):
        """Test loading conversation in chat_history format."""
        conversation = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"}
        ]
        filename = "test.json"

        self.storage.save_conversation(conversation, filename)
        loaded_conversation = self.storage.load_conversation(filename)

        self.assertEqual(loaded_conversation, conversation)

    def test_load_conversation_with_list_format(self):
        """Test loading conversation in direct list format."""
        conversation = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"}
        ]
        filename = "test.json"

        # Save directly as list (not wrapped in chat_history)
        self.storage.save_data(conversation, filename, "conversations")
        loaded_conversation = self.storage.load_conversation(filename)

        self.assertEqual(loaded_conversation, conversation)

    def test_load_conversation_validates_message_structure(self):
        """Test load_conversation validates message structure."""
        # Missing 'content' field
        invalid_conversation = [
            {"role": "user"}
        ]
        filename = "invalid.json"

        self.storage.save_data(invalid_conversation, filename, "conversations")

        with self.assertRaises(ValueValidationError):
            self.storage.load_conversation(filename)

    def test_load_conversation_requires_role_field(self):
        """Test load_conversation requires role field."""
        # Missing 'role' field
        invalid_conversation = [
            {"content": "Hello"}
        ]
        filename = "invalid.json"

        self.storage.save_data(invalid_conversation, filename, "conversations")

        with self.assertRaises(ValueValidationError):
            self.storage.load_conversation(filename)

    def test_load_conversation_invalid_format_raises_error(self):
        """Test load_conversation with invalid format raises error."""
        # Save invalid format (not a list or dict with chat_history)
        invalid_data = "not a conversation"
        filename = "invalid.json"

        # Manually create invalid JSON file (bypass save_data validation)
        conversations_dir = self.storage.get_directory("conversations")
        with open(os.path.join(conversations_dir, filename), 'w') as f:
            json.dump(invalid_data, f)

        with self.assertRaises(ValueValidationError):
            self.storage.load_conversation(filename)

    def test_list_conversations(self):
        """Test listing all conversation files."""
        # Create multiple conversations
        conv1 = [{"role": "user", "content": "Hello"}]
        conv2 = [{"role": "user", "content": "Hi"}]

        self.storage.save_conversation(conv1, "conv1.json")
        self.storage.save_conversation(conv2, "conv2.json")

        conversations = self.storage.list_conversations()

        self.assertEqual(len(conversations), 2)


class TestDictionaryStorage(unittest.TestCase):
    """Test DictionaryStorage class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_dictionary_storage_")
        self.storage = DictionaryStorage(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_dictionary_storage_initialization(self):
        """Test DictionaryStorage initializes with dictionaries directory."""
        self.assertEqual(self.storage.base_directory, Path(self.test_dir))
        self.assertEqual(self.storage.dictionaries_dir, "dictionaries")

        # Verify dictionaries directory is created
        dictionaries_path = Path(self.test_dir) / "dictionaries"
        self.assertTrue(os.path.exists(dictionaries_path))

    def test_save_dictionary_with_filename(self):
        """Test saving dictionary with specified filename."""
        dictionary = {"key1": "value1", "key2": "value2"}
        filename = "test_dict.json"

        file_path = self.storage.save_dictionary(dictionary, filename)

        self.assertTrue(os.path.exists(file_path))
        self.assertEqual(file_path.name, filename)

        # Verify content
        with open(file_path, 'r') as f:
            data = json.load(f)
        self.assertEqual(data, dictionary)

    def test_save_dictionary_with_auto_filename(self):
        """Test saving dictionary with auto-generated timestamped filename."""
        dictionary = {"key": "value"}

        file_path = self.storage.save_dictionary(dictionary)

        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(file_path.name.startswith("dictionary_"))
        self.assertTrue(file_path.name.endswith(".json"))

    def test_load_dictionary(self):
        """Test loading dictionary."""
        dictionary = {"key1": "value1", "key2": "value2"}
        filename = "test.json"

        self.storage.save_dictionary(dictionary, filename)
        loaded_dictionary = self.storage.load_dictionary(filename)

        self.assertEqual(loaded_dictionary, dictionary)

    def test_load_dictionary_validates_type(self):
        """Test load_dictionary validates data is a dictionary."""
        # Save non-dictionary data
        invalid_data = ["not", "a", "dictionary"]
        filename = "invalid.json"

        self.storage.save_data(invalid_data, filename, "dictionaries")

        with self.assertRaises(TypeValidationError):
            self.storage.load_dictionary(filename)

    def test_load_dictionary_validates_string_values(self):
        """Test load_dictionary validates all values are strings."""
        # Dictionary with non-string value
        invalid_dictionary = {"key1": "value1", "key2": 123}
        filename = "invalid.json"

        self.storage.save_data(invalid_dictionary, filename, "dictionaries")

        with self.assertRaises(TypeValidationError):
            self.storage.load_dictionary(filename)

    def test_list_dictionaries(self):
        """Test listing all dictionary files."""
        # Create multiple dictionaries
        dict1 = {"key1": "value1"}
        dict2 = {"key2": "value2"}

        self.storage.save_dictionary(dict1, "dict1.json")
        self.storage.save_dictionary(dict2, "dict2.json")

        dictionaries = self.storage.list_dictionaries()

        self.assertEqual(len(dictionaries), 2)


class TestFileStorageIntegration(unittest.TestCase):
    """Integration tests for file storage."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_file_storage_integration_")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_save_load_delete_workflow(self):
        """Test complete save-load-delete workflow."""
        storage = FileStorage(self.test_dir)
        data = {"test": "data", "number": 42}
        filename = "workflow_test.json"

        # Save
        file_path = storage.save_data(data, filename)
        self.assertTrue(storage.file_exists(filename))

        # Load
        loaded_data = storage.load_data(filename)
        self.assertEqual(loaded_data, data)

        # Delete
        storage.delete_file(filename)
        self.assertFalse(storage.file_exists(filename))

    def test_conversation_storage_workflow(self):
        """Test complete conversation storage workflow."""
        storage = ConversationStorage(self.test_dir)
        conversation = [
            {"role": "user", "content": "What is Python?"},
            {"role": "assistant", "content": "Python is a programming language."}
        ]

        # Save with auto filename
        file_path = storage.save_conversation(conversation)

        # List conversations
        conversations = storage.list_conversations()
        self.assertEqual(len(conversations), 1)

        # Load conversation
        loaded_conversation = storage.load_conversation(file_path.name)
        self.assertEqual(loaded_conversation, conversation)

    def test_dictionary_storage_workflow(self):
        """Test complete dictionary storage workflow."""
        storage = DictionaryStorage(self.test_dir)
        dictionary = {
            "hello": "world",
            "foo": "bar",
            "test": "data"
        }

        # Save with auto filename
        file_path = storage.save_dictionary(dictionary)

        # List dictionaries
        dictionaries = storage.list_dictionaries()
        self.assertEqual(len(dictionaries), 1)

        # Load dictionary
        loaded_dictionary = storage.load_dictionary(file_path.name)
        self.assertEqual(loaded_dictionary, dictionary)

    def test_multiple_storage_instances_share_data(self):
        """Test multiple storage instances can access same data."""
        storage1 = FileStorage(self.test_dir)
        storage2 = FileStorage(self.test_dir)

        data = {"shared": "data"}
        filename = "shared.json"

        # Save with first instance
        storage1.save_data(data, filename)

        # Load with second instance
        loaded_data = storage2.load_data(filename)
        self.assertEqual(loaded_data, data)


if __name__ == "__main__":
    unittest.main()
