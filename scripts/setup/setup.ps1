# Setup script for Data Annotation Swiss Knife
# This script creates a virtual environment and installs the application

# Function to check if running as administrator
function Test-Administrator {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    $currentUser.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
}

# Print header
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Data Annotation Swiss Knife Setup Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python 3.8+ is installed
Write-Host "Checking Python version..." -ForegroundColor Cyan
$pythonCommand = $null

# Try python3 command first
try {
    $pythonVersion = python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
    if ($?) {
        $pythonCommand = "python3"
    }
}
catch {
    # Python3 command not found, try python
    try {
        $pythonVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
        if ($?) {
            $pythonCommand = "python"
        }
    }
    catch {
        # Python command not found
    }
}

if ($null -eq $pythonCommand) {
    Write-Host "Error: Python 3.8 or higher is required but not found." -ForegroundColor Red
    Write-Host "Please install Python 3.8 or higher from https://www.python.org/downloads/ and try again."
    exit 1
}

# Check Python version
$pythonVersion = & $pythonCommand -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$pythonMajor = [int]($pythonVersion.Split('.')[0])
$pythonMinor = [int]($pythonVersion.Split('.')[1])

if ($pythonMajor -lt 3 -or ($pythonMajor -eq 3 -and $pythonMinor -lt 8)) {
    Write-Host "Error: Python 3.8 or higher is required." -ForegroundColor Red
    Write-Host "Found Python $pythonVersion"
    Write-Host "Please install Python 3.8 or higher from https://www.python.org/downloads/ and try again."
    exit 1
}

Write-Host "Found Python $pythonVersion" -ForegroundColor Green

# Determine the script directory and virtual environment path
$scriptDir = $PSScriptRoot
$projectDir = (Get-Item $scriptDir).Parent.Parent.FullName
$venvDir = Join-Path -Path $projectDir -ChildPath "venv"

# Check if virtual environment already exists
if (Test-Path -Path $venvDir) {
    Write-Host "Virtual environment already exists at $venvDir" -ForegroundColor Yellow
    $recreate = Read-Host "Do you want to recreate it? (y/n)"
    if ($recreate -eq "y" -or $recreate -eq "Y") {
        Write-Host "Removing existing virtual environment..." -ForegroundColor Cyan
        Remove-Item -Path $venvDir -Recurse -Force
    }
    else {
        Write-Host "Using existing virtual environment..." -ForegroundColor Cyan
    }
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path -Path $venvDir)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    & $pythonCommand -m venv $venvDir
    if (-not $?) {
        Write-Host "Error: Failed to create virtual environment." -ForegroundColor Red
        exit 1
    }
    Write-Host "Virtual environment created successfully." -ForegroundColor Green
}

# Determine the activation script
$activateScript = Join-Path -Path $venvDir -ChildPath "Scripts\Activate.ps1"

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
try {
    . $activateScript
}
catch {
    Write-Host "Error: Failed to activate virtual environment." -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Cyan
try {
    pip install --upgrade pip
}
catch {
    Write-Host "Warning: Failed to upgrade pip. Continuing anyway..." -ForegroundColor Yellow
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Cyan
$requirementsFile = Join-Path -Path $projectDir -ChildPath "requirements.txt"
try {
    pip install -r $requirementsFile
    if (-not $?) {
        throw "pip install failed"
    }
}
catch {
    Write-Host "Error: Failed to install dependencies." -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}
Write-Host "Dependencies installed successfully." -ForegroundColor Green

# Install the application in development mode
Write-Host "Installing the application..." -ForegroundColor Cyan
try {
    pip install -e $projectDir
    if (-not $?) {
        throw "pip install failed"
    }
}
catch {
    Write-Host "Error: Failed to install the application." -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}
Write-Host "Application installed successfully." -ForegroundColor Green

# Create run script for PowerShell
Write-Host "Creating run scripts..." -ForegroundColor Cyan
$runPsScript = @"
# Run script for Data Annotation Swiss Knife

# Get the directory of this script
`$scriptDir = `$PSScriptRoot
`$venvDir = Join-Path -Path `$scriptDir -ChildPath "venv"
`$activateScript = Join-Path -Path `$venvDir -ChildPath "Scripts\Activate.ps1"

# Activate virtual environment
. `$activateScript

# Run the application
annotation-toolkit `$args
"@

$runPsPath = Join-Path -Path $projectDir -ChildPath "scripts\run\run.ps1"
$runPsScript | Out-File -FilePath $runPsPath -Encoding utf8

Write-Host "Run scripts created successfully." -ForegroundColor Green

# Print success message
Write-Host ""
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "How to run the application:" -ForegroundColor Cyan
Write-Host ""
Write-Host "In PowerShell:" -ForegroundColor White
Write-Host "  .\run.ps1 gui" -ForegroundColor Yellow -NoNewline
Write-Host " - Launch the graphical user interface"
Write-Host "  .\run.ps1 dict2bullet input.json -o output.md" -ForegroundColor Yellow -NoNewline
Write-Host " - Convert dictionary to bullet list"
Write-Host "  .\run.ps1 jsonvis conversation.json -o output.txt" -ForegroundColor Yellow -NoNewline
Write-Host " - Visualize conversation"
Write-Host ""
Write-Host "Using Command Prompt:" -ForegroundColor White
Write-Host "  run.bat gui" -ForegroundColor Yellow -NoNewline
Write-Host " - Launch the graphical user interface"
Write-Host "  run.bat dict2bullet input.json -o output.md" -ForegroundColor Yellow -NoNewline
Write-Host " - Convert dictionary to bullet list"
Write-Host "  run.bat jsonvis conversation.json -o output.txt" -ForegroundColor Yellow -NoNewline
Write-Host " - Visualize conversation"
Write-Host ""
Write-Host "For more information, see the README.md file or run:" -ForegroundColor White
Write-Host "  .\run.ps1 --help" -ForegroundColor Yellow -NoNewline
Write-Host " (PowerShell)"
Write-Host "  run.bat --help" -ForegroundColor Yellow -NoNewline
Write-Host " (Command Prompt)"
Write-Host ""

# Note about execution policy
Write-Host "Note: If you encounter errors running the PowerShell script, you may need to change the execution policy." -ForegroundColor Yellow
Write-Host "Run PowerShell as Administrator and execute:" -ForegroundColor Yellow
Write-Host "  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor White
Write-Host ""
