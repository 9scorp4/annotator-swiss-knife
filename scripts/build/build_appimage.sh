#!/bin/bash
# Build script for creating Linux AppImage
# This script packages the PyInstaller bundle into an AppImage

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/dist"
APPDIR="$BUILD_DIR/AppDir"

echo "========================================="
echo "Annotation Toolkit - AppImage Build"
echo "========================================="

# Get version from package
cd "$PROJECT_ROOT"
VERSION=$(python3 -c "from annotation_toolkit import __version__; print(__version__)" 2>/dev/null || echo "0.0.0.dev0")
echo "Building version: $VERSION"

# Step 1: Run PyInstaller with the Linux spec
echo ""
echo "Step 1: Running PyInstaller..."
cd "$SCRIPT_DIR"
pyinstaller linux_build.spec --distpath "$BUILD_DIR" --clean --noconfirm

# Check if build succeeded
if [ ! -d "$BUILD_DIR/AnnotationToolkit" ]; then
    echo "Error: PyInstaller build failed - directory not found"
    exit 1
fi

# Step 2: Create AppDir structure
echo ""
echo "Step 2: Creating AppDir structure..."
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"

# Copy PyInstaller bundle to AppDir
echo "Copying application files..."
cp -r "$BUILD_DIR/AnnotationToolkit"/* "$APPDIR/usr/bin/"

# Make the main executable file executable
chmod +x "$APPDIR/usr/bin/AnnotationToolkit"

# Step 3: Create .desktop file
echo ""
echo "Step 3: Creating .desktop file..."
cat > "$APPDIR/annotation-toolkit.desktop" << 'EOF'
[Desktop Entry]
Type=Application
Name=Annotation Toolkit
Comment=Comprehensive data annotation toolkit
Exec=AnnotationToolkit
Icon=annotation-toolkit
Categories=Utility;Development;
Terminal=false
EOF

# Copy .desktop file to usr/share/applications
cp "$APPDIR/annotation-toolkit.desktop" "$APPDIR/usr/share/applications/"

# Step 4: Create a simple icon (if one doesn't exist)
echo ""
echo "Step 4: Creating application icon..."
# For now, we'll create a simple text-based icon placeholder
# In a real deployment, you'd want to include an actual PNG icon
# Create a simple SVG icon and convert to PNG if imagemagick is available
if command -v convert &> /dev/null; then
    # Create a simple colored square as placeholder
    convert -size 256x256 xc:#4A90E2 \
        -gravity center \
        -pointsize 72 \
        -fill white \
        -annotate +0+0 "AT" \
        "$APPDIR/usr/share/icons/hicolor/256x256/apps/annotation-toolkit.png" 2>/dev/null || true
fi

# If ImageMagick failed or isn't available, just link the icon to a text file
if [ ! -f "$APPDIR/usr/share/icons/hicolor/256x256/apps/annotation-toolkit.png" ]; then
    echo "Warning: Could not create icon (ImageMagick not available)"
    # Create a minimal PNG file as fallback
    touch "$APPDIR/usr/share/icons/hicolor/256x256/apps/annotation-toolkit.png"
fi

# Link icon to AppDir root
ln -sf usr/share/icons/hicolor/256x256/apps/annotation-toolkit.png "$APPDIR/annotation-toolkit.png"

# Step 5: Create AppRun script
echo ""
echo "Step 5: Creating AppRun script..."
cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
# AppRun script for Annotation Toolkit AppImage

SELF=$(readlink -f "$0")
HERE=${SELF%/*}

# Export Qt plugin path so Qt can find platform plugins
export QT_PLUGIN_PATH="$HERE/usr/bin/PyQt5/Qt/plugins:${QT_PLUGIN_PATH}"
export QT_QPA_PLATFORM_PLUGIN_PATH="$HERE/usr/bin/PyQt5/Qt/plugins/platforms"

# Export library path
export LD_LIBRARY_PATH="$HERE/usr/bin:${LD_LIBRARY_PATH}"

# Change to the directory where the executable is
cd "$HERE/usr/bin"

# Execute the application
exec "./AnnotationToolkit" "$@"
EOF

chmod +x "$APPDIR/AppRun"

# Step 6: Download appimagetool if not present
echo ""
echo "Step 6: Downloading appimagetool..."
APPIMAGETOOL="$BUILD_DIR/appimagetool-x86_64.AppImage"
if [ ! -f "$APPIMAGETOOL" ]; then
    echo "Downloading appimagetool..."
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" \
        -O "$APPIMAGETOOL"
    chmod +x "$APPIMAGETOOL"
else
    echo "Using existing appimagetool"
fi

# Step 7: Build the AppImage
echo ""
echo "Step 7: Building AppImage..."
cd "$BUILD_DIR"

# Set ARCH environment variable
export ARCH=x86_64

# Build AppImage
OUTPUT_APPIMAGE="$BUILD_DIR/AnnotationToolkit-${VERSION}-${ARCH}.AppImage"
rm -f "$OUTPUT_APPIMAGE"

"$APPIMAGETOOL" "$APPDIR" "$OUTPUT_APPIMAGE"

# Make it executable
chmod +x "$OUTPUT_APPIMAGE"

echo ""
echo "========================================="
echo "Build complete!"
echo "AppImage created: $OUTPUT_APPIMAGE"
echo "========================================="
echo ""
echo "To test the AppImage:"
echo "  $OUTPUT_APPIMAGE"
echo ""
