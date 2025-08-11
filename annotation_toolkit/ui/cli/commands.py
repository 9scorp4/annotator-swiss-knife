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
from ...di import DIContainer
from ...di.bootstrap import bootstrap_application, get_tool_instances, validate_container_configuration
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
        # Bootstrap DI container and get the tool
        logger.debug("Bootstrapping DI container for command")
        container = bootstrap_application(config)
        
        if not validate_container_configuration(container):
            logger.error("DI container validation failed")
            print("Error: Failed to initialize application services", file=sys.stderr)
            return 1
            
        # Get the tool from the container
        logger.debug("Resolving DictToBulletList tool from DI container")
        tool = container.resolve(DictToBulletList)
        
        # Override the markdown output setting based on command line arg
        tool.markdown_output = (args.format == "markdown")
        logger.debug(f"Set tool markdown_output to: {tool.markdown_output}")

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
        # Bootstrap DI container and get the tool
        logger.debug("Bootstrapping DI container for command")
        container = bootstrap_application(config)
        
        if not validate_container_configuration(container):
            logger.error("DI container validation failed")
            print("Error: Failed to initialize application services", file=sys.stderr)
            return 1
            
        # Get the tool from the container
        logger.debug("Resolving JsonVisualizer tool from DI container")
        tool = container.resolve(JsonVisualizer)
        
        # Override the output format setting based on command line arg
        tool._output_format = args.format
        logger.debug(f"Set tool output_format to: {tool._output_format}")

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
        # Bootstrap DI container and get the tool
        logger.debug("Bootstrapping DI container for command")
        container = bootstrap_application(config)
        
        if not validate_container_configuration(container):
            logger.error("DI container validation failed")
            print("Error: Failed to initialize application services", file=sys.stderr)
            return 1
            
        # Get the tool from the container
        logger.debug("Resolving TextCleaner tool from DI container")
        tool = container.resolve(TextCleaner)
        
        # Override the output format setting based on command line arg if needed
        # Note: TextCleaner might not have an output_format parameter, so we handle this gracefully
        if hasattr(tool, '_output_format'):
            tool._output_format = args.format
            logger.debug(f"Set tool output_format to: {tool._output_format}")
        else:
            logger.debug("TextCleaner tool does not support output_format configuration")

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
