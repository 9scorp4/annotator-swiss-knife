"""
Unit tests for CLI command implementations.

This module tests the command execution functions for dict2bullet, jsonvis,
textclean, convgen, and textcollector commands.
"""

import argparse
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from annotation_toolkit.config import Config
from annotation_toolkit.ui.cli.commands import (
    run_dict_to_bullet_command,
    run_json_visualizer_command,
    run_text_cleaner_command,
    run_conversation_generator_command,
    run_text_collector_command
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


class TestDictToBulletCommand(unittest.TestCase):
    """Test run_dict_to_bullet_command."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_commands_")
        self.config = Config()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_dict_to_bullet_successful_execution(self):
        """Test successful dict_to_bullet command execution."""
        # Create test input file
        input_data = {"key1": "value1", "key2": "value2"}
        input_file = os.path.join(self.test_dir, "input.json")
        with open(input_file, "w") as f:
            json.dump(input_data, f)

        # Create args
        args = argparse.Namespace(
            input_file=input_file,
            output=None,  # Print to stdout
            format="text"
        )

        # Run command
        exit_code = run_dict_to_bullet_command(args, self.config)

        self.assertEqual(exit_code, 0)

    def test_dict_to_bullet_with_output_file(self):
        """Test dict_to_bullet command with output file."""
        # Create test input file
        input_data = {"key1": "value1", "key2": "value2"}
        input_file = os.path.join(self.test_dir, "input.json")
        with open(input_file, "w") as f:
            json.dump(input_data, f)

        output_file = os.path.join(self.test_dir, "output.txt")

        # Create args
        args = argparse.Namespace(
            input_file=input_file,
            output=output_file,
            format="text"
        )

        # Run command
        exit_code = run_dict_to_bullet_command(args, self.config)

        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists(output_file))

        # Verify output content
        with open(output_file, "r") as f:
            output = f.read()
        self.assertIn("key1", output)
        self.assertIn("value1", output)

    def test_dict_to_bullet_markdown_format(self):
        """Test dict_to_bullet command with markdown format."""
        # Create test input file
        input_data = {"key1": "value1"}
        input_file = os.path.join(self.test_dir, "input.json")
        with open(input_file, "w") as f:
            json.dump(input_data, f)

        output_file = os.path.join(self.test_dir, "output.md")

        # Create args
        args = argparse.Namespace(
            input_file=input_file,
            output=output_file,
            format="markdown"
        )

        # Run command
        exit_code = run_dict_to_bullet_command(args, self.config)

        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists(output_file))

    def test_dict_to_bullet_file_not_found(self):
        """Test dict_to_bullet command with non-existent file."""
        args = argparse.Namespace(
            input_file="nonexistent.json",
            output=None,
            format="text"
        )

        exit_code = run_dict_to_bullet_command(args, self.config)

        self.assertEqual(exit_code, 1)

    def test_dict_to_bullet_invalid_json(self):
        """Test dict_to_bullet command with invalid JSON."""
        # Create invalid JSON file
        input_file = os.path.join(self.test_dir, "invalid.json")
        with open(input_file, "w") as f:
            f.write("not valid json {")

        args = argparse.Namespace(
            input_file=input_file,
            output=None,
            format="text"
        )

        exit_code = run_dict_to_bullet_command(args, self.config)

        self.assertEqual(exit_code, 1)

    def test_dict_to_bullet_invalid_input_type(self):
        """Test dict_to_bullet command with non-dictionary input."""
        # Create JSON array instead of dictionary
        input_data = ["item1", "item2"]
        input_file = os.path.join(self.test_dir, "array.json")
        with open(input_file, "w") as f:
            json.dump(input_data, f)

        args = argparse.Namespace(
            input_file=input_file,
            output=None,
            format="text"
        )

        exit_code = run_dict_to_bullet_command(args, self.config)

        self.assertEqual(exit_code, 1)


class TestJsonVisualizerCommand(unittest.TestCase):
    """Test run_json_visualizer_command."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_commands_")
        self.config = Config()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_json_visualizer_successful_execution(self):
        """Test successful json_visualizer command execution."""
        # Create test conversation file
        conversation = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        input_file = os.path.join(self.test_dir, "conversation.json")
        with open(input_file, "w") as f:
            json.dump(conversation, f)

        args = argparse.Namespace(
            input_file=input_file,
            output=None,
            format="text",
            search=None,
            case_sensitive=False
        )

        exit_code = run_json_visualizer_command(args, self.config)

        self.assertEqual(exit_code, 0)

    def test_json_visualizer_with_output_file(self):
        """Test json_visualizer command with output file."""
        # Create test conversation file
        conversation = [
            {"role": "user", "content": "Test message"}
        ]
        input_file = os.path.join(self.test_dir, "conversation.json")
        with open(input_file, "w") as f:
            json.dump(conversation, f)

        output_file = os.path.join(self.test_dir, "output.txt")

        args = argparse.Namespace(
            input_file=input_file,
            output=output_file,
            format="text",
            search=None,
            case_sensitive=False
        )

        exit_code = run_json_visualizer_command(args, self.config)

        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists(output_file))

    def test_json_visualizer_with_search(self):
        """Test json_visualizer command with search."""
        # Create test conversation file
        conversation = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "World"}
        ]
        input_file = os.path.join(self.test_dir, "conversation.json")
        with open(input_file, "w") as f:
            json.dump(conversation, f)

        args = argparse.Namespace(
            input_file=input_file,
            output=None,
            format="text",
            search="Hello",
            case_sensitive=False
        )

        exit_code = run_json_visualizer_command(args, self.config)

        self.assertEqual(exit_code, 0)

    def test_json_visualizer_search_no_matches(self):
        """Test json_visualizer search with no matches."""
        # Create test conversation file
        conversation = [
            {"role": "user", "content": "Hello"}
        ]
        input_file = os.path.join(self.test_dir, "conversation.json")
        with open(input_file, "w") as f:
            json.dump(conversation, f)

        args = argparse.Namespace(
            input_file=input_file,
            output=None,
            format="text",
            search="nonexistent",
            case_sensitive=False
        )

        exit_code = run_json_visualizer_command(args, self.config)

        self.assertEqual(exit_code, 0)

    def test_json_visualizer_file_not_found(self):
        """Test json_visualizer command with non-existent file."""
        args = argparse.Namespace(
            input_file="nonexistent.json",
            output=None,
            format="text",
            search=None,
            case_sensitive=False
        )

        exit_code = run_json_visualizer_command(args, self.config)

        self.assertEqual(exit_code, 1)


