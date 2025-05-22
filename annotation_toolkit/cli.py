"""
Command-line interface for the annotation toolkit.

This module provides a command-line interface for the annotation toolkit.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Sequence

from .config import Config
from .core.conversation.visualizer import JsonVisualizer
from .core.text.dict_to_bullet import DictToBulletList
from .ui.cli.commands import (
    run_dict_to_bullet_command,
    run_json_visualizer_command,
    run_text_cleaner_command,
)
from .utils import logger


def create_parser() -> argparse.ArgumentParser:
    """
    Create the command-line argument parser.

    Returns:
        argparse.ArgumentParser: The argument parser.
    """
    parser = argparse.ArgumentParser(
        description="Annotation Toolkit - A collection of tools for data annotation"
    )

    # Add version argument
    parser.add_argument(
        "--version", action="version", version="Annotation Toolkit v0.1.0"
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

    # GUI command
    gui_parser = subparsers.add_parser(
        "gui", help="Launch the graphical user interface"
    )

    return parser


def main(args: Optional[Sequence[str]] = None) -> int:
    """
    Main entry point for the command-line interface.

    Args:
        args (Optional[Sequence[str]]): Command-line arguments.
            If None, sys.argv[1:] is used.

    Returns:
        int: Exit code.
    """
    logger.info("Starting Annotation Toolkit CLI")
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
    except Exception as e:
        logger.exception(f"Failed to load configuration: {str(e)}")
        print(f"Error loading configuration: {str(e)}", file=sys.stderr)
        return 1

    # Process commands
    try:
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
        elif parsed_args.command == "gui":
            logger.info("Launching GUI application")
            # Import here to avoid circular imports
            from .ui.gui.app import run_application

            run_application()
            return 0
        else:
            logger.warning(f"Unknown command: {parsed_args.command}")
            parser.print_help()
            return 1
    except Exception as e:
        logger.exception(f"Error executing command {parsed_args.command}: {str(e)}")
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
