"""
Session persistence for saving window state and user preferences.

Manages application session data including window geometry, recent files, and UI state.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from PyQt5.QtCore import QSettings, QByteArray, QSize, QPoint
from PyQt5.QtWidgets import QMainWindow

from ....utils import logger


class SessionManager:
    """
    Manages application session persistence.

    Features:
    - Window geometry and state
    - Recent files list
    - Last used tool
    - UI preferences
    - Theme selection
    """

    MAX_RECENT_FILES = 10

    def __init__(self, app_name: str = "AnnotationToolkit"):
        """
        Initialize the session manager.

        Args:
            app_name: Application name for settings storage
        """
        self.settings = QSettings("Anthropic", app_name)
        logger.info(f"SessionManager initialized for {app_name}")

    # ===== WINDOW STATE =====

    def save_window_state(self, window: QMainWindow) -> None:
        """
        Save window geometry and state.

        Args:
            window: Main window to save state from
        """
        self.settings.beginGroup("MainWindow")

        # Save geometry
        self.settings.setValue("geometry", window.saveGeometry())
        self.settings.setValue("windowState", window.saveState())

        # Save size and position as fallback
        self.settings.setValue("size", window.size())
        self.settings.setValue("pos", window.pos())
        self.settings.setValue("maximized", window.isMaximized())

        self.settings.endGroup()
        logger.debug("Window state saved")

    def restore_window_state(self, window: QMainWindow) -> bool:
        """
        Restore window geometry and state.

        Args:
            window: Main window to restore state to

        Returns:
            True if state was restored successfully
        """
        self.settings.beginGroup("MainWindow")

        try:
            # Try to restore full geometry
            geometry = self.settings.value("geometry")
            if geometry:
                window.restoreGeometry(geometry)

            # Try to restore window state
            state = self.settings.value("windowState")
            if state:
                window.restoreState(state)

            # Fallback: restore size and position
            if not geometry:
                size = self.settings.value("size")
                pos = self.settings.value("pos")

                if size:
                    window.resize(size)
                if pos:
                    window.move(pos)

            # Restore maximized state
            if self.settings.value("maximized", False, type=bool):
                window.showMaximized()

            self.settings.endGroup()
            logger.debug("Window state restored")
            return True

        except Exception as e:
            logger.error(f"Failed to restore window state: {e}")
            self.settings.endGroup()
            return False

    # ===== RECENT FILES =====

    def add_recent_file(self, file_path: str) -> None:
        """
        Add a file to the recent files list.

        Args:
            file_path: Path to the file
        """
        recent = self.get_recent_files()

        # Remove if already in list
        if file_path in recent:
            recent.remove(file_path)

        # Add to front
        recent.insert(0, file_path)

        # Limit to MAX_RECENT_FILES
        recent = recent[:self.MAX_RECENT_FILES]

        # Save
        self.settings.setValue("RecentFiles/files", recent)
        logger.debug(f"Added to recent files: {file_path}")

    def get_recent_files(self) -> List[str]:
        """
        Get the list of recent files.

        Returns:
            List of recent file paths (most recent first)
        """
        recent = self.settings.value("RecentFiles/files", [], type=list)

        # Filter out non-existent files
        valid_files = [f for f in recent if Path(f).exists()]

        # Update if list changed
        if len(valid_files) != len(recent):
            self.settings.setValue("RecentFiles/files", valid_files)

        return valid_files

    def clear_recent_files(self) -> None:
        """Clear the recent files list."""
        self.settings.setValue("RecentFiles/files", [])
        logger.info("Recent files cleared")

    # ===== LAST USED TOOL =====

    def set_last_tool(self, tool_name: str) -> None:
        """
        Set the last used tool.

        Args:
            tool_name: Name of the tool
        """
        self.settings.setValue("Session/lastTool", tool_name)
        self.settings.setValue("Session/lastToolTime", datetime.now().isoformat())

    def get_last_tool(self) -> Optional[str]:
        """
        Get the last used tool.

        Returns:
            Tool name, or None if not set
        """
        return self.settings.value("Session/lastTool", None, type=str)

    # ===== UI PREFERENCES =====

    def set_preference(self, key: str, value: Any) -> None:
        """
        Set a UI preference.

        Args:
            key: Preference key
            value: Preference value
        """
        self.settings.setValue(f"Preferences/{key}", value)

    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a UI preference.

        Args:
            key: Preference key
            default: Default value if not set

        Returns:
            Preference value
        """
        return self.settings.value(f"Preferences/{key}", default)

    # ===== THEME =====

    def set_theme(self, theme_name: str) -> None:
        """
        Set the selected theme.

        Args:
            theme_name: Theme name ("light" or "dark")
        """
        self.settings.setValue("Appearance/theme", theme_name)
        logger.info(f"Theme set to: {theme_name}")

    def get_theme(self) -> str:
        """
        Get the selected theme.

        Returns:
            Theme name ("light" or "dark"), defaults to "light"
        """
        return self.settings.value("Appearance/theme", "light", type=str)

    # ===== SPLITTER STATES =====

    def save_splitter_state(self, name: str, state: QByteArray) -> None:
        """
        Save splitter state.

        Args:
            name: Splitter identifier
            state: Splitter state to save
        """
        self.settings.setValue(f"Splitters/{name}", state)

    def get_splitter_state(self, name: str) -> Optional[QByteArray]:
        """
        Get saved splitter state.

        Args:
            name: Splitter identifier

        Returns:
            Splitter state, or None if not saved
        """
        return self.settings.value(f"Splitters/{name}", None)

    # ===== TOOL-SPECIFIC STATE =====

    def save_tool_state(self, tool_name: str, state: Dict[str, Any]) -> None:
        """
        Save tool-specific state.

        Args:
            tool_name: Name of the tool
            state: State dictionary to save
        """
        self.settings.beginGroup(f"ToolState/{tool_name}")

        for key, value in state.items():
            self.settings.setValue(key, value)

        self.settings.endGroup()
        logger.debug(f"Saved state for tool: {tool_name}")

    def load_tool_state(self, tool_name: str) -> Dict[str, Any]:
        """
        Load tool-specific state.

        Args:
            tool_name: Name of the tool

        Returns:
            State dictionary (empty if no state saved)
        """
        self.settings.beginGroup(f"ToolState/{tool_name}")

        state = {}
        for key in self.settings.allKeys():
            state[key] = self.settings.value(key)

        self.settings.endGroup()
        return state

    # ===== SESSION INFO =====

    def get_session_info(self) -> Dict[str, Any]:
        """
        Get information about the current session.

        Returns:
            Dictionary with session information
        """
        return {
            "recent_files_count": len(self.get_recent_files()),
            "last_tool": self.get_last_tool(),
            "theme": self.get_theme(),
            "has_window_state": self.settings.contains("MainWindow/geometry")
        }

    def clear_session(self) -> None:
        """Clear all session data (except preferences)."""
        # Clear window state
        self.settings.remove("MainWindow")

        # Clear recent files
        self.clear_recent_files()

        # Clear session info
        self.settings.remove("Session")

        # Clear tool states
        self.settings.remove("ToolState")

        logger.info("Session cleared")

    def export_settings(self, file_path: str) -> bool:
        """
        Export settings to a file.

        Args:
            file_path: Path to export file

        Returns:
            True if successful
        """
        try:
            import json

            export_data = {
                "preferences": {},
                "recent_files": self.get_recent_files(),
                "theme": self.get_theme(),
                "exported_at": datetime.now().isoformat()
            }

            # Export preferences
            self.settings.beginGroup("Preferences")
            for key in self.settings.allKeys():
                export_data["preferences"][key] = self.settings.value(key)
            self.settings.endGroup()

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)

            logger.info(f"Settings exported to: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export settings: {e}")
            return False

    def import_settings(self, file_path: str) -> bool:
        """
        Import settings from a file.

        Args:
            file_path: Path to import file

        Returns:
            True if successful
        """
        try:
            import json

            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)

            # Import preferences
            if "preferences" in import_data:
                for key, value in import_data["preferences"].items():
                    self.set_preference(key, value)

            # Import theme
            if "theme" in import_data:
                self.set_theme(import_data["theme"])

            logger.info(f"Settings imported from: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to import settings: {e}")
            return False
