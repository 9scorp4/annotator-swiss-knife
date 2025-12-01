# Annotation Swiss Knife - Architecture Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Architectural Principles](#architectural-principles)
3. [Layer Architecture](#layer-architecture)
4. [Core Components](#core-components)
5. [Infrastructure Layer](#infrastructure-layer)
6. [Data Flow](#data-flow)
7. [Design Patterns](#design-patterns)
8. [Module Dependencies](#module-dependencies)

---

## System Overview

The Annotation Swiss Knife is built on a clean, layered architecture that emphasizes:

- **Separation of Concerns**: Clear boundaries between UI, business logic, and infrastructure
- **Dependency Injection**: Centralized service management with lifecycle control
- **Extensibility**: Easy addition of new tools and features
- **Cross-Platform Support**: Works on macOS, Windows, and Linux
- **Production-Ready Infrastructure**: Performance monitoring, security, error recovery

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Presentation Layer                       │
├──────────────────────────┬────────────────────────────────────┤
│      GUI (PyQt5)         │      CLI (argparse)                │
│   - Main Application     │   - Command Parser                 │
│   - Tool Widgets         │   - Command Handlers               │
└──────────────────────────┴────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
├──────────────────────────┬────────────────────────────────────┤
│   Tool Implementations   │   Configuration Management         │
│   - DictToBulletList     │   - Config Loading                 │
│   - TextCleaner          │   - Environment Variables          │
│   - JsonVisualizer       │   - YAML Support                   │
│   - ConversationGenerator│                                    │
└──────────────────────────┴────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                      │
├──────────────────────────────────────────────────────────────┤
│  Performance  │  Security   │  Error      │  Logging         │
│  - Profiling  │  - Validation│  Recovery   │  - Structured   │
│  - Streaming  │  - Sanitization│ - Retry   │  - Audit Trail  │
│  - Caching    │  - Rate Limit │ - Circuit  │  - Context      │
│               │             │   Breaker   │                  │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Dependency Injection Container              │
│           Manages Service Lifecycle and Dependencies          │
└─────────────────────────────────────────────────────────────┘
```

---

## Architectural Principles

### 1. Clean Architecture

The system follows clean architecture principles:

- **Independence of Frameworks**: Business logic doesn't depend on PyQt5 or argparse
- **Testability**: Core logic can be tested without UI or external dependencies
- **Independence of UI**: Business logic works with both CLI and GUI
- **Independence of Database**: No database currently, but architecture supports it

### 2. SOLID Principles

- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Open for extension (new tools), closed for modification
- **Liskov Substitution**: All tools implement base class contracts
- **Interface Segregation**: Separate interfaces for different tool types
- **Dependency Inversion**: Depend on abstractions (base classes), not concrete implementations

### 3. Dependency Injection

All services are managed through a DI container:

- **Centralized Configuration**: Service registration in one place (`di/bootstrap.py`)
- **Lifecycle Management**: SINGLETON, TRANSIENT, SCOPED scopes
- **Testability**: Easy to mock dependencies in tests
- **Circular Dependency Detection**: Prevents circular dependencies at registration time

---

## Layer Architecture

### Presentation Layer

**GUI** (`annotation_toolkit/ui/gui/`):
- **app.py**: Main application window, tool initialization
- **widgets/**: Individual tool widgets (dict_widget.py, json_widget.py, etc.)
- **utils/fonts.py**: FontManager for centralized typography management
- **Platform-aware**: Different fonts and themes for macOS/Windows/Linux

#### Font Management

**Location**: `annotation_toolkit/ui/gui/utils/fonts.py`

**Responsibilities**:
- Centralized font selection across all UI components
- Platform-specific font fallback chains (SF Pro on macOS, Segoe UI on Windows, Ubuntu/Roboto on Linux)
- Consistent typography with predefined size constants
- Automatic font detection and initialization

**Font Size Constants**:
- `SIZE_XS` (9pt), `SIZE_SM` (11pt), `SIZE_BASE` (12pt)
- `SIZE_MD` (13pt), `SIZE_LG` (14pt), `SIZE_XL` (16pt)
- `SIZE_XXL` (18pt), `SIZE_ICON` (36pt)

**Usage**:
```python
from annotation_toolkit.ui.gui.utils.fonts import FontManager

# Initialize once at app startup
FontManager.initialize()

# Use throughout the app
label.setFont(FontManager.get_font(size=FontManager.SIZE_LG, bold=True))
code_edit.setFont(FontManager.get_code_font())
```

**CLI** (`annotation_toolkit/ui/cli/`):
- **cli.py**: Argument parser and command router
- **commands.py**: Command implementations for each tool

### Application Layer

**Core Tools** (`annotation_toolkit/core/`):
- **base.py**: Abstract base classes (`AnnotationTool`, `TextAnnotationTool`, `JsonAnnotationTool`)
- **text/**: Text processing tools (dict_to_bullet.py, text_cleaner.py)
- **conversation/**: Conversation tools (visualizer.py, generator.py)

**Configuration** (`annotation_toolkit/config.py`):
- Default configuration
- YAML file loading
- Environment variable overrides
- Nested key access with `get()` and `set()`

### Infrastructure Layer

**Performance** (`annotation_toolkit/utils/`):
- **profiling.py**: Performance monitoring, memory tracking, regression detection
- **streaming.py**: Large file handling without full memory load
- **caching**: LRU cache with TTL (configuration-driven)

**Security** (`annotation_toolkit/utils/`):
- **security.py**: Path validation, input sanitization, rate limiting
- **validation.py**: Data validation framework with streaming support

**Resilience** (`annotation_toolkit/utils/`):
- **recovery.py**: Retry strategies, circuit breaker, fallback handling
- **resources.py**: Resource management, automatic cleanup

**Observability** (`annotation_toolkit/utils/`):
- **structured_logging.py**: Enhanced logging with context, audit trails
- **error_handler.py**: Centralized error handling with decorators
- **errors.py**: Hierarchical exception classes

---

## Core Components

### Dependency Injection Container

**Location**: `annotation_toolkit/di/container.py`

**Responsibilities**:
- Service registration with factory functions
- Service resolution with dependency injection
- Lifecycle management (SINGLETON, TRANSIENT, SCOPED)
- Circular dependency detection

**Usage**:
```python
from annotation_toolkit.di import DIContainer
from annotation_toolkit.di.bootstrap import bootstrap_application

# Bootstrap container with all services
container = bootstrap_application(config)

# Resolve services
tool = container.resolve(DictToBulletList)
```

#### Lazy Tool Resolution

**Location**: `annotation_toolkit/di/bootstrap.py`

The LazyToolRegistry provides deferred tool resolution, improving application startup time by only instantiating tools when they're first accessed.

**Benefits**:
- Faster application startup
- Lower initial memory footprint
- Pay-for-what-you-use model
- Singleton caching after first resolution

**Implementation**:
```python
class LazyToolRegistry:
    """Registry for lazily resolving tools from DI container."""

    def __init__(self, container: DIContainer):
        self._container = container
        self._tool_cache = {}

    def get_tool(self, tool_class: type) -> Any:
        if tool_class not in self._tool_cache:
            self._tool_cache[tool_class] = self._container.resolve(tool_class)
        return self._tool_cache[tool_class]
```

**Usage**:
```python
# In application bootstrap
registry = LazyToolRegistry(container)

# Tools only created when first accessed
dict_tool = registry.get_tool(DictToBulletList)  # Created here
json_tool = registry.get_tool(JsonVisualizer)    # Created here
dict_tool_again = registry.get_tool(DictToBulletList)  # Retrieved from cache
```

### Configuration System

**Location**: `annotation_toolkit/config.py`

**Responsibilities**:
- Load default configuration
- Override from YAML files
- Override from environment variables
- Nested key access

**Priority** (highest to lowest):
1. Environment variables (`ANNOTATION_TOOLKIT_*`)
2. YAML configuration file
3. Default configuration

### Error Handling System

**Location**: `annotation_toolkit/utils/errors.py`, `error_handler.py`

**Exception Hierarchy**:
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

**Features**:
- Error codes for categorization
- Contextual information (file, line, function)
- Actionable suggestions
- Decorators for consistent handling

---

## Infrastructure Layer

### Performance Profiling

**Purpose**: Monitor and optimize application performance

**Components**:
- `PerformanceProfiler`: Thread-safe timing and statistics
- `MemoryProfiler`: Memory usage tracking
- `CPUProfiler`: CPU profiling with cProfile
- `RegressionDetector`: Detect performance degradations

**Integration**: Decorators (`@profile_performance`) and context managers

### Streaming Support

**Purpose**: Handle large files without loading into memory

**Components**:
- `StreamingJSONParser`: Stream JSON arrays and objects
- Chunk-based file reading

**Trigger**: Automatic for files > `streaming_threshold_mb` (default: 10MB)

### Validation Framework

**Purpose**: Validate data with detailed error reporting

**Components**:
- `ValidationResult`: Container for validation messages
- `JsonStreamingValidator`: Validate JSON with schema support
- `ConversationValidator`: Specialized conversation validation
- `TextStreamingValidator`: Text file validation

**Integration**: Use in tools before processing external data

### Error Recovery

**Purpose**: Resilient error handling with automatic retry

**Strategies**:
- **ExponentialBackoffStrategy**: Increasing delays between retries
- **LinearBackoffStrategy**: Fixed delays
- **CircuitBreaker**: Fail fast after threshold
- **Fallback**: Default values on failure

**Usage**: Decorators (`@exponential_retry`, `@circuit_breaker`)

### Structured Logging

**Purpose**: Enhanced logging for debugging and compliance

**Features**:
- Context tracking (user_id, request_id, session_id)
- Performance metrics logging
- Audit trail for compliance
- Correlation IDs for distributed tracing

**Components**:
- `StructuredLogger`: Enhanced logger
- `LoggingContext`: Context manager for tracking
- `AuditLogger`: Specialized audit logging

### Resource Management

**Purpose**: Automatic cleanup of resources

**Components**:
- `ManagedResource`: Generic resource wrapper
- `ResourcePool`: Resource pooling
- `TemporaryDirectory`: Auto-cleanup temp directories
- `ResourceTransaction`: Transaction with rollback

**Cleanup**: Global registry with atexit handlers

### Security

**Purpose**: Protect against common security vulnerabilities

**Components**:
- `PathValidator`: Prevent directory traversal
- `InputSanitizer`: Prevent XSS, SQL injection
- `RateLimiter`: Rate limiting
- `SecureFileHandler`: Secure file operations

**Protections**:
- Directory traversal attacks
- Symlink attacks (configurable)
- File size bombs
- Input injection attacks

---

## Data Flow

### CLI Command Flow

```
1. User executes command
   annotation-toolkit dict2bullet input.json --output output.md

2. CLI parser (cli.py)
   ├─ Parse arguments
   └─ Route to command handler

3. Command handler (commands.py)
   ├─ Load configuration
   ├─ Bootstrap DI container
   ├─ Resolve tool from container
   └─ Execute tool.process()

4. Tool execution
   ├─ Validate input
   ├─ Process data
   └─ Return result

5. Output handling
   ├─ Write to file (if --output)
   └─ Print to stdout (if no --output)
```

### GUI Tool Flow

```
1. User interaction
   ├─ Paste data into input area
   └─ Click "Process" button

2. Widget event handler
   ├─ Get input text
   └─ Call tool.process()

3. Tool execution
   ├─ Validate input
   ├─ Process data
   └─ Return result

4. Display result
   ├─ Update output area
   └─ Update status bar
```

### Dependency Resolution Flow

```
1. Application startup
   ├─ Load configuration
   └─ Bootstrap DI container

2. Service registration (bootstrap.py)
   ├─ Register factories
   └─ Specify dependencies

3. Service resolution
   ├─ Request service from container
   ├─ Resolve dependencies recursively
   ├─ Call factory with dependencies
   └─ Return service instance

4. Lifecycle management
   ├─ SINGLETON: Cache instance
   ├─ TRANSIENT: New instance each time
   └─ SCOPED: Instance per scope
```

---

## Design Patterns

### Factory Pattern

**Used for**: Tool creation with dependency injection

**Location**: `di/bootstrap.py`

```python
def create_dict_to_bullet(config: ConfigInterface, logger: LoggerInterface) -> DictToBulletList:
    markdown_output = config.get("tools", "dict_to_bullet", "markdown_output", default=True)
    return DictToBulletList(markdown_output=markdown_output)
```

### Decorator Pattern

**Used for**: Error handling, profiling, retry logic

**Locations**: `error_handler.py`, `profiling.py`, `recovery.py`

```python
@with_error_handling(error_code=ErrorCode.PROCESSING_ERROR)
@profile_performance(name="process_data")
@exponential_retry(max_attempts=3)
def process_data(data):
    # Implementation
    pass
```

### Strategy Pattern

**Used for**: Retry strategies, validation strategies

**Location**: `recovery.py`, `validation.py`

```python
class ExponentialBackoffStrategy(ErrorRecoveryStrategy):
    def get_delay(self, attempt: int) -> float:
        return min(self.base_delay * (2 ** attempt), self.max_delay)
```

### Observer Pattern

**Used for**: GUI event handling, logging

**Location**: `ui/gui/widgets/`

```python
# PyQt signal/slot mechanism
process_button.clicked.connect(self.on_process_clicked)
```

### Template Method Pattern

**Used for**: Base tool classes

**Location**: `core/base.py`

```python
class JsonAnnotationTool(AnnotationTool):
    def process(self, data: Any) -> Any:
        # Template method
        return self.process_json(data)

    @abstractmethod
    def process_json(self, json_data: Union[Dict, List]) -> Any:
        # Subclasses implement this
        pass
```

### Circuit Breaker Pattern

**Used for**: Resilient external service calls

**Location**: `recovery.py`

```python
@circuit_breaker(failure_threshold=5, timeout=60)
def call_external_service():
    # Fails fast after 5 consecutive failures
    pass
```

---

## Module Dependencies

### Dependency Graph

```
┌─────────────┐
│     UI      │ (GUI/CLI)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Tools    │ (Core business logic)
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│    Config   │────▶│  DI Container│
└──────┬──────┘     └──────────────┘
       │
       ▼
┌─────────────┐
│    Utils    │ (Infrastructure)
└─────────────┘
```

### Import Rules

1. **UI layer** can import from Tools and Utils
2. **Tools layer** can import from Utils
3. **Utils layer** should not import from Tools or UI (except type hints)
4. **Config** can be imported from anywhere
5. **DI Container** can be imported from anywhere

### External Dependencies

**Core**:
- Python 3.8+
- PyYAML (configuration)

**GUI**:
- PyQt5 (graphical interface)

**CLI**:
- argparse (built-in)

**Optional**:
- psutil (memory profiling)
- ijson (streaming JSON)
- pytest-cov (test coverage)

---

## Extensibility Points

### Adding a New Tool

1. Create tool class inheriting from `AnnotationTool` (or `TextAnnotationTool`/`JsonAnnotationTool`)
2. Implement required methods (`name`, `description`, `process_*()`)
3. Create factory function in `di/bootstrap.py`
4. Register in `configure_services()`
5. Add to `get_tool_instances()`
6. Create widget in `ui/gui/widgets/` (optional)
7. Add CLI command in `ui/cli/commands.py` (optional)

### Adding Infrastructure Module

1. Create module in `annotation_toolkit/utils/`
2. Define classes and functions
3. Add configuration section in `config.py` default config
4. Document in `CLAUDE.md` and relevant docs
5. Write tests in `tests/utils/`

### Adding Configuration Options

1. Add to `Config.DEFAULT_CONFIG` in `config.py`
2. Document in `CONFIGURATION_REFERENCE.md`
3. Update example config in `README.md` and `User_Manual.md`

---

## Performance Considerations

### Caching Strategy

- LRU cache with configurable TTL and automatic cleanup
- Disabled by default
- Enable via `performance.enable_caching: true`
- **New in v0.6.0**: TTLCache automatically cleans up expired entries every 60 seconds
- Prevents memory bloat in long-running processes
- Cleanup triggered on cache access (amortized cost)

### Profiling Optimizations

- **New in v0.6.0**: O(1) bounded statistics storage using `deque`
- Efficient memory usage for performance metrics
- Pre-compiled regex patterns for faster validation
- Lazy configuration loading in security module

### Streaming Threshold

- Files > 10MB use streaming automatically
- Configurable via `performance.streaming_threshold_mb`

### Memory Management

- File handles automatically closed (context managers)
- Temporary files automatically cleaned (atexit handlers)
- Resource pools for reusable resources

### Profiling

- Disable in production: `performance.enable_profiling: false`
- Enable for debugging performance issues

---

## Security Considerations

### Input Validation

- All user inputs validated before processing
- Path validation prevents directory traversal
- File size limits prevent resource exhaustion

### Rate Limiting

- Configurable per-operation rate limits
- Prevents abuse and DoS

### Secure File Operations

- `SecureFileHandler` combines multiple security checks
- Symlink detection (configurable)
- Path length limits

### Sensitive Data

- No sensitive data in logs (configurable log levels)
- Audit trail for compliance
- Input sanitization prevents injection attacks

---

## Testing Strategy

### Unit Tests

- Each module has corresponding test file
- Tests in `tests/` mirror `annotation_toolkit/` structure
- Use unittest framework

### Integration Tests

- Test DI container service resolution
- Test CLI commands end-to-end
- Test GUI tool integration

### Coverage

- Run with `python -m tests.run_tests --coverage`
- Requires pytest-cov

---

## Future Enhancements

### Potential Additions

1. **Database Support**: Add persistence layer
2. **API Server**: RESTful API for tools
3. **Plugin System**: Load tools from external packages
4. **Distributed Processing**: Multi-machine processing
5. **Real-time Collaboration**: Multi-user annotation

### Architectural Considerations

- Keep clean separation of concerns
- Maintain backward compatibility
- Follow existing patterns
- Comprehensive documentation

---

For more details, see:
- [CLAUDE.md](../CLAUDE.md) - Developer guidance
- [SECURITY.md](SECURITY.md) - Security features and best practices
- [PERFORMANCE.md](PERFORMANCE.md) - Performance optimization
- [API_REFERENCE.md](API_REFERENCE.md) - Complete API documentation
