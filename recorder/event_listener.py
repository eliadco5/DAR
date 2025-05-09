# Hooks for mouse/keyboard events
from pynput import mouse, keyboard
import time
from recorder.screenshot import ScreenshotUtil

class EventListener:
    def __init__(self):
        self.events = []
        self.mouse_listener = None
        self.keyboard_listener = None
        self.recording = False
        self.start_time = None

    def _on_mouse_event(self, event_type, x, y, button=None):
        if not self.recording:
            return
        timestamp = time.time() - self.start_time
        event = {
            'type': 'mouse',
            'event': event_type,
            'x': x,
            'y': y,
            'button': str(button) if button else None,
            'timestamp': timestamp
        }
        # Capture screenshot only for mouse down events
        if event_type == 'down':
            event['screenshot'] = ScreenshotUtil.capture_region(x, y)
        self.events.append(event)

    def _on_click(self, x, y, button, pressed):
        event_type = 'down' if pressed else 'up'
        self._on_mouse_event(event_type, x, y, button)

    def _on_move(self, x, y):
        self._on_mouse_event('move', x, y)

    def _on_scroll(self, x, y, dx, dy):
        if not self.recording:
            return
        timestamp = time.time() - self.start_time
        self.events.append({
            'type': 'mouse',
            'event': 'scroll',
            'x': x,
            'y': y,
            'dx': dx,
            'dy': dy,
            'timestamp': timestamp
        })

    def _on_press(self, key):
        if not self.recording:
            return
        timestamp = time.time() - self.start_time
        self.events.append({
            'type': 'keyboard',
            'event': 'down',
            'key': str(key),
            'timestamp': timestamp
        })

    def _on_release(self, key):
        if not self.recording:
            return
        timestamp = time.time() - self.start_time
        self.events.append({
            'type': 'keyboard',
            'event': 'up',
            'key': str(key),
            'timestamp': timestamp
        })

    def start(self):
        if self.recording:
            return
        self.recording = True
        self.start_time = time.time()
        self.events = []
        self.mouse_listener = mouse.Listener(
            on_click=self._on_click,
            on_move=self._on_move,
            on_scroll=self._on_scroll
        )
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.mouse_listener.start()
        self.keyboard_listener.start()

    def pause(self):
        self.recording = False

    def resume(self):
        if not self.recording:
            self.recording = True
            self.start_time = time.time() - (self.events[-1]['timestamp'] if self.events else 0)

    def stop(self):
        self.recording = False
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None

    def clear(self):
        self.events = []

    def get_events(self):
        return self.events.copy() 