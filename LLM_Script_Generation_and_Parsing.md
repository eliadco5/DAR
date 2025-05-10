# LLM Guide: How to Build & Parse Scripts

This guide explains how LLMs can directly generate Desktop Automation Recorder scripts from text descriptions, following the same structure produced by the `scriptgen/generator.py` module. The goal is to enable LLMs to create test scripts programmatically without requiring the user to record actions manually.

## Script Structure and Format

When generating scripts automatically, your output should follow the exact format that `generator.py` produces. Below is the structure to follow:

```python
import os
import pyautogui
import time
import sys
import json
import datetime
import traceback
import argparse
from PIL import Image, ImageChops, ImageStat

pyautogui.FAILSAFE = True

# Parse command line arguments
parser = argparse.ArgumentParser(description='Automated UI test script')
parser.add_argument('-y', '--yes', action='store_true', help='Automatically answer "yes" to continue prompts')
parser.add_argument('-n', '--no', action='store_true', help='Automatically answer "no" to continue prompts')
parser.add_argument('--headless', action='store_true', help='Run in headless mode, continue on errors')
args = parser.parse_args()

# Check for conflicting arguments
if args.yes and args.no:
    print("Error: Cannot specify both --yes and --no flags")
    sys.exit(2)

# Test reporting variables
test_results = {
    "test_name": os.path.basename(__file__),
    "start_time": "",
    "end_time": "",
    "duration_seconds": 0,
    "status": "PENDING",
    "visual_checks": [],
    "errors": [],
    "checks_passed": 0,
    "checks_failed": 0,
    "tolerance_level": "Medium",
    "tolerance_value": 7,
    "failure_line": None,
    "failure_details": None,
    "auto_continue": "no" if args.no else "yes" if args.yes else None
}

# [Helper functions section - include all verify_screenshot, images_are_similar, etc. functions]

def run_test():
    """Run the test and return results"""
    start_time = datetime.datetime.now()
    test_results["start_time"] = start_time.isoformat()
    test_results["status"] = "RUNNING"
    
    try:
        print(f"Starting test: {test_results['test_name']}")
        print(f"Tolerance level: {test_results['tolerance_level']} ({test_results['tolerance_value']})")
        if args.yes:
            print("Auto-continue mode enabled (--yes flag)")
        elif args.no:
            print("Auto-stop mode enabled (--no flag)")
        elif HEADLESS_MODE:
            print("Headless mode enabled (--headless flag)")
        # Initial wait before starting the test
        time.sleep(2)

        # YOUR GENERATED TEST ACTIONS WILL GO HERE
        
        # Example actions - replace with your generated content:
        # ====================
        # Login to application
        # ====================
        
        print(f"\n[COMMENT] Login to application\n")
        
        pyautogui.click(500, 300)
        pyautogui.write('username')
        pyautogui.press('tab')
        pyautogui.write('password')
        pyautogui.press('enter')
        
        # Test completed successfully if we got here
        if test_results["status"] == "RUNNING":
            test_results["status"] = "PASSED"
        return test_results
    except Exception as e:
        # [Exception handling code]
        test_results["status"] = "ERROR"
        return test_results
    finally:
        # [Cleanup code]

# Entry point for both script execution and importing as a module
if __name__ == "__main__":
    results = run_test()
    sys.exit(0 if results["status"] == "PASSED" else 1)
else:
    pass  # No additional action needed
```

## How to Generate Scripts from Text Input

As an LLM, your task is to convert natural language test descriptions into executable Python scripts following the format above. Below are the specific steps and formats to follow:

### Step 1: Understand the Actions to Generate

When a user provides a test description like:
```
Create a login test that:
1. Opens the application
2. Enters username "admin"
3. Enters password "password123"
4. Clicks the login button
5. Verifies the dashboard appears
```

You should translate these steps into specific pyautogui commands and verification steps.

### Step 2: Structure Your Output

Your generated code should:

1. Include all necessary imports and boilerplate code
2. Map each user instruction to appropriate PyAutoGUI commands
3. Add appropriate comments and visual checks where specified
4. Structure everything within the `run_test()` function

### Step 3: Use the Correct PyAutoGUI Commands

Map user actions to these PyAutoGUI commands:

#### Mouse Actions
```python
# Click
pyautogui.click(x, y)

# Move cursor without clicking
pyautogui.moveTo(x, y)

# Mouse down/up separately
pyautogui.mouseDown(x, y)
pyautogui.mouseUp(x, y)

# Right click
pyautogui.rightClick(x, y)

# Double click
pyautogui.doubleClick(x, y)

# Scroll
pyautogui.scroll(amount, x, y)
```

#### Keyboard Actions
```python
# Type text
pyautogui.write('text to type')

# Press a single key
pyautogui.press('enter')  # Other keys: tab, esc, space, backspace, delete

# Key combinations
pyautogui.hotkey('ctrl', 'c')  # Copy
pyautogui.hotkey('ctrl', 'v')  # Paste

# Press and release modifier keys
pyautogui.keyDown('shift')
pyautogui.keyUp('shift')
```

#### Timing and Waits
```python
# Wait for a specific time
time.sleep(seconds)

# Dynamic wait (a better practice than fixed sleeps when possible)
while not pyautogui.pixelMatchesColor(x, y, (r, g, b)):
    time.sleep(0.1)
    timeout -= 0.1
    if timeout <= 0:
        raise Exception("Timed out waiting for element")
```

