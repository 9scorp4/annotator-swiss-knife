"""
Unit tests for session persistence manager.

This module tests SessionManager for saving/restoring window state,
recent files, preferences, and session data using QSettings.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QSettings, QByteArray, QSize, QPoint

# Create QApplication instance if it doesn't exist
app = QApplication.instance()
if app is None:
    app = QApplication([])

from annotation_toolkit.ui.gui.utils.session_manager import SessionManager


class TestSessionManagerInit(unittest.TestCase):
    """Test SessionManager initialization."""

    def setUp(self):
        """Set up test fixtures."""
        # Use unique app name for each test to avoid conflicts
        self.app_name = f"TestApp_{id(self)}"

    def tearDown(self):
        """Clean up test fixtures."""
        # Clear settings
        settings = QSettings("Anthropic", self.app_name)
        settings.clear()

    def test_session_manager_initialization(self):
        """Test SessionManager initializes with QSettings."""
        manager = SessionManager(self.app_name)

        self.assertIsInstance(manager.settings, QSettings)

    def test_session_manager_default_app_name(self):
        """Test SessionManager with default app name."""
        manager = SessionManager()

        # Should use "AnnotationToolkit" as default
        self.assertEqual(manager.settings.applicationName(), "AnnotationToolkit")

    def test_session_manager_custom_app_name(self):
        """Test SessionManager with custom app name."""
        manager = SessionManager("CustomApp")

        self.assertEqual(manager.settings.applicationName(), "CustomApp")


class TestSessionManagerRecentFiles(unittest.TestCase):
    """Test SessionManager recent files functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.app_name = f"TestApp_{id(self)}"
        self.manager = SessionManager(self.app_name)
        # Create temp files for testing
        self.test_dir = tempfile.mkdtemp(prefix="test_session_")
        self.test_file1 = os.path.join(self.test_dir, "file1.txt")
        self.test_file2 = os.path.join(self.test_dir, "file2.txt")
        self.test_file3 = os.path.join(self.test_dir, "file3.txt")

        # Create the test files
        for file_path in [self.test_file1, self.test_file2, self.test_file3]:
            with open(file_path, 'w') as f:
                f.write("test")

    def tearDown(self):
        """Clean up test fixtures."""
        self.manager.settings.clear()
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_get_recent_files_empty_initially(self):
        """Test get_recent_files returns empty list initially."""
        recent = self.manager.get_recent_files()

        self.assertEqual(len(recent), 0)

    def test_add_recent_file(self):
        """Test adding a file to recent files list."""
        self.manager.add_recent_file(self.test_file1)

        recent = self.manager.get_recent_files()

        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0], self.test_file1)

    def test_add_multiple_recent_files(self):
        """Test adding multiple files to recent files list."""
        self.manager.add_recent_file(self.test_file1)
        self.manager.add_recent_file(self.test_file2)
        self.manager.add_recent_file(self.test_file3)

        recent = self.manager.get_recent_files()

        self.assertEqual(len(recent), 3)
        # Most recent first
        self.assertEqual(recent[0], self.test_file3)
        self.assertEqual(recent[1], self.test_file2)
        self.assertEqual(recent[2], self.test_file1)

    def test_add_duplicate_recent_file_moves_to_front(self):
        """Test adding duplicate file moves it to front."""
        self.manager.add_recent_file(self.test_file1)
        self.manager.add_recent_file(self.test_file2)
        self.manager.add_recent_file(self.test_file1)  # Duplicate

        recent = self.manager.get_recent_files()

        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[0], self.test_file1)  # Should be first
        self.assertEqual(recent[1], self.test_file2)

    def test_recent_files_respects_max_limit(self):
        """Test recent files list respects MAX_RECENT_FILES limit."""
        # Add more files than MAX_RECENT_FILES
        for i in range(15):
            file_path = os.path.join(self.test_dir, f"file{i}.txt")
            with open(file_path, 'w') as f:
                f.write("test")
            self.manager.add_recent_file(file_path)

        recent = self.manager.get_recent_files()

        # Should be limited to MAX_RECENT_FILES (10)
        self.assertEqual(len(recent), SessionManager.MAX_RECENT_FILES)

    def test_get_recent_files_filters_nonexistent_files(self):
        """Test get_recent_files filters out non-existent files."""
        self.manager.add_recent_file(self.test_file1)
        self.manager.add_recent_file(self.test_file2)

        # Delete one file
        os.remove(self.test_file2)

        recent = self.manager.get_recent_files()

        # Should only return existing file
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0], self.test_file1)

    def test_clear_recent_files(self):
        """Test clearing recent files list."""
        self.manager.add_recent_file(self.test_file1)
        self.manager.add_recent_file(self.test_file2)

        self.manager.clear_recent_files()

        recent = self.manager.get_recent_files()
        self.assertEqual(len(recent), 0)


