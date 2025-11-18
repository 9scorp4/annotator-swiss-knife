"""
Unit tests for auto-save system.

This module tests AutoSaveManager for automatic state saving,
crash recovery, backup rotation, and signal emissions.
"""

import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QTimer

from annotation_toolkit.ui.gui.utils.auto_save import AutoSaveManager


class TestAutoSaveManagerInit(unittest.TestCase):
    """Test AutoSaveManager initialization."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_autosave_")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_auto_save_manager_with_default_dir(self):
        """Test AutoSaveManager with default save directory."""
        manager = AutoSaveManager()

        expected_dir = Path.home() / "annotation_toolkit_data" / "autosave"
        self.assertEqual(manager.save_dir, expected_dir)
        self.assertTrue(manager.save_dir.exists())

        # Cleanup
        manager.stop()

    def test_auto_save_manager_with_custom_dir(self):
        """Test AutoSaveManager with custom save directory."""
        custom_dir = Path(self.test_dir) / "custom_autosave"
        manager = AutoSaveManager(save_dir=custom_dir)

        self.assertEqual(manager.save_dir, custom_dir)
        self.assertTrue(custom_dir.exists())

        manager.stop()

    def test_auto_save_manager_creates_save_dir_if_not_exists(self):
        """Test AutoSaveManager creates save directory if it doesn't exist."""
        custom_dir = Path(self.test_dir) / "new" / "nested" / "dir"
        self.assertFalse(custom_dir.exists())

        manager = AutoSaveManager(save_dir=custom_dir)

        self.assertTrue(custom_dir.exists())
        manager.stop()

    def test_auto_save_manager_with_custom_interval(self):
        """Test AutoSaveManager with custom interval."""
        manager = AutoSaveManager(save_dir=Path(self.test_dir), interval_seconds=30)

        self.assertEqual(manager.interval_seconds, 30)
        manager.stop()

    def test_auto_save_manager_with_custom_max_backups(self):
        """Test AutoSaveManager with custom max_backups."""
        manager = AutoSaveManager(save_dir=Path(self.test_dir), max_backups=10)

        self.assertEqual(manager.max_backups, 10)
        manager.stop()

    def test_auto_save_manager_initializes_timer(self):
        """Test AutoSaveManager initializes QTimer."""
        manager = AutoSaveManager(save_dir=Path(self.test_dir))

        self.assertIsInstance(manager._timer, QTimer)
        self.assertFalse(manager._timer.isActive())
        manager.stop()

    def test_auto_save_manager_initializes_empty_callbacks(self):
        """Test AutoSaveManager initializes with empty callback dict."""
        manager = AutoSaveManager(save_dir=Path(self.test_dir))

        self.assertEqual(len(manager._save_callbacks), 0)
        manager.stop()


class TestAutoSaveManagerRegistration(unittest.TestCase):
    """Test AutoSaveManager registration methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_autosave_")
        self.manager = AutoSaveManager(save_dir=Path(self.test_dir))

    def tearDown(self):
        """Clean up test fixtures."""
        self.manager.stop()
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_register_callback(self):
        """Test registering a save callback."""
        callback = lambda: {"test": "data"}
        self.manager.register("test_key", callback)

        self.assertIn("test_key", self.manager._save_callbacks)
        self.assertEqual(self.manager._save_callbacks["test_key"], callback)

    def test_register_multiple_callbacks(self):
        """Test registering multiple callbacks."""
        callback1 = lambda: {"test1": "data1"}
        callback2 = lambda: {"test2": "data2"}

        self.manager.register("key1", callback1)
        self.manager.register("key2", callback2)

        self.assertEqual(len(self.manager._save_callbacks), 2)
        self.assertIn("key1", self.manager._save_callbacks)
        self.assertIn("key2", self.manager._save_callbacks)

    def test_register_overwrites_existing_callback(self):
        """Test registering same key overwrites existing callback."""
        callback1 = lambda: {"version": 1}
        callback2 = lambda: {"version": 2}

        self.manager.register("test_key", callback1)
        self.manager.register("test_key", callback2)

        self.assertEqual(len(self.manager._save_callbacks), 1)
        self.assertEqual(self.manager._save_callbacks["test_key"], callback2)

    def test_unregister_callback(self):
        """Test unregistering a callback."""
        callback = lambda: {"test": "data"}
        self.manager.register("test_key", callback)

        self.manager.unregister("test_key")

        self.assertNotIn("test_key", self.manager._save_callbacks)

    def test_unregister_nonexistent_callback(self):
        """Test unregistering non-existent callback does nothing."""
        # Should not raise error
        self.manager.unregister("nonexistent_key")

        # No callbacks should exist
        self.assertEqual(len(self.manager._save_callbacks), 0)

    def test_unregister_does_not_affect_other_callbacks(self):
        """Test unregistering one callback doesn't affect others."""
        callback1 = lambda: {"test1": "data1"}
        callback2 = lambda: {"test2": "data2"}

        self.manager.register("key1", callback1)
        self.manager.register("key2", callback2)

        self.manager.unregister("key1")

        self.assertNotIn("key1", self.manager._save_callbacks)
        self.assertIn("key2", self.manager._save_callbacks)


