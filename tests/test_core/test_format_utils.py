"""
Tests for the format_utils module.
"""

import pytest
from annotation_toolkit.utils.format_utils import parse_conversation_json


def test_parse_conversation_json_standard_format():
    """Test parsing standard conversation format."""
    json_data = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]

    result = parse_conversation_json(json_data)

    assert len(result) == 2
    assert result[0]["role"] == "user"
    assert result[0]["content"] == "Hello"
    assert result[1]["role"] == "assistant"
    assert result[1]["content"] == "Hi there!"


def test_parse_conversation_json_chat_history_format():
    """Test parsing chat_history format."""
    json_data = {
        "chat_history": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
    }

    result = parse_conversation_json(json_data)

    assert len(result) == 2
    assert result[0]["role"] == "user"
    assert result[0]["content"] == "Hello"
    assert result[1]["role"] == "assistant"
    assert result[1]["content"] == "Hi there!"


def test_parse_conversation_json_message_v2_format():
    """Test parsing message_v2 format."""
    json_data = [
        {
            "source": "user",
            "version": "message_v2",
            "body": "Hello",
            "destination": None,
            "eot": True,
            "metadata": None,
            "ipython": False,
            "is_complete": True,
            "is_header_complete": True,
            "media_attachments": None,
        },
        {
            "source": "assistant",
            "version": "message_v2",
            "body": "Hi there!",
            "destination": None,
            "eot": True,
            "metadata": None,
            "ipython": False,
            "is_complete": True,
            "is_header_complete": True,
            "media_attachments": None,
        },
    ]

    result = parse_conversation_json(json_data)

    assert len(result) == 2
    assert result[0]["role"] == "user"
    assert result[0]["content"] == "Hello"
    assert result[1]["role"] == "assistant"
    assert result[1]["content"] == "Hi there!"


def test_parse_conversation_json_invalid_format():
    """Test parsing invalid format."""
    json_data = [{"invalid": "format"}]

    with pytest.raises(ValueError):
        parse_conversation_json(json_data)


def test_parse_conversation_json_not_dict():
    """Test parsing non-dictionary message."""
    json_data = ["not a dictionary"]

    with pytest.raises(ValueError):
        parse_conversation_json(json_data)
