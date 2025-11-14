# Configuration Reference - Annotation Swiss Knife

## Overview

The Annotation Swiss Knife uses a hierarchical configuration system with three layers:

1. **Default Configuration** (lowest priority)
2. **YAML Configuration Files** (medium priority)
3. **Environment Variables** (highest priority)

Configuration is managed through the `Config` class in `annotation_toolkit/config.py`.

---

## Configuration File Format

### Complete Configuration Example

```yaml
# Tool-specific settings
tools:
  dict_to_bullet:
    enabled: true
    default_color: "#4CAF50"
    markdown_output: true
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

# User interface settings
ui:
  theme: default  # default, dark, light
  font_size: 12
  window_size:
    width: 1000
    height: 700
  font_family: "Monospace"  # Platform-specific fonts used if not specified

# Data handling settings
data:
  save_directory: ~/annotation_toolkit_data
  autosave: false
  autosave_interval: 300  # seconds
  backup_files: true
  max_recent_files: 10

# Security settings
security:
  max_file_size_mb: 100
  max_path_length: 4096
  allow_symlinks: false
  rate_limit_requests_per_minute: 100
  strict_validation: true
  allowed_encodings:
    - utf-8
    - utf-16
    - ascii

# Performance settings
performance:
  enable_caching: true
  cache_ttl_seconds: 300
  max_cache_size: 1000
  max_cache_size_mb: 100
  streaming_threshold_mb: 10
  stream_chunk_size_kb: 1024
  enable_profiling: false
  profiling_sample_rate: 1.0
  max_pool_size: 10
  pool_timeout_seconds: 30
  max_workers: 4
  use_multiprocessing: false

# Logging configuration
logging:
  level: INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  file: annotation_toolkit.log
  max_size: 10MB
  backup_count: 5
  structured_logging: false
  audit_trail: false
  max_log_size_mb: 50

# Data validation settings
validation:
  strict_mode: true
  max_validation_errors: 100
  stop_on_first_error: false
  validate_on_load: true

# Error recovery settings
error_recovery:
  max_retry_attempts: 3
  base_retry_delay: 1.0
  max_retry_delay: 30.0
  circuit_breaker_threshold: 10
  circuit_breaker_timeout: 120
  enable_fallback: true
```

---

## Configuration Sections

### Tools Configuration

Configuration for individual annotation tools.

#### dict_to_bullet

```yaml
tools:
  dict_to_bullet:
    enabled: true                # Enable/disable tool
    default_color: "#4CAF50"     # Default color for GUI widget
    markdown_output: true        # Output as markdown (vs plain text)
    markdown_links: true         # Create markdown links for URLs
```

**Options**:
- `enabled` (bool): Enable/disable tool. Default: `true`
- `default_color` (str): Hex color code for GUI widget. Default: `"#4CAF50"`
- `markdown_output` (bool): Generate markdown output. Default: `true`
- `markdown_links` (bool): Create clickable markdown links. Default: `true`

#### conversation_visualizer

```yaml
tools:
  conversation_visualizer:
    enabled: true
    default_color: "#2196F3"
    user_message_color: "#0d47a1"
    ai_message_color: "#33691e"
    show_timestamps: false
```

**Options**:
- `enabled` (bool): Enable/disable tool. Default: `true`
- `default_color` (str): Default widget color. Default: `"#2196F3"`
- `user_message_color` (str): Color for user messages. Default: `"#0d47a1"`
- `ai_message_color` (str): Color for AI messages. Default: `"#33691e"`
- `show_timestamps` (bool): Display timestamps. Default: `false`

#### conversation_generator

```yaml
tools:
  conversation_generator:
    enabled: true
    max_turns: 20
    default_color: "#9C27B0"
```

**Options**:
- `enabled` (bool): Enable/disable tool. Default: `true`
- `max_turns` (int): Maximum conversation turns allowed. Default: `20`
- `default_color` (str): Widget color. Default: `"#9C27B0"`

#### text_cleaner

```yaml
tools:
  text_cleaner:
    enabled: true
    default_color: "#4CAF50"
    preserve_structure: true
```

**Options**:
- `enabled` (bool): Enable/disable tool. Default: `true`
- `default_color` (str): Widget color. Default: `"#4CAF50"`
- `preserve_structure` (bool): Preserve text structure. Default: `true`

#### json_visualizer

```yaml
tools:
  json_visualizer:
    enabled: true
    default_color: "#FF9800"
    user_message_color: "#0d47a1"
    ai_message_color: "#33691e"
    debug_logging: false
    auto_repair: true
```

**Options**:
- `enabled` (bool): Enable/disable tool. Default: `true`
- `default_color` (str): Widget color. Default: `"#FF9800"`
- `user_message_color` (str): Color for user messages. Default: `"#0d47a1"`
- `ai_message_color` (str): Color for AI messages. Default: `"#33691e"`
- `debug_logging` (bool): Enable debug logging. Default: `false`
- `auto_repair` (bool): Automatically repair malformed JSON. Default: `true`

---

### UI Configuration

User interface settings for the GUI application.

