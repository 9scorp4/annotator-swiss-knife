# Data Annotation Swiss Knife

A comprehensive yet simple toolkit designed to streamline various data annotation tasks. This toolkit integrates multiple annotation tools into a cohesive application with proper architecture, making it more maintainable, extensible, and user-friendly.

## Features

### Core Annotation Tools

* **Dictionary to Bullet List**: Convert dictionaries with URLs to formatted bullet lists with hyperlinks
* **Text Cleaner**: Clean text from markdown/JSON/code artifacts and transform cleaned text back to code format
* **JSON Visualizer**: Visualize and format JSON data with special handling for conversation data, XML tags, and malformed JSON repair
* **Conversation Generator**: Build AI conversation JSON data turn-by-turn, supporting up to 20 conversation turns with validation
* **Text Collector**: Collect text from multiple fields and output them as a JSON list, with automatic empty string filtering

### Advanced Infrastructure

* **Performance Profiling**: Track execution time, memory usage, and detect performance regressions with comprehensive statistics
* **Streaming Support**: Handle large files efficiently without loading entire contents into memory
* **Validation Framework**: Validate JSON, conversation data, and text files with detailed error reporting
* **Error Recovery**: Automatic retry with exponential backoff, circuit breaker pattern, and fallback handling
* **Structured Logging**: Enhanced logging with context tracking, performance metrics, and audit trails
* **Resource Management**: Automatic cleanup of file handles, temporary files, and pooled resources
* **Security Features**: Path validation, input sanitization, rate limiting, and secure file operations
* **Enhanced Error Handling**: Comprehensive error handling system with detailed error messages, error codes, and actionable suggestions

## Installation

### Using Setup Scripts (Recommended)

This application comes with setup scripts that automate the installation process, including creating a virtual environment and installing all dependencies. **This is the recommended approach for Meta managed devices** as it runs from source and doesn't require executable signing.

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

> 📋 **Windows Users**: For detailed Windows-specific instructions, troubleshooting, and alternative installation methods, see the [**Windows Setup Guide**](WINDOWS_SETUP_GUIDE.md).

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

## Releases & Downloads

### Pre-built Executables