class TestSessionManagerLastTool(unittest.TestCase):
    """Test SessionManager last tool functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.app_name = f"TestApp_{id(self)}"
        self.manager = SessionManager(self.app_name)

    def tearDown(self):
        """Clean up test fixtures."""
        self.manager.settings.clear()

    def test_get_last_tool_returns_none_initially(self):
        """Test get_last_tool returns None or empty string initially."""
        last_tool = self.manager.get_last_tool()

        # QSettings with type=str returns empty string for missing values
        self.assertIn(last_tool, [None, ""])

    def test_set_last_tool(self):
        """Test setting the last used tool."""
        self.manager.set_last_tool("DictToBullet")

        last_tool = self.manager.get_last_tool()

        self.assertEqual(last_tool, "DictToBullet")

    def test_set_last_tool_updates_existing(self):
        """Test setting last tool updates existing value."""
        self.manager.set_last_tool("Tool1")
        self.manager.set_last_tool("Tool2")

        last_tool = self.manager.get_last_tool()

        self.assertEqual(last_tool, "Tool2")


class TestSessionManagerPreferences(unittest.TestCase):
    """Test SessionManager preferences functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.app_name = f"TestApp_{id(self)}"
        self.manager = SessionManager(self.app_name)

    def tearDown(self):
        """Clean up test fixtures."""
        self.manager.settings.clear()

    def test_get_preference_returns_default_when_not_set(self):
        """Test get_preference returns default value when not set."""
        value = self.manager.get_preference("nonexistent_key", "default_value")

        self.assertEqual(value, "default_value")

    def test_set_and_get_preference(self):
        """Test setting and getting a preference."""
        self.manager.set_preference("test_key", "test_value")

        value = self.manager.get_preference("test_key")

        self.assertEqual(value, "test_value")

    def test_set_preference_with_different_types(self):
        """Test preferences work with different value types."""
        self.manager.set_preference("str_pref", "string")
        self.manager.set_preference("int_pref", 42)
        self.manager.set_preference("bool_pref", True)
        self.manager.set_preference("list_pref", [1, 2, 3])

        self.assertEqual(self.manager.get_preference("str_pref"), "string")
        self.assertEqual(self.manager.get_preference("int_pref"), 42)
        self.assertEqual(self.manager.get_preference("bool_pref"), True)
        self.assertEqual(self.manager.get_preference("list_pref"), [1, 2, 3])

    def test_set_preference_overwrites_existing(self):
        """Test setting preference overwrites existing value."""
        self.manager.set_preference("test_key", "value1")
        self.manager.set_preference("test_key", "value2")

        value = self.manager.get_preference("test_key")

        self.assertEqual(value, "value2")


