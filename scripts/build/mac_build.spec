# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_all

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

block_cipher = None

a = Analysis(
    ['build_app.py'],
    pathex=[project_root],
    binaries=toolkit_binaries,
    datas=toolkit_datas,
    hiddenimports=[
        # Standard library modules (explicitly included to avoid PyInstaller issues)
        'json',
        'xml',
        'xml.etree',
        'xml.etree.ElementTree',
        're',
        'logging',
        'pathlib',
        'collections',
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
    name='AnnotationToolkit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
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
    name='AnnotationToolkit',
)

app = BUNDLE(
    coll,
    name='AnnotationToolkit.app',
    icon=None,
    bundle_identifier='com.annotationtoolkit.app',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'CFBundleShortVersionString': version,
        'CFBundleVersion': version,
        'NSHumanReadableCopyright': '© 2025 Nicolas Arias Garcia',
    },
)
