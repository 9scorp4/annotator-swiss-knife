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

# Build the release executable
echo "Building macOS executable (Release)..."
# Use the spec file in the same directory as the script
cd "$SCRIPT_DIR"
# Calculate the path to the project root's dist directory
DIST_DIR="$SCRIPT_DIR/../../dist"
pyinstaller "mac_build.spec" --distpath "$DIST_DIR" --clean --noconfirm

# Build the debug executable
echo ""
echo "Building macOS executable (Debug)..."
pyinstaller "mac_build_debug.spec" --distpath "$DIST_DIR" --clean --noconfirm

# Get version from package
cd "$SCRIPT_DIR/../.."
VERSION=$(python3 -c "from annotation_toolkit import __version__; print(__version__)" 2>/dev/null || echo "0.0.0.dev0")
echo "Version: $VERSION"

# Create zip archives for distribution
echo ""
echo "Creating release archive..."
cd "$SCRIPT_DIR/../../dist"
if [ -d "AnnotationToolkit.app" ]; then
    zip -r -q "AnnotationToolkit-${VERSION}-macOS-release.zip" "AnnotationToolkit.app"
    echo "Created: AnnotationToolkit-${VERSION}-macOS-release.zip"
fi

echo "Creating debug archive..."
if [ -d "AnnotationToolkit-Debug.app" ]; then
    zip -r -q "AnnotationToolkit-${VERSION}-macOS-debug.zip" "AnnotationToolkit-Debug.app"
    echo "Created: AnnotationToolkit-${VERSION}-macOS-debug.zip"
fi

echo ""
echo "=== Build Complete ==="
echo ""
echo "The macOS applications have been built successfully!"
echo ""
echo "Release build: dist/AnnotationToolkit-${VERSION}-macOS-release.zip"
echo "Debug build:   dist/AnnotationToolkit-${VERSION}-macOS-debug.zip"
echo ""
echo "To run the application, extract the zip and double-click the .app file."
echo ""
echo "Note: If you get a security warning when trying to open the app,"
echo "go to System Preferences > Security & Privacy and click 'Open Anyway'."
echo ""
