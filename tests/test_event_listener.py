import unittest
from recorder.event_listener import EventListener
import time

class TestEventListener(unittest.TestCase):
    def setUp(self):
        self.listener = EventListener()
        self.listener.start_time = time.time()
        self.listener.recording = True

    def test_mouse_click_event(self):
        self.listener._on_click(100, 200, 'Button.left', True)
        events = self.listener.get_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['type'], 'mouse')
        self.assertEqual(events[0]['event'], 'down')
        self.assertEqual(events[0]['x'], 100)
        self.assertEqual(events[0]['y'], 200)

    def test_keyboard_event(self):
        self.listener._on_press('a')
        events = self.listener.get_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['type'], 'keyboard')
        self.assertEqual(events[0]['event'], 'down')
        self.assertEqual(events[0]['key'], 'a')

    def test_clear_events(self):
        self.listener._on_click(100, 200, 'Button.left', True)
        self.listener.clear()
        self.assertEqual(len(self.listener.get_events()), 0)

    def test_pause_resume(self):
        self.listener.pause()
        self.assertFalse(self.listener.recording)
        self.listener.resume()
        self.assertTrue(self.listener.recording)

if __name__ == '__main__':
    unittest.main() 