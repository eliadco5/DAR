# Session management (start/stop, hotkeys)
from recorder.event_listener import EventListener

class SessionManager:
    def __init__(self):
        self.listener = EventListener()
        self.state = 'stopped'  # 'recording', 'paused', 'stopped'

    def start(self):
        self.listener.start()
        self.state = 'recording'

    def pause(self):
        self.listener.pause()
        self.state = 'paused'

    def resume(self):
        self.listener.resume()
        self.state = 'recording'

    def stop(self):
        self.listener.stop()
        self.state = 'stopped'

    def clear(self):
        self.listener.clear()
        self.state = 'stopped'

    def get_events(self):
        return self.listener.get_events() 