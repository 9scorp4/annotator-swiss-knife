"""
Resource management utilities.

This module provides context managers and utilities for managing resources
like file handles, connections, and temporary files.
"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union, TypeVar, Generic
from contextlib import contextmanager, ExitStack
from threading import Lock
import weakref
import atexit

from .logger import get_logger
from .errors import ResourceError

logger = get_logger()

T = TypeVar('T')


class ManagedResource(Generic[T]):
    """
    A managed resource that ensures proper cleanup.

    This class wraps a resource and ensures it's properly cleaned up
    when no longer needed.
    """

    def __init__(self, resource: T, cleanup_func: Callable[[T], None]):
        """
        Initialize managed resource.

        Args:
            resource: The resource to manage.
            cleanup_func: Function to call for cleanup.
        """
        self.resource = resource
        self._cleanup_func = cleanup_func
        self._is_disposed = False
        self._lock = Lock()

    def __enter__(self) -> T:
        """Context manager entry."""
        if self._is_disposed:
            raise ResourceError("Resource has been disposed")
        return self.resource

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.dispose()

    def dispose(self):
        """Manually dispose of the resource."""
        with self._lock:
            if not self._is_disposed:
                try:
                    self._cleanup_func(self.resource)
                except Exception as e:
                    logger.warning(f"Error during resource cleanup: {e}")
                finally:
                    self._is_disposed = True

    def __del__(self):
        """Destructor to ensure cleanup."""
        if not self._is_disposed:
            self.dispose()


class ResourcePool:
    """
    A pool for managing shared resources with automatic cleanup.

    This class manages a pool of resources and ensures they're properly
    cleaned up when the pool is destroyed.
    """

    def __init__(self, max_size: int = 10):
        """
        Initialize resource pool.

        Args:
            max_size: Maximum number of resources to keep in pool.
        """
        self.max_size = max_size
        self._pool: List[Any] = []
        self._in_use: Dict[int, Any] = {}
        self._cleanup_funcs: Dict[int, Callable] = {}
        self._lock = Lock()

    def add_resource(self, resource: T, cleanup_func: Callable[[T], None]) -> int:
        """
        Add a resource to the pool.

        Args:
            resource: The resource to add.
            cleanup_func: Function to call for cleanup.

        Returns:
            Resource ID for later retrieval.
        """
        with self._lock:
            resource_id = id(resource)
            self._pool.append(resource)
            self._cleanup_funcs[resource_id] = cleanup_func

            # Enforce max size
            while len(self._pool) > self.max_size:
                old_resource = self._pool.pop(0)
                old_id = id(old_resource)
                if old_id in self._cleanup_funcs:
                    try:
                        self._cleanup_funcs[old_id](old_resource)
                    except Exception as e:
                        logger.warning(f"Error cleaning up pooled resource: {e}")
                    del self._cleanup_funcs[old_id]

            return resource_id

    def get_resource(self, resource_id: int) -> Optional[T]:
        """
        Get a resource from the pool.

        Args:
            resource_id: The resource ID.

        Returns:
            The resource if found, None otherwise.
        """
        with self._lock:
            for resource in self._pool:
                if id(resource) == resource_id:
                    self._pool.remove(resource)
                    self._in_use[resource_id] = resource
                    return resource
            return None

    def return_resource(self, resource_id: int):
        """
        Return a resource to the pool.

        Args:
            resource_id: The resource ID.
        """
        with self._lock:
            if resource_id in self._in_use:
                resource = self._in_use.pop(resource_id)
                self._pool.append(resource)

    def clear(self):
        """Clear all resources from the pool."""
        with self._lock:
            # Clean up all resources
            all_resources = list(self._pool) + list(self._in_use.values())
            for resource in all_resources:
                resource_id = id(resource)
                if resource_id in self._cleanup_funcs:
                    try:
                        self._cleanup_funcs[resource_id](resource)
                    except Exception as e:
                        logger.warning(f"Error cleaning up pooled resource: {e}")

            self._pool.clear()
            self._in_use.clear()
            self._cleanup_funcs.clear()

    def __del__(self):
        """Destructor to ensure cleanup."""
        self.clear()


class ManagedFileHandle:
    """
    A file handle wrapper that ensures proper closing.

    This class wraps file handles and ensures they're properly closed
    even if an exception occurs.
    """

    def __init__(self, file_path: Union[str, Path], mode: str = 'r',
                 encoding: Optional[str] = None, **kwargs):
        """
        Initialize managed file handle.

        Args:
            file_path: Path to the file.
            mode: File open mode.
            encoding: File encoding.
            **kwargs: Additional arguments for open().
        """
        self.file_path = Path(file_path)
        self.mode = mode
        self.encoding = encoding
        self.kwargs = kwargs
        self._handle = None
        self._is_open = False

    def __enter__(self):
        """Open the file and return the handle."""
        if self._is_open:
            raise ResourceError("File handle is already open")

        try:
            if self.encoding:
                self._handle = open(self.file_path, self.mode,
                                  encoding=self.encoding, **self.kwargs)
            else:
                self._handle = open(self.file_path, self.mode, **self.kwargs)
            self._is_open = True
            logger.debug(f"Opened file: {self.file_path}")
            return self._handle
        except Exception as e:
            logger.error(f"Failed to open file {self.file_path}: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close the file handle."""
        if self._is_open and self._handle:
            try:
                self._handle.close()
                logger.debug(f"Closed file: {self.file_path}")
            except Exception as e:
                logger.warning(f"Error closing file {self.file_path}: {e}")
            finally:
                self._is_open = False
                self._handle = None


