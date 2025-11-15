#!/bin/bash
# Full test suite with coverage for CI/CD
# Includes all tests but excludes json_fixer to avoid OOM
# Usage: ./scripts/test/ci.sh

set -e

echo "========================================="
echo "Running CI test suite with coverage"
echo "Expected time: < 3 minutes"
echo "========================================="
echo ""

# Clean previous coverage data
coverage erase

# Run tests excluding slow marker with coverage
pytest -m "not slow" \
    --cov=annotation_toolkit \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=xml \
    --tb=short \
    --maxfail=5 \
    -v

echo ""
echo "========================================="
echo "CI tests completed successfully!"
echo "Coverage report generated in htmlcov/"
echo "========================================="
