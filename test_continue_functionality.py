"""
Test script to verify the "Continue" functionality in playback.
This script creates a series of checks that are designed to fail,
and then uses a simulated process to verify that the right actions are
executed in the right order when "Continue" is clicked.
"""

import os
import sys
import unittest
import time
from PIL import Image, ImageDraw, ImageChops
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest

# Add parent directory to path to allow imports from project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.main_window import MainWindow
from playback.player import play_actions

class TestContinueFunctionality(unittest.TestCase):
    """Test the Continue functionality in the playback system."""
    
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
    
    def tearDown(self):
        """Clean up after each test."""
        self.window.close()
        self.window.showMinimized = self.original_showMinimized
        # Ensure any popups are closed
        for widget in QApplication.topLevelWidgets():
            if widget != self.window and widget.isVisible():
                widget.close()
    
    def create_test_actions(self, num_checks=3):
        """Create a series of test actions with visual checks that are designed to fail."""
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
                'check_name': f'Check #{i+1}',
                'force_fail': True  # Force this check to fail during testing
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
    
    def test_continue_playback(self):
        """Test that playback continues from the correct point after clicking Continue."""
        # Create test actions with 3 checks that will fail
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
        
        # Start the playback
        QTimer.singleShot(100, self.window.preview_actions)
        
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
    
    def test_direct_play_actions_continuation(self):
        """Test the play_actions function directly to verify it properly handles continuation."""
        # Create test actions with 2 checks
        actions = self.create_test_actions(num_checks=2)
        
        # Log of processed actions
        processed_indices = []
        
        # Function to record processed indices
        def record_action(i):
            processed_indices.append(i)
            print(f"Processed action at index {i}")
        
        # First test: Starting from beginning
        start_index = 0
        print(f"\nTesting playback starting from index {start_index}")
        
        # We'll stop at the first check failure (actions[1])
        mock_callback = lambda img1, img2: None  # Mock callback
        result, fail_info, last_index = play_actions(
            actions[start_index:], 
            tolerance=7,
            fail_callback=mock_callback,
            start_index=0
        )
        
        # Verify we stopped at the correct point (first check)
        self.assertFalse(result, "Playback should have failed")
        self.assertEqual(last_index, 1, f"Expected to stop at index 1, got {last_index}")
        
        # Now test continuing from after the failure
        actual_last_index = start_index + last_index
        start_index = actual_last_index + 1
        print(f"\nTesting continuation from index {start_index}")
        
        result, fail_info, last_index = play_actions(
            actions[start_index:], 
            tolerance=7,
            fail_callback=mock_callback,
            start_index=0
        )
        
        # Verify we stopped at the next check
        self.assertFalse(result, "Playback should have failed")
        self.assertEqual(last_index, 1, f"Expected to stop at index 1, got {last_index}")
        
        # Final continuation (should reach the end)
        actual_last_index = start_index + last_index
        start_index = actual_last_index + 1
        print(f"\nTesting final continuation from index {start_index}")
        
        result, fail_info, last_index = play_actions(
            actions[start_index:], 
            tolerance=7,
            fail_callback=mock_callback,
            start_index=0
        )
        
        # Verify we completed successfully
        self.assertTrue(result, "Final playback should have succeeded")

if __name__ == '__main__':
    unittest.main() 