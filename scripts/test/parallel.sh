#!/bin/bash
# Parallel test execution for maximum speed
# Requires pytest-xdist
# Usage: ./scripts/test/parallel.sh

set -e

echo "========================================="
echo "Running tests in PARALLEL mode"
echo "Expected time: < 1 minute"
echo "========================================="
echo ""

# Run tests excluding slow marker in parallel
pytest -m "not slow" \
    -n auto \
    --tb=short \
    --maxfail=5 \
    -v

echo ""
echo "========================================="
echo "Parallel tests completed successfully!"
echo "========================================="
