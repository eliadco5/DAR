import unittest
from recorder.session import SessionManager

class TestSessionManager(unittest.TestCase):
    def setUp(self):
        self.manager = SessionManager()

    def test_start_sets_state(self):
        self.manager.start()
        self.assertEqual(self.manager.state, 'recording')

    def test_pause_sets_state(self):
        self.manager.start()
        self.manager.pause()
        self.assertEqual(self.manager.state, 'paused')

    def test_resume_sets_state(self):
        self.manager.start()
        self.manager.pause()
        self.manager.resume()
        self.assertEqual(self.manager.state, 'recording')

    def test_stop_sets_state(self):
        self.manager.start()
        self.manager.stop()
        self.assertEqual(self.manager.state, 'stopped')

    def test_clear_resets_events(self):
        self.manager.start()
        self.manager.listener._on_click(10, 20, 'Button.left', True)
        self.manager.clear()
        self.assertEqual(len(self.manager.get_events()), 0)
        self.assertEqual(self.manager.state, 'stopped')

if __name__ == '__main__':
    unittest.main() 