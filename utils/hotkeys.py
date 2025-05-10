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
    def __init__(self, on_pause=None, on_stop=None, on_check=None, on_resume=None, on_comment=None, get_session_state=None):
        self.on_pause = on_pause
        self.on_stop = on_stop
        self.on_check = on_check
        self.on_resume = on_resume
        self.on_comment = on_comment
        self.get_session_state = get_session_state
        self.listener = None
        self._thread = None

    def _on_press(self, key):
        try:
            # Get current session state if available
            session_state = self.get_session_state() if self.get_session_state else None
            
            match key:
                case keyboard.Key.f6:
                    logger.info("F6 hotkey detected, triggering comment")
                    if self.on_comment:
                        self.on_comment()
                case keyboard.Key.f7:
                    logger.info("F7 hotkey detected, triggering check")
                    if self.on_check:
                        self.on_check()
                case keyboard.Key.f8:
                    logger.info(f"F8 hotkey detected, session state: {session_state}")
                    # Only trigger pause if session is recording
                    if self.on_pause and session_state == 'recording':
                        logger.info("Triggering pause")
                        self.on_pause()
                case keyboard.Key.f9:
                    logger.info(f"F9 hotkey detected, session state: {session_state}")
                    # Only trigger resume if session is paused
                    if self.on_resume and session_state == 'paused':
                        logger.info("Triggering resume")
                        self.on_resume()
                case keyboard.Key.f10:
                    logger.info("F10 hotkey detected, triggering stop")
                    if self.on_stop:
                        self.on_stop()
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