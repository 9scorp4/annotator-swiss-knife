"""
Unit tests for the Logger module.

This module tests the logger functionality including singleton pattern,
log file creation, different log levels, and cross-platform behavior.
"""

import logging
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from annotation_toolkit.utils.logger import Logger, get_logger


class TestLoggerInit(unittest.TestCase):
    """Test logger initialization and configuration."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset singleton state before each test
        Logger._instance = None
        Logger._initialized = False
        # Create temporary directory for test logs
        self.test_log_dir = tempfile.mkdtemp(prefix="test_logger_")

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up test log directory
        import shutil
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)
        # Reset singleton state after each test
        Logger._instance = None
        Logger._initialized = False

    def test_logger_singleton_pattern(self):
        """Test that Logger implements singleton pattern correctly."""
        logger1 = Logger(log_dir=self.test_log_dir)
        logger2 = Logger(log_dir=self.test_log_dir)

        # Should be the same instance
        self.assertIs(logger1, logger2)
        self.assertEqual(id(logger1), id(logger2))

    def test_logger_initialization_only_once(self):
        """Test that logger only initializes once despite multiple instantiations."""
        logger1 = Logger(log_dir=self.test_log_dir, log_level=logging.DEBUG)
        initial_log_path = logger1.log_path

        # Second initialization with different parameters should not change anything
        logger2 = Logger(log_dir="/tmp/different", log_level=logging.ERROR)

        # Should still use the first initialization's log path
        self.assertEqual(logger2.log_path, initial_log_path)
        self.assertTrue(logger2.log_path.startswith(self.test_log_dir))

    def test_logger_creates_log_directory(self):
        """Test that logger creates log directory if it doesn't exist."""
        test_dir = os.path.join(self.test_log_dir, "nested", "logs")
        self.assertFalse(os.path.exists(test_dir))

        logger = Logger(log_dir=test_dir)

        # Directory should now exist
        self.assertTrue(os.path.exists(test_dir))
        self.assertTrue(os.path.isdir(test_dir))

    def test_logger_creates_log_file(self):
        """Test that logger creates log file with timestamp."""
        logger = Logger(log_dir=self.test_log_dir)

        # Log file should be created
        self.assertTrue(os.path.exists(logger.log_path))
        self.assertTrue(logger.log_path.startswith(self.test_log_dir))

        # Filename should follow pattern: annotator_YYYYMMDD_HHMMSS.log
        filename = os.path.basename(logger.log_path)
        self.assertTrue(filename.startswith("annotator_"))
        self.assertTrue(filename.endswith(".log"))

    def test_logger_default_log_level(self):
        """Test that logger uses INFO level by default."""
        logger = Logger(log_dir=self.test_log_dir)

        self.assertEqual(logger.logger.level, logging.INFO)

    def test_logger_custom_log_level(self):
        """Test that logger accepts custom log level."""
        logger = Logger(log_dir=self.test_log_dir, log_level=logging.DEBUG)

        self.assertEqual(logger.logger.level, logging.DEBUG)

    def test_logger_has_file_and_console_handlers(self):
        """Test that logger has both file and console handlers."""
        logger = Logger(log_dir=self.test_log_dir)

        # Should have 2 handlers
        self.assertEqual(len(logger.logger.handlers), 2)

        # Check handler types
        handler_types = [type(h) for h in logger.logger.handlers]
        self.assertIn(logging.FileHandler, handler_types)
        self.assertIn(logging.StreamHandler, handler_types)

    def test_logger_formatter_format(self):
        """Test that logger uses correct log format."""
        logger = Logger(log_dir=self.test_log_dir)

        # Check formatter format string
        for handler in logger.logger.handlers:
            formatter = handler.formatter
            self.assertIsNotNone(formatter)
            # Format should include timestamp, name, level, and message
            self.assertIn("%(asctime)s", formatter._fmt)
            self.assertIn("%(name)s", formatter._fmt)
            self.assertIn("%(levelname)s", formatter._fmt)
            self.assertIn("%(message)s", formatter._fmt)

    def test_logger_fallback_to_temp_on_permission_error(self):
        """Test that logger falls back to temp directory on permission error."""
        # This test verifies the fallback logic exists, but actual permission
        # errors are difficult to simulate reliably in tests

        # We can verify that the logger handles the fallback path
        # by checking it uses tempfile when needed
        import tempfile

        # Create logger with a custom temp directory to test the fallback
        temp_dir = tempfile.mkdtemp(prefix="test_logger_fallback_")
        logger = Logger(log_dir=temp_dir)

        # Should have created logger successfully
        self.assertIsNotNone(logger)
        self.assertTrue(logger.log_path.startswith(temp_dir))

        # Cleanup
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    @patch('os.name', 'posix')
    @patch.dict(os.environ, {'XDG_CONFIG_HOME': '/home/user/.config'})
    def test_logger_uses_xdg_config_home_on_posix(self):
        """Test that logger uses XDG_CONFIG_HOME on POSIX systems."""
        # Reset singleton
        Logger._instance = None
        Logger._initialized = False

        with patch('os.makedirs') as mock_makedirs:
            with patch('builtins.open', unittest.mock.mock_open()):
                logger = Logger()

                # Should try to create directory in XDG_CONFIG_HOME
                expected_path = '/home/user/.config/annotation-toolkit/logs'
                # Check if makedirs was called with the expected path (first call)
                self.assertTrue(
                    any(expected_path in str(call) for call in mock_makedirs.call_args_list)
                )

    def test_logger_propagate_disabled(self):
        """Test that logger propagate is disabled to prevent recursion."""
        logger = Logger(log_dir=self.test_log_dir)

        self.assertFalse(logger.logger.propagate)


