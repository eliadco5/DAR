# Main Tkinter window and controls
import tkinter as tk
from tkinter import ttk
from utils.hotkeys import HotkeyManager
from recorder.session import SessionManager
from gui.editor import ActionEditor

class MainWindow:
    def __init__(self, root=None):
        self.root = root or tk.Tk()
        self.root.title("Desktop Automation Recorder")
        self.root.minsize(1100, 700)
        self.root.geometry("1200x800")
        self.root.configure(bg="#f4f4f4")

        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('TButton', font=('Segoe UI', 12), padding=6)
        style.configure('TLabel', font=('Segoe UI', 12))
        style.configure('Header.TLabel', font=('Segoe UI', 20, 'bold'), background="#f4f4f4")
        style.configure('Status.TLabel', font=('Segoe UI', 12), background="#eaeaea")
        style.configure('Sidebar.TFrame', background="#eaeaea")
        style.configure('Sidebar.TButton', font=('Segoe UI', 12), padding=10, background="#eaeaea")

        # Main layout: sidebar + main area
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Sidebar for main actions
        sidebar = ttk.Frame(main_frame, style='Sidebar.TFrame', width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=0)
        sidebar.pack_propagate(False)

        self.header = ttk.Label(sidebar, text="Automation Recorder", style='Header.TLabel', anchor='center')
        self.header.pack(pady=(30, 30), fill=tk.X)

        self.start_button = ttk.Button(sidebar, text="Start Recording", command=self.start_recording, style='Sidebar.TButton')
        self.start_button.pack(fill=tk.X, pady=5, padx=20)
        self.pause_button = ttk.Button(sidebar, text="Pause Recording", command=self.pause_recording, style='Sidebar.TButton')
        self.pause_button.pack(fill=tk.X, pady=5, padx=20)
        self.stop_button = ttk.Button(sidebar, text="Stop Recording", command=self.stop_recording, style='Sidebar.TButton')
        self.stop_button.pack(fill=tk.X, pady=5, padx=20)
        self.preview_button = ttk.Button(sidebar, text="Preview", command=self.preview_actions, style='Sidebar.TButton')
        self.preview_button.pack(fill=tk.X, pady=5, padx=20)
        self.save_button = ttk.Button(sidebar, text="Save", command=self.save_session, style='Sidebar.TButton')
        self.save_button.pack(fill=tk.X, pady=5, padx=20)
        self.load_button = ttk.Button(sidebar, text="Load", command=self.load_session, style='Sidebar.TButton')
        self.load_button.pack(fill=tk.X, pady=5, padx=20)
        self.export_script_button = ttk.Button(sidebar, text="Export as Script", command=self.export_script, style='Sidebar.TButton')
        self.export_script_button.pack(fill=tk.X, pady=5, padx=20)

        # Main area for action list and editing
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 0), pady=0)

        # Status bar at the bottom
        self.status_var = tk.StringVar(value="Idle")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, style='Status.TLabel', anchor='w', relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, ipady=6)

        # Action list frame
        action_frame = ttk.LabelFrame(content_frame, text="Recorded Actions")
        action_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(30, 10))
        self.actions_listbox = tk.Listbox(action_frame, width=90, height=25, font=('Segoe UI', 11))
        self.actions_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10,0), pady=10)
        self.actions_listbox.bind('<Delete>', lambda e: self.delete_action())
        self.actions_listbox.bind('<BackSpace>', lambda e: self.delete_action())
        scrollbar = ttk.Scrollbar(action_frame, orient=tk.VERTICAL, command=self.actions_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        self.actions_listbox.config(yscrollcommand=scrollbar.set)

        # Edit controls frame
        edit_frame = ttk.Frame(content_frame)
        edit_frame.pack(pady=10)
        self.delete_button = ttk.Button(edit_frame, text="Delete", command=self.delete_action)
        self.delete_button.grid(row=0, column=0, padx=10)
        self.move_up_button = ttk.Button(edit_frame, text="Move Up", command=self.move_action_up)
        self.move_up_button.grid(row=0, column=1, padx=10)
        self.move_down_button = ttk.Button(edit_frame, text="Move Down", command=self.move_action_down)
        self.move_down_button.grid(row=0, column=2, padx=10)
        self.view_screenshot_button = ttk.Button(edit_frame, text="View Screenshot", command=self.view_screenshot)
        self.view_screenshot_button.grid(row=0, column=3, padx=10)

        # Action editor and session manager
        self.action_editor = ActionEditor()
        self.session_manager = SessionManager()

        self.hotkeys = HotkeyManager(on_pause=self.pause_recording, on_stop=self.stop_recording)
        self.hotkeys.start()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_recording(self):
        self.session_manager.start()
        self.status_var.set("Recording...")
        self.update_action_list()
        self.root.after(100, self.poll_actions)

    def pause_recording(self):
        self.session_manager.pause()
        self.status_var.set("Paused")

    def stop_recording(self):
        self.session_manager.stop()
        self.status_var.set("Stopped")
        self.update_action_list()

    def poll_actions(self):
        if self.session_manager.state == 'recording':
            self.update_action_list()
            self.root.after(100, self.poll_actions)

    def update_action_list(self):
        actions = self.session_manager.get_events()
        self.action_editor.set_actions(actions)
        self.actions_listbox.delete(0, tk.END)
        for i, action in enumerate(self.action_editor.get_actions()):
            desc = f"{i+1}. {action['type']} "
            if action['type'] == 'mouse':
                if action['event'] == 'down':
                    desc += f"click at ({action['x']}, {action['y']})"
                elif action['event'] == 'up':
                    desc += f"release at ({action['x']}, {action['y']})"
                else:
                    desc += f"{action['event']} at ({action['x']}, {action['y']})"
            elif action['type'] == 'keyboard':
                desc += f"{action['event']} key {action.get('key', '')}"
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

    def view_screenshot(self):
        selection = self.actions_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        action = self.action_editor.get_actions()[index]
        screenshot = action.get('screenshot')
        if screenshot is not None:
            try:
                from PIL import ImageTk
                win = tk.Toplevel(self.root)
                win.title("Screenshot Preview")
                img = screenshot.copy()
                img.thumbnail((400, 400))
                tk_img = ImageTk.PhotoImage(img)
                label = tk.Label(win, image=tk_img)
                label.image = tk_img  # Keep reference
                label.pack()
            except Exception as e:
                tk.messagebox.showerror("Error", f"Could not display screenshot: {e}")
        else:
            tk.messagebox.showinfo("No Screenshot", "No screenshot available for this action.")

    def on_close(self):
        self.hotkeys.stop()
        self.root.destroy()

    def save_session(self):
        from tkinter import filedialog, messagebox
        from storage.save_load import save_actions
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if filepath:
            try:
                save_actions(filepath, self.action_editor.get_actions())
                messagebox.showinfo("Saved", f"Session saved to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save session: {e}")

    def load_session(self):
        from tkinter import filedialog, messagebox
        from storage.save_load import load_actions
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if filepath:
            try:
                actions = load_actions(filepath)
                self.action_editor.set_actions(actions)
                self.session_manager.listener.events = self.action_editor.get_actions()
                self.update_action_list()
                messagebox.showinfo("Loaded", f"Session loaded from {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load session: {e}")

    def export_script(self):
        from tkinter import filedialog, messagebox
        from scriptgen.generator import generate_script
        filepath = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")])
        if filepath:
            try:
                script = generate_script(self.action_editor.get_actions())
                with open(filepath, 'w') as f:
                    f.write(script)
                messagebox.showinfo("Exported", f"Script exported to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export script: {e}")

    def preview_actions(self):
        import threading
        from tkinter import messagebox
        from playback.player import play_actions
        def run_playback():
            try:
                self.set_controls_state(tk.DISABLED)
                play_actions(self.action_editor.get_actions())
            except Exception as e:
                messagebox.showerror("Playback Error", str(e))
            finally:
                self.set_controls_state(tk.NORMAL)
        threading.Thread(target=run_playback, daemon=True).start()

    def set_controls_state(self, state):
        widgets = [
            self.start_button, self.pause_button, self.stop_button,
            self.delete_button, self.move_up_button, self.move_down_button,
            self.view_screenshot_button, self.save_button, self.load_button,
            self.export_script_button, self.preview_button
        ]
        for w in widgets:
            w.config(state=state)
        self.actions_listbox.config(state=state) 