```yaml
ui:
  theme: default                # Theme: default, dark, light
  font_size: 12                 # Font size in points
  window_size:
    width: 1000                 # Window width in pixels
    height: 700                 # Window height in pixels
  font_family: "Monospace"      # Font family name
```

**Options**:
- `theme` (str): Application theme. Options: `default`, `dark`, `light`. Default: `default`
- `font_size` (int): Font size for text areas. Default: `12`
- `window_size.width` (int): Default window width. Default: `1000`
- `window_size.height` (int): Default window height. Default: `700`
- `font_family` (str): Font family. Default: platform-specific (SF Pro/Segoe UI/Ubuntu)

---

### Data Configuration

Data handling and storage settings.

```yaml
data:
  save_directory: ~/annotation_toolkit_data
  autosave: false
  autosave_interval: 300        # seconds
  backup_files: true
  max_recent_files: 10
```

**Options**:
- `save_directory` (str): Default directory for saved files. Default: `~/annotation_toolkit_data`
- `autosave` (bool): Enable automatic saving. Default: `false`
- `autosave_interval` (int): Autosave interval in seconds. Default: `300`
- `backup_files` (bool): Create backups before overwriting. Default: `true`
- `max_recent_files` (int): Number of recent files to track. Default: `10`

---

### Security Configuration

Security settings for path validation, rate limiting, and file operations.

```yaml
security:
  max_file_size_mb: 100
  max_path_length: 4096
  allow_symlinks: false
  rate_limit_requests_per_minute: 100
  strict_validation: true
  allowed_encodings:
    - utf-8
    - utf-16
    - ascii
```

**Options**:
- `max_file_size_mb` (int): Maximum file size in MB. Default: `100`
- `max_path_length` (int): Maximum path length. Default: `4096`
- `allow_symlinks` (bool): Allow symlink access. Default: `false` (recommended)
- `rate_limit_requests_per_minute` (int): Rate limit for operations. Default: `100`
- `strict_validation` (bool): Enable strict validation. Default: `true`
- `allowed_encodings` (list): Allowed file encodings. Default: `["utf-8", "utf-16", "ascii"]`

**Security Recommendations**:
- Keep `allow_symlinks: false` in production
- Set conservative `max_file_size_mb` based on available memory
- Enable `strict_validation: true` for production use

---

### Performance Configuration

Performance optimization settings.

```yaml
performance:
  enable_caching: true
  cache_ttl_seconds: 300
  max_cache_size: 1000
  max_cache_size_mb: 100
  streaming_threshold_mb: 10
  stream_chunk_size_kb: 1024
  enable_profiling: false
  profiling_sample_rate: 1.0
  max_pool_size: 10
  pool_timeout_seconds: 30
  max_workers: 4
  use_multiprocessing: false
```

**Options**:
- `enable_caching` (bool): Enable caching. Default: `true`
- `cache_ttl_seconds` (int): Cache time-to-live in seconds. Default: `300`
- `max_cache_size` (int): Maximum cache entries. Default: `1000`
- `max_cache_size_mb` (int): Maximum cache size in MB. Default: `100`
- `streaming_threshold_mb` (int): File size threshold for streaming. Default: `10`
- `stream_chunk_size_kb` (int): Chunk size for streaming in KB. Default: `1024`
- `enable_profiling` (bool): Enable performance profiling. Default: `false`
- `profiling_sample_rate` (float): Profiling sample rate (0.0-1.0). Default: `1.0`
- `max_pool_size` (int): Maximum resource pool size. Default: `10`
- `pool_timeout_seconds` (int): Resource pool timeout. Default: `30`
- `max_workers` (int): Maximum concurrent workers. Default: `4`
- `use_multiprocessing` (bool): Use processes instead of threads. Default: `false`

**Performance Tuning**:
- Enable caching for repeated operations
- Lower `streaming_threshold_mb` for low-memory systems
- Disable profiling in production
- Adjust `max_workers` based on CPU cores

---

### Logging Configuration

Logging settings for application logs and audit trails.

```yaml
logging:
  level: INFO
  file: annotation_toolkit.log
  max_size: 10MB
  backup_count: 5
  structured_logging: false
  audit_trail: false
  max_log_size_mb: 50
```

**Options**:
- `level` (str): Logging level. Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. Default: `INFO`
- `file` (str): Log file name. Default: `annotation_toolkit.log`
- `max_size` (str): Maximum log file size. Default: `10MB`
- `backup_count` (int): Number of backup log files. Default: `5`
- `structured_logging` (bool): Enable structured logging. Default: `false`
- `audit_trail` (bool): Enable audit logging. Default: `false`
- `max_log_size_mb` (int): Maximum total log size in MB. Default: `50`

**Logging Levels**:
- `DEBUG`: Detailed debugging information
- `INFO`: General informational messages
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

---

### Validation Configuration

Data validation settings.

```yaml
validation:
  strict_mode: true
  max_validation_errors: 100
  stop_on_first_error: false
  validate_on_load: true
```

