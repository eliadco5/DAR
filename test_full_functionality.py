import os
import sys
import time
import argparse
from PIL import Image, ImageDraw
from scriptgen.generator import generate_script

def create_comprehensive_test_actions():
    """Create a comprehensive list of test actions that includes all features"""
    actions = []
    
    # Start with a comment
    actions.append({
        'type': 'comment',
        'comment': 'Beginning test sequence',
        'timestamp': 0.5
    })
    
    # Mouse movements and clicks
    actions.append({
        'type': 'mouse',
        'event': 'move',
        'x': 100,
        'y': 100,
        'timestamp': 1.0
    })
    
    actions.append({
        'type': 'mouse',
        'event': 'down',
        'x': 100,
        'y': 100,
        'timestamp': 1.2
    })
    
    actions.append({
        'type': 'mouse',
        'event': 'up',
        'x': 100,
        'y': 100,
        'timestamp': 1.3
    })
    
    # Add another comment
    actions.append({
        'type': 'comment',
        'comment': 'Testing keyboard interactions',
        'timestamp': 1.5
    })
    
    # Keyboard actions with modifiers
    actions.append({
        'type': 'keyboard',
        'event': 'down',
        'key': 'ctrl',
        'timestamp': 2.0
    })
    
    actions.append({
        'type': 'keyboard',
        'event': 'down',
        'key': 'a',
        'timestamp': 2.1
    })
    
    actions.append({
        'type': 'keyboard',
        'event': 'up',
        'key': 'a',
        'timestamp': 2.2
    })
    
    actions.append({
        'type': 'keyboard',
        'event': 'up',
        'key': 'ctrl',
        'timestamp': 2.3
    })
    
    # Text typing sequence
    actions.append({
        'type': 'keyboard',
        'event': 'down',
        'key': 'H',
        'timestamp': 3.0
    })
    
    actions.append({
        'type': 'keyboard',
        'event': 'up',
        'key': 'H',
        'timestamp': 3.05
    })
    
    actions.append({
        'type': 'keyboard',
        'event': 'down',
        'key': 'e',
        'timestamp': 3.1
    })
    
    actions.append({
        'type': 'keyboard',
        'event': 'up',
        'key': 'e',
        'timestamp': 3.15
    })
    
    actions.append({
        'type': 'keyboard',
        'event': 'down',
        'key': 'l',
        'timestamp': 3.2
    })
    
    actions.append({
        'type': 'keyboard',
        'event': 'up',
        'key': 'l',
        'timestamp': 3.25
    })
    
    actions.append({
        'type': 'keyboard',
        'event': 'down',
        'key': 'l',
        'timestamp': 3.3
    })
    
    actions.append({
        'type': 'keyboard',
        'event': 'up',
        'key': 'l',
        'timestamp': 3.35
    })
    
    actions.append({
        'type': 'keyboard',
        'event': 'down',
        'key': 'o',
        'timestamp': 3.4
    })
    
    actions.append({
        'type': 'keyboard',
        'event': 'up',
        'key': 'o',
        'timestamp': 3.45
    })
    
    # Add a visual check with custom name
    # Create a test image for the check
    img = Image.new('RGB', (200, 200), color='white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 180, 180], outline='black', width=2)
    draw.text((50, 90), "Test Image", fill='black')
    
    actions.append({
        'type': 'check',
        'check_type': 'image',
        'image': img,
        'timestamp': 4.0,
        'check_name': 'First Custom Check'
    })
    
    # Add another comment
    actions.append({
        'type': 'comment',
        'comment': 'Testing mouse drag operation',
        'timestamp': 4.5
    })
    
    # Mouse drag operation
    actions.append({
        'type': 'mouse',
        'event': 'down',
        'x': 200,
        'y': 200,
        'timestamp': 5.0
    })
    
    actions.append({
        'type': 'mouse',
        'event': 'move',
        'x': 250,
        'y': 250,
        'timestamp': 5.2
    })
    
    actions.append({
        'type': 'mouse',
        'event': 'move',
        'x': 300,
        'y': 300,
        'timestamp': 5.4
    })
    
    actions.append({
        'type': 'mouse',
        'event': 'up',
        'x': 300,
        'y': 300,
        'timestamp': 5.6
    })
    
    # Add another visual check with custom name
    img2 = Image.new('RGB', (300, 300), color='lightblue')
    draw = ImageDraw.Draw(img2)
    draw.ellipse([50, 50, 250, 250], outline='darkblue', width=3)
    draw.text((100, 140), "Second Test Image", fill='darkblue')
    
    actions.append({
        'type': 'check',
        'check_type': 'image',
        'image': img2,
        'timestamp': 6.0,
        'check_name': 'Second Custom Check'
    })
    
    # Final comment
    actions.append({
        'type': 'comment',
        'comment': 'Test sequence completed',
        'timestamp': 6.5
    })
    
    return actions

def main():
    """Generate a test script and validate the result"""
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description='Test recorder functionality and script generation')
        parser.add_argument('--output', type=str, default='comprehensive_test_script.py',
                            help='Output filename for the generated script')
        parser.add_argument('--tolerance', type=str, choices=['Low', 'Medium', 'High'], 
                            default='Medium', help='Tolerance level for visual checks')
        args = parser.parse_args()
        
        # Create test actions
        print("Creating comprehensive test actions...")
        actions = create_comprehensive_test_actions()
        
        # Generate script
        print(f"Generating script with {len(actions)} actions and {args.tolerance} tolerance...")
        script = generate_script(
            actions,
            tolerance_level=args.tolerance,
            output_path=args.output
        )
        
        # Write script to file
        with open(args.output, 'w') as f:
            f.write(script)
        
        print(f"Script generated and saved to {args.output}")
        
        # Validate the script content
        print("Validating script content...")
        with open(args.output, 'r') as f:
            script_content = f.read()
        
        # Check for expected features
        validation_checks = {
            "comments": "[COMMENT]" in script_content,
            "click_operations": "pyautogui.click" in script_content,
            "keyboard_operations": "pyautogui.press" in script_content or "pyautogui.write" in script_content,
            "visual_checks": "First Custom Check" in script_content and "Second Custom Check" in script_content,
            "mouse_drag": "pyautogui.mouseDown" in script_content and "pyautogui.mouseUp" in script_content,
            "screenshots_saved": os.path.exists(os.path.join(os.path.dirname(args.output), "screenshots")),
        }
        
        # Print validation results
        print("\nValidation Results:")
        for feature, result in validation_checks.items():
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status} - {feature.replace('_', ' ').title()}")
        
        # Overall test status
        if all(validation_checks.values()):
            print("\nAll validation checks passed! The script generator is working correctly.")
            return 0
        else:
            print("\nSome validation checks failed. Please check the script content.")
            return 1
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 