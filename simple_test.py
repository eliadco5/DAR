import os
import sys
from scriptgen.generator import generate_script

# Create a dictionary-based list of actions similar to what the application uses
def create_test_actions():
    actions = []
    
    # Add mouse actions
    actions.append({
        'type': 'mouse',
        'event': 'down',
        'x': 100,
        'y': 200,
        'timestamp': 1.0
    })
    
    actions.append({
        'type': 'mouse',
        'event': 'up',
        'x': 100,
        'y': 200,
        'timestamp': 1.1
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
    
    # Create a check action
    actions.append({
        'type': 'check',
        'check_type': 'image',
        'x': 300,
        'y': 400,
        'width': 100,
        'height': 100,
        'timestamp': 3.0
    })
    
    return actions

def main():
    # Create test actions
    actions = create_test_actions()
    
    try:
        # Generate script with tolerance settings
        script = generate_script(actions, tolerance_level="Medium")
        
        # Save to file
        with open("test_generated_script.py", "w") as f:
            f.write(script)
        
        print("Script successfully generated and saved to test_generated_script.py")
        return 0
    except Exception as e:
        print(f"Error generating script: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 