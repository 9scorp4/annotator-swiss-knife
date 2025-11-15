"""
Comprehensive tests for the security utilities.

This module contains comprehensive tests for the security utilities including:
- PathValidator (directory traversal protection, symlink handling)
- FileSizeValidator (file size limits)
- InputSanitizer (injection prevention)
- RateLimiter (rate limiting)
- File hashing utilities
"""

import unittest
import tempfile
import os
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

from annotation_toolkit.utils.security import (
    PathValidator,
    FileSizeValidator,
    InputSanitizer,
    RateLimiter,
    generate_file_hash,
    default_path_validator,
    default_file_size_validator,
    default_input_sanitizer,
    default_rate_limiter,
)
from annotation_toolkit.utils.errors import ValidationError, ValueValidationError


class TestPathValidator(unittest.TestCase):
    """Test cases for PathValidator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.validator = PathValidator(base_dir=self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization_with_base_dir(self):
        """Test PathValidator initialization with base directory."""
        validator = PathValidator(base_dir=self.temp_dir)
        self.assertEqual(validator.base_dir, Path(self.temp_dir).resolve())
        self.assertIn(Path(self.temp_dir).resolve(), validator.allowed_dirs)

    def test_initialization_without_base_dir(self):
        """Test PathValidator initialization without base directory."""
        validator = PathValidator()
        self.assertEqual(validator.base_dir, Path.cwd())

    def test_initialization_with_allowed_dirs(self):
        """Test PathValidator initialization with allowed directories."""
        allowed = [self.temp_dir, "/tmp"]
        validator = PathValidator(base_dir=self.temp_dir, allowed_dirs=allowed)
        self.assertGreaterEqual(len(validator.allowed_dirs), 2)

    def test_validate_path_success(self):
        """Test validating a legitimate path."""
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.touch()

        validated = self.validator.validate_path(str(test_file))
        self.assertEqual(validated, test_file.resolve())

    def test_validate_path_nonexistent_file(self):
        """Test validating a nonexistent file within allowed directory."""
        test_file = Path(self.temp_dir) / "nonexistent.txt"
        # Should not raise error for nonexistent file in allowed dir
        validated = self.validator.validate_path(str(test_file))
        self.assertTrue(str(validated).startswith(str(Path(self.temp_dir).resolve())))

    def test_validate_path_empty_path(self):
        """Test that empty path raises ValidationError."""
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_path("")

        self.assertIn("Empty path", str(context.exception))

    def test_validate_path_too_long(self):
        """Test that overly long path raises ValidationError."""
        long_path = "a" * 5000  # Exceeds MAX_PATH_LENGTH
        with self.assertRaises(ValueValidationError) as context:
            self.validator.validate_path(long_path)

        error = context.exception
        self.assertIn("Path length", error.message)

    def test_validate_path_parent_directory_reference(self):
        """Test that parent directory reference (..) is blocked."""
        malicious_path = os.path.join(self.temp_dir, "..", "etc", "passwd")
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_path(malicious_path)

        self.assertIn("suspicious pattern", str(context.exception).lower())

    def test_validate_path_home_directory_reference(self):
        """Test that home directory reference (~) is blocked."""
        malicious_path = "~/sensitive_file"
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_path(malicious_path)

        self.assertIn("suspicious pattern", str(context.exception).lower())

    def test_validate_path_environment_variable(self):
        """Test that environment variable references are blocked."""
        malicious_paths = ["$HOME/file", "%USERPROFILE%/file"]
        for path in malicious_paths:
            with self.assertRaises(ValidationError):
                self.validator.validate_path(path)

    def test_validate_path_null_byte(self):
        """Test that null byte in path is blocked."""
        malicious_path = f"{self.temp_dir}/file\x00.txt"
        with self.assertRaises(ValidationError):
            self.validator.validate_path(malicious_path)

    def test_validate_path_outside_allowed_directory(self):
        """Test that path outside allowed directories is blocked."""
        outside_path = "/tmp/outside_file.txt"
        # Create a validator with a specific base dir
        specific_validator = PathValidator(base_dir=self.temp_dir)

        with self.assertRaises(ValidationError) as context:
            specific_validator.validate_path(outside_path)

        self.assertIn("outside allowed directories", str(context.exception).lower())

    def test_validate_file_extension_allowed(self):
        """Test validating file with allowed extension."""
        test_file = Path(self.temp_dir) / "test.json"
        test_file.touch()

        validated = self.validator.validate_file_extension(str(test_file))
        self.assertEqual(validated, test_file.resolve())

    def test_validate_file_extension_disallowed(self):
        """Test that disallowed file extension raises error."""
        test_file = Path(self.temp_dir) / "test.exe"
        test_file.touch()

        with self.assertRaises(ValueValidationError) as context:
            self.validator.validate_file_extension(str(test_file))

        self.assertIn("file_extension", str(context.exception).lower())

    def test_validate_file_extension_custom_allowed(self):
        """Test validate file extension with custom allowed extensions."""
        test_file = Path(self.temp_dir) / "test.custom"
        test_file.touch()

        custom_extensions = {'.custom', '.special'}
        validated = self.validator.validate_file_extension(
            str(test_file),
            allowed_extensions=custom_extensions
        )
        self.assertEqual(validated, test_file.resolve())

    def test_validate_file_extension_case_insensitive(self):
        """Test that file extension validation is case-insensitive."""
        test_file = Path(self.temp_dir) / "test.JSON"
        test_file.touch()

        validated = self.validator.validate_file_extension(str(test_file))
        self.assertEqual(validated, test_file.resolve())

    @unittest.skipIf(os.name == 'nt', "Symlink test not reliable on Windows")
    def test_validate_path_with_symlink_inside_allowed_dir(self):
        """Test validating path with symlink inside allowed directory."""
        # Create a regular file
        real_file = Path(self.temp_dir) / "real_file.txt"
        real_file.touch()

        # Create a symlink to it
        link_file = Path(self.temp_dir) / "link_file.txt"
        try:
            link_file.symlink_to(real_file)

            # Should allow symlink within allowed directory
            validated = self.validator.validate_path(str(link_file))
            self.assertTrue(validated.exists())
        except OSError:
            self.skipTest("Cannot create symlinks on this system")

    @unittest.skipIf(os.name == 'nt', "Symlink test not reliable on Windows")
    def test_validate_path_symlink_escape(self):
        """Test that symlink pointing outside allowed dir is blocked."""
        # Create a file outside the allowed directory
        outside_file = Path(tempfile.gettempdir()) / "outside.txt"
        outside_file.touch()

        try:
            # Create a symlink inside allowed dir pointing outside
            link_file = Path(self.temp_dir) / "escape_link.txt"
            link_file.symlink_to(outside_file)

            with self.assertRaises(ValidationError) as context:
                self.validator.validate_path(str(link_file))

            error_msg = str(context.exception).lower()
            self.assertTrue(
                "outside allowed" in error_msg or "symlink" in error_msg
            )
        except OSError:
            self.skipTest("Cannot create symlinks on this system")
        finally:
            # Cleanup
            if outside_file.exists():
                outside_file.unlink()


class TestFileSizeValidator(unittest.TestCase):
    """Test cases for FileSizeValidator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.validator = FileSizeValidator(max_size=1024 * 1024)  # 1MB

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization_default(self):
        """Test FileSizeValidator initialization with default."""
        validator = FileSizeValidator()
        self.assertIsNotNone(validator.max_size)

    def test_initialization_custom_size(self):
        """Test FileSizeValidator initialization with custom size."""
        validator = FileSizeValidator(max_size=5000)
        self.assertEqual(validator.max_size, 5000)

    def test_validate_file_size_small_file(self):
        """Test validating a small file."""
        test_file = Path(self.temp_dir) / "small.txt"
        test_file.write_text("Small content")

        file_size = self.validator.validate_file_size(test_file)
        self.assertGreater(file_size, 0)
        self.assertLess(file_size, 1024 * 1024)

    def test_validate_file_size_at_limit(self):
        """Test validating a file at the size limit."""
        test_file = Path(self.temp_dir) / "at_limit.txt"
        # Create a file just under 1MB
        content = "x" * (1024 * 1024 - 100)
        test_file.write_text(content)

        file_size = self.validator.validate_file_size(test_file)
        self.assertLess(file_size, 1024 * 1024)

    def test_validate_file_size_too_large(self):
        """Test that oversized file raises ValidationError."""
        test_file = Path(self.temp_dir) / "large.txt"
        # Create a file larger than 1MB
        content = "x" * (1024 * 1024 + 1000)
        test_file.write_text(content)

        with self.assertRaises(ValueValidationError) as context:
            self.validator.validate_file_size(test_file)

        error = context.exception
        self.assertIn("file_size", str(error).lower())
        self.assertIn("streaming", error.suggestion.lower())

    def test_validate_file_size_nonexistent(self):
        """Test that nonexistent file raises ValidationError."""
        nonexistent = Path(self.temp_dir) / "nonexistent.txt"

        with self.assertRaises(ValidationError) as context:
            self.validator.validate_file_size(nonexistent)

        self.assertIn("does not exist", str(context.exception).lower())

    def test_validate_file_size_empty_file(self):
        """Test validating an empty file."""
        test_file = Path(self.temp_dir) / "empty.txt"
        test_file.touch()

        file_size = self.validator.validate_file_size(test_file)
        self.assertEqual(file_size, 0)


