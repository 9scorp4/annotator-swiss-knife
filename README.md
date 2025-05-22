# Data Annotation Swiss Knife

A comprehensive yet simple toolkit designed to streamline various data annotation tasks. This toolkit integrates multiple annotation tools into a cohesive application with proper architecture, making it more maintainable, extensible, and user-friendly.

## Features

* **Dictionary to Bullet List**: Convert dictionaries with URLs to formatted bullet lists with hyperlinks
* **Text Cleaner**: Clean text from markdown/JSON/code artifacts and transform cleaned text back to code format
* **JSON Visualizer**: Visualize and format JSON data with special handling for conversation data, XML tags, and malformed JSON repair

## Installation

### Using Setup Scripts (Recommended for Non-Technical Users)

This application comes with setup scripts that automate the installation process, including creating a virtual environment and installing all dependencies.

#### On macOS/Linux:

1. Open Terminal
2. Navigate to the application directory:
   ```bash
   cd path/to/annotator_swiss_knife
   ```
3. Make the setup script executable:
   ```bash
   chmod +x scripts/setup/setup.sh
   ```
4. Run the setup script:
   ```bash
   ./scripts/setup/setup.sh
   ```
5. Follow the on-screen instructions

#### On Windows:

**Using PowerShell (Recommended):**

1. Open PowerShell
2. Navigate to the application directory:
   ```powershell
   cd path\to\annotator_swiss_knife
   ```
3. If you haven't already, you may need to allow script execution:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
4. Run the setup script:
   ```powershell
   .\scripts\setup\setup.ps1
   ```
5. Follow the on-screen instructions

**Using Command Prompt:**

1. Open Command Prompt
2. Navigate to the application directory:
   ```cmd
   cd path\to\annotator_swiss_knife
   ```
3. Run the batch script:
   ```cmd
   scripts\setup\setup.bat
   ```
4. Follow the on-screen instructions

### Running the Application After Setup

After running the setup script, you can use the provided run scripts to launch the application:

#### On macOS/Linux:
```bash
./scripts/run/run.sh gui  # Launch the GUI
./scripts/run/run.sh --help  # Show all available commands
```

#### On Windows (PowerShell):
```powershell
.\scripts\run\run.ps1 gui  # Launch the GUI
.\scripts\run\run.ps1 --help  # Show all available commands
```

#### On Windows (Command Prompt):
```cmd
scripts\run\run.bat gui  # Launch the GUI
scripts\run\run.bat --help  # Show all available commands
```

### From Source (Manual Installation)

If you prefer to set up the application manually:

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install the package in development mode:
   ```bash
   pip install -e .
   ```

### Requirements

* Python 3.8 or higher
* PyQt5 (for GUI)
* PyYAML (for configuration)
* Markdown (for formatting)

## Usage

### Graphical User Interface

To launch the graphical user interface:

```bash
annotation-toolkit gui
```

### Command Line Interface

The toolkit provides a command-line interface for each tool:

#### Dictionary to Bullet List

```bash
annotation-toolkit dict2bullet input.json --output output.md --format markdown
```

#### Conversation Visualizer

```bash
annotation-toolkit convvis conversation.json --output formatted.txt --format text
```

To search for specific text in a conversation:

```bash
annotation-toolkit convvis conversation.json --search "hello" --case-sensitive
```

The Conversation Visualizer supports multiple JSON formats:
1. Standard format: `[{"role": "user", "content": "Hello"}, ...]`
2. Chat history format: `{"chat_history": [{"role": "user", "content": "Hello"}, ...]}`
3. Message_v2 format: `[{"source": "user", "version": "message_v2", "body": "Hello", ...}, ...]`

#### Text Cleaner

```bash
annotation-toolkit textclean input.txt --output cleaned.txt
```

To transform cleaned text back to code format:

```bash
annotation-toolkit textclean --transform-back cleaned.txt --output code_format.txt --format code
```

#### JSON Visualizer

```bash
annotation-toolkit jsonvis data.json --output formatted.txt --format text
```

To search for specific content in JSON data:

```bash
annotation-toolkit jsonvis data.json --search "query" --case-sensitive
```

