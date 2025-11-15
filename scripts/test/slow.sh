#!/bin/bash
# Slow tests only (json_fixer tests)
# Usage: ./scripts/test/slow.sh

set -e

echo "========================================="
echo "Running SLOW tests only (json_fixer)"
echo "Expected time: 2-3 minutes"
echo "========================================="
echo ""

# Run only slow tests without coverage to avoid OOM
pytest -m slow \
    --tb=short \
    -v

echo ""
echo "========================================="
echo "Slow tests completed successfully!"
echo "========================================="
