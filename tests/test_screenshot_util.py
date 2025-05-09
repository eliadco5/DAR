import unittest
from recorder.screenshot import ScreenshotUtil
from PIL import Image

class TestScreenshotUtil(unittest.TestCase):
    def test_capture_fullscreen(self):
        img = ScreenshotUtil.capture_fullscreen()
        self.assertIsInstance(img, Image.Image)
        # Should have non-zero size
        self.assertGreater(img.width, 0)
        self.assertGreater(img.height, 0)

    def test_capture_region(self):
        img = ScreenshotUtil.capture_region(100, 100, width=50, height=50)
        self.assertIsInstance(img, Image.Image)
        self.assertEqual(img.width, 50)
        self.assertEqual(img.height, 50)

if __name__ == '__main__':
    unittest.main() 