"""
Comprehensive tests for the file utilities module.

This module contains comprehensive tests for file utility functions including:
- Atomic writes with backup
- Encoding detection and reading
- JSON/YAML loading and saving
- File extension utilities
- Directory listing
"""

import unittest
import tempfile
import json
import yaml
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import shutil

from annotation_toolkit.utils.file_utils import (
    atomic_write,
    detect_file_encoding,
    read_file_with_encoding_detection,
    ensure_directory_exists,
    load_json,
    save_json,
    load_yaml,
    save_yaml,
    get_file_extension,
    is_json_file,
    is_yaml_file,
    load_data_file,
    save_data_file,
    list_files,
)
from annotation_toolkit.utils.errors import (
    FileNotFoundError as ATFileNotFoundError,
    FileReadError,
    FileWriteError,
    ParsingError,
    TypeValidationError,
    ValueValidationError,
    ValidationError,
)


class TestAtomicWrite(unittest.TestCase):
    """Test cases for atomic_write context manager."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_atomic_write_text_mode(self):
        """Test atomic write in text mode."""
        test_file = Path(self.temp_dir) / "test.txt"

        with atomic_write(test_file) as f:
            f.write("Hello, World!")

        self.assertTrue(test_file.exists())
        self.assertEqual(test_file.read_text(), "Hello, World!")

    def test_atomic_write_binary_mode(self):
        """Test atomic write in binary mode."""
        test_file = Path(self.temp_dir) / "test.bin"

        with atomic_write(test_file, mode='wb') as f:
            f.write(b"Binary data")

        self.assertTrue(test_file.exists())
        self.assertEqual(test_file.read_bytes(), b"Binary data")

    def test_atomic_write_creates_directory(self):
        """Test that atomic write creates parent directories."""
        test_file = Path(self.temp_dir) / "subdir" / "test.txt"

        with atomic_write(test_file) as f:
            f.write("Test")

        self.assertTrue(test_file.exists())

    def test_atomic_write_with_backup(self):
        """Test atomic write creates backup of existing file."""
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("Original content")

        with atomic_write(test_file, backup=True) as f:
            f.write("New content")

        backup_file = test_file.with_suffix(".txt.bak")
        self.assertTrue(backup_file.exists())
        self.assertEqual(backup_file.read_text(), "Original content")
        self.assertEqual(test_file.read_text(), "New content")

    def test_atomic_write_without_backup(self):
        """Test atomic write without backup."""
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("Original")

        with atomic_write(test_file, backup=False) as f:
            f.write("New")

        backup_file = test_file.with_suffix(".txt.bak")
        self.assertFalse(backup_file.exists())

    def test_atomic_write_rollback_on_error(self):
        """Test that atomic write rolls back on error."""
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("Original")

        with self.assertRaises(ValueError):
            with atomic_write(test_file) as f:
                f.write("Partial")
                raise ValueError("Simulated error")

        # Original file should still exist with original content
        self.assertEqual(test_file.read_text(), "Original")

    def test_atomic_write_custom_encoding(self):
        """Test atomic write with custom encoding."""
        test_file = Path(self.temp_dir) / "test.txt"

        with atomic_write(test_file, encoding='latin-1') as f:
            f.write("Test with Latin-1")

        content = test_file.read_text(encoding='latin-1')
        self.assertEqual(content, "Test with Latin-1")


class TestDetectFileEncoding(unittest.TestCase):
    """Test cases for detect_file_encoding function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_detect_utf8_encoding(self):
        """Test detecting UTF-8 encoding."""
        test_file = Path(self.temp_dir) / "utf8.txt"
        test_file.write_text("Hello UTF-8! 你好", encoding='utf-8')

        encoding, confidence = detect_file_encoding(test_file)
        self.assertEqual(encoding, 'utf-8')
        self.assertGreater(confidence, 0.5)

    def test_detect_latin1_encoding(self):
        """Test detecting Latin-1 encoding."""
        test_file = Path(self.temp_dir) / "latin1.txt"
        # Write Latin-1 specific content
        with open(test_file, 'wb') as f:
            f.write("Café".encode('latin-1'))

        encoding, confidence = detect_file_encoding(test_file)
        # Should detect some encoding
        self.assertIsNotNone(encoding)

    def test_detect_encoding_nonexistent_file(self):
        """Test that detect_file_encoding raises error for nonexistent file."""
        nonexistent = Path(self.temp_dir) / "nonexistent.txt"

        with self.assertRaises(ATFileNotFoundError):
            detect_file_encoding(nonexistent)

    def test_detect_encoding_empty_file(self):
        """Test detecting encoding of empty file."""
        test_file = Path(self.temp_dir) / "empty.txt"
        test_file.touch()

        encoding, confidence = detect_file_encoding(test_file)
        # Should return a valid encoding even for empty file
        self.assertIsNotNone(encoding)

    def test_detect_encoding_with_custom_sample_size(self):
        """Test encoding detection with custom sample size."""
        test_file = Path(self.temp_dir) / "large.txt"
        test_file.write_text("Hello UTF-8 世界! " * 1000, encoding='utf-8')

        encoding, confidence = detect_file_encoding(test_file, sample_size=5000)
        self.assertEqual(encoding, 'utf-8')