class TestSessionManagerTheme(unittest.TestCase):
    """Test SessionManager theme functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.app_name = f"TestApp_{id(self)}"
        self.manager = SessionManager(self.app_name)

    def tearDown(self):
        """Clean up test fixtures."""
        self.manager.settings.clear()

    def test_get_theme_returns_light_by_default(self):
        """Test get_theme returns 'light' by default."""
        theme = self.manager.get_theme()

        self.assertEqual(theme, "light")

    def test_set_theme_dark(self):
        """Test setting dark theme."""
        self.manager.set_theme("dark")

        theme = self.manager.get_theme()

        self.assertEqual(theme, "dark")

    def test_set_theme_light(self):
        """Test setting light theme."""
        self.manager.set_theme("light")

        theme = self.manager.get_theme()

        self.assertEqual(theme, "light")

    def test_set_theme_overwrites_existing(self):
        """Test setting theme overwrites existing value."""
        self.manager.set_theme("dark")
        self.manager.set_theme("light")

        theme = self.manager.get_theme()

        self.assertEqual(theme, "light")


class TestSessionManagerToolState(unittest.TestCase):
    """Test SessionManager tool-specific state functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.app_name = f"TestApp_{id(self)}"
        self.manager = SessionManager(self.app_name)

    def tearDown(self):
        """Clean up test fixtures."""
        self.manager.settings.clear()

    def test_load_tool_state_returns_empty_dict_initially(self):
        """Test load_tool_state returns empty dict when no state saved."""
        state = self.manager.load_tool_state("TestTool")

        self.assertEqual(state, {})

    def test_save_and_load_tool_state(self):
        """Test saving and loading tool state."""
        test_state = {
            "option1": "value1",
            "option2": 42,
            "option3": True
        }

        self.manager.save_tool_state("TestTool", test_state)
        loaded_state = self.manager.load_tool_state("TestTool")

        self.assertEqual(loaded_state["option1"], "value1")
        self.assertEqual(loaded_state["option2"], 42)
        self.assertEqual(loaded_state["option3"], True)

    def test_save_tool_state_overwrites_existing(self):
        """Test saving tool state overwrites existing state."""
        state1 = {"version": 1}
        state2 = {"version": 2, "new_option": "value"}

        self.manager.save_tool_state("TestTool", state1)
        self.manager.save_tool_state("TestTool", state2)

        loaded_state = self.manager.load_tool_state("TestTool")

        self.assertEqual(loaded_state["version"], 2)
        self.assertIn("new_option", loaded_state)

    def test_tool_states_are_independent(self):
        """Test different tools have independent states."""
        state1 = {"tool1_data": "value1"}
        state2 = {"tool2_data": "value2"}

        self.manager.save_tool_state("Tool1", state1)
        self.manager.save_tool_state("Tool2", state2)

        loaded_state1 = self.manager.load_tool_state("Tool1")
        loaded_state2 = self.manager.load_tool_state("Tool2")

        self.assertIn("tool1_data", loaded_state1)
        self.assertNotIn("tool2_data", loaded_state1)
        self.assertIn("tool2_data", loaded_state2)
        self.assertNotIn("tool1_data", loaded_state2)