class TestInputSanitizer(unittest.TestCase):
    """Test cases for InputSanitizer class."""

    def test_sanitize_string_normal_string(self):
        """Test sanitizing a normal string."""
        input_str = "Hello, World!"
        result = InputSanitizer.sanitize_string(input_str)
        self.assertEqual(result, input_str)

    def test_sanitize_string_with_null_bytes(self):
        """Test that null bytes are removed."""
        input_str = "Hello\x00World"
        result = InputSanitizer.sanitize_string(input_str)
        self.assertEqual(result, "HelloWorld")
        self.assertNotIn('\x00', result)

    def test_sanitize_string_with_control_characters(self):
        """Test that control characters are removed."""
        # Include a control character (ASCII 1)
        input_str = "Hello\x01World"
        result = InputSanitizer.sanitize_string(input_str)
        self.assertEqual(result, "HelloWorld")

    def test_sanitize_string_preserves_newlines(self):
        """Test that newlines are preserved."""
        input_str = "Line1\nLine2"
        result = InputSanitizer.sanitize_string(input_str)
        self.assertEqual(result, input_str)
        self.assertIn('\n', result)

    def test_sanitize_string_preserves_tabs(self):
        """Test that tabs are preserved."""
        input_str = "Col1\tCol2"
        result = InputSanitizer.sanitize_string(input_str)
        self.assertEqual(result, input_str)
        self.assertIn('\t', result)

    def test_sanitize_string_preserves_carriage_returns(self):
        """Test that carriage returns are preserved."""
        input_str = "Line1\r\nLine2"
        result = InputSanitizer.sanitize_string(input_str)
        self.assertEqual(result, input_str)

    def test_sanitize_string_too_long(self):
        """Test that overly long string raises ValidationError."""
        long_string = "x" * 10001  # Default max is 10000
        with self.assertRaises(ValueValidationError) as context:
            InputSanitizer.sanitize_string(long_string)

        error = context.exception
        self.assertIn("input_length", str(error).lower())

    def test_sanitize_string_custom_max_length(self):
        """Test sanitize string with custom max length."""
        input_str = "x" * 100
        result = InputSanitizer.sanitize_string(input_str, max_length=200)
        self.assertEqual(result, input_str)

        with self.assertRaises(ValueValidationError):
            InputSanitizer.sanitize_string(input_str, max_length=50)

    def test_sanitize_string_non_string_input(self):
        """Test that non-string input raises ValidationError."""
        with self.assertRaises(ValidationError):
            InputSanitizer.sanitize_string(123)

        with self.assertRaises(ValidationError):
            InputSanitizer.sanitize_string(None)

        with self.assertRaises(ValidationError):
            InputSanitizer.sanitize_string(['list'])

    def test_sanitize_json_key_normal_key(self):
        """Test sanitizing a normal JSON key."""
        key = "user_name"
        result = InputSanitizer.sanitize_json_key(key)
        self.assertEqual(result, key)

    def test_sanitize_json_key_with_special_chars(self):
        """Test that special characters are replaced."""
        key = "user@name#123"
        result = InputSanitizer.sanitize_json_key(key)
        # Special chars should be replaced with underscores
        self.assertEqual(result, "user_name_123")

    def test_sanitize_json_key_allows_hyphen_dot(self):
        """Test that hyphens and dots are allowed."""
        key = "user-name.value"
        result = InputSanitizer.sanitize_json_key(key)
        self.assertEqual(result, key)

    def test_sanitize_json_key_starts_with_number(self):
        """Test that key starting with number gets prefix."""
        key = "123user"
        result = InputSanitizer.sanitize_json_key(key)
        self.assertEqual(result, "_123user")
        self.assertFalse(result[0].isdigit())

    def test_sanitize_json_key_too_long(self):
        """Test that overly long key is truncated."""
        long_key = "x" * 150
        result = InputSanitizer.sanitize_json_key(long_key)
        self.assertEqual(len(result), 100)

    def test_sanitize_json_key_empty(self):
        """Test sanitizing empty key."""
        result = InputSanitizer.sanitize_json_key("")
        self.assertEqual(result, "")

    def test_sanitize_json_key_only_special_chars(self):
        """Test sanitizing key with only special characters."""
        key = "@#$%"
        result = InputSanitizer.sanitize_json_key(key)
        self.assertEqual(result, "____")


