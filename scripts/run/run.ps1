# Run script for Data Annotation Swiss Knife

# Set error action preference to stop on errors
$ErrorActionPreference = "Stop"

# Get the directory of this script and project root
$scriptDir = $PSScriptRoot
$projectDir = (Get-Item $scriptDir).Parent.Parent.FullName
$venvDir = Join-Path -Path $projectDir -ChildPath "venv"
$activateScript = Join-Path -Path $venvDir -ChildPath "Scripts\Activate.ps1"

# Check if virtual environment exists
if (-not (Test-Path $venvDir)) {
    Write-Host "ERROR: Virtual environment not found at $venvDir" -ForegroundColor Red
    Write-Host "Please run the setup script first:" -ForegroundColor Yellow
    Write-Host "  scripts\setup\setup.ps1" -ForegroundColor Yellow
    exit 1
}

# Check if activation script exists
if (-not (Test-Path $activateScript)) {
    Write-Host "ERROR: Virtual environment activation script not found at $activateScript" -ForegroundColor Red
    Write-Host "Please run the setup script to recreate the virtual environment:" -ForegroundColor Yellow
    Write-Host "  scripts\setup\setup.ps1" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
try {
    . $activateScript
} catch {
    Write-Host "ERROR: Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "Please run the setup script to recreate the virtual environment:" -ForegroundColor Yellow
    Write-Host "  scripts\setup\setup.ps1" -ForegroundColor Yellow
    exit 1
}

# Check if annotation-toolkit command is available
try {
    Get-Command annotation-toolkit -ErrorAction Stop | Out-Null
} catch {
    Write-Host "ERROR: annotation-toolkit command not found" -ForegroundColor Red
    Write-Host "Please run the setup script to install the application:" -ForegroundColor Yellow
    Write-Host "  scripts\setup\setup.ps1" -ForegroundColor Yellow
    exit 1
}

# Run the application
Write-Host "Running annotation-toolkit..." -ForegroundColor Green
annotation-toolkit $args