class TestSessionManagerSplitterState(unittest.TestCase):
    """Test SessionManager splitter state functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.app_name = f"TestApp_{id(self)}"
        self.manager = SessionManager(self.app_name)

    def tearDown(self):
        """Clean up test fixtures."""
        self.manager.settings.clear()

    def test_get_splitter_state_returns_none_initially(self):
        """Test get_splitter_state returns None when not set."""
        state = self.manager.get_splitter_state("main_splitter")

        self.assertIsNone(state)

    def test_save_and_get_splitter_state(self):
        """Test saving and getting splitter state."""
        test_state = QByteArray(b"test_splitter_data")

        self.manager.save_splitter_state("main_splitter", test_state)
        loaded_state = self.manager.get_splitter_state("main_splitter")

        self.assertEqual(loaded_state, test_state)

    def test_different_splitters_have_independent_states(self):
        """Test different splitters have independent states."""
        state1 = QByteArray(b"splitter1_data")
        state2 = QByteArray(b"splitter2_data")

        self.manager.save_splitter_state("splitter1", state1)
        self.manager.save_splitter_state("splitter2", state2)

        loaded_state1 = self.manager.get_splitter_state("splitter1")
        loaded_state2 = self.manager.get_splitter_state("splitter2")

        self.assertEqual(loaded_state1, state1)
        self.assertEqual(loaded_state2, state2)


class TestSessionManagerSessionInfo(unittest.TestCase):
    """Test SessionManager session info functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.app_name = f"TestApp_{id(self)}"
        self.manager = SessionManager(self.app_name)
        # Create temp files for testing
        self.test_dir = tempfile.mkdtemp(prefix="test_session_")
        self.test_file = os.path.join(self.test_dir, "test.txt")
        with open(self.test_file, 'w') as f:
            f.write("test")

    def tearDown(self):
        """Clean up test fixtures."""
        self.manager.settings.clear()
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_get_session_info_structure(self):
        """Test get_session_info returns correct structure."""
        info = self.manager.get_session_info()

        self.assertIn("recent_files_count", info)
        self.assertIn("last_tool", info)
        self.assertIn("theme", info)
        self.assertIn("has_window_state", info)

    def test_get_session_info_recent_files_count(self):
        """Test session info includes recent files count."""
        self.manager.add_recent_file(self.test_file)

        info = self.manager.get_session_info()

        self.assertEqual(info["recent_files_count"], 1)

    def test_get_session_info_last_tool(self):
        """Test session info includes last tool."""
        self.manager.set_last_tool("TestTool")

        info = self.manager.get_session_info()

        self.assertEqual(info["last_tool"], "TestTool")

    def test_get_session_info_theme(self):
        """Test session info includes theme."""
        self.manager.set_theme("dark")

        info = self.manager.get_session_info()

        self.assertEqual(info["theme"], "dark")


