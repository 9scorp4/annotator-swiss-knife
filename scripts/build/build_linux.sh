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

# Build the debug executable first
echo "Building Linux debug executable..."
# Use the spec file in the same directory as the script
cd "$SCRIPT_DIR"
# Calculate the path to the project root's dist directory
DIST_DIR="$SCRIPT_DIR/../../dist"
pyinstaller "linux_build_debug.spec" --distpath "$DIST_DIR" --clean --noconfirm

# Set executable permission for debug build
if [ -f "$SCRIPT_DIR/../../dist/AnnotationToolkit-Debug/AnnotationToolkit-Debug" ]; then
    chmod +x "$SCRIPT_DIR/../../dist/AnnotationToolkit-Debug/AnnotationToolkit-Debug"
fi

# Build the AppImage (release version)
echo ""
echo "Building Linux AppImage (Release)..."
bash "$SCRIPT_DIR/build_appimage.sh"

echo ""
echo "=== Build Complete ==="
echo ""
echo "The Linux builds have been completed successfully!"
echo ""
echo "AppImage (release):  dist/AnnotationToolkit-*.AppImage"
echo "Debug build:         dist/AnnotationToolkit-Debug/"
echo ""
echo "To run the AppImage:"
echo "  chmod +x dist/AnnotationToolkit-*.AppImage"
echo "  ./dist/AnnotationToolkit-*.AppImage"
echo ""
echo "To run the debug build:"
echo "  cd dist/AnnotationToolkit-Debug"
echo "  ./AnnotationToolkit-Debug"
echo ""
