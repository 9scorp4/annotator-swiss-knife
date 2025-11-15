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

- **Multiple Tools in One**: Five powerful tools in a single application
- **Dual Interface**: Both graphical (GUI) and command-line (CLI) interfaces
- **Cross-Platform**: Works on macOS, Linux, and Windows
- **No Admin Rights Required**: Perfect for corporate environments
- **Advanced Infrastructure**: Performance profiling, streaming, validation, error recovery, and security features
- **Extensible Architecture**: Easy to add new tools and features
- **Comprehensive Error Handling**: Detailed error messages with actionable suggestions

### Target Audience

This toolkit is designed for:
- Data annotation specialists
- Researchers working with conversational data
- Developers cleaning and formatting text data
- Anyone working with JSON data visualization
- Teams working on annotation tasks

---

## Installation

### Prerequisites

- **Python 3.8 or higher** (usually pre-installed on managed devices)
- **Terminal/Command Prompt access**
- **No administrator privileges required**

### Recommended Installation Method (Using Setup Scripts)

The application comes with automated setup scripts that create a virtual environment and install all dependencies. This is the recommended approach, especially for corporate managed devices.

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

Upon launching, you'll see the main application window with four tool tabs:

1. **Dictionary to Bullet** - Convert dictionaries to formatted lists
2. **Text Cleaner** - Clean and transform text data
3. **JSON Visualizer** - Format and visualize JSON data (including conversation data)
4. **Conversation Generator** - Build AI conversation JSON data turn-by-turn

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

### 3. Conversation Generator

**Purpose**: Build AI conversation JSON data by adding conversation turns (user message + assistant response pairs).

**Input**: Either a JSON file with turn pairs, or programmatic turn-by-turn building
**Output**: Properly formatted conversation JSON array

**Key Features**:
- Add up to 20 conversation turns (configurable)
- Validate user and assistant messages
- Load from and save to JSON format
- Generate pretty-printed or compact JSON
- Manage conversation turns (add, remove, clear)

**Example Input** (JSON file):
```json
{
  "turns": [
    {"user": "Hello, how are you?", "assistant": "I'm doing well, thank you!"},
    {"user": "What's the weather like?", "assistant": "I don't have access to weather information."}
  ]
}
```

**Example Output**:
```json
[
  {"role": "user", "content": "Hello, how are you?"},
  {"role": "assistant", "content": "I'm doing well, thank you!"},
  {"role": "user", "content": "What's the weather like?"},
  {"role": "assistant", "content": "I don't have access to weather information."}
]
```

**Use Cases**:
- Creating training data for AI models
- Building conversation datasets for annotation
- Testing conversational interfaces
- Generating synthetic dialogue data

### 4. Text Collector

**Purpose**: Collect text from multiple input fields and output them as a JSON list, automatically filtering out empty or whitespace-only strings.

**Input**: Text file with one item per line (CLI) or multiple text input fields (GUI)
**Output**: JSON array of collected text items

**Key Features**:
- Support for up to 20 text fields (configurable)
- Automatic filtering of empty and whitespace-only entries
- Whitespace trimming from collected text
- Dynamic field addition/removal in GUI
- Pretty-printed or compact JSON output

**Example Input** (text file):
```
First item
Second item

Third item

Fourth item
```

**Example Output**:
```json
[
  "First item",
  "Second item",
  "Third item",
  "Fourth item"
]
```

**Use Cases**:
- Collecting keywords or tags for annotation
- Building lists from multi-line text input
- Preparing data for bulk JSON operations
- Creating arrays from separated text entries

### 5. JSON Visualizer

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

#### 4a. Conversation Data in JSON Visualizer

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

#### Conversation Generator

```bash
# Generate conversation from turn pairs
annotation-toolkit convgen input.json --output conversation.json --format pretty

# Generate compact JSON (no indentation)
annotation-toolkit convgen input.json --output conversation.json --format compact

# Output to stdout
annotation-toolkit convgen input.json
```

