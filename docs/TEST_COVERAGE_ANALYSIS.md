# Annotation Swiss Knife - Comprehensive Test Coverage Analysis

## Executive Summary

The Annotation Swiss Knife is a comprehensive data annotation toolkit with **~10,000+ lines of code** across multiple layers:
- **Core modules** (2,010 lines): Annotation tools and algorithms
- **Utility modules** (7,993 lines): Infrastructure, validation, security, streaming, profiling
- **Existing tests** (1,703 lines): Limited coverage focusing on core tools and config

**Current test coverage is approximately 17% of total codebase.** This document identifies all modules and features that require test coverage.

---

## 1. CORE MODULES (annotation_toolkit/core/)

### 1.1 Base Classes & Interfaces
**File**: `/annotation_toolkit/core/base.py` (169 lines)
**Status**: Partially tested via tool tests

**Classes to test**:
- `AnnotationTool` (abstract base)
- `TextAnnotationTool` (base class for text tools)
- `JsonAnnotationTool` (base class for JSON tools)

**What to test**:
- [ ] Tool initialization and property access
- [ ] Abstract method enforcement
- [ ] Process method delegation to specialized methods
- [ ] Error handling and exception propagation
- [ ] Logging output
- [ ] Type validation in JsonAnnotationTool
- [ ] Return value assertions for TextAnnotationTool
- [ ] Exception context and error code assignment

---

### 1.2 Text Tools
**Location**: `/annotation_toolkit/core/text/`

#### 1.2.1 DictToBulletList
**File**: `dict_to_bullet.py` (estimated 150+ lines)
**Status**: Partially tested in `tests/core/test_dict_to_bullet.py`

**Tests needed**:
- [x] Basic initialization
- [x] Valid JSON processing
- [x] Invalid JSON handling
- [ ] Edge cases:
  - [ ] Empty dictionaries
  - [ ] Very large dictionaries (performance)
  - [ ] Unicode and special characters
  - [ ] Nested dictionaries
  - [ ] Mixed data types in values
  - [ ] URL detection and title extraction
  - [ ] Markdown vs text output formatting
  - [ ] Different text encoding inputs

#### 1.2.2 TextCleaner
**File**: `text_cleaner.py` (estimated 150+ lines)
**Status**: No tests exist

**Tests needed**:
- [ ] Initialization and configuration
- [ ] Whitespace normalization (leading/trailing/multiple spaces)
- [ ] Line break handling
- [ ] Special character handling
- [ ] Case conversion (upper/lower/title)
- [ ] Accent removal and unicode normalization
- [ ] Duplicate line removal
- [ ] Empty line handling
- [ ] Regular expression pattern matching
- [ ] Performance with large text files
- [ ] Encoding detection and handling
- [ ] Error handling for invalid inputs

#### 1.2.3 TextCollector
**File**: `text_collector.py` (estimated 150+ lines)
**Status**: Partially tested in `tests/core/test_text_collector.py`

**Tests needed**:
- [x] Basic initialization
- [ ] Text field collection
- [ ] Maximum field limit enforcement
- [ ] Empty field filtering
- [ ] Field validation
- [ ] JSON output generation
- [ ] Error handling for invalid inputs
- [ ] Large text handling
- [ ] Unicode support
- [ ] Memory efficiency with many fields

---

### 1.3 Conversation Tools
**Location**: `/annotation_toolkit/core/conversation/`

#### 1.3.1 ConversationGenerator
**File**: `generator.py` (estimated 200+ lines)
**Status**: No tests exist

**Tests needed**:
- [ ] Initialization with default and custom max_turns
- [ ] Tool name and description properties
- [ ] Adding turns to conversation
- [ ] Maximum turn limit enforcement
- [ ] Empty message validation
- [ ] Non-empty message validation
- [ ] Conversation JSON generation (pretty and compact)
- [ ] Loading from existing JSON
- [ ] Turn order preservation
- [ ] Special character handling in messages
- [ ] Unicode support
- [ ] Very long message handling
- [ ] Error handling and exceptions
- [ ] Reset/clear conversation
- [ ] Conversation state inspection

#### 1.3.2 JsonVisualizer
**File**: `visualizer.py` (estimated 300+ lines)
**Status**: No tests exist

**Key classes**:
- `TTLCache` - Time-to-live cache with expiration
- `JsonVisualizer` - Main visualization tool

**Tests needed**:
- [ ] **TTLCache**:
  - [ ] Item storage and retrieval
  - [ ] TTL expiration
  - [ ] Cache size limits
  - [ ] Oldest item eviction
  - [ ] Cache hit/miss tracking
  - [ ] Concurrent access safety

- [ ] **JsonVisualizer**:
  - [ ] JSON parsing and validation
  - [ ] Conversation format detection (standard/chat_history/message_v2)
  - [ ] Markdown formatting
  - [ ] Text formatting
  - [ ] XML tag handling
  - [ ] Malformed JSON repair
  - [ ] Search functionality
  - [ ] Large JSON file handling (streaming)
  - [ ] File size validation
  - [ ] Unicode content handling
  - [ ] Color formatting
  - [ ] Caching behavior
  - [ ] Error handling for corrupted data

