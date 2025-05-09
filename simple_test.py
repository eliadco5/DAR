import os
import sys
import time
from scriptgen.generator import generate_script

def create_test_actions():
    """Create a simple list of test actions"""
    actions = []
    
    # Add mouse actions
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
    
    # Add keyboard actions
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
    
    # Add check action
    actions.append({
        'type': 'check',
        'check_type': 'image',
        'timestamp': 3.0,
        'check_name': 'Test Check'
    })
    
    return actions

def main():
    """Generate a test script using our updated generator"""
    try:
        # Create test actions
        actions = create_test_actions()
        
        # Generate script
        output_path = "test_generated_script.py"
        script = generate_script(
            actions,
            tolerance_level="Medium",
            output_path=output_path
        )
        
        # Write script to file
        with open(output_path, 'w') as f:
            f.write(script)
        
        print(f"Script generated and saved to {output_path}")
    except Exception as e:
        print(f"Error generating script: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 