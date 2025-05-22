# Setup Scripts

This directory contains scripts for setting up the Annotation Toolkit application.

## Files

- `setup.bat`: Batch script for setting up the application on Windows using Command Prompt
- `setup.ps1`: PowerShell script for setting up the application on Windows using PowerShell
- `setup.sh`: Shell script for setting up the application on macOS/Linux

## Usage

### On macOS/Linux

```bash
chmod +x setup.sh
./setup.sh
```

### On Windows (PowerShell)

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup.ps1
```

### On Windows (Command Prompt)

```batch
setup.bat
```

For more information, see the main README.md file in the root directory.
