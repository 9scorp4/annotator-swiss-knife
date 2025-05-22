"""
Configuration management for the annotation toolkit.

This module handles loading, validating, and providing access to
configuration settings for the annotation toolkit.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from .utils import logger


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
        },
        "ui": {
            "theme": "default",
            "font_size": 12,
            "window_size": {"width": 1000, "height": 700},
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
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.

        Args:
            config_path (Optional[str]): Path to a configuration file.
                If None, the default configuration will be used.
        """
        logger.debug("Initializing configuration manager")
        self._config = self.DEFAULT_CONFIG.copy()

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

    def load_from_file(self, config_path: str) -> None:
        """
        Load configuration from a YAML file.

        Args:
            config_path (str): Path to the configuration file.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            yaml.YAMLError: If the configuration file is not valid YAML.
        """
        config_path = Path(config_path)
        if not config_path.exists():
            logger.error(f"Configuration file not found: {config_path}")
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            logger.debug(f"Reading configuration file: {config_path}")
            with open(config_path, "r") as f:
                file_config = yaml.safe_load(f)

            if file_config:
                logger.debug("Updating configuration with values from file")
                # Recursively update configuration
                self._update_config(self._config, file_config)
                logger.info(f"Configuration loaded successfully from {config_path}")
            else:
                logger.warning(f"Configuration file {config_path} is empty or invalid")
        except yaml.YAMLError as e:
            logger.exception(f"Error parsing YAML configuration file: {str(e)}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error loading configuration file: {str(e)}")
            raise

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
                # Remove prefix and split into parts
                parts = key[len(prefix) :].lower().split("_")

                # Navigate to the right part of the config
                config = self._config
                for part in parts[:-1]:
                    if part in config:
                        config = config[part]
                    else:
                        # Skip this environment variable if the path doesn't exist
                        logger.warning(
                            f"Ignoring environment variable {key}: invalid configuration path"
                        )
                        break
                else:
                    # If we didn't break, set the value
                    last_part = parts[-1]
                    if last_part in config:
                        # Try to convert the value to the appropriate type
                        original_value = config[last_part]
                        if isinstance(original_value, bool):
                            config[last_part] = value.lower() in (
                                "true",
                                "1",
                                "yes",
                                "y",
                            )
                        elif isinstance(original_value, int):
                            try:
                                config[last_part] = int(value)
                            except ValueError:
                                logger.warning(
                                    f"Could not convert environment variable {key} value '{value}' to int"
                                )
                                pass
                        elif isinstance(original_value, float):
                            try:
                                config[last_part] = float(value)
                            except ValueError:
                                logger.warning(
                                    f"Could not convert environment variable {key} value '{value}' to float"
                                )
                                pass
                        else:
                            config[last_part] = value

                        logger.debug(f"Applied environment variable {key}={value}")
                        env_vars_found += 1
                    else:
                        logger.warning(
                            f"Ignoring environment variable {key}: key {last_part} not found in configuration"
                        )

        if env_vars_found > 0:
            logger.info(
                f"Applied {env_vars_found} configuration settings from environment variables"
            )

    def save_to_file(self, config_path: str) -> None:
        """
        Save the current configuration to a YAML file.

        Args:
            config_path (str): Path to save the configuration file.
        """
        logger.info(f"Saving configuration to file: {config_path}")
        try:
            with open(config_path, "w") as f:
                yaml.dump(self._config, f, default_flow_style=False)
            logger.info(f"Configuration saved successfully to {config_path}")
        except Exception as e:
            logger.exception(f"Error saving configuration to {config_path}: {str(e)}")
            raise

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

    def set(self, value: Any, *keys: str) -> None:
        """
        Set a configuration value.

        Args:
            value: The value to set.
            *keys: The key path to the configuration value.

        Raises:
            KeyError: If the key path is invalid.
        """
        if not keys:
            logger.error("Attempted to set configuration value with no keys provided")
            raise KeyError("No keys provided")

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
                raise KeyError(f"Invalid key path: {keys}")

        if isinstance(config, dict):
            config[keys[-1]] = value
            logger.debug(
                f"Configuration value set successfully: {'.'.join(keys)} = {value}"
            )
        else:
            logger.error(f"Invalid configuration key path: {keys}")
            raise KeyError(f"Invalid key path: {keys}")

    @property
    def all(self) -> Dict:
        """
        Get the entire configuration.

        Returns:
            Dict: The entire configuration.
        """
        return self._config.copy()
