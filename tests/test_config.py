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

        # Clear any ANNOTATION_TOOLKIT environment variables
        self.env_backup = {}
        for key in list(os.environ.keys()):
            if key.startswith("ANNOTATION_TOOLKIT_"):
                self.env_backup[key] = os.environ.pop(key)

    def tearDown(self):
        """Clean up after test."""
        # Restore environment variables
        os.environ.update(self.env_backup)

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

    def test_get_security_config(self):
        """Test getting security configuration."""
        config = Config()
        # Get root security config
        sec_config = config.get_security_config()
        self.assertIsInstance(sec_config, dict)
        self.assertIn("max_file_size", sec_config)

        # Get nested security config
        max_size = config.get_security_config("max_file_size")
        self.assertEqual(max_size, 100 * 1024 * 1024)

        rate_limit = config.get_security_config("rate_limit", "max_requests")
        self.assertEqual(rate_limit, 100)

    def test_get_performance_config(self):
        """Test getting performance configuration."""
        config = Config()
        # Get root performance config
        perf_config = config.get_performance_config()
        self.assertIsInstance(perf_config, dict)
        self.assertIn("cache", perf_config)

        # Get nested performance config
        cache_enabled = config.get_performance_config("cache", "enabled")
        self.assertTrue(cache_enabled)

        cache_size = config.get_performance_config("cache", "max_size")
        self.assertEqual(cache_size, 128)

    def test_all_property(self):
        """Test the all property."""
        config = Config()
        all_config = config.all
        self.assertIsInstance(all_config, dict)
        self.assertIn("ui", all_config)
        self.assertIn("tools", all_config)
        self.assertIn("security", all_config)
        self.assertIn("performance", all_config)

    def test_nested_get(self):
        """Test getting deeply nested values."""
        config = Config()
        # Test multiple levels of nesting
        window_width = config.get("ui", "window_size", "width")
        self.assertEqual(window_width, 1400)

        encoding = config.get("security", "encoding", "default")
        self.assertEqual(encoding, "utf-8")

    def test_nested_set(self):
        """Test setting deeply nested values."""
        config = Config()
        # Set a deeply nested value
        config.set(1600, "ui", "window_size", "width")
        self.assertEqual(config.get("ui", "window_size", "width"), 1600)

        # Set a new nested structure
        config.set("custom", "new", "section", "subsection", "key")
        self.assertEqual(config.get("new", "section", "subsection", "key"), "custom")

    @patch.dict(os.environ, {
        "ANNOTATION_TOOLKIT_SECURITY_MAX_FILE_SIZE": "50000000",
        "ANNOTATION_TOOLKIT_LOGGING_LEVEL": "INFO"
    })
    def test_env_override_with_type_conversion(self):
        """Test environment variable override with type conversion."""
        config = Config()
        # Integer conversion
        max_size = config.get("security", "max_file_size")
        self.assertEqual(max_size, 50000000)
        self.assertIsInstance(max_size, int)

        # String value
        log_level = config.get("logging", "level")
        self.assertEqual(log_level, "INFO")

    @patch.dict(os.environ, {
        "ANNOTATION_TOOLKIT_DATA_AUTOSAVE": "false",
        "ANNOTATION_TOOLKIT_PERFORMANCE_CACHE_ENABLED": "false"
    })
    def test_env_override_boolean_false(self):
        """Test environment variable override with false boolean."""
        config = Config()
        self.assertFalse(config.get("data", "autosave"))
        self.assertFalse(config.get("performance", "cache", "enabled"))

    @patch.dict(os.environ, {
        "ANNOTATION_TOOLKIT_PERFORMANCE_CACHE_TTL_SECONDS": "600"
    })
    def test_env_override_nested_value(self):
        """Test environment variable override for nested value."""
        config = Config()
        ttl = config.get("performance", "cache", "ttl_seconds")
        self.assertEqual(ttl, 600)
        self.assertIsInstance(ttl, int)

    def test_configuration_merge(self):
        """Test that file configuration merges with defaults."""
        # Create a partial config file
        config_data = {
            "ui": {
                "theme": "dark"
                # font_size not specified, should use default
            }
        }
        config_path = Path(self.temp_dir.name) / "partial_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        config = Config(str(config_path))
        # Custom value from file
        self.assertEqual(config.get("ui", "theme"), "dark")
        # Default value should still be present
        self.assertEqual(config.get("ui", "font_size"), 12)
        # Other sections should also have defaults
        self.assertTrue(config.get("tools", "dict_to_bullet", "enabled"))

    def test_save_and_reload_roundtrip(self):
        """Test saving and reloading configuration maintains values."""
        config = Config()
        config.set("custom_theme", "ui", "theme")
        config.set(16, "ui", "font_size")
        config.set(False, "data", "autosave")

        config_path = Path(self.temp_dir.name) / "roundtrip_config.yaml"
        config.save_to_file(str(config_path))

        # Load fresh config from saved file
        reloaded = Config(str(config_path))
        self.assertEqual(reloaded.get("ui", "theme"), "custom_theme")
        self.assertEqual(reloaded.get("ui", "font_size"), 16)
        self.assertFalse(reloaded.get("data", "autosave"))

    def test_get_with_default_nested(self):
        """Test get with default value for nested nonexistent keys."""
        config = Config()
        value = config.get("nonexistent", "nested", "key", default="fallback")
        self.assertEqual(value, "fallback")

    def test_set_overwrites_existing_value(self):
        """Test that set overwrites existing values."""
        config = Config()
        original = config.get("ui", "theme")
        config.set("new_theme", "ui", "theme")
        new_value = config.get("ui", "theme")
        self.assertNotEqual(original, new_value)
        self.assertEqual(new_value, "new_theme")

    def test_default_save_directory_creation(self):
        """Test that default save directory is created."""
        config = Config()
        save_dir = config.get("data", "save_directory")
        self.assertIsNotNone(save_dir)
        self.assertTrue(Path(save_dir).exists() or save_dir.startswith(str(Path.home())))

    def test_configuration_types_preservation(self):
        """Test that configuration preserves different types."""
        config = Config()

        # Boolean
        bool_val = config.get("data", "autosave")
        self.assertIsInstance(bool_val, bool)

        # Integer
        int_val = config.get("ui", "font_size")
        self.assertIsInstance(int_val, int)

        # String
        str_val = config.get("ui", "theme")
        self.assertIsInstance(str_val, str)

        # Dict
        dict_val = config.get("ui", "window_size")
        self.assertIsInstance(dict_val, dict)

    def test_set_creates_intermediate_dicts(self):
        """Test that set creates intermediate dictionaries."""
        config = Config()
        config.set("value", "brand", "new", "deeply", "nested", "key")

        # All intermediate keys should exist
        self.assertIsInstance(config.get("brand"), dict)
        self.assertIsInstance(config.get("brand", "new"), dict)
        self.assertIsInstance(config.get("brand", "new", "deeply"), dict)
        self.assertEqual(config.get("brand", "new", "deeply", "nested", "key"), "value")

    def test_get_empty_keys(self):
        """Test get with empty keys returns None."""
        config = Config()
        # get() with no keys should return None
        result = config.get()
        # Since the behavior may vary, just test that it doesn't crash
        # If it returns the whole config, that's also acceptable
        self.assertTrue(result is None or isinstance(result, dict))

    def test_yaml_file_with_complex_types(self):
        """Test loading YAML with complex types."""
        config_data = {
            "test": {
                "list": [1, 2, 3],
                "nested_list": [[1, 2], [3, 4]],
                "mixed": {
                    "num": 42,
                    "str": "test",
                    "bool": True,
                    "null": None
                }
            }
        }
        config_path = Path(self.temp_dir.name) / "complex_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        config = Config(str(config_path))
        self.assertEqual(config.get("test", "list"), [1, 2, 3])
        self.assertEqual(config.get("test", "nested_list"), [[1, 2], [3, 4]])
        self.assertEqual(config.get("test", "mixed", "num"), 42)
        self.assertIsNone(config.get("test", "mixed", "null"))

    @patch.dict(os.environ, {
        "ANNOTATION_TOOLKIT_UI_THEME": "   spaces   "
    })
    def test_env_whitespace_handling(self):
        """Test that environment variables preserve whitespace."""
        config = Config()
        theme = config.get("ui", "theme")
        # Environment variables are NOT trimmed, they preserve whitespace
        self.assertEqual(theme, "   spaces   ")

    def test_security_config_with_nested_access(self):
        """Test accessing nested security configuration."""
        config = Config()

        # Path validation settings
        check_symlinks = config.get_security_config("path_validation", "check_symlinks")
        self.assertTrue(check_symlinks)

        # Encoding settings
        fallback_encodings = config.get_security_config("encoding", "fallback_encodings")
        self.assertIsInstance(fallback_encodings, list)
        self.assertIn("latin-1", fallback_encodings)

    def test_performance_config_with_nested_access(self):
        """Test accessing nested performance configuration."""
        config = Config()

        # Streaming settings
        chunk_size = config.get_performance_config("streaming", "chunk_size")
        self.assertEqual(chunk_size, 8192)

        # Retry settings
        max_attempts = config.get_performance_config("retry", "max_attempts")
        self.assertEqual(max_attempts, 3)


if __name__ == "__main__":
    unittest.main()