The JSON Visualizer supports multiple data formats:
1. Standard JSON objects and arrays
2. Conversation data in various formats:
   - Standard format: `[{"role": "user", "content": "Hello"}, ...]`
   - Chat history format: `{"chat_history": [{"role": "user", "content": "Hello"}, ...]}`
   - Message_v2 format: `[{"source": "user", "version": "message_v2", "body": "Hello", ...}, ...]`
3. Special handling for XML tags in JSON strings, formatting them for better readability
4. Automatic repair of common JSON formatting issues

### Python API

You can also use the toolkit as a Python library:

```python
from annotation_toolkit.core.text.dict_to_bullet import DictToBulletList
from annotation_toolkit.core.conversation.visualizer import ConversationVisualizer
from annotation_toolkit.core.text.text_cleaner import TextCleaner
from annotation_toolkit.core.conversation.visualizer import JsonVisualizer

# Dictionary to Bullet List
dict_tool = DictToBulletList(markdown_output=True)
output = dict_tool.process_dict({
    "1": "https://www.example.com/page1",
    "2": "https://www.example.com/page2"
})
print(output)

# Conversation Visualizer
conv_tool = ConversationVisualizer(output_format="markdown")
conversation = [
    {"role": "user", "content": "Hello!"},
    {"role": "ai", "content": "Hi there!"}
]
output = conv_tool.format_conversation(conversation)
print(output)

# Text Cleaner
cleaner = TextCleaner()
cleaned_text = cleaner.clean_text("```python\nprint('Hello world!')\n```")
print(cleaned_text)
# Transform back to code format
code_format = cleaner.transform_back(cleaned_text, "code")
print(code_format)

# JSON Visualizer
json_tool = JsonVisualizer(output_format="text")
json_data = {"name": "John", "age": 30, "city": "New York"}
output = json_tool.format_generic_json(json_data)
print(output)

# For conversation data
conversation = [
    {"role": "user", "content": "Hello!"},
    {"role": "ai", "content": "Hi there!"}
]
output = json_tool.format_conversation(conversation)
print(output)

# For XML tags in JSON
json_data = {"message": "<response>\n    This is a response\n</response>"}
output = json_tool.format_generic_json(json_data)
print(output)
```

## Configuration

The toolkit can be configured using a YAML file:

```yaml
tools:
  dict_to_bullet:
    enabled: true
    default_color: "#4CAF50"
  conversation_visualizer:
    enabled: true
    default_color: "#2196F3"
    user_message_color: "#0d47a1"
    ai_message_color: "#33691e"
  text_cleaner:
    enabled: true
    default_color: "#4CAF50"
  json_visualizer:
    enabled: true
    default_color: "#FF9800"
    user_message_color: "#0d47a1"
    ai_message_color: "#33691e"
    debug_logging: false
ui:
  theme: default
  font_size: 12
  window_size:
    width: 1000
    height: 700
data:
  save_directory: ~/annotation_toolkit_data
  autosave: false
  autosave_interval: 300
```

To use a custom configuration file:

```bash
annotation-toolkit --config config.yaml gui
```

## Building Standalone Executables

For instructions on building standalone executables for macOS and Windows, see the [README_BUILD.md](README_BUILD.md) file.

## Repository Structure

```
annotator_swiss_knife/
├── annotation_toolkit/       # Main package source code
├── scripts/                  # Scripts for building, running, and setting up
│   ├── build/                # Build scripts for creating executables
│   ├── run/                  # Scripts for running the application
│   └── setup/                # Scripts for setting up the environment
├── tests/                    # Test suite
├── .gitignore                # Git ignore file
├── README.md                 # Main documentation
├── README_BUILD.md           # Build instructions
├── requirements.txt          # Package dependencies
└── setup.py                  # Package setup script
```

## Extending the Toolkit

The toolkit is designed to be easily extensible. To add a new annotation tool:

1. Create a new class that inherits from one of the base classes in `annotation_toolkit.core.base`
2. Implement the required methods
3. Add UI components for your tool
4. Register your tool in the main application

See the existing tools for examples.

## License

WIP

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
