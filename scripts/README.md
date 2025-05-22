# Scripts Directory

This directory contains various scripts for building, running, and setting up the Annotation Toolkit application.

## Directory Structure

```
scripts/
├── build/                # Build scripts for creating executables
│   ├── build_app.py      # Python script for building the application
│   ├── build_mac.sh      # Shell script for building the macOS application
│   ├── build_windows.bat # Batch script for building the Windows application
│   ├── file_version_info.txt # Version information for the Windows executable
│   ├── mac_build.spec    # PyInstaller specification file for macOS
│   └── windows_build.spec # PyInstaller specification file for Windows
├── run/                  # Scripts for running the application
│   ├── run.bat           # Batch script for running the application on Windows
│   ├── run.ps1           # PowerShell script for running the application on Windows
│   └── run.sh            # Shell script for running the application on macOS/Linux
└── setup/                # Scripts for setting up the application
    ├── setup.bat         # Batch script for setting up the application on Windows
    ├── setup.ps1         # PowerShell script for setting up the application on Windows
    └── setup.sh          # Shell script for setting up the application on macOS/Linux
```

## Build Scripts

The build scripts are used to create standalone executables for the Annotation Toolkit application.

### build_app.py

This Python script is the main build script that handles the build process for both macOS and Windows. It uses PyInstaller to create the executables.

Usage:
```bash
python scripts/build/build_app.py --platform [mac|windows]
```

### build_mac.sh

This shell script is a wrapper around `build_app.py` for macOS. It sets up the environment and calls the Python script with the appropriate parameters.

Usage:
```bash
./scripts/build/build_mac.sh
```

### build_windows.bat

This batch script is a wrapper around `build_app.py` for Windows. It sets up the environment and calls the Python script with the appropriate parameters.

Usage:
```cmd
scripts\build\build_windows.bat
```

### file_version_info.txt

This file contains version information for the Windows executable. It is used by PyInstaller to set the version information in the Windows executable.

### mac_build.spec

This is the PyInstaller specification file for macOS. It defines how the macOS application should be built.

### windows_build.spec

This is the PyInstaller specification file for Windows. It defines how the Windows executable should be built.

## Run Scripts

The run scripts are used to run the Annotation Toolkit application.

### run.sh

This shell script runs the Annotation Toolkit application on macOS/Linux. It activates the virtual environment and runs the application.

Usage:
```bash
./scripts/run/run.sh [command]
```

Available commands:
- `gui`: Launch the graphical user interface
- `dict2bullet`: Run the Dictionary to Bullet List tool
- `convvis`: Run the Conversation Visualizer tool
- `jsonvis`: Run the JSON Visualizer tool
- `textclean`: Run the Text Cleaner tool
- `--help`: Show help message

### run.bat

This batch script runs the Annotation Toolkit application on Windows. It activates the virtual environment and runs the application.

Usage:
```cmd
scripts\run\run.bat [command]
```

Available commands are the same as for `run.sh`.

### run.ps1

This PowerShell script runs the Annotation Toolkit application on Windows. It activates the virtual environment and runs the application.

Usage:
```powershell
.\scripts\run\run.ps1 [command]
```

Available commands are the same as for `run.sh`.

## Setup Scripts

The setup scripts are used to set up the Annotation Toolkit application.

### setup.sh

This shell script sets up the Annotation Toolkit application on macOS/Linux. It creates a virtual environment, installs dependencies, and sets up the application.

Usage:
```bash
./scripts/setup/setup.sh
```

### setup.bat

This batch script sets up the Annotation Toolkit application on Windows. It creates a virtual environment, installs dependencies, and sets up the application.

Usage:
```cmd
scripts\setup\setup.bat
```

### setup.ps1

This PowerShell script sets up the Annotation Toolkit application on Windows. It creates a virtual environment, installs dependencies, and sets up the application.

Usage:
```powershell
.\scripts\setup\setup.ps1
```

## Customizing Scripts

If you need to customize the build, run, or setup scripts, you can modify the appropriate files. For example, if you need to add a new dependency, you can modify the setup scripts to install the new dependency.

For more information on building standalone executables, see the [README_BUILD.md](../README_BUILD.md) file.
