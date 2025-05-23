"""
Tests for the base classes in the annotation toolkit.

This module contains tests for the abstract base classes and interfaces
defined in the annotation_toolkit.core.base module.
"""

import unittest
from unittest.mock import MagicMock, patch

from annotation_toolkit.core.base import AnnotationTool, TextAnnotationTool, JsonAnnotationTool
from annotation_toolkit.utils.errors import ProcessingError, TypeValidationError


class TestAnnotationTool(unittest.TestCase):
    """Test cases for the AnnotationTool abstract base class."""

    def test_annotation_tool_is_abstract(self):
        """Test that AnnotationTool cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            AnnotationTool()


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

    def test_process_calls_process_text(self):
        """Test that process() calls process_text() with the input data converted to string."""
        result = self.tool.process("test")
        self.assertEqual(result, "Processed: test")

    def test_process_with_non_string_input(self):
        """Test that process() converts non-string input to string."""
        result = self.tool.process(123)
        self.assertEqual(result, "Processed: 123")

    def test_process_handles_exceptions(self):
        """Test that process() handles exceptions from process_text()."""
        with patch.object(self.tool, 'process_text', side_effect=ValueError("Test error")):
            with self.assertRaises(ProcessingError):
                self.tool.process("test")


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

    def test_process_calls_process_json(self):
        """Test that process() calls process_json() with the input data."""
        result = self.tool.process({"test": "data"})
        self.assertEqual(result, {"processed": {"test": "data"}})

    def test_process_with_list_input(self):
        """Test that process() accepts list input."""
        result = self.tool.process(["test", "data"])
        self.assertEqual(result, {"processed": ["test", "data"]})

    def test_process_with_non_json_input(self):
        """Test that process() raises TypeValidationError for non-JSON input."""
        with self.assertRaises(TypeValidationError):
            self.tool.process("not json")

    def test_process_handles_exceptions(self):
        """Test that process() handles exceptions from process_json()."""
        with patch.object(self.tool, 'process_json', side_effect=ValueError("Test error")):
            with self.assertRaises(ProcessingError):
                self.tool.process({"test": "data"})


if __name__ == "__main__":
    unittest.main()
