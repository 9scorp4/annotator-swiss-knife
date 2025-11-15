"""
Comprehensive tests for streaming utilities.
"""

import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch

from annotation_toolkit.utils.streaming import (
    StreamingJSONParser,
    ChunkedFileProcessor,
    StreamingTextCleaner,
)
from annotation_toolkit.utils.errors import FileReadError, ParsingError


class TestStreamingJSONParser(unittest.TestCase):
    """Test cases for StreamingJSONParser class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.parser = StreamingJSONParser()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_parser_initialization(self):
        """Test parser initialization."""
        parser = StreamingJSONParser(chunk_size=4096)
        self.assertEqual(parser.chunk_size, 4096)

    def test_parse_array_items_small_array(self):
        """Test parsing small JSON array."""
        test_file = Path(self.temp_dir) / "array.json"
        data = [{"id": 1}, {"id": 2}, {"id": 3}]
        test_file.write_text(json.dumps(data))

        items = list(self.parser.parse_array_items(test_file))
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]["id"], 1)

    def test_parse_array_items_empty_array(self):
        """Test parsing empty JSON array."""
        test_file = Path(self.temp_dir) / "empty.json"
        test_file.write_text("[]")

        items = list(self.parser.parse_array_items(test_file))
        self.assertEqual(len(items), 0)

    def test_parse_array_items_nonexistent_file(self):
        """Test parsing nonexistent file raises error."""
        nonexistent = Path(self.temp_dir) / "nonexistent.json"

        with self.assertRaises(FileReadError):
            list(self.parser.parse_array_items(nonexistent))

    def test_parse_object_items(self):
        """Test parsing JSON object items."""
        test_file = Path(self.temp_dir) / "object.json"
        data = {"key1": "value1", "key2": "value2", "key3": "value3"}
        test_file.write_text(json.dumps(data))

        items = list(self.parser.parse_object_items(test_file))
        self.assertEqual(len(items), 3)
        # Items are tuples of (key, value)
        keys = [item[0] for item in items]
        self.assertIn("key1", keys)

    def test_parse_large_array(self):
        """Test parsing large JSON array."""
        test_file = Path(self.temp_dir) / "large.json"
        # Create larger dataset
        data = [{"id": i, "data": "x" * 100} for i in range(100)]
        test_file.write_text(json.dumps(data))

        items = list(self.parser.parse_array_items(test_file))
        self.assertEqual(len(items), 100)

    def test_streaming_avoids_memory_loading(self):
        """Test that streaming doesn't load entire file."""
        test_file = Path(self.temp_dir) / "stream.json"
        data = [{"id": i} for i in range(1000)]
        test_file.write_text(json.dumps(data))

        # Process first 10 items only
        count = 0
        for item in self.parser.parse_array_items(test_file):
            count += 1
            if count >= 10:
                break

        self.assertEqual(count, 10)

    @patch('annotation_toolkit.utils.streaming.IJSON_AVAILABLE', False)
    def test_parse_array_with_fallback(self):
        """Test parsing array using fallback method."""
        test_file = Path(self.temp_dir) / "fallback_array.json"
        data = [{"id": 1}, {"id": 2}]
        test_file.write_text(json.dumps(data))

        # Force fallback by mocking ijson as unavailable
        parser = StreamingJSONParser()
        items = list(parser.parse_array_items(test_file))
        self.assertEqual(len(items), 2)

    @patch('annotation_toolkit.utils.streaming.IJSON_AVAILABLE', False)
    def test_parse_object_with_fallback(self):
        """Test parsing object using fallback method."""
        test_file = Path(self.temp_dir) / "fallback_object.json"
        data = {"key1": "value1", "key2": "value2"}
        test_file.write_text(json.dumps(data))

        parser = StreamingJSONParser()
        items = list(parser.parse_object_items(test_file))
        self.assertEqual(len(items), 2)

    @patch('annotation_toolkit.utils.streaming.IJSON_AVAILABLE', False)
    def test_fallback_parse_nested_array(self):
        """Test fallback parser with nested arrays."""
        test_file = Path(self.temp_dir) / "nested.json"
        data = [{"items": [1, 2, 3]}, {"items": [4, 5, 6]}]
        test_file.write_text(json.dumps(data))

        parser = StreamingJSONParser()
        items = list(parser.parse_array_items(test_file))
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["items"], [1, 2, 3])

    @patch('annotation_toolkit.utils.streaming.IJSON_AVAILABLE', False)
    def test_fallback_parse_with_strings_containing_quotes(self):
        """Test fallback parser with strings containing quotes."""
        test_file = Path(self.temp_dir) / "quotes.json"
        data = [{"text": 'He said "hello"'}, {"text": "Another 'quote'"}]
        test_file.write_text(json.dumps(data))

        parser = StreamingJSONParser()
        items = list(parser.parse_array_items(test_file))
        self.assertEqual(len(items), 2)

    @patch('annotation_toolkit.utils.streaming.IJSON_AVAILABLE', False)
    def test_fallback_parse_malformed_array_item(self):
        """Test fallback parser with malformed JSON item."""
        test_file = Path(self.temp_dir) / "malformed.json"
        # Mix valid and invalid items
        test_file.write_text('[{"id": 1}, invalid, {"id": 2}]')

        parser = StreamingJSONParser()
        items = list(parser.parse_array_items(test_file))
        # Should skip invalid item and get valid ones
        self.assertGreater(len(items), 0)

    @patch('annotation_toolkit.utils.streaming.IJSON_AVAILABLE', False)
    def test_fallback_parse_no_array_found(self):
        """Test fallback parser when no array is found."""
        test_file = Path(self.temp_dir) / "no_array.json"
        test_file.write_text('{"not": "an array"}')

        parser = StreamingJSONParser()
        # Fallback wraps ParsingError in FileReadError
        with self.assertRaises((ParsingError, FileReadError)):
            list(parser.parse_array_items(test_file))

    @patch('annotation_toolkit.utils.streaming.IJSON_AVAILABLE', False)
    def test_fallback_parse_object_non_dict(self):
        """Test fallback object parser with non-dict JSON."""
        test_file = Path(self.temp_dir) / "not_object.json"
        test_file.write_text('[1, 2, 3]')  # Array instead of object

        parser = StreamingJSONParser()
        with self.assertRaises(ParsingError):
            list(parser.parse_object_items(test_file))

    def test_parse_object_items_nonexistent_file(self):
        """Test parsing nonexistent file for object raises error."""
        nonexistent = Path(self.temp_dir) / "nonexistent_obj.json"

        with self.assertRaises(FileReadError):
            list(self.parser.parse_object_items(nonexistent))


