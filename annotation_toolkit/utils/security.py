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

from functools import lru_cache

from .errors import ValidationError, ValueValidationError
from .logger import get_logger

logger = get_logger()


@lru_cache(maxsize=1)
def _get_security_config():
    """
    Lazy-load security configuration.

    This defers Config instantiation until first access, avoiding
    module-level Config creation that bypasses the DI container.

    Returns:
        dict: Security configuration values with defaults.
    """
    from ..config import Config
    config = Config()
    return {
        'max_file_size': config.get_security_config('max_file_size') or (100 * 1024 * 1024),
        'max_path_length': config.get_security_config('max_path_length') or 4096,
        'allowed_extensions': set(config.get_security_config('allowed_extensions') or ['.json', '.yaml', '.yml', '.txt', '.md', '.csv']),
        'rate_limit_window': config.get_security_config('rate_limit', 'window_seconds') or 60,
        'rate_limit_max_requests': config.get_security_config('rate_limit', 'max_requests') or 100,
    }


# Public getter functions for lazy-loaded security configuration
def get_max_file_size() -> int:
    """Get maximum allowed file size in bytes."""
    return _get_security_config()['max_file_size']

def get_max_path_length() -> int:
    """Get maximum allowed path length."""
    return _get_security_config()['max_path_length']

def get_allowed_extensions() -> set:
    """Get set of allowed file extensions."""
    return _get_security_config()['allowed_extensions']

def get_rate_limit_window() -> int:
    """Get rate limit window in seconds."""
    return _get_security_config()['rate_limit_window']

def get_rate_limit_max_requests() -> int:
    """Get maximum requests per rate limit window."""
    return _get_security_config()['rate_limit_max_requests']

# Pre-compiled regex pattern for suspicious path patterns
# Matches: parent dir (..), home dir (~), env vars ($, %), null byte
_SUSPICIOUS_PATH_PATTERN = re.compile(r'(\.\.|~|\$|%|\x00)')


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
        Validate and sanitize a file path with enhanced symlink protection.

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
        max_path_len = get_max_path_length()
        if len(str(path_obj)) > max_path_len:
            raise ValueValidationError(
                "path",
                str(path_obj),
                f"Path length must be less than {max_path_len} characters"
            )

        # Check for suspicious patterns using pre-compiled regex
        path_str = str(path_obj)
        match = _SUSPICIOUS_PATH_PATTERN.search(path_str)
        if match:
            pattern = match.group(1)
            logger.warning(f"Suspicious pattern detected in path: {path_str}")
            raise ValidationError(
                f"Path contains suspicious pattern: {pattern}",
                details={"path": path_str, "pattern": pattern},
                suggestion="Use absolute paths without special characters"
            )

        # Enhanced symlink detection and resolution
        try:
            # Track symlink chain to prevent loops
            seen_paths = set()
            current_path = path_obj
            max_symlink_depth = 10

            # Follow symlinks manually to detect loops
            for _ in range(max_symlink_depth):
                if current_path in seen_paths:
                    raise ValidationError(
                        "Symlink loop detected",
                        details={"path": str(path_obj)},
                        suggestion="Avoid circular symbolic links"
                    )
                seen_paths.add(current_path)

                if current_path.exists() and current_path.is_symlink():
                    # Get the target of the symlink
                    try:
                        # Use os.readlink for Python 3.8 compatibility
                        # (Path.readlink() was added in Python 3.9)
                        target = Path(os.readlink(str(current_path)))
                        if not target.is_absolute():
                            target = current_path.parent / target
                        current_path = target
                    except OSError as e:
                        raise ValidationError(
                            f"Cannot read symlink target: {str(e)}",
                            details={"path": str(current_path)},
                            suggestion="Check symlink permissions and validity"
                        )
                else:
                    break
            else:
                raise ValidationError(
                    "Too many symlinks in path (possible loop)",
                    details={"path": str(path_obj), "max_depth": max_symlink_depth},
                    suggestion="Reduce symlink chain depth"
                )

            # Resolve the final path
            if not current_path.exists():
                parent = current_path.parent.resolve(strict=False)
                resolved_path = parent / current_path.name
            else:
                # Use resolve() with strict=True for existing paths
                resolved_path = current_path.resolve(strict=True)

            # Additional check: ensure resolved path doesn't escape via symlinks
            # Check each component of the path
            parts = resolved_path.parts
            checked_path = Path(parts[0]) if parts else Path()

            for part in parts[1:]:
                checked_path = checked_path / part
                if checked_path.exists() and checked_path.is_symlink():
                    # Verify symlink target is within allowed directories
                    link_target = checked_path.resolve(strict=True)
                    link_allowed = False
                    for allowed_dir in self.allowed_dirs:
                        try:
                            link_target.relative_to(allowed_dir)
                            link_allowed = True
                            break
                        except ValueError:
                            continue

                    if not link_allowed:
                        logger.warning(f"Symlink escape attempt: {checked_path} -> {link_target}")
                        raise ValidationError(
                            "Symlink points outside allowed directories",
                            details={
                                "symlink": str(checked_path),
                                "target": str(link_target)
                            },
                            suggestion="Ensure all symlinks point to allowed locations"
                        )

        except (OSError, RuntimeError) as e:
            if "Symlink" not in str(e):  # Don't override our symlink errors
                raise ValidationError(
                    f"Failed to resolve path: {str(e)}",
                    details={"path": str(path_obj)},
                    suggestion="Ensure the path is valid and accessible"
                )
            raise

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

        extensions = allowed_extensions or get_allowed_extensions()
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

    def __init__(self, max_size: Optional[int] = None):
        """
        Initialize the FileSizeValidator.

        Args:
            max_size: Maximum allowed file size in bytes. Uses config default if None.
        """
        self.max_size = max_size if max_size is not None else get_max_file_size()

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

    def __init__(self, max_requests: Optional[int] = None,
                 window_seconds: Optional[int] = None):
        """
        Initialize the RateLimiter.

        Args:
            max_requests: Maximum number of requests allowed in the window. Uses config default if None.
            window_seconds: Time window in seconds. Uses config default if None.
        """
        if max_requests is None:
            max_requests = get_rate_limit_max_requests()
        if window_seconds is None:
            window_seconds = get_rate_limit_window()
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


