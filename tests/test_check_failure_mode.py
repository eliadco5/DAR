"""
Test script to verify the "Test Check Failure" functionality.
This test ensures that the test_check_failure method correctly
handles forced failures and properly continues when requested.
"""

import os
import sys
import unittest
import time
from PIL import Image, ImageDraw, ImageChops
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtTest import QTest

# Add parent directory to path to allow imports from project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.main_window import MainWindow

class TestCheckFailureMode(unittest.TestCase):
    """Test the Test Check Failure functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the application environment once for all tests."""
        cls.app = QApplication([])
    
    def setUp(self):
        """Set up each individual test."""
        self.window = MainWindow()
        # Disable minimize during tests
        self.original_showMinimized = self.window.showMinimized
        self.window.showMinimized = lambda: None
        # Track continue button clicks
        self.continue_clicks = 0
        # Track expected continuations
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
    
    def create_test_actions(self, num_checks=3):
        """Create a series of test actions with visual checks."""
        actions = []
        
        # Start with an initial mouse action
        actions.append({
            'type': 'mouse',
            'event': 'move',
            'x': 100,
            'y': 100,
            'timestamp': 0.1
        })
        
        # Create a series of checks with different images
        for i in range(num_checks):
            # Create a unique image for each check
            img = Image.new('RGB', (200, 200), color='white')
            draw = ImageDraw.Draw(img)
            draw.rectangle([20, 20, 180, 180], outline='black', width=2)
            draw.text((50, 90), f"Check #{i+1}", fill='black')
            
            # Add visual check
            actions.append({
                'type': 'check',
                'check_type': 'image',
                'image': img,
                'timestamp': 1.0 + i,
                'check_name': f'Check #{i+1}'
            })
            
            # Add action after each check to verify continuation
            actions.append({
                'type': 'mouse',
                'event': 'move',
                'x': 100 + (i+1)*50,
                'y': 100 + (i+1)*50,
                'timestamp': 1.5 + i
            })
        
        return actions
    
    def simulate_continue_click(self):
        """Simulate a click on the Continue button."""
        self.continue_clicks += 1
        print(f"Simulating continue click #{self.continue_clicks}")
        # Directly call the continue method
        self.window.continue_after_error()
    
    def simulate_stop_click(self):
        """Simulate a click on the Stop Test button."""
        print("Simulating stop click")
        # Directly call the stop method
        self.window.stop_after_error()
    
    def test_check_failure_mode_with_continue(self):
        """Test that the test check failure mode correctly handles continue clicks."""
        # Create test actions with 3 checks
        actions = self.create_test_actions(num_checks=3)
        self.window.action_editor.set_actions(actions)
        self.expected_continuations = 3
        
        # Setup a timer to click continue after each failure
        def handle_errors():
            if self.continue_clicks < self.expected_continuations and self.window.error_panel.isVisible():
                QTimer.singleShot(100, self.simulate_continue_click)
        
        # Setup a periodic timer to check for errors
        error_check_timer = QTimer()
        error_check_timer.timeout.connect(handle_errors)
        error_check_timer.start(500)  # Check every 500ms
        
        # Start the test check failure mode
        QTimer.singleShot(100, self.window.test_check_failure)
        
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
    
    def test_check_failure_mode_with_stop(self):
        """Test that the test check failure mode correctly handles stop clicks."""
        # Create test actions with 3 checks
        actions = self.create_test_actions(num_checks=3)
        self.window.action_editor.set_actions(actions)
        
        # Setup a timer to click stop after the first failure
        def handle_errors():
            if self.window.error_panel.isVisible():
                QTimer.singleShot(100, self.simulate_stop_click)
        
        # Setup a periodic timer to check for errors
        error_check_timer = QTimer()
        error_check_timer.timeout.connect(handle_errors)
        error_check_timer.start(500)  # Check every 500ms
        
        # Start the test check failure mode
        QTimer.singleShot(100, self.window.test_check_failure)
        
        # Wait for playback to complete (maximum 10 seconds)
        timeout = time.time() + 10
        while time.time() < timeout:
            QApplication.processEvents()
            if not self.window.playback_thread or not self.window.playback_thread.is_alive():
                break
            time.sleep(0.1)
        
        # Stop the error checking timer
        error_check_timer.stop()
        
        # Verify results - should have stopped after first failure
        self.assertEqual(self.continue_clicks, 0, "Should not have any continue clicks")
        
        # Ensure playback completed
        self.assertTrue(not self.window.playback_thread or not self.window.playback_thread.is_alive(),
                        "Playback thread should have completed")

if __name__ == '__main__':
    unittest.main() 