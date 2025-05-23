# Annotation Toolkit Test Suite

This directory contains the comprehensive test suite for the Annotation Toolkit project. The tests are organized to mirror the structure of the main package, making it easy to locate tests for specific components.

## Test Structure

The test suite is organized as follows:

- `tests/` - Root directory for all tests
  - `core/` - Tests for core functionality
    - `test_dict_to_bullet.py` - Tests for the Dictionary to Bullet List tool
    - (Other core component tests)
  - `utils/` - Tests for utility modules
    - `json/` - Tests for JSON utilities
      - `test_parser.py` - Tests for JSON parsing utilities
    - `text/` - Tests for text utilities
      - `test_formatting.py` - Tests for text formatting utilities
    - `test_error_handler.py` - Tests for error handling utilities
  - `test_base.py` - Tests for base classes
  - `test_cli.py` - Tests for command-line interface
  - `test_config.py` - Tests for configuration management
  - `run_tests.py` - Script to run all tests

## Running Tests

### Basic Usage

To run all tests:

```bash
python -m tests.run_tests
```

Or from the tests directory:

```bash
python run_tests.py
```

### Command-Line Options

The `run_tests.py` script supports several command-line options:

- `-v, --verbosity`: Set verbosity level (1-3, default: 2)
- `-p, --pattern`: Pattern to match test files (default: "test_*.py")
- `-d, --directory`: Directory to start discovery (default: tests directory)
- `-f, --failfast`: Stop on first failure
- `--coverage`: Run tests with coverage report

Examples:

```bash
# Run with increased verbosity
python run_tests.py -v 3

# Run only tests in the utils directory
python run_tests.py -d utils

# Run with coverage report
python run_tests.py --coverage

# Run only tests matching a specific pattern
python run_tests.py -p "test_config*.py"
```

### Running Individual Test Files

You can also run individual test files directly:

```bash
python -m unittest tests.test_config
python -m unittest tests.core.test_dict_to_bullet
```

## Test Coverage

The test suite aims to provide comprehensive coverage of the Annotation Toolkit codebase, including:

1. **Core Functionality Tests**
   - Base classes and interfaces
   - Text annotation tools
   - JSON annotation tools
   - Conversation visualization tools

2. **CLI Tests**
   - Command-line argument parsing
   - Command execution
   - Error handling

3. **Configuration Tests**
   - Loading configuration from files
   - Environment variable overrides
   - Configuration validation

4. **Utility Tests**
   - Error handling utilities
   - JSON parsing and formatting
   - Text formatting utilities

## Adding New Tests

When adding new functionality to the toolkit, please follow these guidelines for adding tests:

1. Create test files that mirror the structure of the main package
2. Use descriptive test method names that clearly indicate what is being tested
3. Include both positive tests (expected behavior) and negative tests (error handling)
4. Use mocks and patches to isolate the code being tested from external dependencies
5. Add docstrings to test classes and methods to explain what they test

## Requirements

The test suite requires the following packages:

- `pytest` (for running tests)
- `pytest-cov` (for coverage reports)

These can be installed via pip:

```bash
pip install pytest pytest-cov
```
