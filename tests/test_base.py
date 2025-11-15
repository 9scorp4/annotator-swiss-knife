"""
Comprehensive tests for the base classes in the annotation toolkit.

This module contains comprehensive tests for the abstract base classes and interfaces
defined in the annotation_toolkit.core.base module, achieving 90%+ code coverage.
"""

import unittest
from unittest.mock import MagicMock, patch, call
from abc import ABC

from annotation_toolkit.core.base import (
    AnnotationTool,
    TextAnnotationTool,
    JsonAnnotationTool,
    ToolConfigurationError,
    ToolExecutionError
)
from annotation_toolkit.utils.errors import ProcessingError, TypeValidationError


class TestAnnotationTool(unittest.TestCase):
    """Test cases for the AnnotationTool abstract base class."""

    def test_annotation_tool_is_abstract(self):
        """Test that AnnotationTool cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            AnnotationTool()

    def test_annotation_tool_is_abc(self):
        """Test that AnnotationTool is an ABC."""
        self.assertTrue(issubclass(AnnotationTool, ABC))

    def test_annotation_tool_has_abstract_methods(self):
        """Test that AnnotationTool has required abstract methods."""
        abstract_methods = AnnotationTool.__abstractmethods__
        self.assertIn('name', abstract_methods)
        self.assertIn('description', abstract_methods)
        self.assertIn('process', abstract_methods)

    @patch('annotation_toolkit.core.base.logger')
    def test_annotation_tool_init_logging(self, mock_logger):
        """Test that tool initialization logs debug message."""
        class ConcreteTool(AnnotationTool):
            @property
            def name(self):
                return "Test"

            @property
            def description(self):
                return "Test Description"

            def process(self, data):
                return data

        tool = ConcreteTool()
        mock_logger.debug.assert_called_once()
        self.assertIn("ConcreteTool", str(mock_logger.debug.call_args))


class ConcreteTextAnnotationTool(TextAnnotationTool):
    """A concrete implementation of TextAnnotationTool for testing."""

    @property
    def name(self):
        return "Test Text Tool"

    @property
    def description(self):
        return "A test implementation of TextAnnotationTool"

    def process_text(self, text):
        return f"Processed: {text}"


class TestTextAnnotationTool(unittest.TestCase):
    """Test cases for the TextAnnotationTool base class."""

    def setUp(self):
        """Set up test fixtures."""
        self.tool = ConcreteTextAnnotationTool()

    def test_inherits_from_annotation_tool(self):
        """Test that TextAnnotationTool inherits from AnnotationTool."""
        self.assertIsInstance(self.tool, AnnotationTool)

    def test_text_annotation_tool_is_abstract(self):
        """Test that TextAnnotationTool cannot be instantiated without implementing process_text."""
        class IncompleteTextTool(TextAnnotationTool):
            @property
            def name(self):
                return "Incomplete"

            @property
            def description(self):
                return "Incomplete tool"

        with self.assertRaises(TypeError):
            IncompleteTextTool()

    def test_name_property(self):
        """Test that name property returns correct value."""
        self.assertEqual(self.tool.name, "Test Text Tool")

    def test_description_property(self):
        """Test that description property returns correct value."""
        self.assertEqual(self.tool.description, "A test implementation of TextAnnotationTool")

    def test_process_calls_process_text(self):
        """Test that process() calls process_text() with the input data converted to string."""
        result = self.tool.process("test")
        self.assertEqual(result, "Processed: test")

    def test_process_with_non_string_input(self):
        """Test that process() converts non-string input to string."""
        result = self.tool.process(123)
        self.assertEqual(result, "Processed: 123")

    def test_process_with_none(self):
        """Test that process() handles None input."""
        result = self.tool.process(None)
        self.assertEqual(result, "Processed: None")

    def test_process_with_empty_string(self):
        """Test that process() handles empty string."""
        result = self.tool.process("")
        self.assertEqual(result, "Processed: ")

    def test_process_with_boolean(self):
        """Test that process() converts boolean to string."""
        result = self.tool.process(True)
        self.assertEqual(result, "Processed: True")

    def test_process_with_list(self):
        """Test that process() converts list to string."""
        result = self.tool.process([1, 2, 3])
        self.assertEqual(result, "Processed: [1, 2, 3]")

    def test_process_with_dict(self):
        """Test that process() converts dict to string."""
        result = self.tool.process({"key": "value"})
        self.assertIn("Processed:", result)

    @patch('annotation_toolkit.core.base.logger')
    def test_process_logs_info(self, mock_logger):
        """Test that process() logs info message."""
        self.tool.process("test")
        mock_logger.info.assert_called_once()
        call_args = str(mock_logger.info.call_args)
        self.assertIn("Processing text data", call_args)

    @patch('annotation_toolkit.core.base.logger')
    def test_process_logs_debug_on_success(self, mock_logger):
        """Test that process() logs debug message on success."""
        self.tool.process("test")
        # Should have debug call for success
        debug_calls = [call for call in mock_logger.debug.call_args_list
                      if 'completed successfully' in str(call)]
        self.assertGreater(len(debug_calls), 0)

    @patch('annotation_toolkit.core.base.logger')
    def test_process_logs_exception_on_error(self, mock_logger):
        """Test that process() logs exception on error."""
        with patch.object(self.tool, 'process_text', side_effect=ValueError("Test error")):
            with self.assertRaises(ProcessingError):
                self.tool.process("test")

        mock_logger.exception.assert_called_once()

    def test_process_handles_value_error(self):
        """Test that process() wraps ValueError in ProcessingError."""
        with patch.object(self.tool, 'process_text', side_effect=ValueError("Test error")):
            with self.assertRaises(ProcessingError) as context:
                self.tool.process("test")

            error = context.exception
            self.assertIsInstance(error.cause, ValueError)
            self.assertIn("Test error", error.message)

    def test_process_handles_runtime_error(self):
        """Test that process() handles RuntimeError."""
        with patch.object(self.tool, 'process_text', side_effect=RuntimeError("Runtime issue")):
            with self.assertRaises(ProcessingError) as context:
                self.tool.process("test")

            error = context.exception
            self.assertIsInstance(error.cause, RuntimeError)

    def test_process_error_includes_tool_name(self):
        """Test that ProcessingError includes tool name in details."""
        with patch.object(self.tool, 'process_text', side_effect=ValueError("Error")):
            with self.assertRaises(ProcessingError) as context:
                self.tool.process("test")

            error = context.exception
            self.assertIn("tool", error.details)
            self.assertEqual(error.details["tool"], "ConcreteTextAnnotationTool")

    def test_process_error_includes_data_type(self):
        """Test that ProcessingError includes data type in details."""
        with patch.object(self.tool, 'process_text', side_effect=ValueError("Error")):
            with self.assertRaises(ProcessingError) as context:
                self.tool.process(123)

            error = context.exception
            self.assertIn("data_type", error.details)
            self.assertEqual(error.details["data_type"], "int")

    def test_process_error_has_suggestion(self):
        """Test that ProcessingError includes helpful suggestion."""
        with patch.object(self.tool, 'process_text', side_effect=ValueError("Error")):
            with self.assertRaises(ProcessingError) as context:
                self.tool.process("test")

            error = context.exception
            self.assertIsNotNone(error.suggestion)
            self.assertIn("input text", error.suggestion.lower())


class ConcreteJsonAnnotationTool(JsonAnnotationTool):
    """A concrete implementation of JsonAnnotationTool for testing."""

    @property
    def name(self):
        return "Test JSON Tool"

    @property
    def description(self):
        return "A test implementation of JsonAnnotationTool"

    def process_json(self, json_data):
        return {"processed": json_data}


class TestJsonAnnotationTool(unittest.TestCase):
    """Test cases for the JsonAnnotationTool base class."""

    def setUp(self):
        """Set up test fixtures."""
        self.tool = ConcreteJsonAnnotationTool()

    def test_inherits_from_annotation_tool(self):
        """Test that JsonAnnotationTool inherits from AnnotationTool."""
        self.assertIsInstance(self.tool, AnnotationTool)

    def test_json_annotation_tool_is_abstract(self):
        """Test that JsonAnnotationTool cannot be instantiated without implementing process_json."""
        class IncompleteJsonTool(JsonAnnotationTool):
            @property
            def name(self):
                return "Incomplete"

            @property
            def description(self):
                return "Incomplete tool"

        with self.assertRaises(TypeError):
            IncompleteJsonTool()

    def test_name_property(self):
        """Test that name property returns correct value."""
        self.assertEqual(self.tool.name, "Test JSON Tool")

    def test_description_property(self):
        """Test that description property returns correct value."""
        self.assertEqual(self.tool.description, "A test implementation of JsonAnnotationTool")

    def test_process_calls_process_json_with_dict(self):
        """Test that process() calls process_json() with dict input."""
        result = self.tool.process({"test": "data"})
        self.assertEqual(result, {"processed": {"test": "data"}})

    def test_process_calls_process_json_with_list(self):
        """Test that process() calls process_json() with list input."""
        result = self.tool.process(["test", "data"])
        self.assertEqual(result, {"processed": ["test", "data"]})

    def test_process_with_empty_dict(self):
        """Test that process() handles empty dictionary."""
        result = self.tool.process({})
        self.assertEqual(result, {"processed": {}})

    def test_process_with_empty_list(self):
        """Test that process() handles empty list."""
        result = self.tool.process([])
        self.assertEqual(result, {"processed": []})

    def test_process_with_nested_dict(self):
        """Test that process() handles nested dictionary."""
        nested = {"outer": {"inner": "value"}}
        result = self.tool.process(nested)
        self.assertEqual(result, {"processed": nested})

    def test_process_with_complex_list(self):
        """Test that process() handles list with mixed types."""
        mixed_list = [1, "two", {"three": 3}, [4]]
        result = self.tool.process(mixed_list)
        self.assertEqual(result, {"processed": mixed_list})

    def test_process_with_string_raises_type_error(self):
        """Test that process() raises TypeValidationError for string input."""
        with self.assertRaises(TypeValidationError) as context:
            self.tool.process("not json")

        error = context.exception
        self.assertEqual(error.context.error_code.name, "TYPE_ERROR")

    def test_process_with_int_raises_type_error(self):
        """Test that process() raises TypeValidationError for int input."""
        with self.assertRaises(TypeValidationError):
            self.tool.process(123)

    def test_process_with_none_raises_type_error(self):
        """Test that process() raises TypeValidationError for None input."""
        with self.assertRaises(TypeValidationError):
            self.tool.process(None)

    def test_process_with_boolean_raises_type_error(self):
        """Test that process() raises TypeValidationError for boolean input."""
        with self.assertRaises(TypeValidationError):
            self.tool.process(True)

    def test_type_error_includes_expected_types(self):
        """Test that TypeValidationError specifies expected types."""
        with self.assertRaises(TypeValidationError) as context:
            self.tool.process("string")

        error = context.exception
        # Should mention dict or list in the message
        error_msg = error.message.lower()
        self.assertTrue('dict' in error_msg or 'list' in error_msg)

    def test_type_error_includes_tool_name(self):
        """Test that TypeValidationError includes tool name in details."""
        with self.assertRaises(TypeValidationError) as context:
            self.tool.process("string")

        error = context.exception
        self.assertIn("tool", error.details)
        self.assertEqual(error.details["tool"], "ConcreteJsonAnnotationTool")

    def test_type_error_has_suggestion(self):
        """Test that TypeValidationError includes helpful suggestion."""
        with self.assertRaises(TypeValidationError) as context:
            self.tool.process(123)

        error = context.exception
        self.assertIsNotNone(error.suggestion)
        self.assertIn("JSON", error.suggestion)

    @patch('annotation_toolkit.core.base.logger')
    def test_process_logs_info(self, mock_logger):
        """Test that process() logs info message."""
        self.tool.process({"test": "data"})
        mock_logger.info.assert_called_once()
        call_args = str(mock_logger.info.call_args)
        self.assertIn("Processing JSON data", call_args)

    @patch('annotation_toolkit.core.base.logger')
    def test_process_logs_debug_on_success(self, mock_logger):
        """Test that process() logs debug message on success."""
        self.tool.process({"test": "data"})
        # Should have debug call for success
        debug_calls = [call for call in mock_logger.debug.call_args_list
                      if 'completed successfully' in str(call)]
        self.assertGreater(len(debug_calls), 0)

    @patch('annotation_toolkit.core.base.logger')
    def test_process_logs_exception_on_error(self, mock_logger):
        """Test that process() logs exception on error."""
        with patch.object(self.tool, 'process_json', side_effect=ValueError("Test error")):
            with self.assertRaises(ProcessingError):
                self.tool.process({"test": "data"})

        mock_logger.exception.assert_called_once()

    def test_process_handles_exception_from_process_json(self):
        """Test that process() wraps exceptions from process_json()."""
        with patch.object(self.tool, 'process_json', side_effect=ValueError("Test error")):
            with self.assertRaises(ProcessingError) as context:
                self.tool.process({"test": "data"})

            error = context.exception
            self.assertIsInstance(error.cause, ValueError)
            self.assertIn("Test error", error.message)

    def test_process_error_from_json_includes_tool_name(self):
        """Test that ProcessingError includes tool name in details."""
        with patch.object(self.tool, 'process_json', side_effect=ValueError("Error")):
            with self.assertRaises(ProcessingError) as context:
                self.tool.process({"test": "data"})

            error = context.exception
            self.assertIn("tool", error.details)
            self.assertEqual(error.details["tool"], "ConcreteJsonAnnotationTool")

    def test_process_error_from_json_includes_data_type(self):
        """Test that ProcessingError includes data type in details."""
        with patch.object(self.tool, 'process_json', side_effect=ValueError("Error")):
            with self.assertRaises(ProcessingError) as context:
                self.tool.process({"test": "data"})

            error = context.exception
            self.assertIn("data_type", error.details)
            self.assertEqual(error.details["data_type"], "dict")

    def test_process_error_from_json_has_suggestion(self):
        """Test that ProcessingError includes helpful suggestion."""
        with patch.object(self.tool, 'process_json', side_effect=ValueError("Error")):
            with self.assertRaises(ProcessingError) as context:
                self.tool.process([1, 2, 3])

            error = context.exception
            self.assertIsNotNone(error.suggestion)
            self.assertIn("JSON", error.suggestion)


class TestToolConfigurationError(unittest.TestCase):
    """Test cases for ToolConfigurationError import."""

    def test_tool_configuration_error_imported(self):
        """Test that ToolConfigurationError is imported from errors module."""
        from annotation_toolkit.utils.errors import ConfigurationError
        self.assertEqual(ToolConfigurationError, ConfigurationError)


class TestToolExecutionError(unittest.TestCase):
    """Test cases for ToolExecutionError import."""

    def test_tool_execution_error_imported(self):
        """Test that ToolExecutionError is imported from errors module."""
        self.assertIsNotNone(ToolExecutionError)


class TestIntegration(unittest.TestCase):
    """Integration tests for base classes."""

    def test_text_and_json_tools_can_coexist(self):
        """Test that text and JSON tools can be instantiated together."""
        text_tool = ConcreteTextAnnotationTool()
        json_tool = ConcreteJsonAnnotationTool()

        text_result = text_tool.process("test")
        json_result = json_tool.process({"test": "data"})

        self.assertIsInstance(text_result, str)
        self.assertIsInstance(json_result, dict)

    def test_tools_handle_errors_independently(self):
        """Test that errors in one tool don't affect another."""
        text_tool = ConcreteTextAnnotationTool()
        json_tool = ConcreteJsonAnnotationTool()

        # Text tool works fine
        text_result = text_tool.process("test")
        self.assertEqual(text_result, "Processed: test")

        # JSON tool raises error for wrong input
        with self.assertRaises(TypeValidationError):
            json_tool.process("not json")

        # Text tool still works after JSON tool error
        text_result2 = text_tool.process("test2")
        self.assertEqual(text_result2, "Processed: test2")


if __name__ == "__main__":
    unittest.main()