**Input File Format**:
```json
{
  "turns": [
    {"user": "User message 1", "assistant": "Assistant response 1"},
    {"user": "User message 2", "assistant": "Assistant response 2"}
  ]
}
```

**Features**:
- Supports up to 20 conversation turns (configurable)
- Validates all messages are non-empty
- Proper role assignment (user/assistant)
- Pretty-printed or compact output format

#### Text Collector

```bash
# Basic usage (print to stdout)
annotation-toolkit textcollect items.txt

# Save to file with pretty formatting
annotation-toolkit textcollect items.txt --output collection.json --format pretty

# Generate compact JSON
annotation-toolkit textcollect items.txt --output collection.json --format compact
```

**Input File Format**: Plain text file with one item per line. Empty lines and whitespace-only lines are automatically filtered out.

Example input file (`items.txt`):
```
First item
Second item

Third item

```

**Features**:
- Automatic empty line filtering
- Whitespace trimming
- Support for up to 20 items (configurable)
- Pretty-printed or compact JSON output
- UTF-8 encoding support

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
from annotation_toolkit.core.conversation.generator import ConversationGenerator
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

### Conversation Generator

```python
# Initialize conversation generator
conv_gen = ConversationGenerator(max_turns=20)

# Build conversation turn by turn
conv_gen.add_turn(
    "Hello, how are you?",
    "I'm doing well, thank you for asking!"
)

conv_gen.add_turn(
    "What can you help me with?",
    "I can assist with various tasks including answering questions and providing information."
)

# Generate JSON output
json_output = conv_gen.generate_json(pretty=True)
print("Generated conversation:")
print(json_output)

# Check turn count and capacity
print(f"Current turns: {conv_gen.get_turn_count()}")
print(f"Can add more turns: {conv_gen.can_add_turn()}")

# Get specific turn
turn_0 = conv_gen.get_turn(0)
if turn_0:
    user_msg, assistant_msg = turn_0
    print(f"Turn 0 - User: {user_msg}")
    print(f"Turn 0 - Assistant: {assistant_msg}")

# Load conversation from JSON
existing_conversation = [
    {"role": "user", "content": "Hi!"},
    {"role": "assistant", "content": "Hello!"},
    {"role": "user", "content": "How's the weather?"},
    {"role": "assistant", "content": "I don't have weather data."}
]

conv_gen.load_from_json(existing_conversation)
print(f"Loaded {conv_gen.get_turn_count()} turns")

# Generate compact JSON
compact_json = conv_gen.generate_json(pretty=False)
print("Compact JSON:", compact_json)

# Clear conversation
conv_gen.clear()
print(f"After clear: {conv_gen.get_turn_count()} turns")

# Remove a specific turn
conv_gen.add_turn("Turn 1", "Response 1")
conv_gen.add_turn("Turn 2", "Response 2")
conv_gen.add_turn("Turn 3", "Response 3")
conv_gen.remove_turn(1)  # Remove turn at index 1
print(f"After removing turn 1: {conv_gen.get_turn_count()} turns")
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

  conversation_generator:
    enabled: true
    max_turns: 20
    default_color: "#9C27B0"

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

### Performance Profiling

The toolkit includes comprehensive performance profiling capabilities to monitor and optimize operations.

#### Using Performance Profilers

```python
from annotation_toolkit.utils.profiling import (
    PerformanceProfiler,
    MemoryProfiler,
    profile_performance,
    profile_memory,
    RegressionDetector
)

# Decorator-based profiling
@profile_performance(name="data_processing")
def process_large_dataset(data):
    # Your processing logic
    pass

# Context manager profiling
profiler = PerformanceProfiler()
with profiler.profile("operation_name"):
    # Code to profile
    result = expensive_operation()

