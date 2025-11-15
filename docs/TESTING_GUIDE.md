# Testing Guide for Annotation Swiss Knife

This guide provides comprehensive information about testing the Annotation Swiss Knife project, including what needs to be tested, how to write tests, and the current state of test coverage.

## Documents in This Directory

### Quick Start
- **[TEST_COVERAGE_SUMMARY.md](TEST_COVERAGE_SUMMARY.md)** - Start here for a quick overview
  - Current test coverage metrics
  - Priority tiers for testing
  - Estimated effort
  - Quick start guide for developers

### Detailed Analysis
- **[TEST_COVERAGE_ANALYSIS.md](TEST_COVERAGE_ANALYSIS.md)** - Comprehensive module-by-module analysis
  - Detailed breakdown of every module (50+ modules)
  - Specific classes and functions to test
  - Test cases for each feature
  - Integration test requirements
  - 1,378 lines of detailed specifications

## Current State

- **Total Codebase**: ~10,000 lines of Python
- **Current Tests**: ~1,700 lines (~17% coverage)
- **Test Files**: 9 test modules across 3 directories
- **Existing Test Modules**:
  - `tests/core/test_dict_to_bullet.py` - Dictionary to bullet list tool
  - `tests/core/test_text_collector.py` - Text collector tool
  - `tests/utils/json/test_parser.py` - JSON parsing utilities
  - `tests/utils/text/test_formatting.py` - Text formatting utilities
  - `tests/utils/test_error_handler.py` - Error handling system
  - `tests/test_base.py` - Base class tests
  - `tests/test_config.py` - Configuration management
  - `tests/test_dependency_injection.py` - DI system
  - `tests/test_cli.py` - CLI interface

## Architecture Overview

```
annotation_toolkit/
├── core/               (2,010 lines) - Annotation tools
├── utils/              (7,993 lines) - Infrastructure & utilities
├── di/                 (500+ lines) - Dependency injection
├── ui/                 (1,000+ lines) - User interfaces (CLI & GUI)
├── config.py           - Configuration management
├── cli.py              - CLI entry point
└── adapters/           - Storage adapters
```

## Testing Priorities

### CRITICAL (Test First)
Focus on security, reliability, and core functionality:

1. **Security Module** (`utils/security.py` - 450 lines)
   - Path validation (directory traversal prevention)
   - File size validation
   - Rate limiting
   - Input sanitization
   - Secure file operations

2. **Error Handling System** (1,100 lines total)
   - `utils/errors.py` - Exception hierarchy and codes
   - `utils/error_handler.py` - Error handling decorators
   - Error propagation and context
   - Safe execution patterns

3. **DI Container & Bootstrap** (700 lines)
   - `di/container.py` - Service registration and resolution
   - `di/bootstrap.py` - Application initialization
   - Factory patterns for tool creation
   - Circular dependency detection

4. **Base Classes** (`core/base.py` - 169 lines)
   - Abstract tool interfaces
   - Process method delegation
   - Type validation
   - Error handling in tools

### HIGH (Test Second)
Infrastructure modules used throughout codebase:

5. **Validation Framework** (`utils/validation.py` - 500 lines)
6. **File Utilities** (`utils/file_utils.py` - 700 lines)
7. **JSON Utilities** (1,000 lines across parser, fixer, formatter)
8. **Conversation Tools** (`core/conversation/` - 500 lines)

### MEDIUM (Test Third)
Supporting infrastructure:

9. **Performance Profiling** (`utils/profiling.py`)
10. **Recovery & Retry** (`utils/recovery.py`)
11. **Structured Logging** (`utils/structured_logging.py`)
12. **Streaming** (`utils/streaming.py`)

### LOW (Test Last)
UI and specialized modules:

13. **GUI Components** (`ui/gui/`)
14. **CLI Commands** (`ui/cli/commands.py`)
15. **Text & Color Utilities**
16. **Resources & XML**

## Running Tests

### Run All Tests
```bash
# Using unittest
python -m tests.run_tests

# Or directly
python -m unittest discover tests/

# Or with pytest
pytest tests/ -v
```

### Run Specific Test File
```bash
python -m unittest tests.core.test_dict_to_bullet
python -m unittest tests.utils.test_error_handler
```

### Run with Coverage
```bash
python -m pytest tests/ --cov=annotation_toolkit --cov-report=html
# Open htmlcov/index.html to view coverage
```

