#!/usr/bin/env python
"""
PyInstaller entry point for building the Annotation Toolkit executable.
This script launches the GUI application when the executable is run.
"""

import sys
import os

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, project_root)

def main():
    """Main entry point for the PyInstaller executable."""
    from annotation_toolkit.ui.gui.app import run_application

    # Launch the GUI application
    run_application()

if __name__ == '__main__':
    main()