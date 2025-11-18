"""
Pytest configuration for GUI tests.

Provides fixtures for PyQt5 testing in headless environments.
"""

import os
import sys
import pytest


# Set Qt to use offscreen platform for headless testing
# This must be set before importing PyQt5
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt5.QtWidgets import QApplication


@pytest.fixture(scope="session", autouse=True)
def qapp():
    """
    Create a QApplication instance for the entire test session.

    This fixture ensures QApplication is created once and reused across all tests.
    Required for any test that uses PyQt5 components.

    The fixture is autouse=True, so it runs automatically before any tests.
    """
    # Create QApplication instance if it doesn't exist
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    yield app

    # Cleanup happens automatically when app goes out of scope

