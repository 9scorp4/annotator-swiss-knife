"""
Streaming utilities for handling large files efficiently.

This module provides streaming parsers and processors to handle large files
without loading them entirely into memory.
"""

import json
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union, Callable
import io

from .errors import FileReadError, ParsingError
from .logger import get_logger

logger = get_logger()

# Try to import ijson for efficient streaming JSON parsing
try:
    import ijson
    IJSON_AVAILABLE = True
except ImportError:
    IJSON_AVAILABLE = False
    logger.info("ijson not available, using fallback streaming implementation")


class StreamingJSONParser:
    """Parser for streaming JSON data from large files."""

    def __init__(self, chunk_size: int = 8192):
        """
        Initialize the streaming JSON parser.

        Args:
            chunk_size: Size of chunks to read at a time in bytes.
        """
        self.chunk_size = chunk_size

    def parse_array_items(self, file_path: Union[str, Path]) -> Iterator[Any]:
        """
        Stream items from a JSON array file.

        Args:
            file_path: Path to the JSON file containing an array.

        Yields:
            Individual items from the JSON array.

        Raises:
            FileReadError: If the file cannot be read.
            ParsingError: If the JSON is invalid.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileReadError(str(file_path), suggestion="Ensure the file exists")

        if IJSON_AVAILABLE:
            yield from self._parse_with_ijson(file_path, 'item')
        else:
            yield from self._parse_array_fallback(file_path)

    def parse_object_items(self, file_path: Union[str, Path]) -> Iterator[tuple[str, Any]]:
        """
        Stream key-value pairs from a JSON object file.

        Args:
            file_path: Path to the JSON file containing an object.

        Yields:
            Tuples of (key, value) from the JSON object.

        Raises:
            FileReadError: If the file cannot be read.
            ParsingError: If the JSON is invalid.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileReadError(str(file_path), suggestion="Ensure the file exists")

        if IJSON_AVAILABLE:
            yield from self._parse_object_with_ijson(file_path)
        else:
            yield from self._parse_object_fallback(file_path)

    def _parse_with_ijson(self, file_path: Path, prefix: str) -> Iterator[Any]:
        """Use ijson to parse JSON efficiently."""
        try:
            with open(file_path, 'rb') as f:
                parser = ijson.items(f, prefix)
                for item in parser:
                    yield item
        except Exception as e:
            raise ParsingError(
                f"Failed to parse JSON file: {file_path}",
                details={"error": str(e)},
                cause=e
            )

    def _parse_object_with_ijson(self, file_path: Path) -> Iterator[tuple[str, Any]]:
        """Use ijson to parse JSON object efficiently."""
        try:
            with open(file_path, 'rb') as f:
                parser = ijson.kvitems(f, '')
                for key, value in parser:
                    yield (key, value)
        except Exception as e:
            raise ParsingError(
                f"Failed to parse JSON file: {file_path}",
                details={"error": str(e)},
                cause=e
            )

    def _parse_array_fallback(self, file_path: Path) -> Iterator[Any]:
        """Fallback streaming implementation for JSON arrays."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Skip to the start of the array
                char = ''
                while char != '[':
                    char = f.read(1)
                    if not char:
                        raise ParsingError("No JSON array found in file")

                buffer = ''
                depth = 0
                in_string = False
                escape_next = False

                while True:
                    char = f.read(1)
                    if not char:
                        break

                    if escape_next:
                        buffer += char
                        escape_next = False
                        continue

                    if char == '\\' and in_string:
                        escape_next = True
                        buffer += char
                        continue

                    if char == '"' and not escape_next:
                        in_string = not in_string
                        buffer += char
                        continue

                    if not in_string:
                        if char in '[{':
                            depth += 1
                            buffer += char
                        elif char in ']}':
                            if char == ']' and depth == 0:
                                # End of main array
                                if buffer.strip():
                                    # Parse remaining item
                                    try:
                                        yield json.loads(buffer)
                                    except json.JSONDecodeError:
                                        pass
                                break
                            else:
                                depth -= 1
                                buffer += char
                        elif char == ',' and depth == 0:
                            # End of an item
                            if buffer.strip():
                                try:
                                    yield json.loads(buffer)
                                except json.JSONDecodeError as e:
                                    logger.warning(f"Failed to parse item: {e}")
                                buffer = ''
                        else:
                            buffer += char
                    else:
                        buffer += char

        except Exception as e:
            raise FileReadError(
                str(file_path),
                details={"error": str(e)},
                cause=e
            )

    def _parse_object_fallback(self, file_path: Path) -> Iterator[tuple[str, Any]]:
        """Fallback streaming implementation for JSON objects."""
        # For simplicity, load the whole object for fallback
        # A full streaming implementation would be more complex
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    for key, value in data.items():
                        yield (key, value)
                else:
                    raise ParsingError("File does not contain a JSON object")
        except Exception as e:
            raise ParsingError(
                f"Failed to parse JSON file: {file_path}",
                details={"error": str(e)},
                cause=e
            )


class ChunkedFileProcessor:
    """Process large files in chunks."""

    def __init__(self, chunk_size: int = 1024 * 1024):  # 1MB chunks
        """
        Initialize the chunked file processor.

        Args:
            chunk_size: Size of chunks to process at a time in bytes.
        """
        self.chunk_size = chunk_size

    def process_file(self, file_path: Union[str, Path],
                     processor: Callable[[str], Any],
                     encoding: str = 'utf-8') -> Iterator[Any]:
        """
        Process a file in chunks.

        Args:
            file_path: Path to the file.
            processor: Function to process each chunk.
            encoding: File encoding.

        Yields:
            Results from processing each chunk.

        Raises:
            FileReadError: If the file cannot be read.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileReadError(str(file_path), suggestion="Ensure the file exists")

        try:
            with open(file_path, 'r', encoding=encoding) as f:
                while True:
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break

                    result = processor(chunk)
                    if result is not None:
                        yield result
        except Exception as e:
            raise FileReadError(
                str(file_path),
                details={"error": str(e)},
                cause=e
            )

    def process_lines(self, file_path: Union[str, Path],
                      processor: Callable[[str], Any],
                      encoding: str = 'utf-8',
                      skip_empty: bool = True) -> Iterator[Any]:
        """
        Process a file line by line.

        Args:
            file_path: Path to the file.
            processor: Function to process each line.
            encoding: File encoding.
            skip_empty: Whether to skip empty lines.

        Yields:
            Results from processing each line.

        Raises:
            FileReadError: If the file cannot be read.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileReadError(str(file_path), suggestion="Ensure the file exists")

        try:
            with open(file_path, 'r', encoding=encoding) as f:
                for line in f:
                    if skip_empty and not line.strip():
                        continue

                    result = processor(line)
                    if result is not None:
                        yield result
        except Exception as e:
            raise FileReadError(
                str(file_path),
                details={"error": str(e)},
                cause=e
            )


class StreamingTextCleaner:
    """Clean text files in a streaming manner."""

    def __init__(self, chunk_size: int = 8192):
        """
        Initialize the streaming text cleaner.

        Args:
            chunk_size: Size of chunks to process at a time.
        """
        self.chunk_size = chunk_size
        self.processor = ChunkedFileProcessor(chunk_size)

    def clean_file(self, file_path: Union[str, Path],
                   output_path: Optional[Union[str, Path]] = None) -> Optional[str]:
        """
        Clean a text file in a streaming manner.

        Args:
            file_path: Path to the input file.
            output_path: Path to save cleaned output. If None, returns as string.

        Returns:
            Cleaned text if output_path is None, otherwise None.

        Raises:
            FileReadError: If the input file cannot be read.
            FileWriteError: If the output file cannot be written.
        """
        file_path = Path(file_path)

        if output_path:
            output_path = Path(output_path)
            output_file = open(output_path, 'w', encoding='utf-8')
        else:
            output_file = io.StringIO()

        try:
            # Process file line by line
            for cleaned_line in self.processor.process_lines(
                file_path,
                self._clean_line
            ):
                output_file.write(cleaned_line + '\n')

            if output_path:
                output_file.close()
                logger.info(f"Cleaned file saved to: {output_path}")
                return None
            else:
                output_file.seek(0)
                return output_file.read()

        except Exception as e:
            if output_path and not output_file.closed:
                output_file.close()
            raise
        finally:
            if not output_path:
                output_file.close()

    def _clean_line(self, line: str) -> Optional[str]:
        """Clean a single line of text."""
        # Remove leading/trailing whitespace
        cleaned = line.strip()

        # Skip empty lines
        if not cleaned:
            return None

        # Remove control characters
        control_chars = ''.join(chr(i) for i in range(32) if chr(i) not in ['\n', '\t'])
        cleaned = cleaned.translate(str.maketrans('', '', control_chars))

        # Remove null bytes
        cleaned = cleaned.replace('\x00', '')

        return cleaned


# Create global instances
default_json_parser = StreamingJSONParser()
default_chunk_processor = ChunkedFileProcessor()
default_text_cleaner = StreamingTextCleaner()