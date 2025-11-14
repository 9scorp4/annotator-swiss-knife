# API Reference - Annotation Swiss Knife

## Overview

This document provides a comprehensive API reference for all tools, utilities, and core components in the Annotation Swiss Knife toolkit.

## Table of Contents

1. [Core Tools](#core-tools)
2. [Infrastructure Utilities](#infrastructure-utilities)
3. [Configuration](#configuration)
4. [Dependency Injection](#dependency-injection)
5. [Error Handling](#error-handling)

---

## Core Tools

### DictToBulletList

**Location**: `annotation_toolkit.core.text.dict_to_bullet`

**Description**: Converts dictionaries with URLs to formatted bullet lists.

**Class**: `DictToBulletList(TextAnnotationTool)`

**Constructor**:
```python
DictToBulletList(markdown_output: bool = True)
```

**Methods**:
- `process_dict(data: Dict[str, str]) -> str`: Convert dictionary to bullet list
- `process_text(text: str) -> str`: Process text (inherited from base)

**Example**:
```python
from annotation_toolkit.core.text.dict_to_bullet import DictToBulletList

tool = DictToBulletList(markdown_output=True)
result = tool.process_dict({
    "1": "https://example.com",
    "2": "https://example.org"
})
# Result: "• [1](https://example.com)\n• [2](https://example.org)"
```

---

### TextCleaner

**Location**: `annotation_toolkit.core.text.text_cleaner`

**Description**: Cleans text from markdown/JSON/code artifacts.

**Class**: `TextCleaner(TextAnnotationTool)`

**Methods**:
- `clean_text(text: str) -> str`: Remove code blocks and formatting
- `transform_back(text: str, format: str) -> str`: Transform back to code format
- `process_text(text: str) -> str`: Process text (inherited from base)

**Example**:
```python
from annotation_toolkit.core.text.text_cleaner import TextCleaner

tool = TextCleaner()
cleaned = tool.clean_text("```python\nprint('hello')\n```")
# Result: "print('hello')"
```

---

### JsonVisualizer

**Location**: `annotation_toolkit.core.conversation.visualizer`

**Description**: Visualizes and formats JSON data with conversation support.

**Class**: `JsonVisualizer(JsonAnnotationTool)`

**Constructor**:
```python
JsonVisualizer(output_format: str = "text")
```

**Methods**:
- `parse_conversation_data(json_str: str) -> List[Dict]`: Parse conversation JSON
- `format_conversation(conversation: List[Dict], use_colors: bool = True) -> str`: Format conversation
- `format_generic_json(json_data: Union[Dict, List]) -> str`: Format generic JSON
- `search_conversation(conversation: List[Dict], query: str, case_sensitive: bool = False) -> List[int]`: Search conversation
- `process_json(json_data: Union[Dict, List]) -> str`: Process JSON (inherited from base)

**Example**:
```python
from annotation_toolkit.core.conversation.visualizer import JsonVisualizer

tool = JsonVisualizer(output_format="text")
conversation = [
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi there!"}
]
formatted = tool.format_conversation(conversation)
```

---

### ConversationGenerator

**Location**: `annotation_toolkit.core.conversation.generator`

**Description**: Builds AI conversation JSON data turn-by-turn.

**Class**: `ConversationGenerator(JsonAnnotationTool)`

**Constructor**:
```python
ConversationGenerator(max_turns: int = 20)
```

**Methods**:
- `add_turn(user_message: str, assistant_message: str) -> bool`: Add a conversation turn
- `remove_turn(turn_index: int) -> bool`: Remove a turn by index
- `clear() -> None`: Clear all turns
- `get_turn_count() -> int`: Get number of turns
- `can_add_turn() -> bool`: Check if can add more turns
- `generate_json(pretty: bool = True) -> str`: Generate JSON output
- `load_from_json(json_data: Union[str, List[Dict]]) -> None`: Load conversation from JSON
- `get_turn(turn_index: int) -> Optional[Tuple[str, str]]`: Get specific turn
- `process_json(json_data: Union[Dict, List]) -> str`: Process JSON (inherited from base)

**Properties**:
- `max_turns`: Maximum number of turns allowed
- `conversation`: Current conversation (copy)

**Example**:
```python
from annotation_toolkit.core.conversation.generator import ConversationGenerator

gen = ConversationGenerator(max_turns=20)
gen.add_turn("Hello, how are you?", "I'm doing well, thanks!")
gen.add_turn("What's the weather?", "I don't have weather data.")

json_output = gen.generate_json(pretty=True)
print(f"Turn count: {gen.get_turn_count()}")
```

---

## Infrastructure Utilities

### Performance Profiling

**Location**: `annotation_toolkit.utils.profiling`

#### PerformanceProfiler

**Description**: Thread-safe performance profiling with statistics.

**Methods**:
- `profile(name: str) -> ContextManager`: Context manager for profiling
- `get_statistics(name: str) -> Dict[str, float]`: Get profiling statistics
- `reset(name: str = None) -> None`: Reset profiling data

**Returns** (statistics):
- `call_count`: Number of calls
- `total_time`: Total execution time
- `avg_time`: Average time per call
- `min_time`: Minimum time
- `max_time`: Maximum time
- `median`: Median time
- `std_dev`: Standard deviation
- `p95`: 95th percentile
- `p99`: 99th percentile

**Decorators**:
- `@profile_performance(name: str)`: Auto-profile function
- `@profile_memory(name: str)`: Auto-profile memory
- `@comprehensive_profile(name: str)`: Profile time + memory

---

### Streaming

**Location**: `annotation_toolkit.utils.streaming`

#### StreamingJSONParser

**Description**: Stream large JSON files without loading into memory.

**Methods**:
- `stream_array(filepath: str) -> Generator`: Stream JSON array elements
- `stream_object(filepath: str) -> Generator`: Stream JSON object key-value pairs
- `read_in_chunks(filepath: str, chunk_size: int) -> Generator`: Read file in chunks

**Example**:
```python
from annotation_toolkit.utils.streaming import StreamingJSONParser

parser = StreamingJSONParser()
for item in parser.stream_array("large.json"):
    process(item)
```

---

### Validation

**Location**: `annotation_toolkit.utils.validation`

#### Validation Result Classes

**ValidationResult**:
- `is_valid: bool`: Overall validation result
- `messages: List[ValidationMessage]`: Validation messages
- `add_message(message: ValidationMessage)`: Add validation message

**ValidationMessage**:
- `line: int`: Line number
- `column: int`: Column number
- `message: str`: Error message
- `severity: ValidationSeverity`: Severity level
- `suggestion: Optional[str]`: Suggestion for fix

**ValidationSeverity** (Enum):
- `ERROR`: Critical error
- `WARNING`: Warning
- `INFO`: Informational

#### Validators

**JsonStreamingValidator**:
```python
JsonStreamingValidator(schema: Optional[Dict] = None)
```
- `validate_stream(filepath: str) -> Generator[Tuple[bool, str]]`

**ConversationValidator**:
```python
ConversationValidator(max_turns: int = 50)
```
- `validate_stream(filepath: str) -> Generator[Tuple[bool, str]]`

#### Helper Functions

- `validate_json_file(filepath: str, schema: Optional[Dict] = None) -> ValidationResult`
- `validate_conversation_file(filepath: str, max_turns: int = 20, required_fields: List[str] = None) -> ValidationResult`

---

### Error Recovery

**Location**: `annotation_toolkit.utils.recovery`

#### Retry Strategies

**ExponentialBackoffStrategy**:
```python
ExponentialBackoffStrategy(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0
)
```

**LinearBackoffStrategy**:
```python
LinearBackoffStrategy(
    max_attempts: int = 3,
    delay: float = 1.0
)
```

#### CircuitBreaker

```python
CircuitBreaker(
    failure_threshold: int = 5,
    timeout: float = 60.0
)
```

**Methods**:
- `can_execute() -> bool`: Check if can execute
- `record_success()`: Record successful execution
- `record_failure()`: Record failed execution
- `reset()`: Reset circuit breaker

**States**: `CLOSED`, `OPEN`, `HALF_OPEN`

#### Decorators

- `@exponential_retry(max_attempts: int, base_delay: float, max_delay: float)`
- `@linear_retry(max_attempts: int, delay: float)`
- `@circuit_breaker(failure_threshold: int, timeout: float)`
- `@with_fallback(fallback_value: Any)`

---

### Structured Logging

**Location**: `annotation_toolkit.utils.structured_logging`

#### StructuredLogger

```python
StructuredLogger(name: str)
```

**Methods**: Standard logging methods (info, debug, warning, error, critical) with extra context support

#### LoggingContext

```python
LoggingContext(user_id: str = None, request_id: str = None, session_id: str = None, **kwargs)
```

**Usage**:
```python
with LoggingContext(user_id="user123", request_id="req456"):
    logger.info("Processing request")  # Includes user_id and request_id
```

#### Decorators

- `@log_performance(logger: StructuredLogger, operation_name: str)`
- `@audit_file_operation(logger: AuditLogger, operation_type: str, include_content_hash: bool = False)`

---

### Resource Management

**Location**: `annotation_toolkit.utils.resources`

#### Classes

**ResourcePool**:
```python
ResourcePool(
    create_resource: Callable,
    max_size: int = 10,
    timeout: float = 30.0
)
```

**ManagedResource**:
```python
ManagedResource(resource: Any, cleanup: Callable)
```

**TemporaryDirectory**:
```python
TemporaryDirectory(suffix: str = None, prefix: str = None, dir: str = None)
```

#### Helper Functions

- `managed_file(filepath: str, mode: str = 'r') -> ContextManager`
- `temporary_file(suffix: str = None, prefix: str = None, dir: str = None) -> ContextManager`
- `resource_scope() -> ContextManager`

---

### Security

**Location**: `annotation_toolkit.utils.security`

#### PathValidator

```python
PathValidator(
    allowed_base: str,
    max_path_length: int = 4096,
    allow_symlinks: bool = False
)
```

**Methods**:
- `validate_path(path: str) -> bool`: Validate path is safe

#### InputSanitizer

**Methods**:
- `sanitize_for_display(text: str) -> str`: Sanitize for HTML display
- `sanitize_filename(filename: str) -> str`: Sanitize filename
- `sanitize_sql(text: str) -> str`: Basic SQL escaping

#### RateLimiter

```python
RateLimiter(
    max_requests: int = 100,
    window_seconds: float = 60.0
)
```

**Methods**:
- `check_rate_limit(identifier: str) -> bool`: Check if request allowed

#### SecureFileHandler

```python
SecureFileHandler(
    allowed_base: str,
    max_file_size_mb: int = 100,
    allow_symlinks: bool = False
)
```

**Methods**:
- `read_file(filepath: str, encoding: str = 'utf-8') -> str`: Read file with security checks
- `write_file(filepath: str, content: str, encoding: str = 'utf-8') -> None`: Write file with security checks

---

## Configuration

**Location**: `annotation_toolkit.config`

### Config Class

```python
Config(config_path: Optional[str] = None)
```

**Methods**:
- `get(*keys, default=None) -> Any`: Get nested configuration value
- `set(*keys, value: Any) -> None`: Set nested configuration value
- `to_dict() -> Dict`: Export configuration as dictionary

**Example**:
```python
from annotation_toolkit.config import Config

config = Config("custom_config.yaml")
markdown = config.get("tools", "dict_to_bullet", "markdown_output", default=True)
config.set("tools", "dict_to_bullet", "markdown_output", False)
```

**Default Sections**:
- `tools`: Tool-specific configuration
- `ui`: UI settings (theme, font, window size)
- `data`: Data handling settings
- `security`: Security settings
- `performance`: Performance settings
- `logging`: Logging configuration

---

## Dependency Injection

**Location**: `annotation_toolkit.di`

### DIContainer

```python
DIContainer()
```

**Methods**:
- `register_factory(interface: Type, factory: Callable, scope: ServiceScope = SINGLETON, **dependencies) -> None`
- `resolve(interface: Type) -> Any`: Resolve service instance
- `is_registered(interface: Type) -> bool`: Check if service is registered

### ServiceScope (Enum)

- `SINGLETON`: Single instance shared across application
- `TRANSIENT`: New instance for each resolution
- `SCOPED`: Instance per scope (not fully implemented)

### Bootstrap

```python
from annotation_toolkit.di.bootstrap import bootstrap_application, get_tool_instances

container = bootstrap_application(config)
tools = get_tool_instances(container)
```

---

## Error Handling

**Location**: `annotation_toolkit.utils.errors`, `annotation_toolkit.utils.error_handler`

### Exception Hierarchy

```
AnnotationToolkitError (base)
├── ConfigurationError
├── ValidationError
│   ├── TypeValidationError
│   └── SchemaValidationError
├── ProcessingError
├── FileOperationError
│   ├── FileNotFoundError
│   ├── FileReadError
│   └── FileWriteError
└── ToolExecutionError
```

### Decorators

```python
from annotation_toolkit.utils.error_handler import with_error_handling

@with_error_handling(
    error_code: ErrorCode,
    error_message: str = None,
    suggestion: str = None
)
def my_function():
    pass
```

### ErrorCode (Enum)

- `CONFIGURATION_ERROR`
- `VALIDATION_ERROR`
- `PROCESSING_ERROR`
- `FILE_NOT_FOUND`
- `FILE_READ_ERROR`
- `FILE_WRITE_ERROR`
- `PARSING_ERROR`
- `INVALID_INPUT`
- `TOOL_EXECUTION_ERROR`

---

## Usage Examples

### Complete Tool Usage

```python
from annotation_toolkit.config import Config
from annotation_toolkit.di.bootstrap import bootstrap_application
from annotation_toolkit.core.conversation.generator import ConversationGenerator

# Initialize
config = Config("config.yaml")
container = bootstrap_application(config)

# Resolve tool
gen = container.resolve(ConversationGenerator)

# Use tool
gen.add_turn("Hello", "Hi there!")
output = gen.generate_json(pretty=True)
```

### With Profiling

```python
from annotation_toolkit.utils.profiling import profile_performance

@profile_performance(name="my_tool")
def process_data(data):
    # Your processing logic
    return result

# Automatic profiling
result = process_data(large_data)

# View stats
stats = process_data._profiler.get_statistics("my_tool")
print(f"Average time: {stats['avg_time']:.4f}s")
```

### With Error Recovery

```python
from annotation_toolkit.utils.recovery import exponential_retry

@exponential_retry(max_attempts=3, base_delay=1.0)
def unreliable_operation():
    # Might fail transiently
    return external_api.call()

# Automatically retries on failure
result = unreliable_operation()
```

---

For more information, see:
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [User_Manual.md](User_Manual.md) - End-user guide
- [CLAUDE.md](../CLAUDE.md) - Developer guidance