class TemporaryDirectory:
    """
    A temporary directory that's automatically cleaned up.

    This class creates a temporary directory and ensures it's removed
    when the context exits or the object is destroyed.
    """

    def __init__(self, prefix: str = 'annotator_', suffix: str = '_tmp',
                 dir: Optional[Union[str, Path]] = None):
        """
        Initialize temporary directory.

        Args:
            prefix: Prefix for directory name.
            suffix: Suffix for directory name.
            dir: Parent directory for temporary directory.
        """
        self.prefix = prefix
        self.suffix = suffix
        self.dir = str(dir) if dir else None
        self._path = None

    def __enter__(self) -> Path:
        """Create temporary directory and return path."""
        self._path = Path(tempfile.mkdtemp(
            prefix=self.prefix,
            suffix=self.suffix,
            dir=self.dir
        ))
        logger.debug(f"Created temporary directory: {self._path}")
        return self._path

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Remove temporary directory."""
        if self._path and self._path.exists():
            try:
                shutil.rmtree(self._path)
                logger.debug(f"Removed temporary directory: {self._path}")
            except Exception as e:
                logger.warning(f"Error removing temporary directory {self._path}: {e}")

    def cleanup(self):
        """Manually cleanup the temporary directory."""
        self.__exit__(None, None, None)


class ResourceTransaction:
    """
    A transaction manager for resources that ensures rollback on failure.

    This class manages multiple resources as a single transaction,
    rolling back all changes if any operation fails.
    """

    def __init__(self):
        """Initialize resource transaction."""
        self._operations: List[Callable] = []
        self._rollback_operations: List[Callable] = []
        self._committed = False

    def add_operation(self, operation: Callable, rollback: Callable):
        """
        Add an operation to the transaction.

        Args:
            operation: The operation to perform.
            rollback: The rollback operation.
        """
        self._operations.append(operation)
        self._rollback_operations.append(rollback)

    def __enter__(self):
        """Enter transaction context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit transaction context."""
        if exc_type is not None or not self._committed:
            # Exception occurred or commit not called, rollback
            self.rollback()

    def commit(self):
        """Commit the transaction."""
        try:
            for operation in self._operations:
                operation()
            self._committed = True
            logger.debug("Transaction committed successfully")
        except Exception as e:
            logger.error(f"Transaction commit failed: {e}")
            self.rollback()
            raise

    def rollback(self):
        """Rollback the transaction."""
        errors = []
        for rollback_op in reversed(self._rollback_operations):
            try:
                rollback_op()
            except Exception as e:
                errors.append(e)
                logger.warning(f"Error during rollback: {e}")

        if errors:
            logger.error(f"Transaction rollback completed with {len(errors)} errors")
        else:
            logger.debug("Transaction rolled back successfully")


@contextmanager
def managed_file(file_path: Union[str, Path], mode: str = 'r',
                encoding: Optional[str] = None, **kwargs):
    """
    Context manager for file handles with automatic cleanup.

    Args:
        file_path: Path to the file.
        mode: File open mode.
        encoding: File encoding.
        **kwargs: Additional arguments for open().

    Yields:
        File handle.

    Example:
        with managed_file('data.json', 'r') as f:
            data = json.load(f)
    """
    with ManagedFileHandle(file_path, mode, encoding, **kwargs) as handle:
        yield handle


@contextmanager
def temporary_file(suffix: str = '', prefix: str = 'annotator_',
                  dir: Optional[Union[str, Path]] = None,
                  delete: bool = True, mode: str = 'w+b'):
    """
    Context manager for temporary files.

    Args:
        suffix: File suffix.
        prefix: File prefix.
        dir: Directory for temporary file.
        delete: Whether to delete file on exit.
        mode: File open mode.

    Yields:
        Tuple of (file_handle, file_path).

    Example:
        with temporary_file(suffix='.json', mode='w') as (f, path):
            json.dump(data, f)
            # File is automatically cleaned up
    """
    fd, path = tempfile.mkstemp(
        suffix=suffix,
        prefix=prefix,
        dir=str(dir) if dir else None
    )

    try:
        with os.fdopen(fd, mode) as f:
            yield f, Path(path)
    finally:
        if delete and Path(path).exists():
            try:
                os.unlink(path)
                logger.debug(f"Removed temporary file: {path}")
            except Exception as e:
                logger.warning(f"Error removing temporary file {path}: {e}")


@contextmanager
def resource_scope(*resources: ManagedResource):
    """
    Context manager for managing multiple resources.

    Args:
        *resources: Resources to manage.

    Example:
        with resource_scope(resource1, resource2):
            # Use resources
            pass
        # All resources are automatically cleaned up
    """
    stack = ExitStack()
    try:
        managed_resources = []
        for resource in resources:
            managed_resources.append(stack.enter_context(resource))
        yield managed_resources
    finally:
        stack.close()


# Global resource registry for cleanup at exit
_global_resources: List[ManagedResource] = []
_global_lock = Lock()


def register_for_cleanup(resource: ManagedResource):
    """
    Register a resource for cleanup at program exit.

    Args:
        resource: The resource to register.
    """
    with _global_lock:
        _global_resources.append(resource)


def _cleanup_global_resources():
    """Cleanup all globally registered resources."""
    with _global_lock:
        for resource in _global_resources:
            try:
                resource.dispose()
            except Exception as e:
                logger.warning(f"Error during global resource cleanup: {e}")
        _global_resources.clear()


# Register cleanup function to run at exit
atexit.register(_cleanup_global_resources)