class TestRateLimiter(unittest.TestCase):
    """Test cases for RateLimiter class."""

    def test_initialization_default(self):
        """Test RateLimiter initialization with defaults."""
        limiter = RateLimiter()
        self.assertGreater(limiter.max_requests, 0)
        self.assertGreater(limiter.window_seconds, 0)

    def test_initialization_custom(self):
        """Test RateLimiter initialization with custom values."""
        limiter = RateLimiter(max_requests=5, window_seconds=10)
        self.assertEqual(limiter.max_requests, 5)
        self.assertEqual(limiter.window_seconds, 10)

    def test_is_allowed_first_request(self):
        """Test that first request is allowed."""
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        self.assertTrue(limiter.is_allowed("user1"))

    def test_is_allowed_within_limit(self):
        """Test that requests within limit are allowed."""
        limiter = RateLimiter(max_requests=3, window_seconds=60)

        self.assertTrue(limiter.is_allowed("user1"))
        self.assertTrue(limiter.is_allowed("user1"))
        self.assertTrue(limiter.is_allowed("user1"))

    def test_is_allowed_exceeds_limit(self):
        """Test that exceeding limit blocks requests."""
        limiter = RateLimiter(max_requests=3, window_seconds=60)

        # Make 3 allowed requests
        for _ in range(3):
            self.assertTrue(limiter.is_allowed("user1"))

        # 4th request should be blocked
        self.assertFalse(limiter.is_allowed("user1"))

    def test_is_allowed_different_identifiers(self):
        """Test that different identifiers have separate limits."""
        limiter = RateLimiter(max_requests=2, window_seconds=60)

        self.assertTrue(limiter.is_allowed("user1"))
        self.assertTrue(limiter.is_allowed("user2"))
        self.assertTrue(limiter.is_allowed("user1"))
        self.assertTrue(limiter.is_allowed("user2"))

    def test_is_allowed_window_expiry(self):
        """Test that old requests expire after window."""
        limiter = RateLimiter(max_requests=2, window_seconds=1)  # 1 second window

        # Make 2 requests
        self.assertTrue(limiter.is_allowed("user1"))
        self.assertTrue(limiter.is_allowed("user1"))

        # Should be blocked
        self.assertFalse(limiter.is_allowed("user1"))

        # Wait for window to expire
        time.sleep(1.1)

        # Should be allowed again
        self.assertTrue(limiter.is_allowed("user1"))

    def test_get_reset_time_no_requests(self):
        """Test get_reset_time with no prior requests."""
        limiter = RateLimiter()
        reset_time = limiter.get_reset_time("user1")
        self.assertIsNone(reset_time)

    def test_get_reset_time_with_requests(self):
        """Test get_reset_time after making requests."""
        limiter = RateLimiter(max_requests=2, window_seconds=60)

        before_time = time.time()
        limiter.is_allowed("user1")
        reset_time = limiter.get_reset_time("user1")

        self.assertIsNotNone(reset_time)
        self.assertGreater(reset_time, before_time)
        # Allow for small timing differences
        self.assertLessEqual(reset_time, before_time + 61)

    def test_thread_safety(self):
        """Test that RateLimiter is thread-safe."""
        import threading

        limiter = RateLimiter(max_requests=100, window_seconds=10)
        results = []

        def make_request():
            results.append(limiter.is_allowed("user1"))

        threads = [threading.Thread(target=make_request) for _ in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All requests should have been processed
        self.assertEqual(len(results), 50)
        # All should be allowed (within limit of 100)
        self.assertTrue(all(results))


class TestGenerateFileHash(unittest.TestCase):
    """Test cases for generate_file_hash function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_file_hash_sha256(self):
        """Test generating SHA256 hash."""
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("Hello, World!")

        hash_value = generate_file_hash(test_file, algorithm='sha256')
        self.assertIsInstance(hash_value, str)
        self.assertEqual(len(hash_value), 64)  # SHA256 produces 64 hex chars

    def test_generate_file_hash_sha1(self):
        """Test generating SHA1 hash."""
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("Hello, World!")

        hash_value = generate_file_hash(test_file, algorithm='sha1')
        self.assertIsInstance(hash_value, str)
        self.assertEqual(len(hash_value), 40)  # SHA1 produces 40 hex chars

    def test_generate_file_hash_md5(self):
        """Test generating MD5 hash."""
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("Hello, World!")

        hash_value = generate_file_hash(test_file, algorithm='md5')
        self.assertIsInstance(hash_value, str)
        self.assertEqual(len(hash_value), 32)  # MD5 produces 32 hex chars

    def test_generate_file_hash_consistent(self):
        """Test that hash is consistent for same content."""
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("Consistent content")

        hash1 = generate_file_hash(test_file)
        hash2 = generate_file_hash(test_file)
        self.assertEqual(hash1, hash2)

    def test_generate_file_hash_different_content(self):
        """Test that different content produces different hash."""
        file1 = Path(self.temp_dir) / "file1.txt"
        file2 = Path(self.temp_dir) / "file2.txt"
        file1.write_text("Content A")
        file2.write_text("Content B")

        hash1 = generate_file_hash(file1)
        hash2 = generate_file_hash(file2)
        self.assertNotEqual(hash1, hash2)

    def test_generate_file_hash_large_file(self):
        """Test hashing large file (tests chunked reading)."""
        test_file = Path(self.temp_dir) / "large.txt"
        # Create a file larger than chunk size (8192 bytes)
        large_content = "x" * 10000
        test_file.write_text(large_content)

        hash_value = generate_file_hash(test_file)
        self.assertIsInstance(hash_value, str)
        self.assertEqual(len(hash_value), 64)

    def test_generate_file_hash_nonexistent(self):
        """Test that nonexistent file raises ValidationError."""
        nonexistent = Path(self.temp_dir) / "nonexistent.txt"

        with self.assertRaises(ValidationError) as context:
            generate_file_hash(nonexistent)

        self.assertIn("does not exist", str(context.exception).lower())

    def test_generate_file_hash_empty_file(self):
        """Test hashing empty file."""
        test_file = Path(self.temp_dir) / "empty.txt"
        test_file.touch()

        hash_value = generate_file_hash(test_file)
        # Known SHA256 hash of empty file
        empty_sha256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        self.assertEqual(hash_value, empty_sha256)


class TestGlobalInstances(unittest.TestCase):
    """Test cases for global security instances."""

    def test_default_path_validator_exists(self):
        """Test that default_path_validator is available."""
        self.assertIsInstance(default_path_validator, PathValidator)

    def test_default_file_size_validator_exists(self):
        """Test that default_file_size_validator is available."""
        self.assertIsInstance(default_file_size_validator, FileSizeValidator)

    def test_default_input_sanitizer_exists(self):
        """Test that default_input_sanitizer is available."""
        self.assertIsInstance(default_input_sanitizer, InputSanitizer)

    def test_default_rate_limiter_exists(self):
        """Test that default_rate_limiter is available."""
        self.assertIsInstance(default_rate_limiter, RateLimiter)


class TestSecurityIntegration(unittest.TestCase):
    """Integration tests for security utilities."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_validate_and_hash_file(self):
        """Test validating and hashing a file."""
        validator = PathValidator(base_dir=self.temp_dir)
        test_file = Path(self.temp_dir) / "test.json"
        test_file.write_text('{"key": "value"}')

        # Validate path
        validated_path = validator.validate_path(str(test_file))

        # Validate extension
        validated_path = validator.validate_file_extension(validated_path)

        # Validate size
        size_validator = FileSizeValidator()
        size = size_validator.validate_file_size(validated_path)
        self.assertGreater(size, 0)

        # Generate hash
        file_hash = generate_file_hash(validated_path)
        self.assertIsInstance(file_hash, str)

    def test_sanitize_and_validate_combined(self):
        """Test combining input sanitization with validation."""
        # Sanitize input string
        user_input = "file\x00name.txt"  # Contains null byte
        sanitized = InputSanitizer.sanitize_string(user_input)
        self.assertNotIn('\x00', sanitized)

        # Create file with sanitized name
        test_file = Path(self.temp_dir) / sanitized
        test_file.touch()

        # Validate the path
        validator = PathValidator(base_dir=self.temp_dir)
        validated = validator.validate_path(str(test_file))
        self.assertTrue(validated.exists())


if __name__ == "__main__":
    unittest.main()
