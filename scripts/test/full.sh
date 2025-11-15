#!/bin/bash
# Complete test suite including slow tests
# For comprehensive validation (nightly builds, releases)
# Usage: ./scripts/test/full.sh

set -e

echo "========================================="
echo "Running FULL test suite (including slow tests)"
echo "Expected time: < 5 minutes"
echo "Warning: Resource intensive!"
echo "========================================="
echo ""

# Clean previous coverage data
coverage erase

# Run all tests with coverage
pytest \
    --cov=annotation_toolkit \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=xml \
    --tb=short \
    -v

echo ""
echo "========================================="
echo "Full tests completed successfully!"
echo "Coverage report generated in htmlcov/"
echo "========================================="
