# Main Tkinter window and controls
import tkinter as tk
from utils.hotkeys import HotkeyManager

class MainWindow:
    def __init__(self, root=None):
        self.root = root or tk.Tk()
        self.root.title("Desktop Automation Recorder")
        self.root.geometry("400x200")

        self.status_var = tk.StringVar(value="Idle")
        self.status_label = tk.Label(self.root, textvariable=self.status_var, fg="blue")
        self.status_label.pack(pady=10)

        self.start_button = tk.Button(self.root, text="Start Recording", command=self.start_recording)
        self.start_button.pack(pady=5)

        self.pause_button = tk.Button(self.root, text="Pause Recording", command=self.pause_recording)
        self.pause_button.pack(pady=5)

        self.stop_button = tk.Button(self.root, text="Stop Recording", command=self.stop_recording)
        self.stop_button.pack(pady=5)

        self.hotkeys = HotkeyManager(on_pause=self.pause_recording, on_stop=self.stop_recording)
        self.hotkeys.start()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_recording(self):
        self.status_var.set("Recording...")
        self.status_label.config(fg="red")

    def pause_recording(self):
        self.status_var.set("Paused")
        self.status_label.config(fg="orange")

    def stop_recording(self):
        self.status_var.set("Stopped")
        self.status_label.config(fg="gray")

    def on_close(self):
        self.hotkeys.stop()
        self.root.destroy() 