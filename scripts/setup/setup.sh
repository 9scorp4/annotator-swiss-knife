#!/bin/bash
# Setup script for Data Annotation Swiss Knife
# This script creates a virtual environment and installs the application

# Text formatting
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print header
echo -e "${BOLD}=========================================${NC}"
echo -e "${BOLD}Data Annotation Swiss Knife Setup Script${NC}"
echo -e "${BOLD}=========================================${NC}"
echo ""

# Check if Python 3.8+ is installed
echo -e "${BOLD}Checking Python version...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}Error: Python 3.8 or higher is required but not found.${NC}"
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "${RED}Error: Python 3.8 or higher is required.${NC}"
    echo "Found Python $PYTHON_VERSION"
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

echo -e "${GREEN}Found Python $PYTHON_VERSION${NC}"

# Determine the virtual environment directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/../.." &> /dev/null && pwd )"
VENV_DIR="$PROJECT_DIR/venv"

# Check if virtual environment already exists
if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Virtual environment already exists at $VENV_DIR${NC}"
    read -p "Do you want to recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BOLD}Removing existing virtual environment...${NC}"
        rm -rf "$VENV_DIR"
    else
        echo -e "${BOLD}Using existing virtual environment...${NC}"
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${BOLD}Creating virtual environment...${NC}"
    $PYTHON_CMD -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to create virtual environment.${NC}"
        exit 1
    fi
    echo -e "${GREEN}Virtual environment created successfully.${NC}"
fi

# Determine the activation script based on OS
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    ACTIVATE_SCRIPT="$VENV_DIR/Scripts/activate"
else
    ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"
fi

# Activate virtual environment
echo -e "${BOLD}Activating virtual environment...${NC}"
source "$ACTIVATE_SCRIPT"
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to activate virtual environment.${NC}"
    exit 1
fi

# Upgrade pip
echo -e "${BOLD}Upgrading pip...${NC}"
pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Warning: Failed to upgrade pip. Continuing anyway...${NC}"
fi

# Install dependencies
echo -e "${BOLD}Installing dependencies...${NC}"
pip install -r "$PROJECT_DIR/requirements.txt"
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to install dependencies.${NC}"
    exit 1
fi
echo -e "${GREEN}Dependencies installed successfully.${NC}"

# Install the application in development mode
echo -e "${BOLD}Installing the application...${NC}"
pip install -e "$PROJECT_DIR"
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to install the application.${NC}"
    exit 1
fi
echo -e "${GREEN}Application installed successfully.${NC}"

# Create run scripts
echo -e "${BOLD}Creating run scripts...${NC}"

# Create run script for Unix-like systems (Linux, macOS)
cat > "$PROJECT_DIR/scripts/run/run.sh" << 'EOF'
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
EOF
chmod +x "$PROJECT_DIR/scripts/run/run.sh"

# Create run script for Windows
cat > "$PROJECT_DIR/scripts/run/run.bat" << 'EOF'
@echo off
REM Run script for Data Annotation Swiss Knife

setlocal enabledelayedexpansion

REM Get the directory of this script and project root
SET SCRIPT_DIR=%~dp0
SET PROJECT_ROOT=%SCRIPT_DIR%..\..
SET VENV_DIR=%PROJECT_ROOT%\venv
SET ACTIVATE_SCRIPT=%VENV_DIR%\Scripts\activate.bat

REM Check if virtual environment exists
if not exist "%VENV_DIR%" (
    echo ERROR: Virtual environment not found at %VENV_DIR%
    echo Please run the setup script first:
    echo   scripts\setup\setup.bat
    exit /b 1
)

REM Check if activation script exists
if not exist "%ACTIVATE_SCRIPT%" (
    echo ERROR: Virtual environment activation script not found at %ACTIVATE_SCRIPT%
    echo Please run the setup script to recreate the virtual environment:
    echo   scripts\setup\setup.bat
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call "%ACTIVATE_SCRIPT%"
if !errorlevel! neq 0 (
    echo ERROR: Failed to activate virtual environment
    echo Please run the setup script to recreate the virtual environment:
    echo   scripts\setup\setup.bat
    exit /b 1
)

REM Check if annotation-toolkit command is available
where annotation-toolkit >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: annotation-toolkit command not found
    echo Please run the setup script to install the application:
    echo   scripts\setup\setup.bat
    exit /b 1
)

REM Run the application
echo Running annotation-toolkit...
annotation-toolkit %*
EOF

echo -e "${GREEN}Run scripts created successfully.${NC}"

# Print success message
echo ""
echo -e "${BOLD}${GREEN}Setup completed successfully!${NC}"
echo ""
echo -e "${BOLD}How to run the application:${NC}"
echo ""
echo -e "On Linux/macOS:"
echo -e "  ${YELLOW}./run.sh gui${NC} - Launch the graphical user interface"
echo -e "  ${YELLOW}./run.sh dict2bullet input.json -o output.md${NC} - Convert dictionary to bullet list"
echo -e "  ${YELLOW}./run.sh jsonvis conversation.json -o output.txt${NC} - Visualize conversation"
echo ""
echo -e "On Windows:"
echo -e "  ${YELLOW}run.bat gui${NC} - Launch the graphical user interface"
echo -e "  ${YELLOW}run.bat dict2bullet input.json -o output.md${NC} - Convert dictionary to bullet list"
echo -e "  ${YELLOW}run.bat jsonvis conversation.json -o output.txt${NC} - Visualize conversation"
echo ""
echo -e "For more information, see the README.md file or run:"
echo -e "  ${YELLOW}./run.sh --help${NC} (Linux/macOS)"
echo -e "  ${YELLOW}run.bat --help${NC} (Windows)"
echo ""