---

## 2. UTILITY MODULES (annotation_toolkit/utils/)

### 2.1 Error Handling System

#### 2.1.1 Errors Module
**File**: `/utils/errors.py` (700+ lines)
**Status**: Partially tested in `tests/utils/test_error_handler.py`

**Classes to test**:
- `ErrorCode` enum
- `ErrorContext` class
- Exception hierarchy:
  - `AnnotationToolkitError` (base)
  - `ConfigurationError`
  - `InputValidationError`, `TypeValidationError`, `ValueValidationError`
  - `ProcessingError`, `TransformationError`, `ParsingError`
  - `FileNotFoundError`, `FileReadError`, `FileWriteError`
  - `ResourceError`, `ValidationError`
  - `ToolExecutionError`, `ServiceError`
  - And more specialized exceptions

**Tests needed**:
- [ ] Error code enumeration
- [ ] Exception initialization with all parameters
- [ ] Error message formatting
- [ ] Details dictionary handling
- [ ] Suggestion/recommendation generation
- [ ] Cause exception chaining
- [ ] String representation
- [ ] Error code categorization
- [ ] Custom exception attributes
- [ ] Safe execute decorator
- [ ] Error context extraction
- [ ] Multiple exception inheritance behavior

#### 2.1.2 Error Handler Module
**File**: `/utils/error_handler.py` (400+ lines)
**Status**: Partially tested

**Classes/Functions to test**:
- `with_error_handling()` decorator
- `handle_errors()` context manager
- `format_error_for_user()` function
- `safe_execute()` function
- `ErrorLogger` class

**Tests needed**:
- [ ] Decorator application and function wrapping
- [ ] Exception catching and re-raising
- [ ] Error code assignment
- [ ] Error message formatting
- [ ] User-friendly error display
- [ ] Stack trace handling
- [ ] Context manager usage
- [ ] Nested error handling
- [ ] Fallback value provision
- [ ] Silent error mode
- [ ] Exception wrapping
- [ ] Logging integration

---

### 2.2 Validation Framework

#### 2.2.1 Validation Module
**File**: `/utils/validation.py` (500+ lines)
**Status**: No tests exist

**Classes to test**:
- `ValidationSeverity` enum
- `ValidationMessage` dataclass
- `ValidationResult` class
- `JsonStreamingValidator`
- `ConversationValidator`
- `TextStreamingValidator`
- Helper functions: `validate_json_file()`, `validate_conversation_file()`

**Tests needed**:
- [ ] Validation result creation and message collection
- [ ] Severity level handling (ERROR, WARNING, INFO)
- [ ] JSON schema validation
- [ ] Streaming JSON validation
- [ ] Conversation format validation
- [ ] Max turns enforcement
- [ ] Text file validation
- [ ] Encoding validation
- [ ] Empty file handling
- [ ] Large file streaming
- [ ] Error message generation
- [ ] Location tracking in validation
- [ ] Detail capture
- [ ] Validation result serialization
- [ ] Custom validator registration

---

### 2.3 Security Module

#### 2.3.1 Security Utilities
**File**: `/utils/security.py` (450+ lines)
**Status**: No tests exist

**Classes to test**:
- `PathValidator` - Path validation and sanitization
- `FileSizeValidator` - File size enforcement
- `RateLimiter` - Request rate limiting
- `InputSanitizer` - Input sanitization
- `SecureFileHandler` - Secure file operations

**Tests needed**:
- [ ] **PathValidator**:
  - [ ] Valid path acceptance
  - [ ] Directory traversal prevention
  - [ ] Symlink detection and prevention
  - [ ] Absolute path resolution
  - [ ] Allowed directory validation
  - [ ] Path length validation
  - [ ] Hidden file handling
  - [ ] Windows path handling
  - [ ] Relative path conversion
  - [ ] Invalid path rejection

- [ ] **FileSizeValidator**:
  - [ ] File existence checking
  - [ ] Size limit enforcement
  - [ ] Exact size matching
  - [ ] Size range validation
  - [ ] Large file handling
  - [ ] Error reporting

- [ ] **RateLimiter**:
  - [ ] Request counting
  - [ ] Window tracking
  - [ ] Rate limit enforcement
  - [ ] Request rejection
  - [ ] Time window expiration
  - [ ] Concurrent access
  - [ ] Reset functionality

- [ ] **InputSanitizer**:
  - [ ] XSS prevention
  - [ ] SQL injection prevention
  - [ ] HTML encoding
  - [ ] URL encoding
  - [ ] Special character handling
  - [ ] Unicode handling

- [ ] **SecureFileHandler**:
  - [ ] File validation before operations
  - [ ] Size limit enforcement
  - [ ] Path validation
  - [ ] Read operation security
  - [ ] Write operation security
  - [ ] Permission checking
  - [ ] Atomic operations

**Global functions to test**:
- `generate_file_hash()` - Hash computation
- `validate_encoding()` - Encoding validation
- `default_path_validator` - Default validator instance
- `default_file_size_validator` - Default size validator
- `default_input_sanitizer` - Default sanitizer

---

