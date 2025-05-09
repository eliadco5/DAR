# Screenshot/image recognition utilities
import pyautogui
from PIL import Image

class ScreenshotUtil:
    def __init__(self):
        # TODO: Initialize screenshot utilities
        pass

    @staticmethod
    def capture_fullscreen():
        # Capture the entire screen and return as PIL Image
        screenshot = pyautogui.screenshot()
        return screenshot

    @staticmethod
    def capture_region(x, y, width=100, height=100):
        # Capture a region around (x, y) and return as PIL Image
        left = max(x - width // 2, 0)
        top = max(y - height // 2, 0)
        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        return screenshot 