# Get statistics
stats = profiler.get_statistics("operation_name")
print(f"Average time: {stats['avg_time']:.4f}s")
print(f"Min time: {stats['min_time']:.4f}s")
print(f"Max time: {stats['max_time']:.4f}s")
print(f"95th percentile: {stats['p95']:.4f}s")
print(f"99th percentile: {stats['p99']:.4f}s")
print(f"Total calls: {stats['call_count']}")

# Memory profiling
mem_profiler = MemoryProfiler()
with mem_profiler.profile("memory_intensive_op"):
    large_data = load_large_file()
    process(large_data)

mem_stats = mem_profiler.get_memory_stats("memory_intensive_op")
print(f"Peak memory: {mem_stats['peak_memory_mb']:.2f} MB")

# Detect performance regressions
detector = RegressionDetector(threshold_percent=10)
is_regression = detector.check_regression(
    baseline_time=1.0,
    current_time=1.15
)
if is_regression:
    print("Performance regression detected!")
```

### Streaming for Large Files

Handle large JSON files without loading them entirely into memory.

#### Streaming JSON Parser

```python
from annotation_toolkit.utils.streaming import StreamingJSONParser

parser = StreamingJSONParser()

# Stream array elements one by one
for item in parser.stream_array("large_conversation.json"):
    # Process each conversation turn individually
    print(f"Processing turn: {item['role']}")
    process_turn(item)

# Stream object key-value pairs
for key, value in parser.stream_object("large_data.json"):
    print(f"Key: {key}, Value: {value}")

# Chunk-based file processing
for chunk in parser.read_in_chunks("huge_file.json", chunk_size=1024*1024):
    # Process 1MB chunks
    process_chunk(chunk)
```

### Data Validation Framework

Validate JSON, conversation data, and text files with detailed error reporting.

#### JSON and Conversation Validation

```python
from annotation_toolkit.utils.validation import (
    validate_json_file,
    validate_conversation_file,
    JsonStreamingValidator,
    ConversationValidator,
    ValidationSeverity
)

# Validate JSON against a schema
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "number"}
    },
    "required": ["name"]
}

result = validate_json_file("user_data.json", schema=schema)

if not result.is_valid:
    for message in result.messages:
        severity = message.severity.name
        print(f"[{severity}] Line {message.line}: {message.message}")
        if message.suggestion:
            print(f"   Suggestion: {message.suggestion}")
else:
    print("✓ Validation passed")

# Validate conversation data
conv_result = validate_conversation_file(
    "conversation.json",
    max_turns=20,
    required_fields=["role", "content"]
)

# Streaming validation for large files
validator = JsonStreamingValidator(schema=schema)
for is_valid, message in validator.validate_stream("large_file.json"):
    if not is_valid:
        print(f"Validation error: {message}")

# Conversation-specific validation
conv_validator = ConversationValidator(max_turns=50)
for is_valid, message in conv_validator.validate_stream("conversations.json"):
    if not is_valid:
        print(f"Invalid conversation: {message}")
```

### Error Recovery Strategies

Implement robust error handling with automatic retry, circuit breakers, and fallback mechanisms.

#### Retry with Exponential Backoff

```python
from annotation_toolkit.utils.recovery import (
    exponential_retry,
    linear_retry,
    circuit_breaker,
    with_fallback,
    ExponentialBackoffStrategy,
    CircuitBreaker,
    RetryableOperation
)

# Decorator-based retry
@exponential_retry(max_attempts=3, base_delay=1.0, max_delay=10.0)
def fetch_data_from_api():
    # Operation that might fail transiently
    response = external_api.get_data()
    return response

# Linear backoff for predictable delays
@linear_retry(max_attempts=5, delay=2.0)
def process_file(filename):
    # File operation that might fail
    with open(filename, 'r') as f:
        return f.read()

# Circuit breaker pattern
@circuit_breaker(failure_threshold=5, timeout=60)
def call_external_service():
    # Fails fast after threshold is reached
    return service.call()