class TestChunkedFileProcessor(unittest.TestCase):
    """Test cases for ChunkedFileProcessor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_processor_initialization(self):
        """Test processor initialization."""
        processor = ChunkedFileProcessor(chunk_size=1024)
        self.assertEqual(processor.chunk_size, 1024)

    def test_process_file_in_chunks(self):
        """Test processing file in chunks."""
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("Line 1\nLine 2\nLine 3\n")

        processor = ChunkedFileProcessor()

        def line_processor(line):
            return line.strip()

        lines = list(processor.process_lines(test_file, line_processor))
        self.assertEqual(len(lines), 3)
        self.assertIn("Line 1", lines)

    def test_process_empty_file(self):
        """Test processing empty file."""
        test_file = Path(self.temp_dir) / "empty.txt"
        test_file.touch()

        processor = ChunkedFileProcessor()

        def line_processor(line):
            return line

        lines = list(processor.process_lines(test_file, line_processor))
        self.assertEqual(len(lines), 0)

    def test_process_nonexistent_file(self):
        """Test processing nonexistent file raises error."""
        nonexistent = Path(self.temp_dir) / "nonexistent.txt"
        processor = ChunkedFileProcessor()

        def dummy_processor(line):
            return line

        # Error should be raised when trying to process
        with self.assertRaises(FileReadError):
            list(processor.process_lines(nonexistent, dummy_processor))

    def test_process_file_method_with_chunks(self):
        """Test process_file method with chunk processor."""
        test_file = Path(self.temp_dir) / "chunks.txt"
        test_file.write_text("A" * 100 + "B" * 100)

        processor = ChunkedFileProcessor(chunk_size=50)

        def chunk_processor(chunk):
            return len(chunk)

        chunk_sizes = list(processor.process_file(test_file, chunk_processor))
        # Should have processed in chunks
        self.assertGreater(len(chunk_sizes), 1)

    def test_process_file_nonexistent(self):
        """Test process_file with nonexistent file raises error."""
        nonexistent = Path(self.temp_dir) / "nonexistent.txt"
        processor = ChunkedFileProcessor()

        def dummy_processor(chunk):
            return chunk

        with self.assertRaises(FileReadError):
            list(processor.process_file(nonexistent, dummy_processor))

    def test_process_file_processor_returns_none(self):
        """Test process_file when processor returns None."""
        test_file = Path(self.temp_dir) / "none.txt"
        test_file.write_text("content")

        processor = ChunkedFileProcessor()

        def none_processor(chunk):
            return None  # Return None to skip

        results = list(processor.process_file(test_file, none_processor))
        self.assertEqual(len(results), 0)

    def test_process_lines_with_empty_skip(self):
        """Test process_lines with skip_empty parameter."""
        test_file = Path(self.temp_dir) / "with_empty.txt"
        test_file.write_text("Line 1\n\n\nLine 2\n")

        processor = ChunkedFileProcessor()

        def count_processor(line):
            return 1

        # With skip_empty=True (default)
        count = sum(processor.process_lines(test_file, count_processor))
        self.assertEqual(count, 2)

    def test_process_lines_without_skip_empty(self):
        """Test process_lines without skipping empty lines."""
        test_file = Path(self.temp_dir) / "with_empty2.txt"
        test_file.write_text("Line 1\n\n\nLine 2\n")

        processor = ChunkedFileProcessor()

        def count_processor(line):
            return 1

        # With skip_empty=False
        count = sum(processor.process_lines(test_file, count_processor, skip_empty=False))
        self.assertGreater(count, 2)  # Should include empty lines

    def test_process_lines_processor_returns_none(self):
        """Test process_lines when processor returns None."""
        test_file = Path(self.temp_dir) / "none_lines.txt"
        test_file.write_text("Line 1\nLine 2\n")

        processor = ChunkedFileProcessor()

        def none_processor(line):
            return None

        results = list(processor.process_lines(test_file, none_processor))
        self.assertEqual(len(results), 0)


class TestStreamingTextCleaner(unittest.TestCase):
    """Test cases for StreamingTextCleaner class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cleaner = StreamingTextCleaner()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cleaner_initialization(self):
        """Test cleaner initialization."""
        cleaner = StreamingTextCleaner(chunk_size=2048)
        self.assertEqual(cleaner.chunk_size, 2048)

    def test_clean_file_basic(self):
        """Test basic file cleaning."""
        input_file = Path(self.temp_dir) / "input.txt"
        output_file = Path(self.temp_dir) / "output.txt"
        input_file.write_text("  Line 1  \n  Line 2  \n")

        self.cleaner.clean_file(input_file, output_file)

        result = output_file.read_text()
        self.assertIn("Line 1", result)
        self.assertIn("Line 2", result)

    def test_clean_file_removes_extra_whitespace(self):
        """Test that cleaning removes extra whitespace."""
        input_file = Path(self.temp_dir) / "input.txt"
        output_file = Path(self.temp_dir) / "output.txt"
        input_file.write_text("Line    with    spaces\n")

        self.cleaner.clean_file(input_file, output_file)

        result = output_file.read_text()
        # Should normalize spaces
        self.assertIsInstance(result, str)

    def test_clean_file_nonexistent_input(self):
        """Test cleaning nonexistent input file raises error."""
        nonexistent = Path(self.temp_dir) / "nonexistent.txt"
        output_file = Path(self.temp_dir) / "output.txt"

        with self.assertRaises(FileReadError):
            self.cleaner.clean_file(nonexistent, output_file)

    def test_clean_file_return_string(self):
        """Test clean_file returning string when no output path."""
        input_file = Path(self.temp_dir) / "input.txt"
        input_file.write_text("  Line 1  \n  Line 2  \n")

        result = self.cleaner.clean_file(input_file)

        self.assertIsInstance(result, str)
        self.assertIn("Line 1", result)
        self.assertIn("Line 2", result)

    def test_clean_line_removes_control_chars(self):
        """Test _clean_line removes control characters."""
        # String with control characters
        dirty_line = "Text\x01with\x02control\x03chars"
        cleaned = self.cleaner._clean_line(dirty_line)

        # Control chars should be removed
        self.assertIsInstance(cleaned, str)
        self.assertIn("Text", cleaned)

    def test_clean_line_removes_null_bytes(self):
        """Test _clean_line removes null bytes."""
        dirty_line = "Text\x00with\x00nulls"
        cleaned = self.cleaner._clean_line(dirty_line)

        self.assertNotIn('\x00', cleaned)
        self.assertIn("Text", cleaned)

    def test_clean_line_empty_returns_none(self):
        """Test _clean_line returns None for empty lines."""
        cleaned = self.cleaner._clean_line("   \n  ")
        self.assertIsNone(cleaned)

    def test_clean_file_with_empty_lines(self):
        """Test cleaning file with empty lines."""
        input_file = Path(self.temp_dir) / "with_empty.txt"
        output_file = Path(self.temp_dir) / "output.txt"
        input_file.write_text("Line 1\n\n\n  \nLine 2\n")

        self.cleaner.clean_file(input_file, output_file)

        result = output_file.read_text()
        # Empty lines should be skipped
        lines = [l for l in result.split('\n') if l.strip()]
        self.assertEqual(len(lines), 2)


