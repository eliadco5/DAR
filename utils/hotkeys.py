# Global hotkey registration
from pynput import keyboard
import threading

class HotkeyManager:
    def __init__(self, on_pause=None, on_stop=None):
        self.on_pause = on_pause
        self.on_stop = on_stop
        self.listener = None
        self._thread = None

    def _on_press(self, key):
        try:
            if key == keyboard.Key.f8 and self.on_pause:
                self.on_pause()
            elif key == keyboard.Key.f10 and self.on_stop:
                self.on_stop()
        except Exception:
            pass

    def start(self):
        if self.listener is None:
            self.listener = keyboard.Listener(on_press=self._on_press)
            self._thread = threading.Thread(target=self.listener.start, daemon=True)
            self._thread.start()

    def stop(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
            self._thread = None

    def __del__(self):
        self.stop() 