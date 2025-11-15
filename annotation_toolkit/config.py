"""
Configuration management for the annotation toolkit.

This module handles loading, validating, and providing access to
configuration settings for the annotation toolkit.
"""

import copy
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from .utils import logger
from .utils.errors import (
    ErrorCode,
    ConfigurationError,
    FileNotFoundError as ATFileNotFoundError,
    FileReadError,
    FileWriteError,
    InvalidConfigurationError,
    MissingConfigurationError,
    ParsingError
)
from .utils.error_handler import with_error_handling


class Config:
    """
    Configuration manager for the annotation toolkit.

    This class handles loading configuration from files, environment variables,
    and provides a unified interface for accessing configuration settings.
    """

    DEFAULT_CONFIG = {
        "tools": {
            "dict_to_bullet": {"enabled": True, "default_color": "#4CAF50"},
            "conversation_visualizer": {
                "enabled": True,
                "default_color": "#2196F3",
                "user_message_color": "#4285F4",  # Brighter blue that works on both themes
                "ai_message_color": "#34A853",  # Brighter green that works on both themes
            },
            "json_fixer": {
                "enabled": True,
                "debug_logging": True,  # Set to True to enable debug logging
            },
            "text_collector": {
                "enabled": True,
                "max_fields": 20,  # Maximum number of text fields to collect
                "filter_empty": True,  # Filter out empty/whitespace-only strings
            },
        },
        "ui": {
            "theme": "default",
            "font_size": 12,
            "window_size": {"width": 1400, "height": 900},  # Increased for more space
        },
        "data": {
            "save_directory": "",
            "autosave": False,
            "autosave_interval": 300,  # seconds
        },
        "logging": {
            "level": "DEBUG",  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
            "file_logging": True,
            "console_logging": True,
        },
        "security": {
            "max_file_size": 100 * 1024 * 1024,  # 100MB default
            "max_path_length": 4096,
            "allowed_extensions": [".json", ".yaml", ".yml", ".txt", ".md", ".csv"],
            "rate_limit": {
                "window_seconds": 60,
                "max_requests": 100,
            },
            "path_validation": {
                "check_symlinks": True,
                "max_symlink_depth": 10,
                "allow_hidden_files": False,
            },
            "encoding": {
                "default": "utf-8",
                "auto_detect": True,
                "confidence_threshold": 0.7,
                "fallback_encodings": ["latin-1", "cp1252", "iso-8859-1"],
            },
        },
        "performance": {
            "cache": {
                "enabled": True,
                "max_size": 128,
                "ttl_seconds": 300,
            },
            "streaming": {
                "enabled": True,
                "chunk_size": 8192,
                "max_items": 1000,
            },
            "retry": {
                "enabled": True,
                "max_attempts": 3,
                "base_delay": 0.1,
                "max_delay": 2.0,
                "exponential_base": 2.0,
            },
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.

        Args:
            config_path (Optional[str]): Path to a configuration file.
                If None, the default configuration will be used.
        """
        logger.debug("Initializing configuration manager")
        self._config = copy.deepcopy(self.DEFAULT_CONFIG)

        # Load configuration from file if provided
        if config_path:
            logger.info(f"Loading configuration from file: {config_path}")
            self.load_from_file(config_path)
        else:
            logger.info("Using default configuration")

        # Override with environment variables
        logger.debug("Checking for configuration overrides in environment variables")
        self._load_from_env()

        # Set default save directory if not specified
        if not self._config["data"]["save_directory"]:
            default_dir = str(Path.home() / "annotation_toolkit_data")
            logger.debug(f"Setting default save directory to: {default_dir}")
            self._config["data"]["save_directory"] = default_dir

        # Ensure save directory exists
        save_dir = self._config["data"]["save_directory"]
        logger.debug(f"Ensuring save directory exists: {save_dir}")
        os.makedirs(save_dir, exist_ok=True)
        logger.info(f"Configuration initialized successfully")

    def get_security_config(self, *keys) -> Any:
        """
        Get security configuration values.

        Args:
            *keys: Nested keys to retrieve from security config.

        Returns:
            The requested configuration value.

        Example:
            config.get_security_config('max_file_size')
            config.get_security_config('rate_limit', 'max_requests')
        """
        return self.get('security', *keys)

    def get_performance_config(self, *keys) -> Any:
        """
        Get performance configuration values.

        Args:
            *keys: Nested keys to retrieve from performance config.

        Returns:
            The requested configuration value.
        """
        return self.get('performance', *keys)

    @with_error_handling(
        error_code=ErrorCode.FILE_READ_ERROR,
        error_message="Error loading configuration file",
        suggestion="Check that the configuration file exists and is valid YAML."
    )
    def load_from_file(self, config_path: str) -> None:
        """
        Load configuration from a YAML file.

        Args:
            config_path (str): Path to the configuration file.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            ParsingError: If the configuration file is not valid YAML.
            FileReadError: If there's an error reading the file.
        """
        config_path_str = str(config_path)
        config_path = Path(config_path)

        if not config_path.exists():
            logger.error(f"Configuration file not found: {config_path}")
            raise ATFileNotFoundError(
                config_path_str,
                suggestion=f"Ensure the configuration file exists at '{config_path_str}' or specify a different path."
            )

        try:
            logger.debug(f"Reading configuration file: {config_path}")
            with open(config_path, "r") as f:
                try:
                    file_config = yaml.safe_load(f)
                except yaml.YAMLError as e:
                    # Extract line and column info if available
                    line_info = ""
                    if hasattr(e, 'problem_mark'):
                        line_info = f" at line {e.problem_mark.line+1}, column {e.problem_mark.column+1}"

                    raise ParsingError(
                        f"Invalid YAML in configuration file: {config_path_str}{line_info}",
                        details={
                            "file_path": config_path_str,
                            "error": str(e)
                        },
                        suggestion="Check the YAML syntax and ensure it's valid. Common issues include incorrect indentation, missing colons, or unbalanced quotes.",
                        cause=e
                    )

            if file_config:
                logger.debug("Updating configuration with values from file")
                # Recursively update configuration
                self._update_config(self._config, file_config)
                logger.info(f"Configuration loaded successfully from {config_path}")
            else:
                logger.warning(f"Configuration file {config_path} is empty or invalid")
                raise InvalidConfigurationError(
                    f"Configuration file {config_path_str} is empty or contains invalid YAML",
                    suggestion="Ensure the configuration file contains valid YAML data."
                )
        except (ATFileNotFoundError, ParsingError, InvalidConfigurationError):
            # Re-raise these specific exceptions
            raise
        except PermissionError as e:
            raise FileReadError(
                config_path_str,
                details={"error": str(e)},
                suggestion="Check that you have permission to read this file.",
                cause=e
            )
        except Exception as e:
            # Wrap any other exceptions
            raise FileReadError(
                config_path_str,
                details={"error": str(e)},
                suggestion="An unexpected error occurred while reading the configuration file.",
                cause=e
            )

    def _update_config(self, target: Dict, source: Dict) -> None:
        """
        Recursively update a nested dictionary.

        Args:
            target (Dict): The dictionary to update.
            source (Dict): The dictionary with new values.
        """
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                self._update_config(target[key], value)
            else:
                target[key] = value

    def _set_config_value(self, config_section: Dict, key: str, value: str) -> None:
        """
        Set a configuration value with appropriate type conversion.

        Args:
            config_section (Dict): The configuration section to update
            key (str): The key to set
            value (str): The string value from the environment variable
        """
        original_value = config_section[key]

        # Convert the value to the appropriate type
        if isinstance(original_value, bool):
            config_section[key] = value.lower() in ("true", "1", "yes", "y")
        elif isinstance(original_value, int):
            try:
                config_section[key] = int(value)
            except ValueError:
                logger.warning(f"Could not convert value '{value}' to int")
        elif isinstance(original_value, float):
            try:
                config_section[key] = float(value)
            except ValueError:
                logger.warning(f"Could not convert value '{value}' to float")
        else:
            config_section[key] = value

        logger.debug(f"Set {key} to {config_section[key]}")

    def _load_from_env(self) -> None:
        """
        Load configuration from environment variables.

        Environment variables should be prefixed with 'ANNOTATION_TOOLKIT_'.
        Nested keys should be separated by underscores.
        For example, 'ANNOTATION_TOOLKIT_UI_THEME' would override self._config["ui"]["theme"].
        """
        prefix = "ANNOTATION_TOOLKIT_"
        env_vars_found = 0

        for key, value in os.environ.items():
            if key.startswith(prefix):
                logger.debug(f"Found environment variable: {key}={value}")

                # Remove prefix and convert to lowercase
                key_without_prefix = key[len(prefix):].lower()

                # Special handling for known environment variables
                if key_without_prefix == "ui_font_size":
                    if "ui" in self._config and "font_size" in self._config["ui"]:
                        try:
                            self._config["ui"]["font_size"] = int(value)
                            logger.debug(f"Set ui.font_size to {value}")
                            env_vars_found += 1
                            continue
                        except ValueError:
                            logger.warning(f"Could not convert {key}={value} to int")

                if key_without_prefix == "ui_theme":
                    if "ui" in self._config and "theme" in self._config["ui"]:
                        self._config["ui"]["theme"] = value
                        logger.debug(f"Set ui.theme to {value}")
                        env_vars_found += 1
                        continue

                if key_without_prefix == "data_autosave":
                    if "data" in self._config and "autosave" in self._config["data"]:
                        self._config["data"]["autosave"] = value.lower() in ("true", "1", "yes", "y")
                        logger.debug(f"Set data.autosave to {self._config['data']['autosave']}")
                        env_vars_found += 1
                        continue

                # General case for other environment variables
                parts = key_without_prefix.split("_")

                # Try to find the right place in the config
                if len(parts) >= 2:
                    section = parts[0]
                    if section in self._config:
                        # Try different combinations for the key
                        if len(parts) == 2:
                            # Simple case: SECTION_KEY
                            key_name = parts[1]
                            if key_name in self._config[section]:
                                self._set_config_value(self._config[section], key_name, value)
                                env_vars_found += 1
                                continue

                        elif len(parts) >= 3:
                            # Try SECTION_SUBSECTION_KEY
                            subsection = parts[1]
                            if subsection in self._config[section]:
                                key_name = "_".join(parts[2:])
                                if key_name in self._config[section][subsection]:
                                    self._set_config_value(self._config[section][subsection], key_name, value)
                                    env_vars_found += 1
                                    continue

                            # Try SECTION_KEY_WITH_UNDERSCORES
                            key_name = "_".join(parts[1:])
                            if key_name in self._config[section]:
                                self._set_config_value(self._config[section], key_name, value)
                                env_vars_found += 1
                                continue

                logger.warning(f"Ignoring environment variable {key}: could not map to configuration")

        if env_vars_found > 0:
            logger.info(
                f"Applied {env_vars_found} configuration settings from environment variables"
            )

    @with_error_handling(
        error_code=ErrorCode.FILE_WRITE_ERROR,
        error_message="Error saving configuration file",
        suggestion="Check that you have permission to write to the specified location."
    )
    def save_to_file(self, config_path: str) -> None:
        """
        Save the current configuration to a YAML file.

        Args:
            config_path (str): Path to save the configuration file.

        Raises:
            FileWriteError: If there's an error writing to the file.
        """
        config_path_str = str(config_path)
        logger.info(f"Saving configuration to file: {config_path}")

        try:
            # Ensure the directory exists
            directory = os.path.dirname(config_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            with open(config_path, "w") as f:
                yaml.dump(self._config, f, default_flow_style=False)
            logger.info(f"Configuration saved successfully to {config_path}")
        except PermissionError as e:
            raise FileWriteError(
                config_path_str,
                details={"error": str(e)},
                suggestion="Check that you have permission to write to this file and directory.",
                cause=e
            )
        except Exception as e:
            raise FileWriteError(
                config_path_str,
                details={"error": str(e)},
                suggestion="An unexpected error occurred while saving the configuration file.",
                cause=e
            )

    def get(self, *keys: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            *keys: The key path to the configuration value.
            default: The default value to return if the key is not found.

        Returns:
            The configuration value, or the default if not found.
        """
        config = self._config
        for key in keys:
            if isinstance(config, dict) and key in config:
                config = config[key]
            else:
                return default
        return config

    @with_error_handling(
        error_code=ErrorCode.INVALID_CONFIGURATION,
        error_message="Error setting configuration value",
        suggestion="Check that the configuration key path is valid."
    )
    def set(self, value: Any, *keys: str) -> None:
        """
        Set a configuration value.

        Args:
            value: The value to set.
            *keys: The key path to the configuration value.

        Raises:
            InvalidConfigurationError: If the key path is invalid.
            MissingConfigurationError: If no keys are provided.
        """
        if not keys:
            logger.error("Attempted to set configuration value with no keys provided")
            raise MissingConfigurationError(
                "No keys provided when setting configuration value",
                suggestion="Provide at least one key when setting a configuration value."
            )

        logger.debug(f"Setting configuration value at {'.'.join(keys)} to {value}")

        config = self._config
        for key in keys[:-1]:
            if isinstance(config, dict):
                if key not in config:
                    logger.debug(f"Creating new configuration section: {key}")
                    config[key] = {}
                config = config[key]
            else:
                logger.error(f"Invalid configuration key path: {keys}")
                raise InvalidConfigurationError(
                    f"Invalid configuration key path: {'.'.join(keys)}",
                    details={"keys": keys, "invalid_key": key},
                    suggestion=f"Ensure all parts of the key path except the last one refer to existing dictionary sections."
                )

        if isinstance(config, dict):
            config[keys[-1]] = value
            logger.debug(
                f"Configuration value set successfully: {'.'.join(keys)} = {value}"
            )
        else:
            logger.error(f"Invalid configuration key path: {keys}")
            raise InvalidConfigurationError(
                f"Invalid configuration key path: {'.'.join(keys)}",
                details={"keys": keys, "invalid_key": keys[-1]},
                suggestion=f"Ensure all parts of the key path except the last one refer to existing dictionary sections."
            )

    @property
    def all(self) -> Dict:
        """
        Get the entire configuration.

        Returns:
            Dict: The entire configuration.
        """
        return self._config.copy()
