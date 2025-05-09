import sys
import time
import threading
from PyQt6.QtWidgets import QApplication, QDialog, QLineEdit
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QKeyEvent
from gui.main_window import MainWindow
from pynput import keyboard

class HotkeySimulator:
    """Class to simulate hotkey presses using pynput in a separate thread"""
    
    def __init__(self):
        self.controller = keyboard.Controller()
        self.running = False
        self.thread = None
    
    def press_f6(self):
        """Simulate F6 key press and release"""
        self.controller.press(keyboard.Key.f6)
        time.sleep(0.1)
        self.controller.release(keyboard.Key.f6)
    
    def press_f7(self):
        """Simulate F7 key press and release"""
        self.controller.press(keyboard.Key.f7)
        time.sleep(0.1)
        self.controller.release(keyboard.Key.f7)
        
    def press_f8(self):
        """Simulate F8 key press and release (pause)"""
        self.controller.press(keyboard.Key.f8)
        time.sleep(0.1)
        self.controller.release(keyboard.Key.f8)
    
    def press_f9(self):
        """Simulate F9 key press and release (resume)"""
        self.controller.press(keyboard.Key.f9)
        time.sleep(0.1)
        self.controller.release(keyboard.Key.f9)
    
    def press_f10(self):
        """Simulate F10 key press and release (stop)"""
        self.controller.press(keyboard.Key.f10)
        time.sleep(0.1)
        self.controller.release(keyboard.Key.f10)
    
    def press_enter(self):
        """Simulate Enter key press"""
        self.controller.press(keyboard.Key.enter)
        time.sleep(0.1)
        self.controller.release(keyboard.Key.enter)
    
    def type_text(self, text):
        """Type the given text"""
        self.controller.type(text)
    
    def _run_scheduled_action(self, delay, action, *args):
        """Run a scheduled action after a delay"""
        time.sleep(delay)
        if self.running:
            if callable(action):
                action(*args)
    
    def schedule(self, delay, action, *args):
        """Schedule an action to run after a delay"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(
                target=self._run_scheduled_action,
                args=(delay, action) + args,
                daemon=True
            )
            self.thread.start()
    
    def stop(self):
        """Stop the simulator"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(1.0)
            self.thread = None

def focus_dialog_and_type(simulator, text):
    """Focus on the dialog and type text"""
    # Give the dialog time to appear and get focus
    time.sleep(0.5)
    
    # Type the text in the dialog
    simulator.type_text(text)
    time.sleep(0.2)
    
    # Press Enter to close the dialog
    simulator.press_enter()

def test_functionality_direct():
    """Test the check and comment functionality directly via method calls"""
    # Create the application
    app = QApplication(sys.argv)
    
    # Create main window
    print("Starting direct functionality test...")
    window = MainWindow()
    window.show()
    
    # Give UI time to initialize
    time.sleep(1)
    
    # Start recording to enable functionality
    print("Starting recording session...")
    window.start_recording()
    time.sleep(0.5)
    
    # Test check functionality directly by calling the method
    print("\nTesting check functionality directly...")
    
    # This will be called by the _execute_add_check method which simulates a user entering "TestDirectCheck"
    original_input_dialog = QDialog.exec
    
    def mock_dialog_exec(self):
        if "Name Your Visual Check" in self.windowTitle():
            # Find the line edit and set its text
            for child in self.findChildren(QLineEdit):
                child.setText("TestDirectCheck")
            return QDialog.DialogCode.Accepted
        else:
            # For other dialogs, use the original implementation
            return original_input_dialog(self)
    
    # Mock the dialog exec method
    QDialog.exec = mock_dialog_exec
    
    # Call the add check method directly
    window.add_check_action()
    
    # Give time for the check to be added
    time.sleep(2)
    
    # Test comment functionality directly
    print("\nTesting comment functionality directly...")
    
    def mock_comment_dialog_exec(self):
        if "Enter Your Comment" in self.windowTitle():
            # Find the line edit and set its text
            for child in self.findChildren(QLineEdit):
                child.setText("TestDirectComment")
            return QDialog.DialogCode.Accepted
        else:
            # For other dialogs, use the original implementation
            return original_input_dialog(self)
    
    # Mock the dialog exec method
    QDialog.exec = mock_comment_dialog_exec
    
    # Call the add comment method directly
    window.add_comment_action()
    
    # Give time for the comment to be added
    time.sleep(2)
    
    # Restore original method
    QDialog.exec = original_input_dialog
    
    # Verify check was added
    action_list = window.action_list
    check_found = False
    for i in range(action_list.count()):
        item = action_list.item(i)
        if "Check: 'TestDirectCheck'" in item.text():
            check_found = True
            print("✓ Found check with correct name: TestDirectCheck")
            break
    
    if not check_found:
        print("✗ Check not found in action list")
    
    # Verify comment was added
    comment_found = False
    for i in range(action_list.count()):
        item = action_list.item(i)
        if "Comment: 'TestDirectComment'" in item.text():
            comment_found = True
            print("✓ Found comment with correct text: TestDirectComment")
            break
    
    if not comment_found:
        print("✗ Comment not found in action list")
    
    # Generate script to check if comments and checks appear properly
    print("\nGenerating test script...")
    window.export_script()
    
    # Stop recording and close the window
    window.stop_recording()
    window.close()
    
    print("\nFunctionality test results:")
    if check_found and comment_found:
        print("✓ All functionality tests passed!")
        print("  - Check feature works correctly")
        print("  - Comment feature works correctly")
        return 0
    else:
        print("✗ Some functionality tests failed!")
        if not check_found:
            print("  - Check feature not working properly")
        if not comment_found:
            print("  - Comment feature not working properly")
        return 1

if __name__ == "__main__":
    sys.exit(test_functionality_direct()) 