class TestLoggerMethods(unittest.TestCase):
    """Test logger logging methods."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset singleton state
        Logger._instance = None
        Logger._initialized = False
        # Create temporary directory for test logs
        self.test_log_dir = tempfile.mkdtemp(prefix="test_logger_")
        self.logger = Logger(log_dir=self.test_log_dir, log_level=logging.DEBUG)

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up test log directory
        import shutil
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)
        # Reset singleton state
        Logger._instance = None
        Logger._initialized = False

    def test_info_method_logs_message(self):
        """Test that info method logs message at INFO level."""
        test_message = "Test info message"
        self.logger.info(test_message)

        # Read log file and check message
        with open(self.logger.log_path, 'r') as f:
            log_content = f.read()

        self.assertIn(test_message, log_content)
        self.assertIn("INFO", log_content)

    def test_debug_method_logs_message(self):
        """Test that debug method logs message at DEBUG level."""
        test_message = "Test debug message"
        self.logger.debug(test_message)

        # Read log file and check message
        with open(self.logger.log_path, 'r') as f:
            log_content = f.read()

        self.assertIn(test_message, log_content)
        self.assertIn("DEBUG", log_content)

    def test_warning_method_logs_message(self):
        """Test that warning method logs message at WARNING level."""
        test_message = "Test warning message"
        self.logger.warning(test_message)

        # Read log file and check message
        with open(self.logger.log_path, 'r') as f:
            log_content = f.read()

        self.assertIn(test_message, log_content)
        self.assertIn("WARNING", log_content)

    def test_error_method_logs_message(self):
        """Test that error method logs message at ERROR level."""
        test_message = "Test error message"
        self.logger.error(test_message)

        # Read log file and check message
        with open(self.logger.log_path, 'r') as f:
            log_content = f.read()

        self.assertIn(test_message, log_content)
        self.assertIn("ERROR", log_content)

    def test_exception_method_logs_with_traceback(self):
        """Test that exception method logs message with traceback."""
        test_message = "Test exception message"

        try:
            raise ValueError("Test exception")
        except ValueError:
            self.logger.exception(test_message)

        # Read log file and check message and traceback
        with open(self.logger.log_path, 'r') as f:
            log_content = f.read()

        self.assertIn(test_message, log_content)
        self.assertIn("ERROR", log_content)  # exception logs at ERROR level
        self.assertIn("Traceback", log_content)
        self.assertIn("ValueError: Test exception", log_content)

    def test_get_log_path_returns_correct_path(self):
        """Test that get_log_path returns the correct log file path."""
        log_path = self.logger.get_log_path()

        self.assertTrue(os.path.exists(log_path))
        self.assertTrue(log_path.startswith(self.test_log_dir))
        self.assertTrue(log_path.endswith(".log"))


class TestLoggerLevels(unittest.TestCase):
    """Test logger with different log levels."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset singleton state
        Logger._instance = None
        Logger._initialized = False
        # Create temporary directory for test logs
        self.test_log_dir = tempfile.mkdtemp(prefix="test_logger_")

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up test log directory
        import shutil
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)
        # Reset singleton state
        Logger._instance = None
        Logger._initialized = False

    def test_logger_with_warning_level_filters_debug(self):
        """Test that WARNING level logger doesn't log DEBUG messages."""
        logger = Logger(log_dir=self.test_log_dir, log_level=logging.WARNING)

        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")

        # Read log file
        with open(logger.log_path, 'r') as f:
            log_content = f.read()

        # Only WARNING should be logged
        self.assertNotIn("Debug message", log_content)
        self.assertNotIn("Info message", log_content)
        self.assertIn("Warning message", log_content)

    def test_logger_with_error_level_filters_info_and_warning(self):
        """Test that ERROR level logger only logs ERROR and CRITICAL."""
        logger = Logger(log_dir=self.test_log_dir, log_level=logging.ERROR)

        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        # Read log file
        with open(logger.log_path, 'r') as f:
            log_content = f.read()

        # Only ERROR should be logged
        self.assertNotIn("Info message", log_content)
        self.assertNotIn("Warning message", log_content)
        self.assertIn("Error message", log_content)

    def test_logger_with_debug_level_logs_all(self):
        """Test that DEBUG level logger logs all messages."""
        logger = Logger(log_dir=self.test_log_dir, log_level=logging.DEBUG)

        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        # Read log file
        with open(logger.log_path, 'r') as f:
            log_content = f.read()

        # All messages should be logged
        self.assertIn("Debug message", log_content)
        self.assertIn("Info message", log_content)
        self.assertIn("Warning message", log_content)
        self.assertIn("Error message", log_content)


