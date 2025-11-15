# Build Scripts

This directory contains scripts for building standalone executables of the Annotation Toolkit application.

## Files

- `build_app.py`: Python script for building the application
- `build_mac.sh`: Shell script for building the macOS application
- `build_windows.bat`: Batch script for building the Windows application
- `file_version_info.txt`: Version information for the Windows executable
- `mac_build.spec`: PyInstaller specification file for macOS
- `windows_build.spec`: PyInstaller specification file for Windows

## Usage

### On macOS

```bash
./build_mac.sh
```

### On Windows

```batch
build_windows.bat
```

For more information, see the main README_BUILD.md file in the root directory.