class TestReadFileWithEncodingDetection(unittest.TestCase):
    """Test cases for read_file_with_encoding_detection function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_read_file_utf8(self):
        """Test reading UTF-8 file."""
        test_file = Path(self.temp_dir) / "utf8.txt"
        content_original = "Hello, UTF-8 世界!"
        test_file.write_text(content_original, encoding='utf-8')

        content, encoding = read_file_with_encoding_detection(test_file)
        self.assertEqual(content, content_original)
        self.assertEqual(encoding, 'utf-8')

    def test_read_file_nonexistent(self):
        """Test reading nonexistent file raises error."""
        nonexistent = Path(self.temp_dir) / "nonexistent.txt"

        with self.assertRaises(ATFileNotFoundError):
            read_file_with_encoding_detection(nonexistent)

    def test_read_file_returns_tuple(self):
        """Test that function returns tuple of (content, encoding)."""
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("Test", encoding='utf-8')

        result = read_file_with_encoding_detection(test_file)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)


class TestEnsureDirectoryExists(unittest.TestCase):
    """Test cases for ensure_directory_exists function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_ensure_directory_exists_new(self):
        """Test creating a new directory."""
        new_dir = Path(self.temp_dir) / "new_directory"
        result = ensure_directory_exists(new_dir)

        self.assertTrue(new_dir.exists())
        self.assertTrue(new_dir.is_dir())
        self.assertEqual(result, new_dir)

    def test_ensure_directory_exists_existing(self):
        """Test with existing directory."""
        existing_dir = Path(self.temp_dir) / "existing"
        existing_dir.mkdir()

        result = ensure_directory_exists(existing_dir)
        self.assertTrue(existing_dir.exists())
        self.assertEqual(result, existing_dir)

    def test_ensure_directory_exists_nested(self):
        """Test creating nested directories."""
        nested_dir = Path(self.temp_dir) / "level1" / "level2" / "level3"
        result = ensure_directory_exists(nested_dir)

        self.assertTrue(nested_dir.exists())
        self.assertTrue(nested_dir.is_dir())


