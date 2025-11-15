"""
JSON Fixer for the annotation toolkit.

This module provides a general solution for fixing common JSON syntax issues.
"""

import json
import logging
import re
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union
import time
from functools import wraps

from ...config import Config

# Configure a specific logger for JSON fixing
json_fixer_logger = logging.getLogger("annotation_toolkit.json_fixer")

# Get the debug_logging configuration
config = Config()
debug_logging = config.get("tools", "json_fixer", "debug_logging", default=False)

# Set the logging level based on the configuration
if debug_logging:
    json_fixer_logger.setLevel(logging.DEBUG)
else:
    json_fixer_logger.setLevel(logging.INFO)

# Add a file handler to save detailed logs
try:
    # Use the save directory from configuration or a temp directory
    import tempfile

    # Try to get logs directory from config, fallback to temp dir
    logs_dir = config.get("data", "save_directory", default=None)
    if logs_dir:
        project_logs_dir = Path(logs_dir) / "logs"
    else:
        # Use system temp directory as fallback
        project_logs_dir = Path(tempfile.gettempdir()) / "annotation_toolkit" / "logs"

    if not project_logs_dir.exists():
        project_logs_dir.mkdir(parents=True, exist_ok=True)

    # Create a file handler for JSON fixing logs
    json_log_file = project_logs_dir / "json_fixer.log"

    file_handler = logging.FileHandler(json_log_file, mode="a")

    # Set the logging level for the file handler
    if debug_logging:
        file_handler.setLevel(logging.DEBUG)
    else:
        file_handler.setLevel(logging.INFO)

    # Create a formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    # Add the handler to the logger
    json_fixer_logger.addHandler(file_handler)

    # Also add a console handler for immediate feedback
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    if debug_logging:
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.INFO)
    json_fixer_logger.addHandler(console_handler)

    json_fixer_logger.info(f"JSON fixer logger initialized (debug={debug_logging})")
except Exception as e:
    # If logging setup fails, continue without file logging
    json_fixer_logger.info(f"File logging disabled: {str(e)}")
    pass


class TokenType(Enum):
    """Token types for JSON parsing."""

    STRING = "STRING"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    NULL = "NULL"
    OBJECT_START = "OBJECT_START"
    OBJECT_END = "OBJECT_END"
    ARRAY_START = "ARRAY_START"
    ARRAY_END = "ARRAY_END"
    COLON = "COLON"
    COMMA = "COMMA"
    WHITESPACE = "WHITESPACE"
    IDENTIFIER = "IDENTIFIER"  # For unquoted strings
    UNKNOWN = "UNKNOWN"


class Token:
    """Token class for JSON parsing."""

    def __init__(self, token_type: TokenType, value: str, position: int):
        self.type = token_type
        self.value = value
        self.position = position

    def __repr__(self) -> str:
        return f"Token({self.type}, '{self.value}', {self.position})"


