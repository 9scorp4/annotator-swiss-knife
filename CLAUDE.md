# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Annotation Swiss Knife is a comprehensive data annotation toolkit that provides multiple annotation tools through both GUI and CLI interfaces. The project emphasizes clean architecture with dependency injection, comprehensive error handling, and cross-platform support (macOS, Windows, Linux).

## Core Architecture

### Dependency Injection System

The project uses a custom DI container (`annotation_toolkit/di/`) for managing service lifecycles and dependencies:

- **DIContainer** (`di/container.py`): Main container managing service registration and resolution with circular dependency detection
- **Bootstrap** (`di/bootstrap.py`): Application-level service configuration. Use `bootstrap_application(config)` to initialize the DI container with all services
- **Service Scopes**: Supports SINGLETON (default), TRANSIENT, and SCOPED lifecycles
- **Factory Pattern**: Tools are created via factory functions that inject Config and Logger dependencies

**Key Pattern**: When adding new tools, register them in `di/bootstrap.py` using `container.register_factory()` with appropriate dependencies.

### Tool Base Classes

All annotation tools inherit from base classes in `annotation_toolkit/core/base.py`:

- **AnnotationTool**: Abstract base requiring `name`, `description`, and `process()` method
- **TextAnnotationTool**: For text processing tools, implements `process_text(text: str) -> str`
- **JsonAnnotationTool**: For JSON/dict processing, implements `process_json(json_data: Union[Dict, List]) -> Any`

Tools are automatically resolved from the DI container in both CLI and GUI applications.

### Configuration System

Configuration is managed through `annotation_toolkit/config.py` with multiple layers:

1. **Default Configuration**: Defined in `Config.DEFAULT_CONFIG`
2. **YAML Files**: Load custom config via `Config(config_path)`
3. **Environment Variables**: Override with `ANNOTATION_TOOLKIT_*` prefix (e.g., `ANNOTATION_TOOLKIT_UI_THEME=dark`)

Config supports nested keys with the `get()` and `set()` methods. Security and performance settings are centralized here.

### Error Handling System

Comprehensive error handling defined in `annotation_toolkit/utils/errors.py` and `error_handler.py`:

- **Hierarchical Exceptions**: All exceptions inherit from `AnnotationToolkitError`
- **Error Codes**: Enumerated in `ErrorCode` for categorization
- **Context-Rich Errors**: Include file paths, line numbers, error details, and actionable suggestions
- **Decorators**: Use `@with_error_handling()` decorator for consistent error handling
- **Safe Execution**: Use `safe_execute()` for exception handling with fallback values

## Version Management & CI/CD

### Version Numbering

The project uses **setuptools-scm** for automatic version management based on git tags:

- **Version source of truth:** Git tags (e.g., `v0.3.0`, `v1.0.0`)
- **Semantic versioning:** MAJOR.MINOR.PATCH format
- **Pre-releases:** Support for beta, rc, alpha tags (e.g., `v1.0.0-beta.1`)
- **Development builds:** Include commit hash (e.g., `0.3.0.dev12+gabc1234`)

**Check current version:**
```bash
python -c "from annotation_toolkit import __version__; print(__version__)"
```

### CI/CD Pipeline

The project has automated CI/CD workflows in `.github/workflows/`:

**Continuous Integration** (`ci.yml`):
- Runs on every push/PR to main and develop branches
- Multi-version Python testing (3.8-3.12)
- Test coverage reporting with Codecov
- Package build verification
- Fast tests run on all branches, slow tests only on main

**Continuous Deployment** (`release.yml`):
- Triggers on git tags matching `v*.*.*`
- Builds executables for macOS, Windows, and Linux in parallel
- Generates SHA256 checksums for all artifacts
- Creates GitHub Releases with auto-generated release notes
- Attaches executables to releases
- Supports manual triggering via workflow_dispatch
- Detects pre-releases (beta, rc, alpha) automatically

### Creating a Release

See [docs/RELEASE_PROCESS.md](docs/RELEASE_PROCESS.md) for detailed instructions.

**Quick release process:**

```bash
# 1. Update CHANGELOG.md with release notes

# 2. Commit changes
git add .
git commit -m "Prepare for v1.0.0 release"
git push origin main

# 3. Create and push version tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# GitHub Actions automatically:
# - Builds macOS (.app), Windows (.exe), and Linux (binary) executables
# - Creates GitHub Release
# - Attaches executables with SHA256 checksums
# - Generates release notes with installation instructions
```