class TestAutoSaveManagerTimerControl(unittest.TestCase):
    """Test AutoSaveManager timer control methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_autosave_")
        self.manager = AutoSaveManager(save_dir=Path(self.test_dir), interval_seconds=1)

    def tearDown(self):
        """Clean up test fixtures."""
        self.manager.stop()
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_start_timer(self):
        """Test starting the auto-save timer."""
        self.assertFalse(self.manager._timer.isActive())

        self.manager.start()

        self.assertTrue(self.manager._timer.isActive())

    def test_start_timer_sets_correct_interval(self):
        """Test timer interval is set correctly."""
        self.manager.start()

        # Interval in milliseconds
        self.assertEqual(self.manager._timer.interval(), 1000)

    def test_start_timer_idempotent(self):
        """Test starting timer multiple times is idempotent."""
        self.manager.start()
        self.manager.start()

        # Should only be one active timer
        self.assertTrue(self.manager._timer.isActive())

    def test_stop_timer(self):
        """Test stopping the auto-save timer."""
        self.manager.start()
        self.assertTrue(self.manager._timer.isActive())

        self.manager.stop()

        self.assertFalse(self.manager._timer.isActive())

    def test_stop_timer_idempotent(self):
        """Test stopping timer multiple times is idempotent."""
        self.manager.start()
        self.manager.stop()
        self.manager.stop()

        # Should be stopped
        self.assertFalse(self.manager._timer.isActive())

    def test_stop_timer_when_not_started(self):
        """Test stopping timer that was never started."""
        # Should not raise error
        self.manager.stop()

        self.assertFalse(self.manager._timer.isActive())


class TestAutoSaveManagerSaving(unittest.TestCase):
    """Test AutoSaveManager save operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_autosave_")
        self.manager = AutoSaveManager(save_dir=Path(self.test_dir))

    def tearDown(self):
        """Clean up test fixtures."""
        self.manager.stop()
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_save_now_with_specific_key(self):
        """Test immediate save for specific key."""
        test_data = {"content": "test data"}
        callback = lambda: test_data

        self.manager.register("test_key", callback)
        self.manager.save_now("test_key")

        # Verify file was created
        save_path = self.manager._get_save_path("test_key")
        self.assertTrue(save_path.exists())

        # Verify content
        with open(save_path, 'r') as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data["state"], test_data)

    def test_save_now_all_keys(self):
        """Test immediate save for all keys."""
        callback1 = lambda: {"data": 1}
        callback2 = lambda: {"data": 2}

        self.manager.register("key1", callback1)
        self.manager.register("key2", callback2)

        self.manager.save_now()

        # Both should be saved
        self.assertTrue(self.manager._get_save_path("key1").exists())
        self.assertTrue(self.manager._get_save_path("key2").exists())

    def test_save_state_creates_file_with_metadata(self):
        """Test save creates file with proper metadata."""
        test_data = {"test": "value"}
        callback = lambda: test_data

        self.manager.register("test_key", callback)
        result = self.manager._save_state("test_key")

        self.assertTrue(result)

        # Read saved file
        save_path = self.manager._get_save_path("test_key")
        with open(save_path, 'r') as f:
            saved_data = json.load(f)

        # Verify structure
        self.assertIn("save_key", saved_data)
        self.assertIn("timestamp", saved_data)
        self.assertIn("version", saved_data)
        self.assertIn("state", saved_data)

        self.assertEqual(saved_data["save_key"], "test_key")
        self.assertEqual(saved_data["state"], test_data)

    def test_save_state_returns_false_for_unregistered_key(self):
        """Test save returns False for unregistered key."""
        result = self.manager._save_state("nonexistent_key")

        self.assertFalse(result)

    def test_save_state_handles_callback_exception(self):
        """Test save handles exceptions from callback."""
        def failing_callback():
            raise ValueError("Test error")

        self.manager.register("test_key", failing_callback)
        result = self.manager._save_state("test_key")

        self.assertFalse(result)

    def test_save_state_emits_save_completed_signal(self):
        """Test save emits save_completed signal on success."""
        callback = lambda: {"test": "data"}
        self.manager.register("test_key", callback)

        # Connect signal to capture emissions
        signal_received = []
        self.manager.save_completed.connect(lambda key: signal_received.append(key))

        self.manager._save_state("test_key")

        self.assertEqual(signal_received, ["test_key"])

    def test_save_state_emits_save_failed_signal(self):
        """Test save emits save_failed signal on failure."""
        def failing_callback():
            raise ValueError("Test error")

        self.manager.register("test_key", failing_callback)

        # Connect signal to capture emissions
        signal_received = []
        self.manager.save_failed.connect(
            lambda key, msg: signal_received.append((key, msg))
        )

        self.manager._save_state("test_key")

        self.assertEqual(len(signal_received), 1)
        self.assertEqual(signal_received[0][0], "test_key")
        self.assertIn("Test error", signal_received[0][1])

    def test_save_state_updates_last_save_time(self):
        """Test save updates last save time tracking."""
        callback = lambda: {"test": "data"}
        self.manager.register("test_key", callback)

        before_time = time.time()
        self.manager._save_state("test_key")
        after_time = time.time()

        self.assertIn("test_key", self.manager._last_save_times)
        last_save = self.manager._last_save_times["test_key"]
        self.assertGreaterEqual(last_save, before_time)
        self.assertLessEqual(last_save, after_time)


