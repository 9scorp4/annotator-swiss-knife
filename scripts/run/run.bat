@echo off
REM Run script for Data Annotation Swiss Knife

setlocal enabledelayedexpansion

REM Get the directory of this script and project root
SET "SCRIPT_DIR=%~dp0"
REM Remove trailing backslash if present
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Navigate up to get project root (two levels up from run.bat)
cd /d "%SCRIPT_DIR%"
cd ..\..
SET "PROJECT_ROOT=%CD%"

REM Set virtual environment paths
SET "VENV_DIR=%PROJECT_ROOT%\venv"
SET "ACTIVATE_SCRIPT=%VENV_DIR%\Scripts\activate.bat"

REM Check if virtual environment exists
if not exist "%VENV_DIR%" (
    echo ERROR: Virtual environment not found at %VENV_DIR%
    echo Please run the setup script first:
    echo   scripts\setup\setup.bat
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call "%ACTIVATE_SCRIPT%"
if !errorlevel! neq 0 (
    echo ERROR: Failed to activate virtual environment
    exit /b 1
)

REM Run the application
annotation-toolkit %*
