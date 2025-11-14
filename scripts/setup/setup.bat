@echo off
REM Setup script for Data Annotation Swiss Knife
REM This script creates a virtual environment and installs the application

setlocal enabledelayedexpansion

REM Print header
echo =========================================
echo Data Annotation Swiss Knife Setup Script
echo =========================================
echo.

REM Check if Python is installed
echo Checking Python version...
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: Python is required but not found.
    echo Please install Python 3.8 or higher and add it to your PATH.
    echo Download from: https://python.org/downloads/
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%

REM Check if Python version is 3.8 or higher
for /f "tokens=1,2 delims=." %%i in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%i
    set PYTHON_MINOR=%%j
)

if !PYTHON_MAJOR! lss 3 (
    echo ERROR: Python 3.8 or higher is required.
    echo Found Python %PYTHON_VERSION%
    echo Please install Python 3.8 or higher and try again.
    pause
    exit /b 1
)

if !PYTHON_MAJOR! equ 3 if !PYTHON_MINOR! lss 8 (
    echo ERROR: Python 3.8 or higher is required.
    echo Found Python %PYTHON_VERSION%
    echo Please install Python 3.8 or higher and try again.
    pause
    exit /b 1
)

REM Get the directory of this script and project root
SET "SCRIPT_DIR=%~dp0"
REM Remove trailing backslash if present
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Navigate up to get project root (two levels up from setup.bat)
cd /d "%SCRIPT_DIR%"
cd ..\..
SET "PROJECT_ROOT=%CD%"

REM Set virtual environment directory
SET "VENV_DIR=%PROJECT_ROOT%\venv"

REM Check if virtual environment already exists
if exist "%VENV_DIR%" (
    echo Virtual environment already exists at %VENV_DIR%
    set /p RECREATE="Do you want to recreate it? (y/n): "
    if /i "!RECREATE!"=="y" (
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
    if !errorlevel! neq 0 (
        echo ERROR: Failed to create virtual environment.
        echo Make sure you have the 'venv' module available.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
)

REM Activate virtual environment
echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
if !errorlevel! neq 0 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
if !errorlevel! neq 0 (
    echo WARNING: Failed to upgrade pip. Continuing anyway...
)

REM Install dependencies
echo Installing dependencies...
pip install -r "%PROJECT_ROOT%\requirements.txt"
if !errorlevel! neq 0 (
    echo ERROR: Failed to install dependencies.
    echo Make sure requirements.txt exists and contains valid packages.
    pause
    exit /b 1
)
echo Dependencies installed successfully.

REM Install the application in development mode
echo Installing the application...
pip install -e "%PROJECT_ROOT%"
if !errorlevel! neq 0 (
    echo ERROR: Failed to install the application.
    echo Make sure setup.py exists in the project root.
    pause
    exit /b 1
)
echo Application installed successfully.

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo How to run the application:
echo.
echo   scripts\run\run.bat gui                           - Launch the graphical user interface
echo   scripts\run\run.bat dict2bullet input.json -o output.md  - Convert dictionary to bullet list
echo   scripts\run\run.bat jsonvis conversation.json -o output.txt  - Visualize conversation
echo.
echo For more information, see the README.md file or run:
echo   scripts\run\run.bat --help
echo.
pause
