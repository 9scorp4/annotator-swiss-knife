@echo off
REM Run script for Data Annotation Swiss Knife

REM Get the directory of this script
SET SCRIPT_DIR=%~dp0
SET VENV_DIR=%SCRIPT_DIR%..\..\venv
SET ACTIVATE_SCRIPT=%VENV_DIR%\Scripts\activate.bat

REM Activate virtual environment
call "%ACTIVATE_SCRIPT%"

REM Run the application
annotation-toolkit %*
