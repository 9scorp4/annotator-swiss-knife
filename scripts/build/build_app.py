#!/usr/bin/env python
"""
PyInstaller entry point for building the Annotation Toolkit executable.
This script launches the GUI application when the executable is run.
"""

import sys

def main():
    """Main entry point for the PyInstaller executable."""
    from annotation_toolkit.ui.gui.app import run_application

    # Launch the GUI application
    run_application()

if __name__ == '__main__':
    main()