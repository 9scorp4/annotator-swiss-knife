"""
Security utilities for the annotation toolkit.

This module provides security-related functions including path validation,
input sanitization, and rate limiting to prevent common security vulnerabilities.
"""

import os
import re
from pathlib import Path
from typing import Optional, Union, Set
import hashlib
import time
from collections import defaultdict
from threading import Lock

from .errors import ValidationError, ValueValidationError
from .logger import get_logger

logger = get_logger()

# Constants for security configuration
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB default max file size
MAX_PATH_LENGTH = 4096  # Maximum path length
ALLOWED_EXTENSIONS = {'.json', '.yaml', '.yml', '.txt', '.md', '.csv'}
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 100  # max requests per window


class PathValidator:
    """Validates and sanitizes file paths to prevent directory traversal attacks."""

    def __init__(self, base_dir: Optional[Union[str, Path]] = None,
                 allowed_dirs: Optional[Set[Union[str, Path]]] = None):
        """
        Initialize the PathValidator.

        Args:
            base_dir: The base directory that all paths must be within.
                     If None, uses the current working directory.
            allowed_dirs: Additional directories that are allowed.
        """
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.base_dir = self.base_dir.resolve()

        self.allowed_dirs = {self.base_dir}
        if allowed_dirs:
            self.allowed_dirs.update(Path(d).resolve() for d in allowed_dirs)

        # Add user's home directory for annotation_toolkit_data
        home_data_dir = Path.home() / "annotation_toolkit_data"
        self.allowed_dirs.add(home_data_dir.resolve())

        logger.debug(f"PathValidator initialized with base_dir: {self.base_dir}")

    def validate_path(self, path: Union[str, Path]) -> Path:
        """
        Validate and sanitize a file path.

        Args:
            path: The path to validate.

        Returns:
            The validated and resolved Path object.

        Raises:
            ValidationError: If the path is invalid or attempts directory traversal.
        """
        if not path:
            raise ValidationError("Empty path provided")

        # Convert to Path and resolve to absolute path
        path_obj = Path(path)

        # Check path length
        if len(str(path_obj)) > MAX_PATH_LENGTH:
            raise ValueValidationError(
                "path",
                str(path_obj),
                f"Path length must be less than {MAX_PATH_LENGTH} characters"
            )

        # Check for suspicious patterns
        path_str = str(path_obj)
        suspicious_patterns = [
            r'\.\.',  # Parent directory reference
            r'~',     # Home directory reference
            r'\$',    # Environment variable
            r'%',     # Windows environment variable
            r'\x00',  # Null byte
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, path_str):
                logger.warning(f"Suspicious pattern detected in path: {path_str}")
                raise ValidationError(
                    f"Path contains suspicious pattern: {pattern}",
                    details={"path": path_str, "pattern": pattern},
                    suggestion="Use absolute paths without special characters"
                )

        # Resolve the path to its absolute form
        try:
            # If path doesn't exist yet, resolve its parent
            if not path_obj.exists():
                parent = path_obj.parent.resolve()
                resolved_path = parent / path_obj.name
            else:
                resolved_path = path_obj.resolve()
        except (OSError, RuntimeError) as e:
            raise ValidationError(
                f"Failed to resolve path: {str(e)}",
                details={"path": str(path_obj)},
                suggestion="Ensure the path is valid and accessible"
            )

        # Check if the resolved path is within allowed directories
        is_allowed = False
        for allowed_dir in self.allowed_dirs:
            try:
                resolved_path.relative_to(allowed_dir)
                is_allowed = True
                break
            except ValueError:
                continue

        if not is_allowed:
            logger.warning(f"Path traversal attempt detected: {resolved_path}")
            raise ValidationError(
                "Path is outside allowed directories",
                details={
                    "path": str(resolved_path),
                    "allowed_dirs": [str(d) for d in self.allowed_dirs]
                },
                suggestion="Use paths within the project directory or user data directory"
            )

        return resolved_path

    def validate_file_extension(self, path: Union[str, Path],
                               allowed_extensions: Optional[Set[str]] = None) -> Path:
        """
        Validate file extension.

        Args:
            path: The file path to validate.
            allowed_extensions: Set of allowed extensions. If None, uses default set.

        Returns:
            The validated Path object.

        Raises:
            ValidationError: If the file extension is not allowed.
        """
        validated_path = self.validate_path(path)

        extensions = allowed_extensions or ALLOWED_EXTENSIONS
        file_ext = validated_path.suffix.lower()

        if file_ext not in extensions:
            raise ValueValidationError(
                "file_extension",
                file_ext,
                f"Must be one of: {', '.join(sorted(extensions))}"
            )

        return validated_path


