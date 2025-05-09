import unittest
import tkinter as tk
from gui.main_window import MainWindow

class TestMainWindow(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = MainWindow(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_buttons_exist(self):
        # Check if Start, Stop, and Pause buttons exist
        self.assertTrue(hasattr(self.app, 'start_button'))
        self.assertTrue(hasattr(self.app, 'stop_button'))
        self.assertTrue(hasattr(self.app, 'pause_button'))

if __name__ == '__main__':
    unittest.main() 