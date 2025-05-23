"""
Tests for the command-line interface module.

This module contains tests for the CLI functionality in the
annotation_toolkit.cli module.
"""

import argparse
import sys
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

from annotation_toolkit.cli import create_parser, execute_command, main
from annotation_toolkit.config import Config
from annotation_toolkit.utils.errors import ProcessingError


class TestCLI(unittest.TestCase):
    """Test cases for the CLI module."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = create_parser()

    def test_create_parser(self):
        """Test that the argument parser is created correctly."""
        self.assertIsInstance(self.parser, argparse.ArgumentParser)

        # Check that the expected subparsers are present
        subparsers_action = None
        for action in self.parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                subparsers_action = action
                break

        self.assertIsNotNone(subparsers_action, "No subparsers found")

        # Check that the expected commands are available
        commands = list(subparsers_action.choices.keys())
        self.assertIn("dict2bullet", commands)
        self.assertIn("jsonvis", commands)
        self.assertIn("textclean", commands)
        self.assertIn("gui", commands)

    def test_parser_dict2bullet_args(self):
        """Test parsing dict2bullet command arguments."""
        args = self.parser.parse_args(["dict2bullet", "input.json"])
        self.assertEqual(args.command, "dict2bullet")
        self.assertEqual(args.input_file, "input.json")
        self.assertIsNone(args.output)
        self.assertEqual(args.format, "markdown")

        # Test with optional arguments
        args = self.parser.parse_args(["dict2bullet", "input.json", "--output", "output.md", "--format", "text"])
        self.assertEqual(args.output, "output.md")
        self.assertEqual(args.format, "text")

    def test_parser_jsonvis_args(self):
        """Test parsing jsonvis command arguments."""
        args = self.parser.parse_args(["jsonvis", "input.json"])
        self.assertEqual(args.command, "jsonvis")
        self.assertEqual(args.input_file, "input.json")
        self.assertIsNone(args.output)
        self.assertEqual(args.format, "text")
        self.assertIsNone(args.search)
        self.assertFalse(args.case_sensitive)

        # Test with optional arguments
        args = self.parser.parse_args([
            "jsonvis", "input.json",
            "--output", "output.md",
            "--format", "markdown",
            "--search", "query",
            "--case-sensitive"
        ])
        self.assertEqual(args.output, "output.md")
        self.assertEqual(args.format, "markdown")
        self.assertEqual(args.search, "query")
        self.assertTrue(args.case_sensitive)

    def test_parser_textclean_args(self):
        """Test parsing textclean command arguments."""
        args = self.parser.parse_args(["textclean", "input.txt"])
        self.assertEqual(args.command, "textclean")
        self.assertEqual(args.input_file, "input.txt")
        self.assertIsNone(args.output)
        self.assertEqual(args.format, "markdown")

        # Test with optional arguments
        args = self.parser.parse_args(["textclean", "input.txt", "--output", "output.txt", "--format", "json"])
        self.assertEqual(args.output, "output.txt")
        self.assertEqual(args.format, "json")

    def test_parser_gui_args(self):
        """Test parsing gui command arguments."""
        args = self.parser.parse_args(["gui"])
        self.assertEqual(args.command, "gui")

    def test_parser_config_arg(self):
        """Test parsing the config argument."""
        args = self.parser.parse_args(["--config", "config.yaml", "gui"])
        self.assertEqual(args.config, "config.yaml")
        self.assertEqual(args.command, "gui")

    @patch("annotation_toolkit.cli.run_dict_to_bullet_command")
    def test_execute_command_dict2bullet(self, mock_run_command):
        """Test executing the dict2bullet command."""
        mock_run_command.return_value = 0

        args = argparse.Namespace(
            command="dict2bullet",
            input_file="input.json",
            output=None,
            format="markdown"
        )
        config = Config()

        result = execute_command(args, config)

        self.assertEqual(result, 0)
        mock_run_command.assert_called_once_with(args, config)

    @patch("annotation_toolkit.cli.run_json_visualizer_command")
    def test_execute_command_jsonvis(self, mock_run_command):
        """Test executing the jsonvis command."""
        mock_run_command.return_value = 0

        args = argparse.Namespace(
            command="jsonvis",
            input_file="input.json",
            output=None,
            format="text",
            search=None,
            case_sensitive=False
        )
        config = Config()

        result = execute_command(args, config)

        self.assertEqual(result, 0)
        mock_run_command.assert_called_once_with(args, config)

    @patch("annotation_toolkit.cli.run_text_cleaner_command")
    def test_execute_command_textclean(self, mock_run_command):
        """Test executing the textclean command."""
        mock_run_command.return_value = 0

        args = argparse.Namespace(
            command="textclean",
            input_file="input.txt",
            output=None,
            format="markdown"
        )
        config = Config()

        result = execute_command(args, config)

        self.assertEqual(result, 0)
        mock_run_command.assert_called_once_with(args, config)

    @patch("annotation_toolkit.ui.gui.app.run_application")
    def test_execute_command_gui(self, mock_run_app):
        """Test executing the gui command."""
        mock_run_app.return_value = None

        args = argparse.Namespace(command="gui")
        config = Config()

        result = execute_command(args, config)

        self.assertEqual(result, 0)
        mock_run_app.assert_called_once()

    def test_execute_command_unknown(self):
        """Test executing an unknown command."""
        args = argparse.Namespace(command="unknown")
        config = Config()

        with self.assertRaises(ProcessingError):
            execute_command(args, config)

    @patch("annotation_toolkit.cli.create_parser")
    @patch("annotation_toolkit.cli.Config")
    @patch("annotation_toolkit.cli.execute_command")
    def test_main_with_command(self, mock_execute, mock_config, mock_create_parser):
        """Test the main function with a command."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_create_parser.return_value = mock_parser

        mock_args = MagicMock()
        mock_args.command = "dict2bullet"
        mock_args.config = None
        mock_parser.parse_args.return_value = mock_args

        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance

        mock_execute.return_value = 0

        # Call main with arguments
        result = main(["dict2bullet", "input.json"])

        # Check results
        self.assertEqual(result, 0)
        mock_create_parser.assert_called_once()
        mock_parser.parse_args.assert_called_once_with(["dict2bullet", "input.json"])
        mock_config.assert_called_once()
        mock_execute.assert_called_once_with(mock_args, mock_config_instance)

    @patch("annotation_toolkit.cli.create_parser")
    def test_main_no_command(self, mock_create_parser):
        """Test the main function with no command."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_create_parser.return_value = mock_parser

        mock_args = MagicMock()
        mock_args.command = None
        mock_parser.parse_args.return_value = mock_args

        # Call main with no command
        result = main([])

        # Check results
        self.assertEqual(result, 0)
        mock_create_parser.assert_called_once()
        mock_parser.parse_args.assert_called_once_with([])
        mock_parser.print_help.assert_called_once()

    @patch("annotation_toolkit.cli.create_parser")
    @patch("annotation_toolkit.cli.Config")
    def test_main_config_error(self, mock_config, mock_create_parser):
        """Test the main function with a configuration error."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_create_parser.return_value = mock_parser

        mock_args = MagicMock()
        mock_args.command = "dict2bullet"
        mock_args.config = "config.yaml"
        mock_parser.parse_args.return_value = mock_args

        # Make Config raise an exception
        from annotation_toolkit.utils.errors import ConfigurationError
        mock_config.side_effect = ConfigurationError("Test error")

        # Redirect stderr to capture output
        stderr_backup = sys.stderr
        sys.stderr = StringIO()

        try:
            # Call main
            result = main(["dict2bullet", "input.json"])

            # Check results
            self.assertEqual(result, 1)
            self.assertIn("Error loading configuration", sys.stderr.getvalue())
        finally:
            # Restore stderr
            sys.stderr = stderr_backup

    @patch("annotation_toolkit.cli.create_parser")
    @patch("annotation_toolkit.cli.Config")
    @patch("annotation_toolkit.cli.execute_command")
    def test_main_command_error(self, mock_execute, mock_config, mock_create_parser):
        """Test the main function with a command execution error."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_create_parser.return_value = mock_parser

        mock_args = MagicMock()
        mock_args.command = "dict2bullet"
        mock_args.config = None
        mock_parser.parse_args.return_value = mock_args

        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance

        # Make execute_command raise an exception
        from annotation_toolkit.utils.errors import ProcessingError
        mock_execute.side_effect = ProcessingError("Test error")

        # Redirect stderr to capture output
        stderr_backup = sys.stderr
        sys.stderr = StringIO()

        try:
            # Call main
            result = main(["dict2bullet", "input.json"])

            # Check results
            self.assertEqual(result, 1)
            self.assertIn("Error:", sys.stderr.getvalue())
        finally:
            # Restore stderr
            sys.stderr = stderr_backup


if __name__ == "__main__":
    unittest.main()
