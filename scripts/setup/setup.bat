@echo off
REM Setup script for Data Annotation Swiss Knife
REM This script creates a virtual environment and installs the application

echo =========================================
echo Data Annotation Swiss Knife Setup Script
echo =========================================
echo.

REM Check if Python 3.8+ is installed
echo Checking Python version...
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not found in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/ and try again.
    exit /b 1
)

REM Check Python version
for /f "tokens=*" %%a in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do set PYTHON_VERSION=%%a
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

if %PYTHON_MAJOR% LSS 3 (
    echo Error: Python 3.8 or higher is required.
    echo Found Python %PYTHON_VERSION%
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/ and try again.
    exit /b 1
)

if %PYTHON_MAJOR% EQU 3 (
    if %PYTHON_MINOR% LSS 8 (
        echo Error: Python 3.8 or higher is required.
        echo Found Python %PYTHON_VERSION%
        echo Please install Python 3.8 or higher from https://www.python.org/downloads/ and try again.
        exit /b 1
    )
)

echo Found Python %PYTHON_VERSION%

REM Determine the script directory and virtual environment path
set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR%..\..
set VENV_DIR=%PROJECT_DIR%\venv

REM Check if virtual environment already exists
if exist "%VENV_DIR%" (
    echo Virtual environment already exists at %VENV_DIR%
    set /p RECREATE="Do you want to recreate it? (y/n) "
    if /i "%RECREATE%"=="y" (
        echo Removing existing virtual environment...
        rmdir /s /q "%VENV_DIR%"
    ) else (
        echo Using existing virtual environment...
    )
)

REM Create virtual environment if it doesn't exist
if not exist "%VENV_DIR%" (
    echo Creating virtual environment...
    python -m venv "%VENV_DIR%"
    if %ERRORLEVEL% neq 0 (
        echo Error: Failed to create virtual environment.
        exit /b 1
    )
    echo Virtual environment created successfully.
)

REM Activate virtual environment
echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to activate virtual environment.
    exit /b 1
)

REM Upgrade pip
echo Upgrading pip...
pip install --upgrade pip
if %ERRORLEVEL% neq 0 (
    echo Warning: Failed to upgrade pip. Continuing anyway...
)

REM Install dependencies
echo Installing dependencies...
pip install -r "%PROJECT_DIR%\requirements.txt"
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to install dependencies.
    exit /b 1
)
echo Dependencies installed successfully.

REM Install the application in development mode
echo Installing the application...
pip install -e "%PROJECT_DIR%"
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to install the application.
    exit /b 1
)
echo Application installed successfully.

REM Create run script for Windows
echo Creating run scripts...

REM Create run.bat if it doesn't exist
if not exist "%PROJECT_DIR%\scripts\run\run.bat" (
    echo @echo off > "%PROJECT_DIR%\scripts\run\run.bat"
    echo REM Run script for Data Annotation Swiss Knife >> "%PROJECT_DIR%\scripts\run\run.bat"
    echo. >> "%PROJECT_DIR%\scripts\run\run.bat"
    echo REM Get the directory of this script >> "%PROJECT_DIR%\scripts\run\run.bat"
    echo SET SCRIPT_DIR=%%~dp0 >> "%PROJECT_DIR%\scripts\run\run.bat"
    echo SET VENV_DIR=%%SCRIPT_DIR%%..\\..\\venv >> "%PROJECT_DIR%\scripts\run\run.bat"
    echo SET ACTIVATE_SCRIPT=%%VENV_DIR%%\\Scripts\\activate.bat >> "%PROJECT_DIR%\scripts\run\run.bat"
    echo. >> "%PROJECT_DIR%\scripts\run\run.bat"
    echo REM Activate virtual environment >> "%PROJECT_DIR%\scripts\run\run.bat"
    echo call "%%ACTIVATE_SCRIPT%%" >> "%PROJECT_DIR%\scripts\run\run.bat"
    echo. >> "%PROJECT_DIR%\scripts\run\run.bat"
    echo REM Run the application >> "%PROJECT_DIR%\scripts\run\run.bat"
    echo annotation-toolkit %%* >> "%PROJECT_DIR%\scripts\run\run.bat"
)

echo Run scripts created successfully.

REM Print success message
echo.
echo Setup completed successfully!
echo.
echo How to run the application:
echo.
echo Using Command Prompt:
echo   run.bat gui - Launch the graphical user interface
echo   run.bat dict2bullet input.json -o output.md - Convert dictionary to bullet list
echo   run.bat jsonvis conversation.json -o output.txt - Visualize conversation
echo.
echo For more information, see the README.md file or run:
echo   run.bat --help
echo.
