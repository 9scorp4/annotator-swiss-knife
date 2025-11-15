#!/bin/bash
# Fast test suite for rapid development feedback
# Excludes slow tests (json_fixer) to run in < 2 minutes
# Usage: ./scripts/test/fast.sh

set -e

echo "========================================="
echo "Running FAST test suite (excluding slow tests)"
echo "Expected time: < 2 minutes"
echo "========================================="
echo ""

# Run tests excluding slow marker
pytest -m "not slow" \
    --tb=short \
    --maxfail=5 \
    -v

echo ""
echo "========================================="
echo "Fast tests completed successfully!"
echo "========================================="
