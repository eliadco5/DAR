import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLabel, QStatusBar, QFrame, QFileDialog, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from utils.hotkeys import HotkeyManager
from recorder.session import SessionManager
from gui.editor import ActionEditor
from storage.save_load import save_actions, load_actions
from scriptgen.generator import generate_script
from playback.player import play_actions
from PIL import ImageQt, Image
import threading

DARK_STYLE = """
QWidget { background-color: #232629; color: #f0f0f0; }
QFrame#Sidebar { background-color: #181a1b; }
QLabel#Header { color: #f0f0f0; font-size: 22px; font-weight: bold; }
QPushButton { background-color: #323639; color: #f0f0f0; border: 1px solid #444; border-radius: 6px; padding: 8px 0; }
QPushButton:hover { background-color: #3a3f44; }
QPushButton:pressed { background-color: #232629; }
QListWidget { background-color: #232629; color: #f0f0f0; border: 1px solid #444; }
QStatusBar { background: #181a1b; color: #f0f0f0; min-height:36px; padding:0 8px 0 8px; }
QStatusBar::item { border: none; }
QLabel { color: #f0f0f0; }
"""

LIGHT_STYLE = """
QWidget { background-color: #f4f4f4; color: #232629; }
QFrame#Sidebar { background-color: #eaeaea; }
QLabel#Header { color: #232629; font-size: 22px; font-weight: bold; }
QPushButton { background-color: #f4f4f4; color: #232629; border: 1px solid #bbb; border-radius: 6px; padding: 8px 0; }
QPushButton:hover { background-color: #e0e0e0; }
QPushButton:pressed { background-color: #eaeaea; }
QListWidget { background-color: #fff; color: #232629; border: 1px solid #bbb; }
QStatusBar { background: #eaeaea; color: #232629; min-height:36px; padding:0 8px 0 8px; }
QStatusBar::item { border: none; }
QLabel { color: #232629; }
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Desktop Automation Recorder')
        self.setMinimumSize(1100, 700)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName('Sidebar')
        sidebar.setFrameShape(QFrame.Shape.StyledPanel)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        sidebar.setLayout(sidebar_layout)
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: #181a1b;")

        self.header = QLabel('Recorder')
        self.header.setObjectName('Header')
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(self.header)

        self.start_button = QPushButton('Start Recording')
        self.start_button.clicked.connect(self.start_recording)
        self.pause_button = QPushButton('Pause Recording')
        self.pause_button.clicked.connect(self.pause_recording)
        self.stop_button = QPushButton('Stop Recording')
        self.stop_button.clicked.connect(self.stop_recording)
        self.preview_button = QPushButton('Preview')
        self.preview_button.clicked.connect(self.preview_actions)
        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save_session)
        self.load_button = QPushButton('Load')
        self.load_button.clicked.connect(self.load_session)
        self.export_script_button = QPushButton('Generate Script')
        self.export_script_button.clicked.connect(self.export_script)
        for btn in [self.start_button, self.pause_button, self.stop_button, self.preview_button, self.save_button, self.load_button, self.export_script_button]:
            btn.setMinimumHeight(40)
            sidebar_layout.addWidget(btn)

        # Main area
        main_area = QWidget()
        main_layout = QVBoxLayout()
        main_area.setLayout(main_layout)

        main_layout.addWidget(QLabel('Recorded Actions'))
        self.action_list = QListWidget()
        main_layout.addWidget(self.action_list)

        # Edit controls
        edit_controls = QHBoxLayout()
        self.delete_button = QPushButton('Delete')
        self.delete_button.clicked.connect(self.delete_action)
        self.move_up_button = QPushButton('Move Up')
        self.move_up_button.clicked.connect(self.move_action_up)
        self.move_down_button = QPushButton('Move Down')
        self.move_down_button.clicked.connect(self.move_action_down)
        self.view_screenshot_button = QPushButton('View Screenshot')
        self.view_screenshot_button.clicked.connect(self.view_screenshot)
        for btn in [self.delete_button, self.move_up_button, self.move_down_button, self.view_screenshot_button]:
            btn.setMinimumHeight(32)
            edit_controls.addWidget(btn)
        main_layout.addLayout(edit_controls)

        # Layout
        central = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(sidebar)
        layout.addWidget(main_area, 1)
        central.setLayout(layout)
        self.setCentralWidget(central)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.setStyleSheet("QStatusBar{min-height:36px;padding:0 8px 0 8px; background-color: #181a1b;} QStatusBar::item { border: none; }")
        self.status_label = QLabel('Idle')
        self.status_label.setStyleSheet("font-size: 15px; color: #f0f0f0;")
        self.status.addWidget(self.status_label, 1)

        self.is_dark = True
        self.toggle_theme_button = QPushButton('☀️')
        self.toggle_theme_button.setFixedSize(15, 15)
        self.toggle_theme_button.setToolTip('Switch to Light Mode')
        self.toggle_theme_button.clicked.connect(self.toggle_theme)
        self.toggle_theme_button.setStyleSheet(
            "min-width: 24px; max-width: 24px; min-height: 12; max-height: 12;"
            "font-size: 11px;"
            "border: 2px solid #f0c000; border-radius: 12px;"
            "background: transparent; color: #f0c000;"
            "margin: 0;"
        )
        self.status.addPermanentWidget(self.toggle_theme_button)
        self.sidebar = sidebar

        # Action editor and session manager
        self.action_editor = ActionEditor()
        self.session_manager = SessionManager()

        # Hotkey manager
        self.hotkeys = HotkeyManager(on_pause=self.pause_recording, on_stop=self.stop_recording)
        self.hotkeys.start()
        self._setup_shortcuts()

        # Apply dark mode stylesheet by default
        self.setStyleSheet(DARK_STYLE)

    def _setup_shortcuts(self):
        # Add keyboard shortcuts for delete, move up, move down
        self.action_list.installEventFilter(self)

    def eventFilter(self, obj, event):
        from PyQt6.QtCore import QEvent
        if obj == self.action_list:
            if event.type() == QEvent.Type.KeyPress:
                key = event.key()
                if key in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
                    self.delete_action()
                    return True
                elif key == Qt.Key.Key_Up and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    self.move_action_up()
                    return True
                elif key == Qt.Key.Key_Down and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    self.move_action_down()
                    return True
        return super().eventFilter(obj, event)

    def start_recording(self):
        self.session_manager.start()
        self.status_label.setText("Recording...")
        self.update_action_list()
        self._poll_actions()

    def pause_recording(self):
        self.session_manager.pause()
        self.status_label.setText("Paused")

    def stop_recording(self):
        self.session_manager.stop()
        self.status_label.setText("Stopped")
        self.update_action_list()

    def _poll_actions(self):
        if self.session_manager.state == 'recording':
            self.update_action_list()
            QTimer.singleShot(100, self._poll_actions)

    def update_action_list(self):
        actions = self.session_manager.get_events()
        self.action_editor.set_actions(actions)
        self.action_list.clear()
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
            self.action_list.addItem(desc)

    def delete_action(self):
        row = self.action_list.currentRow()
        if row >= 0:
            self.action_editor.delete_action(row)
            self.session_manager.listener.events = self.action_editor.get_actions()
            self.update_action_list()

    def move_action_up(self):
        row = self.action_list.currentRow()
        if row > 0:
            self.action_editor.move_action_up(row)
            self.update_action_list()
            self.action_list.setCurrentRow(row - 1)

    def move_action_down(self):
        row = self.action_list.currentRow()
        if row < self.action_list.count() - 1 and row >= 0:
            self.action_editor.move_action_down(row)
            self.update_action_list()
            self.action_list.setCurrentRow(row + 1)

    def view_screenshot(self):
        row = self.action_list.currentRow()
        if row < 0:
            return
        action = self.action_editor.get_actions()[row]
        screenshot = action.get('screenshot')
        if screenshot is not None:
            try:
                img = screenshot.copy()
                img.thumbnail((400, 400))
                qt_img = ImageQt.ImageQt(img)
                from PyQt6.QtWidgets import QLabel, QDialog, QVBoxLayout
                from PyQt6.QtGui import QPixmap
                win = QDialog(self)
                win.setWindowTitle("Screenshot Preview")
                layout = QVBoxLayout()
                label = QLabel()
                label.setPixmap(QPixmap.fromImage(qt_img))
                layout.addWidget(label)
                win.setLayout(layout)
                win.exec()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not display screenshot: {e}")
        else:
            QMessageBox.information(self, "No Screenshot", "No screenshot available for this action.")

    def save_session(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Save Session", "", "JSON Files (*.json)")
        if filepath:
            try:
                save_actions(filepath, self.action_editor.get_actions())
                QMessageBox.information(self, "Saved", f"Session saved to {filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save session: {e}")

    def load_session(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Load Session", "", "JSON Files (*.json)")
        if filepath:
            try:
                actions = load_actions(filepath)
                self.action_editor.set_actions(actions)
                self.session_manager.listener.events = self.action_editor.get_actions()
                self.update_action_list()
                QMessageBox.information(self, "Loaded", f"Session loaded from {filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not load session: {e}")

    def export_script(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Export Script", "", "Python Files (*.py)")
        if filepath:
            try:
                script = generate_script(self.action_editor.get_actions())
                with open(filepath, 'w') as f:
                    f.write(script)
                QMessageBox.information(self, "Exported", f"Script exported to {filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not export script: {e}")

    def preview_actions(self):
        def run_playback():
            try:
                self.set_controls_state(False)
                play_actions(self.action_editor.get_actions())
            except Exception as e:
                QMessageBox.critical(self, "Playback Error", str(e))
            finally:
                self.set_controls_state(True)
        threading.Thread(target=run_playback, daemon=True).start()

    def set_controls_state(self, enabled):
        for btn in [self.start_button, self.pause_button, self.stop_button, self.delete_button,
                    self.move_up_button, self.move_down_button, self.view_screenshot_button,
                    self.save_button, self.load_button, self.export_script_button, self.preview_button]:
            btn.setEnabled(enabled)
        self.action_list.setEnabled(enabled)

    def closeEvent(self, event):
        self.hotkeys.stop()
        event.accept()

    def toggle_theme(self):
        self.toggle_theme_button.setEnabled(False)
        if self.is_dark:
            self.setStyleSheet(LIGHT_STYLE)
            self.toggle_theme_button.setText('🌙')
            self.toggle_theme_button.setToolTip('Switch to Dark Mode')
            self.status.setStyleSheet("QStatusBar{min-height:36px;padding:0 8px 0 8px; background-color: #eaeaea;} QStatusBar::item { border: none; }")
            self.status_label.setStyleSheet("font-size: 15px; color: #232629;")
            self.sidebar.setStyleSheet("background-color: #eaeaea;")
            self.header.setStyleSheet("color: #232629; font-size: 22px; font-weight: bold;")
        else:
            self.setStyleSheet(DARK_STYLE)
            self.toggle_theme_button.setText('☀️')
            self.toggle_theme_button.setToolTip('Switch to Light Mode')
            self.status.setStyleSheet("QStatusBar{min-height:36px;padding:0 8px 0 8px; background-color: #181a1b;} QStatusBar::item { border: none; }")
            self.status_label.setStyleSheet("font-size: 15px; color: #f0f0f0;")
            self.sidebar.setStyleSheet("background-color: #181a1b;")
            self.header.setStyleSheet("color: #f0f0f0; font-size: 22px; font-weight: bold;")
        self.is_dark = not self.is_dark
        QTimer.singleShot(200, lambda: self.toggle_theme_button.setEnabled(True))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 