@echo off
REM Run script for Data Annotation Swiss Knife

setlocal enabledelayedexpansion

REM Get the directory of this script and project root
SET SCRIPT_DIR=%~dp0
REM Remove trailing backslash from SCRIPT_DIR if present
if "%SCRIPT_DIR:~-1%"=="\" set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%
REM Get project root (two levels up from script directory)
for %%i in ("%SCRIPT_DIR%") do set PARENT_DIR=%%~dpi
if "%PARENT_DIR:~-1%"=="\" set PARENT_DIR=%PARENT_DIR:~0,-1%
for %%i in ("%PARENT_DIR%") do set PROJECT_ROOT=%%~dpi
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

REM Check if activation script exists
if not exist "%ACTIVATE_SCRIPT%" (
    echo ERROR: Virtual environment activation script not found at %ACTIVATE_SCRIPT%
    echo Please run the setup script to recreate the virtual environment:
    echo   scripts\setup\setup.bat
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call "%ACTIVATE_SCRIPT%"
if !errorlevel! neq 0 (
    echo ERROR: Failed to activate virtual environment
    echo Please run the setup script to recreate the virtual environment:
    echo   scripts\setup\setup.bat
    exit /b 1
)

REM Check if annotation-toolkit command is available
where annotation-toolkit >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: annotation-toolkit command not found
    echo Please run the setup script to install the application:
    echo   scripts\setup\setup.bat
    exit /b 1
)

REM Run the application
echo Running annotation-toolkit...
annotation-toolkit %*
