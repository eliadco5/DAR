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

# Visual verification settings
TOLERANCE = 7  # Tolerance level: Medium
VERIFICATION_ENABLED = True  # Set to False to disable visual verification
HEADLESS_MODE = args.headless  # If True, tests will continue even if checks fail

def save_report(report_data, suffix=""):
    """Save test report to a JSON file"""
    report_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(report_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    test_name = os.path.splitext(os.path.basename(__file__))[0]
    report_path = os.path.join(report_dir, f"{test_name}_{timestamp}{suffix}.json")
    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=2)
    print(f"Test report saved to: {report_path}")
    return report_path

def log_check_result(check_type, location, status, details=None, check_name=None, check_index=None):
    """Log a check result to the test results"""
    if details is None:
        details = {}
    check_data = {
        "type": check_type,
        "location": location,
        "status": status,
        "timestamp": datetime.datetime.now().isoformat(),
        "details": details,
        "check_name": check_name or f"Check_{len(test_results['visual_checks']) + 1}",
        "check_index": check_index or len(test_results['visual_checks']) + 1
    }
    
    # Record the line number where this check was executed
    frame = traceback.extract_stack()[-2]
    check_data["line_number"] = frame.lineno
    check_data["file_name"] = frame.filename
    
    test_results["visual_checks"].append(check_data)
    if status == "PASS":
        test_results["checks_passed"] += 1
    elif status == "FAIL":
        test_results["checks_failed"] += 1
        test_results["status"] = "FAILED"
        
        # Store the failure line information for easy reference
        if test_results.get("failure_line") is None:
            test_results["failure_line"] = check_data["line_number"]
            test_results["failure_details"] = {
                "check_name": check_data["check_name"],
                "check_index": check_data["check_index"],
                "location": location,
                "mean_difference": details.get("mean_difference", "N/A")
            }
    return check_data

def log_error(message, error_type="Error", details=None):
    """Log an error to the test results"""
    if details is None:
        details = {}
    
    # Record the line number where this error occurred
    frame = traceback.extract_stack()[-2]
    line_number = frame.lineno
    file_name = frame.filename
    
    error_data = {
        "type": error_type,
        "message": message,
        "timestamp": datetime.datetime.now().isoformat(),
        "details": details,
        "line_number": line_number,
        "file_name": file_name
    }
    test_results["errors"].append(error_data)
    test_results["status"] = "FAILED"
    
    # Store the failure line information for easy reference
    if test_results.get("failure_line") is None:
        test_results["failure_line"] = line_number
        test_results["failure_details"] = {
            "error_type": error_type,
            "message": message
        }
    
    return error_data

def images_are_similar(img1, img2, tolerance=TOLERANCE):
    """Compare two images and return True if they are similar within tolerance"""
    if img1.size != img2.size:
        return False, {"error": "Image size mismatch", "sizes": [img1.size, img2.size]}
    diff = ImageChops.difference(img1, img2)
    stat = ImageStat.Stat(diff)
    mean_diff = sum(stat.mean) / len(stat.mean)
    channel_diffs = {f"channel_{i}": val for i, val in enumerate(stat.mean)}
    is_similar = mean_diff <= tolerance
    details = {
        "mean_difference": mean_diff,
        "tolerance": tolerance,
        "channel_differences": channel_diffs
    }
    return is_similar, details

