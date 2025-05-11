import sys
from scriptgen.generator import generate_script

# Create a test action list with various actions
def create_test_action_list():
    actions = []
    
    # Add mouse actions
    actions.append({
        'type': 'mouse',
        'event': 'click',
        'x': 100,
        'y': 200,
        'timestamp': 1.0
    })
    
    actions.append({
        'type': 'mouse',
        'event': 'move',
        'x': 300,
        'y': 400,
        'timestamp': 2.0
    })
    
    # Add keyboard actions
    actions.append({
        'type': 'keyboard',
        'event': 'down',
        'key': 'ctrl',
        'timestamp': 3.0
    })
    
    actions.append({
        'type': 'keyboard',
        'event': 'down',
        'key': 'a',
        'timestamp': 3.5
    })
    
    actions.append({
        'type': 'keyboard',
        'event': 'up',
        'key': 'a',
        'timestamp': 4.0
    })
    
    actions.append({
        'type': 'keyboard',
        'event': 'up',
        'key': 'ctrl',
        'timestamp': 4.5
    })
    
    # Add visual checks
    actions.append({
        'type': 'check',
        'check_type': 'image',
        'x': 500,
        'y': 600,
        'width': 100,
        'height': 100,
        'timestamp': 5.0
    })
    
    return actions

def main():
    # Create test action list
    action_list = create_test_action_list()
    
    try:
        # Generate script with different tolerance settings
        script = generate_script(action_list, tolerance_level="Medium")
        
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