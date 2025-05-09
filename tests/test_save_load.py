import unittest
import os
from PIL import Image
from storage.save_load import save_actions, load_actions

class TestSaveLoad(unittest.TestCase):
    def setUp(self):
        # Create a simple red image for testing
        self.img = Image.new('RGB', (10, 10), color='red')
        self.actions = [
            {'type': 'mouse', 'event': 'down', 'x': 1, 'y': 2, 'screenshot': self.img},
            {'type': 'keyboard', 'event': 'down', 'key': 'a', 'screenshot': None}
        ]
        self.test_file = 'test_actions.json'

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_save_and_load_actions(self):
        save_actions(self.test_file, self.actions)
        loaded = load_actions(self.test_file)
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0]['type'], 'mouse')
        self.assertIsInstance(loaded[0]['screenshot'], Image.Image)
        self.assertEqual(loaded[1]['type'], 'keyboard')
        self.assertIsNone(loaded[1]['screenshot'])

if __name__ == '__main__':
    unittest.main() 