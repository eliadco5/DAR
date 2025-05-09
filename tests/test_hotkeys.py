import unittest
from utils.hotkeys import HotkeyManager
from pynput.keyboard import Key

class TestHotkeyManager(unittest.TestCase):
    def setUp(self):
        self.pause_called = False
        self.stop_called = False
        self.manager = HotkeyManager(on_pause=self.on_pause, on_stop=self.on_stop)

    def on_pause(self):
        self.pause_called = True

    def on_stop(self):
        self.stop_called = True

    def test_f8_triggers_pause(self):
        self.manager._on_press(Key.f8)
        self.assertTrue(self.pause_called)

    def test_f10_triggers_stop(self):
        self.manager._on_press(Key.f10)
        self.assertTrue(self.stop_called)

if __name__ == '__main__':
    unittest.main() 