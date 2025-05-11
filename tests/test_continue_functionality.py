"""
Test script to verify the "Continue" functionality in playback.
This test ensures that when a check fails during playback, selecting 'Continue'
correctly resumes the test from the next action rather than restarting.
"""

import os
import sys
import unittest
import time
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtTest import QTest

# Add parent directory to path to allow imports from project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.main_window import MainWindow

class TestContinueFunctionality(unittest.TestCase):
    """Test the Continue functionality during playback."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the application environment once for all tests."""
        cls.app = QApplication([])
    
    def setUp(self):
        """Set up each individual test."""
        self.window = MainWindow()
        self.original_showMinimized = self.window.showMinimized
        self.window.showMinimized = lambda: None  # Disable minimize during tests
        self.continue_clicks = 0
        self.expected_continuations = 0
        
        # Prevent message boxes from showing
        self.original_question = QMessageBox.question
        QMessageBox.question = lambda *args, **kwargs: QMessageBox.StandardButton.Yes
    
    def tearDown(self):
        """Clean up after each test."""
        self.window.close()
        self.window.showMinimized = self.original_showMinimized
        QMessageBox.question = self.original_question
        
        # Ensure any popups are closed
        for widget in QApplication.topLevelWidgets():
            if widget != self.window and widget.isVisible():
                widget.close()
    
    def create_test_actions(self):
        """Create a series of actions with visual checks designed to fail."""
        actions = []
        
        # First mouse movement
        actions.append({
            'type': 'mouse',
            'event': 'move',
            'x': 100,
            'y': 100,
            'timestamp': 0.1
        })
        
        # First check - will fail
        actions.append({
            'type': 'check',
            'check_type': 'image',
            'image': None,  # This will force a failure
            'timestamp': 0.5,
            'check_name': 'First Check'
        })
        
        # Second mouse movement - should continue to this after clicking "Continue"
        actions.append({
            'type': 'mouse',
            'event': 'move',
            'x': 200,
            'y': 200,
            'timestamp': 1.0
        })
        
        # Second check - will fail again
        actions.append({
            'type': 'check',
            'check_type': 'image',
            'image': None,  # This will force a failure
            'timestamp': 1.5,
            'check_name': 'Second Check'
        })
        
        # Third mouse movement - should continue to this after clicking "Continue" again
        actions.append({
            'type': 'mouse',
            'event': 'move',
            'x': 300,
            'y': 300,
            'timestamp': 2.0
        })
        
        return actions
    
    def simulate_continue_click(self):
        """Simulate a click on the Continue button."""
        self.continue_clicks += 1
        print(f"Simulating continue click #{self.continue_clicks}")
        # Directly call the continue method
        self.window.continue_after_error()
    
    def test_continue_playback(self):
        """Test that playback continues from the next action after clicking Continue."""
        # Set up test actions
        actions = self.create_test_actions()
        self.window.action_editor.set_actions(actions)
        self.expected_continuations = 2
        
        # Setup a timer to click continue whenever the error panel is visible
        def handle_errors():
            if self.continue_clicks < self.expected_continuations and self.window.error_panel.isVisible():
                QTimer.singleShot(100, self.simulate_continue_click)
        
        # Setup a periodic timer to check for errors
        error_check_timer = QTimer()
        error_check_timer.timeout.connect(handle_errors)
        error_check_timer.start(500)  # Check every 500ms
        
        # Start playback
        QTimer.singleShot(100, self.window.run_playback)
        
        # Wait for playback to complete (maximum 10 seconds)
        timeout = time.time() + 10
        while time.time() < timeout:
            QApplication.processEvents()
            if not self.window.playback_thread or not self.window.playback_thread.is_alive():
                break
            time.sleep(0.1)
        
        # Stop the error checking timer
        error_check_timer.stop()
        
        # Verify results
        self.assertEqual(self.continue_clicks, self.expected_continuations, 
                         f"Expected {self.expected_continuations} continue clicks, got {self.continue_clicks}")
        
        # Ensure playback completed
        self.assertTrue(not self.window.playback_thread or not self.window.playback_thread.is_alive(),
                       "Playback thread should have completed")
        
        # If we got to the end, that means continuation worked
        # (otherwise it would be stuck in the error panel)
    
    def test_direct_play_actions_continuation(self):
        """Test that direct play_actions continues from the next action after clicking Continue."""
        # Set up test actions
        actions = self.create_test_actions()
        self.window.action_editor.set_actions(actions)
        self.expected_continuations = 2
        
        # Setup a timer to click continue whenever the error panel is visible
        def handle_errors():
            if self.continue_clicks < self.expected_continuations and self.window.error_panel.isVisible():
                QTimer.singleShot(100, self.simulate_continue_click)
        
        # Setup a periodic timer to check for errors
        error_check_timer = QTimer()
        error_check_timer.timeout.connect(handle_errors)
        error_check_timer.start(500)  # Check every 500ms
        
        # Start direct play_actions
        QTimer.singleShot(100, lambda: self.window.play_actions(actions))
        
        # Wait for playback to complete (maximum 10 seconds)
        timeout = time.time() + 10
        while time.time() < timeout:
            QApplication.processEvents()
            if not self.window.playback_thread or not self.window.playback_thread.is_alive():
                break
            time.sleep(0.1)
        
        # Stop the error checking timer
        error_check_timer.stop()
        
        # Verify results
        self.assertEqual(self.continue_clicks, self.expected_continuations, 
                         f"Expected {self.expected_continuations} continue clicks, got {self.continue_clicks}")
        
        # Ensure playback completed
        self.assertTrue(not self.window.playback_thread or not self.window.playback_thread.is_alive(),
                       "Playback thread should have completed")

if __name__ == '__main__':
    unittest.main() 