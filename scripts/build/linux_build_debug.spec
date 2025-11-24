# -*- mode: python ; coding: utf-8 -*-
# DEBUG BUILD - This spec file creates a debug build with console output enabled
import os
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_all

# Get the absolute path to the project root directory
# When running as a spec file, we need to use a different approach
# since __file__ is not defined
current_dir = os.getcwd()
# Assuming the build script is run from the project root or scripts/build directory
if current_dir.endswith('scripts/build'):
    project_root = os.path.abspath(os.path.join(current_dir, '../..'))
else:
    project_root = current_dir

# Add project root to sys.path to import annotation_toolkit
sys.path.insert(0, project_root)

# Get version from package
try:
    from annotation_toolkit import __version__
    version = __version__
except ImportError:
    version = "0.0.0.dev0"

# Collect all annotation_toolkit package data, submodules, and binaries
toolkit_datas, toolkit_binaries, toolkit_hiddenimports = collect_all('annotation_toolkit')

# Collect Qt5 plugins for Linux
# These are critical for PyQt5 GUI to work properly on Linux (X11/Wayland)
qt5_plugins_datas = []
qt5_binaries = []
try:
    from PyQt5 import QtCore
    qt_plugin_path = os.path.join(os.path.dirname(QtCore.__file__), 'Qt', 'plugins')
    if os.path.exists(qt_plugin_path):
        # Add platform plugins (libqxcb.so required for X11 support)
        platforms_dir = os.path.join(qt_plugin_path, 'platforms')
        if os.path.exists(platforms_dir):
            qt5_plugins_datas.append((platforms_dir, 'PyQt5/Qt/plugins/platforms'))

        # Add xcbglintegrations (required for OpenGL/X11 integration)
        xcbgl_dir = os.path.join(qt_plugin_path, 'xcbglintegrations')
        if os.path.exists(xcbgl_dir):
            qt5_plugins_datas.append((xcbgl_dir, 'PyQt5/Qt/plugins/xcbglintegrations'))

        # Add platformthemes (for native look and feel)
        platformthemes_dir = os.path.join(qt_plugin_path, 'platformthemes')
        if os.path.exists(platformthemes_dir):
            qt5_plugins_datas.append((platformthemes_dir, 'PyQt5/Qt/plugins/platformthemes'))

        # Add imageformats plugins (for image support)
        imageformats_dir = os.path.join(qt_plugin_path, 'imageformats')
        if os.path.exists(imageformats_dir):
            qt5_plugins_datas.append((imageformats_dir, 'PyQt5/Qt/plugins/imageformats'))

    # Try to collect Qt libraries that might be needed
    qt_lib_path = os.path.join(os.path.dirname(QtCore.__file__), 'Qt', 'lib')
    if os.path.exists(qt_lib_path):
        # Look for ICU libraries (required by Qt on Linux)
        for lib_file in os.listdir(qt_lib_path):
            if lib_file.startswith('libicu') and lib_file.endswith('.so'):
                lib_full_path = os.path.join(qt_lib_path, lib_file)
                qt5_binaries.append((lib_full_path, '.'))
except ImportError:
    print("Warning: Could not locate Qt5 plugins. GUI may not work correctly.")

# Combine all data and binaries
all_datas = qt5_plugins_datas + toolkit_datas
all_binaries = qt5_binaries + toolkit_binaries

block_cipher = None

a = Analysis(
    ['build_app.py'],
    pathex=[project_root],
    binaries=all_binaries,
    datas=all_datas,
    hiddenimports=[
        # PyQt5 imports (external dependency, not covered by collect_all)
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        # Other external dependencies
        'yaml',
        'markdown',
    ] + toolkit_hiddenimports,  # Add collected hiddenimports from annotation_toolkit
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AnnotationToolkit-Debug',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='AnnotationToolkit-Debug',
)