**Options**:
- `strict_mode` (bool): Fail on validation warnings. Default: `true`
- `max_validation_errors` (int): Stop after N errors. Default: `100`
- `stop_on_first_error` (bool): Stop on first error. Default: `false`
- `validate_on_load` (bool): Validate data when loading. Default: `true`

---

### Error Recovery Configuration

Error recovery and retry settings.

```yaml
error_recovery:
  max_retry_attempts: 3
  base_retry_delay: 1.0
  max_retry_delay: 30.0
  circuit_breaker_threshold: 10
  circuit_breaker_timeout: 120
  enable_fallback: true
```

**Options**:
- `max_retry_attempts` (int): Maximum retry attempts. Default: `3`
- `base_retry_delay` (float): Base delay for exponential backoff (seconds). Default: `1.0`
- `max_retry_delay` (float): Maximum retry delay (seconds). Default: `30.0`
- `circuit_breaker_threshold` (int): Failures before circuit opens. Default: `10`
- `circuit_breaker_timeout` (float): Circuit breaker timeout (seconds). Default: `120`
- `enable_fallback` (bool): Enable fallback mechanisms. Default: `true`

---

## Environment Variables

Override configuration with environment variables using the `ANNOTATION_TOOLKIT_` prefix.

### Format

```
ANNOTATION_TOOLKIT_<SECTION>_<KEY>=value
```

### Examples

```bash
# Tool configuration
export ANNOTATION_TOOLKIT_TOOLS_DICT_TO_BULLET_MARKDOWN_OUTPUT=true

# UI configuration
export ANNOTATION_TOOLKIT_UI_THEME=dark
export ANNOTATION_TOOLKIT_UI_FONT_SIZE=14

# Security configuration
export ANNOTATION_TOOLKIT_SECURITY_MAX_FILE_SIZE_MB=50
export ANNOTATION_TOOLKIT_SECURITY_ALLOW_SYMLINKS=false

# Performance configuration
export ANNOTATION_TOOLKIT_PERFORMANCE_ENABLE_CACHING=true
export ANNOTATION_TOOLKIT_PERFORMANCE_STREAMING_THRESHOLD_MB=10

# Logging configuration
export ANNOTATION_TOOLKIT_LOGGING_LEVEL=DEBUG
export ANNOTATION_TOOLKIT_LOGGING_STRUCTURED_LOGGING=true
```

### Nested Keys

For nested configuration, use underscores to separate levels:

```bash
# For: ui.window_size.width
export ANNOTATION_TOOLKIT_UI_WINDOW_SIZE_WIDTH=1200

# For: tools.conversation_generator.max_turns
export ANNOTATION_TOOLKIT_TOOLS_CONVERSATION_GENERATOR_MAX_TURNS=30
```

---

## Loading Configuration

### Default Configuration

```python
from annotation_toolkit.config import Config

# Load default configuration
config = Config()
```

### From YAML File

```python
# Load from specific file
config = Config("custom_config.yaml")
```

### With Environment Variables

Environment variables automatically override YAML and default configuration:

```bash
export ANNOTATION_TOOLKIT_UI_THEME=dark
python -m annotation_toolkit.cli gui
```

---

## Accessing Configuration

### Get Nested Values

```python
from annotation_toolkit.config import Config

config = Config()

# Get nested value
markdown = config.get("tools", "dict_to_bullet", "markdown_output", default=True)

# Get with default
theme = config.get("ui", "theme", default="default")
```

### Set Values

```python
# Set nested value
config.set("tools", "dict_to_bullet", "markdown_output", False)

# Set multiple levels
config.set("ui", "window_size", "width", 1200)
```

### Export Configuration

```python
# Export to dictionary
config_dict = config.to_dict()

# Save to YAML
import yaml
with open("exported_config.yaml", "w") as f:
    yaml.dump(config_dict, f)
```

---

## Configuration Best Practices

### Development

- Use `DEBUG` logging level
- Enable profiling: `performance.enable_profiling: true`
- Disable caching for testing: `performance.enable_caching: false`
- Use smaller file size limits for testing

### Production

- Use `INFO` or `WARNING` logging level
- Disable profiling: `performance.enable_profiling: false`
- Enable caching: `performance.enable_caching: true`
- Set appropriate security limits
- Disable `allow_symlinks: false`
- Enable audit trail if needed: `logging.audit_trail: true`

### Security

- Never commit secrets to configuration files
- Use environment variables for sensitive data
- Set conservative `max_file_size_mb`
- Keep `allow_symlinks: false` in production
- Enable `strict_validation: true`

### Performance

- Adjust `streaming_threshold_mb` based on available memory
- Set `max_workers` based on CPU cores (typically 2-4)
- Enable caching for repeated operations
- Lower `cache_ttl_seconds` for frequently changing data

---

## Related Documentation

- [SECURITY.md](SECURITY.md) - Security features and best practices
- [PERFORMANCE.md](PERFORMANCE.md) - Performance optimization
- [User_Manual.md](User_Manual.md) - End-user documentation
- [CLAUDE.md](../CLAUDE.md) - Developer guidance
