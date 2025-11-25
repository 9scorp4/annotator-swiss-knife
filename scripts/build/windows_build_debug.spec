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

# Collect Qt5 plugins for Windows
# These are critical for PyQt5 GUI to work properly
qt5_plugins_datas = []
try:
    from PyQt5 import QtCore
    qt_plugin_path = os.path.join(os.path.dirname(QtCore.__file__), 'Qt5', 'plugins')
    if os.path.exists(qt_plugin_path):
        # Add platform plugins (required for GUI to start)
        platforms_dir = os.path.join(qt_plugin_path, 'platforms')
        if os.path.exists(platforms_dir):
            qt5_plugins_datas.append((platforms_dir, 'PyQt5/Qt5/plugins/platforms'))

        # Add styles plugins (for consistent UI appearance)
        styles_dir = os.path.join(qt_plugin_path, 'styles')
        if os.path.exists(styles_dir):
            qt5_plugins_datas.append((styles_dir, 'PyQt5/Qt5/plugins/styles'))

        # Add imageformats plugins (for image support)
        imageformats_dir = os.path.join(qt_plugin_path, 'imageformats')
        if os.path.exists(imageformats_dir):
            qt5_plugins_datas.append((imageformats_dir, 'PyQt5/Qt5/plugins/imageformats'))
except ImportError:
    print("Warning: Could not locate Qt5 plugins. GUI may not work correctly.")

# Combine all data files
all_datas = qt5_plugins_datas + toolkit_datas

block_cipher = None

a = Analysis(
    ['build_app.py'],
    pathex=[project_root],
    binaries=toolkit_binaries,
    datas=all_datas,
    hiddenimports=[
        # Standard library modules (explicitly included to avoid PyInstaller issues)
        'argparse',
        'asyncio',
        'atexit',
        'collections',
        'contextlib',
        'contextvars',
        'copy',
        'cProfile',
        'dataclasses',
        'datetime',
        'enum',
        'functools',
        'hashlib',
        'html',
        'inspect',
        'io',
        'json',
        'logging',
        'math',
        'os',
        'pathlib',
        'pstats',
        'random',
        're',
        'shutil',
        'statistics',
        'sys',
        'tempfile',
        'threading',
        'time',
        'traceback',
        'typing',
        'urllib',
        'urllib.parse',
        'urllib.request',
        'uuid',
        'weakref',
        'webbrowser',
        'xml',
        'xml.etree',
        'xml.etree.ElementTree',
        # PyQt5 imports (external dependency, not covered by collect_all)
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.QtSvg',
        # Other external dependencies
        'yaml',
        'markdown',
        'chardet',
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
    version=os.path.join(current_dir, 'file_version_info.txt') if os.path.exists(os.path.join(current_dir, 'file_version_info.txt')) else None,
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
