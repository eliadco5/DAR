# Test Suite for Desktop Automation Recorder

This directory contains various test scripts to verify the functionality of the Desktop Automation Recorder.

## Available Tests

### 1. Core Functionality Tests

- **test_full_functionality.py**: Comprehensive test to verify all aspects of the script generator, including check names and comments.
  ```
  python test_full_functionality.py
  ```

- **test_ui_comments.py**: Tests the display of comments in the UI with proper styling.
  ```
  python test_ui_comments.py
  ```

- **test_hotkeys.py**: Tests the functionality of adding checks and comments through direct method calls.
  ```
  python test_hotkeys.py
  ```

### 2. Other Tests

- **simple_test.py**: Basic test with minimal actions.
  ```
  python simple_test.py
  ```

- **test_flags.py**: Tests the command-line flags for the generated scripts.
  ```
  python test_flags.py
  ```

- **test_script_gen.py**: Tests script generation options.
  ```
  python test_script_gen.py
  ```

## Running All Tests

To run all tests together, use:

```bash
python -m unittest discover tests
```

## Test Description

### test_full_functionality.py
This script tests the complete functionality of the Desktop Automation Recorder by:
1. Creating actions of all types (mouse, keyboard, checks, comments)
2. Generating a script with custom check names and comments
3. Verifying that the script includes all expected features
4. Validating that screenshots are saved correctly

### test_ui_comments.py
This script tests the UI representation of comments by:
1. Opening the UI and starting a recording session
2. Adding several test comments
3. Verifying that they appear in the action list with the correct styling (colors and fonts)
4. Generating a script and verifying comments are included

### test_hotkeys.py
This script tests the comment and check functionality by:
1. Opening the UI and starting a recording session
2. Directly calling the methods that handle checks and comments
3. Mocking dialog interaction to simulate user input
4. Verifying that checks and comments are added to the action list

## Troubleshooting

- If you encounter focus issues with dialog windows when using hotkey tests, try using the direct method call approach as implemented in `test_hotkeys.py`.
- If screenshot verification fails, check that the screenshots directory exists and has proper permissions.
- For UI tests, make sure to allow sufficient time between operations, especially when dialogs need to appear and process input. 