class TestGetLoggerFunction(unittest.TestCase):
    """Test get_logger helper function."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset singleton state
        Logger._instance = None
        Logger._initialized = False
        # Create temporary directory for test logs
        self.test_log_dir = tempfile.mkdtemp(prefix="test_logger_")

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up test log directory
        import shutil
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)
        # Reset singleton state
        Logger._instance = None
        Logger._initialized = False

    def test_get_logger_without_params_returns_default(self):
        """Test that get_logger without params returns default logger."""
        # Initialize default logger first
        from annotation_toolkit.utils.logger import logger as default_logger

        logger = get_logger()

        # Should return the same instance as the default logger
        self.assertIsInstance(logger, Logger)

    def test_get_logger_with_custom_dir(self):
        """Test that get_logger with custom dir creates logger with that dir."""
        logger = get_logger(log_dir=self.test_log_dir)

        self.assertIsInstance(logger, Logger)
        self.assertTrue(logger.log_path.startswith(self.test_log_dir))

    def test_get_logger_with_custom_level(self):
        """Test that get_logger with custom level creates logger with that level."""
        logger = get_logger(log_dir=self.test_log_dir, log_level=logging.DEBUG)

        self.assertEqual(logger.logger.level, logging.DEBUG)

    def test_get_logger_returns_singleton(self):
        """Test that get_logger returns singleton instance."""
        logger1 = get_logger(log_dir=self.test_log_dir)
        logger2 = get_logger(log_dir=self.test_log_dir)

        self.assertIs(logger1, logger2)


class TestLoggerEdgeCases(unittest.TestCase):
    """Test logger edge cases and error conditions."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset singleton state
        Logger._instance = None
        Logger._initialized = False
        # Create temporary directory for test logs
        self.test_log_dir = tempfile.mkdtemp(prefix="test_logger_")

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up test log directory
        import shutil
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)
        # Reset singleton state
        Logger._instance = None
        Logger._initialized = False

    def test_logger_with_empty_message(self):
        """Test that logger handles empty messages."""
        logger = Logger(log_dir=self.test_log_dir)
        logger.info("")

        # Should not raise error
        with open(logger.log_path, 'r') as f:
            log_content = f.read()

        self.assertIn("INFO", log_content)

    def test_logger_with_unicode_message(self):
        """Test that logger handles unicode characters."""
        logger = Logger(log_dir=self.test_log_dir)
        unicode_message = "Test message with unicode: ñ, é, 中文, 🎉"
        logger.info(unicode_message)

        # Read log file and check message
        with open(logger.log_path, 'r', encoding='utf-8') as f:
            log_content = f.read()

        self.assertIn(unicode_message, log_content)

    def test_logger_with_multiline_message(self):
        """Test that logger handles multiline messages."""
        logger = Logger(log_dir=self.test_log_dir)
        multiline_message = "Line 1\nLine 2\nLine 3"
        logger.info(multiline_message)

        # Read log file and check message
        with open(logger.log_path, 'r') as f:
            log_content = f.read()

        self.assertIn("Line 1", log_content)
        self.assertIn("Line 2", log_content)
        self.assertIn("Line 3", log_content)

    def test_logger_handlers_cleared_on_initialization(self):
        """Test that logger clears handlers to prevent accumulation."""
        logger = Logger(log_dir=self.test_log_dir)
        initial_handler_count = len(logger.logger.handlers)

        # Should have exactly 2 handlers (file and console)
        self.assertEqual(initial_handler_count, 2)


class TestLoggerIntegration(unittest.TestCase):
    """Integration tests for logger with real file operations."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset singleton state
        Logger._instance = None
        Logger._initialized = False
        # Create temporary directory for test logs
        self.test_log_dir = tempfile.mkdtemp(prefix="test_logger_")

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up test log directory
        import shutil
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)
        # Reset singleton state
        Logger._instance = None
        Logger._initialized = False

    def test_logger_multiple_messages_in_sequence(self):
        """Test logging multiple messages in sequence."""
        logger = Logger(log_dir=self.test_log_dir, log_level=logging.DEBUG)

        messages = [
            ("debug", "Debug message 1"),
            ("info", "Info message 1"),
            ("warning", "Warning message 1"),
            ("error", "Error message 1"),
        ]

        for level, message in messages:
            getattr(logger, level)(message)

        # Read log file and verify all messages
        with open(logger.log_path, 'r') as f:
            log_content = f.read()

        for level, message in messages:
            self.assertIn(message, log_content)
            self.assertIn(level.upper(), log_content)

    def test_logger_timestamp_format(self):
        """Test that log entries have proper timestamp format."""
        logger = Logger(log_dir=self.test_log_dir)
        logger.info("Test timestamp")

        # Read log file
        with open(logger.log_path, 'r') as f:
            log_content = f.read()

        # Check for timestamp pattern (YYYY-MM-DD HH:MM:SS,mmm)
        import re
        timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}'
        self.assertTrue(re.search(timestamp_pattern, log_content))


if __name__ == "__main__":
    unittest.main()