def retry_with_backoff(max_retries: int = 3, base_delay: float = 0.1,
                       max_delay: float = 2.0, exponential_base: float = 2.0):
    """
    Decorator for retrying a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts.
        base_delay: Initial delay between retries in seconds.
        max_delay: Maximum delay between retries in seconds.
        exponential_base: Base for exponential backoff calculation.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if attempt < max_retries - 1:
                        # Calculate delay with exponential backoff
                        delay = min(base_delay * (exponential_base ** attempt), max_delay)

                        # Log retry attempt
                        json_fixer_logger.debug(
                            f"Retry attempt {attempt + 1}/{max_retries} after {delay:.2f}s delay. "
                            f"Error: {str(e)}"
                        )

                        time.sleep(delay)
                    else:
                        # Last attempt failed
                        json_fixer_logger.warning(
                            f"All {max_retries} retry attempts failed. Last error: {str(e)}"
                        )

            # Re-raise the last exception
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


class JsonFixer:
    """
    A general solution for fixing common JSON syntax issues.

    This class uses a tokenizer-based approach to parse and fix JSON,
    handling common issues like missing quotes, missing commas, and
    unescaped special characters.
    """

    def __init__(self, debug: bool = None, max_retries: int = 3,
                 enable_retry: bool = True):
        """
        Initialize the JsonFixer.

        Args:
            debug: Whether to enable debug logging. If None, use the configuration value.
            max_retries: Maximum number of retry attempts for fixing operations.
            enable_retry: Whether to enable automatic retry with exponential backoff.
        """
        # Use the provided debug value if specified, otherwise use the configuration
        self.debug = (
            debug
            if debug is not None
            else config.get("tools", "json_fixer", "debug_logging", default=False)
        )
        self.fixes_applied = []
        self.max_retries = max_retries
        self.enable_retry = enable_retry

        # Set the logging level based on the debug flag
        if self.debug:
            json_fixer_logger.setLevel(logging.DEBUG)
            for handler in json_fixer_logger.handlers:
                handler.setLevel(logging.DEBUG)
            # Force a debug message to verify logging is working
            json_fixer_logger.debug("Debug logging enabled for this JsonFixer instance")
            # Also print to stdout for immediate feedback
            print("Debug logging enabled for JsonFixer")

    def fix(self, text: str) -> str:
        """
        Fix common JSON syntax issues in the given text.

        Args:
            text: The JSON text to fix.

        Returns:
            The fixed JSON text.
        """
        self.fixes_applied = []

        # Log the input text
        if self.debug:
            json_fixer_logger.debug(f"Input text: {text[:100]}...")
            # Also print to stdout for immediate feedback
            print(f"JsonFixer input text: {text[:50]}...")

        # First, clean the input text
        text = self._clean_input(text)

        if self.debug:
            json_fixer_logger.debug(f"After cleaning: {text[:100]}...")

        # Apply pre-tokenization fixes for common patterns
        text = self._apply_pre_tokenization_fixes(text)

        if self.debug:
            json_fixer_logger.debug(f"After pre-tokenization fixes: {text[:100]}...")

        # Tokenize the text
        tokens = list(self._tokenize(text))

        if self.debug:
            json_fixer_logger.debug(f"Tokenized {len(tokens)} tokens")
            # Log the first few tokens
            for i, token in enumerate(tokens[:10]):
                json_fixer_logger.debug(f"Token {i}: {token}")

        # Fix common issues
        fixed_tokens = self._fix_tokens(tokens)

        if self.debug:
            json_fixer_logger.debug(f"Fixed tokens: {len(fixed_tokens)} tokens")
            # Log any differences in token count
            if len(tokens) != len(fixed_tokens):
                json_fixer_logger.debug(
                    f"Token count changed: {len(tokens)} -> {len(fixed_tokens)}"
                )

        # Reconstruct the JSON text
        fixed_text = self._reconstruct_json(fixed_tokens)

        if self.debug:
            json_fixer_logger.debug(f"Reconstructed text: {fixed_text[:100]}...")

        # Apply post-reconstruction fixes
        fixed_text = self._apply_post_reconstruction_fixes(fixed_text)

        if self.debug:
            json_fixer_logger.debug(
                f"After post-reconstruction fixes: {fixed_text[:100]}..."
            )

        # Log the fixes applied
        if self.fixes_applied:
            json_fixer_logger.info(f"Applied {len(self.fixes_applied)} fixes:")
            for fix in self.fixes_applied:
                json_fixer_logger.info(f"  - {fix}")
                if self.debug:
                    # Also print to stdout for immediate feedback
                    print(f"Applied fix: {fix}")

        # Validate the fixed JSON
        try:
            json.loads(fixed_text)
            json_fixer_logger.info("Fixed JSON is valid")
            if self.debug:
                json_fixer_logger.debug("JSON validation successful")
        except json.JSONDecodeError as e:
            json_fixer_logger.warning(f"Fixed JSON is still invalid: {str(e)}")
            if self.debug:
                # Log more details about the error
                json_fixer_logger.debug(f"JSON error details: {e}")
                # Log the context around the error
                if hasattr(e, "pos") and e.pos > 0:
                    start_pos = max(0, e.pos - 20)
                    end_pos = min(len(fixed_text), e.pos + 20)
                    context = fixed_text[start_pos:end_pos]
                    json_fixer_logger.debug(f"Error context: ...{context}...")
                    # Also print to stdout for immediate feedback
                    print(f"JSON error at position {e.pos}: {context}")

            # Try one more aggressive fix if validation failed
            try:
                fixed_text = self._apply_aggressive_fixes(fixed_text, e)
                # Validate again
                json.loads(fixed_text)
                json_fixer_logger.info("JSON fixed with aggressive fixes")
                self.fixes_applied.append("Applied aggressive fixes")
            except json.JSONDecodeError as e2:
                json_fixer_logger.warning(f"Aggressive fixes failed: {str(e2)}")

        return fixed_text

    def _clean_input(self, text: str) -> str:
        """
        Clean the input text to handle common formatting issues.

        Args:
            text: The input text to clean.

        Returns:
            The cleaned text.
        """
        if self.debug:
            json_fixer_logger.debug(f"Cleaning input text: {text[:50]}...")

        # Check if the input is a code block with backticks
        if text.startswith("```") and text.endswith("```"):
            # Extract content from code block
            lines = text.split("\n")
            if len(lines) > 2:  # At least 3 lines (opening, content, closing)
                # Remove first and last lines (backticks)
                text = "\n".join(lines[1:-1])
                if self.debug:
                    json_fixer_logger.debug("Removed code block backticks (multiline)")
                self.fixes_applied.append("Removed code block backticks (multiline)")
            else:
                # Just remove backticks if it's a single line
                text = text.strip("`")
                if self.debug:
                    json_fixer_logger.debug(
                        "Removed code block backticks (single line)"
                    )
                self.fixes_applied.append("Removed code block backticks (single line)")

        # Handle potential Unicode issues
        text = text.replace("\u2028", " ").replace("\u2029", " ")

        # Handle special characters that might cause issues
        text = text.replace("\u200b", "")  # Zero-width space
        text = text.replace("\ufeff", "")  # Zero-width no-break space (BOM)

        # Fix common encoding issues with Latin characters
        encoding_fixes = {
            "√≠": "í",
            "√≥": "ó",
            "√°": "á",
            "√©": "é",
            "√±": "ñ",
            "√∫": "ú",
            "√º": "ü",
            "√Å": "Á",
            "√â": "É",
            "√ç": "Í",
            "√ì": "Ó",
            "√ö": "Ú",
            "√ë": "Ñ",
        }

        for wrong, correct in encoding_fixes.items():
            if wrong in text:
                text = text.replace(wrong, correct)
                self.fixes_applied.append(f"Fixed encoding: {wrong} -> {correct}")
                if self.debug:
                    json_fixer_logger.debug(f"Fixed encoding: {wrong} -> {correct}")

        # Special handling for problematic sections with hash symbols and XML-like tags
        # This is a more targeted approach than just escaping all control characters

        # First, identify problematic sections
        problematic_sections = []

        # Find sections with hash symbols
        hash_matches = re.finditer(r'###[^"]*###', text)
        for match in hash_matches:
            start, end = match.span()
            problematic_sections.append((start, end, match.group(0)))
            if self.debug:
                json_fixer_logger.debug(
                    f"Found problematic hash section: {match.group(0)[:30]}..."
                )

        # Find sections with XML-like tags
        xml_matches = re.finditer(
            r"<[A-Za-z_][A-Za-z0-9_]*>[^<]*</[A-Za-z_][A-Za-z0-9_]*>", text
        )
        for match in xml_matches:
            start, end = match.span()
            problematic_sections.append((start, end, match.group(0)))
            if self.debug:
                json_fixer_logger.debug(
                    f"Found problematic XML-like section: {match.group(0)[:30]}..."
                )

        # Sort problematic sections by start position
        problematic_sections.sort()

        # Replace problematic sections with escaped versions
        if problematic_sections:
            result = ""
            last_end = 0

            for start, end, section in problematic_sections:
                # Add text before this section
                result += text[last_end:start]

                # Escape special characters in this section
                escaped_section = section

                # Escape hash symbols
                escaped_section = escaped_section.replace("#", "\\u0023")

                # Escape < and > in XML-like tags
                escaped_section = escaped_section.replace("<", "\\u003C")
                escaped_section = escaped_section.replace(">", "\\u003E")

                # Add the escaped section
                result += escaped_section
                last_end = end

            # Add any remaining text
            result += text[last_end:]
            text = result

            self.fixes_applied.append(
                "Escaped special characters in problematic sections"
            )
            if self.debug:
                json_fixer_logger.debug(
                    "Escaped special characters in problematic sections"
                )

        # Properly escape control characters in JSON strings
        def escape_control_chars(match):
            content = match.group(1)
            # Replace control characters with their escaped versions
            for i in range(32):
                if i not in (9, 10, 13):  # Tab, LF, CR are allowed in JSON strings
                    char = chr(i)
                    escaped = f"\\u{i:04x}"
                    content = content.replace(char, escaped)

            # Also handle specific problematic characters
            content = content.replace("\n", "\\n")
            content = content.replace("\r", "\\r")
            content = content.replace("\t", "\\t")
            content = content.replace("\b", "\\b")
            content = content.replace("\f", "\\f")

            return f'"{content}"'

        # Apply the escaping to all string literals in the JSON
        text = re.sub(r'"([^"\\]*(?:\\.[^"\\]*)*)"', escape_control_chars, text)
        self.fixes_applied.append("Escaped control characters in JSON strings")

        # Handle trailing commas in objects and arrays
        text = re.sub(r",\s*}", "}", text)
        text = re.sub(r",\s*]", "]", text)

        if self.debug:
            json_fixer_logger.debug(f"Cleaned text: {text[:50]}...")

        return text

    def validate(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Validate the JSON text.

        Args:
            text: The JSON text to validate.

        Returns:
            A tuple of (is_valid, error_message).
        """
        try:
            json.loads(text)
            return True, None
        except json.JSONDecodeError as e:
            return False, str(e)

    def _fix_with_python_object(self, text: str) -> str:
        """
        Fix a JSON string by converting it to a Python object and back.

        This approach uses Python's built-in json.dumps function to properly
        escape special characters in the JSON string.

        Args:
            text: The JSON string to fix.

        Returns:
            The fixed JSON string.
        """
        if self.debug:
            json_fixer_logger.debug("Fixing JSON with Python object approach")

        try:
            # First, clean the input text to handle basic formatting issues
            cleaned_text = self._clean_input(text)

            # Handle unterminated strings directly
            # This is a common issue that can prevent the JSON from being parsed
            def fix_unterminated_strings(text):
                # Count quotes in the text
                quote_count = text.count('"')
                # If there's an odd number of quotes, we have unterminated strings
                if quote_count % 2 == 1:
                    # Find all string starts
                    string_starts = []
                    in_string = False
                    escaped = False
                    for i, char in enumerate(text):
                        if char == '"' and not escaped:
                            if in_string:
                                in_string = False
                            else:
                                in_string = True
                                string_starts.append(i)
                        escaped = char == "\\" and not escaped

                    # If we're still in a string at the end, add a closing quote
                    if in_string and string_starts:
                        last_start = string_starts[-1]
                        # Find where to add the closing quote (before the next structural character)
                        for i in range(last_start + 1, len(text)):
                            if text[i] in ",{}[]":
                                text = text[:i] + '"' + text[i:]
                                break
                        else:
                            # If no structural character found, add at the end
                            text += '"'

                return text

            # Fix unterminated strings
            cleaned_text = fix_unterminated_strings(cleaned_text)

            # Try to extract a valid JSON object from the string
            match = re.search(r"(\{.*\})", cleaned_text, re.DOTALL)
            if match:
                json_obj_str = match.group(1)

                # Try to parse the JSON object
                try:
                    parsed = json.loads(json_obj_str)

                    # Use json.dumps to properly escape everything
                    fixed_json = json.dumps(parsed)

                    self.fixes_applied.append("Fixed JSON using Python object approach")
                    if self.debug:
                        json_fixer_logger.debug(
                            "Fixed JSON using Python object approach"
                        )

                    return fixed_json
                except json.JSONDecodeError as e:
                    if self.debug:
                        json_fixer_logger.debug(f"JSON object parsing failed: {e}")

                    # Try a more direct approach for chat history format
                    chat_history_match = re.search(
                        r'"chat_history"\s*:\s*\[(.*)\]', json_obj_str, re.DOTALL
                    )
                    if chat_history_match:
                        try:
                            # Extract the chat history array content
                            chat_history_str = chat_history_match.group(1)

                            # Split into individual messages
                            messages = []
                            message_pattern = r"\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}"
                            message_matches = re.finditer(
                                message_pattern, chat_history_str
                            )

                            for match in message_matches:
                                message_str = match.group(0)
                                try:
                                    # Try to parse each message
                                    message = json.loads(message_str)
                                    messages.append(message)
                                except json.JSONDecodeError:
                                    # If parsing fails, extract content and role manually
                                    content_match = re.search(
                                        r'"content"\s*:\s*"([^"]*)"', message_str
                                    )
                                    role_match = re.search(
                                        r'"role"\s*:\s*"([^"]*)"', message_str
                                    )

                                    if content_match and role_match:
                                        content = content_match.group(1)
                                        role = role_match.group(1)
                                        messages.append(
                                            {"content": content, "role": role}
                                        )

                            if messages:
                                # Create a new object with the fixed chat history
                                obj = {"chat_history": messages}

                                # Use json.dumps to properly escape everything
                                fixed_json = json.dumps(obj)

                                self.fixes_applied.append(
                                    "Fixed JSON by reconstructing chat history"
                                )
                                if self.debug:
                                    json_fixer_logger.debug(
                                        "Fixed JSON by reconstructing chat history"
                                    )

                                return fixed_json
                        except Exception as e:
                            if self.debug:
                                json_fixer_logger.debug(
                                    f"Chat history reconstruction failed: {e}"
                                )

                    # If chat history approach fails, try to extract and fix the content field
                    content_match = re.search(
                        r'"content"\s*:\s*"(.*?)"(?=,|\s*})', json_obj_str, re.DOTALL
                    )
                    if content_match:
                        content = content_match.group(1)

                        # Create a Python dictionary with the extracted content
                        obj = {"content": content}

                        # Use json.dumps to properly escape everything
                        fixed_json = json.dumps(obj)

                        self.fixes_applied.append(
                            "Fixed JSON by extracting and escaping content"
                        )
                        if self.debug:
                            json_fixer_logger.debug(
                                "Fixed JSON by extracting and escaping content"
                            )

                        return fixed_json

            # If we couldn't extract a valid JSON object, try a more aggressive approach
            # Look for key-value pairs and construct a Python dictionary
            pairs = re.findall(r'"([^"]+)"\s*:\s*"([^"]*)"', cleaned_text)
            if pairs:
                obj = {key: value for key, value in pairs}

                # Use json.dumps to properly escape everything
                fixed_json = json.dumps(obj)

                self.fixes_applied.append("Fixed JSON by extracting key-value pairs")
                if self.debug:
                    json_fixer_logger.debug("Fixed JSON by extracting key-value pairs")

                return fixed_json

            # If all else fails, return the cleaned text
            return cleaned_text
        except Exception as e:
            if self.debug:
                json_fixer_logger.debug(f"Error in _fix_with_python_object: {e}")
            return text

    def fix_and_parse(self, text: str) -> Any:
        """
        Fix the JSON text and parse it using the Python object approach.

        Args:
            text: The JSON text to fix and parse.

        Returns:
            The parsed JSON object.

        Raises:
            json.JSONDecodeError: If the JSON text cannot be fixed and parsed.
        """
        if self.enable_retry:
            return self._fix_and_parse_with_retry(text)
        else:
            return self._fix_and_parse_internal(text)

    @retry_with_backoff(max_retries=3, base_delay=0.1, max_delay=1.0)
    def _fix_and_parse_with_retry(self, text: str) -> Any:
        """Fix and parse with automatic retry on failure."""
        return self._fix_and_parse_internal(text)

    def _fix_and_parse_internal(self, text: str) -> Any:
        """Internal implementation of fix_and_parse."""
        if self.debug:
            json_fixer_logger.debug(f"Starting fix_and_parse with text: {text[:50]}...")

        # First try to parse the text directly
        try:
            if self.debug:
                json_fixer_logger.debug("Attempting to parse input directly")
            return json.loads(text)
        except json.JSONDecodeError as e:
            if self.debug:
                json_fixer_logger.debug(f"Direct parsing failed: {e}")
                # Log the context around the error
                if hasattr(e, "pos") and e.pos > 0:
                    start_pos = max(0, e.pos - 20)
                    end_pos = min(len(text), e.pos + 20)
                    context = text[start_pos:end_pos]
                    json_fixer_logger.debug(f"Error context: ...{context}...")

            # Try to fix the text using the Python object approach
            if self.debug:
                json_fixer_logger.debug("Attempting to fix with Python object approach")
            fixed_text = self._fix_with_python_object(text)

            # Try to parse the fixed text
            try:
                result = json.loads(fixed_text)
                if self.debug:
                    json_fixer_logger.debug("Successfully parsed fixed text")
                return result
            except json.JSONDecodeError as e:
                if self.debug:
                    json_fixer_logger.debug(f"Python object approach failed: {e}")

                    # As a last resort, try the original fix method
                    if self.debug:
                        json_fixer_logger.debug(
                            "Attempting to fix with original method"
                        )
                    fixed_text = self.fix(text)

                    try:
                        result = json.loads(fixed_text)
                        if self.debug:
                            json_fixer_logger.debug(
                                "Successfully parsed with original method"
                            )
                        return result
                    except json.JSONDecodeError as e:
                        if self.debug:
                            json_fixer_logger.debug(f"All fixing methods failed: {e}")
                        # Re-raise the exception
                        raise

    def _reconstruct_json(self, tokens: List[Token]) -> str:
        """
        Reconstruct the JSON text from the tokens.

        Args:
            tokens: The tokens to reconstruct.

        Returns:
            The reconstructed JSON text.
        """
        return "".join(token.value for token in tokens)

    def _apply_post_reconstruction_fixes(self, text: str) -> str:
        """
        Apply fixes to the text after reconstruction.

        This method handles issues that might still exist after tokenization
        and reconstruction, such as missing closing brackets and braces.

        Args:
            text: The text to fix.

        Returns:
            The fixed text.
        """
        if self.debug:
            json_fixer_logger.debug("Applying post-reconstruction fixes")

        # Count opening and closing brackets/braces
        open_curly = text.count("{")
        close_curly = text.count("}")
        open_square = text.count("[")
        close_square = text.count("]")

        # Fix missing closing braces
        if open_curly > close_curly:
            missing = open_curly - close_curly
            text += "}" * missing
            self.fixes_applied.append(f"Added {missing} missing closing braces")
            if self.debug:
                json_fixer_logger.debug(f"Added {missing} missing closing braces")

        # Fix missing closing brackets
        if open_square > close_square:
            missing = open_square - close_square
            text += "]" * missing
            self.fixes_applied.append(f"Added {missing} missing closing brackets")
            if self.debug:
                json_fixer_logger.debug(f"Added {missing} missing closing brackets")

        # Fix missing opening braces
        if close_curly > open_curly:
            missing = close_curly - open_curly
            text = "{" * missing + text
            self.fixes_applied.append(f"Added {missing} missing opening braces")
            if self.debug:
                json_fixer_logger.debug(f"Added {missing} missing opening braces")

        # Fix missing opening brackets
        if close_square > open_square:
            missing = close_square - open_square
            text = "[" * missing + text
            self.fixes_applied.append(f"Added {missing} missing opening brackets")
            if self.debug:
                json_fixer_logger.debug(f"Added {missing} missing opening brackets")

        # Fix trailing commas in objects and arrays (again, just to be sure)
        text = re.sub(r",\s*}", "}", text)
        text = re.sub(r",\s*]", "]", text)

        # Fix missing commas between elements (again, just to be sure)
        text = re.sub(r'("(?:[^"\\]|\\.)*")("(?:[^"\\]|\\.)*":)', r"\1,\2", text)

        return text

    def _apply_aggressive_fixes(self, text: str, error: json.JSONDecodeError) -> str:
        """
        Apply more aggressive fixes when standard fixes fail.

        This method is called when the standard fixes don't resolve all issues.
        It uses the error information to target specific problems.

        Args:
            text: The text to fix.
            error: The JSONDecodeError that occurred.

        Returns:
            The fixed text.
        """
        if self.debug:
            json_fixer_logger.debug(f"Applying aggressive fixes for error: {error}")

        error_msg = str(error)
        error_pos = getattr(error, "pos", 0)

        # Extract context around the error
        start_pos = max(0, error_pos - 20)
        end_pos = min(len(text), error_pos + 20)
        context = text[start_pos:end_pos]

        if self.debug:
            json_fixer_logger.debug(f"Error context: ...{context}...")

        # Handle specific error types
        if "Expecting ',' delimiter" in error_msg:
            # Insert a comma at the error position
            text = text[:error_pos] + "," + text[error_pos:]
            self.fixes_applied.append(f"Inserted missing comma at position {error_pos}")
            if self.debug:
                json_fixer_logger.debug(
                    f"Inserted missing comma at position {error_pos}"
                )

        elif "Expecting property name enclosed in double quotes" in error_msg:
            # Find the next non-whitespace character
            i = error_pos
            while i < len(text) and text[i].isspace():
                i += 1

            if i < len(text):
                # Find the end of the property name
                start = i
                while i < len(text) and text[i] not in ':{},[]"\n\r\t':
                    i += 1

                if i > start:
                    # Extract the property name
                    prop_name = text[start:i]
                    # Replace it with a quoted version
                    text = text[:start] + f'"{prop_name}"' + text[i:]
                    self.fixes_applied.append(
                        f"Added quotes around property name: {prop_name}"
                    )
                    if self.debug:
                        json_fixer_logger.debug(
                            f"Added quotes around property name: {prop_name}"
                        )

        elif "Expecting ':' delimiter" in error_msg:
            # Insert a colon at the error position
            text = text[:error_pos] + ":" + text[error_pos:]
            self.fixes_applied.append(f"Inserted missing colon at position {error_pos}")
            if self.debug:
                json_fixer_logger.debug(
                    f"Inserted missing colon at position {error_pos}"
                )

        elif "Expecting value" in error_msg:
            # Insert a placeholder value at the error position
            text = text[:error_pos] + '""' + text[error_pos:]
            self.fixes_applied.append(
                f"Inserted empty string value at position {error_pos}"
            )
            if self.debug:
                json_fixer_logger.debug(
                    f"Inserted empty string value at position {error_pos}"
                )

        elif "Extra data" in error_msg:
            # Truncate the text at the error position
            text = text[:error_pos]
            self.fixes_applied.append(f"Truncated extra data at position {error_pos}")
            if self.debug:
                json_fixer_logger.debug(f"Truncated extra data at position {error_pos}")

        elif "Unterminated string" in error_msg:
            # Find the start of the unterminated string
            i = error_pos
            while i >= 0 and text[i] != '"':
                i -= 1

            if i >= 0:
                # Add a closing quote after the string
                # First, find where the string should end (before the next structural character)
                j = error_pos
                while j < len(text) and text[j] not in ",{}[]":
                    j += 1

                text = text[:j] + '"' + text[j:]
                self.fixes_applied.append(
                    f"Added closing quote for unterminated string at position {i}"
                )
                if self.debug:
                    json_fixer_logger.debug(
                        f"Added closing quote for unterminated string at position {i}"
                    )

        # Apply general fixes that might help with any error

        # Fix common encoding issues that might have been missed
        text = text.replace('\\"', '"')  # Unescape quotes inside strings
        text = text.replace("\\\\", "\\")  # Unescape backslashes

        # Fix potential issues with control characters
        text = "".join(c for c in text if ord(c) >= 32 or c in "\n\r\t")

        # Try to balance brackets and braces
        open_curly = text.count("{")
        close_curly = text.count("}")
        open_square = text.count("[")
        close_square = text.count("]")

        if open_curly > close_curly:
            text += "}" * (open_curly - close_curly)
        if open_square > close_square:
            text += "]" * (open_square - close_square)

        return text

    def _fix_tokens(self, tokens: List[Token]) -> List[Token]:
        """
        Fix common issues in the token stream.

        Args:
            tokens: The tokens to fix.

        Returns:
            The fixed tokens.
        """
        fixed_tokens = []
        i = 0

        while i < len(tokens):
            token = tokens[i]

            # Fix unquoted identifiers
            if token.type == TokenType.IDENTIFIER:
                # Check if this is a field name in an object
                if i > 0 and i < len(tokens) - 1:
                    prev_token = tokens[i - 1]
                    next_token = tokens[i + 1]

                    # If it's after an object start or comma, and before a colon,
                    # it's likely a field name that should be quoted
                    if (
                        prev_token.type == TokenType.OBJECT_START
                        or prev_token.type == TokenType.COMMA
                    ) and next_token.type == TokenType.COLON:
                        fixed_tokens.append(
                            Token(TokenType.STRING, f'"{token.value}"', token.position)
                        )
                        self.fixes_applied.append(
                            f"Added quotes around field name: {token.value}"
                        )
                        i += 1
                        continue

                    # If it's after a colon, it's likely a string value that should be quoted
                    if prev_token.type == TokenType.COLON:
                        fixed_tokens.append(
                            Token(TokenType.STRING, f'"{token.value}"', token.position)
                        )
                        self.fixes_applied.append(
                            f"Added quotes around string value: {token.value}"
                        )
                        i += 1
                        continue

            # Fix missing commas between elements
            if i > 0 and i < len(tokens) - 1:
                prev_token = tokens[i - 1]

                # If we have a string followed by another string, or a string followed by an object/array start,
                # we're likely missing a comma
                if (
                    prev_token.type == TokenType.STRING
                    or prev_token.type == TokenType.NUMBER
                    or prev_token.type == TokenType.BOOLEAN
                    or prev_token.type == TokenType.NULL
                    or prev_token.type == TokenType.OBJECT_END
                    or prev_token.type == TokenType.ARRAY_END
                ) and (
                    token.type == TokenType.STRING
                    or token.type == TokenType.OBJECT_START
                    or token.type == TokenType.ARRAY_START
                ):

                    # Skip if there's already a comma or if we're in a key-value pair
                    if not (i > 1 and tokens[i - 2].type == TokenType.COLON):
                        fixed_tokens.append(
                            Token(
                                TokenType.COMMA,
                                ",",
                                prev_token.position + len(prev_token.value),
                            )
                        )
                        self.fixes_applied.append(
                            f"Added missing comma between {prev_token.value} and {token.value}"
                        )

            # Fix missing values after colons
            if token.type == TokenType.COLON and i == len(tokens) - 1:
                # If this is the last token, add a placeholder value
                fixed_tokens.append(token)  # Add the colon
                fixed_tokens.append(Token(TokenType.STRING, '""', token.position + 1))
                self.fixes_applied.append(
                    f"Added empty string after colon at position {token.position}"
                )
                i += 1
                continue
            elif token.type == TokenType.COLON and i < len(tokens) - 1:
                next_token = tokens[i + 1]
                # If the next token is not a value type, add a placeholder value
                if next_token.type not in [
                    TokenType.STRING,
                    TokenType.NUMBER,
                    TokenType.BOOLEAN,
                    TokenType.NULL,
                    TokenType.OBJECT_START,
                    TokenType.ARRAY_START,
                ]:
                    fixed_tokens.append(token)  # Add the colon
                    fixed_tokens.append(
                        Token(TokenType.STRING, '""', token.position + 1)
                    )
                    self.fixes_applied.append(
                        f"Added empty string after colon at position {token.position}"
                    )
                    i += 1  # Increment to avoid infinite loop
                    continue

            # Add the current token
            fixed_tokens.append(token)
            i += 1

        # Check if we need to add a value after the last colon
        if fixed_tokens and fixed_tokens[-1].type == TokenType.COLON:
            fixed_tokens.append(
                Token(TokenType.STRING, '""', fixed_tokens[-1].position + 1)
            )
            self.fixes_applied.append(
                f"Added empty string after final colon at position {fixed_tokens[-1].position}"
            )

        return fixed_tokens

    def _tokenize(self, text: str) -> Iterator[Token]:
        """
        Tokenize the JSON text.

        Args:
            text: The JSON text to tokenize.

        Yields:
            Tokens from the JSON text.
        """
        i = 0
        text_length = len(text)

        # Keep track of the last token type to handle special cases
        last_token_type = None

        while i < text_length:
            char = text[i]

            # Skip whitespace
            if char.isspace():
                start = i
                while i < text_length and text[i].isspace():
                    i += 1
                yield Token(TokenType.WHITESPACE, text[start:i], start)
                continue

            # Handle object start
            if char == "{":
                yield Token(TokenType.OBJECT_START, "{", i)
                last_token_type = TokenType.OBJECT_START
                i += 1
                continue

            # Handle object end
            if char == "}":
                yield Token(TokenType.OBJECT_END, "}", i)
                last_token_type = TokenType.OBJECT_END
                i += 1
                continue

            # Handle array start
            if char == "[":
                yield Token(TokenType.ARRAY_START, "[", i)
                last_token_type = TokenType.ARRAY_START
                i += 1
                continue

            # Handle array end
            if char == "]":
                yield Token(TokenType.ARRAY_END, "]", i)
                last_token_type = TokenType.ARRAY_END
                i += 1
                continue

            # Handle colon
            if char == ":":
                colon_pos = i
                yield Token(TokenType.COLON, ":", i)
                last_token_type = TokenType.COLON
                i += 1

                # Special handling for the case where a colon is followed by text without quotes
                # This is a common issue in the input we're seeing
                if i < text_length:
                    # Skip any whitespace
                    while i < text_length and text[i].isspace():
                        i += 1

                    # If we're not at the end and the next character is not a quote, object start, or array start
                    if (
                        i < text_length
                        and text[i] not in ['"', "{", "[", "n", "t", "f"]
                        and not text[i].isdigit()
                        and text[i] != "-"
                    ):
                        # This is likely an unquoted string value
                        start = i

                        # Find the end of this value (until comma, closing brace, or end of text)
                        while i < text_length and text[i] not in [",", "}", "]"]:
                            i += 1

                        # Extract the unquoted value
                        unquoted_value = text[start:i].strip()

                        if unquoted_value:
                            if self.debug:
                                json_fixer_logger.debug(
                                    f"Found unquoted value after colon: '{unquoted_value}'"
                                )

                            # Create a string token with quotes around the value
                            yield Token(TokenType.STRING, f'"{unquoted_value}"', start)
                            last_token_type = TokenType.STRING

                            # Add this fix to the list
                            self.fixes_applied.append(
                                f"Added quotes around unquoted value: {unquoted_value}"
                            )

                            # Continue with the next token
                            continue

                continue

            # Handle comma
            if char == ",":
                yield Token(TokenType.COMMA, ",", i)
                last_token_type = TokenType.COMMA
                i += 1
                continue

            # Handle string
            if char == '"':
                start = i
                i += 1
                escaped = False

                # Special handling for unterminated strings
                try:
                    while i < text_length:
                        if text[i] == "\\" and not escaped:
                            escaped = True
                        elif text[i] == '"' and not escaped:
                            i += 1
                            yield Token(TokenType.STRING, text[start:i], start)
                            last_token_type = TokenType.STRING
                            break
                        else:
                            escaped = False
                        i += 1

                    # If we reached the end of the text without finding a closing quote
                    if i >= text_length and start < text_length:
                        # This is an unterminated string
                        if self.debug:
                            json_fixer_logger.debug(
                                f"Found unterminated string starting at position {start}: {text[start:start+20]}..."
                            )

                        # Add a closing quote and yield the string token
                        unterminated_string = text[start:text_length] + '"'
                        yield Token(TokenType.STRING, unterminated_string, start)
                        last_token_type = TokenType.STRING

                        # Add this fix to the list
                        self.fixes_applied.append(
                            f"Added closing quote to unterminated string at position {start}"
                        )

                        # We've reached the end of the text
                        break
                except Exception as e:
                    # If there's an error processing the string, log it and continue
                    if self.debug:
                        json_fixer_logger.debug(
                            f"Error processing string at position {start}: {str(e)}"
                        )

                    # Try to recover by creating a string token with what we have
                    unterminated_string = (
                        text[start : min(start + 50, text_length)] + '"'
                    )
                    yield Token(TokenType.STRING, unterminated_string, start)
                    last_token_type = TokenType.STRING

                    # Add this fix to the list
                    self.fixes_applied.append(
                        f"Recovered from error in string at position {start}"
                    )

                    # Move past this part of the text
                    i = min(start + 50, text_length)

                continue

            # Handle number
            if char.isdigit() or char == "-":
                start = i
                i += 1

                # Integer part
                while i < text_length and text[i].isdigit():
                    i += 1

                # Decimal part
                if i < text_length and text[i] == ".":
                    i += 1
                    while i < text_length and text[i].isdigit():
                        i += 1

                # Exponent part
                if i < text_length and text[i] in "eE":
                    i += 1
                    if i < text_length and text[i] in "+-":
                        i += 1
                    while i < text_length and text[i].isdigit():
                        i += 1

                yield Token(TokenType.NUMBER, text[start:i], start)
                continue

            # Handle boolean and null
            if char in "tfn":
                if text[i : i + 4] == "true":
                    yield Token(TokenType.BOOLEAN, "true", i)
                    i += 4
                    continue
                elif text[i : i + 5] == "false":
                    yield Token(TokenType.BOOLEAN, "false", i)
                    i += 5
                    continue
                elif text[i : i + 4] == "null":
                    yield Token(TokenType.NULL, "null", i)
                    i += 4
                    continue

            # Handle unquoted identifiers (potential issue)
            if char.isalpha() or char == "_":
                start = i
                while i < text_length and (
                    text[i].isalnum() or text[i] == "_" or text[i] == " "
                ):
                    i += 1
                yield Token(TokenType.IDENTIFIER, text[start:i], start)
                continue

            # Handle unknown characters
            yield Token(TokenType.UNKNOWN, char, i)
            i += 1

    def _apply_pre_tokenization_fixes(self, text: str) -> str:
        """
        Apply fixes to the text before tokenization.

        This method handles common patterns that are easier to fix with regex
        before tokenization, such as missing commas between elements and
        unquoted string values.

        Args:
            text: The text to fix.

        Returns:
            The fixed text.
        """
        if self.debug:
            json_fixer_logger.debug("Applying pre-tokenization fixes")

        # Fix missing commas between string values and object keys
        # Pattern: "value""key": - should be "value","key":
        text = re.sub(r'("(?:[^"\\]|\\.)*")("(?:[^"\\]|\\.)*":)', r"\1,\2", text)

        # Fix missing commas between closing brackets and opening brackets or strings
        # Pattern: }{ or }[ or }"string" - should have a comma between them
        text = re.sub(r"([\}\]])([\{\[\"])(?!\s*[,\}\]])(?!\s*$)", r"\1,\2", text)

        # Fix unquoted field names in objects
        # Pattern: {key: or ,key: - should be {"key": or ,"key":
        text = re.sub(r"([\{\,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:", r'\1"\2":', text)

        # Fix unquoted string values after colons
        # Pattern: :"value" or : value - should be :"value" or : "value"
        # But don't match numbers, true, false, null, or objects/arrays
        def fix_unquoted_value(match):
            colon = match.group(1)
            value = match.group(2).strip()

            # Skip if it's already a valid JSON value
            if (
                value.startswith('"')
                or value.startswith("{")
                or value.startswith("[")
                or value == "true"
                or value == "false"
                or value == "null"
                or re.match(r"^-?\d+(\.\d+)?([eE][+-]?\d+)?$", value)
            ):
                return match.group(0)

            # Otherwise, quote it
            return f'{colon}"{value}"'

        text = re.sub(
            r'(:)\s*([^"{}\[\],\s][^{}\[\],]*?)(?=,|\}|\]|$)', fix_unquoted_value, text
        )

        # Fix missing quotes around keys with special characters
        # This is a more aggressive fix that might cause issues, so we only apply it if needed
        # Pattern: {"key-with-dash": - should have quotes around the key
        text = re.sub(r"([\{\,])\s*([a-zA-Z0-9_\-\.]+)\s*:", r'\1"\2":', text)

        # Fix dollar signs in strings that aren't properly escaped
        # Pattern: "price: $50" - should be "price: \$50"
        text = re.sub(r"(\$)(?=\d)", r"\\$", text)

        # Fix unterminated strings at the end of the text
        # Pattern: "unterminated - should be "unterminated"
        if '"' in text:
            # Count quotes in the text
            quote_count = text.count('"')
            # If there's an odd number of quotes, add a closing quote at the end
            if quote_count % 2 == 1:
                text += '"'
                self.fixes_applied.append("Added closing quote at the end of the text")
                if self.debug:
                    json_fixer_logger.debug(
                        "Added closing quote at the end of the text"
                    )

        return text
