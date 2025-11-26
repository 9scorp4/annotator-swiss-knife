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

# Install the package in editable mode
echo "Installing annotation_toolkit package..."
PROJECT_ROOT="$SCRIPT_DIR/../.."
pip install -e "$PROJECT_ROOT"

# Install PyInstaller if not already installed
if ! pip show pyinstaller &> /dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Build the release executable
echo "Building macOS executable..."
# Use the spec file in the same directory as the script
cd "$SCRIPT_DIR"
# Calculate the path to the project root's dist directory
DIST_DIR="$SCRIPT_DIR/../../dist"
pyinstaller "mac_build.spec" --distpath "$DIST_DIR" --clean --noconfirm

# Get version from package
cd "$SCRIPT_DIR/../.."
VERSION=$(python3 -c "from annotation_toolkit import __version__; print(__version__)" 2>/dev/null || echo "0.0.0.dev0")
echo "Version: $VERSION"

# Create zip archive for distribution
echo ""
echo "Creating archive..."
cd "$SCRIPT_DIR/../../dist"
if [ -d "AnnotationToolkit.app" ]; then
    zip -r -q "AnnotationToolkit-${VERSION}-macOS.zip" "AnnotationToolkit.app"
    echo "Created: AnnotationToolkit-${VERSION}-macOS.zip"
fi

echo ""
echo "=== Build Complete ==="
echo ""
echo "The macOS application has been built successfully!"
echo ""
echo "Build location: dist/AnnotationToolkit-${VERSION}-macOS.zip"
echo ""
echo "To run the application, extract the zip and double-click the .app file."
echo ""
echo "Note: If you get a security warning when trying to open the app,"
echo "go to System Preferences > Security & Privacy and click 'Open Anyway'."
echo ""
