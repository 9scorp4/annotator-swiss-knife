"""
Comprehensive tests for ConversationGenerator tool.
"""

import unittest
import json
from unittest.mock import patch

from annotation_toolkit.core.conversation.generator import ConversationGenerator
from annotation_toolkit.utils.errors import TypeValidationError, ProcessingError


class TestConversationGeneratorInitialization(unittest.TestCase):
    """Test cases for ConversationGenerator initialization."""

    def test_initialization_default(self):
        """Test initialization with default parameters."""
        gen = ConversationGenerator()
        self.assertEqual(gen.max_turns, 20)
        self.assertEqual(len(gen.conversation), 0)

    def test_initialization_custom_max_turns(self):
        """Test initialization with custom max_turns."""
        gen = ConversationGenerator(max_turns=10)
        self.assertEqual(gen.max_turns, 10)

    def test_name_property(self):
        """Test name property."""
        gen = ConversationGenerator()
        self.assertEqual(gen.name, "Conversation Generator")

    def test_description_property(self):
        """Test description property."""
        gen = ConversationGenerator()
        self.assertIsInstance(gen.description, str)
        self.assertIn("conversation", gen.description.lower())


class TestConversationGeneratorAddTurn(unittest.TestCase):
    """Test cases for add_turn method."""

    def setUp(self):
        """Set up test fixtures."""
        self.gen = ConversationGenerator()

    def test_add_turn_basic(self):
        """Test adding a basic turn."""
        result = self.gen.add_turn("Hello", "Hi there!")
        self.assertTrue(result)
        self.assertEqual(self.gen.get_turn_count(), 1)

    def test_add_turn_adds_two_messages(self):
        """Test that adding a turn creates two messages."""
        self.gen.add_turn("User message", "Assistant response")
        conv = self.gen.conversation
        self.assertEqual(len(conv), 2)
        self.assertEqual(conv[0]["role"], "user")
        self.assertEqual(conv[1]["role"], "assistant")

    def test_add_turn_strips_whitespace(self):
        """Test that messages are stripped of whitespace."""
        self.gen.add_turn("  Message  ", "  Response  ")
        conv = self.gen.conversation
        self.assertEqual(conv[0]["content"], "Message")
        self.assertEqual(conv[1]["content"], "Response")

    def test_add_turn_multiple_turns(self):
        """Test adding multiple turns."""
        self.gen.add_turn("Turn 1 user", "Turn 1 assistant")
        self.gen.add_turn("Turn 2 user", "Turn 2 assistant")
        self.gen.add_turn("Turn 3 user", "Turn 3 assistant")

        self.assertEqual(self.gen.get_turn_count(), 3)
        self.assertEqual(len(self.gen.conversation), 6)

    def test_add_turn_empty_user_message_raises_error(self):
        """Test that empty user message raises ProcessingError."""
        with self.assertRaises(ProcessingError):
            self.gen.add_turn("", "Response")

    def test_add_turn_whitespace_only_user_message_raises_error(self):
        """Test that whitespace-only user message raises ProcessingError."""
        with self.assertRaises(ProcessingError):
            self.gen.add_turn("   ", "Response")

    def test_add_turn_empty_assistant_message_raises_error(self):
        """Test that empty assistant message raises ProcessingError."""
        with self.assertRaises(ProcessingError):
            self.gen.add_turn("Message", "")

    def test_add_turn_whitespace_only_assistant_message_raises_error(self):
        """Test that whitespace-only assistant message raises ProcessingError."""
        with self.assertRaises(ProcessingError):
            self.gen.add_turn("Message", "   ")

    def test_add_turn_non_string_user_message_raises_error(self):
        """Test that non-string user message raises TypeValidationError."""
        with self.assertRaises(TypeValidationError):
            self.gen.add_turn(123, "Response")

    def test_add_turn_non_string_assistant_message_raises_error(self):
        """Test that non-string assistant message raises TypeValidationError."""
        with self.assertRaises(TypeValidationError):
            self.gen.add_turn("Message", 456)

    def test_add_turn_max_turns_limit(self):
        """Test that max_turns limit is enforced."""
        gen = ConversationGenerator(max_turns=2)

        # Add 2 turns (should succeed)
        self.assertTrue(gen.add_turn("Turn 1 user", "Turn 1 assistant"))
        self.assertTrue(gen.add_turn("Turn 2 user", "Turn 2 assistant"))

        # Try to add 3rd turn (should fail)
        result = gen.add_turn("Turn 3 user", "Turn 3 assistant")
        self.assertFalse(result)
        self.assertEqual(gen.get_turn_count(), 2)


