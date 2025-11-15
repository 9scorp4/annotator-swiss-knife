# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

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

block_cipher = None

a = Analysis(
    ['build_app.py'],
    pathex=[project_root],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'yaml',
        'markdown',
        'annotation_toolkit',
        'annotation_toolkit.ui',
        'annotation_toolkit.ui.gui',
        'annotation_toolkit.ui.gui.app',
        'annotation_toolkit.core',
        'annotation_toolkit.utils',
        'annotation_toolkit.adapters',
        'annotation_toolkit.core.conversation',
        'annotation_toolkit.core.text',
        'annotation_toolkit.ui.cli',
        'annotation_toolkit.ui.gui.widgets',
    ],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AnnotationToolkit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