class TestAutoSaveManagerLoading(unittest.TestCase):
    """Test AutoSaveManager load operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_autosave_")
        self.manager = AutoSaveManager(save_dir=Path(self.test_dir))

    def tearDown(self):
        """Clean up test fixtures."""
        self.manager.stop()
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_load_state_returns_saved_state(self):
        """Test load_state returns previously saved state."""
        test_data = {"content": "test data", "value": 42}
        callback = lambda: test_data

        self.manager.register("test_key", callback)
        self.manager.save_now("test_key")

        loaded_state = self.manager.load_state("test_key")

        self.assertEqual(loaded_state, test_data)

    def test_load_state_returns_none_for_nonexistent_file(self):
        """Test load_state returns None when file doesn't exist."""
        loaded_state = self.manager.load_state("nonexistent_key")

        self.assertIsNone(loaded_state)

    def test_load_state_handles_invalid_json(self):
        """Test load_state handles invalid JSON gracefully."""
        save_path = self.manager._get_save_path("test_key")

        # Write invalid JSON
        with open(save_path, 'w') as f:
            f.write("{ invalid json }")

        loaded_state = self.manager.load_state("test_key")

        self.assertIsNone(loaded_state)

    def test_load_state_handles_missing_state_field(self):
        """Test load_state handles missing 'state' field."""
        save_path = self.manager._get_save_path("test_key")

        # Write valid JSON without 'state' field
        with open(save_path, 'w') as f:
            json.dump({"save_key": "test_key", "timestamp": "2024-01-01"}, f)

        loaded_state = self.manager.load_state("test_key")

        self.assertIsNone(loaded_state)

    def test_has_recovery_data_returns_true_when_exists(self):
        """Test has_recovery_data returns True when data exists."""
        callback = lambda: {"test": "data"}
        self.manager.register("test_key", callback)
        self.manager.save_now("test_key")

        self.assertTrue(self.manager.has_recovery_data("test_key"))

    def test_has_recovery_data_returns_false_when_not_exists(self):
        """Test has_recovery_data returns False when no data."""
        self.assertFalse(self.manager.has_recovery_data("nonexistent_key"))

    def test_get_recovery_timestamp_returns_timestamp(self):
        """Test get_recovery_timestamp returns saved timestamp."""
        callback = lambda: {"test": "data"}
        self.manager.register("test_key", callback)
        self.manager.save_now("test_key")

        timestamp = self.manager.get_recovery_timestamp("test_key")

        self.assertIsNotNone(timestamp)
        # Should be ISO format string
        self.assertIn("T", timestamp)

    def test_get_recovery_timestamp_returns_none_when_not_exists(self):
        """Test get_recovery_timestamp returns None when no save exists."""
        timestamp = self.manager.get_recovery_timestamp("nonexistent_key")

        self.assertIsNone(timestamp)