### Run Specific Test Class
```bash
python -m unittest tests.core.test_dict_to_bullet.TestDictToBulletList
```

### Run Specific Test Method
```bash
python -m unittest tests.core.test_dict_to_bullet.TestDictToBulletList.test_process_text_valid_json
```

## Writing Tests

### Basic Test Structure
```python
import unittest
from annotation_toolkit.module_name import ClassName

class TestClassName(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures - runs before each test"""
        self.instance = ClassName()
    
    def tearDown(self):
        """Clean up after tests - runs after each test"""
        pass
    
    def test_basic_functionality(self):
        """Test normal operation"""
        result = self.instance.method(valid_input)
        self.assertEqual(result, expected_output)
    
    def test_error_handling(self):
        """Test exception handling"""
        with self.assertRaises(ExpectedException):
            self.instance.method(invalid_input)
    
    def test_edge_cases(self):
        """Test boundary conditions"""
        self.assertEqual(self.instance.method(""), expected_empty_result)
```

### Common Assertions
```python
# Equality
self.assertEqual(actual, expected)
self.assertNotEqual(actual, not_expected)

# Boolean
self.assertTrue(condition)
self.assertFalse(condition)

# None
self.assertIsNone(value)
self.assertIsNotNone(value)

# Identity
self.assertIs(obj1, obj2)  # Same object
self.assertIsNot(obj1, obj2)  # Different objects

# Membership
self.assertIn(item, container)
self.assertNotIn(item, container)

# Exceptions
with self.assertRaises(ExceptionType):
    code_that_should_raise()

# Collections
self.assertListEqual(actual_list, expected_list)
self.assertDictEqual(actual_dict, expected_dict)

# Comparison
self.assertGreater(a, b)
self.assertLess(a, b)
self.assertGreaterEqual(a, b)
```

### Working with Files in Tests
```python
import tempfile
from pathlib import Path

class TestFileOperations(unittest.TestCase):
    def setUp(self):
        """Create temporary directory"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
    
    def tearDown(self):
        """Clean up temporary files"""
        self.temp_dir.cleanup()
    
    def test_file_operations(self):
        """Test file reading/writing"""
        test_file = self.temp_path / "test.txt"
        test_file.write_text("test content")
        
        result = some_file_operation(test_file)
        self.assertEqual(result, expected)
```

### Mocking External Dependencies
```python
from unittest.mock import patch, MagicMock

class TestWithMocks(unittest.TestCase):
    @patch('module.function')
    def test_with_mock(self, mock_func):
        """Test using mocked function"""
        mock_func.return_value = "mocked_result"
        
        result = code_that_calls_mocked_function()
        
        # Verify mock was called
        mock_func.assert_called_once()
        self.assertEqual(result, "mocked_result")
    
    def test_with_context_manager(self):
        """Test using mock as context manager"""
        with patch('module.function') as mock_func:
            mock_func.return_value = "result"
            result = code_under_test()
            self.assertEqual(result, "result")
```

## Test Organization

```
tests/
├── __init__.py
├── core/              - Tests for core tools
│   ├── __init__.py
│   ├── test_base.py               - Base classes
│   ├── test_dict_to_bullet.py     - DictToBulletList tool
│   ├── test_text_cleaner.py       - TextCleaner tool (TODO)
│   └── test_text_collector.py     - TextCollector tool
├── utils/             - Tests for utilities
│   ├── __init__.py
│   ├── test_error_handler.py      - Error handling
│   ├── test_security.py           - Security utilities (TODO)
│   ├── test_validation.py         - Validation framework (TODO)
│   ├── test_profiling.py          - Performance profiling (TODO)
│   ├── json/
│   │   ├── __init__.py
│   │   ├── test_parser.py         - JSON parsing
│   │   ├── test_fixer.py          - JSON fixing (TODO)
│   │   └── test_formatter.py      - JSON formatting (TODO)
│   ├── text/
│   │   ├── __init__.py
│   │   └── test_formatting.py     - Text formatting
│   └── xml/
│       ├── __init__.py
│       └── test_formatter.py      - XML formatting (TODO)
├── di/                - Tests for DI system (TODO)
│   ├── __init__.py
│   ├── test_container.py
│   ├── test_bootstrap.py
│   └── test_interfaces.py
├── ui/                - Tests for UI (TODO)
│   ├── __init__.py
│   ├── test_cli.py
│   └── test_gui.py
├── test_config.py     - Configuration management
├── test_cli.py        - CLI interface
├── test_dependency_injection.py - DI system
├── test_integration.py - Integration tests (TODO)
├── run_tests.py       - Test runner
└── fixtures/          - Shared test data (TODO)
    ├── sample.json
    ├── sample.yaml
    └── ...
```