# Lazy global instances - created on first access instead of at module import
_default_path_validator = None
_default_file_size_validator = None
_default_input_sanitizer = None
_default_rate_limiter = None


def get_default_path_validator() -> PathValidator:
    """Get the default PathValidator instance (lazy-loaded)."""
    global _default_path_validator
    if _default_path_validator is None:
        _default_path_validator = PathValidator()
    return _default_path_validator


def get_default_file_size_validator() -> FileSizeValidator:
    """Get the default FileSizeValidator instance (lazy-loaded)."""
    global _default_file_size_validator
    if _default_file_size_validator is None:
        _default_file_size_validator = FileSizeValidator()
    return _default_file_size_validator


def get_default_input_sanitizer() -> InputSanitizer:
    """Get the default InputSanitizer instance (lazy-loaded)."""
    global _default_input_sanitizer
    if _default_input_sanitizer is None:
        _default_input_sanitizer = InputSanitizer()
    return _default_input_sanitizer


def get_default_rate_limiter() -> RateLimiter:
    """Get the default RateLimiter instance (lazy-loaded)."""
    global _default_rate_limiter
    if _default_rate_limiter is None:
        _default_rate_limiter = RateLimiter()
    return _default_rate_limiter


# Module-level __getattr__ for lazy attribute access (Python 3.7+)
# This enables backwards-compatible access like `from security import default_path_validator`
_LAZY_ATTRIBUTES = {
    'default_path_validator': get_default_path_validator,
    'default_file_size_validator': get_default_file_size_validator,
    'default_input_sanitizer': get_default_input_sanitizer,
    'default_rate_limiter': get_default_rate_limiter,
}


def __getattr__(name: str):
    """Lazy module attribute access for default instances."""
    if name in _LAZY_ATTRIBUTES:
        return _LAZY_ATTRIBUTES[name]()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")