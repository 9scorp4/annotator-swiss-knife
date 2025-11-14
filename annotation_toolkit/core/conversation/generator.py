"""
Conversation Generator tool.

This module implements a tool for generating JSON strings containing
AI conversation data by allowing users to build conversations turn by turn.
"""

import json
from typing import Any, Dict, List, Optional, Tuple, Union

from ...core.base import JsonAnnotationTool, ToolExecutionError
from ...utils import logger
from ...utils.errors import ErrorCode, ProcessingError, TypeValidationError


class ConversationGenerator(JsonAnnotationTool):
    """
    Tool for generating AI conversation JSON strings.

    This tool allows users to build conversations by adding turns
    (user prompts and AI responses) and generates properly formatted
    JSON strings for use in AI annotation tasks.
    """

    MAX_TURNS = 20

    def __init__(self, max_turns: int = MAX_TURNS):
        """
        Initialize the Conversation Generator.

        Args:
            max_turns (int): Maximum number of conversation turns allowed.
                Default is 20.
        """
        super().__init__()
        self._max_turns = max_turns
        self._conversation: List[Dict[str, str]] = []
        logger.debug(
            f"ConversationGenerator initialized with max_turns={max_turns}"
        )

    @property
    def name(self) -> str:
        """
        Return the name of the tool.

        Returns:
            str: The name of the tool.
        """
        return "Conversation Generator"

    @property
    def description(self) -> str:
        """
        Return a description of the tool.

        Returns:
            str: A description of the tool's functionality.
        """
        return "Generates JSON strings for AI conversations by building them turn by turn."

    @property
    def max_turns(self) -> int:
        """
        Get the maximum number of turns allowed.

        Returns:
            int: Maximum number of turns.
        """
        return self._max_turns

    @property
    def conversation(self) -> List[Dict[str, str]]:
        """
        Get the current conversation.

        Returns:
            List[Dict[str, str]]: The current conversation turns.
        """
        return self._conversation.copy()

    def add_turn(self, user_message: str, assistant_message: str) -> bool:
        """
        Add a conversation turn (user message + assistant response).

        Args:
            user_message (str): The user's message/prompt.
            assistant_message (str): The assistant's response.

        Returns:
            bool: True if the turn was added successfully, False if max turns reached.

        Raises:
            TypeValidationError: If messages are not strings or are empty.
        """
        logger.info("Adding conversation turn")

        # Validate inputs
        if not isinstance(user_message, str):
            raise TypeValidationError(
                "user_message",
                str,
                type(user_message),
                suggestion="User message must be a string."
            )

        if not isinstance(assistant_message, str):
            raise TypeValidationError(
                "assistant_message",
                str,
                type(assistant_message),
                suggestion="Assistant message must be a string."
            )

        if not user_message.strip():
            raise ProcessingError(
                "User message cannot be empty",
                error_code=ErrorCode.VALIDATION_ERROR,
                suggestion="Please provide a non-empty user message."
            )

        if not assistant_message.strip():
            raise ProcessingError(
                "Assistant message cannot be empty",
                error_code=ErrorCode.VALIDATION_ERROR,
                suggestion="Please provide a non-empty assistant message."
            )

        # Check if we've reached max turns
        if len(self._conversation) >= self._max_turns * 2:
            logger.warning(f"Cannot add turn: maximum of {self._max_turns} turns reached")
            return False

        # Add the turn as two messages
        self._conversation.append({
            "role": "user",
            "content": user_message.strip()
        })
        self._conversation.append({
            "role": "assistant",
            "content": assistant_message.strip()
        })

        logger.debug(f"Turn added successfully. Total messages: {len(self._conversation)}")
        return True

    def remove_turn(self, turn_index: int) -> bool:
        """
        Remove a conversation turn by its index.

        Args:
            turn_index (int): The index of the turn to remove (0-based).

        Returns:
            bool: True if the turn was removed successfully, False otherwise.
        """
        logger.info(f"Removing turn at index {turn_index}")

        # Calculate message indices (each turn = 2 messages)
        user_msg_index = turn_index * 2
        assistant_msg_index = turn_index * 2 + 1

        # Validate index
        if user_msg_index < 0 or assistant_msg_index >= len(self._conversation):
            logger.warning(f"Invalid turn index: {turn_index}")
            return False

        # Remove both messages (remove in reverse order to maintain indices)
        del self._conversation[assistant_msg_index]
        del self._conversation[user_msg_index]

        logger.debug(f"Turn removed successfully. Remaining messages: {len(self._conversation)}")
        return True

    def clear(self) -> None:
        """
        Clear all conversation turns.
        """
        logger.info("Clearing all conversation turns")
        self._conversation.clear()
        logger.debug("Conversation cleared")

    def get_turn_count(self) -> int:
        """
        Get the current number of conversation turns.

        Returns:
            int: Number of turns (each turn = user message + assistant response).
        """
        return len(self._conversation) // 2

    def can_add_turn(self) -> bool:
        """
        Check if another turn can be added.

        Returns:
            bool: True if another turn can be added, False if max turns reached.
        """
        return len(self._conversation) < self._max_turns * 2

    def generate_json(self, pretty: bool = True) -> str:
        """
        Generate JSON string from the current conversation.

        Args:
            pretty (bool): If True, generate pretty-printed JSON.
                If False, generate compact JSON.

        Returns:
            str: JSON string representation of the conversation.
        """
        logger.info(f"Generating JSON (pretty={pretty})")

        if not self._conversation:
            logger.debug("Empty conversation, returning empty array JSON")
            return "[]"

        if pretty:
            json_str = json.dumps(self._conversation, indent=2, ensure_ascii=False)
        else:
            json_str = json.dumps(self._conversation, ensure_ascii=False)

        logger.debug(f"JSON generated: {len(json_str)} characters")
        return json_str

    def load_from_json(self, json_data: Union[str, List[Dict[str, str]]]) -> None:
        """
        Load conversation from JSON data.

        Args:
            json_data: Either a JSON string or a list of message dictionaries.

        Raises:
            ProcessingError: If the JSON data is invalid.
        """
        logger.info("Loading conversation from JSON")

        # Parse if string
        if isinstance(json_data, str):
            try:
                parsed_data = json.loads(json_data)
            except json.JSONDecodeError as e:
                raise ProcessingError(
                    f"Invalid JSON: {str(e)}",
                    error_code=ErrorCode.PARSING_ERROR,
                    suggestion="Ensure the JSON is properly formatted."
                )
        else:
            parsed_data = json_data

        # Validate format
        if not isinstance(parsed_data, list):
            raise TypeValidationError(
                "conversation_data",
                list,
                type(parsed_data),
                suggestion="Conversation must be a list of messages."
            )

        # Validate each message
        for i, msg in enumerate(parsed_data):
            if not isinstance(msg, dict):
                raise TypeValidationError(
                    f"message[{i}]",
                    dict,
                    type(msg),
                    suggestion="Each message must be a dictionary."
                )

            if "role" not in msg or "content" not in msg:
                raise ProcessingError(
                    f"Message {i} is missing 'role' or 'content' field",
                    error_code=ErrorCode.VALIDATION_ERROR,
                    suggestion="Each message must have 'role' and 'content' fields."
                )

            if msg["role"] not in ["user", "assistant"]:
                raise ProcessingError(
                    f"Message {i} has invalid role: {msg['role']}",
                    error_code=ErrorCode.VALIDATION_ERROR,
                    suggestion="Role must be either 'user' or 'assistant'."
                )

        # Check turn limit
        if len(parsed_data) > self._max_turns * 2:
            raise ProcessingError(
                f"Conversation exceeds maximum of {self._max_turns} turns",
                error_code=ErrorCode.VALIDATION_ERROR,
                suggestion=f"Limit conversation to {self._max_turns} turns."
            )

        # Load the conversation
        self._conversation = parsed_data
        logger.info(f"Conversation loaded successfully: {len(self._conversation)} messages")

    def process_json(self, json_data: Union[Dict, List]) -> str:
        """
        Process JSON input and return a formatted conversation string.

        This implements the JsonAnnotationTool interface.

        Args:
            json_data: The input JSON data (conversation list).

        Returns:
            str: JSON string representation of the conversation.
        """
        logger.info("Processing JSON data through process_json interface")

        # Load the conversation from the JSON data
        self.load_from_json(json_data)

        # Generate and return the JSON string
        return self.generate_json(pretty=True)

    def get_turn(self, turn_index: int) -> Optional[Tuple[str, str]]:
        """
        Get a specific turn by index.

        Args:
            turn_index (int): The index of the turn to retrieve (0-based).

        Returns:
            Optional[Tuple[str, str]]: Tuple of (user_message, assistant_message)
                or None if index is invalid.
        """
        user_msg_index = turn_index * 2
        assistant_msg_index = turn_index * 2 + 1

        if user_msg_index < 0 or assistant_msg_index >= len(self._conversation):
            return None

        user_msg = self._conversation[user_msg_index]["content"]
        assistant_msg = self._conversation[assistant_msg_index]["content"]

        return (user_msg, assistant_msg)