### 2.4 Infrastructure Modules

#### 2.4.1 Performance Profiling Module
**File**: `/utils/profiling.py` (600+ lines)
**Status**: No tests exist

**Classes to test**:
- `ProfileStats` dataclass
- `MemoryStats` dataclass
- `PerformanceProfiler` - Main profiler
- `MemoryProfiler` - Memory tracking
- `CPUProfiler` - CPU profiling
- `RegressionDetector` - Performance regression detection
- `profile_performance()` decorator

**Tests needed**:
- [ ] **PerformanceProfiler**:
  - [ ] Operation timing
  - [ ] Call count tracking
  - [ ] Min/max/average calculation
  - [ ] Percentile computation (p95, p99)
  - [ ] Standard deviation
  - [ ] Thread safety
  - [ ] Statistics retrieval
  - [ ] Recent times tracking
  - [ ] Reset functionality

- [ ] **MemoryProfiler**:
  - [ ] Memory usage tracking
  - [ ] Peak memory detection
  - [ ] Memory delta calculation
  - [ ] GC integration
  - [ ] psutil availability handling

- [ ] **CPUProfiler**:
  - [ ] CPU profiling with cProfile
  - [ ] Statistics generation
  - [ ] Report formatting
  - [ ] Top functions identification

- [ ] **RegressionDetector**:
  - [ ] Baseline establishment
  - [ ] Regression detection
  - [ ] Threshold configuration
  - [ ] Comparison operations
  - [ ] Report generation

- [ ] **Decorator**:
  - [ ] Function decoration
  - [ ] Automatic profiling
  - [ ] Result passthrough
  - [ ] Exception handling
  - [ ] Statistics export

---

#### 2.4.2 Streaming Module
**File**: `/utils/streaming.py` (400+ lines)
**Status**: No tests exist

**Classes to test**:
- `StreamingJSONParser` - Stream JSON arrays/objects

**Functions to test**:
- `stream_array_from_file()`
- `stream_object_from_file()`
- `create_stream_processor()`

**Tests needed**:
- [ ] **StreamingJSONParser**:
  - [ ] JSON array streaming
  - [ ] JSON object streaming
  - [ ] Chunk size configuration
  - [ ] Large file handling
  - [ ] Memory efficiency
  - [ ] Iterator protocol
  - [ ] Exception handling
  - [ ] File reading errors
  - [ ] ijson availability fallback
  - [ ] Partial JSON handling

- [ ] **Stream functions**:
  - [ ] Array item iteration
  - [ ] Object key-value iteration
  - [ ] File path validation
  - [ ] Error recovery
  - [ ] Progress tracking

---

#### 2.4.3 Recovery Module
**File**: `/utils/recovery.py` (500+ lines)
**Status**: No tests exist

**Classes to test**:
- `CircuitBreakerState` enum
- `RecoveryAttempt` dataclass
- `ErrorRecoveryStrategy` base class
- `ExponentialBackoffStrategy`
- `LinearBackoffStrategy`
- `CircuitBreaker`
- `FallbackHandler`
- `RetryableOperation`

**Decorators to test**:
- `@exponential_retry()`
- `@linear_retry()`
- `@circuit_breaker()`
- `@with_fallback()`

**Tests needed**:
- [ ] **Retry Strategies**:
  - [ ] Exponential backoff calculation
  - [ ] Linear backoff calculation
  - [ ] Jitter application
  - [ ] Max delay enforcement
  - [ ] Attempt counting
  - [ ] Retry decision making

- [ ] **CircuitBreaker**:
  - [ ] State transitions (CLOSED -> OPEN -> HALF_OPEN -> CLOSED)
  - [ ] Failure threshold
  - [ ] Timeout handling
  - [ ] Request blocking in OPEN state
  - [ ] Test in HALF_OPEN state
  - [ ] Recovery to CLOSED state
  - [ ] Reset functionality
  - [ ] Thread safety

- [ ] **FallbackHandler**:
  - [ ] Primary operation execution
  - [ ] Fallback invocation on failure
  - [ ] Result passthrough
  - [ ] Exception handling
  - [ ] Multiple fallback levels

- [ ] **Decorators**:
  - [ ] Function wrapping
  - [ ] Automatic retry
  - [ ] Delay application
  - [ ] Exception propagation
  - [ ] Result passthrough

---

#### 2.4.4 Resources Module
**File**: `/utils/resources.py` (420+ lines)
**Status**: No tests exist

**Classes to test**:
- `ManagedResource` generic class
- `ResourcePool`
- `ManagedFileHandle`
- `TemporaryDirectory`
- `ResourceTransaction`
- `ContextualResource`

**Functions to test**:
- `managed_file()` context manager
- `temporary_file()` context manager
- `temporary_directory()` context manager
- `resource_pool()` context manager
- Global resource registry

**Tests needed**:
- [ ] **ManagedResource**:
  - [ ] Context manager protocol
  - [ ] Cleanup function invocation
  - [ ] Disposal state tracking
  - [ ] Exception handling
  - [ ] Resource access