class TestTextCleanerCommand(unittest.TestCase):
    """Test run_text_cleaner_command."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_commands_")
        self.config = Config()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_text_cleaner_successful_execution(self):
        """Test successful text_cleaner command execution."""
        # Create test text file
        input_text = "This is   test text\nwith  multiple   spaces"
        input_file = os.path.join(self.test_dir, "input.txt")
        with open(input_file, "w") as f:
            f.write(input_text)

        args = argparse.Namespace(
            input_file=input_file,
            output=None,
            format="text"
        )

        exit_code = run_text_cleaner_command(args, self.config)

        self.assertEqual(exit_code, 0)

    def test_text_cleaner_with_output_file(self):
        """Test text_cleaner command with output file."""
        # Create test text file
        input_text = "Test text"
        input_file = os.path.join(self.test_dir, "input.txt")
        with open(input_file, "w") as f:
            f.write(input_text)

        output_file = os.path.join(self.test_dir, "output.txt")

        args = argparse.Namespace(
            input_file=input_file,
            output=output_file,
            format="text"
        )

        exit_code = run_text_cleaner_command(args, self.config)

        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists(output_file))

    def test_text_cleaner_file_not_found(self):
        """Test text_cleaner command with non-existent file."""
        args = argparse.Namespace(
            input_file="nonexistent.txt",
            output=None,
            format="text"
        )

        exit_code = run_text_cleaner_command(args, self.config)

        self.assertEqual(exit_code, 1)


class TestConversationGeneratorCommand(unittest.TestCase):
    """Test run_conversation_generator_command."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_commands_")
        self.config = Config()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_conversation_generator_successful_execution(self):
        """Test successful conversation_generator command execution."""
        # Create test input file
        input_data = {
            "turns": [
                {"user": "Hello", "assistant": "Hi there!"},
                {"user": "How are you?", "assistant": "I'm good!"}
            ]
        }
        input_file = os.path.join(self.test_dir, "input.json")
        with open(input_file, "w") as f:
            json.dump(input_data, f)

        args = argparse.Namespace(
            input_file=input_file,
            output=None,
            format="compact"
        )

        exit_code = run_conversation_generator_command(args, self.config)

        self.assertEqual(exit_code, 0)

    def test_conversation_generator_with_output_file(self):
        """Test conversation_generator command with output file."""
        # Create test input file
        input_data = {
            "turns": [
                {"user": "Test", "assistant": "Response"}
            ]
        }
        input_file = os.path.join(self.test_dir, "input.json")
        with open(input_file, "w") as f:
            json.dump(input_data, f)

        output_file = os.path.join(self.test_dir, "output.json")

        args = argparse.Namespace(
            input_file=input_file,
            output=output_file,
            format="pretty"
        )

        exit_code = run_conversation_generator_command(args, self.config)

        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists(output_file))

        # Verify output is valid JSON
        with open(output_file, "r") as f:
            output_data = json.load(f)
        self.assertIsInstance(output_data, list)

    def test_conversation_generator_pretty_format(self):
        """Test conversation_generator with pretty format."""
        # Create test input file
        input_data = {
            "turns": [
                {"user": "Test", "assistant": "Response"}
            ]
        }
        input_file = os.path.join(self.test_dir, "input.json")
        with open(input_file, "w") as f:
            json.dump(input_data, f)

        output_file = os.path.join(self.test_dir, "output.json")

        args = argparse.Namespace(
            input_file=input_file,
            output=output_file,
            format="pretty"
        )

        exit_code = run_conversation_generator_command(args, self.config)

        self.assertEqual(exit_code, 0)

        # Pretty format should have indentation
        with open(output_file, "r") as f:
            content = f.read()
        self.assertIn("  ", content)  # Has indentation

    def test_conversation_generator_file_not_found(self):
        """Test conversation_generator command with non-existent file."""
        args = argparse.Namespace(
            input_file="nonexistent.json",
            output=None,
            format="compact"
        )

        exit_code = run_conversation_generator_command(args, self.config)

        self.assertEqual(exit_code, 1)

    def test_conversation_generator_invalid_json(self):
        """Test conversation_generator command with invalid JSON."""
        # Create invalid JSON file
        input_file = os.path.join(self.test_dir, "invalid.json")
        with open(input_file, "w") as f:
            f.write("not valid json")

        args = argparse.Namespace(
            input_file=input_file,
            output=None,
            format="compact"
        )

        exit_code = run_conversation_generator_command(args, self.config)

        self.assertEqual(exit_code, 1)

    def test_conversation_generator_missing_turns(self):
        """Test conversation_generator with missing turns field."""
        # Create input without 'turns' field
        input_data = {"data": "no turns here"}
        input_file = os.path.join(self.test_dir, "input.json")
        with open(input_file, "w") as f:
            json.dump(input_data, f)

        args = argparse.Namespace(
            input_file=input_file,
            output=None,
            format="compact"
        )

        exit_code = run_conversation_generator_command(args, self.config)

        self.assertEqual(exit_code, 1)

    def test_conversation_generator_invalid_turn_format(self):
        """Test conversation_generator with invalid turn format."""
        # Create input with invalid turn (missing assistant field)
        input_data = {
            "turns": [
                {"user": "Hello"}  # Missing assistant field
            ]
        }
        input_file = os.path.join(self.test_dir, "input.json")
        with open(input_file, "w") as f:
            json.dump(input_data, f)

        args = argparse.Namespace(
            input_file=input_file,
            output=None,
            format="compact"
        )

        exit_code = run_conversation_generator_command(args, self.config)

        self.assertEqual(exit_code, 1)


