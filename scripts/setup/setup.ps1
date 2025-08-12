# Setup script for Data Annotation Swiss Knife
# This script creates a virtual environment and installs the application

param(
    [switch]$Force = $false
)

# Text formatting
$Green = "`e[32m"
$Red = "`e[31m"
$Yellow = "`e[33m"
$Bold = "`e[1m"
$Reset = "`e[0m"

# Print header
Write-Host "${Bold}=========================================${Reset}"
Write-Host "${Bold}Data Annotation Swiss Knife Setup Script${Reset}"
Write-Host "${Bold}=========================================${Reset}"
Write-Host ""

# Check if Python is installed
Write-Host "${Bold}Checking Python version...${Reset}"
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }

    $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)\.(\d+)"
    if (-not $versionMatch) {
        throw "Could not parse Python version"
    }

    $major = [int]$Matches[1]
    $minor = [int]$Matches[2]

    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
        Write-Host "${Red}Error: Python 3.8 or higher is required.${Reset}"
        Write-Host "Found: $pythonVersion"
        Write-Host "Please install Python 3.8 or higher from https://python.org/downloads/"
        exit 1
    }

    Write-Host "${Green}Found: $pythonVersion${Reset}"
} catch {
    Write-Host "${Red}Error: Python is required but not found.${Reset}"
    Write-Host "Please install Python 3.8 or higher and add it to your PATH."
    Write-Host "Download from: https://python.org/downloads/"
    exit 1
}

# Get script directory and project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)
$venvDir = Join-Path $projectRoot "venv"

# Check if virtual environment already exists
if (Test-Path $venvDir) {
    Write-Host "${Yellow}Virtual environment already exists at $venvDir${Reset}"
    if ($Force) {
        Write-Host "${Bold}Force flag specified. Removing existing virtual environment...${Reset}"
        Remove-Item -Recurse -Force $venvDir
    } else {
        $recreate = Read-Host "Do you want to recreate it? (y/n)"
        if ($recreate -match "^[Yy]") {
            Write-Host "${Bold}Removing existing virtual environment...${Reset}"
            Remove-Item -Recurse -Force $venvDir
        } else {
            Write-Host "${Bold}Using existing virtual environment...${Reset}"
        }
    }
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path $venvDir)) {
    Write-Host "${Bold}Creating virtual environment...${Reset}"
    python -m venv $venvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Host "${Red}Error: Failed to create virtual environment.${Reset}"
        Write-Host "Make sure you have the 'venv' module available."
        exit 1
    }
    Write-Host "${Green}Virtual environment created successfully.${Reset}"
}

# Activate virtual environment
Write-Host "${Bold}Activating virtual environment...${Reset}"
$activateScript = Join-Path $venvDir "Scripts\Activate.ps1"

# Enable script execution if needed
try {
    & $activateScript
} catch {
    Write-Host "${Yellow}Enabling PowerShell script execution...${Reset}"
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    & $activateScript
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "${Red}Error: Failed to activate virtual environment.${Reset}"
    exit 1
}

# Upgrade pip
Write-Host "${Bold}Upgrading pip...${Reset}"
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "${Yellow}Warning: Failed to upgrade pip. Continuing anyway...${Reset}"
}

# Install dependencies
Write-Host "${Bold}Installing dependencies...${Reset}"
$requirementsPath = Join-Path $projectRoot "requirements.txt"
pip install -r $requirementsPath
if ($LASTEXITCODE -ne 0) {
    Write-Host "${Red}Error: Failed to install dependencies.${Reset}"
    Write-Host "Make sure requirements.txt exists and contains valid packages."
    exit 1
}
Write-Host "${Green}Dependencies installed successfully.${Reset}"

# Install the application in development mode
Write-Host "${Bold}Installing the application...${Reset}"
pip install -e $projectRoot
if ($LASTEXITCODE -ne 0) {
    Write-Host "${Red}Error: Failed to install the application.${Reset}"
    Write-Host "Make sure setup.py exists in the project root."
    exit 1
}
Write-Host "${Green}Application installed successfully.${Reset}"

Write-Host ""
Write-Host "${Bold}${Green}Setup completed successfully!${Reset}"
Write-Host ""
Write-Host "${Bold}How to run the application:${Reset}"
Write-Host ""
Write-Host "  ${Yellow}scripts\run\run.bat gui${Reset}                           - Launch the graphical user interface"
Write-Host "  ${Yellow}scripts\run\run.bat dict2bullet input.json -o output.md${Reset}  - Convert dictionary to bullet list"
Write-Host "  ${Yellow}scripts\run\run.bat jsonvis conversation.json -o output.txt${Reset}  - Visualize conversation"
Write-Host ""
Write-Host "Or using PowerShell:"
Write-Host "  ${Yellow}scripts\run\run.ps1 gui${Reset}                           - Launch the graphical user interface"
Write-Host ""
Write-Host "For more information, see the README.md file or run:"
Write-Host "  ${Yellow}scripts\run\run.bat --help${Reset}"
Write-Host ""