class TestConversationGeneratorRemoveTurn(unittest.TestCase):
    """Test cases for remove_turn method."""

    def setUp(self):
        """Set up test fixtures."""
        self.gen = ConversationGenerator()
        self.gen.add_turn("Turn 1 user", "Turn 1 assistant")
        self.gen.add_turn("Turn 2 user", "Turn 2 assistant")
        self.gen.add_turn("Turn 3 user", "Turn 3 assistant")

    def test_remove_turn_first(self):
        """Test removing the first turn."""
        result = self.gen.remove_turn(0)
        self.assertTrue(result)
        self.assertEqual(self.gen.get_turn_count(), 2)

    def test_remove_turn_middle(self):
        """Test removing a middle turn."""
        result = self.gen.remove_turn(1)
        self.assertTrue(result)
        self.assertEqual(self.gen.get_turn_count(), 2)

        # Verify remaining turns
        turn = self.gen.get_turn(0)
        self.assertEqual(turn[0], "Turn 1 user")

    def test_remove_turn_last(self):
        """Test removing the last turn."""
        result = self.gen.remove_turn(2)
        self.assertTrue(result)
        self.assertEqual(self.gen.get_turn_count(), 2)

    def test_remove_turn_invalid_index_negative(self):
        """Test that invalid negative index returns False."""
        result = self.gen.remove_turn(-1)
        self.assertFalse(result)

    def test_remove_turn_invalid_index_too_large(self):
        """Test that invalid large index returns False."""
        result = self.gen.remove_turn(999)
        self.assertFalse(result)

    def test_remove_turn_updates_conversation(self):
        """Test that remove_turn properly updates conversation."""
        self.gen.remove_turn(1)

        # Check that turn 2 is removed and turn 3 is now at index 1
        turn = self.gen.get_turn(1)
        self.assertEqual(turn[0], "Turn 3 user")


class TestConversationGeneratorClear(unittest.TestCase):
    """Test cases for clear method."""

    def test_clear_empty_conversation(self):
        """Test clearing an empty conversation."""
        gen = ConversationGenerator()
        gen.clear()
        self.assertEqual(gen.get_turn_count(), 0)

    def test_clear_with_turns(self):
        """Test clearing a conversation with turns."""
        gen = ConversationGenerator()
        gen.add_turn("Turn 1 user", "Turn 1 assistant")
        gen.add_turn("Turn 2 user", "Turn 2 assistant")

        gen.clear()

        self.assertEqual(gen.get_turn_count(), 0)
        self.assertEqual(len(gen.conversation), 0)


class TestConversationGeneratorGetTurnCount(unittest.TestCase):
    """Test cases for get_turn_count method."""

    def test_get_turn_count_empty(self):
        """Test turn count for empty conversation."""
        gen = ConversationGenerator()
        self.assertEqual(gen.get_turn_count(), 0)

    def test_get_turn_count_single_turn(self):
        """Test turn count with single turn."""
        gen = ConversationGenerator()
        gen.add_turn("User", "Assistant")
        self.assertEqual(gen.get_turn_count(), 1)

    def test_get_turn_count_multiple_turns(self):
        """Test turn count with multiple turns."""
        gen = ConversationGenerator()
        for i in range(5):
            gen.add_turn(f"User {i}", f"Assistant {i}")
        self.assertEqual(gen.get_turn_count(), 5)


class TestConversationGeneratorCanAddTurn(unittest.TestCase):
    """Test cases for can_add_turn method."""

    def test_can_add_turn_empty(self):
        """Test can_add_turn on empty conversation."""
        gen = ConversationGenerator(max_turns=2)
        self.assertTrue(gen.can_add_turn())

    def test_can_add_turn_below_limit(self):
        """Test can_add_turn below max limit."""
        gen = ConversationGenerator(max_turns=3)
        gen.add_turn("User 1", "Assistant 1")
        self.assertTrue(gen.can_add_turn())

    def test_can_add_turn_at_limit(self):
        """Test can_add_turn at max limit."""
        gen = ConversationGenerator(max_turns=2)
        gen.add_turn("User 1", "Assistant 1")
        gen.add_turn("User 2", "Assistant 2")
        self.assertFalse(gen.can_add_turn())


