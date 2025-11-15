"""
Comprehensive tests for resource management utilities.
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import MagicMock, patch, call

from annotation_toolkit.utils.resources import (
    ManagedResource,
    ResourcePool,
    ManagedFileHandle,
    TemporaryDirectory,
    ResourceTransaction,
    managed_file,
    temporary_file,
    resource_scope,
    register_for_cleanup,
    _cleanup_global_resources,
)
from annotation_toolkit.utils.errors import ResourceError


class TestManagedResource(unittest.TestCase):
    """Test cases for ManagedResource class."""

    def test_initialization(self):
        """Test managed resource initialization."""
        cleanup_func = MagicMock()
        resource = ManagedResource("test_resource", cleanup_func)
        self.assertEqual(resource.resource, "test_resource")
        self.assertFalse(resource._is_disposed)

    def test_context_manager_basic(self):
        """Test basic context manager usage."""
        cleanup_func = MagicMock()

        with ManagedResource("test", cleanup_func) as res:
            self.assertEqual(res, "test")

        cleanup_func.assert_called_once_with("test")

    def test_manual_dispose(self):
        """Test manual resource disposal."""
        cleanup_func = MagicMock()
        resource = ManagedResource("test", cleanup_func)

        resource.dispose()

        cleanup_func.assert_called_once_with("test")
        self.assertTrue(resource._is_disposed)

    def test_double_dispose_safe(self):
        """Test that double disposal is safe."""
        cleanup_func = MagicMock()
        resource = ManagedResource("test", cleanup_func)

        resource.dispose()
        resource.dispose()

        # Should only be called once
        cleanup_func.assert_called_once()

    def test_enter_after_dispose_raises_error(self):
        """Test that entering disposed resource raises error."""
        cleanup_func = MagicMock()
        resource = ManagedResource("test", cleanup_func)
        resource.dispose()

        with self.assertRaises(ResourceError):
            with resource:
                pass

    def test_cleanup_error_handling(self):
        """Test that cleanup errors are handled gracefully."""
        cleanup_func = MagicMock(side_effect=Exception("cleanup failed"))
        resource = ManagedResource("test", cleanup_func)

        # Should not raise exception
        resource.dispose()
        self.assertTrue(resource._is_disposed)

    def test_destructor_cleanup(self):
        """Test that destructor calls dispose."""
        cleanup_func = MagicMock()
        resource = ManagedResource("test", cleanup_func)

        # Manually call destructor
        resource.__del__()

        cleanup_func.assert_called_once()


class TestResourcePool(unittest.TestCase):
    """Test cases for ResourcePool class."""

    def test_initialization(self):
        """Test resource pool initialization."""
        pool = ResourcePool(max_size=5)
        self.assertEqual(pool.max_size, 5)

    def test_add_resource(self):
        """Test adding resource to pool."""
        pool = ResourcePool()
        cleanup_func = MagicMock()

        resource_id = pool.add_resource("resource1", cleanup_func)
        self.assertIsInstance(resource_id, int)

    def test_get_resource(self):
        """Test getting resource from pool."""
        pool = ResourcePool()
        cleanup_func = MagicMock()

        resource_id = pool.add_resource("resource1", cleanup_func)
        retrieved = pool.get_resource(resource_id)

        self.assertEqual(retrieved, "resource1")

    def test_get_nonexistent_resource(self):
        """Test getting nonexistent resource returns None."""
        pool = ResourcePool()
        result = pool.get_resource(99999)
        self.assertIsNone(result)

    def test_return_resource(self):
        """Test returning resource to pool."""
        pool = ResourcePool()
        cleanup_func = MagicMock()

        resource_id = pool.add_resource("resource1", cleanup_func)
        pool.get_resource(resource_id)
        pool.return_resource(resource_id)

        # Resource should be back in pool
        retrieved = pool.get_resource(resource_id)
        self.assertEqual(retrieved, "resource1")

    def test_max_size_enforcement(self):
        """Test that max size is enforced."""
        pool = ResourcePool(max_size=2)
        cleanup_func = MagicMock()

        pool.add_resource("resource1", cleanup_func)
        pool.add_resource("resource2", cleanup_func)
        pool.add_resource("resource3", cleanup_func)  # Should remove resource1

        # Cleanup should have been called for oldest resource
        self.assertTrue(cleanup_func.called)

    def test_clear_pool(self):
        """Test clearing the pool."""
        pool = ResourcePool()
        cleanup_func = MagicMock()

        pool.add_resource("resource1", cleanup_func)
        pool.add_resource("resource2", cleanup_func)

        pool.clear()

        # Cleanup should be called for all resources
        self.assertEqual(cleanup_func.call_count, 2)

    def test_pool_destructor(self):
        """Test that pool destructor clears resources."""
        cleanup_func = MagicMock()
        pool = ResourcePool()
        pool.add_resource("resource1", cleanup_func)

        pool.__del__()

        cleanup_func.assert_called_once()


class TestManagedFileHandle(unittest.TestCase):
    """Test cases for ManagedFileHandle class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = Path(self.temp_dir) / "test.txt"
        self.test_file.write_text("test content")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test file handle initialization."""
        handle = ManagedFileHandle(self.test_file, mode='r')
        self.assertEqual(handle.file_path, self.test_file)
        self.assertEqual(handle.mode, 'r')

    def test_context_manager_read(self):
        """Test reading file with context manager."""
        with ManagedFileHandle(self.test_file, mode='r') as f:
            content = f.read()

        self.assertEqual(content, "test content")

    def test_context_manager_write(self):
        """Test writing file with context manager."""
        write_file = Path(self.temp_dir) / "write.txt"

        with ManagedFileHandle(write_file, mode='w') as f:
            f.write("new content")

        self.assertEqual(write_file.read_text(), "new content")

    def test_file_handle_with_encoding(self):
        """Test file handle with specific encoding."""
        with ManagedFileHandle(self.test_file, mode='r', encoding='utf-8') as f:
            content = f.read()

        self.assertIsInstance(content, str)

    def test_enter_twice_raises_error(self):
        """Test that opening already open handle raises error."""
        handle = ManagedFileHandle(self.test_file, mode='r')

        with handle:
            with self.assertRaises(ResourceError):
                handle.__enter__()

    def test_file_closed_on_exit(self):
        """Test that file is closed on context exit."""
        handle = ManagedFileHandle(self.test_file, mode='r')

        with handle as f:
            self.assertFalse(f.closed)

        self.assertFalse(handle._is_open)

    def test_file_nonexistent_raises_error(self):
        """Test that opening nonexistent file raises error."""
        nonexistent = Path(self.temp_dir) / "nonexistent.txt"

        with self.assertRaises(FileNotFoundError):
            with ManagedFileHandle(nonexistent, mode='r'):
                pass


class TestTemporaryDirectory(unittest.TestCase):
    """Test cases for TemporaryDirectory class."""

    def test_context_manager_creates_directory(self):
        """Test that context manager creates directory."""
        with TemporaryDirectory() as temp_dir:
            self.assertTrue(temp_dir.exists())
            self.assertTrue(temp_dir.is_dir())

    def test_directory_removed_on_exit(self):
        """Test that directory is removed on exit."""
        temp_path = None

        with TemporaryDirectory() as temp_dir:
            temp_path = temp_dir
            self.assertTrue(temp_path.exists())

        self.assertFalse(temp_path.exists())

    def test_custom_prefix_suffix(self):
        """Test custom prefix and suffix."""
        with TemporaryDirectory(prefix='test_', suffix='_end') as temp_dir:
            self.assertTrue(temp_dir.name.startswith('test_'))
            self.assertTrue(temp_dir.name.endswith('_end'))

    def test_custom_parent_directory(self):
        """Test custom parent directory."""
        parent = tempfile.mkdtemp()

        try:
            with TemporaryDirectory(dir=parent) as temp_dir:
                self.assertEqual(temp_dir.parent, Path(parent))
        finally:
            import shutil
            shutil.rmtree(parent, ignore_errors=True)

    def test_manual_cleanup(self):
        """Test manual cleanup method."""
        temp_dir_obj = TemporaryDirectory()
        temp_path = temp_dir_obj.__enter__()

        self.assertTrue(temp_path.exists())

        temp_dir_obj.cleanup()

        self.assertFalse(temp_path.exists())

    def test_files_in_directory_removed(self):
        """Test that files in directory are also removed."""
        with TemporaryDirectory() as temp_dir:
            test_file = temp_dir / "test.txt"
            test_file.write_text("content")
            temp_path = temp_dir

        self.assertFalse(temp_path.exists())
        self.assertFalse(test_file.exists())


class TestResourceTransaction(unittest.TestCase):
    """Test cases for ResourceTransaction class."""

    def test_initialization(self):
        """Test transaction initialization."""
        transaction = ResourceTransaction()
        self.assertFalse(transaction._committed)

    def test_add_operation(self):
        """Test adding operations to transaction."""
        transaction = ResourceTransaction()
        op = MagicMock()
        rollback = MagicMock()

        transaction.add_operation(op, rollback)

        self.assertEqual(len(transaction._operations), 1)
        self.assertEqual(len(transaction._rollback_operations), 1)

    def test_commit_success(self):
        """Test successful transaction commit."""
        transaction = ResourceTransaction()
        op1 = MagicMock()
        op2 = MagicMock()
        rollback1 = MagicMock()
        rollback2 = MagicMock()

        transaction.add_operation(op1, rollback1)
        transaction.add_operation(op2, rollback2)

        transaction.commit()

        op1.assert_called_once()
        op2.assert_called_once()
        rollback1.assert_not_called()
        rollback2.assert_not_called()
        self.assertTrue(transaction._committed)

    def test_commit_failure_triggers_rollback(self):
        """Test that commit failure triggers rollback."""
        transaction = ResourceTransaction()
        op1 = MagicMock()
        op2 = MagicMock(side_effect=Exception("operation failed"))
        rollback1 = MagicMock()
        rollback2 = MagicMock()

        transaction.add_operation(op1, rollback1)
        transaction.add_operation(op2, rollback2)

        with self.assertRaises(Exception):
            transaction.commit()

        # Both rollbacks should be called in reverse order
        rollback1.assert_called_once()
        rollback2.assert_called_once()

    def test_context_manager_auto_rollback(self):
        """Test that context manager auto-rollbacks on exception."""
        rollback = MagicMock()

        with self.assertRaises(ValueError):
            with ResourceTransaction() as transaction:
                transaction.add_operation(lambda: None, rollback)
                raise ValueError("test error")

        rollback.assert_called_once()

    def test_context_manager_no_commit_rollsback(self):
        """Test that exiting without commit triggers rollback."""
        rollback = MagicMock()

        with ResourceTransaction() as transaction:
            transaction.add_operation(lambda: None, rollback)
            # Don't call commit

        rollback.assert_called_once()

    def test_manual_rollback(self):
        """Test manual rollback."""
        transaction = ResourceTransaction()
        rollback1 = MagicMock()
        rollback2 = MagicMock()

        transaction.add_operation(lambda: None, rollback1)
        transaction.add_operation(lambda: None, rollback2)

        transaction.rollback()

        rollback1.assert_called_once()
        rollback2.assert_called_once()

    def test_rollback_errors_handled(self):
        """Test that rollback errors are handled gracefully."""
        transaction = ResourceTransaction()
        rollback = MagicMock(side_effect=Exception("rollback failed"))

        transaction.add_operation(lambda: None, rollback)

        # Should not raise exception
        transaction.rollback()


class TestManagedFileContextManager(unittest.TestCase):
    """Test cases for managed_file context manager."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = Path(self.temp_dir) / "test.txt"
        self.test_file.write_text("test content")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_managed_file_read(self):
        """Test managed_file for reading."""
        with managed_file(self.test_file, 'r') as f:
            content = f.read()

        self.assertEqual(content, "test content")

    def test_managed_file_write(self):
        """Test managed_file for writing."""
        write_file = Path(self.temp_dir) / "write.txt"

        with managed_file(write_file, 'w') as f:
            f.write("new content")

        self.assertEqual(write_file.read_text(), "new content")

    def test_managed_file_with_encoding(self):
        """Test managed_file with encoding."""
        with managed_file(self.test_file, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIsInstance(content, str)


class TestTemporaryFileContextManager(unittest.TestCase):
    """Test cases for temporary_file context manager."""

    def test_temporary_file_basic(self):
        """Test basic temporary file creation."""
        with temporary_file(suffix='.txt', mode='w+') as (f, path):
            self.assertTrue(path.exists())
            f.write("temp content")
            f.seek(0)
            content = f.read()
            self.assertEqual(content, "temp content")

    def test_temporary_file_deleted_on_exit(self):
        """Test that temporary file is deleted on exit."""
        temp_path = None

        with temporary_file(mode='w+') as (f, path):
            temp_path = path
            self.assertTrue(temp_path.exists())

        self.assertFalse(temp_path.exists())

    def test_temporary_file_with_custom_prefix(self):
        """Test temporary file with custom prefix."""
        with temporary_file(prefix='test_', suffix='.txt', mode='w+') as (f, path):
            self.assertTrue(path.name.startswith('test_'))
            self.assertTrue(path.name.endswith('.txt'))

    def test_temporary_file_no_delete(self):
        """Test temporary file without deletion."""
        temp_path = None

        with temporary_file(delete=False, mode='w+') as (f, path):
            temp_path = path
            f.write("content")

        # Should still exist
        self.assertTrue(temp_path.exists())

        # Clean up manually
        os.unlink(temp_path)


class TestResourceScopeContextManager(unittest.TestCase):
    """Test cases for resource_scope context manager."""

    def test_resource_scope_single_resource(self):
        """Test resource_scope with single resource."""
        cleanup_func = MagicMock()
        resource = ManagedResource("test", cleanup_func)

        with resource_scope(resource) as resources:
            self.assertEqual(len(resources), 1)
            self.assertEqual(resources[0], "test")

        cleanup_func.assert_called_once()

    def test_resource_scope_multiple_resources(self):
        """Test resource_scope with multiple resources."""
        cleanup1 = MagicMock()
        cleanup2 = MagicMock()
        resource1 = ManagedResource("res1", cleanup1)
        resource2 = ManagedResource("res2", cleanup2)

        with resource_scope(resource1, resource2) as resources:
            self.assertEqual(len(resources), 2)
            self.assertEqual(resources[0], "res1")
            self.assertEqual(resources[1], "res2")

        cleanup1.assert_called_once()
        cleanup2.assert_called_once()

    def test_resource_scope_exception_cleanup(self):
        """Test that resources are cleaned up on exception."""
        cleanup = MagicMock()
        resource = ManagedResource("test", cleanup)

        with self.assertRaises(ValueError):
            with resource_scope(resource):
                raise ValueError("test error")

        cleanup.assert_called_once()


class TestGlobalResourceRegistry(unittest.TestCase):
    """Test cases for global resource registry."""

    def test_register_for_cleanup(self):
        """Test registering resource for cleanup."""
        cleanup_func = MagicMock()
        resource = ManagedResource("test", cleanup_func)

        register_for_cleanup(resource)

        # Manually trigger cleanup
        _cleanup_global_resources()

        cleanup_func.assert_called_once()

    def test_cleanup_global_resources(self):
        """Test cleaning up global resources."""
        cleanup1 = MagicMock()
        cleanup2 = MagicMock()
        resource1 = ManagedResource("res1", cleanup1)
        resource2 = ManagedResource("res2", cleanup2)

        register_for_cleanup(resource1)
        register_for_cleanup(resource2)

        _cleanup_global_resources()

        cleanup1.assert_called_once()
        cleanup2.assert_called_once()


if __name__ == "__main__":
    unittest.main()
