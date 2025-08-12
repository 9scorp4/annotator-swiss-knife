# Run script for Data Annotation Swiss Knife

param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
)

# Text formatting
$Green = "`e[32m"
$Red = "`e[31m"
$Yellow = "`e[33m"
$Reset = "`e[0m"

# Get script directory and project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)
$venvDir = Join-Path $projectRoot "venv"
$activateScript = Join-Path $venvDir "Scripts\Activate.ps1"

# Check if virtual environment exists
if (-not (Test-Path $venvDir)) {
    Write-Host "${Red}ERROR: Virtual environment not found at $venvDir${Reset}"
    Write-Host "${Yellow}Please run the setup script first:${Reset}"
    Write-Host "  scripts\setup\setup.bat"
    Write-Host "  or"
    Write-Host "  scripts\setup\setup.ps1"
    exit 1
}

# Check if activation script exists
if (-not (Test-Path $activateScript)) {
    Write-Host "${Red}ERROR: Virtual environment activation script not found at $activateScript${Reset}"
    Write-Host "${Yellow}Please run the setup script to recreate the virtual environment:${Reset}"
    Write-Host "  scripts\setup\setup.bat"
    Write-Host "  or"
    Write-Host "  scripts\setup\setup.ps1"
    exit 1
}

# Activate virtual environment
Write-Host "${Green}Activating virtual environment...${Reset}"
try {
    & $activateScript
} catch {
    Write-Host "${Yellow}Enabling PowerShell script execution...${Reset}"
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    & $activateScript
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "${Red}ERROR: Failed to activate virtual environment${Reset}"
    Write-Host "${Yellow}Please run the setup script to recreate the virtual environment:${Reset}"
    Write-Host "  scripts\setup\setup.bat"
    Write-Host "  or"
    Write-Host "  scripts\setup\setup.ps1"
    exit 1
}

# Check if annotation-toolkit command is available
try {
    Get-Command annotation-toolkit -ErrorAction Stop | Out-Null
} catch {
    Write-Host "${Red}ERROR: annotation-toolkit command not found${Reset}"
    Write-Host "${Yellow}Please run the setup script to install the application:${Reset}"
    Write-Host "  scripts\setup\setup.bat"
    Write-Host "  or"
    Write-Host "  scripts\setup\setup.ps1"
    exit 1
}

# Run the application
Write-Host "${Green}Running annotation-toolkit...${Reset}"
& annotation-toolkit @Arguments
