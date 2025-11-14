"""
Command-line interface for the annotation swiss knife.

This module provides a command-line interface for the annotation swiss knife.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Sequence

from .config import Config
from .core.conversation.visualizer import JsonVisualizer
from .core.text.dict_to_bullet import DictToBulletList
from .di import get_container, resolve, DIContainer, ConfigInterface
from .di.bootstrap import bootstrap_application, validate_container_configuration
from .ui.cli.commands import (
    run_conversation_generator_command,
    run_dict_to_bullet_command,
    run_json_visualizer_command,
    run_text_cleaner_command,
    run_text_collector_command,
)
from .utils import logger
from .utils.error_handler import (
    format_error_for_user,
    handle_errors,
    with_error_handling,
)
from .utils.errors import (
    AnnotationToolkitError,
    ConfigurationError,
    ErrorCode,
    FileNotFoundError as ATFileNotFoundError,
    FileReadError,
    ParsingError,
    ProcessingError,
)


def create_parser() -> argparse.ArgumentParser:
    """
    Create the command-line argument parser.

    Returns:
        argparse.ArgumentParser: The argument parser.
    """
    parser = argparse.ArgumentParser(
        description="Annotation Swiss Knife - A comprehensive swiss knife for data annotation tasks"
    )

    # Add version argument
    parser.add_argument(
        "--version", action="version", version="Annotation Swiss Knife v0.1.0"
    )

    # Add config file argument
    parser.add_argument("--config", "-c", help="Path to a configuration file")

    # Add subparsers for the different tools
    subparsers = parser.add_subparsers(dest="command", help="Tool to use")

    # Dictionary to Bullet List command
    dict_parser = subparsers.add_parser(
        "dict2bullet", help="Convert a dictionary to a bullet list"
    )
    dict_parser.add_argument(
        "input_file", help="Path to the input JSON file containing the dictionary"
    )
    dict_parser.add_argument(
        "--output", "-o", help="Path to save the output file (default: print to stdout)"
    )
    dict_parser.add_argument(
        "--format",
        "-f",
        choices=["text", "markdown"],
        default="markdown",
        help="Output format (default: markdown)",
    )

    # JSON Visualizer command
    conv_parser = subparsers.add_parser(
        "jsonvis", help="Visualize JSON data including conversations"
    )
    conv_parser.add_argument(
        "input_file", help="Path to the input JSON file containing the conversation"
    )
    conv_parser.add_argument(
        "--output", "-o", help="Path to save the output file (default: print to stdout)"
    )
    conv_parser.add_argument(
        "--format",
        "-f",
        choices=["text", "markdown"],
        default="text",
        help="Output format (default: text)",
    )
    conv_parser.add_argument(
        "--search", "-s", help="Search for a specific text in the conversation"
    )
    conv_parser.add_argument(
        "--case-sensitive", action="store_true", help="Use case-sensitive search"
    )

    # Text Cleaner command
    text_cleaner_parser = subparsers.add_parser(
        "textclean", help="Clean text from markdown/JSON/code artifacts"
    )
    text_cleaner_parser.add_argument(
        "input_file", help="Path to the input file containing the text to clean"
    )
    text_cleaner_parser.add_argument(
        "--output", "-o", help="Path to save the output file (default: print to stdout)"
    )
    text_cleaner_parser.add_argument(
        "--format",
        "-f",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)",
    )

    # Conversation Generator command
    convgen_parser = subparsers.add_parser(
        "convgen", help="Generate AI conversation JSON from turn pairs"
    )
    convgen_parser.add_argument(
        "input_file",
        help='Path to input JSON file with format: {"turns": [{"user": "...", "assistant": "..."}, ...]}'
    )
    convgen_parser.add_argument(
        "--output", "-o", help="Path to save the output JSON file (default: print to stdout)"
    )
    convgen_parser.add_argument(
        "--format",
        "-f",
        choices=["pretty", "compact"],
        default="pretty",
        help="JSON output format (default: pretty)",
    )

    # Text Collector command
    textcollect_parser = subparsers.add_parser(
        "textcollect", help="Collect text from multiple fields into a JSON list"
    )
    textcollect_parser.add_argument(
        "input_file",
        help="Path to input text file (one text item per line)"
    )
    textcollect_parser.add_argument(
        "--output", "-o", help="Path to save the output JSON file (default: print to stdout)"
    )
    textcollect_parser.add_argument(
        "--format",
        "-f",
        choices=["pretty", "compact"],
        default="pretty",
        help="JSON output format (default: pretty)",
    )

    # GUI command
    gui_parser = subparsers.add_parser(
        "gui", help="Launch the graphical user interface"
    )

    return parser


@with_error_handling(
    error_code=ErrorCode.PROCESSING_ERROR,
    error_message="Error executing command",
    suggestion="Check the command arguments and ensure they are valid.",
)
def execute_command(parsed_args: argparse.Namespace, config: Config) -> int:
    """
    Execute the selected command.

    Args:
        parsed_args: The parsed command-line arguments.
        config: The application configuration.

    Returns:
        int: Exit code.

    Raises:
        ProcessingError: If there's an error executing the command.
    """
    if parsed_args.command == "dict2bullet":
        logger.info(
            f"Running dict2bullet command with input file: {parsed_args.input_file}"
        )
        return run_dict_to_bullet_command(parsed_args, config)
    elif parsed_args.command == "jsonvis":
        logger.info(
            f"Running jsonvis command with input file: {parsed_args.input_file}"
        )
        return run_json_visualizer_command(parsed_args, config)
    elif parsed_args.command == "textclean":
        logger.info(
            f"Running textclean command with input file: {parsed_args.input_file}"
        )
        return run_text_cleaner_command(parsed_args, config)
    elif parsed_args.command == "convgen":
        logger.info(
            f"Running convgen command with input file: {parsed_args.input_file}"
        )
        return run_conversation_generator_command(parsed_args, config)
    elif parsed_args.command == "textcollect":
        logger.info(
            f"Running textcollect command with input file: {parsed_args.input_file}"
        )
        return run_text_collector_command(parsed_args, config)
    elif parsed_args.command == "gui":
        logger.info("Launching GUI application")
        # Import here to avoid circular imports
        from .ui.gui.app import run_application

        run_application()
        return 0
    else:
        logger.warning(f"Unknown command: {parsed_args.command}")
        raise ProcessingError(
            f"Unknown command: {parsed_args.command}",
            error_code=ErrorCode.INVALID_INPUT,
            suggestion="Use one of the available commands: dict2bullet, jsonvis, textclean, convgen, textcollect, or gui.",
        )


def main(args: Optional[Sequence[str]] = None) -> int:
    """
    Main entry point for the command-line interface.

    Args:
        args (Optional[Sequence[str]]): Command-line arguments.
            If None, sys.argv[1:] is used.

    Returns:
        int: Exit code.
    """
    logger.info("Starting Annotation Swiss Knife CLI")
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Log the command being executed
    if parsed_args.command:
        logger.info(f"Command selected: {parsed_args.command}")
    else:
        logger.info("No command specified, showing help")
        parser.print_help()
        return 0

    # Load configuration
    try:
        if parsed_args.config:
            logger.info(f"Loading configuration from {parsed_args.config}")
            config = Config(parsed_args.config)
        else:
            logger.info("Loading default configuration")
            config = Config()
        logger.debug(f"Configuration loaded successfully")
    except AnnotationToolkitError as e:
        # Format the error for display to the user
        error_message = format_error_for_user(e)
        logger.error(f"Failed to load configuration: {error_message}")
        print(f"Error loading configuration: {error_message}", file=sys.stderr)
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error loading configuration: {str(e)}")
        print(f"Unexpected error loading configuration: {str(e)}", file=sys.stderr)
        return 1

    # Process commands
    try:
        if not parsed_args.command:
            parser.print_help()
            return 0

        return execute_command(parsed_args, config)
    except AnnotationToolkitError as e:
        # Format the error for display to the user
        error_message = format_error_for_user(e)
        logger.error(f"Error executing command {parsed_args.command}: {error_message}")
        print(f"Error: {error_message}", file=sys.stderr)
        return 1
    except Exception as e:
        logger.exception(
            f"Unexpected error executing command {parsed_args.command}: {str(e)}"
        )
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
