# Windows Setup and Troubleshooting Guide

This guide provides Windows-specific instructions for setting up and running the Data Annotation Swiss Knife application.

## Quick Start for Windows Users

### Prerequisites
1. **Python 3.8 or higher** installed from [python.org](https://python.org/downloads/)
   - ⚠️ **Important**: During installation, check "Add Python to PATH"
   - To verify: Open Command Prompt and run `python --version`

### Installation Options

#### Option 1: Command Prompt (Batch Files)
```cmd
# Navigate to the project directory
cd path\to\annotator_swiss_knife

# Run setup
scripts\setup\setup.bat

# Run the application
scripts\run\run.bat gui
```

#### Option 2: PowerShell (Recommended)
```powershell
# Navigate to the project directory
cd path\to\annotator_swiss_knife

# Run setup
scripts\setup\setup.ps1

# Run the application
scripts\run\run.ps1 gui
```

#### Option 3: Windows Subsystem for Linux (WSL)
If you have WSL installed, you can use the Linux scripts:
```bash
# Navigate to the project directory
cd /mnt/c/path/to/annotator_swiss_knife

# Run setup
./scripts/setup/setup.sh

# Run the application
./scripts/run/run.sh gui
```

## Common Issues and Solutions

### Issue 1: "Python is not recognized"
**Error**: `'python' is not recognized as an internal or external command`

**Solution**:
1. Install Python from [python.org](https://python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Restart Command Prompt/PowerShell
4. Test with `python --version`

**Alternative**: Try using `py` instead of `python`:
```cmd
py --version
py -m venv venv
```

### Issue 2: PowerShell Execution Policy Error
**Error**: `cannot be loaded because running scripts is disabled on this system`

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

This allows locally created scripts to run while maintaining security for downloaded scripts.

### Issue 3: Virtual Environment Activation Fails
**Error**: Virtual environment doesn't activate properly

**Solutions**:
1. **For Command Prompt**: Ensure you're using `call` before the activation script:
   ```cmd
   call venv\Scripts\activate.bat
   ```

2. **For PowerShell**: Ensure execution policy allows scripts:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   venv\Scripts\Activate.ps1
   ```

### Issue 4: PyQt5 Installation Problems
**Error**: PyQt5 fails to install or GUI doesn't work

**Solutions**:
1. **Install Visual C++ Redistributable**:
   - Download from Microsoft's website
   - Or install Visual Studio Build Tools

2. **Try alternative PyQt5 installation**:
   ```cmd
   pip install PyQt5 --only-binary=all
   ```

3. **For older Windows versions**:
   ```cmd
   pip install PyQt5==5.12.3
   ```

### Issue 5: Permission Errors
**Error**: Access denied when creating virtual environment

**Solutions**:
1. **Run as Administrator**: Right-click Command Prompt/PowerShell and select "Run as administrator"

2. **Check antivirus**: Temporarily disable real-time protection during setup

3. **Use different location**: Move project to a location without restrictions (e.g., `C:\projects\`)

### Issue 6: Long Path Issues
**Error**: Path names are too long

**Solutions**:
1. **Enable long paths in Windows**:
   - Run `gpedit.msc` as administrator
   - Navigate to: Computer Configuration > Administrative Templates > System > Filesystem
   - Enable "Enable Win32 long paths"

2. **Move project closer to root**:
   ```cmd
   move annotator_swiss_knife C:\projects\annotator_swiss_knife
   ```

## Alternative Installation Methods

### Using Conda/Miniconda
If you prefer Conda over pip:

```cmd
# Create conda environment
conda create -n annotation-toolkit python=3.8
conda activate annotation-toolkit

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### Using Git Bash
If you have Git for Windows installed:

```bash
# Use the Linux scripts directly
./scripts/setup/setup.sh
./scripts/run/run.sh gui
```

## Testing Your Installation

### 1. Verify Python Installation
```cmd
python --version
pip --version
```

### 2. Test Virtual Environment
```cmd
# Navigate to project
cd annotator_swiss_knife

# Check if venv exists
dir venv

# Activate manually
venv\Scripts\activate.bat

# Check if annotation-toolkit is available
annotation-toolkit --help
```

### 3. Test GUI Application
```cmd
scripts\run\run.bat gui
```

The GUI should launch without errors.

## Performance Tips for Windows

1. **Exclude from Windows Defender**: Add the project folder to Windows Defender exclusions for faster pip installs

2. **Use SSD storage**: Install on SSD rather than HDD for better performance

3. **Close unnecessary applications**: Free up memory before running the GUI application

## Getting Help

If you're still experiencing issues:

1. **Check the main README.md** for general troubleshooting
2. **Check Windows Event Viewer** for system-level errors
3. **Run with verbose output**:
   ```cmd
   scripts\run\run.bat --verbose gui
   ```
4. **Create an issue** with:
   - Windows version (`winver`)
   - Python version (`python --version`)
   - Error messages (copy/paste exactly)
   - Steps you tried

## Advanced: Building Windows Executable

To create a standalone Windows executable:

```cmd
# Activate virtual environment
scripts\setup\setup.bat

# Install PyInstaller (already in requirements.txt)
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed annotation_toolkit/main.py

# Find the executable in dist/ folder
```

This creates a single `.exe` file that can run without Python installed.
