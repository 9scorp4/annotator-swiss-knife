# Building Annotation Toolkit Executables

This guide explains how to build standalone executables for the Annotation Toolkit application for both macOS and Windows.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (to clone the repository)

## Building on macOS

1. Open Terminal
2. Navigate to the project directory:
   ```
   cd /path/to/annotator_swiss_knife
   ```
3. Make the build script executable:
   ```
   chmod +x scripts/build/build_mac.sh
   ```
4. Run the build script:
   ```
   ./scripts/build/build_mac.sh
   ```
5. Once the build is complete, you can find the application at:
   ```
   dist/AnnotationToolkit.app
   ```
6. To run the application, double-click on the `AnnotationToolkit.app` file.

**Note:** If you get a security warning when trying to open the app, go to System Preferences > Security & Privacy and click 'Open Anyway'.

## Building on Windows

1. Open Command Prompt
2. Navigate to the project directory:
   ```
   cd \path\to\annotator_swiss_knife
   ```
3. Run the build script:
   ```
   scripts\build\build_windows.bat
   ```
4. Once the build is complete, you can find the executable at:
   ```
   dist\AnnotationToolkit.exe
   ```
5. To run the application, double-click on the `AnnotationToolkit.exe` file.

**Note:** If Windows SmartScreen prevents the app from running, click "More info" and then "Run anyway".

## Troubleshooting

### Common Issues on macOS

- **App won't open due to security settings**: macOS has strict security settings for unsigned applications. To open the app:
  1. Right-click (or Control-click) on the app
  2. Select "Open" from the context menu
  3. Click "Open" in the dialog that appears

### Common Issues on Windows

- **Missing DLLs**: If you get errors about missing DLLs, make sure you have the Visual C++ Redistributable installed.
- **PyInstaller not found**: Make sure you have activated the virtual environment before running the build script.

## Customizing the Build

If you need to customize the build process, you can modify the following files:

- `scripts/build/mac_build.spec`: PyInstaller specification file for macOS
- `scripts/build/windows_build.spec`: PyInstaller specification file for Windows
- `scripts/build/file_version_info.txt`: Version information for the Windows executable

## Distribution

After building the executables, you can distribute them to users:

- For macOS, you can create a DMG file or zip the .app file
- For Windows, you can create an installer using tools like NSIS or Inno Setup, or simply zip the executable and its dependencies
