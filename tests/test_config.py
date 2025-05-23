"""
Tests for the configuration management module.

This module contains tests for the Config class in the
annotation_toolkit.config module.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, mock_open

import yaml

from annotation_toolkit.config import Config
from annotation_toolkit.utils.errors import (
    ConfigurationError,
    FileNotFoundError as ATFileNotFoundError,
    FileReadError,
    FileWriteError,
    InvalidConfigurationError,
    ParsingError
)


class TestConfig(unittest.TestCase):
    """Test cases for the Config class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

    def test_default_initialization(self):
        """Test that the Config class initializes with default values."""
        config = Config()
        self.assertIsNotNone(config.all)
        self.assertEqual(config.get("ui", "theme"), "default")
        self.assertEqual(config.get("ui", "font_size"), 12)
        self.assertEqual(config.get("tools", "dict_to_bullet", "enabled"), True)

    def test_load_from_file(self):
        """Test loading configuration from a file."""
        # Create a test configuration file
        config_data = {
            "ui": {
                "theme": "dark",
                "font_size": 14
            }
        }
        config_path = Path(self.temp_dir.name) / "test_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        # Load the configuration
        config = Config(str(config_path))

        # Check that the configuration was loaded correctly
        self.assertEqual(config.get("ui", "theme"), "dark")
        self.assertEqual(config.get("ui", "font_size"), 14)
        # Check that default values are still present for unspecified settings
        self.assertEqual(config.get("tools", "dict_to_bullet", "enabled"), True)

    def test_load_from_nonexistent_file(self):
        """Test loading configuration from a nonexistent file."""
        with self.assertRaises(ATFileNotFoundError):
            Config("/nonexistent/path/config.yaml")

    def test_load_invalid_yaml(self):
        """Test loading configuration from a file with invalid YAML."""
        # Create a test configuration file with invalid YAML
        config_path = Path(self.temp_dir.name) / "invalid_config.yaml"
        with open(config_path, "w") as f:
            f.write("ui:\n  theme: 'dark\n  font_size: 14")  # Missing closing quote

        # Try to load the configuration
        with self.assertRaises(ParsingError):
            Config(str(config_path))

    def test_load_empty_yaml(self):
        """Test loading configuration from an empty YAML file."""
        # Create an empty test configuration file
        config_path = Path(self.temp_dir.name) / "empty_config.yaml"
        with open(config_path, "w") as f:
            f.write("")

        # Try to load the configuration
        with self.assertRaises(InvalidConfigurationError):
            Config(str(config_path))

    def test_save_to_file(self):
        """Test saving configuration to a file."""
        config = Config()
        config.set("dark", "ui", "theme")
        config.set(14, "ui", "font_size")

        # Save the configuration
        config_path = Path(self.temp_dir.name) / "saved_config.yaml"
        config.save_to_file(str(config_path))

        # Check that the file was created
        self.assertTrue(config_path.exists())

        # Load the configuration back and check the values
        loaded_config = Config(str(config_path))
        self.assertEqual(loaded_config.get("ui", "theme"), "dark")
        self.assertEqual(loaded_config.get("ui", "font_size"), 14)

    def test_save_to_nonexistent_directory(self):
        """Test saving configuration to a nonexistent directory."""
        config = Config()
        config_path = Path(self.temp_dir.name) / "new_dir" / "config.yaml"

        # The directory doesn't exist yet, but save_to_file should create it
        config.save_to_file(str(config_path))
        self.assertTrue(config_path.exists())

    @patch("builtins.open", side_effect=PermissionError("Permission denied"))
    def test_save_permission_error(self, mock_open):
        """Test saving configuration with permission error."""
        config = Config()
        with self.assertRaises(FileWriteError):
            config.save_to_file("/path/to/config.yaml")

    def test_get_nonexistent_key(self):
        """Test getting a nonexistent configuration key."""
        config = Config()
        # Should return the default value
        self.assertEqual(config.get("nonexistent", "key", default="default"), "default")
        # Should return None if no default is specified
        self.assertIsNone(config.get("nonexistent", "key"))

    def test_set_and_get(self):
        """Test setting and getting configuration values."""
        config = Config()
        config.set("new_value", "ui", "theme")
        self.assertEqual(config.get("ui", "theme"), "new_value")

    def test_set_new_section(self):
        """Test setting a value in a new section."""
        config = Config()
        config.set("value", "new_section", "key")
        self.assertEqual(config.get("new_section", "key"), "value")

    def test_set_invalid_path(self):
        """Test setting a value with an invalid path."""
        config = Config()
        # Set a non-dict value
        config.set("value", "simple_key")
        # Try to set a nested value under the non-dict key
        with self.assertRaises(InvalidConfigurationError):
            config.set("nested_value", "simple_key", "nested_key")

    def test_set_no_keys(self):
        """Test setting a value with no keys."""
        config = Config()
        with self.assertRaises(ConfigurationError):
            config.set("value")

    @patch.dict(os.environ, {
        "ANNOTATION_TOOLKIT_UI_THEME": "dark",
        "ANNOTATION_TOOLKIT_UI_FONT_SIZE": "16",
        "ANNOTATION_TOOLKIT_DATA_AUTOSAVE": "true"
    })
    def test_load_from_env(self):
        """Test loading configuration from environment variables."""
        config = Config()
        self.assertEqual(config.get("ui", "theme"), "dark")
        self.assertEqual(config.get("ui", "font_size"), 16)
        self.assertEqual(config.get("data", "autosave"), True)

    @patch.dict(os.environ, {
        "ANNOTATION_TOOLKIT_NONEXISTENT_SECTION_KEY": "value"
    })
    def test_load_from_env_nonexistent_path(self):
        """Test loading configuration from environment variables with nonexistent path."""
        # This should not raise an exception, just log a warning
        config = Config()
        # The nonexistent path should not be added to the configuration
        self.assertIsNone(config.get("nonexistent_section", "key"))


if __name__ == "__main__":
    unittest.main()
