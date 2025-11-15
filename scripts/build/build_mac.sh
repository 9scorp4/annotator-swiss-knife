#!/bin/bash

# Build script for macOS executable

# Set error handling
set -e

echo "=== Annotation Toolkit macOS Build Script ==="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Create or activate virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Calculate the path to requirements.txt relative to the script location
REQUIREMENTS_PATH="$SCRIPT_DIR/../../requirements.txt"
pip install -r "$REQUIREMENTS_PATH"

# Install PyInstaller if not already installed
if ! pip show pyinstaller &> /dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Build the executable
echo "Building macOS executable..."
# Use the spec file in the same directory as the script
pyinstaller "$SCRIPT_DIR/mac_build.spec"

echo ""
echo "=== Build Complete ==="
echo ""
echo "The macOS application has been built successfully!"
echo "You can find the application at: dist/AnnotationToolkit.app"
echo ""
echo "To run the application, double-click on the AnnotationToolkit.app file."
echo ""
echo "Note: If you get a security warning when trying to open the app,"
echo "go to System Preferences > Security & Privacy and click 'Open Anyway'."
echo ""