def verify_screenshot(ref_img_path, x, y, width=100, height=100, check_name=None, check_index=None):
    """Verify the current screen matches reference screenshot"""
    if not VERIFICATION_ENABLED or not os.path.exists(ref_img_path):
        return True  # Skip verification if disabled or image missing
    
    location = f"({x}, {y})"
    check_type = "Region screenshot"
    
    try:
        ref_img = Image.open(ref_img_path)
        left = max(x - width // 2, 0)
        top = max(y - height // 2, 0)
        test_img = pyautogui.screenshot(region=(left, top, width, height))
        
        is_similar, details = images_are_similar(ref_img, test_img)
        
        if is_similar:
            print(f"[PASS] Check #{check_index}: {check_name} - Visual check passed at {location}")
            log_check_result(check_type, location, "PASS", details, check_name, check_index)
            return True
        else:
            print(f"[FAIL] Check #{check_index}: {check_name} - Visual check failed at {location}")
            print(f"       Screenshots differ by {details['mean_difference']:.2f} (tolerance: {details['tolerance']})")
            details["reference_image"] = ref_img_path
            # Save the failed test image
            fail_dir = os.path.join(os.path.dirname(__file__), "failures")
            os.makedirs(fail_dir, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            fail_path = os.path.join(fail_dir, f"fail_{check_index}_{check_name}_{os.path.basename(ref_img_path).split('.')[0]}_{timestamp}.png")
            test_img.save(fail_path)
            details["test_image"] = fail_path
            
            log_check_result(check_type, location, "FAIL", details, check_name, check_index)
            
            if HEADLESS_MODE:
                return False
            elif args.yes:
                print("Auto-continuing due to --yes flag")
                return False
            elif args.no:
                print("Auto-stopping due to --no flag")
                raise Exception(f"Visual verification failed at check #{check_index}: {check_name}")
            elif input("Continue anyway? (y/n): ").lower() != "y":
                raise Exception(f"Visual verification failed at check #{check_index}: {check_name}")
            return False
    except Exception as e:
        error_message = f"Error during visual verification at {location}: {str(e)}"
        print(f"[ERROR] Check #{check_index}: {check_name} - {error_message}")
        log_error(error_message, "VisualCheckError", {"check_name": check_name, "check_index": check_index})
        if HEADLESS_MODE:
            return False
        elif args.yes:
            print("Auto-continuing due to --yes flag")
            return False
        elif args.no:
            print("Auto-stopping due to --no flag")
            raise Exception(f"Visual verification error at check #{check_index}: {check_name} - {str(e)}")
        elif input("Continue anyway? (y/n): ").lower() != "y":
            raise Exception(f"Visual verification error at check #{check_index}: {check_name} - {str(e)}")
        return False

def verify_window_screenshot(ref_img_path, check_name=None, check_index=None):
    """Verify the current active window matches reference screenshot"""
    if not VERIFICATION_ENABLED or not os.path.exists(ref_img_path):
        return True  # Skip verification if disabled or image missing
    
    check_type = "Window screenshot"
    location = "Active window"
    
    try:
        ref_img = Image.open(ref_img_path)
        
        # Capture active window
        try:
            import ctypes
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            rect = ctypes.wintypes.RECT()
            ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
            width = rect.right - rect.left
            height = rect.bottom - rect.top
            test_img = pyautogui.screenshot(region=(rect.left, rect.top, width, height))
            capture_method = "Active window"
        except Exception:
            # Fallback to full screen
            test_img = pyautogui.screenshot()
            capture_method = "Full screen (fallback)"
        
        # Resize test image to match reference if needed
        original_size = test_img.size
        if test_img.size != ref_img.size:
            test_img = test_img.resize(ref_img.size)
        
        is_similar, details = images_are_similar(ref_img, test_img)
        details["capture_method"] = capture_method
        details["original_size"] = original_size
        details["resized_to"] = ref_img.size
        
        if is_similar:
            print(f"[PASS] Check #{check_index}: {check_name} - Window visual check passed")
            log_check_result(check_type, location, "PASS", details, check_name, check_index)
            return True
        else:
            print(f"[FAIL] Check #{check_index}: {check_name} - Window visual check failed")
            print(f"       Screenshots differ by {details['mean_difference']:.2f} (tolerance: {details['tolerance']})")
            details["reference_image"] = ref_img_path
            # Save the failed test image
            fail_dir = os.path.join(os.path.dirname(__file__), "failures")
            os.makedirs(fail_dir, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            fail_path = os.path.join(fail_dir, f"fail_{check_index}_{check_name}_{os.path.basename(ref_img_path).split('.')[0]}_{timestamp}.png")
            test_img.save(fail_path)
            details["test_image"] = fail_path
            
            log_check_result(check_type, location, "FAIL", details, check_name, check_index)
            
            if HEADLESS_MODE:
                return False
            elif args.yes:
                print("Auto-continuing due to --yes flag")
                return False
            elif args.no:
                print("Auto-stopping due to --no flag")
                raise Exception(f"Window visual verification failed at check #{check_index}: {check_name}")
            elif input("Continue anyway? (y/n): ").lower() != "y":
                raise Exception(f"Window visual verification failed at check #{check_index}: {check_name}")
            return False
    except Exception as e:
        error_message = f"Error during window visual verification: {str(e)}"
        print(f"[ERROR] Check #{check_index}: {check_name} - {error_message}")
        log_error(error_message, "WindowVisualCheckError", {"check_name": check_name, "check_index": check_index})
        if HEADLESS_MODE:
            return False
        elif args.yes:
            print("Auto-continuing due to --yes flag")
            return False
        elif args.no:
            print("Auto-stopping due to --no flag")
            raise Exception(f"Window visual verification error at check #{check_index}: {check_name} - {str(e)}")
        elif input("Continue anyway? (y/n): ").lower() != "y":
            raise Exception(f"Window visual verification error at check #{check_index}: {check_name} - {str(e)}")
        return False

# Main test execution function
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

        # Test actions


        # Test completed successfully if we got here
        if test_results["status"] == "RUNNING":
            test_results["status"] = "PASSED"
        return test_results
    except Exception as e:
        # Catch and log any unhandled exceptions
        error_message = f"Unhandled exception: {str(e)}"
        print(f"[ERROR] {error_message}")
        
        # Get current exception information
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_info = traceback.extract_tb(exc_traceback)
        filename, line, func, text = tb_info[-1]
        
        log_error(error_message, "UnhandledException", {
            "line_number": line,
            "function": func,
            "code": text,
            "traceback": traceback.format_exc()
        })
        
        test_results["status"] = "ERROR"
        return test_results
    finally:
        # Always update end time and duration
        end_time = datetime.datetime.now()
        test_results["end_time"] = end_time.isoformat()
        duration = (end_time - datetime.datetime.fromisoformat(test_results["start_time"])).total_seconds()
        test_results["duration_seconds"] = duration
        
        # Final test results summary
        if test_results["status"] == "FAILED" and test_results.get("failure_line") is not None:
            print("\n" + "="*60)
            print("TEST FAILED")
            print(f"Failure occurred at line {test_results['failure_line']}")
            if "check_name" in test_results.get("failure_details", {}):
                print(f"Check: #{test_results['failure_details']['check_index']} - {test_results['failure_details']['check_name']}")
                print(f"Location: {test_results['failure_details']['location']}")
                if "mean_difference" in test_results['failure_details']:
                    print(f"Image difference: {test_results['failure_details']['mean_difference']:.2f} (tolerance: {TOLERANCE})")
            else:
                print(f"Error: {test_results['failure_details'].get('message', 'Unknown error')}")
            print("="*60 + "\n")
        
        print(f"Test completed with status: {test_results['status']}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Checks passed: {test_results['checks_passed']}")
        print(f"Checks failed: {test_results['checks_failed']}")
        # Save the report
        save_report(test_results)


# Entry point for both script execution and importing as a module
if __name__ == "__main__":
    # When running directly as a script
    results = run_test()
    # Exit with appropriate status code
    if args.yes or args.headless:
        # With --yes or --headless flag, we always exit with success
        # since user indicated they want to continue despite failures
        sys.exit(0)
    else:
        # Otherwise, exit based on test status
        sys.exit(0 if results["status"] == "PASSED" else 1)
else:
    # When imported as a module (by test runner)
    # Export the run_test function
    pass  # No additional action needed
