#!/bin/bash
# Run script for Data Annotation Swiss Knife

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/../.." &> /dev/null && pwd )"

# Check if we're running from a distribution or development environment
if [ -d "$PROJECT_DIR/dist/AnnotationToolkit.app" ]; then
    echo "Running from distribution..."
    # Launch the application directly
    "$PROJECT_DIR/dist/AnnotationToolkit.app/Contents/MacOS/AnnotationToolkit" "$@"
else
    echo "Running from development environment..."
    # Check if virtual environment exists
    VENV_DIR="$PROJECT_DIR/venv"
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"

        echo "Installing requirements..."
        source "$VENV_DIR/bin/activate"
        pip install -r "$PROJECT_DIR/requirements.txt"
        pip install -e "$PROJECT_DIR"
    else
        echo "Activating virtual environment..."
        source "$VENV_DIR/bin/activate"
    fi

    # Run the application
    annotation-toolkit "$@"
fi
