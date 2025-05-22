"""
Tests for the Dictionary to Bullet List tool.
"""

import json

import pytest

from annotation_toolkit.core.base import ToolExecutionError
from annotation_toolkit.core.text.dict_to_bullet import DictToBulletList


class TestDictToBulletList:
    """Test cases for the DictToBulletList tool."""

    def test_name_and_description(self):
        """Test name and description."""
        tool = DictToBulletList()
        assert tool.name == "Dictionary to Bullet List"
        assert "dictionary" in tool.description.lower()

    def test_process_dict_with_urls(self):
        """Test processing a dictionary with URLs."""
        tool = DictToBulletList(markdown_output=True)
        input_dict = {
            "1": "https://www.example.com/page1",
            "2": "https://www.example.com/page2",
        }

        output = tool.process_dict(input_dict)

        # Check if output is a string
        assert isinstance(output, str)

        # Check if output contains markdown links
        assert "[Page1]" in output
        assert "(https://www.example.com/page1)" in output
        assert "[Page2]" in output
        assert "(https://www.example.com/page2)" in output

        # Check if output has bullet points
        assert output.startswith("*")

    def test_process_dict_without_markdown(self):
        """Test processing a dictionary without markdown output."""
        tool = DictToBulletList(markdown_output=False)
        input_dict = {
            "1": "https://www.example.com/page1",
            "2": "https://www.example.com/page2",
        }

        output = tool.process_dict(input_dict)

        # Check if output contains URLs but not markdown links
        assert "Page1: https://www.example.com/page1" in output
        assert "Page2: https://www.example.com/page2" in output

        # Check if output has bullet points
        assert output.startswith("*")

    def test_process_text_valid_json(self):
        """Test processing a valid JSON string."""
        tool = DictToBulletList()
        input_json = json.dumps(
            {"1": "https://www.example.com/page1", "2": "https://www.example.com/page2"}
        )

        output = tool.process_text(input_json)

        # Check if output is processed correctly
        assert "[Page1]" in output
        assert "(https://www.example.com/page1)" in output

    def test_process_text_invalid_json(self):
        """Test processing an invalid JSON string."""
        tool = DictToBulletList()
        input_json = "{invalid json}"

        with pytest.raises(ToolExecutionError) as excinfo:
            tool.process_text(input_json)

        assert "Invalid JSON" in str(excinfo.value)

    def test_process_text_non_dict_json(self):
        """Test processing JSON that is not a dictionary."""
        tool = DictToBulletList()
        input_json = json.dumps(["not", "a", "dict"])

        with pytest.raises(ToolExecutionError) as excinfo:
            tool.process_text(input_json)

        assert "must be a JSON object" in str(excinfo.value)

    def test_process_dict_non_string_values(self):
        """Test processing a dictionary with non-string values."""
        tool = DictToBulletList()
        input_dict = {"1": "https://www.example.com/page1", "2": 123}  # Not a string

        with pytest.raises(ToolExecutionError) as excinfo:
            tool.process_dict(input_dict)

        assert "must be strings" in str(excinfo.value)

    def test_process_dict_to_items(self):
        """Test processing a dictionary to a list of items."""
        tool = DictToBulletList()
        input_dict = {
            "1": "https://www.example.com/page1",
            "2": "https://www.example.com/page2",
            "key3": "not-a-url",
        }

        items = tool.process_dict_to_items(input_dict)

        # Check if items are correctly processed
        assert len(items) == 3
        assert items[0][0] == "Page1"
        assert items[0][1] == "https://www.example.com/page1"
        assert items[1][0] == "Page2"
        assert items[1][1] == "https://www.example.com/page2"
        assert items[2][0] == "key3"
        assert items[2][1] == "not-a-url"

    def test_markdown_output_property(self):
        """Test the markdown_output property."""
        tool = DictToBulletList(markdown_output=True)
        assert tool.markdown_output is True

        tool.markdown_output = False
        assert tool.markdown_output is False
