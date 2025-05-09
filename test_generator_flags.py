import os
import sys
import time
import subprocess
from PIL import Image
from scriptgen.generator import generate_script

def create_test_actions_with_failing_check():
    """Create a list of test actions with an intentionally failing check"""
    actions = []
    
    # Add normal actions
    actions.append({
        'type': 'mouse',
        'event': 'down',
        'x': 100,
        'y': 100,
        'timestamp': 1.0
    })
    
    actions.append({
        'type': 'mouse',
        'event': 'up',
        'x': 100,
        'y': 100,
        'timestamp': 1.2
    })
    
    # Create a check action with a custom image that won't match the screen
    # Create a solid red image that won't match any real screenshot
    check_dir = os.path.join(os.path.dirname(__file__), 'screenshots')
    os.makedirs(check_dir, exist_ok=True)
    
    red_img = Image.new('RGB', (100, 100), color='red')
    check_img_path = os.path.join(check_dir, 'red_check.png')
    red_img.save(check_img_path)
    
    # Add check action with the reference to our red image
    actions.append({
        'type': 'check',
        'check_type': 'image',
        'timestamp': 2.0,
        'check_name': 'Red Check',
        'image': red_img  # This will be saved by the generator
    })
    
    return actions

def generate_failing_test():
    """Generate a test script that will have a failing check"""
    try:
        # Create test actions with failing check
        actions = create_test_actions_with_failing_check()
        
        # Generate script
        output_path = "test_with_failing_check.py"
        script = generate_script(
            actions,
            tolerance_level="Medium",
            output_path=output_path
        )
        
        # Write script to file
        with open(output_path, 'w') as f:
            f.write(script)
        
        print(f"Script with failing check generated and saved to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error generating script: {e}")
        import traceback
        traceback.print_exc()
        return None

def run_test_with_flags(script_path, flags):
    """Run the generated script with specified flags"""
    cmd = [sys.executable, script_path] + flags
    print(f"\nRunning test with flags: {' '.join(flags)}")
    print("-" * 60)
    
    try:
        # Use subprocess.run for better error handling
        result = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True,
            timeout=15  # 15 second timeout
        )
        
        exit_code = result.returncode
        stdout = result.stdout
        stderr = result.stderr
    except subprocess.TimeoutExpired as e:
        print("Test timed out after 15 seconds")
        exit_code = -1
        stdout = e.stdout if e.stdout else ""
        stderr = e.stderr if e.stderr else ""
    
    # Print stdout
    if stdout:
        print("STDOUT:")
        lines = stdout.split('\n')
        for i, line in enumerate(lines[:30]):
            print(line)
        
        if len(lines) > 30:
            print(f"... (showing 30/{len(lines)} lines)")
    
    # Print stderr
    if stderr:
        print("\nSTDERR:")
        lines = stderr.split('\n')
        for i, line in enumerate(lines[:10]):
            print(line)
        
        if len(lines) > 10:
            print(f"... (showing 10/{len(lines)} lines)")
    
    print("-" * 60)
    print(f"Exit code: {exit_code}")
    
    # For --yes and --headless flags, we expect success (exit code 0)
    # For --no flag, we expect failure (non-zero exit code)
    if "--no" in flags and not "--yes" in flags:
        # --no flag should make it fail on check failure
        expected_result = False
        actual_result = exit_code == 0
        print(f"Expected failure: {'PASS' if not actual_result else 'FAIL'}")
        return not actual_result
    elif "--yes" in flags and "--no" in flags:
        # Both flags should cause error at the beginning (exit code 2)
        expected_result = False
        actual_result = exit_code == 2
        print(f"Expected error code 2: {'PASS' if actual_result else 'FAIL'}")
        return actual_result
    else:
        # --yes or --headless should continue despite check failures
        expected_result = True
        actual_result = exit_code == 0
        print(f"Expected success: {'PASS' if actual_result else 'FAIL'}")
        return actual_result

def main():
    """Generate and test a script with failing check using different flags"""
    script_path = generate_failing_test()
    if not script_path:
        print("Failed to generate test script")
        return 1
    
    # Test with different flag combinations
    success = True
    
    # Compile check to make sure script is valid Python
    print("\nVerifying script compiles correctly...")
    compile_result = subprocess.run(
        [sys.executable, "-m", "py_compile", script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if compile_result.returncode != 0:
        print(f"Compilation failed: {compile_result.stderr}")
        return 1
    else:
        print("Script compiles successfully")
    
    # Test with --yes flag (should continue despite failure)
    yes_result = run_test_with_flags(script_path, ["--yes"])
    if not yes_result:
        print("✘ Test with --yes flag should continue despite failures")
        success = False
    else:
        print("✓ Test with --yes flag passed correctly")
    
    # Test with --no flag (should fail on check failure)
    no_result = run_test_with_flags(script_path, ["--no"])
    if not no_result:
        print("✘ Test with --no flag should fail immediately")
        success = False
    else:
        print("✓ Test with --no flag passed correctly")
    
    # Test with --headless flag (should continue despite failure)
    headless_result = run_test_with_flags(script_path, ["--headless"])
    if not headless_result:
        print("✘ Test with --headless flag should continue despite failures")
        success = False
    else:
        print("✓ Test with --headless flag passed correctly")
        
    # Test with both flags (should error with code 2)
    conflict_result = run_test_with_flags(script_path, ["--yes", "--no"])
    if not conflict_result:
        print("✘ Test with conflicting flags should exit with code 2")
        success = False
    else:
        print("✓ Test with conflicting flags passed correctly")
    
    if success:
        print("\n✓ All flag tests PASSED!")
        return 0
    else:
        print("\n✘ Some flag tests FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 