import os
import sys
import unittest
import coverage
from datetime import datetime


def setup_test_environment():
    """Setup the test environment"""
    print("Setting up test environment...")

    # Clean up any existing test databases
    test_files = [
        "test_clothing_store.db",
        "test_clothing_store.db-journal"
    ]

    for file in test_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"Removed existing test file: {file}")
            except Exception as e:
                print(f"Warning: Could not remove {file}: {e}")


def run_tests_with_coverage():
    """Run tests with coverage reporting"""
    # Start coverage monitoring
    cov = coverage.Coverage(
        branch=True,
        source=['clothing_store_db', 'inventory_utils', 'triggers'],
        omit=['test_*', 'run_tests.py']
    )
    cov.start()

    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.discover('.', pattern='test_*.py')

    # Create test result
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    # Stop coverage monitoring
    cov.stop()
    cov.save()

    # Create coverage reports
    print("\nCoverage Report:")
    cov.report()

    # Generate HTML coverage report
    cov.html_report(directory='coverage_report')

    return result.wasSuccessful()


def cleanup_test_environment():
    """Clean up after tests"""
    print("\nCleaning up test environment...")

    # Remove test files
    test_files = [
        "test_clothing_store.db",
        "test_clothing_store.db-journal"
    ]

    for file in test_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"Cleaned up test file: {file}")
            except Exception as e:
                print(f"Warning: Could not remove {file}: {e}")


def generate_test_report(success):
    """Generate test execution report"""
    report = f"""
Test Execution Report
====================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Status: {'Success' if success else 'Failure'}

Coverage report has been generated in the coverage_report directory.
"""

    with open('test_report.txt', 'w') as f:
        f.write(report)

    print("\nTest report generated: test_report.txt")


if __name__ == '__main__':
    try:
        # Setup
        setup_test_environment()

        # Run tests
        print("\nRunning tests...")
        success = run_tests_with_coverage()

        # Generate report
        generate_test_report(success)

        # Cleanup
        cleanup_test_environment()

        # Exit with appropriate status
        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"\nError during test execution: {e}")
        sys.exit(1)
    finally:
        cleanup_test_environment()