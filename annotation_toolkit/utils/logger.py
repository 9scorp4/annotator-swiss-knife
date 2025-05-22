"""
Logger module for the annotation toolkit.

This module provides a logger component that can be used throughout the application
to log messages at different levels (info, debug, error, warning, exception).
Log files are named after the date and time of the operation.
"""

import datetime
import logging
import os
from pathlib import Path


class Logger:
    """
    Logger class for the annotation toolkit.

    This class provides methods for logging messages at different levels
    (info, debug, error, warning, exception). Log files are named after
    the date and time of the operation.
    """

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """Singleton pattern to ensure only one logger instance exists."""
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self, log_dir=None, log_level=logging.INFO):
        """
        Initialize the logger.

        Args:
            log_dir (str, optional): Directory where log files will be stored.
                If None, logs will be stored in a 'logs' directory in the current working directory.
            log_level (int, optional): Logging level. Defaults to logging.INFO.
        """
        # Only initialize once (singleton pattern)
        if Logger._initialized:
            return

        # Set up log directory
        if log_dir is None:
            # Default to a 'logs' directory in the current working directory
            self.log_dir = os.path.join(os.getcwd(), "logs")
        else:
            self.log_dir = log_dir

        # Create log directory if it doesn't exist
        os.makedirs(self.log_dir, exist_ok=True)

        # Generate log filename based on current date and time
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"annotator_{timestamp}.log"
        self.log_path = os.path.join(self.log_dir, log_filename)

        # Configure logger
        self.logger = logging.getLogger("annotation_toolkit")
        self.logger.setLevel(log_level)

        # Create file handler
        file_handler = logging.FileHandler(self.log_path)
        file_handler.setLevel(log_level)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        # Create formatter and add it to the handlers
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        Logger._initialized = True

    def info(self, message):
        """
        Log an info message.

        Args:
            message (str): The message to log.
        """
        self.logger.info(message)

    def debug(self, message):
        """
        Log a debug message.

        Args:
            message (str): The message to log.
        """
        self.logger.debug(message)

    def warning(self, message):
        """
        Log a warning message.

        Args:
            message (str): The message to log.
        """
        self.logger.warning(message)

    def error(self, message):
        """
        Log an error message.

        Args:
            message (str): The message to log.
        """
        self.logger.error(message)

    def exception(self, message):
        """
        Log an exception message with traceback.

        Args:
            message (str): The message to log.
        """
        self.logger.exception(message)

    def get_log_path(self):
        """
        Get the path to the current log file.

        Returns:
            str: Path to the current log file.
        """
        return self.log_path


# Create a default logger instance
logger = Logger()


def get_logger(log_dir=None, log_level=None):
    """
    Get the logger instance.

    Args:
        log_dir (str, optional): Directory where log files will be stored.
        log_level (int, optional): Logging level.

    Returns:
        Logger: The logger instance.
    """
    if log_dir is not None or log_level is not None:
        # If parameters are provided, reinitialize the logger
        current_level = log_level if log_level is not None else logging.INFO
        return Logger(log_dir=log_dir, log_level=current_level)
    return logger
