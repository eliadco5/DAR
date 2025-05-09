# Screenshot/image recognition utilities
import pyautogui
from PIL import Image
import ctypes
import platform

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

    @staticmethod
    def capture_active_window():
        """Capture the currently focused window and return as PIL Image"""
        if platform.system() == 'Windows':
            # Windows specific implementation
            try:
                # Get the handle of the active window
                hwnd = ctypes.windll.user32.GetForegroundWindow()
                
                # Get the window dimensions
                rect = ctypes.wintypes.RECT()
                ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
                
                # Calculate width and height
                width = rect.right - rect.left
                height = rect.bottom - rect.top
                
                # Capture the region
                screenshot = pyautogui.screenshot(region=(rect.left, rect.top, width, height))
                return screenshot
            except Exception as e:
                print(f"Error capturing active window: {e}")
                # Fallback to full screen
                return pyautogui.screenshot()
        else:
            # For non-Windows platforms, we need different implementations
            # For now, fallback to full screen
            return pyautogui.screenshot() 