- [ ] **ResourcePool**:
  - [ ] Resource acquisition
  - [ ] Resource release
  - [ ] Pool size limits
  - [ ] Resource reuse
  - [ ] Cleanup on pool close
  - [ ] Timeout handling

- [ ] **File Handle Management**:
  - [ ] File opening and closing
  - [ ] Automatic cleanup
  - [ ] Exception handling
  - [ ] Multiple file handling
  - [ ] Resource limits

- [ ] **Temporary Resources**:
  - [ ] Temporary file creation
  - [ ] Automatic deletion
  - [ ] Path accessibility
  - [ ] Exception cleanup
  - [ ] Multiple temp files
  - [ ] Directory handling

- [ ] **Transactions**:
  - [ ] Commit functionality
  - [ ] Rollback functionality
  - [ ] State tracking
  - [ ] Exception handling
  - [ ] Nested transactions

- [ ] **Global Registry**:
  - [ ] Resource registration
  - [ ] Cleanup on exit
  - [ ] Weak references
  - [ ] Memory leak prevention

---

#### 2.4.5 Structured Logging Module
**File**: `/utils/structured_logging.py` (530+ lines)
**Status**: No tests exist

**Classes to test**:
- `LogContext` dataclass
- `PerformanceMetrics` dataclass
- `AuditEvent` dataclass
- `StructuredLogger`
- `LoggingContext` context manager
- `PerformanceTracker`
- `AuditLogger`

**Functions/Decorators to test**:
- `get_structured_logger()`
- `@track_performance()`
- `@log_audit_event()`
- Context variable management

**Tests needed**:
- [ ] **StructuredLogger**:
  - [ ] Initialization with component name
  - [ ] Logging with context
  - [ ] Extra data inclusion
  - [ ] Severity levels (debug, info, warning, error, exception)
  - [ ] Context propagation
  - [ ] Log output format
  - [ ] Performance metric logging

- [ ] **LoggingContext**:
  - [ ] Context variable setting
  - [ ] Correlation ID generation
  - [ ] User ID tracking
  - [ ] Operation name tracking
  - [ ] Context cleanup on exit
  - [ ] Nested context handling
  - [ ] Exception handling

- [ ] **PerformanceTracker**:
  - [ ] Operation timing
  - [ ] Metrics collection
  - [ ] Memory tracking
  - [ ] CPU tracking
  - [ ] Automatic logging
  - [ ] Result passthrough

- [ ] **AuditLogger**:
  - [ ] Event recording
  - [ ] User tracking
  - [ ] Action logging
  - [ ] Resource tracking
  - [ ] Timestamp recording
  - [ ] File rotation
  - [ ] Retention policies

---

### 2.5 File & Format Utilities

#### 2.5.1 File Utilities Module
**File**: `/utils/file_utils.py` (700+ lines)
**Status**: No tests exist

**Functions to test**:
- `atomic_write()` context manager
- `load_json()` - JSON file loading
- `save_json()` - JSON file saving
- `load_yaml()` - YAML file loading
- `save_yaml()` - YAML file saving
- `detect_encoding()` - File encoding detection
- `read_file_with_encoding()` - File reading
- `write_file_safely()` - Safe file writing
- `ensure_directory()` - Directory creation
- `validate_file_path()` - Path validation
- `get_relative_path()` - Path manipulation
- `merge_files()` - File merging
- `backup_file()` - File backup
- `list_files_recursively()` - File listing

**Tests needed**:
- [ ] **Atomic Write**:
  - [ ] Successful write operation
  - [ ] Temporary file usage
  - [ ] Atomic replacement
  - [ ] Backup creation
  - [ ] Exception rollback
  - [ ] Permission handling
  - [ ] Concurrent access

- [ ] **JSON Operations**:
  - [ ] Valid JSON loading
  - [ ] Invalid JSON error handling
  - [ ] Pretty printing
  - [ ] Compact saving
  - [ ] Unicode handling
  - [ ] Large file handling
  - [ ] Default value support

- [ ] **YAML Operations**:
  - [ ] Valid YAML loading
  - [ ] Invalid YAML error handling
  - [ ] Nested structure support
  - [ ] Comments preservation
  - [ ] Encoding handling

- [ ] **Encoding Detection**:
  - [ ] UTF-8 detection
  - [ ] Latin-1 detection
  - [ ] Windows encoding detection
  - [ ] BOM handling
  - [ ] Confidence scores
  - [ ] Fallback encoding

- [ ] **Safe File Operations**:
  - [ ] Permission checking
  - [ ] Size validation
  - [ ] Path validation
  - [ ] Error reporting
  - [ ] Temporary file cleanup

- [ ] **Path Operations**:
  - [ ] Directory creation
  - [ ] Parent directory handling
  - [ ] Path resolution
  - [ ] Relative path computation
  - [ ] Cross-platform compatibility

---

#### 2.5.2 JSON Utilities

**2.5.2.1 Parser Module** (`/utils/json/parser.py`, ~300 lines)
**Status**: Partially tested

**Functions to test**:
- `parse_json_string()`
- `clean_json_string()`
- `fix_common_json_issues()`
- `extract_json_from_text()`
- `parse_conversation_data()`
- `is_valid_json()`
- `parse_json()` - Error handling wrapper