class TestConversationGeneratorGenerateJson(unittest.TestCase):
    """Test cases for generate_json method."""

    def setUp(self):
        """Set up test fixtures."""
        self.gen = ConversationGenerator()

    def test_generate_json_empty(self):
        """Test generating JSON for empty conversation."""
        result = self.gen.generate_json()
        self.assertEqual(result, "[]")

    def test_generate_json_single_turn(self):
        """Test generating JSON for single turn."""
        self.gen.add_turn("Hello", "Hi!")
        result = self.gen.generate_json()

        parsed = json.loads(result)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["role"], "user")
        self.assertEqual(parsed[0]["content"], "Hello")
        self.assertEqual(parsed[1]["role"], "assistant")
        self.assertEqual(parsed[1]["content"], "Hi!")

    def test_generate_json_pretty(self):
        """Test generating pretty-printed JSON."""
        self.gen.add_turn("User", "Assistant")
        result = self.gen.generate_json(pretty=True)

        # Pretty JSON should have newlines
        self.assertIn("\n", result)

    def test_generate_json_compact(self):
        """Test generating compact JSON."""
        self.gen.add_turn("User", "Assistant")
        result = self.gen.generate_json(pretty=False)

        # Compact JSON should not have indentation
        parsed = json.loads(result)
        self.assertIsInstance(parsed, list)

    def test_generate_json_valid_structure(self):
        """Test that generated JSON has valid structure."""
        self.gen.add_turn("Turn 1 user", "Turn 1 assistant")
        self.gen.add_turn("Turn 2 user", "Turn 2 assistant")

        result = self.gen.generate_json()
        parsed = json.loads(result)

        self.assertEqual(len(parsed), 4)
        for msg in parsed:
            self.assertIn("role", msg)
            self.assertIn("content", msg)


class TestConversationGeneratorLoadFromJson(unittest.TestCase):
    """Test cases for load_from_json method."""

    def setUp(self):
        """Set up test fixtures."""
        self.gen = ConversationGenerator()

    def test_load_from_json_string(self):
        """Test loading from JSON string."""
        json_str = '[{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi"}]'
        self.gen.load_from_json(json_str)

        self.assertEqual(self.gen.get_turn_count(), 1)
        self.assertEqual(len(self.gen.conversation), 2)

    def test_load_from_json_list(self):
        """Test loading from list of dicts."""
        data = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"}
        ]
        self.gen.load_from_json(data)

        self.assertEqual(self.gen.get_turn_count(), 1)

    def test_load_from_json_invalid_string_raises_error(self):
        """Test that invalid JSON string raises ProcessingError."""
        with self.assertRaises(ProcessingError):
            self.gen.load_from_json("not valid json")

    def test_load_from_json_non_list_raises_error(self):
        """Test that non-list data raises TypeValidationError."""
        with self.assertRaises(TypeValidationError):
            self.gen.load_from_json({"not": "a list"})

    def test_load_from_json_non_dict_message_raises_error(self):
        """Test that non-dict message raises TypeValidationError."""
        with self.assertRaises(TypeValidationError):
            self.gen.load_from_json(["not a dict"])

    def test_load_from_json_missing_role_raises_error(self):
        """Test that message missing 'role' raises ProcessingError."""
        with self.assertRaises(ProcessingError):
            self.gen.load_from_json([{"content": "Hello"}])

    def test_load_from_json_missing_content_raises_error(self):
        """Test that message missing 'content' raises ProcessingError."""
        with self.assertRaises(ProcessingError):
            self.gen.load_from_json([{"role": "user"}])

    def test_load_from_json_invalid_role_raises_error(self):
        """Test that invalid role raises ProcessingError."""
        with self.assertRaises(ProcessingError):
            self.gen.load_from_json([{"role": "system", "content": "Hello"}])

    def test_load_from_json_exceeds_max_turns_raises_error(self):
        """Test that exceeding max_turns raises ProcessingError."""
        gen = ConversationGenerator(max_turns=1)
        data = [
            {"role": "user", "content": "Turn 1"},
            {"role": "assistant", "content": "Response 1"},
            {"role": "user", "content": "Turn 2"},
            {"role": "assistant", "content": "Response 2"}
        ]

        with self.assertRaises(ProcessingError):
            gen.load_from_json(data)

    def test_load_from_json_replaces_existing(self):
        """Test that loading replaces existing conversation."""
        self.gen.add_turn("Old turn", "Old response")

        new_data = [
            {"role": "user", "content": "New turn"},
            {"role": "assistant", "content": "New response"}
        ]
        self.gen.load_from_json(new_data)

        self.assertEqual(self.gen.get_turn_count(), 1)
        turn = self.gen.get_turn(0)
        self.assertEqual(turn[0], "New turn")


