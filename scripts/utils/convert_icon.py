#!/usr/bin/env python3
"""
Icon Conversion Utility

Converts icon.svg to platform-specific icon formats:
- macOS: .icns (multi-resolution: 16, 32, 64, 128, 256, 512, 1024)
- Windows: .ico (16, 32, 48, 256)
- Linux: PNG files (16, 32, 48, 64, 128, 256, 512)

Usage:
    python scripts/utils/convert_icon.py

Requirements:
    - PyQt5 (for SVG to PNG conversion)
    - Pillow (for ICO creation)
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

try:
    from PyQt5.QtCore import Qt, QSize
    from PyQt5.QtGui import QPixmap, QPainter
    from PyQt5.QtSvg import QSvgRenderer
    from PyQt5.QtWidgets import QApplication
except ImportError:
    print("Error: PyQt5 not found. Install with: pip install PyQt5")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow not found. Install with: pip install Pillow")
    sys.exit(1)


# Icon sizes for each platform
MACOS_SIZES = [16, 32, 64, 128, 256, 512, 1024]
WINDOWS_SIZES = [16, 32, 48, 256]
LINUX_SIZES = [16, 32, 48, 64, 128, 256, 512]


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


def svg_to_png(svg_path: Path, png_path: Path, size: int, app: QApplication) -> None:
    """
    Convert SVG to PNG at specified size using PyQt5.

    Args:
        svg_path: Path to source SVG file
        png_path: Path to output PNG file
        size: Size in pixels (square)
        app: QApplication instance
    """
    print(f"  Converting to {size}x{size} PNG: {png_path.name}")

    # Load SVG and render to pixmap
    renderer = QSvgRenderer(str(svg_path))
    pixmap = QPixmap(QSize(size, size))
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    # Save as PNG
    pixmap.save(str(png_path), "PNG")


def create_icns(png_files: List[Tuple[Path, int]], output_path: Path) -> None:
    """
    Create macOS .icns file from PNG files.

    Args:
        png_files: List of (path, size) tuples for PNG files
        output_path: Path to output .icns file
    """
    print(f"\nCreating macOS icon: {output_path.name}")

    # Create iconset directory
    iconset_dir = output_path.parent / f"{output_path.stem}.iconset"
    iconset_dir.mkdir(exist_ok=True)

    # Copy PNGs to iconset with proper naming
    iconset_mapping = {
        16: ["icon_16x16.png"],
        32: ["icon_16x16@2x.png", "icon_32x32.png"],
        64: ["icon_32x32@2x.png"],
        128: ["icon_128x128.png"],
        256: ["icon_128x128@2x.png", "icon_256x256.png"],
        512: ["icon_256x256@2x.png", "icon_512x512.png"],
        1024: ["icon_512x512@2x.png"]
    }

    for png_path, size in png_files:
        if size in iconset_mapping:
            img = Image.open(png_path)
            for name in iconset_mapping[size]:
                output_file = iconset_dir / name
                img.save(output_file, "PNG")
                print(f"  Added: {name}")

    # Convert iconset to icns using iconutil (macOS only)
    if sys.platform == "darwin":
        import subprocess
        try:
            subprocess.run(
                ["iconutil", "-c", "icns", str(iconset_dir), "-o", str(output_path)],
                check=True,
                capture_output=True
            )
            print(f"✓ Created: {output_path}")

            # Clean up iconset directory
            import shutil
            shutil.rmtree(iconset_dir)
        except subprocess.CalledProcessError as e:
            print(f"Error creating .icns: {e}")
            print(f"Iconset directory preserved at: {iconset_dir}")
    else:
        print(f"Warning: iconutil not available on {sys.platform}")
        print(f"Iconset directory created at: {iconset_dir}")
        print(f"Run 'iconutil -c icns {iconset_dir}' on macOS to create .icns")


def create_ico(png_files: List[Tuple[Path, int]], output_path: Path) -> None:
    """
    Create Windows .ico file from PNG files.

    Args:
        png_files: List of (path, size) tuples for PNG files
        output_path: Path to output .ico file
    """
    print(f"\nCreating Windows icon: {output_path.name}")

    images = []
    for png_path, size in png_files:
        img = Image.open(png_path)
        images.append(img)
        print(f"  Added: {size}x{size}")

    # Save as ICO with all sizes
    images[0].save(
        output_path,
        format="ICO",
        sizes=[(img.width, img.height) for img in images]
    )
    print(f"✓ Created: {output_path}")


def main():
    """Main conversion process."""
    # Create QApplication (required for Qt operations)
    app = QApplication(sys.argv)

    project_root = get_project_root()
    assets_dir = project_root / "annotation_toolkit" / "ui" / "gui" / "assets"

    svg_path = assets_dir / "icon.svg"
    if not svg_path.exists():
        print(f"Error: Icon source not found at {svg_path}")
        sys.exit(1)

    print(f"Converting icon from: {svg_path}")
    print(f"Output directory: {assets_dir}\n")

    # Create temporary directory for PNG files
    temp_dir = assets_dir / "temp_png"
    temp_dir.mkdir(exist_ok=True)

    # Generate PNG files for all platforms
    all_sizes = sorted(set(MACOS_SIZES + WINDOWS_SIZES + LINUX_SIZES))
    png_files = []

    print("Generating PNG files...")
    for size in all_sizes:
        png_path = temp_dir / f"icon_{size}.png"
        svg_to_png(svg_path, png_path, size, app)
        png_files.append((png_path, size))

    # Create macOS .icns
    macos_png_files = [(p, s) for p, s in png_files if s in MACOS_SIZES]
    create_icns(macos_png_files, assets_dir / "icon.icns")

    # Create Windows .ico
    windows_png_files = [(p, s) for p, s in png_files if s in WINDOWS_SIZES]
    create_ico(windows_png_files, assets_dir / "icon.ico")

    # Copy Linux PNG files
    print("\nCreating Linux PNG icons...")
    for png_path, size in png_files:
        if size in LINUX_SIZES:
            linux_png_path = assets_dir / f"icon_{size}.png"
            import shutil
            shutil.copy(png_path, linux_png_path)
            print(f"  Created: icon_{size}.png")

    # Clean up temporary directory
    import shutil
    shutil.rmtree(temp_dir)

    print("\n" + "="*60)
    print("Icon conversion complete!")
    print("="*60)
    print(f"\nGenerated files in {assets_dir}:")
    print(f"  - icon.icns (macOS)")
    print(f"  - icon.ico (Windows)")
    print(f"  - icon_{{16,32,48,64,128,256,512}}.png (Linux)")
    print("\nThese files are now ready for use in PyInstaller builds.")


if __name__ == "__main__":
    main()