class TestTextCollectorCommand(unittest.TestCase):
    """Test run_text_collector_command."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_commands_")
        self.config = Config()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_text_collector_successful_execution(self):
        """Test successful text_collector command execution."""
        # Create test text file
        input_text = "line1\nline2\nline3"
        input_file = os.path.join(self.test_dir, "input.txt")
        with open(input_file, "w") as f:
            f.write(input_text)

        args = argparse.Namespace(
            input_file=input_file,
            output=None,
            format="compact"
        )

        exit_code = run_text_collector_command(args, self.config)

        self.assertEqual(exit_code, 0)

    def test_text_collector_with_output_file(self):
        """Test text_collector command with output file."""
        # Create test text file
        input_text = "item1\nitem2\nitem3"
        input_file = os.path.join(self.test_dir, "input.txt")
        with open(input_file, "w") as f:
            f.write(input_text)

        output_file = os.path.join(self.test_dir, "output.json")

        args = argparse.Namespace(
            input_file=input_file,
            output=output_file,
            format="pretty"
        )

        exit_code = run_text_collector_command(args, self.config)

        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists(output_file))

        # Verify output is valid JSON array
        with open(output_file, "r") as f:
            output_data = json.load(f)
        self.assertIsInstance(output_data, list)
        self.assertEqual(len(output_data), 3)

    def test_text_collector_filters_empty_lines(self):
        """Test text_collector filters out empty lines."""
        # Create test text file with empty lines
        input_text = "line1\n\nline2\n\n\nline3"
        input_file = os.path.join(self.test_dir, "input.txt")
        with open(input_file, "w") as f:
            f.write(input_text)

        output_file = os.path.join(self.test_dir, "output.json")

        args = argparse.Namespace(
            input_file=input_file,
            output=output_file,
            format="compact"
        )

        exit_code = run_text_collector_command(args, self.config)

        self.assertEqual(exit_code, 0)

        # Should only have 3 non-empty lines
        with open(output_file, "r") as f:
            output_data = json.load(f)
        self.assertEqual(len(output_data), 3)

    def test_text_collector_file_not_found(self):
        """Test text_collector command with non-existent file."""
        args = argparse.Namespace(
            input_file="nonexistent.txt",
            output=None,
            format="compact"
        )

        exit_code = run_text_collector_command(args, self.config)

        self.assertEqual(exit_code, 1)


class TestCommandsEdgeCases(unittest.TestCase):
    """Test edge cases for all commands."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_commands_")
        self.config = Config()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_output_creates_parent_directories(self):
        """Test that output file creation creates parent directories."""
        # Create test input file
        input_data = {"key": "value"}
        input_file = os.path.join(self.test_dir, "input.json")
        with open(input_file, "w") as f:
            json.dump(input_data, f)

        # Output to nested directory that doesn't exist
        output_file = os.path.join(self.test_dir, "nested", "dir", "output.txt")

        args = argparse.Namespace(
            input_file=input_file,
            output=output_file,
            format="text"
        )

        exit_code = run_dict_to_bullet_command(args, self.config)

        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists(output_file))

    def test_unicode_handling(self):
        """Test commands handle unicode characters."""
        # Create test file with unicode
        input_data = {"unicode": "ñ, é, 中文, 🎉"}
        input_file = os.path.join(self.test_dir, "unicode.json")
        with open(input_file, "w", encoding="utf-8") as f:
            json.dump(input_data, f, ensure_ascii=False)

        output_file = os.path.join(self.test_dir, "output.txt")

        args = argparse.Namespace(
            input_file=input_file,
            output=output_file,
            format="text"
        )

        exit_code = run_dict_to_bullet_command(args, self.config)

        self.assertEqual(exit_code, 0)

        # Verify unicode preserved
        with open(output_file, "r", encoding="utf-8") as f:
            output = f.read()
        self.assertIn("🎉", output)