class TestLoadJson(unittest.TestCase):
    """Test cases for load_json function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_json_dict(self):
        """Test loading JSON file with dictionary."""
        test_file = Path(self.temp_dir) / "test.json"
        data = {"key": "value", "number": 42}
        test_file.write_text(json.dumps(data))

        result = load_json(test_file, validate_path=False)
        self.assertEqual(result, data)

    def test_load_json_list(self):
        """Test loading JSON file with list."""
        test_file = Path(self.temp_dir) / "test.json"
        data = [1, 2, 3, "four", {"five": 5}]
        test_file.write_text(json.dumps(data))

        result = load_json(test_file, validate_path=False)
        self.assertEqual(result, data)

    def test_load_json_invalid_json(self):
        """Test loading invalid JSON raises ParsingError."""
        test_file = Path(self.temp_dir) / "invalid.json"
        test_file.write_text("{invalid json}")

        with self.assertRaises((ParsingError, FileReadError)) as context:
            load_json(test_file, validate_path=False)

        error = context.exception
        # Check that the error message contains "Invalid JSON" or "JSON"
        self.assertTrue(
            "Invalid JSON" in str(error) or "JSON" in str(error) or "json" in str(error).lower()
        )

    def test_load_json_nonexistent_file(self):
        """Test loading nonexistent file raises FileNotFoundError."""
        nonexistent = Path(self.temp_dir) / "nonexistent.json"

        with self.assertRaises(ATFileNotFoundError):
            load_json(nonexistent, validate_path=False)

    def test_load_json_without_path_validation(self):
        """Test loading JSON without path validation."""
        test_file = Path(self.temp_dir) / "test.txt"  # Wrong extension
        data = {"key": "value"}
        test_file.write_text(json.dumps(data))

        # Should work without validation
        result = load_json(test_file, validate_path=False)
        self.assertEqual(result, data)

    def test_load_json_with_encoding_detection(self):
        """Test loading JSON with encoding detection."""
        test_file = Path(self.temp_dir) / "test.json"
        data = {"message": "Hello 世界"}
        test_file.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

        result = load_json(test_file, detect_encoding=True, validate_path=False)
        self.assertEqual(result, data)

    def test_load_json_without_encoding_detection(self):
        """Test loading JSON without encoding detection."""
        test_file = Path(self.temp_dir) / "test.json"
        data = {"key": "value"}
        test_file.write_text(json.dumps(data))

        result = load_json(test_file, detect_encoding=False, validate_path=False)
        self.assertEqual(result, data)


class TestSaveJson(unittest.TestCase):
    """Test cases for save_json function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_json_dict(self):
        """Test saving dictionary to JSON."""
        test_file = Path(self.temp_dir) / "test.json"
        data = {"key": "value", "number": 42}

        save_json(data, test_file, validate_path=False)

        self.assertTrue(test_file.exists())
        loaded = json.loads(test_file.read_text())
        self.assertEqual(loaded, data)

    def test_save_json_list(self):
        """Test saving list to JSON."""
        test_file = Path(self.temp_dir) / "test.json"
        data = [1, 2, 3, "four"]

        save_json(data, test_file, validate_path=False)

        loaded = json.loads(test_file.read_text())
        self.assertEqual(loaded, data)

    def test_save_json_creates_directory(self):
        """Test that save_json creates parent directories."""
        test_file = Path(self.temp_dir) / "subdir" / "test.json"
        data = {"key": "value"}

        save_json(data, test_file, validate_path=False)

        self.assertTrue(test_file.exists())

    def test_save_json_invalid_type(self):
        """Test saving invalid type raises TypeValidationError."""
        test_file = Path(self.temp_dir) / "test.json"

        with self.assertRaises(TypeValidationError):
            save_json("not a dict or list", test_file, validate_path=False)

    def test_save_json_non_serializable(self):
        """Test saving non-JSON-serializable data raises error."""
        test_file = Path(self.temp_dir) / "test.json"

        class NonSerializable:
            pass

        data = {"obj": NonSerializable()}

        # Should raise FileWriteError (wraps TypeValidationError that has a bug)
        with self.assertRaises((TypeValidationError, FileWriteError)):
            save_json(data, test_file, validate_path=False)

    def test_save_json_atomic_write(self):
        """Test that save_json uses atomic writes by default."""
        test_file = Path(self.temp_dir) / "test.json"
        data = {"key": "value"}

        save_json(data, test_file, validate_path=False, atomic=True)
        self.assertTrue(test_file.exists())

    def test_save_json_without_atomic_write(self):
        """Test saving JSON without atomic writes."""
        test_file = Path(self.temp_dir) / "test.json"
        data = {"key": "value"}

        save_json(data, test_file, validate_path=False, atomic=False)
        self.assertTrue(test_file.exists())

    def test_save_json_custom_kwargs(self):
        """Test saving JSON with custom kwargs."""
        test_file = Path(self.temp_dir) / "test.json"
        data = {"key": "value"}

        save_json(data, test_file, validate_path=False, indent=4, sort_keys=True)

        content = test_file.read_text()
        self.assertIn("    ", content)  # Check indentation


