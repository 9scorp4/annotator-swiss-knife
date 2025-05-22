"""
Command implementations for the annotation toolkit CLI.

This module provides implementations for the various CLI commands.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

from ...config import Config
from ...core.base import ToolExecutionError
from ...core.conversation.visualizer import JsonVisualizer
from ...core.text.dict_to_bullet import DictToBulletList
from ...core.text.text_cleaner import TextCleaner
from ...utils import logger
from ...utils.file_utils import load_json


def run_dict_to_bullet_command(args: argparse.Namespace, config: Config) -> int:
    """
    Run the Dictionary to Bullet List command.

    Args:
        args (argparse.Namespace): Command-line arguments.
        config (Config): The configuration.

    Returns:
        int: Exit code.
    """
    logger.info("Running Dictionary to Bullet List command")
    logger.debug(f"Command arguments: {args}")

    try:
        # Create the tool
        logger.debug(f"Creating DictToBulletList tool with format: {args.format}")
        tool = DictToBulletList(markdown_output=(args.format == "markdown"))

        # Load input data
        input_path = Path(args.input_file)
        logger.info(f"Loading input data from: {input_path}")

        if not input_path.exists():
            logger.error(f"Input file not found: {input_path}")
            print(f"Error: Input file not found: {input_path}", file=sys.stderr)
            return 1

        try:
            logger.debug(f"Parsing JSON from: {input_path}")
            input_data = load_json(input_path)
            logger.debug(f"Successfully loaded JSON data")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON file: {str(e)}")
            print(f"Error: Invalid JSON file: {e}", file=sys.stderr)
            return 1

        # Ensure input is a dictionary
        if not isinstance(input_data, dict):
            logger.error(f"Input is not a dictionary, got: {type(input_data).__name__}")
            print("Error: Input must be a JSON object (dictionary)", file=sys.stderr)
            return 1

        # Process the data
        logger.info(f"Processing dictionary with {len(input_data)} items")
        output = tool.process_dict(input_data)
        logger.debug(f"Processing complete, output length: {len(output)} characters")

        # Output the result
        if args.output:
            output_path = Path(args.output)
            logger.info(f"Saving output to: {output_path}")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output)
            logger.info(f"Output saved successfully to: {output_path}")
            print(f"Output saved to: {output_path}")
        else:
            logger.info("Printing output to console")
            print(output)

        logger.info("Dictionary to Bullet List command completed successfully")
        return 0

    except ToolExecutionError as e:
        logger.error(f"Tool execution error: {str(e)}")
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error in dict_to_bullet command: {str(e)}")
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        return 1


def run_json_visualizer_command(args: argparse.Namespace, config: Config) -> int:
    """
    Run the JSON Visualizer command.

    Args:
        args (argparse.Namespace): Command-line arguments.
        config (Config): The configuration.

    Returns:
        int: Exit code.
    """
    logger.info("Running JSON Visualizer command")
    logger.debug(f"Command arguments: {args}")

    try:
        # Get color settings from config
        logger.debug("Getting color settings from config")
        user_message_color = config.get(
            "tools", "conversation_visualizer", "user_message_color", default="#0d47a1"
        )
        ai_message_color = config.get(
            "tools", "conversation_visualizer", "ai_message_color", default="#33691e"
        )
        logger.debug(
            f"Using colors - user: {user_message_color}, AI: {ai_message_color}"
        )

        # Create the tool
        logger.debug(f"Creating JsonVisualizer tool with format: {args.format}")
        tool = JsonVisualizer(
            output_format=args.format,
            user_message_color=user_message_color,
            ai_message_color=ai_message_color,
        )

        # Load input data
        input_path = Path(args.input_file)
        logger.info(f"Loading input data from: {input_path}")

        if not input_path.exists():
            logger.error(f"Input file not found: {input_path}")
            print(f"Error: Input file not found: {input_path}", file=sys.stderr)
            return 1

        try:
            logger.debug(f"Reading file content from: {input_path}")
            with open(input_path, "r", encoding="utf-8") as f:
                input_data = f.read()
            logger.debug(
                f"Successfully read file, content length: {len(input_data)} characters"
            )
        except Exception as e:
            logger.error(f"Error reading file: {str(e)}")
            print(f"Error reading file: {str(e)}", file=sys.stderr)
            return 1

        # Parse and process the data
        try:
            logger.info("Parsing conversation data")
            conversation = tool.parse_conversation_data(input_data)
            logger.info(
                f"Successfully parsed conversation with {len(conversation)} messages"
            )
        except ToolExecutionError as e:
            logger.error(f"Error parsing conversation data: {str(e)}")
            print(f"Error parsing conversation data: {str(e)}", file=sys.stderr)
            return 1

        # Search if requested
        if args.search:
            logger.info(
                f"Searching for: '{args.search}' (case sensitive: {args.case_sensitive})"
            )
            print(f"Searching for: {args.search}")
            matches = tool.search_conversation(
                conversation, args.search, case_sensitive=args.case_sensitive
            )

            if not matches:
                logger.info("No matches found")
                print("No matches found.")
                return 0

            logger.info(f"Found {len(matches)} matching messages")
            print(f"Found {len(matches)} matching messages:")

            # Only process and display matching messages
            matched_conversation = [conversation[i] for i in matches]
            logger.debug(f"Formatting {len(matched_conversation)} matched messages")
            output = tool.format_conversation(matched_conversation, use_colors=False)
        else:
            # Process all messages
            logger.debug(f"Formatting all {len(conversation)} messages")
            output = tool.format_conversation(conversation, use_colors=False)

        # Output the result
        if args.output:
            output_path = Path(args.output)
            logger.info(f"Saving output to: {output_path}")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output)
            logger.info(f"Output saved successfully to: {output_path}")
            print(f"Output saved to: {output_path}")
        else:
            logger.info("Printing output to console")
            print(output)

        logger.info("JSON Visualizer command completed successfully")
        return 0

    except ToolExecutionError as e:
        logger.error(f"Tool execution error: {str(e)}")
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error in json_visualizer command: {str(e)}")
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        return 1


def run_text_cleaner_command(args: argparse.Namespace, config: Config) -> int:
    """
    Run the Text Cleaner command.

    Args:
        args (argparse.Namespace): Command-line arguments.
        config (Config): The configuration.

    Returns:
        int: Exit code.
    """
    logger.info("Running Text Cleaner command")
    logger.debug(f"Command arguments: {args}")

    try:
        # Create the tool
        logger.debug(f"Creating TextCleaner tool with format: {args.format}")
        tool = TextCleaner(output_format=args.format)

        # Load input data
        input_path = Path(args.input_file)
        logger.info(f"Loading input data from: {input_path}")

        if not input_path.exists():
            logger.error(f"Input file not found: {input_path}")
            print(f"Error: Input file not found: {input_path}", file=sys.stderr)
            return 1

        try:
            logger.debug(f"Reading file content from: {input_path}")
            with open(input_path, "r", encoding="utf-8") as f:
                input_data = f.read()
            logger.debug(
                f"Successfully read file, content length: {len(input_data)} characters"
            )
        except Exception as e:
            logger.error(f"Error reading file: {str(e)}")
            print(f"Error reading file: {str(e)}", file=sys.stderr)
            return 1

        # Process the data
        logger.info("Processing text data")
        output = tool.process_text(input_data)
        logger.debug(f"Processing complete, output length: {len(output)} characters")

        # Output the result
        if args.output:
            output_path = Path(args.output)
            logger.info(f"Saving output to: {output_path}")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output)
            logger.info(f"Output saved successfully to: {output_path}")
            print(f"Output saved to: {output_path}")
        else:
            logger.info("Printing output to console")
            print(output)

        logger.info("Text Cleaner command completed successfully")
        return 0

    except ToolExecutionError as e:
        logger.error(f"Tool execution error: {str(e)}")
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error in text_cleaner command: {str(e)}")
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        return 1
