# Data Annotation Swiss Knife - User Manual

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Tools Overview](#tools-overview)
5. [Using the GUI](#using-the-gui)
6. [Using the CLI](#using-the-cli)
7. [Python API](#python-api)
8. [Configuration](#configuration)
9. [Advanced Features](#advanced-features)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)
12. [FAQ](#faq)

---

## Overview

The Data Annotation Swiss Knife is a comprehensive toolkit designed to streamline various data annotation tasks. This application integrates multiple annotation tools into a cohesive platform with proper architecture, making it maintainable, extensible, and user-friendly.

### Key Features

- **Multiple Tools in One**: Three powerful tools in a single application
- **Dual Interface**: Both graphical (GUI) and command-line (CLI) interfaces
- **Cross-Platform**: Works on macOS, Linux, and Windows
- **No Admin Rights Required**: Perfect for corporate environments
- **Extensible Architecture**: Easy to add new tools and features
- **Comprehensive Error Handling**: Detailed error messages with actionable suggestions

### Target Audience

This toolkit is designed for:
- Data annotation specialists
- Researchers working with conversational data
- Developers cleaning and formatting text data
- Anyone working with JSON data visualization
- Meta employees working on annotation tasks

---

## Installation

### Prerequisites

- **Python 3.8 or higher** (usually pre-installed on Meta devices)
- **Terminal/Command Prompt access**
- **No administrator privileges required**

### Recommended Installation Method (Using Setup Scripts)

The application comes with automated setup scripts that create a virtual environment and install all dependencies. This is the recommended approach, especially for Meta managed devices.

#### macOS/Linux

1. **Extract the Application**
   ```bash
   cd ~/Downloads  # Navigate to your download location
   unzip annotator_swiss_knife.zip
   cd annotator_swiss_knife
   ```

2. **Run One-Time Setup**
   ```bash
   chmod +x scripts/setup/setup.sh
   ./scripts/setup/setup.sh
   ```

3. **Launch the Application**
   ```bash
   chmod +x scripts/run/run.sh
   ./scripts/run/run.sh gui
   ```

#### Windows

**Using PowerShell (Recommended):**

1. **Extract the Application**
   ```powershell
   cd $env:USERPROFILE\Downloads
   # Extract zip file via right-click → "Extract All"
   cd annotator_swiss_knife
   ```

2. **Allow Script Execution (if needed)**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Run One-Time Setup**
   ```powershell
   .\scripts\setup\setup.ps1
   ```

4. **Launch the Application**
   ```powershell
   .\scripts\run\run.ps1 gui
   ```

**Using Command Prompt:**

1. **Extract and Navigate**
   ```cmd
   cd C:\Users\YourName\Downloads\annotator_swiss_knife
   ```

2. **Run Setup and Launch**
   ```cmd
   scripts\setup\setup.bat
   scripts\run\run.bat gui
   ```

### Manual Installation (Advanced Users)

If you prefer manual installation:

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Package**
   ```bash
   pip install -e .
   ```

3. **Launch**
   ```bash
   annotation-toolkit gui
   ```

### Recommended Directory Structure

For best organization, place the application in one of these locations:

**macOS/Linux:**
- `~/Documents/tools/annotator_swiss_knife/`
- `~/Desktop/annotator_swiss_knife/`
- `~/tools/annotator_swiss_knife/`

**Windows:**
- `C:\Users\YourName\Documents\tools\annotator_swiss_knife\`
- `C:\Users\YourName\Desktop\annotator_swiss_knife\`
- `C:\tools\annotator_swiss_knife\`

---

## Getting Started

### First Launch

After installation, launch the application using the appropriate run script for your platform:

```bash
# macOS/Linux
./scripts/run/run.sh gui

# Windows PowerShell
.\scripts\run\run.ps1 gui

# Windows Command Prompt
scripts\run\run.bat gui
```

### Main Interface

Upon launching, you'll see the main application window with three tool tabs:

1. **Dictionary to Bullet** - Convert dictionaries to formatted lists
2. **Text Cleaner** - Clean and transform text data
3. **JSON Visualizer** - Format and visualize JSON data (including conversation data)

Each tab provides a dedicated interface for its specific functionality.

---

## Tools Overview

### 1. Dictionary to Bullet List

**Purpose**: Converts dictionaries containing URLs into formatted bullet lists with hyperlinks.

**Input**: JSON dictionaries with key-value pairs where values are URLs
**Output**: Formatted bullet lists in Markdown or plain text

**Example Input**:
```json
{
  "1": "https://www.example.com/page1",
  "2": "https://www.example.com/page2",
  "Documentation": "https://docs.example.com"
}
```

**Example Output** (Markdown):
```markdown
• [1](https://www.example.com/page1)
• [2](https://www.example.com/page2)
• [Documentation](https://docs.example.com)
```

### 2. Text Cleaner

**Purpose**: Cleans text from markdown, JSON, and code artifacts, and can transform cleaned text back to code format.

**Key Features**:
- Remove code blocks, backticks, and formatting
- Clean markdown syntax
- Transform text back to code format
- Preserve essential content while removing noise

**Example**:
```
Input:  ```python\nprint('Hello world!')\n```
Output: print('Hello world!')
```

### 3. JSON Visualizer

**Purpose**: Visualizes and formats JSON data with special handling for conversation data, XML tags, and malformed JSON repair.

**Supported Formats**:
- Standard JSON objects and arrays
- Conversation data in multiple formats
- XML tags within JSON strings
- Automatic malformed JSON repair

**Key Features**:
- Pretty-print JSON with proper indentation
- Special formatting for conversation data
- XML tag formatting for better readability
- Search functionality within JSON data

#### 3a. Conversation Data in JSON Visualizer

The JSON Visualizer includes special handling for conversation data formats:

**Supported Conversation Formats**:
1. **Standard Format**: `[{"role": "user", "content": "Hello"}, ...]`
2. **Chat History Format**: `{"chat_history": [{"role": "user", "content": "Hello"}, ...]}`
3. **Message_v2 Format**: `[{"source": "user", "version": "message_v2", "body": "Hello", ...}, ...]`

**Conversation-Specific Features**:
- Role-based formatting and color coding
- Message thread visualization
- Search within conversation content
- Export conversation data to various formats

---

## Using the GUI

### Interface Layout

The GUI features a clean, tabbed interface with each tool in its own tab:

#### Common Elements
- **Input Area**: Text area for pasting or typing input data
- **Output Area**: Display area for processed results
- **Action Buttons**: Process, Clear, Copy, Save functions
- **Status Bar**: Shows processing status and error messages

#### Tool-Specific Features

**Dictionary to Bullet Tab**:
- Format selection (Markdown/Plain Text)
- Color-coded output
- Automatic URL detection and linking

**Text Cleaner Tab**:
- Clean operation
- Transform back to code format
- Format selection for output

**JSON Visualizer Tab**:
- JSON validation and repair
- Pretty-print formatting
- Search functionality
- Export options
- Auto-detection of conversation format
- Role-based color coding for conversation data
- Search within conversations and JSON data

### Basic Workflow

1. **Select Tool**: Click on the appropriate tab
2. **Input Data**: Paste or type your data in the input area
3. **Configure Options**: Set output format, colors, etc.
4. **Process**: Click the "Process" button
5. **Review Output**: Check the formatted result
6. **Export**: Copy to clipboard or save to file

### Keyboard Shortcuts

- `Ctrl+V` / `Cmd+V`: Paste into input area
- `Ctrl+C` / `Cmd+C`: Copy output
- `Ctrl+A` / `Cmd+A`: Select all text
- `Ctrl+Z` / `Cmd+Z`: Undo
- `F5`: Process/Refresh

---

## Using the CLI

The toolkit provides a comprehensive command-line interface for automation and scripting.

### Basic Command Structure

```bash
annotation-toolkit [TOOL] [INPUT_FILE] [OPTIONS]
```

### Available Commands

#### Dictionary to Bullet List

```bash
# Basic usage
annotation-toolkit dict2bullet input.json

# With output file and format
annotation-toolkit dict2bullet input.json --output output.md --format markdown

# With custom colors (GUI only)
annotation-toolkit dict2bullet input.json --color "#4CAF50"
```

#### JSON Visualizer (for JSON data including conversations)

```bash
# Basic formatting
annotation-toolkit jsonvis data.json

# With output file and format
annotation-toolkit jsonvis data.json --output formatted.txt --format text

# Search within JSON/conversation data
annotation-toolkit jsonvis conversation.json --search "hello" --case-sensitive

# Export to markdown
annotation-toolkit jsonvis data.json --output formatted.md --format markdown
```

#### Text Cleaner

```bash
# Clean text
annotation-toolkit textclean input.txt --output cleaned.txt

# Transform back to code format
annotation-toolkit textclean --transform-back cleaned.txt --output code_format.txt --format code

# Process multiple files
annotation-toolkit textclean *.txt --batch-process
```

### CLI Options

#### Global Options
- `--config CONFIG_FILE`: Use custom configuration file
- `--output OUTPUT_FILE`: Specify output file
- `--format FORMAT`: Output format (text/markdown/json)
- `--verbose`: Enable verbose logging
- `--help`: Show help message

#### Tool-Specific Options
- `--search TEXT`: Search for specific text
- `--case-sensitive`: Case-sensitive search
- `--color COLOR`: Set custom color (hex code)
- `--repair`: Attempt to repair malformed data
- `--transform-back`: Transform cleaned text back to code

### Examples

#### Process a Conversation File
```bash
# Convert conversation to readable format
annotation-toolkit jsonvis chat_data.json --output readable_chat.txt --format text

# Search for specific messages
annotation-toolkit jsonvis chat_data.json --search "error" --case-sensitive
```

#### Clean Multiple Text Files
```bash
# Clean all text files in directory
for file in *.txt; do
  annotation-toolkit textclean "$file" --output "cleaned_$file"
done
```

#### Format and Repair JSON
```bash
# Format and repair JSON file
annotation-toolkit jsonvis data.json --repair --output formatted.json --format json
```

---

## Python API

The toolkit can be used as a Python library for integration into other applications.

### Import Statements

```python
from annotation_toolkit.core.text.dict_to_bullet import DictToBulletList
from annotation_toolkit.core.conversation.visualizer import JsonVisualizer
from annotation_toolkit.core.text.text_cleaner import TextCleaner
```

### Dictionary to Bullet List

```python
# Initialize the tool
dict_tool = DictToBulletList(markdown_output=True)

# Process dictionary data
data = {
    "1": "https://www.example.com/page1",
    "2": "https://www.example.com/page2",
    "Documentation": "https://docs.example.com"
}

# Generate formatted output
output = dict_tool.process_dict(data)
print(output)
```

### Text Cleaner

```python
# Initialize text cleaner
cleaner = TextCleaner()

# Clean text with code artifacts
dirty_text = '''Here's some code:
\`\`\`python
print('Hello world!')
\`\`\`
And some **markdown** formatting.'''

# Clean the text
cleaned = cleaner.clean_text(dirty_text)
print("Cleaned:", cleaned)

# Transform back to code format
code_format = cleaner.transform_back(cleaned, "code")
print("Code format:", code_format)
```

### JSON Visualizer

```python
# Initialize JSON visualizer
json_tool = JsonVisualizer(output_format="text")

# Format generic JSON
data = {
    "name": "John Doe",
    "age": 30,
    "city": "New York",
    "preferences": {
        "color": "blue",
        "food": "pizza"
    }
}

output = json_tool.format_generic_json(data)
print(output)

# Handle conversation data specifically
conversation = [
    {"role": "user", "content": "Hello!"},
    {"role": "ai", "content": "Hi there!"}
]

conv_output = json_tool.format_conversation(conversation)
print(conv_output)

# Handle XML tags in JSON
xml_data = {
    "response": "<response>\n    <message>This is a response</message>\n</response>"
}

xml_output = json_tool.format_generic_json(xml_data)
print(xml_output)
```

### Error Handling

```python
from annotation_toolkit.utils.errors import (
    AnnotationToolkitError,
    ProcessingError,
    ValidationError
)

try:
    # Process data
    result = dict_tool.process_dict(invalid_data)
except ValidationError as e:
    print(f"Validation error: {e}")
    print(f"Suggestion: {e.suggestion}")
except ProcessingError as e:
    print(f"Processing error: {e}")
except AnnotationToolkitError as e:
    print(f"General error: {e}")
```

---

## Configuration

The toolkit supports configuration via YAML files for customizing behavior and appearance.

### Default Configuration

```yaml
tools:
  dict_to_bullet:
    enabled: true
    default_color: "#4CAF50"
    markdown_links: true

  conversation_visualizer:
    enabled: true
    default_color: "#2196F3"
    user_message_color: "#0d47a1"
    ai_message_color: "#33691e"
    show_timestamps: false

  text_cleaner:
    enabled: true
    default_color: "#4CAF50"
    preserve_structure: true

  json_visualizer:
    enabled: true
    default_color: "#FF9800"
    user_message_color: "#0d47a1"
    ai_message_color: "#33691e"
    debug_logging: false
    auto_repair: true

ui:
  theme: default
  font_size: 12
  window_size:
    width: 1000
    height: 700
  font_family: "Monospace"

data:
  save_directory: ~/annotation_toolkit_data
  autosave: false
  autosave_interval: 300
  backup_files: true

logging:
  level: INFO
  file: annotation_toolkit.log
  max_size: 10MB
  backup_count: 5
```

### Using Custom Configuration

#### Via Command Line
```bash
annotation-toolkit --config custom_config.yaml gui
```

#### Via Python API
```python
from annotation_toolkit.config import load_config

# Load custom configuration
config = load_config("custom_config.yaml")

# Initialize tool with custom config
dict_tool = DictToBulletList(config=config.tools.dict_to_bullet)
```

### Configuration Options

#### Tool Settings
- `enabled`: Enable/disable specific tools
- `default_color`: Default color for tool output
- `*_message_color`: Colors for different message types
- Tool-specific options (e.g., `markdown_links`, `auto_repair`)

#### UI Settings
- `theme`: Application theme (default/dark/light)
- `font_size`: Interface font size
- `window_size`: Default window dimensions
- `font_family`: Font family for text areas

#### Data Settings
- `save_directory`: Default directory for saved files
- `autosave`: Enable automatic saving
- `autosave_interval`: Autosave interval in seconds
- `backup_files`: Create backup files before overwriting

---

## Advanced Features

### Batch Processing

The toolkit supports batch processing for handling multiple files:

#### CLI Batch Processing
```bash
# Process all JSON files in directory
for file in *.json; do
  annotation-toolkit jsonvis "$file" --output "formatted_$file"
done

# Batch clean text files
find . -name "*.txt" -exec annotation-toolkit textclean {} \;
```

#### Python API Batch Processing
```python
import os
from annotation_toolkit.core.text.text_cleaner import TextCleaner

cleaner = TextCleaner()

# Process all files in directory
input_dir = "input_files"
output_dir = "cleaned_files"

for filename in os.listdir(input_dir):
    if filename.endswith('.txt'):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, f"cleaned_{filename}")

        with open(input_path, 'r') as f:
            content = f.read()

        cleaned = cleaner.clean_text(content)

        with open(output_path, 'w') as f:
            f.write(cleaned)
```

### Search and Filter

#### Search in JSON/Conversation Data
```python
json_tool = JsonVisualizer()

# Search within conversation data
conversation = [
    {"role": "user", "content": "Hello, how are you?"},
    {"role": "ai", "content": "Hi there! I'm doing well."},
    {"role": "user", "content": "What's the weather like?"}
]

# Basic search
results = json_tool.search_conversation(conversation, "weather")

# Case-sensitive search
results = json_tool.search_conversation(
    conversation,
    "Hello",
    case_sensitive=True
)
```

#### Filter JSON Data
```python
json_tool = JsonVisualizer()

# Filter conversation by role
user_messages = json_tool.filter_by_role(conversation, "user")
ai_messages = json_tool.filter_by_role(conversation, "ai")

# Filter by content length
short_messages = json_tool.filter_by_length(conversation, max_length=100)
```

### Custom Output Formats

#### Create Custom Formatters
```python
from annotation_toolkit.core.base import BaseFormatter

class CustomFormatter(BaseFormatter):
    def format_data(self, data, **kwargs):
        # Custom formatting logic
        formatted = self._apply_custom_format(data)
        return formatted

    def _apply_custom_format(self, data):
        # Implementation details
        pass

# Use custom formatter
formatter = CustomFormatter()
output = formatter.format_data(my_data)
```

### Integration with External Tools

#### Export to Different Formats
```python
# Export conversation to CSV
import csv

def export_conversation_to_csv(conversation, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['role', 'content', 'timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for message in conversation:
            writer.writerow({
                'role': message.get('role', ''),
                'content': message.get('content', ''),
                'timestamp': message.get('timestamp', '')
            })

# Export JSON to Excel
import pandas as pd

def json_to_excel(json_data, filename):
    df = pd.DataFrame(json_data)
    df.to_excel(filename, index=False)
```

---

## Troubleshooting

### Common Issues and Solutions

#### Installation Issues

**Python Not Found**
```bash
# Try different Python commands
python --version
python3 --version
py --version  # Windows
```

**Virtual Environment Issues**
```bash
# Manual virtual environment creation
python -m venv annotation_toolkit_env
# Windows
annotation_toolkit_env\Scripts\activate
# macOS/Linux
source annotation_toolkit_env/bin/activate
```

**Permission Denied (macOS/Linux)**
```bash
# Make scripts executable
chmod +x scripts/setup/setup.sh
chmod +x scripts/run/run.sh
```

**PowerShell Execution Policy (Windows)**
```powershell
# Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Runtime Issues

**GUI Won't Start**
- Ensure you're using the `gui` command
- Check if PyQt5 is properly installed
- Try running from command line to see error messages

**Import Errors**
- Verify virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version compatibility

**Memory Issues with Large Files**
- Process files in smaller chunks
- Use CLI for large batch operations
- Increase system memory allocation

#### Data Processing Issues

**JSON Parsing Errors**
```python
# Enable JSON repair
json_tool = JsonVisualizer(auto_repair=True)

# Manual repair
try:
    parsed = json_tool.parse_json(malformed_json)
except json.JSONDecodeError:
    repaired = json_tool.repair_json(malformed_json)
    parsed = json.loads(repaired)
```

**Text Encoding Issues**
```python
# Specify encoding when reading files
with open(filename, 'r', encoding='utf-8') as f:
    content = f.read()
```

**Conversation Format Not Recognized**
- Check if conversation follows supported formats
- Use the JSON Visualizer to inspect data structure
- Convert to supported format if necessary

### Debugging Tips

#### Enable Verbose Logging
```bash
# CLI with verbose output
annotation-toolkit --verbose jsonvis data.json

# Python API with debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Check Configuration
```python
# Verify configuration loading
from annotation_toolkit.config import get_config

config = get_config()
print(config)
```

#### Test with Sample Data
```python
# Use minimal test data
test_conversation = [
    {"role": "user", "content": "test"},
    {"role": "ai", "content": "response"}
]

json_tool = JsonVisualizer()
result = json_tool.format_conversation(test_conversation)
print(result)
```

### Performance Optimization

#### For Large Files
- Use CLI for better memory management
- Process files in batches
- Use streaming for very large datasets

#### For Frequent Use
- Keep virtual environment activated
- Use Python API for repeated operations
- Cache processed results when possible

---

## Best Practices

### File Organization

#### Recommended Directory Structure
```
~/annotation_work/
├── input/           # Raw input files
├── output/          # Processed output
├── config/          # Custom configurations
├── scripts/         # Custom automation scripts
└── backups/         # File backups
```

#### Naming Conventions
- Use descriptive filenames: `conversation_data_2024_01_15.json`
- Include date stamps for version control
- Separate input and output clearly
- Use consistent extensions (`.json`, `.txt`, `.md`)

### Data Handling

#### Before Processing
- **Validate data format** using JSON validators
- **Create backups** of important files
- **Check file encoding** (prefer UTF-8)
- **Review data size** for memory considerations

#### During Processing
- **Start with small samples** to test formatting
- **Monitor system resources** for large files
- **Use appropriate output formats** for your needs
- **Verify results** before bulk processing

#### After Processing
- **Review output quality** before proceeding
- **Save configurations** that work well
- **Document any custom modifications**
- **Archive completed work** properly

### Security Considerations

#### Data Privacy
- **Never include sensitive data** in configuration files
- **Use secure directories** for temporary files
- **Clear clipboard** after copying sensitive data
- **Review output** before sharing

#### File Permissions
- **Set appropriate permissions** on output files
- **Use secure temporary directories**
- **Clean up temporary files** after processing

### Performance Tips

#### Memory Management
- **Process large files** in chunks when possible
- **Use CLI for batch operations**
- **Close unused applications** when processing large datasets
- **Monitor system resources**

#### Speed Optimization
- **Use SSD storage** when possible
- **Keep files local** rather than network drives
- **Use appropriate batch sizes**
- **Leverage parallel processing** for independent files

### Quality Assurance

#### Validation Checklist
- [ ] Input data format is correct
- [ ] Output format meets requirements
- [ ] All necessary fields are preserved
- [ ] Character encoding is maintained
- [ ] File sizes are reasonable
- [ ] No data corruption occurred

#### Testing Approach
1. **Start small**: Test with minimal datasets
2. **Validate output**: Check formatting and completeness
3. **Scale gradually**: Increase file sizes progressively
4. **Document issues**: Keep track of problems and solutions
5. **Create standards**: Establish consistent processes

---

## FAQ

### General Questions

**Q: What is the Data Annotation Swiss Knife?**
A: It's a comprehensive toolkit that integrates three different annotation tools into a single application: Dictionary to Bullet List, Text Cleaner, and JSON Visualizer (which includes conversation data handling).

**Q: Do I need administrator rights to install it?**
A: No, the application runs entirely from source code and doesn't require installation or admin privileges, making it perfect for corporate environments.

**Q: What platforms are supported?**
A: The toolkit works on macOS, Linux, and Windows with Python 3.8 or higher.

**Q: Can I use it without the GUI?**
A: Yes, there's a comprehensive command-line interface (CLI) for all tools.

### Installation and Setup

**Q: The setup script fails on my machine. What should I do?**
A: Try the manual installation method:
1. Create a virtual environment: `python -m venv venv`
2. Activate it: `source venv/bin/activate` (Unix) or `venv\Scripts\activate` (Windows)
3. Install: `pip install -e .`

**Q: How do I update to a newer version?**
A: Simply replace the application folder with the new version and re-run the setup script to update dependencies.

**Q: Can I run multiple instances simultaneously?**
A: Yes, you can run multiple instances, but be careful with file access conflicts when processing the same files.

### Usage Questions

**Q: What conversation formats are supported?**
A: The toolkit supports three main formats:
1. Standard: `[{"role": "user", "content": "message"}, ...]`
2. Chat history: `{"chat_history": [{"role": "user", "content": "message"}, ...]}`
3. Message_v2: `[{"source": "user", "version": "message_v2", "body": "message", ...}, ...]`

**Q: Can I process multiple files at once?**
A: Yes, use the CLI with bash loops or the Python API for batch processing.

**Q: How do I handle very large files?**
A: Use the CLI interface for better memory management, or process files in smaller chunks using the Python API.

**Q: Can I customize the output format?**
A: Yes, the toolkit supports multiple output formats (text, markdown, JSON) and allows configuration of colors and styling.

### Technical Questions

**Q: How do I integrate the toolkit into my own Python application?**
A: Import the required classes and use the Python API:
```python
from annotation_toolkit.core.text.dict_to_bullet import DictToBulletList
dict_tool = DictToBulletList()
result = dict_tool.process_dict(data)
```

**Q: Can I add custom tools to the toolkit?**
A: Yes, the architecture is extensible. Create new classes inheriting from the base classes and register them in the application.

**Q: How do I configure logging?**
A: Use the configuration file to set logging levels and output files, or configure Python logging directly in your code.

**Q: Is there an API rate limit or file size limit?**
A: No artificial limits are imposed, but performance depends on system resources. Very large files may require CLI processing.

### Troubleshooting

**Q: The GUI shows "Tool not available" errors.**
A: Check your configuration file to ensure all tools are enabled, and verify that all dependencies are installed correctly.

**Q: I'm getting encoding errors when processing files.**
A: Ensure your files are in UTF-8 encoding. You can convert them using text editors or command-line tools.

**Q: The application is running slowly.**
A: Try using the CLI for large files, processing in smaller batches, or closing other applications to free up system resources.

**Q: How do I report bugs or request features?**
A: Contact the development team or check if there's a GitHub repository or internal issue tracking system for the project.

### Advanced Usage

**Q: Can I automate the toolkit with scripts?**
A: Absolutely! Use the CLI interface in bash scripts, PowerShell scripts, or Python automation scripts.

**Q: How do I preserve my custom configurations?**
A: Save your configuration files in a dedicated directory and specify them using the `--config` parameter.

**Q: Can I use the toolkit in a Docker container?**
A: Yes, but ensure the container has Python 3.8+, PyQt5 for GUI (if needed), and proper X11 forwarding for GUI applications.

**Q: Is there a way to validate data before processing?**
A: Yes, the toolkit includes comprehensive error handling and validation. You can also use the JSON Visualizer's repair functionality for malformed data.

---

*This manual covers the comprehensive functionality of the Data Annotation Swiss Knife. For additional support, please refer to the troubleshooting section or contact the development team.*
