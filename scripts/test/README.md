# Test Scripts

This directory contains scripts for running tests in different configurations optimized for various scenarios.

## Available Scripts

### 🚀 `fast.sh` - Fast Development Tests
```bash
./scripts/test/fast.sh
```
- **Purpose**: Rapid feedback during development
- **Excludes**: Slow tests (json_fixer)
- **Time**: < 2 minutes
- **Coverage**: ~50-60%
- **Use when**: Making changes and want quick validation

### 🔄 `ci.sh` - CI/CD Pipeline Tests
```bash
./scripts/test/ci.sh
```
- **Purpose**: Automated CI/CD pipeline testing
- **Excludes**: Slow tests to avoid OOM issues
- **Time**: < 3 minutes
- **Coverage**: ~50-60%
- **Generates**: HTML, XML, and terminal coverage reports
- **Use when**: Running in CI/CD (GitHub Actions, CircleCI, etc.)

### 📦 `full.sh` - Complete Test Suite
```bash
./scripts/test/full.sh
```
- **Purpose**: Comprehensive validation
- **Includes**: All tests including slow ones
- **Time**: < 5 minutes
- **Coverage**: ~60-70%
- **Warning**: Resource intensive, may cause OOM on constrained systems
- **Use when**: Pre-release validation, nightly builds

### 🐌 `slow.sh` - Slow Tests Only
```bash
./scripts/test/slow.sh
```
- **Purpose**: Run only resource-intensive tests
- **Includes**: json_fixer tests (86 tests)
- **Time**: 2-3 minutes
- **Coverage**: Not collected (to avoid OOM)
- **Use when**: Specifically validating json_fixer functionality

### ⚡ `parallel.sh` - Parallel Execution
```bash
./scripts/test/parallel.sh
```
- **Purpose**: Maximum speed test execution
- **Requires**: pytest-xdist
- **Excludes**: Slow tests
- **Time**: < 1 minute
- **Uses**: Auto-detected CPU cores
- **Use when**: You have a multi-core machine and want fastest feedback

## Test Markers

Tests are organized using pytest markers:

- **`@pytest.mark.slow`**: Resource-intensive tests (json_fixer)
- **`@pytest.mark.fast`**: Quick unit tests
- **`@pytest.mark.integration`**: Integration tests
- **`@pytest.mark.unit`**: Unit tests

## Running Tests Manually

### Exclude slow tests
```bash
pytest -m "not slow"
```

### Only slow tests
```bash
pytest -m slow
```

### With coverage
```bash
pytest --cov=annotation_toolkit --cov-report=html
```

### Parallel execution
```bash
pytest -n auto -m "not slow"
```

### Specific test file
```bash
pytest tests/core/test_dict_to_bullet.py -v
```

## CI/CD Integration

For CI/CD pipelines, use the `ci.sh` script or run:

```bash
# GitHub Actions, CircleCI, Travis CI, etc.
pytest -m "not slow" \
    --cov=annotation_toolkit \
    --cov-report=xml \
    --maxfail=5 \
    --tb=short
```

This configuration:
- Excludes slow tests to prevent OOM
- Generates XML coverage for services like Codecov
- Fails fast after 5 failures
- Uses short tracebacks for cleaner logs

## Coverage Reports

After running tests with coverage, reports are generated in:

- **HTML**: `htmlcov/index.html` - Open in browser
- **XML**: `coverage.xml` - For CI/CD tools
- **Terminal**: Shown during test execution

## Performance Targets

| Test Suite | Target Time | Coverage Target |
|------------|-------------|-----------------|
| Fast       | < 2 min     | 50-60%         |
| CI         | < 3 min     | 50-60%         |
| Full       | < 5 min     | 60-70%         |
| Parallel   | < 1 min     | 50-60%         |

## Troubleshooting

### Out of Memory (Exit 137)
- Use `fast.sh` or `ci.sh` instead of `full.sh`
- Run slow tests separately without coverage
- Reduce parallel workers: `pytest -n 2` instead of `-n auto`

### Tests Taking Too Long
- Use parallel execution: `./scripts/test/parallel.sh`
- Skip slow tests: `pytest -m "not slow"`
- Run specific test files instead of full suite

### Coverage Not Generated
- Ensure pytest-cov is installed: `pip install pytest-cov`
- Check pyproject.toml coverage configuration
- Run with explicit coverage flags: `pytest --cov=annotation_toolkit`
