#!/bin/bash
# Run script for Data Annotation Swiss Knife

set -e  # Exit on any error

# Text formatting for better user experience
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Get the directory of this script and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." &> /dev/null && pwd )"
VENV_DIR="$PROJECT_ROOT/venv"

# Determine the activation script based on OS
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    ACTIVATE_SCRIPT="$VENV_DIR/Scripts/activate"
else
    ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"
fi

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}Error: Virtual environment not found at $VENV_DIR${NC}"
    echo -e "${YELLOW}Please run the setup script first:${NC}"
    echo -e "  ./scripts/setup/setup.sh"
    exit 1
fi

# Check if activation script exists
if [ ! -f "$ACTIVATE_SCRIPT" ]; then
    echo -e "${RED}Error: Virtual environment activation script not found at $ACTIVATE_SCRIPT${NC}"
    echo -e "${YELLOW}Please run the setup script to recreate the virtual environment:${NC}"
    echo -e "  ./scripts/setup/setup.sh"
    exit 1
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source "$ACTIVATE_SCRIPT"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to activate virtual environment${NC}"
    echo -e "${YELLOW}Please run the setup script to recreate the virtual environment:${NC}"
    echo -e "  ./scripts/setup/setup.sh"
    exit 1
fi

# Check if annotation-toolkit command is available
if ! command -v annotation-toolkit &> /dev/null; then
    echo -e "${RED}Error: annotation-toolkit command not found${NC}"
    echo -e "${YELLOW}Please run the setup script to install the application:${NC}"
    echo -e "  ./scripts/setup/setup.sh"
    exit 1
fi

# Run the application
echo -e "${GREEN}Running annotation-toolkit...${NC}"
annotation-toolkit "$@"
