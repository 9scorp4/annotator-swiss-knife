"""
Auto-save system with crash recovery.

Provides automatic saving of widget state with crash recovery capabilities.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime

from PyQt5.QtCore import QTimer, QObject, pyqtSignal

from ....utils import logger


class AutoSaveManager(QObject):
    """
    Manages automatic saving of application state with crash recovery.

    Features:
    - Periodic auto-save at configurable intervals
    - Crash recovery from last auto-save
    - Multiple save slots for different widgets
    - Timestamp tracking
    - Backup rotation
    """

    # Signal emitted when auto-save completes
    save_completed = pyqtSignal(str)  # save_key

    # Signal emitted when auto-save fails
    save_failed = pyqtSignal(str, str)  # save_key, error_message

    def __init__(
        self,
        save_dir: Optional[Path] = None,
        interval_seconds: int = 60,
        max_backups: int = 5
    ):
        """
        Initialize the auto-save manager.

        Args:
            save_dir: Directory for auto-save files (default: ~/annotation_toolkit_data/autosave)
            interval_seconds: Auto-save interval in seconds (default: 60)
            max_backups: Maximum number of backup files to keep (default: 5)
        """
        super().__init__()

        self.save_dir = save_dir or (Path.home() / "annotation_toolkit_data" / "autosave")
        self.save_dir.mkdir(parents=True, exist_ok=True)

        self.interval_seconds = interval_seconds
        self.max_backups = max_backups

        # Store save callbacks for each key
        self._save_callbacks: Dict[str, Callable[[], Dict[str, Any]]] = {}

        # Timer for periodic saves
        self._timer = QTimer()
        self._timer.timeout.connect(self._perform_auto_save)

        # Track when each key was last saved
        self._last_save_times: Dict[str, float] = {}

        logger.info(f"AutoSaveManager initialized: dir={self.save_dir}, interval={interval_seconds}s")

    def register(self, save_key: str, save_callback: Callable[[], Dict[str, Any]]) -> None:
        """
        Register a widget/component for auto-save.

        Args:
            save_key: Unique identifier for this save slot
            save_callback: Function that returns state dict to save
        """
        self._save_callbacks[save_key] = save_callback
        logger.info(f"Registered auto-save for: {save_key}")

    def unregister(self, save_key: str) -> None:
        """
        Unregister a widget/component from auto-save.

        Args:
            save_key: Key to unregister
        """
        if save_key in self._save_callbacks:
            del self._save_callbacks[save_key]
            logger.info(f"Unregistered auto-save for: {save_key}")

    def start(self) -> None:
        """Start the auto-save timer."""
        if not self._timer.isActive():
            self._timer.start(self.interval_seconds * 1000)
            logger.info(f"Auto-save started (interval: {self.interval_seconds}s)")

    def stop(self) -> None:
        """Stop the auto-save timer."""
        if self._timer.isActive():
            self._timer.stop()
            logger.info("Auto-save stopped")

    def save_now(self, save_key: Optional[str] = None) -> None:
        """
        Trigger an immediate save.

        Args:
            save_key: Specific key to save (if None, saves all)
        """
        if save_key:
            self._save_state(save_key)
        else:
            self._perform_auto_save()

    def _perform_auto_save(self) -> None:
        """Perform auto-save for all registered callbacks."""
        for save_key in list(self._save_callbacks.keys()):
            self._save_state(save_key)

    def _save_state(self, save_key: str) -> bool:
        """
        Save state for a specific key.

        Args:
            save_key: Key to save

        Returns:
            True if save was successful
        """
        if save_key not in self._save_callbacks:
            return False

        try:
            # Get state from callback
            callback = self._save_callbacks[save_key]
            state = callback()

            # Add metadata
            save_data = {
                "save_key": save_key,
                "timestamp": datetime.now().isoformat(),
                "version": "1.0",
                "state": state
            }

            # Save to file
            save_path = self._get_save_path(save_key)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)

            # Rotate backups
            self._rotate_backups(save_key)

            # Update last save time
            self._last_save_times[save_key] = time.time()

            logger.debug(f"Auto-saved: {save_key}")
            self.save_completed.emit(save_key)
            return True

        except Exception as e:
            error_msg = f"Auto-save failed for {save_key}: {str(e)}"
            logger.error(error_msg)
            self.save_failed.emit(save_key, str(e))
            return False

    def _rotate_backups(self, save_key: str) -> None:
        """
        Rotate backup files, keeping only max_backups.

        Args:
            save_key: Key for which to rotate backups
        """
        save_path = self._get_save_path(save_key)

        # Create backup
        if save_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = save_path.parent / f"{save_key}_backup_{timestamp}.json"
            save_path.rename(backup_path)

        # Remove old backups
        backup_pattern = f"{save_key}_backup_*.json"
        backup_files = sorted(self.save_dir.glob(backup_pattern), reverse=True)

        for old_backup in backup_files[self.max_backups:]:
            try:
                old_backup.unlink()
                logger.debug(f"Removed old backup: {old_backup.name}")
            except Exception as e:
                logger.warning(f"Failed to remove old backup {old_backup}: {e}")

    def load_state(self, save_key: str) -> Optional[Dict[str, Any]]:
        """
        Load saved state for a key.

        Args:
            save_key: Key to load

        Returns:
            Saved state dict, or None if not found/invalid
        """
        save_path = self._get_save_path(save_key)

        if not save_path.exists():
            logger.debug(f"No auto-save file found for: {save_key}")
            return None

        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)

            # Validate structure
            if "state" not in save_data:
                logger.warning(f"Invalid auto-save file for {save_key}: missing 'state' field")
                return None

            timestamp = save_data.get("timestamp", "unknown")
            logger.info(f"Loaded auto-save for {save_key} from {timestamp}")

            return save_data["state"]

        except Exception as e:
            logger.error(f"Failed to load auto-save for {save_key}: {e}")
            return None

    def has_recovery_data(self, save_key: str) -> bool:
        """
        Check if recovery data exists for a key.

        Args:
            save_key: Key to check

        Returns:
            True if recovery data exists
        """
        return self._get_save_path(save_key).exists()

    def get_recovery_timestamp(self, save_key: str) -> Optional[str]:
        """
        Get the timestamp of the last auto-save for a key.

        Args:
            save_key: Key to check

        Returns:
            ISO format timestamp string, or None if no save exists
        """
        save_path = self._get_save_path(save_key)

        if not save_path.exists():
            return None

        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            return save_data.get("timestamp")
        except Exception:
            return None

    def clear_recovery_data(self, save_key: str) -> None:
        """
        Clear recovery data for a key.

        Args:
            save_key: Key to clear
        """
        save_path = self._get_save_path(save_key)

        if save_path.exists():
            try:
                save_path.unlink()
                logger.info(f"Cleared recovery data for: {save_key}")
            except Exception as e:
                logger.error(f"Failed to clear recovery data for {save_key}: {e}")

    def _get_save_path(self, save_key: str) -> Path:
        """
        Get the save file path for a key.

        Args:
            save_key: Save key

        Returns:
            Path to save file
        """
        # Sanitize key for filesystem
        safe_key = "".join(c if c.isalnum() or c in "_-" else "_" for c in save_key)
        return self.save_dir / f"{safe_key}_autosave.json"

    def get_all_recovery_keys(self) -> List[str]:
        """
        Get all keys that have recovery data available.

        Returns:
            List of save keys with recovery data
        """
        recovery_files = self.save_dir.glob("*_autosave.json")
        keys = []

        for file_path in recovery_files:
            # Extract key from filename
            key = file_path.stem.replace("_autosave", "")
            keys.append(key)

        return keys
