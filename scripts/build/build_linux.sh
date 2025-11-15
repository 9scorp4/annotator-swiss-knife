#!/bin/bash

# Build script for Linux executable

# Set error handling
set -e

echo "=== Annotation Toolkit Linux Build Script ==="
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
echo "Building Linux executable..."
# Use the spec file in the same directory as the script
pyinstaller "$SCRIPT_DIR/linux_build.spec"

echo ""
echo "=== Build Complete ==="
echo ""
echo "The Linux executable has been built successfully!"
echo "You can find the executable at: dist/AnnotationToolkit"
echo ""
echo "To run the application:"
echo "  chmod +x dist/AnnotationToolkit"
echo "  ./dist/AnnotationToolkit"
echo ""
