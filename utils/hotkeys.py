# Global hotkey registration
from pynput import keyboard
import threading
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("HotkeyManager")

class HotkeyManager:
    def __init__(self, on_pause=None, on_stop=None, on_check=None):
        self.on_pause = on_pause
        self.on_stop = on_stop
        self.on_check = on_check
        self.listener = None
        self._thread = None

    def _on_press(self, key):
        try:
            if key == keyboard.Key.f8 and self.on_pause:
                logger.info("F8 hotkey detected, triggering pause")
                self.on_pause()
            elif key == keyboard.Key.f10 and self.on_stop:
                logger.info("F10 hotkey detected, triggering stop")
                self.on_stop()
            elif key == keyboard.Key.f7 and self.on_check:
                logger.info("F7 hotkey detected, triggering check")
                self.on_check()
        except Exception as e:
            # Log the exception instead of silently ignoring it
            logger.error(f"Error in hotkey handler: {e}")
            logger.error(traceback.format_exc())

    def start(self):
        if self.listener is None:
            self.listener = keyboard.Listener(on_press=self._on_press)
            self._thread = threading.Thread(target=self.listener.start, daemon=True)
            self._thread.start()
            logger.info("Hotkey manager started")

    def stop(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
            self._thread = None
            logger.info("Hotkey manager stopped")

    def __del__(self):
        self.stop() 