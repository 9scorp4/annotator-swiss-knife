#!/bin/bash
# Run script for Data Annotation Swiss Knife

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." &> /dev/null && pwd )"
VENV_DIR="$PROJECT_ROOT/venv"
ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"

# Activate virtual environment
source "$ACTIVATE_SCRIPT"

# Run the application
annotation-toolkit "$@"
