#!/usr/bin/env python3
"""
Test runner for the annotation toolkit.

This script runs all the tests for the annotation toolkit using unittest discovery.
"""

import os
import sys
import unittest
import argparse


def run_tests(verbosity=1, pattern="test_*.py", start_dir=".", failfast=False):
    """
    Run all tests matching the pattern.

    Args:
        verbosity (int): Verbosity level (1-3).
        pattern (str): Pattern to match test files.
        start_dir (str): Directory to start discovery.
        failfast (bool): Stop on first failure.

    Returns:
        bool: True if all tests pass, False otherwise.
    """
    # Get the absolute path to the tests directory
    tests_dir = os.path.abspath(os.path.dirname(__file__))

    # If start_dir is the default, use the tests directory
    if start_dir == ".":
        start_dir = tests_dir

    # Create a test loader
    loader = unittest.TestLoader()

    # Discover tests
    suite = loader.discover(start_dir=start_dir, pattern=pattern)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity, failfast=failfast)
    result = runner.run(suite)

    # Return True if successful, False otherwise
    return result.wasSuccessful()


def main():
    """Parse command line arguments and run tests."""
    parser = argparse.ArgumentParser(description="Run annotation toolkit tests")
    parser.add_argument(
        "-v", "--verbosity",
        type=int,
        choices=[1, 2, 3],
        default=2,
        help="Verbosity level (1-3)"
    )
    parser.add_argument(
        "-p", "--pattern",
        type=str,
        default="test_*.py",
        help="Pattern to match test files"
    )
    parser.add_argument(
        "-d", "--directory",
        type=str,
        default=".",
        help="Directory to start discovery"
    )
    parser.add_argument(
        "-f", "--failfast",
        action="store_true",
        help="Stop on first failure"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run tests with coverage report"
    )

    args = parser.parse_args()

    if args.coverage:
        try:
            import coverage
            cov = coverage.Coverage(
                source=["annotation_toolkit"],
                omit=["*/tests/*", "*/venv/*"]
            )
            cov.start()
            success = run_tests(
                verbosity=args.verbosity,
                pattern=args.pattern,
                start_dir=args.directory,
                failfast=args.failfast
            )
            cov.stop()
            cov.save()
            print("\nCoverage Report:")
            cov.report()
            return 0 if success else 1
        except ImportError:
            print("Error: coverage package not installed. Run 'pip install pytest-cov' first.")
            return 1
    else:
        success = run_tests(
            verbosity=args.verbosity,
            pattern=args.pattern,
            start_dir=args.directory,
            failfast=args.failfast
        )
        return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