**Tests needed**:
- [ ] Valid JSON parsing
- [ ] Invalid JSON error handling
- [ ] JSON string cleaning (whitespace, quotes)
- [ ] Common issue fixing (missing colons, trailing commas, etc.)
- [ ] JSON extraction from mixed text
- [ ] Conversation format detection
- [ ] Chat history format parsing
- [ ] Message_v2 format parsing
- [ ] Encoding handling
- [ ] Large JSON handling
- [ ] Malformed JSON recovery
- [ ] Empty input handling
- [ ] Null value handling

**2.5.2.2 Fixer Module** (`/utils/json/fixer.py`, ~400 lines)
**Status**: No tests exist

**Classes/Functions to test**:
- `JsonFixerState` enum
- `JsonFixerConfig` class
- `JsonFixer` main class
- `fix_json()` function
- `repair_malformed_json()` function
- `fix_common_patterns()` function
- Individual fixing functions:
  - `fix_trailing_commas()`
  - `fix_missing_quotes()`
  - `fix_single_quotes()`
  - `fix_unescaped_newlines()`
  - `fix_duplicate_keys()`
  - `fix_incomplete_objects()`
  - etc.

**Tests needed**:
- [ ] **JsonFixer**:
  - [ ] Configuration initialization
  - [ ] Fix application
  - [ ] Multiple issue fixing
  - [ ] Partial JSON repair
  - [ ] Error tracking
  - [ ] Result reporting

- [ ] **Individual Fixes**:
  - [ ] Trailing comma removal
  - [ ] Missing quote addition
  - [ ] Single quote conversion
  - [ ] Newline escaping
  - [ ] Duplicate key handling
  - [ ] Incomplete object completion
  - [ ] Invalid escape sequences
  - [ ] Comment removal
  - [ ] Mixed quote handling

- [ ] **Edge Cases**:
  - [ ] Already valid JSON
  - [ ] Completely invalid JSON
  - [ ] Partially fixable JSON
  - [ ] Large JSON documents
  - [ ] Nested structures
  - [ ] Unicode content

**2.5.2.3 Formatter Module** (`/utils/json/formatter.py`, ~300 lines)
**Status**: No tests exist

**Functions to test**:
- `prettify_json()` - JSON pretty printing
- `format_conversation_as_text()` - Conversation text formatting
- `format_conversation_as_markdown()` - Conversation markdown formatting
- `format_json_with_colors()` - Colored JSON output
- `compact_json()` - JSON minification
- `format_with_indentation()` - Custom indentation
- `truncate_long_values()` - Value truncation
- `sanitize_json_for_display()` - Safe display formatting

**Tests needed**:
- [ ] JSON pretty printing with indentation
- [ ] Conversation text formatting
- [ ] Role-based formatting (user/assistant)
- [ ] Conversation markdown formatting
- [ ] Color formatting
- [ ] ANSI color support
- [ ] Unicode content preservation
- [ ] Special character escaping
- [ ] Line length limits
- [ ] Indentation customization
- [ ] Value truncation
- [ ] XSS/injection prevention
- [ ] Large structure handling
- [ ] Empty content handling

---

#### 2.5.3 XML Utilities

**File**: `/utils/xml/formatter.py` (estimated 200+ lines)
**Status**: No tests exist

**Classes/Functions to test**:
- `XmlFormatter` class
- `format_xml()` function
- `prettify_xml()` function
- `extract_xml_tags()` function
- `escape_xml_content()` function
- `handle_xml_entities()` function

**Tests needed**:
- [ ] XML parsing and validation
- [ ] Pretty printing with indentation
- [ ] Tag extraction
- [ ] Content escaping
- [ ] Entity handling
- [ ] Attribute formatting
- [ ] Namespace handling
- [ ] CDATA sections
- [ ] Comments preservation
- [ ] Malformed XML recovery
- [ ] Unicode support
- [ ] Large XML handling

---

#### 2.5.4 Text Formatting Utilities

**File**: `/utils/text/formatting.py` (estimated 200+ lines)
**Status**: Partially tested in `tests/utils/text/test_formatting.py`

**Functions to test**:
- `normalize_whitespace()` - Whitespace normalization
- `normalize_line_breaks()` - Line break normalization
- `remove_extra_spaces()` - Space removal
- `split_into_paragraphs()` - Text segmentation
- `word_wrap()` - Text wrapping
- `truncate_text()` - Text truncation
- `indent_text()` - Text indentation
- `align_text()` - Text alignment
- `format_with_prefix()` - Prefix formatting
- `justify_text()` - Text justification

**Tests needed**:
- [ ] Whitespace handling (leading, trailing, internal)
- [ ] Line break preservation/normalization
- [ ] Multiple space collapsing
- [ ] Paragraph segmentation
- [ ] Word wrapping at specified width
- [ ] Text truncation with ellipsis
- [ ] Indentation levels
- [ ] Text alignment (left, right, center)
- [ ] Prefix application
- [ ] Text justification
- [ ] Unicode support
- [ ] Empty string handling
- [ ] Very long lines
- [ ] Mixed line endings