class TestConversationGeneratorProcessJson(unittest.TestCase):
    """Test cases for process_json method."""

    def test_process_json_basic(self):
        """Test processing JSON data."""
        gen = ConversationGenerator()
        data = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"}
        ]

        result = gen.process_json(data)

        # Should return JSON string
        parsed = json.loads(result)
        self.assertEqual(len(parsed), 2)

    def test_process_json_pretty_output(self):
        """Test that process_json returns pretty JSON."""
        gen = ConversationGenerator()
        data = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"}
        ]

        result = gen.process_json(data)

        # Pretty JSON should have newlines
        self.assertIn("\n", result)


class TestConversationGeneratorGetTurn(unittest.TestCase):
    """Test cases for get_turn method."""

    def setUp(self):
        """Set up test fixtures."""
        self.gen = ConversationGenerator()
        self.gen.add_turn("Turn 1 user", "Turn 1 assistant")
        self.gen.add_turn("Turn 2 user", "Turn 2 assistant")

    def test_get_turn_first(self):
        """Test getting the first turn."""
        turn = self.gen.get_turn(0)
        self.assertIsNotNone(turn)
        self.assertEqual(turn[0], "Turn 1 user")
        self.assertEqual(turn[1], "Turn 1 assistant")

    def test_get_turn_second(self):
        """Test getting the second turn."""
        turn = self.gen.get_turn(1)
        self.assertIsNotNone(turn)
        self.assertEqual(turn[0], "Turn 2 user")
        self.assertEqual(turn[1], "Turn 2 assistant")

    def test_get_turn_invalid_index_returns_none(self):
        """Test that invalid index returns None."""
        turn = self.gen.get_turn(999)
        self.assertIsNone(turn)

    def test_get_turn_negative_index_returns_none(self):
        """Test that negative index returns None."""
        turn = self.gen.get_turn(-1)
        self.assertIsNone(turn)


class TestConversationGeneratorConversationProperty(unittest.TestCase):
    """Test cases for conversation property."""

    def test_conversation_property_returns_copy(self):
        """Test that conversation property returns a copy."""
        gen = ConversationGenerator()
        gen.add_turn("User", "Assistant")

        conv = gen.conversation
        conv.append({"role": "user", "content": "Modified"})

        # Original should not be modified
        self.assertEqual(gen.get_turn_count(), 1)


class TestConversationGeneratorIntegration(unittest.TestCase):
    """Integration tests for ConversationGenerator."""

    def test_full_workflow(self):
        """Test complete workflow of building and exporting conversation."""
        gen = ConversationGenerator()

        # Build conversation
        gen.add_turn("What is Python?", "Python is a programming language.")
        gen.add_turn("What is it used for?", "It's used for web development, data science, and more.")

        # Generate JSON
        json_str = gen.generate_json(pretty=True)

        # Verify
        parsed = json.loads(json_str)
        self.assertEqual(len(parsed), 4)
        self.assertEqual(parsed[0]["content"], "What is Python?")

    def test_load_modify_export(self):
        """Test loading, modifying, and exporting."""
        gen = ConversationGenerator()

        # Load existing conversation
        data = [
            {"role": "user", "content": "Turn 1"},
            {"role": "assistant", "content": "Response 1"}
        ]
        gen.load_from_json(data)

        # Add new turn
        gen.add_turn("Turn 2", "Response 2")

        # Remove first turn
        gen.remove_turn(0)

        # Export
        result = gen.generate_json()
        parsed = json.loads(result)

        # Should only have turn 2
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["content"], "Turn 2")

    def test_max_turns_enforcement(self):
        """Test max_turns enforcement throughout workflow."""
        gen = ConversationGenerator(max_turns=2)

        # Add max turns
        gen.add_turn("Turn 1", "Response 1")
        gen.add_turn("Turn 2", "Response 2")

        # Should not be able to add more
        self.assertFalse(gen.can_add_turn())
        result = gen.add_turn("Turn 3", "Response 3")
        self.assertFalse(result)

        # Remove one turn
        gen.remove_turn(0)

        # Should be able to add again
        self.assertTrue(gen.can_add_turn())


if __name__ == "__main__":
    unittest.main()