# Fallback mechanism
@with_fallback(fallback_value={"default": "data"})
def load_config():
    # Returns fallback if operation fails
    return config_loader.load()

# Manual retry strategy
strategy = ExponentialBackoffStrategy(
    max_attempts=3,
    base_delay=1.0,
    max_delay=30.0
)

operation = RetryableOperation(strategy)
result = operation.execute(
    lambda: risky_operation(),
    retry_on=[ConnectionError, TimeoutError]
)

# Circuit breaker with manual control
breaker = CircuitBreaker(
    failure_threshold=10,
    timeout=120
)

if breaker.can_execute():
    try:
        result = external_call()
        breaker.record_success()
    except Exception as e:
        breaker.record_failure()
        raise

print(f"Circuit breaker state: {breaker.state.name}")
print(f"Failure count: {breaker.failure_count}")
```

### Structured Logging

Enhanced logging with context tracking, performance metrics, and audit trails.

#### Context-Aware Logging

```python
from annotation_toolkit.utils.structured_logging import (
    StructuredLogger,
    LoggingContext,
    PerformanceTracker,
    AuditLogger,
    log_performance,
    audit_file_operation
)

# Initialize structured logger
logger = StructuredLogger("my_application")

# Log with context
with LoggingContext(user_id="user123", request_id="req456", session_id="sess789"):
    logger.info("Processing user request", extra={
        "item_count": 42,
        "operation": "batch_process"
    })

    # All logs within this context include user_id, request_id, session_id
    logger.debug("Starting validation")
    result = validate_data(data)
    logger.info("Validation complete", extra={"result": result})

# Performance tracking with logging
tracker = PerformanceTracker(logger)

with tracker.track("data_processing"):
    # Automatically logs performance metrics
    process_large_dataset()

# Performance metrics are logged with:
# - Execution time
# - Memory usage (if psutil available)
# - CPU usage

# Decorator-based performance logging
@log_performance(logger=logger, operation_name="file_processing")
def process_file(filename):
    # Performance automatically logged
    with open(filename, 'r') as f:
        return f.read()

# Audit logging for compliance
audit_logger = AuditLogger("security_audit")

@audit_file_operation(
    logger=audit_logger,
    operation_type="write",
    include_content_hash=True
)
def save_sensitive_data(filepath, data):
    with open(filepath, 'w') as f:
        f.write(data)

# Audit log includes:
# - Timestamp
# - User/session context
# - Operation type
# - File path
# - Success/failure
# - Content hash (if enabled)
```

### Resource Management

Automatic cleanup of file handles, temporary files, and pooled resources.

#### Managed Resources

```python
from annotation_toolkit.utils.resources import (
    ManagedResource,
    ResourcePool,
    managed_file,
    temporary_file,
    resource_scope,
    TemporaryDirectory
)

# Managed file handles (auto-close)
with managed_file("/path/to/file.txt", mode="r") as f:
    content = f.read()
# File automatically closed, even if exception occurs

# Temporary files with auto-cleanup
with temporary_file(suffix=".json") as temp_path:
    # Write to temporary file
    with open(temp_path, 'w') as f:
        json.dump(data, f)

    # Process temporary file
    result = process_json_file(temp_path)
# Temporary file automatically deleted

# Temporary directories
with TemporaryDirectory() as temp_dir:
    # Create files in temporary directory
    file_path = os.path.join(temp_dir, "data.json")
    save_data(file_path, my_data)

    # Process files
    process_directory(temp_dir)
# Directory and all contents automatically deleted

# Resource pooling
pool = ResourcePool(
    create_resource=lambda: create_database_connection(),
    max_size=10,
    timeout=30.0
)

# Acquire resource from pool
with pool.acquire() as connection:
    result = connection.execute(query)
# Resource automatically returned to pool