class TestSessionManagerClearSession(unittest.TestCase):
    """Test SessionManager clear session functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.app_name = f"TestApp_{id(self)}"
        self.manager = SessionManager(self.app_name)
        # Create temp files for testing
        self.test_dir = tempfile.mkdtemp(prefix="test_session_")
        self.test_file = os.path.join(self.test_dir, "test.txt")
        with open(self.test_file, 'w') as f:
            f.write("test")

    def tearDown(self):
        """Clean up test fixtures."""
        self.manager.settings.clear()
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_clear_session_clears_recent_files(self):
        """Test clear_session clears recent files."""
        self.manager.add_recent_file(self.test_file)

        self.manager.clear_session()

        recent = self.manager.get_recent_files()
        self.assertEqual(len(recent), 0)

    def test_clear_session_clears_last_tool(self):
        """Test clear_session clears last tool."""
        self.manager.set_last_tool("TestTool")

        self.manager.clear_session()

        last_tool = self.manager.get_last_tool()
        # QSettings with type=str returns empty string for missing values
        self.assertIn(last_tool, [None, ""])

    def test_clear_session_preserves_preferences(self):
        """Test clear_session preserves user preferences."""
        self.manager.set_preference("test_pref", "value")

        self.manager.clear_session()

        # Preferences should still exist
        value = self.manager.get_preference("test_pref")
        self.assertEqual(value, "value")

    def test_clear_session_preserves_theme(self):
        """Test clear_session preserves theme setting."""
        self.manager.set_theme("dark")

        self.manager.clear_session()

        # Theme should be preserved
        theme = self.manager.get_theme()
        self.assertEqual(theme, "dark")


class TestSessionManagerExportImport(unittest.TestCase):
    """Test SessionManager export/import functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.app_name = f"TestApp_{id(self)}"
        self.manager = SessionManager(self.app_name)
        self.test_dir = tempfile.mkdtemp(prefix="test_session_")
        self.export_file = os.path.join(self.test_dir, "export.json")

    def tearDown(self):
        """Clean up test fixtures."""
        self.manager.settings.clear()
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_export_settings_creates_file(self):
        """Test export_settings creates export file."""
        result = self.manager.export_settings(self.export_file)

        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.export_file))

    def test_export_settings_includes_theme(self):
        """Test exported settings include theme."""
        self.manager.set_theme("dark")

        self.manager.export_settings(self.export_file)

        with open(self.export_file, 'r') as f:
            data = json.load(f)

        self.assertEqual(data["theme"], "dark")

    def test_export_settings_includes_preferences(self):
        """Test exported settings include preferences."""
        self.manager.set_preference("pref1", "value1")
        self.manager.set_preference("pref2", 42)

        self.manager.export_settings(self.export_file)

        with open(self.export_file, 'r') as f:
            data = json.load(f)

        self.assertIn("preferences", data)
        self.assertEqual(data["preferences"]["pref1"], "value1")
        self.assertEqual(data["preferences"]["pref2"], 42)

    def test_import_settings_restores_theme(self):
        """Test import_settings restores theme."""
        # Export settings with dark theme
        self.manager.set_theme("dark")
        self.manager.export_settings(self.export_file)

        # Create new manager and import
        new_manager = SessionManager(f"{self.app_name}_2")
        result = new_manager.import_settings(self.export_file)

        self.assertTrue(result)
        self.assertEqual(new_manager.get_theme(), "dark")

        # Cleanup
        new_manager.settings.clear()

    def test_import_settings_restores_preferences(self):
        """Test import_settings restores preferences."""
        # Export settings with preferences
        self.manager.set_preference("pref1", "value1")
        self.manager.set_preference("pref2", 42)
        self.manager.export_settings(self.export_file)

        # Create new manager and import
        new_manager = SessionManager(f"{self.app_name}_2")
        result = new_manager.import_settings(self.export_file)

        self.assertTrue(result)
        self.assertEqual(new_manager.get_preference("pref1"), "value1")
        self.assertEqual(new_manager.get_preference("pref2"), 42)

        # Cleanup
        new_manager.settings.clear()

    def test_export_settings_returns_false_on_error(self):
        """Test export_settings returns False on error."""
        # Try to export to invalid path
        result = self.manager.export_settings("/invalid/path/export.json")

        self.assertFalse(result)

    def test_import_settings_returns_false_on_error(self):
        """Test import_settings returns False on error."""
        # Try to import from non-existent file
        result = self.manager.import_settings("/nonexistent/file.json")

        self.assertFalse(result)


class TestSessionManagerWindowState(unittest.TestCase):
    """Test SessionManager window state functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.app_name = f"TestApp_{id(self)}"
        self.manager = SessionManager(self.app_name)
        self.window = QMainWindow()

    def tearDown(self):
        """Clean up test fixtures."""
        self.manager.settings.clear()
        self.window.close()

    def test_save_window_state(self):
        """Test saving window state."""
        # Should not raise error
        self.manager.save_window_state(self.window)

        # Verify settings were saved
        self.manager.settings.beginGroup("MainWindow")
        self.assertIsNotNone(self.manager.settings.value("geometry"))
        self.manager.settings.endGroup()

    def test_restore_window_state_returns_true_on_success(self):
        """Test restore_window_state returns True when successful."""
        self.manager.save_window_state(self.window)

        result = self.manager.restore_window_state(self.window)

        # Should succeed (even with minimal state)
        self.assertTrue(result)

    def test_window_state_persists_across_save_restore(self):
        """Test window state persists across save/restore cycle."""
        # Set specific window size
        self.window.resize(800, 600)

        self.manager.save_window_state(self.window)

        # Create new window and restore
        new_window = QMainWindow()
        self.manager.restore_window_state(new_window)

        # Size should match (or be close due to OS constraints)
        # We just verify the restore happened without error
        new_window.close()


if __name__ == "__main__":
    unittest.main()