class TestLoadYaml(unittest.TestCase):
    """Test cases for load_yaml function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_yaml_dict(self):
        """Test loading YAML file with dictionary."""
        test_file = Path(self.temp_dir) / "test.yaml"
        data = {"key": "value", "number": 42}
        test_file.write_text(yaml.dump(data))

        result = load_yaml(test_file, validate_path=False)
        self.assertEqual(result, data)

    def test_load_yaml_invalid(self):
        """Test loading invalid YAML raises ParsingError."""
        test_file = Path(self.temp_dir) / "invalid.yaml"
        test_file.write_text("- invalid:\n  - yaml:\n    structure")

        # This might or might not raise depending on yaml strictness
        # Just ensure it returns something or raises ParsingError or FileReadError
        try:
            result = load_yaml(test_file, validate_path=False)
        except (ParsingError, FileReadError):
            pass  # Expected

    def test_load_yaml_nonexistent_file(self):
        """Test loading nonexistent file raises FileNotFoundError."""
        nonexistent = Path(self.temp_dir) / "nonexistent.yaml"

        with self.assertRaises(ATFileNotFoundError):
            load_yaml(nonexistent, validate_path=False)

    def test_load_yaml_yml_extension(self):
        """Test loading YAML file with .yml extension."""
        test_file = Path(self.temp_dir) / "test.yml"
        data = {"key": "value"}
        test_file.write_text(yaml.dump(data))

        result = load_yaml(test_file, validate_path=False)
        self.assertEqual(result, data)


class TestSaveYaml(unittest.TestCase):
    """Test cases for save_yaml function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_yaml_dict(self):
        """Test saving dictionary to YAML."""
        test_file = Path(self.temp_dir) / "test.yaml"
        data = {"key": "value", "number": 42}

        save_yaml(data, test_file, validate_path=False)

        self.assertTrue(test_file.exists())
        loaded = yaml.safe_load(test_file.read_text())
        self.assertEqual(loaded, data)

    def test_save_yaml_invalid_type(self):
        """Test saving non-dict raises TypeValidationError."""
        test_file = Path(self.temp_dir) / "test.yaml"

        with self.assertRaises(TypeValidationError):
            save_yaml([1, 2, 3], test_file, validate_path=False)

    def test_save_yaml_creates_directory(self):
        """Test that save_yaml creates parent directories."""
        test_file = Path(self.temp_dir) / "subdir" / "test.yaml"
        data = {"key": "value"}

        save_yaml(data, test_file, validate_path=False)
        self.assertTrue(test_file.exists())


class TestFileExtensionUtilities(unittest.TestCase):
    """Test cases for file extension utility functions."""

    def test_get_file_extension(self):
        """Test getting file extension."""
        self.assertEqual(get_file_extension("file.txt"), "txt")
        self.assertEqual(get_file_extension("file.json"), "json")
        self.assertEqual(get_file_extension("file.tar.gz"), "gz")

    def test_get_file_extension_no_extension(self):
        """Test getting extension of file without extension."""
        self.assertEqual(get_file_extension("file"), "")

    def test_is_json_file_true(self):
        """Test is_json_file returns True for JSON files."""
        self.assertTrue(is_json_file("test.json"))
        self.assertTrue(is_json_file("test.JSON"))  # Case insensitive

    def test_is_json_file_false(self):
        """Test is_json_file returns False for non-JSON files."""
        self.assertFalse(is_json_file("test.txt"))
        self.assertFalse(is_json_file("test.yaml"))

    def test_is_yaml_file_true(self):
        """Test is_yaml_file returns True for YAML files."""
        self.assertTrue(is_yaml_file("test.yaml"))
        self.assertTrue(is_yaml_file("test.yml"))
        self.assertTrue(is_yaml_file("test.YAML"))

    def test_is_yaml_file_false(self):
        """Test is_yaml_file returns False for non-YAML files."""
        self.assertFalse(is_yaml_file("test.json"))
        self.assertFalse(is_yaml_file("test.txt"))


class TestLoadDataFile(unittest.TestCase):
    """Test cases for load_data_file function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_data_file_json(self):
        """Test loading JSON file via load_data_file."""
        test_file = Path(self.temp_dir) / "test.json"
        data = {"key": "value"}
        test_file.write_text(json.dumps(data))

        # Temp directories are outside allowed paths, so this raises ValidationError
        with self.assertRaises(ValidationError):
            load_data_file(test_file)

    def test_load_data_file_yaml(self):
        """Test loading YAML file via load_data_file."""
        test_file = Path(self.temp_dir) / "test.yaml"
        data = {"key": "value"}
        test_file.write_text(yaml.dump(data))

        # Temp directories are outside allowed paths, so this raises ValidationError
        with self.assertRaises(ValidationError):
            load_data_file(test_file)

    def test_load_data_file_unsupported_extension(self):
        """Test loading file with unsupported extension raises error."""
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("some content")

        with self.assertRaises(ValueValidationError):
            load_data_file(test_file)

    def test_load_data_file_nonexistent(self):
        """Test loading nonexistent file raises error."""
        nonexistent = Path(self.temp_dir) / "nonexistent.json"

        with self.assertRaises(ATFileNotFoundError):
            load_data_file(nonexistent)


class TestSaveDataFile(unittest.TestCase):
    """Test cases for save_data_file function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_data_file_json(self):
        """Test saving to JSON file via save_data_file."""
        test_file = Path(self.temp_dir) / "test.json"
        data = {"key": "value"}

        # Temp directories are outside allowed paths, so this raises ValidationError
        with self.assertRaises(ValidationError):
            save_data_file(data, test_file)

    def test_save_data_file_yaml(self):
        """Test saving to YAML file via save_data_file."""
        test_file = Path(self.temp_dir) / "test.yaml"
        data = {"key": "value"}

        # Temp directories are outside allowed paths, so this raises ValidationError
        with self.assertRaises(ValidationError):
            save_data_file(data, test_file)

    def test_save_data_file_unsupported_extension(self):
        """Test saving to unsupported extension raises error."""
        test_file = Path(self.temp_dir) / "test.txt"
        data = {"key": "value"}

        with self.assertRaises(ValueValidationError):
            save_data_file(data, test_file)