## Coverage Goals

### By Module
- **Core tools**: 80%+ (high risk of user impact)
- **Utilities**: 75%+ (infrastructure)
- **DI system**: 80%+ (critical for initialization)
- **UI**: 60%+ (GUI harder to test)
- **Configuration**: 75%+

### Overall Goals
- Phase 1 (CRITICAL): 80% coverage
- Phase 2 (HIGH): 70% coverage
- Phase 3 (MEDIUM): 60% coverage
- Final: 70%+ overall coverage

## Continuous Integration

Tests should run automatically:
- On every commit (local pre-commit hook)
- On pull requests (GitHub Actions)
- Nightly full suite with coverage
- Performance benchmarks weekly

## Best Practices

### Do's
- ✓ Test one thing per test method
- ✓ Use descriptive test names (`test_addition_with_positive_numbers`)
- ✓ Use setUp/tearDown for common initialization
- ✓ Mock external dependencies
- ✓ Test error cases, not just happy paths
- ✓ Keep tests fast (< 1ms per test ideal)
- ✓ Use temporary files/directories for file tests
- ✓ Test edge cases (empty inputs, None, large values)

### Don'ts
- ✗ Don't test implementation details, test behavior
- ✗ Don't create long chains of dependencies in tests
- ✗ Don't ignore failing tests
- ✗ Don't test multiple concerns in one test
- ✗ Don't hardcode paths (use tempfile)
- ✗ Don't leave test data around
- ✗ Don't test third-party libraries
- ✗ Don't write tests that sometimes pass/fail randomly

## Debugging Failures

### View Detailed Failure Info
```bash
python -m pytest tests/test_module.py -vv --tb=long
```

### Run Single Failing Test
```bash
python -m unittest tests.module.TestClass.test_method -v
```

### Drop into Debugger on Failure
```bash
python -m pytest tests/test_module.py --pdb
```

### Run Tests with Logging
```bash
python -m pytest tests/ -v -s  # -s shows print output
```

## Special Testing Scenarios

### Testing Exceptions
```python
def test_exception_raised(self):
    with self.assertRaises(ValueError) as ctx:
        raise_error_function()
    
    # Check exception message
    self.assertIn("expected message", str(ctx.exception))
```

### Testing with Multiple Inputs (Parametrized)
```python
import unittest
from parameterized import parameterized

class TestMultipleInputs(unittest.TestCase):
    @parameterized.expand([
        ("input1", "expected1"),
        ("input2", "expected2"),
        ("input3", "expected3"),
    ])
    def test_with_multiple_inputs(self, input_val, expected):
        result = function_under_test(input_val)
        self.assertEqual(result, expected)
```

### Testing Async Code
```python
import asyncio

class TestAsync(unittest.TestCase):
    def test_async_function(self):
        async def async_test():
            result = await async_function()
            return result
        
        result = asyncio.run(async_test())
        self.assertEqual(result, expected)
```

## Resources

### Related Documentation
- [Architecture Documentation](ARCHITECTURE.md) - System design
- [Security Documentation](SECURITY.md) - Security considerations
- [Performance Documentation](PERFORMANCE.md) - Performance guidelines
- [API Reference](API_REFERENCE.md) - Class/function signatures

### Python Testing Resources
- [unittest documentation](https://docs.python.org/3/library/unittest.html)
- [pytest documentation](https://docs.pytest.org/)
- [mock documentation](https://docs.python.org/3/library/unittest.mock.html)

## Questions & Support

For questions about testing this project:
1. Check the [TEST_COVERAGE_ANALYSIS.md](TEST_COVERAGE_ANALYSIS.md) for detailed specs
2. Look at existing test files for patterns
3. Review the module's docstrings for API details
4. Consult the Architecture documentation

---

**Last Updated**: November 14, 2025
**Test Coverage**: ~17% (1,703 lines of tests / ~10,000 lines of code)
**Priority**: Improve to 70%+ coverage across all modules
