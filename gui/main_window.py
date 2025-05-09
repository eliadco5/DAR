# Main Tkinter window and controls
import tkinter as tk
from utils.hotkeys import HotkeyManager
from recorder.session import SessionManager
from gui.editor import ActionEditor

class MainWindow:
    def __init__(self, root=None):
        self.root = root or tk.Tk()
        self.root.title("Desktop Automation Recorder")
        self.root.geometry("600x400")

        self.status_var = tk.StringVar(value="Idle")
        self.status_label = tk.Label(self.root, textvariable=self.status_var, fg="blue")
        self.status_label.pack(pady=10)

        self.start_button = tk.Button(self.root, text="Start Recording", command=self.start_recording)
        self.start_button.pack(pady=5)

        self.pause_button = tk.Button(self.root, text="Pause Recording", command=self.pause_recording)
        self.pause_button.pack(pady=5)

        self.stop_button = tk.Button(self.root, text="Stop Recording", command=self.stop_recording)
        self.stop_button.pack(pady=5)

        # Action list and editor
        self.action_editor = ActionEditor()
        self.session_manager = SessionManager()

        self.actions_listbox = tk.Listbox(self.root, width=80, height=10)
        self.actions_listbox.pack(pady=10)

        self.edit_frame = tk.Frame(self.root)
        self.edit_frame.pack(pady=5)
        self.delete_button = tk.Button(self.edit_frame, text="Delete", command=self.delete_action)
        self.delete_button.grid(row=0, column=0, padx=5)
        self.move_up_button = tk.Button(self.edit_frame, text="Move Up", command=self.move_action_up)
        self.move_up_button.grid(row=0, column=1, padx=5)
        self.move_down_button = tk.Button(self.edit_frame, text="Move Down", command=self.move_action_down)
        self.move_down_button.grid(row=0, column=2, padx=5)

        self.hotkeys = HotkeyManager(on_pause=self.pause_recording, on_stop=self.stop_recording)
        self.hotkeys.start()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_recording(self):
        self.session_manager.start()
        self.status_var.set("Recording...")
        self.status_label.config(fg="red")
        self.update_action_list()
        self.root.after(500, self.poll_actions)

    def pause_recording(self):
        self.session_manager.pause()
        self.status_var.set("Paused")
        self.status_label.config(fg="orange")

    def stop_recording(self):
        self.session_manager.stop()
        self.status_var.set("Stopped")
        self.status_label.config(fg="gray")
        self.update_action_list()

    def poll_actions(self):
        if self.session_manager.state == 'recording':
            self.update_action_list()
            self.root.after(500, self.poll_actions)

    def update_action_list(self):
        actions = self.session_manager.get_events()
        self.action_editor.set_actions(actions)
        self.actions_listbox.delete(0, tk.END)
        for i, action in enumerate(self.action_editor.get_actions()):
            desc = f"{i+1}. {action['type']} {action['event']}"
            if action['type'] == 'mouse':
                desc += f" at ({action['x']}, {action['y']})"
            if action['type'] == 'keyboard':
                desc += f" key {action.get('key', '')}"
            self.actions_listbox.insert(tk.END, desc)

    def delete_action(self):
        selection = self.actions_listbox.curselection()
        if selection:
            index = selection[0]
            self.action_editor.delete_action(index)
            # Update SessionManager's events to match edited list
            self.session_manager.listener.events = self.action_editor.get_actions()
            self.update_action_list()

    def move_action_up(self):
        selection = self.actions_listbox.curselection()
        if selection and selection[0] > 0:
            index = selection[0]
            self.action_editor.move_action_up(index)
            self.update_action_list()
            self.actions_listbox.select_set(index - 1)

    def move_action_down(self):
        selection = self.actions_listbox.curselection()
        if selection and selection[0] < self.actions_listbox.size() - 1:
            index = selection[0]
            self.action_editor.move_action_down(index)
            self.update_action_list()
            self.actions_listbox.select_set(index + 1)

    def on_close(self):
        self.hotkeys.stop()
        self.root.destroy() 