**Pre-release example:**
```bash
git tag -a v1.0.0-beta.1 -m "Release version 1.0.0-beta.1"
git push origin v1.0.0-beta.1
# Automatically marked as pre-release on GitHub
```

## Development Commands

### Running the Application

**GUI Application:**
```bash
# Using run scripts (recommended)
./scripts/run/run.sh gui              # macOS/Linux
scripts\run\run.bat gui               # Windows

# Direct invocation
annotation-toolkit gui
python -m annotation_toolkit.cli gui
```

**CLI Tools:**
```bash
# Dictionary to Bullet List
annotation-toolkit dict2bullet input.json --output output.md --format markdown

# JSON Visualizer (handles conversations and generic JSON)
annotation-toolkit jsonvis data.json --output formatted.txt --search "query"

# Text Cleaner
annotation-toolkit textclean input.txt --output cleaned.txt

# Conversation Generator
annotation-toolkit convgen input.json --output conversation.json --format pretty
```

### Testing

**Run all tests:**
```bash
python -m tests.run_tests
```

**Run with coverage:**
```bash
python -m tests.run_tests --coverage
```

**Run specific test file:**
```bash
python -m unittest tests.test_config
python -m unittest tests.core.test_dict_to_bullet
```

**Test options:**
- `-v 3`: Verbose output
- `-f`: Fail fast (stop on first failure)
- `-d utils`: Run tests in specific directory

### Building Executables

**Automated Builds (Recommended):**
Executables are automatically built via CI/CD when you create a git tag. See the "Creating a Release" section above.

**Manual Local Builds:**
You can also build executables locally for testing:

```bash
# macOS
./scripts/build/build_mac.sh

# Windows
scripts\build\build_windows.bat

# Linux
./scripts/build/build_linux.sh
```

See `docs/README_BUILD.md` for detailed local build instructions. PyInstaller specs are in `scripts/build/`.

### Setup

**First-time setup:**
```bash
./scripts/setup/setup.sh        # macOS/Linux
scripts\setup\setup.ps1         # Windows PowerShell
scripts\setup\setup.bat         # Windows CMD
```

This creates a virtual environment and installs all dependencies from `requirements.txt`.

## Important Patterns

### Adding a New Annotation Tool

1. **Create tool class** inheriting from appropriate base class in `annotation_toolkit/core/`
2. **Implement required methods**: `name`, `description`, and `process_text()` or `process_json()`
3. **Add factory function** in `di/bootstrap.py`:
   ```python
   def create_my_tool(config: ConfigInterface, logger_service: LoggerInterface) -> MyTool:
       # Get config values
       setting = config.get("tools", "my_tool", "setting", default=True)
       return MyTool(setting=setting)
   ```
4. **Register in `configure_services()`**:
   ```python
   container.register_factory(
       interface=MyTool,
       factory=create_my_tool,
       scope=ServiceScope.SINGLETON,
       config=ConfigInterface,
       logger_service=LoggerInterface,
   )
   ```
5. **Add UI widget** in `annotation_toolkit/ui/gui/widgets/` if needed
6. **Update `get_tool_instances()`** in `di/bootstrap.py` to resolve the tool
7. **Add CLI command** in `annotation_toolkit/ui/cli/commands.py`

### Tool Resolution Pattern

Both CLI and GUI resolve tools through the DI container:

```python
# Bootstrap the DI container
container = bootstrap_application(config)

# Get all tool instances
tools = get_tool_instances(container)

# Or resolve specific tool
tool = container.resolve(DictToBulletList)
```

The GUI application (`ui/gui/app.py`) initializes tools in `_initialize_tools()` with fallback to manual initialization if DI fails.

### Configuration Override Pattern

Configuration can be layered:

```python
# Default config
config = Config()

# Load from file
config = Config("custom_config.yaml")

# Environment variable override (highest priority)
export ANNOTATION_TOOLKIT_UI_THEME=dark
export ANNOTATION_TOOLKIT_DATA_AUTOSAVE=true
```

### Error Handling Pattern

Use decorators for consistent error handling:

```python
from annotation_toolkit.utils import with_error_handling, ErrorCode

@with_error_handling(
    error_code=ErrorCode.PROCESSING_ERROR,
    suggestion="Check the input data format"
)
def process_data(data):
    # Implementation
    pass
```

Raise specific exceptions with context:

```python
from annotation_toolkit.utils.errors import TypeValidationError

if not isinstance(data, dict):
    raise TypeValidationError(
        "data",
        dict,
        type(data),
        suggestion="Ensure you're passing a dictionary."
    )
```

## Key Entry Points

