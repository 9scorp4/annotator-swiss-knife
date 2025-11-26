@echo off
:: Build script for Windows executable

echo === Annotation Toolkit Windows Build Script ===
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH. Please install Python and try again.
    exit /b 1
)

:: Get the directory of this script and project root
SET SCRIPT_DIR=%~dp0
if "%SCRIPT_DIR:~-1%"=="\" set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

:: Get project root (parent of parent of this script)
for %%i in ("%SCRIPT_DIR%") do set SCRIPTS_DIR=%%~dpi
if "%SCRIPTS_DIR:~-1%"=="\" set SCRIPTS_DIR=%SCRIPTS_DIR:~0,-1%
for %%i in ("%SCRIPTS_DIR%") do set PROJECT_ROOT=%%~dpi
if "%PROJECT_ROOT:~-1%"=="\" set PROJECT_ROOT=%PROJECT_ROOT:~0,-1%

:: Create or activate virtual environment in project root
SET VENV_DIR=%PROJECT_ROOT%\venv
if not exist "%VENV_DIR%" (
    echo Creating virtual environment...
    python -m venv "%VENV_DIR%"
)

echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

:: Install requirements
echo Installing requirements...
:: Use the full path to requirements.txt
pip install -r "%PROJECT_ROOT%\requirements.txt"

:: Install the package in editable mode
echo Installing annotation_toolkit package...
pip install -e "%PROJECT_ROOT%"

:: Install PyInstaller if not already installed
pip show pyinstaller >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

:: Build the executable
echo Building Windows executable...
:: Change to the build directory to run PyInstaller
cd /d "%SCRIPT_DIR%"
:: Set dist directory to project root's dist
SET DIST_DIR=%PROJECT_ROOT%\dist
pyinstaller "windows_build.spec" --distpath "%DIST_DIR%" --clean --noconfirm

:: Get version from package
cd /d "%PROJECT_ROOT%"
for /f "delims=" %%i in ('python -c "from annotation_toolkit import __version__; print(__version__)"') do set VERSION=%%i
echo Version: %VERSION%

:: Create zip archive for distribution
cd /d "%PROJECT_ROOT%\dist"

echo.
echo Creating archive...
if exist "AnnotationToolkit" (
    powershell -Command "Compress-Archive -Path 'AnnotationToolkit' -DestinationPath 'AnnotationToolkit-%VERSION%-Windows.zip' -Force"
    echo Created: AnnotationToolkit-%VERSION%-Windows.zip
)

echo.
echo === Build Complete ===
echo.
echo The Windows application has been built successfully!
echo.
echo Build location: dist\AnnotationToolkit-%VERSION%-Windows.zip
echo.
echo To run the application:
echo 1. Extract the zip file
echo 2. Run AnnotationToolkit.exe
echo.
echo Note: If Windows SmartScreen prevents the app from running,
echo click "More info" and then "Run anyway".
echo.

pause