---

#### 2.5.5 Color Utilities

**File**: `/utils/color_utils.py` (estimated 100 lines)
**Status**: No tests exist

**Functions to test**:
- `hex_to_rgb()` - Hex to RGB conversion
- `rgb_to_hex()` - RGB to hex conversion
- `hex_to_ansi_color()` - Hex to ANSI conversion
- `rgb_to_ansi_color()` - RGB to ANSI conversion
- `get_color_name()` - Color naming
- `is_valid_color()` - Color validation
- `blend_colors()` - Color blending
- `get_contrast_color()` - Contrast color

**Tests needed**:
- [ ] Hex format parsing
- [ ] RGB value conversion
- [ ] ANSI color code generation
- [ ] Color validation
- [ ] Invalid color handling
- [ ] Color normalization
- [ ] Named color support
- [ ] Brightness calculation
- [ ] Contrast detection
- [ ] Color blending algorithms

---

#### 2.5.6 Logger Module

**File**: `/utils/logger.py` (150+ lines)
**Status**: No tests exist

**Functions/Classes to test**:
- `get_logger()` - Logger factory
- `configure_logging()` - Logging configuration
- `set_log_level()` - Level setting
- `Logger` class (if custom implementation)
- Context logging support

**Tests needed**:
- [ ] Logger initialization
- [ ] Log level setting
- [ ] Log output (console and file)
- [ ] Log format
- [ ] Multiple loggers
- [ ] Logger hierarchy
- [ ] Handler configuration
- [ ] Filter functionality
- [ ] Record formatting
- [ ] Performance with many logs

---

## 3. DEPENDENCY INJECTION SYSTEM (annotation_toolkit/di/)

### 3.1 Core DI Components

#### 3.1.1 Container Module
**File**: `/di/container.py` (300+ lines)
**Status**: Partially tested in `tests/test_dependency_injection.py`

**Classes to test**:
- `DIContainer` - Main container
- `ServiceRegistry` - Service registration storage
- `ServiceScope` enum (SINGLETON, TRANSIENT, SCOPED)

**Methods to test**:
- `register()` - Service registration
- `register_instance()` - Instance registration
- `register_factory()` - Factory registration
- `resolve()` - Service resolution
- `get_registered_services()` - Service enumeration
- `clear()` - Container reset
- `can_resolve()` - Resolution checking

**Tests needed**:
- [ ] Basic service registration and resolution
- [ ] Singleton scope (same instance)
- [ ] Transient scope (new instance each time)
- [ ] Scoped lifecycle
- [ ] Factory function usage
- [ ] Dependency injection with parameters
- [ ] Circular dependency detection
- [ ] Service not found errors
- [ ] Multiple registrations
- [ ] Instance registration
- [ ] Type validation
- [ ] Container cloning
- [ ] Service enumeration

---

#### 3.1.2 Bootstrap Module
**File**: `/di/bootstrap.py` (400+ lines)
**Status**: Partially tested

**Classes to test**:
- `LoggerAdapter` - Logger interface adapter

**Functions to test**:
- `bootstrap_application()` - Container initialization
- `configure_services()` - Service configuration
- `get_tool_instances()` - Tool resolution
- `validate_container_configuration()` - Validation
- Factory functions:
  - `create_dict_to_bullet_tool()`
  - `create_json_visualizer_tool()`
  - `create_conversation_generator_tool()`
  - `create_text_cleaner_tool()`
  - `create_text_collector_tool()`

**Tests needed**:
- [ ] **Bootstrap process**:
  - [ ] Container creation
  - [ ] Service registration
  - [ ] Configuration loading
  - [ ] Tool factory invocation
  - [ ] Dependency satisfaction

- [ ] **LoggerAdapter**:
  - [ ] Logger delegation
  - [ ] Method availability
  - [ ] Message passing
  - [ ] Deduplication logic

- [ ] **Tool factories**:
  - [ ] Configuration reading
  - [ ] Tool instantiation
  - [ ] Dependency injection
  - [ ] Default values
  - [ ] Error handling

- [ ] **Validation**:
  - [ ] Container state validation
  - [ ] Required services presence
  - [ ] Configuration validity
  - [ ] Factory callable checking

- [ ] **Tool instances**:
  - [ ] Tool resolution
  - [ ] Multiple tool handling
  - [ ] Tool configuration
  - [ ] Error handling

---

#### 3.1.3 Interfaces Module
**File**: `/di/interfaces.py` (estimated 100 lines)
**Status**: No tests exist

**Interfaces to test**:
- `DIContainerInterface` - Container contract
- `ConfigInterface` - Configuration contract
- `LoggerInterface` - Logger contract
- `AnnotationToolInterface` - Tool contract
- `TextAnnotationToolInterface` - Text tool contract
- `JsonAnnotationToolInterface` - JSON tool contract
- `ConversationToolInterface` - Conversation tool contract

**Tests needed**:
- [ ] Interface definition
- [ ] Implementation compliance
- [ ] Method signatures
- [ ] Return type contracts
- [ ] Exception contracts
- [ ] Property definitions

---

