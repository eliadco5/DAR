import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from gui.main_window import MainWindow

def test_comment_ui_representation():
    """
    Test that comments are properly displayed in the UI with the correct styling.
    This test:
    1. Opens the UI
    2. Simulates adding several comments
    3. Verifies they appear in the action list with correct styling
    """
    # Create the application
    app = QApplication(sys.argv)
    
    # Create main window
    print("Starting UI test for comments...")
    window = MainWindow()
    window.show()
    
    # Give UI time to initialize
    time.sleep(1)
    
    # Start recording to enable comments
    print("Starting recording session...")
    window.start_recording()
    time.sleep(0.5)
    
    # Add test comments
    print("Adding test comments...")
    test_comments = [
        "This is a test comment",
        "This is another test comment with more text",
        "A third comment for verification"
    ]
    
    for i, comment_text in enumerate(test_comments):
        # Simulate adding a comment through the internal function
        comment_action = {
            'type': 'comment',
            'comment': comment_text,
            'timestamp': time.time() - (window.session_manager.listener.start_time or time.time()),
            'region': None
        }
        
        # Add the comment to the action list
        actions = window.action_editor.get_actions()
        actions.append(comment_action)
        window.action_editor.set_actions(actions)
        window.session_manager.listener.events = window.action_editor.get_actions()
        
        # Update UI
        window.update_action_list()
        time.sleep(0.2)
        
        print(f"Added comment {i+1}: {comment_text}")
    
    # Verify the comments appear in the action list
    print("\nVerifying comments in action list...")
    action_list = window.action_list
    
    # Check number of items in the list
    list_count = action_list.count()
    print(f"Items in action list: {list_count}")
    
    # Check each item in the list
    comment_count = 0
    for i in range(list_count):
        item = action_list.item(i)
        text = item.text()
        if "Comment:" in text:
            comment_count += 1
            comment_index = comment_count - 1
            if comment_index < len(test_comments):
                expected_text = test_comments[comment_index]
                if expected_text in text:
                    print(f"✓ Found comment {comment_count}: '{expected_text}'")
                else:
                    print(f"✗ Comment {comment_count} text mismatch: '{text}'")
            
            # Check for styling - comments should have a custom background and text color
            if window.is_dark:
                # In dark mode, should have green foreground
                if item.foreground().color().name() != "#A3BE8C":  # Light green in dark mode
                    print(f"✗ Comment {comment_count} has wrong text color: {item.foreground().color().name()}")
                else:
                    print(f"✓ Comment {comment_count} has correct text color")
            else:
                # In light mode, should have dark green foreground
                if item.foreground().color().name() != "#38761D":  # Dark green in light mode
                    print(f"✗ Comment {comment_count} has wrong text color: {item.foreground().color().name()}")
                else:
                    print(f"✓ Comment {comment_count} has correct text color")
                    
            # Check font weight - should be bold
            if not item.font().bold():
                print(f"✗ Comment {comment_count} is not bold")
            else:
                print(f"✓ Comment {comment_count} is bold")
    
    print(f"\nFound {comment_count} comments out of {len(test_comments)} expected")
    if comment_count == len(test_comments):
        print("All comments correctly displayed in UI")
    else:
        print("Some comments are missing from the UI")
    
    # Generate script to check comments appear properly in scripts
    print("\nGenerating test script with comments...")
    window.export_script()
    
    # Wait before closing
    time.sleep(2)
    
    # Stop recording and close the window
    window.stop_recording()
    window.close()
    
    print("UI comment test completed")
    return 0

if __name__ == "__main__":
    sys.exit(test_comment_ui_representation()) 