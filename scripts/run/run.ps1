# Run script for Data Annotation Swiss Knife

# Get the directory of this script
$scriptDir = $PSScriptRoot
$projectDir = (Get-Item $scriptDir).Parent.Parent.FullName
$venvDir = Join-Path -Path $projectDir -ChildPath "venv"
$activateScript = Join-Path -Path $venvDir -ChildPath "Scripts\Activate.ps1"

# Activate virtual environment
. $activateScript

# Run the application
annotation-toolkit $args