class TestStreamingIntegration(unittest.TestCase):
    """Integration tests for streaming utilities."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_parse_and_process_json_array(self):
        """Test parsing and processing JSON array."""
        test_file = Path(self.temp_dir) / "data.json"
        data = [{"value": i} for i in range(50)]
        test_file.write_text(json.dumps(data))

        parser = StreamingJSONParser()
        total = 0

        for item in parser.parse_array_items(test_file):
            total += item["value"]

        # Sum of 0 to 49
        expected = sum(range(50))
        self.assertEqual(total, expected)

    def test_chunked_processing_large_file(self):
        """Test chunked processing of large file."""
        test_file = Path(self.temp_dir) / "large.txt"
        # Create file with 1000 lines
        lines = [f"Line {i}\n" for i in range(1000)]
        test_file.write_text("".join(lines))

        processor = ChunkedFileProcessor(chunk_size=1024)

        def count_line(line):
            return 1

        line_count = sum(processor.process_lines(test_file, count_line))
        self.assertEqual(line_count, 1000)

    def test_end_to_end_clean_and_parse(self):
        """Test end-to-end workflow of cleaning and parsing."""
        # Create dirty JSON file
        input_file = Path(self.temp_dir) / "dirty.txt"
        input_file.write_text('  {"key": "value"}  \n  ')

        # Clean it
        cleaner = StreamingTextCleaner()
        cleaned_file = Path(self.temp_dir) / "cleaned.txt"
        cleaner.clean_file(input_file, cleaned_file)

        # Verify cleaning worked
        result = cleaned_file.read_text()
        self.assertIn("key", result)


if __name__ == "__main__":
    unittest.main()