#### 3.1.4 Registry Module
**File**: `/di/registry.py` (estimated 150 lines)
**Status**: No tests exist

**Classes to test**:
- `ServiceRegistry` - Service registration storage
- `ServiceDescriptor` - Service metadata
- `ServiceScope` enum

**Tests needed**:
- [ ] Service registration
- [ ] Service lookup
- [ ] Scope management
- [ ] Lifecycle handling
- [ ] Factory storage
- [ ] Instance caching
- [ ] Service enumeration

---

#### 3.1.5 Exceptions Module
**File**: `/di/exceptions.py` (estimated 50 lines)
**Status**: No tests exist

**Exceptions to test**:
- `ServiceNotRegisteredError`
- `CircularDependencyError`
- `ServiceCreationError`
- `InvalidConfigurationError`

**Tests needed**:
- [ ] Exception raising
- [ ] Error messages
- [ ] Exception hierarchy
- [ ] Exception catching
- [ ] Context preservation

---

#### 3.1.6 Decorators Module
**File**: `/di/decorators.py` (estimated 100 lines)
**Status**: No tests exist

**Decorators to test**:
- `@injectable` - Service decoration
- `@transient` - Scope declaration
- `@singleton` - Scope declaration
- `@scoped` - Scope declaration

**Tests needed**:
- [ ] Decorator application
- [ ] Metadata attachment
- [ ] Scope indication
- [ ] Chaining with other decorators
- [ ] Function/class wrapping

---

## 4. USER INTERFACE LAYERS

### 4.1 CLI Interface

#### 4.1.1 CLI Main Module
**File**: `/ui/cli.py` (300+ lines)
**Status**: Partially tested in `tests/test_cli.py`

**Functions to test**:
- `create_parser()` - Argument parser creation
- `execute_command()` - Command execution
- `main()` - Entry point
- Error handling and exit codes

**Tests needed**:
- [ ] Argument parsing for all commands
- [ ] Default argument values
- [ ] Argument validation
- [ ] Help text generation
- [ ] Version output
- [ ] Configuration file loading
- [ ] Command dispatching
- [ ] Error handling
- [ ] Exit codes
- [ ] Output formatting

---

#### 4.1.2 CLI Commands Module
**File**: `/ui/cli/commands.py` (400+ lines)
**Status**: No tests exist

**Functions to test**:
- `run_dict_to_bullet_command()`
- `run_json_visualizer_command()`
- `run_conversation_generator_command()`
- `run_text_cleaner_command()`
- `run_text_collector_command()`
- Helper functions

**Tests needed**:
- [ ] Each command execution
- [ ] Input file loading
- [ ] Output file writing
- [ ] DI container integration
- [ ] Tool invocation
- [ ] Result formatting
- [ ] Error handling
- [ ] Exit codes
- [ ] Logging output
- [ ] Configuration override

---

### 4.2 GUI Interface

#### 4.2.1 GUI Application
**File**: `/ui/gui/app.py` (estimated 400+ lines)
**Status**: No tests exist

**Classes/Functions to test**:
- `AnnotationToolkitApp` - Main application window
- `_initialize_tools()` - Tool initialization
- `_setup_ui()` - UI setup
- `_load_stylesheet()` - Styling
- Menu creation and handling
- Theme management
- Tool widget management
- File operations

**Tests needed**:
- [ ] Application initialization
- [ ] Window creation
- [ ] Tool initialization
- [ ] UI layout
- [ ] Menu functionality
- [ ] Theme switching
- [ ] File dialogs
- [ ] Error display
- [ ] Configuration persistence
- [ ] Window state management

---

#### 4.2.2 GUI Widgets
**Location**: `/ui/gui/widgets/`

**Widgets to test** (estimated 1000+ lines total):
- `DictWidget` - Dictionary visualization widget
- `JsonWidget` - JSON visualization widget
- `TextCleanerWidget` - Text cleaning widget
- `TextCollectorWidget` - Text collection widget
- `ConversationGeneratorWidget` - Conversation building widget
- `CustomWidgets` - Reusable components
- `JsonFixer` - JSON fixing widget
- `MainMenu` - Menu widget
- `Sidebar` - Navigation sidebar

**Tests needed for each widget**:
- [ ] Widget initialization
- [ ] UI element creation
- [ ] Event handling
- [ ] Data binding
- [ ] Tool integration
- [ ] File operations
- [ ] Error display
- [ ] Result formatting
- [ ] Button functionality
- [ ] Input validation
- [ ] Output generation
- [ ] State management
- [ ] Theme support

---

#### 4.2.3 GUI Theme Module
**File**: `/ui/gui/theme.py` (estimated 200+ lines)
**Status**: No tests exist

**Functions to test**:
- `apply_theme()` - Theme application
- `get_theme()` - Theme retrieval
- `set_theme()` - Theme setting
- `detect_system_theme()` - System detection
- Theme constants and definitions

**Tests needed**:
- [ ] Theme switching
- [ ] Color consistency
- [ ] Font application
- [ ] Platform-specific themes
- [ ] Dark/light mode
- [ ] Custom themes
- [ ] Widget styling
- [ ] Accessibility

---