- **CLI Main**: `annotation_toolkit/cli.py` - Command-line interface entry point with argument parsing
- **GUI Main**: `annotation_toolkit/ui/gui/app.py` - PyQt5 GUI application with DI integration
- **DI Bootstrap**: `annotation_toolkit/di/bootstrap.py` - Service configuration and container setup
- **Config Manager**: `annotation_toolkit/config.py` - Configuration loading with YAML and env var support
- **Base Classes**: `annotation_toolkit/core/base.py` - Abstract base classes for all tools

## Cross-Platform Considerations

The project supports Windows, macOS, and Linux:

- Scripts provided in `.sh`, `.ps1`, and `.bat` formats
- Path handling uses `Path` from `pathlib` for cross-platform compatibility
- GUI fonts are platform-aware (SF Pro on macOS, Segoe UI on Windows, Ubuntu/Roboto on Linux)
- Theme detection supports both light and dark system preferences

## Testing Architecture

Test structure mirrors the main package:

- `tests/core/` - Core functionality tests
- `tests/utils/` - Utility module tests
- `tests/test_cli.py` - CLI command tests
- `tests/test_config.py` - Configuration tests
- `tests/test_dependency_injection.py` - DI system tests

Tests use unittest framework with optional pytest-cov for coverage reporting.

## Infrastructure Modules

The toolkit includes advanced infrastructure modules in `annotation_toolkit/utils/` for production-grade applications.

### Performance Profiling (`profiling.py`)

Monitor and optimize application performance with detailed statistics.

**Key Classes**:
- `PerformanceProfiler`: Thread-safe profiling with statistics (avg, min, max, percentiles)
- `MemoryProfiler`: Memory usage tracking (requires psutil)
- `CPUProfiler`: CPU profiling with cProfile integration
- `RegressionDetector`: Detect performance degradations

**Usage**:
```python
from annotation_toolkit.utils.profiling import profile_performance, PerformanceProfiler

@profile_performance(name="my_operation")
def expensive_operation():
    # Your code here
    pass

# Or use directly
profiler = PerformanceProfiler()
with profiler.profile("operation_name"):
    # Code to profile
    pass

stats = profiler.get_statistics("operation_name")
# Returns: call_count, total_time, avg_time, min_time, max_time,
#          median, std_dev, p95, p99
```

### Streaming Support (`streaming.py`)

Handle large files efficiently without loading entire contents into memory.

**Key Classes**:
- `StreamingJSONParser`: Stream large JSON files (uses ijson when available)

**Usage**:
```python
from annotation_toolkit.utils.streaming import StreamingJSONParser

parser = StreamingJSONParser()

# Stream array elements one by one
for item in parser.stream_array("large_file.json"):
    process(item)

# Stream object key-value pairs
for key, value in parser.stream_object("data.json"):
    process(key, value)
```

**When to use**: Files > 10MB (configurable via `performance.streaming_threshold_mb`)

### Validation Framework (`validation.py`)

Validate data with detailed error reporting and streaming support.

**Key Classes**:
- `ValidationResult`: Container for validation results with severity levels
- `JsonStreamingValidator`: Validate JSON against schemas with streaming
- `ConversationValidator`: Specialized conversation data validation
- `TextStreamingValidator`: Text file validation

**Usage**:
```python
from annotation_toolkit.utils.validation import validate_json_file, validate_conversation_file

# Validate JSON against schema
result = validate_json_file("data.json", schema=my_schema)
if not result.is_valid:
    for message in result.messages:
        print(f"{message.severity}: {message.message}")

# Validate conversation data
result = validate_conversation_file("conversation.json", max_turns=20)
```

**Integration**: Use in tools that process external data for early error detection.

### Error Recovery (`recovery.py`)

Implement robust error handling with automatic retry and circuit breaker patterns.

**Key Classes**:
- `ExponentialBackoffStrategy`: Retry with exponential backoff
- `LinearBackoffStrategy`: Retry with linear delays
- `CircuitBreaker`: Circuit breaker pattern (OPEN/CLOSED/HALF_OPEN states)
- `FallbackHandler`: Execute with fallback options
- `RetryableOperation`: Wrapper for retry logic

**Usage**:
```python
from annotation_toolkit.utils.recovery import exponential_retry, circuit_breaker

@exponential_retry(max_attempts=3, base_delay=1.0)
def unreliable_operation():
    # Operation that might fail transiently
    pass

@circuit_breaker(failure_threshold=5, timeout=60)
def external_service_call():
    # Fails fast after threshold
    pass
```

**When to use**:
- Network operations that might fail transiently
- External service calls
- File operations with potential locks

