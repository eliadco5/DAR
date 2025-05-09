import unittest
from scriptgen.generator import generate_script

class TestScriptGenerator(unittest.TestCase):
    def test_generate_script(self):
        actions = [
            {'type': 'mouse', 'event': 'down', 'x': 100, 'y': 200, 'timestamp': 0.0},
            {'type': 'mouse', 'event': 'up', 'x': 100, 'y': 200, 'timestamp': 0.1},
            {'type': 'keyboard', 'event': 'down', 'key': 'a', 'timestamp': 0.2},
            {'type': 'keyboard', 'event': 'up', 'key': 'a', 'timestamp': 0.3},
        ]
        script = generate_script(actions)
        self.assertIn('pyautogui.mouseDown()', script)
        self.assertIn('pyautogui.mouseUp()', script)
        self.assertIn('pyautogui.keyDown', script)
        self.assertIn('pyautogui.keyUp', script)
        # All time differences are 0.1, so expect three time.sleep(0.100)
        self.assertEqual(script.count('time.sleep(0.100)'), 3)

if __name__ == '__main__':
    unittest.main() 