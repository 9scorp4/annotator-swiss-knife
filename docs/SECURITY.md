# Security Guide - Annotation Swiss Knife

## Table of Contents

1. [Security Overview](#security-overview)
2. [Security Features](#security-features)
3. [Configuration](#configuration)
4. [Best Practices](#best-practices)
5. [Threat Model](#threat-model)
6. [Security Checklist](#security-checklist)

---

## Security Overview

The Annotation Swiss Knife implements defense-in-depth security with multiple layers:

- **Input Validation**: All user inputs validated before processing
- **Path Security**: Prevention of directory traversal and symlink attacks
- **Rate Limiting**: Protection against abuse and DoS
- **Input Sanitization**: Protection against injection attacks (XSS, SQL)
- **Secure File Operations**: Combined security checks for file I/O
- **Audit Logging**: Comprehensive audit trails for compliance

---

## Security Features

### 1. Path Validation (`PathValidator`)

**Purpose**: Prevent directory traversal attacks and unauthorized file access

**Protections**:
- Validates paths are within allowed base directory
- Detects and blocks directory traversal attempts (`../`, `..\\`)
- Optionally blocks symlink access
- Enforces maximum path length limits

**Usage**:
```python
from annotation_toolkit.utils.security import PathValidator

validator = PathValidator(
    allowed_base="/safe/directory",
    max_path_length=4096,
    allow_symlinks=False
)

if validator.validate_path(user_provided_path):
    # Safe to use
    process_file(user_provided_path)
else:
    raise SecurityError("Invalid or unsafe path")
```

**Configuration**:
```yaml
security:
  max_path_length: 4096
  allow_symlinks: false
```

**Attack Prevention**:
- ✅ Blocks `../../etc/passwd`
- ✅ Blocks `/etc/passwd` (absolute paths outside allowed base)
- ✅ Blocks symlinks to sensitive files (configurable)
- ✅ Blocks excessively long paths

### 2. File Size Validation (`FileSizeValidator`)

**Purpose**: Prevent resource exhaustion from large file uploads

**Usage**:
```python
from annotation_toolkit.utils.security import FileSizeValidator

validator = FileSizeValidator(max_size_mb=100)

if validator.validate_file_size(filepath):
    # Safe to process
    process_file(filepath)
else:
    raise SecurityError("File exceeds maximum size")
```

**Configuration**:
```yaml
security:
  max_file_size_mb: 100
```

**Protection**: Prevents "zip bomb" and other resource exhaustion attacks

### 3. Input Sanitization (`InputSanitizer`)

**Purpose**: Prevent injection attacks (XSS, SQL injection, command injection)

**Methods**:

**XSS Protection**:
```python
from annotation_toolkit.utils.security import InputSanitizer

sanitizer = InputSanitizer()

# Sanitize for HTML display
user_input = "<script>alert('xss')</script>"
safe_output = sanitizer.sanitize_for_display(user_input)
# Result: &lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;
```

**Filename Sanitization**:
```python
# Remove dangerous characters from filenames
unsafe_filename = "../../etc/passwd"
safe_filename = sanitizer.sanitize_filename(unsafe_filename)
# Result: "etc_passwd"
```

**SQL Sanitization** (basic):
```python
# Basic SQL escaping
sql_input = "'; DROP TABLE users; --"
safe_sql = sanitizer.sanitize_sql(sql_input)
```

**Important**: SQL sanitization is basic. Use parameterized queries for production databases.

### 4. Rate Limiting (`RateLimiter`)

**Purpose**: Prevent abuse and DoS attacks

**Usage**:
```python
from annotation_toolkit.utils.security import RateLimiter

limiter = RateLimiter(
    max_requests=100,
    window_seconds=60
)

if limiter.check_rate_limit(user_id):
    # Process request
    handle_request(user_id)
else:
    raise SecurityError("Rate limit exceeded")
```

**Configuration**:
```yaml
security:
  rate_limit_requests_per_minute: 100
```

**Use Cases**:
- API endpoints
- File processing operations
- User authentication attempts

### 5. Secure File Handler (`SecureFileHandler`)

**Purpose**: Combine multiple security checks in one handler

**Features**:
- Path validation
- File size validation
- Encoding validation
- Automatic cleanup on errors

**Usage**:
```python
from annotation_toolkit.utils.security import SecureFileHandler

handler = SecureFileHandler(
    allowed_base="/safe/directory",
    max_file_size_mb=50,
    allow_symlinks=False
)

# Read with security checks
try:
    data = handler.read_file("/safe/directory/file.json")
except SecurityError as e:
    print(f"Security violation: {e}")

# Write with security checks
handler.write_file(
    "/safe/directory/output.json",
    json.dumps(data)
)
```

**Checks Performed**:
1. Path is within allowed base directory
2. No directory traversal attempts
3. No symlink access (if disabled)
4. File size within limits
5. Valid UTF-8 encoding

---

## Configuration

### Security Configuration Options

```yaml
security:
  # File size limits
  max_file_size_mb: 100

  # Path validation
  max_path_length: 4096
  allow_symlinks: false

  # Rate limiting
  rate_limit_requests_per_minute: 100

  # Input validation
  strict_validation: true

  # Encoding
  allowed_encodings:
    - utf-8
    - utf-16
    - ascii
```

### Environment Variable Overrides

```bash
export ANNOTATION_TOOLKIT_SECURITY_MAX_FILE_SIZE_MB=50
export ANNOTATION_TOOLKIT_SECURITY_ALLOW_SYMLINKS=false
export ANNOTATION_TOOLKIT_SECURITY_RATE_LIMIT_REQUESTS_PER_MINUTE=50
```

---

## Best Practices

### 1. Input Validation

**Always validate**:
- ✅ File paths before file operations
- ✅ File sizes before processing
- ✅ User input before display
- ✅ JSON data against schemas

**Never trust**:
- ❌ User-provided paths
- ❌ External data sources
- ❌ Environment variables (validate first)

### 2. File Operations

**Do**:
- ✅ Use `SecureFileHandler` for all file I/O
- ✅ Use context managers (automatic cleanup)
- ✅ Validate paths with `PathValidator`
- ✅ Check file sizes before processing

**Don't**:
- ❌ Accept absolute paths from users
- ❌ Allow symlink access in production
- ❌ Process files without size limits
- ❌ Use user input directly in file paths

### 3. Logging and Audit

**Do**:
- ✅ Log all file operations (audit trail)
- ✅ Log security violations
- ✅ Log rate limit violations
- ✅ Include user/session context

**Don't**:
- ❌ Log sensitive data (passwords, tokens)
- ❌ Log full file contents
- ❌ Log personally identifiable information (PII) without anonymization

### 4. Error Handling

**Do**:
- ✅ Use specific exceptions (`SecurityError`, `ValidationError`)
- ✅ Provide actionable error messages
- ✅ Log errors with context

**Don't**:
- ❌ Expose stack traces to end users
- ❌ Reveal internal paths in error messages
- ❌ Leak sensitive information in exceptions

### 5. Configuration

**Do**:
- ✅ Use restrictive defaults (deny by default)
- ✅ Document security implications
- ✅ Validate configuration on load
- ✅ Use environment variables for sensitive data

**Don't**:
- ❌ Store secrets in configuration files
- ❌ Commit API keys or passwords
- ❌ Use overly permissive settings

---

## Threat Model

### Threats Addressed

1. **Directory Traversal** ✅
   - **Attack**: `../../etc/passwd`
   - **Mitigation**: `PathValidator` with allowed base directory

2. **Symlink Attacks** ✅
   - **Attack**: Symlink to `/etc/passwd`
   - **Mitigation**: `allow_symlinks: false` configuration

3. **Resource Exhaustion** ✅
   - **Attack**: Upload massive files (zip bomb)
   - **Mitigation**: `FileSizeValidator` with size limits

4. **Cross-Site Scripting (XSS)** ✅
   - **Attack**: `<script>alert('xss')</script>`
   - **Mitigation**: `InputSanitizer.sanitize_for_display()`

5. **SQL Injection** ⚠️
   - **Attack**: `'; DROP TABLE users; --`
   - **Mitigation**: Basic sanitization (use parameterized queries for production)

6. **Denial of Service (DoS)** ✅
   - **Attack**: Flood requests
   - **Mitigation**: `RateLimiter` with configurable limits

7. **Path Injection** ✅
   - **Attack**: `file.txt; rm -rf /`
   - **Mitigation**: `sanitize_filename()` removes dangerous characters

### Threats Not Addressed

1. **Network Security**: Application runs locally, no network security needed
2. **Authentication**: No user authentication (single-user application)
3. **Encryption**: No data encryption (local files)
4. **Code Injection**: Python code execution not allowed from user input

### Security Assumptions

- Application runs on trusted local machine
- User has legitimate access to files they process
- No multi-user environment (no authorization needed)
- Files are stored locally (no network storage security)

---

## Security Checklist

### Development

- [ ] All user inputs validated before use
- [ ] File paths validated with `PathValidator`
- [ ] File sizes checked before processing
- [ ] User input sanitized before display
- [ ] Error messages don't leak sensitive information
- [ ] Logging includes security-relevant events
- [ ] Configuration has secure defaults
- [ ] Tests include security test cases

### Deployment

- [ ] Review `security:` configuration section
- [ ] Set appropriate `max_file_size_mb`
- [ ] Disable `allow_symlinks` in production
- [ ] Configure `rate_limit_requests_per_minute`
- [ ] Enable audit logging (`audit_trail: true`)
- [ ] Review allowed file encodings
- [ ] Test with malicious inputs

### Operations

- [ ] Monitor logs for security violations
- [ ] Review audit trail regularly
- [ ] Update security configuration as needed
- [ ] Keep dependencies up to date
- [ ] Review file access patterns
- [ ] Investigate rate limit violations

---

## Security Incident Response

### If Security Violation Detected

1. **Log the incident**:
   ```python
   logger.error("Security violation detected", extra={
       "user_id": user_id,
       "violation_type": "path_traversal",
       "attempted_path": path,
       "timestamp": datetime.now()
   })
   ```

2. **Block the operation**:
   ```python
   raise SecurityError("Security violation: unauthorized file access")
   ```

3. **Alert administrators** (if audit logging enabled):
   - Check audit log for incident details
   - Review user activity logs
   - Investigate source of malicious input

4. **Update security controls**:
   - Adjust rate limits if needed
   - Tighten path validation rules
   - Update file size limits

---

## Security Updates

### Keeping Secure

1. **Update dependencies**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Review security advisories**:
   - Python security updates
   - PyQt5 security patches
   - PyYAML security fixes

3. **Audit code**:
   - Regular security code reviews
   - Static analysis tools
   - Penetration testing

### Reporting Security Issues

If you discover a security vulnerability:

1. **Do not** create a public GitHub issue
2. Contact the development team privately
3. Provide detailed description and reproduction steps
4. Allow time for fix before public disclosure

---

## Compliance

### Audit Trail

Enable comprehensive audit logging for compliance:

```yaml
logging:
  audit_trail: true
  structured_logging: true
  level: INFO
```

**Audit log includes**:
- File operations (read, write, delete)
- User context (user_id, session_id)
- Timestamps
- Operation results (success/failure)
- File content hashes (optional)

### Data Privacy

**Recommendations**:
- Review audit logs for PII
- Anonymize user data in logs
- Implement log rotation and retention policies
- Secure log storage

### Regulatory Compliance

**GDPR Considerations**:
- Right to erasure: Delete user data on request
- Data minimization: Don't log unnecessary user data
- Purpose limitation: Only process data for stated purposes

---

## Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [PERFORMANCE.md](PERFORMANCE.md) - Performance optimization
- [CLAUDE.md](../CLAUDE.md) - Developer guidance
- [User_Manual.md](User_Manual.md) - End-user documentation