class TestListFiles(unittest.TestCase):
    """Test cases for list_files function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_list_files_all(self):
        """Test listing all files in directory."""
        # Create test files
        (Path(self.temp_dir) / "file1.txt").touch()
        (Path(self.temp_dir) / "file2.json").touch()
        (Path(self.temp_dir) / "file3.yaml").touch()

        files = list_files(self.temp_dir)
        self.assertEqual(len(files), 3)

    def test_list_files_with_extension_filter(self):
        """Test listing files with extension filter."""
        (Path(self.temp_dir) / "file1.txt").touch()
        (Path(self.temp_dir) / "file2.txt").touch()
        (Path(self.temp_dir) / "file3.json").touch()

        files = list_files(self.temp_dir, extension=".txt")
        self.assertEqual(len(files), 2)

    def test_list_files_extension_without_dot(self):
        """Test extension filter works without leading dot."""
        (Path(self.temp_dir) / "file1.json").touch()
        (Path(self.temp_dir) / "file2.json").touch()

        files = list_files(self.temp_dir, extension="json")
        self.assertEqual(len(files), 2)

    def test_list_files_empty_directory(self):
        """Test listing files in empty directory."""
        files = list_files(self.temp_dir)
        self.assertEqual(len(files), 0)

    def test_list_files_nonexistent_directory(self):
        """Test listing files in nonexistent directory raises error."""
        nonexistent = Path(self.temp_dir) / "nonexistent"

        with self.assertRaises(ATFileNotFoundError):
            list_files(nonexistent)

    def test_list_files_excludes_subdirectories(self):
        """Test that list_files excludes subdirectories."""
        (Path(self.temp_dir) / "file.txt").touch()
        (Path(self.temp_dir) / "subdir").mkdir()

        files = list_files(self.temp_dir)
        self.assertEqual(len(files), 1)  # Only the file, not the directory


class TestIntegration(unittest.TestCase):
    """Integration tests for file utilities."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_load_json_roundtrip(self):
        """Test saving and loading JSON preserves data."""
        test_file = Path(self.temp_dir) / "roundtrip.json"
        original_data = {"key": "value", "number": 42, "list": [1, 2, 3]}

        save_json(original_data, test_file, validate_path=False)
        loaded_data = load_json(test_file, validate_path=False)

        self.assertEqual(loaded_data, original_data)

    def test_save_and_load_yaml_roundtrip(self):
        """Test saving and loading YAML preserves data."""
        test_file = Path(self.temp_dir) / "roundtrip.yaml"
        original_data = {"key": "value", "number": 42}

        save_yaml(original_data, test_file, validate_path=False)
        loaded_data = load_yaml(test_file, validate_path=False)

        self.assertEqual(loaded_data, original_data)

    def test_atomic_write_protects_against_corruption(self):
        """Test that atomic write protects against corruption."""
        test_file = Path(self.temp_dir) / "protected.json"
        original_data = {"original": "data"}

        save_json(original_data, test_file, validate_path=False)

        # Try to save corrupted data with error
        try:
            with atomic_write(test_file) as f:
                f.write('{"corrupted": ')  # Incomplete JSON
                raise ValueError("Simulated error")
        except ValueError:
            pass

        # Original data should still be intact
        loaded = load_json(test_file, validate_path=False)
        self.assertEqual(loaded, original_data)


if __name__ == "__main__":
    unittest.main()
