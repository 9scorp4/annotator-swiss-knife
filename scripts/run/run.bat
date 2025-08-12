@echo off
REM Run script for Data Annotation Swiss Knife

setlocal enabledelayedexpansion

REM Get the directory of this script and project root
SET SCRIPT_DIR=%~dp0
if "%SCRIPT_DIR:~-1%"=="\" set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

REM Get parent directory (scripts)
for %%i in ("%SCRIPT_DIR%") do set SCRIPTS_DIR=%%~dpi
if "%SCRIPTS_DIR:~-1%"=="\" set SCRIPTS_DIR=%SCRIPTS_DIR:~0,-1%

REM Get project root (parent of scripts)
for %%i in ("%SCRIPTS_DIR%") do set PROJECT_ROOT=%%~dpi
if "%PROJECT_ROOT:~-1%"=="\" set PROJECT_ROOT=%PROJECT_ROOT:~0,-1%

SET VENV_DIR=%PROJECT_ROOT%\venv
SET ACTIVATE_SCRIPT=%VENV_DIR%\Scripts\activate.bat

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