#### 4.2.4 GUI Sidebar
**File**: `/ui/gui/sidebar.py` (estimated 150+ lines)
**Status**: No tests exist

**Tests needed**:
- [ ] Sidebar initialization
- [ ] Tool listing
- [ ] Tool selection
- [ ] Navigation
- [ ] State management
- [ ] Collapsing/expanding

---

## 5. CONFIGURATION SYSTEM

### 5.1 Config Module
**File**: `/config.py` (500+ lines)
**Status**: Partially tested in `tests/test_config.py`

**Classes/Methods to test**:
- `Config` class
- `__init__()` - Initialization
- `load_from_file()` - File loading
- `save_to_file()` - File saving
- `get()` - Value retrieval
- `set()` - Value setting
- `get_security_config()` - Security config
- `get_performance_config()` - Performance config
- Environment variable loading
- Configuration merging

**Tests needed**:
- [x] Default configuration loading
- [x] File-based configuration loading
- [ ] Configuration file validation
- [ ] YAML parsing
- [ ] Configuration merging
- [ ] Environment variable overrides
- [ ] Invalid YAML handling
- [ ] Missing file handling
- [ ] File write operations
- [ ] Configuration value retrieval
- [ ] Configuration value setting
- [ ] Nested key access
- [ ] Default value fallbacks
- [ ] Security config access
- [ ] Performance config access
- [ ] Type conversions
- [ ] Configuration persistence
- [ ] Configuration validation

---

## 6. ADAPTERS

### 6.1 File Storage Adapter
**File**: `/adapters/file_storage.py` (estimated 200+ lines)
**Status**: No tests exist

**Classes/Functions to test**:
- `FileStorageAdapter` - File storage interface
- `save()` - Save operation
- `load()` - Load operation
- `delete()` - Delete operation
- `list()` - File listing

**Tests needed**:
- [ ] File saving
- [ ] File loading
- [ ] File deletion
- [ ] File listing
- [ ] Directory creation
- [ ] Error handling
- [ ] Path validation
- [ ] Permission checking
- [ ] Atomic operations

---

## 7. ENTRY POINTS

### 7.1 Main Package
**File**: `/annotation_toolkit/__init__.py`
**Status**: No tests exist

**Tests needed**:
- [ ] Package imports
- [ ] Version availability
- [ ] Main exports
- [ ] Initialization

---

## 8. INTEGRATION & END-TO-END TESTS

**Tests needed**:
- [ ] **CLI Integration**:
  - [ ] Full command workflows
  - [ ] File I/O workflows
  - [ ] Error recovery
  - [ ] Exit code handling

- [ ] **GUI Integration**:
  - [ ] Application startup
  - [ ] Tool usage workflows
  - [ ] File operations
  - [ ] Theme switching
  - [ ] Configuration persistence

- [ ] **DI Integration**:
  - [ ] Full container setup
  - [ ] Service resolution chains
  - [ ] Tool initialization
  - [ ] Configuration loading

- [ ] **Data Processing Workflows**:
  - [ ] JSON visualization workflows
  - [ ] Conversation generation workflows
  - [ ] Text processing workflows
  - [ ] File conversion workflows

---

## 9. TEST COVERAGE SUMMARY

### Current Test Coverage
- **Core Base Classes**: ~30% (basic initialization only)
- **Text Tools**: ~20% (DictToBulletList has basic tests)
- **Conversation Tools**: ~0%
- **Utilities**: ~15% (Error handling, JSON parsing only)
- **DI System**: ~40% (Container basics only)
- **CLI**: ~25% (Parser creation only)
- **GUI**: ~0%
- **Configuration**: ~30% (Basic load/get operations)

### Total Codebase: ~10,000 lines
### Current Tests: ~1,700 lines (~17% coverage)
### Estimated Tests Needed: ~5,000-7,000 additional lines

---

## 10. PRIORITY TESTING TIERS

### Tier 1: CRITICAL (Security & Core Functionality)
1. Security module (path validation, file size limits, rate limiting)
2. Error handling system
3. DI container and bootstrap
4. Configuration system
5. Core tool base classes
6. File utilities (atomic writes, safe operations)

### Tier 2: HIGH (Infrastructure & Data Processing)
1. Validation framework
2. Recovery/retry mechanisms
3. JSON utilities (parser, fixer, formatter)
4. Text utilities
5. Conversation tools
6. Resource management

### Tier 3: MEDIUM (Profiling & Logging)
1. Performance profiling
2. Structured logging
3. Streaming utilities
4. XML/text formatting

### Tier 4: LOW (UI & Integration)
1. GUI widgets and theme
2. CLI commands
3. Integration tests
4. End-to-end workflows

---

## Recommendations

1. **Start with Tier 1**: Critical security and core functionality tests first
2. **Use fixtures**: Create reusable test data and mocks
3. **Mock external dependencies**: File I/O, network, etc.
4. **Test edge cases**: Unicode, large files, malformed data
5. **Performance tests**: For profiling and streaming modules
6. **Integration tests**: After unit tests are in place
7. **CI/CD integration**: Automated test runs on commits
8. **Coverage reporting**: Track coverage metrics over time