# Resource scope for complex cleanup
with resource_scope() as scope:
    # Register resources for cleanup
    file1 = open("file1.txt", "w")
    scope.register(file1, cleanup=lambda f: f.close())

    file2 = open("file2.txt", "w")
    scope.register(file2, cleanup=lambda f: f.close())

    # Use resources
    file1.write("data1")
    file2.write("data2")
# All registered resources automatically cleaned up
```

### Security Features

Path validation, input sanitization, rate limiting, and secure file operations.

#### Security Utilities

```python
from annotation_toolkit.utils.security import (
    PathValidator,
    InputSanitizer,
    RateLimiter,
    SecureFileHandler,
    FileSizeValidator
)

# Path validation (prevent directory traversal)
validator = PathValidator(
    allowed_base="/safe/directory",
    max_path_length=4096,
    allow_symlinks=False
)

user_provided_path = "/safe/directory/user_file.txt"
if validator.validate_path(user_provided_path):
    # Safe to use
    process_file(user_provided_path)
else:
    print("Invalid or unsafe path")

# Input sanitization
sanitizer = InputSanitizer()

# Sanitize for display (prevent XSS)
user_input = "<script>alert('xss')</script>"
safe_display = sanitizer.sanitize_for_display(user_input)
print(safe_display)  # &lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;

# Sanitize for file names
filename = sanitizer.sanitize_filename("../../etc/passwd")
print(filename)  # etc_passwd

# Sanitize SQL (basic protection)
sql_input = "'; DROP TABLE users; --"
safe_sql = sanitizer.sanitize_sql(sql_input)

# Rate limiting
limiter = RateLimiter(
    max_requests=100,
    window_seconds=60
)

user_id = "user123"
if limiter.check_rate_limit(user_id):
    # Process request
    handle_request(user_id)
else:
    print("Rate limit exceeded")

# File size validation
size_validator = FileSizeValidator(max_size_mb=100)

if size_validator.validate_file_size("/path/to/file.txt"):
    # Safe to process
    process_file("/path/to/file.txt")
else:
    print("File exceeds maximum size")

# Secure file handler (combines multiple security checks)
secure_handler = SecureFileHandler(
    allowed_base="/safe/directory",
    max_file_size_mb=50,
    allow_symlinks=False
)

try:
    # Reads file with security checks
    data = secure_handler.read_file("/safe/directory/data.json")

    # Writes file with security checks
    secure_handler.write_file(
        "/safe/directory/output.json",
        json.dumps(processed_data)
    )
except SecurityError as e:
    print(f"Security violation: {e}")
```

### Configuration for Advanced Features

Add these settings to your configuration file to control advanced features:

```yaml
security:
  max_file_size_mb: 100
  max_path_length: 4096
  allow_symlinks: false
  rate_limit_requests_per_minute: 100

performance:
  enable_caching: true
  cache_ttl_seconds: 300
  streaming_threshold_mb: 10  # Use streaming for files larger than 10MB
  enable_profiling: false       # Enable performance profiling

logging:
  level: INFO                   # DEBUG, INFO, WARNING, ERROR, CRITICAL
  structured_logging: true      # Enable structured logging
  audit_trail: true             # Enable audit logging
  max_log_size_mb: 50
  backup_count: 5

validation:
  strict_mode: true             # Fail on validation warnings
  max_validation_errors: 100    # Stop after 100 errors

error_recovery:
  max_retry_attempts: 3
  base_retry_delay: 1.0
  max_retry_delay: 30.0
  circuit_breaker_threshold: 10
  circuit_breaker_timeout: 120
```

For comprehensive documentation on advanced features, see:
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and design patterns
- [PERFORMANCE.md](PERFORMANCE.md) - Performance optimization guide
- [SECURITY.md](SECURITY.md) - Security features and best practices
- [API_REFERENCE.md](API_REFERENCE.md) - Complete API documentation
- [CONFIGURATION_REFERENCE.md](CONFIGURATION_REFERENCE.md) - All configuration options

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