### Step 4: Add Comments and Checks

For comments (section breaks), use:
```python
# ====================
# Comment text
# ====================

print(f"\n[COMMENT] Comment text\n")
```

For visual checks, use:
```python
print(f"Check #{check_index}: Performing manual visual check: {check_name}")
verify_window_screenshot(os.path.join(os.path.dirname(__file__), f'screenshots/check_{check_index}.png'), check_name=check_name, check_index=check_index)
print(f"Check #{check_index}: Visual check completed")
```

## Example Text Input to Script Conversion

### Input:
```
Create a test script that:
- Logs into Gmail
- Composes a new email
- Sends it to test@example.com
- Verifies the email appears in the sent folder
```

### Output:
```python
def run_test():
    """Run the test and return results"""
    start_time = datetime.datetime.now()
    test_results["start_time"] = start_time.isoformat()
    test_results["status"] = "RUNNING"
    
    try:
        print(f"Starting test: {test_results['test_name']}")
        # Initial wait
        time.sleep(2)
        
        # ====================
        # Login to Gmail
        # ====================
        
        print(f"\n[COMMENT] Login to Gmail\n")
        
        # Navigate to Gmail
        pyautogui.click(500, 60)  # Click address bar
        pyautogui.write('mail.google.com')
        pyautogui.press('enter')
        time.sleep(3)  # Wait for page to load
        
        # Enter credentials
        pyautogui.click(500, 300)  # Email field
        pyautogui.write('your.email@gmail.com')
        pyautogui.press('enter')
        time.sleep(2)
        
        pyautogui.click(500, 300)  # Password field
        pyautogui.write('your_password')
        pyautogui.press('enter')
        time.sleep(5)  # Wait for Gmail to load
        
        # Check successful login
        print(f"Check #1: Performing manual visual check: Gmail Inbox Loaded")
        verify_window_screenshot(os.path.join(os.path.dirname(__file__), 'screenshots/check_1.png'), check_name="Gmail Inbox Loaded", check_index=1)
        print(f"Check #1: Visual check completed")
        
        # ====================
        # Compose a new email
        # ====================
        
        print(f"\n[COMMENT] Compose a new email\n")
        
        # Click compose button
        pyautogui.click(100, 200)
        time.sleep(1)
        
        # Fill email details
        pyautogui.click(500, 250)  # To field
        pyautogui.write('test@example.com')
        
        pyautogui.press('tab')  # Move to subject
        pyautogui.write('Test Email from Automation')
        
        pyautogui.press('tab')  # Move to body
        pyautogui.write('This is an automated test email.')
        
        # ====================
        # Send the email
        # ====================
        
        print(f"\n[COMMENT] Send the email\n")
        
        # Click send button
        pyautogui.click(100, 600)
        time.sleep(3)
        
        # ====================
        # Verify sent email
        # ====================
        
        print(f"\n[COMMENT] Verify sent email\n")
        
        # Navigate to sent folder
        pyautogui.click(100, 400)  # Sent folder
        time.sleep(2)
        
        # Verify email appears in sent folder
        print(f"Check #2: Performing manual visual check: Email In Sent Folder")
        verify_window_screenshot(os.path.join(os.path.dirname(__file__), 'screenshots/check_2.png'), check_name="Email In Sent Folder", check_index=2)
        print(f"Check #2: Visual check completed")
        
        # Test completed successfully
        if test_results["status"] == "RUNNING":
            test_results["status"] = "PASSED"
        return test_results
        
    except Exception as e:
        # Exception handling code
        test_results["status"] = "ERROR"
        return test_results
```

## Parsing Scripts into Modules

When breaking a script into modules or combining multiple scripts, follow these approaches:

### Identifying Section Boundaries

- **Comment Markers**: Use the `# ====================` comment blocks as natural section breaks
- **Check Points**: Visual verification steps indicate logical test boundaries
- **Sleep Statements**: Long waits (>3 seconds) often indicate transitions between test phases

### Extracting Modular Components

To extract a reusable module:

1. Identify the code block you want to modularize (typically between comment sections)
2. Extract it into a function with appropriate parameters
3. Replace the original code with a call to the new function

Example:
```python
def login_to_application(username, password):
    # ====================
    # Login to application
    # ====================
    
    print(f"\n[COMMENT] Login to application\n")
    
    pyautogui.click(500, 300)  # Username field
    pyautogui.write(username)
    pyautogui.press('tab')
    pyautogui.write(password)
    pyautogui.press('enter')
    time.sleep(2)  # Wait for login
    
    # Verify login successful
    print(f"Check #1: Performing manual visual check: Login Successful")
    verify_window_screenshot(os.path.join(os.path.dirname(__file__), 'screenshots/check_1.png'), check_name="Login Successful", check_index=1)
    print(f"Check #1: Visual check completed")
```

## Conclusion

By following this guide, LLMs should be able to:
1. Generate complete test automation scripts directly from natural language descriptions
2. Produce scripts that follow the same structure and format as those generated by the application's recording feature
3. Create modular, maintainable scripts that can be combined or split as needed

When generating scripts, ensure all necessary boilerplate code is included and that actions are translated correctly into PyAutoGUI commands. Use comments and visual checks strategically to make scripts more maintainable and functional. 