### Structured Logging (`structured_logging.py`)

Enhanced logging with context tracking, performance metrics, and audit trails.

**Key Classes**:
- `StructuredLogger`: Enhanced logger with context support
- `LoggingContext`: Context manager for correlation IDs and user tracking
- `PerformanceTracker`: Track operation performance with logging
- `AuditLogger`: Specialized audit trail logging

**Usage**:
```python
from annotation_toolkit.utils.structured_logging import StructuredLogger, LoggingContext

logger = StructuredLogger("my_module")

with LoggingContext(user_id="user123", request_id="req456"):
    logger.info("Processing request", extra={"item_count": 42})
    # All logs include user_id and request_id
```

**Benefits**:
- Distributed tracing with correlation IDs
- Compliance/audit requirements
- Performance debugging

### Resource Management (`resources.py`)

Automatic cleanup of file handles, temporary files, and pooled resources.

**Key Classes**:
- `ManagedResource`: Generic resource wrapper with cleanup
- `ResourcePool`: Pool for managing shared resources
- `ManagedFileHandle`: File handle wrapper with auto-close
- `TemporaryDirectory`: Auto-cleanup temp directories
- `ResourceTransaction`: Transaction manager with rollback

**Usage**:
```python
from annotation_toolkit.utils.resources import managed_file, temporary_file

# Managed file handles
with managed_file("/path/to/file.txt", mode="r") as f:
    content = f.read()
# Automatically closed

# Temporary files
with temporary_file(suffix=".json") as temp_path:
    # Use temporary file
    process_file(temp_path)
# Automatically deleted
```

**Important**: Resources are registered globally and cleaned up via atexit handlers.

### Security Utilities (`security.py`)

Path validation, input sanitization, rate limiting, and secure file operations.

**Key Classes**:
- `PathValidator`: Validate paths, prevent directory traversal
- `FileSizeValidator`: Enforce file size limits
- `RateLimiter`: Request rate limiting
- `InputSanitizer`: Sanitize input for XSS, SQL injection
- `SecureFileHandler`: Secure file operations with validation

**Usage**:
```python
from annotation_toolkit.utils.security import PathValidator, SecureFileHandler

# Path validation
validator = PathValidator(allowed_base="/safe/path")
if validator.validate_path(user_provided_path):
    # Safe to use
    process_file(user_provided_path)

# Secure file handler
handler = SecureFileHandler(allowed_base="/safe/path", max_file_size_mb=100)
data = handler.read_file(filepath)  # Validated before reading
```

**Critical for**:
- User-provided file paths
- External data processing
- Any operation with security implications

### Configuration for Infrastructure

Add to `config.yaml`:

```yaml
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

error_recovery:
  max_retry_attempts: 3
  base_retry_delay: 1.0
  max_retry_delay: 30.0
  circuit_breaker_threshold: 10
  circuit_breaker_timeout: 120
```

## Special Features

### JSON Visualizer

Handles multiple conversation formats:
- Standard format: `[{"role": "user", "content": "..."}, ...]`
- Chat history format: `{"chat_history": [...]}`
- Message_v2 format: `[{"source": "user", "version": "message_v2", "body": "..."}, ...]`

Also repairs malformed JSON and formats embedded XML tags.

### Conversation Generator

Builds AI conversation JSON data turn-by-turn with validation.

**Key Features**:
- Add up to 20 conversation turns (configurable via `max_turns`)
- Validates messages are non-empty strings
- Load from JSON, export to JSON (pretty or compact)
- Implements `JsonAnnotationTool` interface

**Usage**:
```python
from annotation_toolkit.core.conversation.generator import ConversationGenerator

gen = ConversationGenerator(max_turns=20)
gen.add_turn("User message", "Assistant response")
json_output = gen.generate_json(pretty=True)

# Or load existing conversation
gen.load_from_json([
    {"role": "user", "content": "Hi!"},
    {"role": "assistant", "content": "Hello!"}
])
```

**CLI**:
```bash
annotation-toolkit convgen input.json --output conversation.json --format pretty
```

**Input format** (JSON file):
```json
{
  "turns": [
    {"user": "message1", "assistant": "response1"},
    {"user": "message2", "assistant": "response2"}
  ]
}
```

### Security Configuration

Security settings in `config.py` include:
- File size limits and path length validation
- Rate limiting for operations
- Path validation with symlink detection
- Encoding auto-detection with fallback options

### Performance Configuration

Performance settings control:
- Caching (LRU cache with TTL)
- Streaming for large files
- Retry logic with exponential backoff