Pre-built standalone executables are available for download from the [GitHub Releases](https://github.com/9scorp4/annotator-swiss-knife/releases) page. No Python installation required!

**Available Platforms:**
- **macOS** - `.app` bundle (macOS 10.14+)
- **Windows** - `.exe` executable (Windows 10+)
- **Linux** - Standalone binary (Ubuntu 20.04+, other distributions may work)

**Installation:**

1. Go to the [latest release](https://github.com/9scorp4/annotator-swiss-knife/releases/latest)
2. Download the appropriate file for your platform
3. Follow the platform-specific instructions in the release notes

**Security Notes:**
- Executables are **not code-signed** and may trigger security warnings
- SHA256 checksums are provided for verification
- On macOS: Right-click and select "Open" to bypass Gatekeeper on first launch
- On Windows: Click "More info" then "Run anyway" if SmartScreen appears

### Installing from PyPI

> **Note**: This package is not currently published to PyPI. Use the installation methods above or install from source.

### Version History

See the [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes in each version.

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

#### Conversation Generator

```bash
annotation-toolkit convgen input.json --output conversation.json --format pretty
```

The input JSON file should have the following format:

```json
{
  "turns": [
    {"user": "Hello, how are you?", "assistant": "I'm doing well, thank you!"},
    {"user": "What's the weather like?", "assistant": "I don't have access to weather information."}
  ]
}
```

The output will be a properly formatted conversation JSON array:

```json
[
  {"role": "user", "content": "Hello, how are you?"},
  {"role": "assistant", "content": "I'm doing well, thank you!"},
  {"role": "user", "content": "What's the weather like?"},
  {"role": "assistant", "content": "I don't have access to weather information."}
]
```

#### Text Collector

```bash
annotation-toolkit textcollect input.txt --output collection.json --format pretty
```

The input file should be a text file with one text item per line. Empty lines and whitespace-only lines are automatically filtered out.

Example input file (`items.txt`):
```
First item
Second item

Third item
```

The output will be a JSON array:
```json
[
  "First item",
  "Second item",
  "Third item"
]
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
from annotation_toolkit.core.conversation.generator import ConversationGenerator
from annotation_toolkit.core.text.text_cleaner import TextCleaner
from annotation_toolkit.core.conversation.visualizer import JsonVisualizer

# Dictionary to Bullet List
dict_tool = DictToBulletList(markdown_output=True)
output = dict_tool.process_dict({
    "1": "https://www.example.com/page1",
    "2": "https://www.example.com/page2"
})
print(output)

# Conversation Generator
conv_gen = ConversationGenerator(max_turns=20)
conv_gen.add_turn("Hello, how are you?", "I'm doing well, thank you!")
conv_gen.add_turn("What's the weather like?", "I don't have access to weather information.")
json_output = conv_gen.generate_json(pretty=True)
print(json_output)

# Load from JSON
conversation_data = [
    {"role": "user", "content": "Hi!"},
    {"role": "assistant", "content": "Hello!"}
]
conv_gen.load_from_json(conversation_data)
print(f"Loaded {conv_gen.get_turn_count()} turns")

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
  conversation_generator:
    enabled: true
    max_turns: 20
    default_color: "#9C27B0"
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
security:
  max_file_size_mb: 100
  max_path_length: 4096
  allow_symlinks: false
  rate_limit_requests_per_minute: 100
performance:
  enable_caching: true
  cache_ttl_seconds: 300
  streaming_threshold_mb: 10
  enable_profiling: false
logging:
  level: INFO
  structured_logging: false
  audit_trail: false
```

To use a custom configuration file:

```bash
annotation-toolkit --config config.yaml gui
```

## Testing

The toolkit includes a comprehensive test suite that ensures the reliability and correctness of all components. The tests are organized to mirror the structure of the main package, making it easy to locate tests for specific components.

### Running Tests

To run all tests:

```bash
python -m tests.run_tests
```

Or from the tests directory:

```bash
cd tests
python run_tests.py
```

### Test Coverage

You can generate a test coverage report:

```bash
python -m tests.run_tests --coverage
```

This requires the `pytest-cov` package, which can be installed via pip:

```bash
pip install pytest-cov
```

### Test Structure

The test suite covers:

- Core functionality (base classes, text tools, JSON tools)
- Command-line interface
- Configuration management
- Utility modules (error handling, JSON parsing, text formatting)

For more details about the test suite, see the [tests/README.md](tests/README.md) file.

## Building Standalone Executables

For instructions on building standalone executables for macOS and Windows, see the [README_BUILD.md](README_BUILD.md) file.

## Repository Structure

```
annotator_swiss_knife/
├── annotation_toolkit/          # Main package source code
│   ├── core/                    # Core annotation tools
│   │   ├── base.py              # Base classes for all tools
│   │   ├── conversation/        # Conversation-related tools
│   │   │   ├── generator.py     # Conversation generator
│   │   │   └── visualizer.py    # JSON/conversation visualizer
│   │   └── text/                # Text processing tools
│   │       ├── dict_to_bullet.py
│   │       └── text_cleaner.py
│   ├── di/                      # Dependency injection system
│   │   ├── bootstrap.py         # DI container bootstrap
│   │   ├── container.py         # DI container implementation
│   │   └── decorators.py        # DI decorators (@inject)
│   ├── ui/                      # User interfaces
│   │   ├── cli/                 # Command-line interface
│   │   └── gui/                 # Graphical user interface
│   │       └── widgets/         # GUI widgets for each tool
│   ├── utils/                   # Utility modules
│   │   ├── error_handler.py     # Error handling system
│   │   ├── errors.py            # Custom exceptions
│   │   ├── file_utils.py        # File operations
│   │   ├── json/                # JSON utilities
│   │   │   └── fixer.py         # JSON repair utilities
│   │   ├── xml/                 # XML utilities
│   │   │   └── formatter.py     # XML formatting
│   │   ├── profiling.py         # Performance profiling
│   │   ├── streaming.py         # Large file streaming
│   │   ├── validation.py        # Data validation framework
│   │   ├── recovery.py          # Error recovery strategies
│   │   ├── structured_logging.py # Enhanced logging
│   │   ├── resources.py         # Resource management
│   │   └── security.py          # Security utilities
│   ├── cli.py                   # CLI entry point
│   └── config.py                # Configuration management
├── docs/                        # Documentation
│   ├── ARCHITECTURE.md          # Architecture overview
│   ├── SECURITY.md              # Security documentation
│   ├── PERFORMANCE.md           # Performance guide
│   ├── API_REFERENCE.md         # API reference
│   ├── CONFIGURATION_REFERENCE.md # Config reference
│   └── DEPENDENCY_INJECTION_IMPLEMENTATION.md
├── scripts/                     # Scripts for building, running, and setting up
│   ├── build/                   # Build scripts for creating executables
│   ├── run/                     # Scripts for running the application
│   └── setup/                   # Scripts for setting up the environment
├── tests/                       # Test suite
│   ├── core/                    # Tests for core functionality
│   ├── utils/                   # Tests for utility modules
│   ├── test_base.py             # Tests for base classes
│   ├── test_cli.py              # Tests for command-line interface
│   ├── test_config.py           # Tests for configuration management
│   ├── test_dependency_injection.py # Tests for DI system
│   ├── run_tests.py             # Script to run all tests
│   └── README.md                # Test suite documentation
├── .gitignore                   # Git ignore file
├── CLAUDE.md                    # Developer guidance for Claude Code
├── README.md                    # Main documentation
├── README_BUILD.md              # Build instructions
├── User_Manual.md               # End-user manual
├── requirements.txt             # Package dependencies
└── setup.py                     # Package setup script
```

## Advanced Features

The toolkit includes advanced infrastructure for performance monitoring, error recovery, security, and resource management.

### Performance Profiling

Track execution time, memory usage, and detect performance regressions:

```python
from annotation_toolkit.utils.profiling import (
    PerformanceProfiler,
    MemoryProfiler,
    profile_performance,
    profile_memory
)

# Use decorators for automatic profiling
@profile_performance(name="my_operation")
def process_data(data):
    # Your code here
    pass

# Or use profilers directly
profiler = PerformanceProfiler()
with profiler.profile("operation_name"):
    # Code to profile
    pass

stats = profiler.get_statistics("operation_name")
print(f"Average time: {stats['avg_time']:.4f}s")
print(f"95th percentile: {stats['p95']:.4f}s")

# Memory profiling
mem_profiler = MemoryProfiler()
with mem_profiler.profile("memory_intensive_op"):
    # Code to profile
    pass
```

### Streaming for Large Files

Handle large files efficiently without loading them entirely into memory:

```python
from annotation_toolkit.utils.streaming import StreamingJSONParser

# Stream large JSON files
parser = StreamingJSONParser()
for item in parser.stream_array("large_file.json"):
    # Process each item individually
    process(item)

# Stream JSON objects
for key, value in parser.stream_object("large_object.json"):
    # Process each key-value pair
    process(key, value)
```

### Validation Framework

Validate data with detailed error reporting:

```python
from annotation_toolkit.utils.validation import (
    validate_json_file,
    validate_conversation_file,
    JsonStreamingValidator
)

# Validate JSON against a schema
result = validate_json_file("data.json", schema=my_schema)
if not result.is_valid:
    for message in result.messages:
        print(f"{message.severity}: {message.message}")

# Validate conversation data
result = validate_conversation_file("conversation.json", max_turns=20)
```

### Error Recovery Strategies

Automatic retry with exponential backoff and circuit breaker patterns:

```python
from annotation_toolkit.utils.recovery import (
    exponential_retry,
    circuit_breaker,
    with_fallback,
    ExponentialBackoffStrategy
)

# Automatic retry with exponential backoff
@exponential_retry(max_attempts=3, base_delay=1.0)
def unreliable_operation():
    # Operation that might fail
    pass

# Circuit breaker pattern
@circuit_breaker(failure_threshold=5, timeout=60)
def external_service_call():
    # Call to external service
    pass

# Fallback handling
@with_fallback(fallback_value="default")
def risky_operation():
    # Operation with fallback
    pass
```

### Structured Logging

Enhanced logging with context tracking and audit trails:

```python
from annotation_toolkit.utils.structured_logging import (
    StructuredLogger,
    LoggingContext,
    audit_file_operation
)

logger = StructuredLogger("my_module")

# Log with context
with LoggingContext(user_id="user123", request_id="req456"):
    logger.info("Processing request", extra={"item_count": 42})

# Audit file operations
@audit_file_operation(operation_type="write")
def save_file(path, data):
    # File operation
    pass
```

### Security Features

Path validation, input sanitization, and rate limiting:

```python
from annotation_toolkit.utils.security import (
    PathValidator,
    InputSanitizer,
    RateLimiter,
    SecureFileHandler
)

# Validate paths to prevent directory traversal
validator = PathValidator(allowed_base="/safe/path")
if validator.validate_path("/safe/path/file.txt"):
    # Path is safe
    pass

# Sanitize user input
sanitizer = InputSanitizer()
clean_input = sanitizer.sanitize_for_display(user_input)

# Rate limiting
limiter = RateLimiter(max_requests=100, window_seconds=60)
if limiter.check_rate_limit("user_id"):
    # Process request
    pass

# Secure file operations
handler = SecureFileHandler()
data = handler.read_file("/path/to/file.json")
```

For more details on advanced features, see:
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture
- [PERFORMANCE.md](docs/PERFORMANCE.md) - Performance optimization guide
- [SECURITY.md](docs/SECURITY.md) - Security features and best practices
- [API_REFERENCE.md](docs/API_REFERENCE.md) - Complete API documentation

## Extending the Toolkit

The toolkit is designed to be easily extensible. To add a new annotation tool:

1. Create a new class that inherits from one of the base classes in `annotation_toolkit.core.base`
2. Implement the required methods
3. Add UI components for your tool
4. Register your tool in the main application

See the existing tools for examples.

## Error Handling

The toolkit includes a comprehensive error handling system that provides detailed and actionable error messages. This makes it easier to diagnose and resolve issues during development and in production.

### Key Features

* **Hierarchical Exception Classes**: Custom exception classes organized by error type
* **Error Codes**: Enumerated error codes for categorizing errors
* **Contextual Information**: Error messages include file, function, and line number information
* **Actionable Suggestions**: Error messages include suggestions for resolving issues
* **Error Handling Utilities**: Functions and decorators for consistent error handling

### Using the Error Handling System

```python
from annotation_toolkit.utils import (
    with_error_handling,
    ErrorCode,
    TypeValidationError
)

# Using decorators for automatic error handling
@with_error_handling(
    error_code=ErrorCode.PROCESSING_ERROR,
    suggestion="Check the input data format"
)
def process_data(data):
    # Function implementation
    pass

# Raising specific exceptions with context
def validate_input(data):
    if not isinstance(data, dict):
        raise TypeValidationError(
            "data",
            dict,
            type(data),
            suggestion="Ensure you're passing a dictionary to validate_input."
        )
    # Validation logic
```

For more details, see the [Error Handling documentation](annotation_toolkit/utils/ERROR_HANDLING.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Nicolas Arias Garcia

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
