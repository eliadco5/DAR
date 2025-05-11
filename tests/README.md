# Test Suite Documentation

This directory contains test scripts for validating the functionality of the application.

## Key Test Files

- `test_continue_functionality.py`: Tests the continuation feature during playback
- `test_check_failure_mode.py`: Tests the check failure handling, particularly with continue and stop buttons
- `run_tests.py`: Runner script to execute all test files

## Running Tests

### Method 1: Using the test runner

To run all tests:

```bash
python run_tests.py
```

### Method 2: Running individual test files

To run a specific test file:

```bash
python -m tests.test_continue_functionality
# or
python -m tests.test_check_failure_mode
```

### Method 3: Using unittest directly

```bash
python -m unittest discover tests
```

## Test Structure

Each test class follows a similar structure:

1. **Setup and Teardown**: Initialize the application environment and clean up after tests
2. **Test Data Creation**: Generate test actions with visual checks
3. **Event Simulation**: Simulate user interactions like clicking continue or stop
4. **Validation**: Verify the application behaves correctly in response to these events

## Test Environment

Tests use the PyQt6 event loop to simulate real-world usage. They create a MainWindow instance and interact with it programmatically.

Key concepts:
- QTimer is used to schedule actions
- QApplication.processEvents() processes the event queue during waiting periods
- Tests override certain methods (like showMinimized) to make testing more reliable

## Troubleshooting

If tests fail, check the following:

1. Ensure PyQt6 is properly installed
2. Verify the project structure is correct
3. Check for timing issues - tests may need longer timeouts in some environments
4. Look for modal dialogs that might block test execution

## Adding New Tests

To add a new test:

1. Create a new test file in the tests directory
2. Import the required modules
3. Create a test class inheriting from unittest.TestCase
4. Implement setup, teardown, and test methods
5. Add your test class to run_tests.py 