class TestAutoSaveManagerBackupRotation(unittest.TestCase):
    """Test AutoSaveManager backup rotation."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_autosave_")
        self.manager = AutoSaveManager(
            save_dir=Path(self.test_dir),
            max_backups=3
        )

    def tearDown(self):
        """Clean up test fixtures."""
        self.manager.stop()
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_rotate_backups_creates_backup(self):
        """Test backup rotation creates backup files."""
        callback = lambda: {"version": 1}
        self.manager.register("test_key", callback)

        # Save multiple times
        self.manager.save_now("test_key")
        time.sleep(0.1)  # Ensure different timestamps
        callback = lambda: {"version": 2}
        self.manager.register("test_key", callback)
        self.manager.save_now("test_key")

        # Check for backup files
        backup_files = list(Path(self.test_dir).glob("test_key_backup_*.json"))
        self.assertGreater(len(backup_files), 0)

    def test_rotate_backups_respects_max_backups(self):
        """Test backup rotation enforces max_backups limit."""
        callback_counter = {"count": 0}

        def changing_callback():
            callback_counter["count"] += 1
            return {"version": callback_counter["count"]}

        self.manager.register("test_key", changing_callback)

        # Save more than max_backups times
        for _ in range(6):
            self.manager.save_now("test_key")
            time.sleep(0.1)  # Ensure different timestamps

        # Count backup files
        backup_files = list(Path(self.test_dir).glob("test_key_backup_*.json"))

        # Should have at most max_backups (3) backup files
        self.assertLessEqual(len(backup_files), 3)


class TestAutoSaveManagerRecovery(unittest.TestCase):
    """Test AutoSaveManager recovery operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_autosave_")
        self.manager = AutoSaveManager(save_dir=Path(self.test_dir))

    def tearDown(self):
        """Clean up test fixtures."""
        self.manager.stop()
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_clear_recovery_data_removes_save_file(self):
        """Test clear_recovery_data removes save file."""
        callback = lambda: {"test": "data"}
        self.manager.register("test_key", callback)
        self.manager.save_now("test_key")

        self.assertTrue(self.manager.has_recovery_data("test_key"))

        self.manager.clear_recovery_data("test_key")

        self.assertFalse(self.manager.has_recovery_data("test_key"))

    def test_clear_recovery_data_for_nonexistent_file(self):
        """Test clearing recovery data for non-existent file."""
        # Should not raise error
        self.manager.clear_recovery_data("nonexistent_key")

    def test_get_all_recovery_keys_returns_all_keys(self):
        """Test get_all_recovery_keys returns all saved keys."""
        callback1 = lambda: {"data": 1}
        callback2 = lambda: {"data": 2}
        callback3 = lambda: {"data": 3}

        self.manager.register("key1", callback1)
        self.manager.register("key2", callback2)
        self.manager.register("key3", callback3)

        self.manager.save_now()

        recovery_keys = self.manager.get_all_recovery_keys()

        self.assertEqual(len(recovery_keys), 3)
        self.assertIn("key1", recovery_keys)
        self.assertIn("key2", recovery_keys)
        self.assertIn("key3", recovery_keys)

    def test_get_all_recovery_keys_returns_empty_when_none(self):
        """Test get_all_recovery_keys returns empty list when no saves."""
        recovery_keys = self.manager.get_all_recovery_keys()

        self.assertEqual(len(recovery_keys), 0)


class TestAutoSaveManagerFilePathHandling(unittest.TestCase):
    """Test AutoSaveManager file path handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp(prefix="test_autosave_")
        self.manager = AutoSaveManager(save_dir=Path(self.test_dir))

    def tearDown(self):
        """Clean up test fixtures."""
        self.manager.stop()
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_get_save_path_returns_correct_path(self):
        """Test _get_save_path returns correct file path."""
        save_path = self.manager._get_save_path("test_key")

        self.assertEqual(save_path.parent, Path(self.test_dir))
        self.assertTrue(save_path.name.endswith("_autosave.json"))
        self.assertIn("test_key", save_path.name)

    def test_get_save_path_sanitizes_special_characters(self):
        """Test _get_save_path sanitizes special characters."""
        save_path = self.manager._get_save_path("test/key:with*special?chars")

        # Special characters should be replaced with underscores
        self.assertNotIn("/", save_path.name)
        self.assertNotIn(":", save_path.name)
        self.assertNotIn("*", save_path.name)
        self.assertNotIn("?", save_path.name)

    def test_get_save_path_preserves_alphanumeric(self):
        """Test _get_save_path preserves alphanumeric characters."""
        save_path = self.manager._get_save_path("test_key-123")

        self.assertIn("test_key-123", save_path.name)


if __name__ == "__main__":
    unittest.main()
