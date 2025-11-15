# Building Annotation Toolkit Executables

This guide explains how to build standalone executables for the Annotation Toolkit application locally for development and testing.

> **Note**: For official releases, executables are automatically built via CI/CD when creating git tags. See [RELEASE_PROCESS.md](RELEASE_PROCESS.md) for the automated release process.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (to clone the repository)

## Automated Builds (Recommended for Releases)

The project includes a CI/CD pipeline that automatically builds executables for all platforms when you create a release tag:

1. Create a git tag: `git tag -a v1.0.0 -m "Release version 1.0.0"`
2. Push the tag: `git push origin v1.0.0`
3. GitHub Actions builds executables for macOS, Windows, and Linux
4. Executables are attached to the GitHub Release

See [RELEASE_PROCESS.md](RELEASE_PROCESS.md) for complete instructions.

## Manual Local Builds (For Development/Testing)

### Building on macOS

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

## Building on Linux

1. Open Terminal
2. Navigate to the project directory:
   ```
   cd /path/to/annotator_swiss_knife
   ```
3. Make the build script executable:
   ```
   chmod +x scripts/build/build_linux.sh
   ```
4. Run the build script:
   ```
   ./scripts/build/build_linux.sh
   ```
5. Once the build is complete, you can find the executable at:
   ```
   dist/AnnotationToolkit
   ```
6. To run the application:
   ```
   chmod +x dist/AnnotationToolkit
   ./dist/AnnotationToolkit
   ```

**Note:** The Linux executable is built as a standalone binary and may require additional system libraries depending on your distribution.

## Troubleshooting

### Common Issues on Linux

- **GLIBC version mismatch**: The executable requires a minimum GLIBC version. If you see an error like `GLIBC_X.XX' not found`, your system has an older GLIBC version than required.
  - **Solution 1**: Use the AppImage release build (recommended) - it's more portable
  - **Solution 2**: Check your GLIBC version with `ldd --version`
  - **Solution 3**: Use the Python package instead: `pip install annotation-toolkit`
  - The CI/CD builds use Ubuntu 20.04 (GLIBC 2.31) for better compatibility

- **Qt platform plugin errors**: If you see "Could not find the Qt platform plugin", make sure you have the required X11 libraries installed:
  ```bash
  sudo apt-get install libxcb-xinerama0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0
  ```

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
- `scripts/build/linux_build.spec`: PyInstaller specification file for Linux
- `scripts/build/file_version_info.txt`: Version information for the Windows executable

**Note:** Version numbers are now automatically derived from git tags using setuptools-scm. The spec files read the version dynamically from the package.

## Distribution

### Automated Distribution (Recommended)

The recommended way to distribute executables is through GitHub Releases:

1. Follow the release process in [RELEASE_PROCESS.md](RELEASE_PROCESS.md)
2. Create a git tag (e.g., `v1.0.0`)
3. Push the tag to GitHub
4. GitHub Actions automatically builds and publishes executables
5. Users download from the [Releases page](https://github.com/9scorp4/annotator-swiss-knife/releases)

This ensures:
- Consistent builds across all platforms
- Automatic version numbering
- SHA256 checksums for verification
- Proper release notes and documentation

### Manual Distribution

If you've built executables locally, you can distribute them manually:

- **macOS:** Create a DMG file or zip the .app bundle
- **Windows:** Create an installer using tools like NSIS or Inno Setup, or zip the .exe file
- **Linux:** Create a .tar.gz archive or AppImage

**Security Note:** Manually distributed executables are unsigned and will trigger security warnings. For production releases, use the automated GitHub Releases process.
