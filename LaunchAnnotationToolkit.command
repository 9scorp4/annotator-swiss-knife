#!/bin/bash

# Script to launch the Annotation Toolkit application
# This is a workaround for macOS security settings that prevent
# the application from being launched by double-clicking

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Define the path to the application
APP_PATH="$SCRIPT_DIR/dist/AnnotationToolkit.app/Contents/MacOS/AnnotationToolkit"

# Check if the application exists
if [ -f "$APP_PATH" ]; then
    echo "Launching Annotation Toolkit application..."
    # Launch the application
    "$APP_PATH"
else
    echo "Error: Application not found at $APP_PATH"
    echo "Trying to run from development environment..."

    # Try to run using the run.sh script
    if [ -f "$SCRIPT_DIR/scripts/run/run.sh" ]; then
        echo "Running using run.sh script..."
        "$SCRIPT_DIR/scripts/run/run.sh" gui
    else
        echo "Error: Could not find run.sh script."
        echo "Please make sure the application is built or the development environment is set up."
    fi
fi

# Display any error messages and wait for user input before closing
echo "Press Enter to close this window"; read
