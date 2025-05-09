# Hooks for mouse/keyboard events
from pynput import mouse, keyboard
import time
from recorder.screenshot import ScreenshotUtil
import ast

CONTROL_CHAR_TO_KEY = {
    chr(i): c for i, c in zip(range(1, 27), 'abcdefghijklmnopqrstuvwxyz')
}
MODIFIER_KEYS = {
    'Key.ctrl': 'ctrl', 'Key.ctrl_l': 'ctrl', 'Key.ctrl_r': 'ctrl',
    'Key.alt': 'alt', 'Key.alt_l': 'alt', 'Key.alt_r': 'alt',
    'Key.shift': 'shift', 'Key.shift_l': 'shift', 'Key.shift_r': 'shift',
}

def normalize_key(key):
    # Modifier keys
    if key in MODIFIER_KEYS:
        return MODIFIER_KEYS[key]
    # Key like 'a', 'b', etc.
    if len(key) == 1 and key.isprintable():
        return key
    # Control character (e.g., '\x03')
    try:
        k = ast.literal_eval(key) if (key.startswith("'") or key.startswith('"')) else key
        if isinstance(k, str) and len(k) == 1 and ord(k) < 32:
            mapped = CONTROL_CHAR_TO_KEY.get(k)
            if mapped:
                return mapped
            else:
                return ''
        if isinstance(k, str) and k.isprintable():
            return k
        return k
    except Exception:
        return key.strip("'\"")

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
        key_str = str(key)
        norm_key = normalize_key(key_str)
        self.events.append({
            'type': 'keyboard',
            'event': 'down',
            'key': norm_key,
            'timestamp': timestamp
        })

    def _on_release(self, key):
        if not self.recording:
            return
        timestamp = time.time() - self.start_time
        key_str = str(key)
        norm_key = normalize_key(key_str)
        self.events.append({
            'type': 'keyboard',
            'event': 'up',
            'key': norm_key,
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
        """
        Pause recording but keep the listeners active.
        This allows for quick resuming without creating new listeners.
        """
        if self.recording:
            print("DEBUG: Pausing event recording (listeners remain active)")
            self.recording = False

    def resume(self):
        if not self.recording:
            # Check if listeners are not running and restart them if needed
            if self.mouse_listener is None or not self.mouse_listener.is_alive():
                self.mouse_listener = mouse.Listener(
                    on_click=self._on_click,
                    on_move=self._on_move,
                    on_scroll=self._on_scroll
                )
                self.mouse_listener.start()
                
            if self.keyboard_listener is None or not self.keyboard_listener.is_alive():
                self.keyboard_listener = keyboard.Listener(
                    on_press=self._on_press,
                    on_release=self._on_release
                )
                self.keyboard_listener.start()
                
            # Resume recording
            self.recording = True
            if self.events:
                # Calculate start time based on the last event's timestamp
                self.start_time = time.time() - self.events[-1]['timestamp']
            else:
                # No previous events, just start fresh
                self.start_time = time.time()
            
            print(f"DEBUG: Event listener resumed. Listeners active: Mouse={self.mouse_listener.is_alive() if self.mouse_listener else False}, Keyboard={self.keyboard_listener.is_alive() if self.keyboard_listener else False}")

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