class FileSizeValidator:
    """Validates file sizes to prevent memory exhaustion."""

    def __init__(self, max_size: int = MAX_FILE_SIZE):
        """
        Initialize the FileSizeValidator.

        Args:
            max_size: Maximum allowed file size in bytes.
        """
        self.max_size = max_size

    def validate_file_size(self, path: Union[str, Path]) -> int:
        """
        Validate that a file is within the size limit.

        Args:
            path: Path to the file.

        Returns:
            The file size in bytes.

        Raises:
            ValidationError: If the file is too large.
        """
        path_obj = Path(path)

        if not path_obj.exists():
            raise ValidationError(f"File does not exist: {path}")

        file_size = path_obj.stat().st_size

        if file_size > self.max_size:
            raise ValueValidationError(
                "file_size",
                f"{file_size / (1024*1024):.2f}MB",
                f"Must be less than {self.max_size / (1024*1024):.2f}MB",
                suggestion="Consider processing the file in chunks or using a streaming approach"
            )

        return file_size


class InputSanitizer:
    """Sanitizes user input to prevent injection attacks."""

    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 10000) -> str:
        """
        Sanitize a string input.

        Args:
            input_str: The string to sanitize.
            max_length: Maximum allowed length.

        Returns:
            The sanitized string.

        Raises:
            ValidationError: If the input is invalid.
        """
        if not isinstance(input_str, str):
            raise ValidationError(f"Input must be a string, got {type(input_str)}")

        if len(input_str) > max_length:
            raise ValueValidationError(
                "input_length",
                len(input_str),
                f"Must be less than {max_length} characters"
            )

        # Remove null bytes
        sanitized = input_str.replace('\x00', '')

        # Remove control characters except newline, tab, carriage return
        control_chars = ''.join(
            chr(i) for i in range(32)
            if chr(i) not in ['\n', '\t', '\r']
        )
        sanitized = sanitized.translate(str.maketrans('', '', control_chars))

        return sanitized

    @staticmethod
    def sanitize_json_key(key: str) -> str:
        """
        Sanitize a JSON key to prevent injection.

        Args:
            key: The JSON key to sanitize.

        Returns:
            The sanitized key.
        """
        # Allow only alphanumeric, underscore, hyphen, and dot
        sanitized = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', key)

        # Ensure it doesn't start with a number
        if sanitized and sanitized[0].isdigit():
            sanitized = '_' + sanitized

        return sanitized[:100]  # Limit key length


class RateLimiter:
    """Simple rate limiter to prevent abuse."""

    def __init__(self, max_requests: int = RATE_LIMIT_MAX_REQUESTS,
                 window_seconds: int = RATE_LIMIT_WINDOW):
        """
        Initialize the RateLimiter.

        Args:
            max_requests: Maximum number of requests allowed in the window.
            window_seconds: Time window in seconds.
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
        self.lock = Lock()

    def is_allowed(self, identifier: str) -> bool:
        """
        Check if a request is allowed.

        Args:
            identifier: Unique identifier for the requester (e.g., user ID, IP).

        Returns:
            True if the request is allowed, False otherwise.
        """
        with self.lock:
            now = time.time()

            # Clean old requests
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if now - req_time < self.window_seconds
            ]

            # Check if limit exceeded
            if len(self.requests[identifier]) >= self.max_requests:
                logger.warning(f"Rate limit exceeded for identifier: {identifier}")
                return False

            # Record this request
            self.requests[identifier].append(now)
            return True

    def get_reset_time(self, identifier: str) -> Optional[float]:
        """
        Get the time when the rate limit resets for an identifier.

        Args:
            identifier: Unique identifier for the requester.

        Returns:
            Unix timestamp when the limit resets, or None if not limited.
        """
        with self.lock:
            if identifier not in self.requests or not self.requests[identifier]:
                return None

            oldest_request = min(self.requests[identifier])
            return oldest_request + self.window_seconds


def generate_file_hash(path: Union[str, Path], algorithm: str = 'sha256') -> str:
    """
    Generate a hash of a file's contents.

    Args:
        path: Path to the file.
        algorithm: Hash algorithm to use ('sha256', 'sha1', 'md5').

    Returns:
        Hex digest of the file's hash.
    """
    path_obj = Path(path)

    if not path_obj.exists():
        raise ValidationError(f"File does not exist: {path}")

    hash_obj = hashlib.new(algorithm)

    with open(path_obj, 'rb') as f:
        # Read in chunks to handle large files
        for chunk in iter(lambda: f.read(8192), b''):
            hash_obj.update(chunk)

    return hash_obj.hexdigest()


# Create global instances for convenience
default_path_validator = PathValidator()
default_file_size_validator = FileSizeValidator()
default_input_sanitizer = InputSanitizer()
default_rate_limiter = RateLimiter()