class TestCommandsIntegration(unittest.TestCase):
    """Integration tests for CLI commands."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_commands_integration_")
        self.config = Config()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_command_workflow_dict_to_bullet(self):
        """Test complete workflow for dict_to_bullet command."""
        # Create input
        input_data = {
            "feature1": "description1",
            "feature2": "description2"
        }
        input_file = os.path.join(self.test_dir, "features.json")
        with open(input_file, "w") as f:
            json.dump(input_data, f)

        # Run command with output
        output_file = os.path.join(self.test_dir, "features.md")
        args = argparse.Namespace(
            input_file=input_file,
            output=output_file,
            format="markdown"
        )

        exit_code = run_dict_to_bullet_command(args, self.config)

        # Verify success
        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists(output_file))

        # Verify content
        with open(output_file, "r") as f:
            content = f.read()
        self.assertIn("feature1", content)
        self.assertIn("description1", content)

    def test_command_workflow_conversation_generator(self):
        """Test complete workflow for conversation_generator command."""
        # Create input with multiple turns
        input_data = {
            "turns": [
                {"user": "What is Python?", "assistant": "Python is a programming language."},
                {"user": "What are its features?", "assistant": "It has many features."},
                {"user": "Can you give examples?", "assistant": "Sure, here are examples."}
            ]
        }
        input_file = os.path.join(self.test_dir, "conversation_turns.json")
        with open(input_file, "w") as f:
            json.dump(input_data, f)

        # Run command
        output_file = os.path.join(self.test_dir, "conversation_output.json")
        args = argparse.Namespace(
            input_file=input_file,
            output=output_file,
            format="pretty"
        )

        exit_code = run_conversation_generator_command(args, self.config)

        # Verify success
        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists(output_file))

        # Verify output structure
        with open(output_file, "r") as f:
            conversation = json.load(f)

        self.assertIsInstance(conversation, list)
        self.assertEqual(len(conversation), 6)  # 3 turns = 6 messages

        # Verify alternating roles
        for i, msg in enumerate(conversation):
            expected_role = "user" if i % 2 == 0 else "assistant"
            self.assertEqual(msg["role"], expected_role)


if __name__ == "__main__":
    unittest.main()
