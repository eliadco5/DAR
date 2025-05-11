import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLabel, QStatusBar, QFrame, QFileDialog, QMessageBox, QSizePolicy, QSpinBox, QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QComboBox, QInputDialog, QLineEdit, QListWidgetItem
)
from PyQt6.QtCore import Qt, QTimer, QMetaObject, Q_ARG, pyqtSignal, QObject, QEvent
from PyQt6.QtGui import QIcon, QPixmap, QBrush, QColor, QFont
from utils.hotkeys import HotkeyManager
from recorder.session import SessionManager
from gui.editor import ActionEditor
from storage.save_load import save_actions, load_actions
from scriptgen.generator import generate_script
from playback.player import play_actions
from PIL import ImageQt, Image, ImageChops, ImageStat
import threading
from recorder.screenshot import ScreenshotUtil
import time
import os
import traceback

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

# Custom signal handler for thread-safe UI updates
class SignalHandler(QObject):
    update_error_panel = pyqtSignal(object, object)
    playback_finished = pyqtSignal(bool)
    add_check = pyqtSignal()  # Signal for adding check points
    add_comment = pyqtSignal()  # Signal for adding comments
    
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Desktop Automation Recorder')
        self.setMinimumSize(1100, 700)

        # Create signal handler for thread communication
        self.signals = SignalHandler()
        self.signals.update_error_panel.connect(self._on_update_error_panel)
        self.signals.playback_finished.connect(self._on_playback_finished)
        self.signals.add_check.connect(self._execute_add_check)  # Connect check signal
        self.signals.add_comment.connect(self._execute_add_comment)  # Connect comment signal

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
        self.pause_button = QPushButton('Pause Recording (F8)')
        self.pause_button.clicked.connect(self.pause_recording)
        self.pause_button.setEnabled(False)  # Initially disabled
        self.pause_button.setStyleSheet("""
            QPushButton:disabled { 
                color: #888888; 
            }
        """)
        self.stop_button = QPushButton('Stop Recording (F10)')
        self.stop_button.clicked.connect(self.stop_recording)
        self.check_button = QPushButton('Add Check (F7)')
        self.check_button.clicked.connect(self.add_check_action)
        self.comment_button = QPushButton('Add Comment (F6)')
        self.comment_button.clicked.connect(self.add_comment_action)
        self.preview_button = QPushButton('Preview')
        self.preview_button.clicked.connect(self.preview_actions)
        self.preview_button.setEnabled(False)  # Initially disabled
        self.preview_button.setStyleSheet("""
            QPushButton:disabled { 
                color: #888888; 
            }
        """)
        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save_session)
        self.load_button = QPushButton('Load')
        self.load_button.clicked.connect(self.load_session)
        self.test_check_button = QPushButton('Test Check Failure')
        self.test_check_button.clicked.connect(self.test_check_failure)
        self.test_check_button.setEnabled(False)  # Initially disabled
        self.test_check_button.setStyleSheet("""
            QPushButton:disabled { 
                color: #888888; 
            }
        """)
        
        for btn in [self.start_button, self.pause_button, self.stop_button, 
                   self.check_button, self.comment_button, self.preview_button, 
                   self.save_button, self.load_button, self.test_check_button]:
            btn.setMinimumHeight(40)
            sidebar_layout.addWidget(btn)

        self.tolerance_label = QLabel('Tolerance:')
        self.tolerance_combo = QComboBox()
        self.tolerance_combo.addItems(["Low", "Medium", "High"])
        self.tolerance_combo.setCurrentIndex(1)  # Default to Medium
        self.tolerance_combo.setToolTip(
            "Visual comparison tolerance levels:\n\n"
            "Low (3): Very strict matching. Even minor pixel differences will fail.\n"
            "Medium (7): Balanced. Small visual differences are accepted.\n"
            "High (10): More permissive. Allows more visual differences to pass.\n\n"
            "Increase for dynamic UIs with small variations.\n"
            "Decrease for precise visual validation."
        )
        sidebar_layout.addWidget(self.tolerance_label)
        sidebar_layout.addWidget(self.tolerance_combo)
        
        # Add Generate Script button at the bottom with some spacing
        sidebar_layout.addStretch(1)  # Add stretch to push the button to the bottom
        self.export_script_button = QPushButton('Generate Script')
        self.export_script_button.clicked.connect(self.export_script)
        self.export_script_button.setMinimumHeight(40)
        self.export_script_button.setEnabled(False)  # Initially disabled
        self.export_script_button.setStyleSheet("""
            QPushButton:disabled { 
                color: #888888; 
            }
        """)
        sidebar_layout.addWidget(self.export_script_button)

        # Left side - operations panel
        operations_panel = QWidget()
        operations_layout = QVBoxLayout()
        operations_panel.setLayout(operations_layout)

        operations_layout.addWidget(QLabel('Recorded Actions'))
        self.action_list = QListWidget()
        operations_layout.addWidget(self.action_list)

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
        operations_layout.addLayout(edit_controls)

        # Right side - error panel
        self.error_panel = QWidget()
        error_layout = QVBoxLayout()
        self.error_panel.setLayout(error_layout)
        
        self.error_header = QLabel('Visual Check Result')
        self.error_header.setObjectName('Header')
        self.error_header.setStyleSheet("font-size: 18px; font-weight: bold;")
        error_layout.addWidget(self.error_header)
        
        self.error_status = QLabel('')
        error_layout.addWidget(self.error_status)
        
        # Image comparison layout
        image_layout = QHBoxLayout()
        
        # Reference image
        ref_container = QVBoxLayout()
        self.ref_label = QLabel('Reference Image')
        self.ref_image = QLabel()
        self.ref_image.setMinimumSize(300, 300)
        self.ref_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ref_image.setStyleSheet("border: 1px solid #444;")
        ref_container.addWidget(self.ref_label)
        ref_container.addWidget(self.ref_image)
        image_layout.addLayout(ref_container)
        
        # Test image
        test_container = QVBoxLayout()
        self.test_label = QLabel('Current Image')
        self.test_image = QLabel()
        self.test_image.setMinimumSize(300, 300)
        self.test_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.test_image.setStyleSheet("border: 1px solid #444;")
        test_container.addWidget(self.test_label)
        test_container.addWidget(self.test_image)
        image_layout.addLayout(test_container)
        
        error_layout.addLayout(image_layout)
        
        # Add continue/ignore button
        button_layout = QHBoxLayout()
        
        self.dont_continue_button = QPushButton('Stop Test')
        self.dont_continue_button.clicked.connect(self.stop_after_error)
        self.dont_continue_button.setMinimumHeight(40)
        self.dont_continue_button.setStyleSheet("""
            QPushButton { 
                background-color: #B33A3A; 
                color: white;
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: #D44242;
            }
        """)
        
        self.continue_button = QPushButton('Continue Anyway')
        self.continue_button.clicked.connect(self.continue_after_error)
        self.continue_button.setMinimumHeight(40)
        self.continue_button.setStyleSheet("""
            QPushButton { 
                background-color: #3A7CA5; 
                color: white;
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: #4590BD;
            }
        """)
        
        button_layout.addWidget(self.dont_continue_button)
        button_layout.addWidget(self.continue_button)
        
        error_layout.addLayout(button_layout)
        
        # Hide error panel initially
        self.error_panel.hide()

        # Main layout with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left_widget = QWidget()
        left_layout = QHBoxLayout()
        left_layout.addWidget(sidebar)
        left_layout.addWidget(operations_panel)
        left_widget.setLayout(left_layout)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(self.error_panel)
        splitter.setSizes([700, 400])  # Initial sizes
        
        # Set as central widget
        self.setCentralWidget(splitter)

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
        self.hotkeys = HotkeyManager(
            on_pause=self.pause_recording,
            on_stop=self.stop_recording,
            on_check=self.add_check_action,
            on_resume=self.resume_recording,
            on_comment=self.add_comment_action,
            get_session_state=self.get_session_state
        )
        self.hotkeys.start()
        self._setup_shortcuts()

        # Apply dark mode stylesheet by default
        self.setStyleSheet(DARK_STYLE)

        self.failed_check_images = None  # (ref_img, test_img)
        self.continue_after_fail = False
        self.playback_thread = None
        self.check_event = threading.Event()  # For thread synchronization

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
        self.update_pause_resume_button(paused=False)
        self.update_action_list()
        self._poll_actions()
        
        # Enable pause button when recording starts
        self.pause_button.setEnabled(True)
        
        # Minimize the window when recording starts
        self.showMinimized()

    def pause_recording(self):
        # Only pause if recording is active
        if self.session_manager.state == 'recording':
            self.session_manager.pause()
            self.status_label.setText("Paused")
            self.update_pause_resume_button(paused=True)

    def stop_recording(self):
        self.session_manager.stop()
        self.status_label.setText("Stopped")
        self.update_action_list()
        
        # Disable pause button when recording stops
        self.pause_button.setEnabled(False)
        
        # Enable other buttons if there are actions
        has_actions = len(self.action_editor.get_actions()) > 0
        self.preview_button.setEnabled(has_actions)
        self.export_script_button.setEnabled(has_actions)
        self.test_check_button.setEnabled(has_actions)

    def _poll_actions(self):
        """Poll for new actions and update the UI.
        This method will recursively schedule itself while recording is active.
        """
        # Only poll if the state is currently recording
        if self.session_manager.state != 'recording':
            print("DEBUG: Polling stopped because state is", self.session_manager.state)
            return
            
        # Update the action list with the latest events
        self.update_action_list()
        
        # Schedule the next poll
        print("DEBUG: Polling for actions...")
        QTimer.singleShot(100, self._poll_actions)

    def update_action_list(self):
        actions = self.session_manager.get_events()
        self.action_editor.set_actions(actions)
        self.action_list.clear()
        for i, action in enumerate(self.action_editor.get_actions()):
            if action['type'] == 'check':
                img = action.get('image')
                size_info = f" ({img.width}x{img.height})" if img else ""
                check_name = action.get('check_name', '')
                if check_name:
                    desc = f"{i+1}. Check: '{check_name}'{size_info}"
                else:
                    desc = f"{i+1}. Check: Window visual verification{size_info}"
                item = QListWidgetItem(desc)
                item.setData(Qt.ItemDataRole.UserRole, action)
                self.action_list.addItem(item)
            elif action['type'] == 'comment':
                # Display comments with a distinctive style
                comment_text = action.get('comment', '')
                desc = f"{i+1}. Comment: '{comment_text}'"
                item = QListWidgetItem(desc)
                item.setData(Qt.ItemDataRole.UserRole, action)
                # Set distinctive styling for comments - different color and background
                if self.is_dark:
                    item.setForeground(QBrush(QColor("#A3BE8C")))  # Light green in dark mode
                    item.setBackground(QBrush(QColor("#2E3440")))  # Slightly lighter background
                else:
                    item.setForeground(QBrush(QColor("#38761D")))  # Dark green in light mode
                    item.setBackground(QBrush(QColor("#E8F4E5")))  # Light green background
                item.setFont(QFont("Segoe UI", weight=QFont.Weight.Bold))
                self.action_list.addItem(item)
            else:
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
                item = QListWidgetItem(desc)
                item.setData(Qt.ItemDataRole.UserRole, action)
                self.action_list.addItem(item)
        self.action_list.scrollToBottom()
        
        # Enable/disable buttons based on whether there are any actions
        has_actions = len(self.action_editor.get_actions()) > 0
        self.preview_button.setEnabled(has_actions)
        self.export_script_button.setEnabled(has_actions)
        self.test_check_button.setEnabled(has_actions)

    def delete_action(self):
        row = self.action_list.currentRow()
        if row >= 0:
            self.action_editor.delete_action(row)
            self.session_manager.listener.events = self.action_editor.get_actions()
            self.update_action_list()
            
            # Check if all actions have been deleted
            has_actions = len(self.action_editor.get_actions()) > 0
            self.preview_button.setEnabled(has_actions)
            self.export_script_button.setEnabled(has_actions)
            self.test_check_button.setEnabled(has_actions)

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
                
                # Enable buttons since we now have actions
                has_actions = len(actions) > 0
                self.preview_button.setEnabled(has_actions)
                self.export_script_button.setEnabled(has_actions)
                self.test_check_button.setEnabled(has_actions)
                
                QMessageBox.information(self, "Loaded", f"Session loaded from {filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not load session: {e}")

    def export_script(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Export Script", "", "Python Files (*.py)")
        if filepath:
            try:
                # Pass the current tolerance level to the script generator
                tolerance_level = self.tolerance_combo.currentText()
                script = generate_script(
                    self.action_editor.get_actions(), 
                    output_path=filepath,
                    tolerance_level=tolerance_level
                )
                with open(filepath, 'w') as f:
                    f.write(script)
                
                # Create custom export confirmation dialog with better formatting
                dialog = QDialog(self)
                dialog.setWindowTitle("Exported")
                dialog.setFixedSize(550, 250)
                dialog.setStyleSheet("""
                    QDialog { background-color: #232629; color: #f0f0f0; }
                    QLabel { color: #f0f0f0; font-size: 14px; }
                    QPushButton { 
                        background-color: #323639; 
                        color: #f0f0f0; 
                        border: 1px solid #444; 
                        border-radius: 6px; 
                        padding: 8px 16px;
                        min-width: 80px;
                    }
                    QPushButton:hover { background-color: #3a3f44; }
                    QPushButton:pressed { background-color: #232629; }
                """)
                
                layout = QVBoxLayout(dialog)
                layout.setContentsMargins(20, 20, 20, 20)
                layout.setSpacing(10)
                
                # Create icon and message in horizontal layout
                info_layout = QHBoxLayout()
                info_layout.setSpacing(15)
                
                # Create info icon label
                icon_label = QLabel()
                icon_label.setStyleSheet("font-size: 32px;")
                icon_label.setText("ℹ️")  # Using emoji as icon
                icon_label.setFixedSize(48, 48)
                icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                info_layout.addWidget(icon_label)
                
                message_layout = QVBoxLayout()
                message_layout.setSpacing(8)
                
                script_path = filepath.replace('/', '\\')
                script_label = QLabel("Script exported to:")
                script_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
                script_label.setWordWrap(True)
                
                script_label_path = QLabel(f"{script_path}")
                script_label_path.setStyleSheet("color: #8ab4f8; font-family: monospace; margin-left: 15px;")
                script_label_path.setWordWrap(True)
                script_label_path.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                
                # Ensure proper Windows path display with backslashes
                screenshots_path = os.path.join(os.path.dirname(filepath), 'screenshots')
                # Replace forward slashes with backslashes for display
                screenshots_path = screenshots_path.replace('/', '\\')
                
                screenshots_label = QLabel("Screenshots saved to:")
                screenshots_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
                screenshots_label.setWordWrap(True)
                
                screenshots_label_path = QLabel(f"{screenshots_path}")
                screenshots_label_path.setStyleSheet("color: #8ab4f8; font-family: monospace; margin-left: 15px;")
                screenshots_label_path.setWordWrap(True)
                screenshots_label_path.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                
                # Add tolerance level information
                tolerance_label = QLabel("Image comparison tolerance:")
                tolerance_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
                tolerance_label.setWordWrap(True)
                
                tolerance_value = self.get_tolerance_value()
                tolerance_text = QLabel(f"{tolerance_level} ({tolerance_value})")
                tolerance_text.setStyleSheet("color: #8ab4f8; margin-left: 15px;")

                message_layout.addWidget(script_label)
                message_layout.addWidget(script_label_path)
                message_layout.addWidget(screenshots_label)
                message_layout.addWidget(screenshots_label_path)
                message_layout.addWidget(tolerance_label)
                message_layout.addWidget(tolerance_text)
                info_layout.addLayout(message_layout, 1)
                
                layout.addLayout(info_layout)
                
                # Add OK button in its own layout for positioning
                button_layout = QHBoxLayout()
                button_layout.addStretch(1)
                ok_button = QPushButton("OK")
                ok_button.setFixedWidth(120)
                ok_button.setFixedHeight(40)
                ok_button.setStyleSheet("""
                    QPushButton { 
                        background-color: #323639; 
                        color: #f0f0f0; 
                        border: 1px solid #444; 
                        border-radius: 6px; 
                        padding: 8px 16px;
                        font-size: 14px;
                        font-weight: bold;
                    }
                    QPushButton:hover { background-color: #3a3f44; }
                    QPushButton:pressed { background-color: #232629; }
                """)
                ok_button.clicked.connect(dialog.accept)
                button_layout.addWidget(ok_button)
                
                layout.addLayout(button_layout)
                layout.addSpacing(10)
                
                dialog.exec()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not export script: {e}")

    def preview_actions(self):
        def run_playback():
            try:
                result = True
                fail_info = None
                
                # Setup for playback
                self.signals.update_error_panel.emit(None, None)  # Clear error panel
                self.check_event.clear()  # Reset event
                self.continue_after_fail = False
                
                # Get actions once so we can modify the starting point if needed
                all_actions = self.action_editor.get_actions()
                start_index = 0
                
                while start_index < len(all_actions):
                    # Create a subset of actions starting from the current index
                    actions = all_actions[start_index:]
                    
                    # Log what we're about to do for debugging
                    print(f"DEBUG: Starting playback from index {start_index} (of {len(all_actions)} total)")
                    if len(actions) > 0:
                        next_action = actions[0]
                        print(f"DEBUG: Next action type: {next_action.get('type', 'unknown')}")
                    
                    # Run playback with the configured tolerance, starting with the subset of actions
                    tolerance = self.get_tolerance_value()
                    result, fail_info, last_action_index = play_actions(
                        actions, 
                        tolerance=tolerance, 
                        fail_callback=self.on_visual_check_failed,
                        start_index=0  # We're starting from the beginning of the slice
                    )
                    
                    # Adjust the index to be relative to the original list
                    actual_last_index = start_index + last_action_index
                    print(f"DEBUG: Playback returned result={result}, last_action_index={last_action_index}, actual_last_index={actual_last_index}")
                    
                    # If playback failed due to visual check
                    if not result and fail_info:
                        # Wait for user to decide whether to continue
                        print("DEBUG: Waiting for user decision on check failure")
                        self.check_event.wait()  # Wait until user makes a decision
                        print(f"DEBUG: User decided to {'continue' if self.continue_after_fail else 'stop'}")
                        
                        # If user chose to continue, restart playback from the next action
                        if self.continue_after_fail:
                            # Continue from the action after the one that failed
                            start_index = actual_last_index + 1
                            print(f"DEBUG: Continuing from index {start_index}")
                            continue
                        else:
                            # User chose to stop
                            print("DEBUG: User chose to stop playback")
                            break
                    
                    # If we got here, playback completed without errors or was the final segment
                    break
            except Exception as e:
                print(f"Playback error: {e}")
                traceback.print_exc()  # Print full stack trace for better diagnosis
                result = False
            finally:
                # Signal that playback is finished
                self.signals.playback_finished.emit(result)
            
        # Clean up any existing thread
        if self.playback_thread and self.playback_thread.is_alive():
            self.check_event.set()  # Just in case it's waiting
            self.playback_thread.join(0.5)  # Wait a bit for it to end
        
        # Start new playback thread
        self.set_controls_state(False)
        
        # Minimize window before starting playback
        self.showMinimized()
        
        self.playback_thread = threading.Thread(target=run_playback, daemon=True)
        self.playback_thread.start()

    def set_controls_state(self, enabled):
        for btn in [self.start_button, self.pause_button, self.stop_button, self.delete_button,
                    self.move_up_button, self.move_down_button, self.view_screenshot_button,
                    self.save_button, self.load_button, self.export_script_button, self.preview_button, 
                    self.check_button, self.comment_button, self.test_check_button]:
            btn.setEnabled(enabled)
        self.action_list.setEnabled(enabled)

    def closeEvent(self, event):
        # Clean up threads before closing
        self.hotkeys.stop()
        if self.playback_thread and self.playback_thread.is_alive():
            self.check_event.set()  # Release any waiting thread
            self.playback_thread.join(0.5)  # Wait a bit for it to end
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

    def add_check_action(self):
        """Called from the hotkey thread when F7 is pressed"""
        # Use signal to execute in the main thread
        self.signals.add_check.emit()
        
    def _execute_add_check(self):
        """Executes in the main thread via signal/slot mechanism"""
        # Store current recording state
        was_recording = self.session_manager.state == 'recording'
        current_state = self.session_manager.state
        
        print(f"DEBUG: Executing add check. Current state: {current_state}")
        
        # Pause recording temporarily while showing the dialog
        if was_recording:
            print("DEBUG: Pausing recording for check dialog")
            self.session_manager.pause()
            # Update the UI to show the paused state
            self.update_pause_resume_button(paused=True)
            
        # On Windows, prepare for better window focus handling
        try_windows_focus = False
        if sys.platform == 'win32':
            try:
                import ctypes
                user32 = ctypes.windll.user32
                # Remember the current foreground window so we can force focus later
                foreground_hwnd = user32.GetForegroundWindow()
                print(f"DEBUG: Current foreground window handle: {foreground_hwnd}")
                try_windows_focus = True
            except Exception as e:
                print(f"DEBUG: Windows focus utilities not available: {e}")
                pass
        
        # Create a custom dialog that will stay on top of all windows
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
        from PyQt6.QtCore import Qt
        
        dialog = QDialog(None)  # Create with no parent initially
        dialog.setWindowTitle("Name Your Visual Check")
        
        # Set strong always-on-top flags to ensure dialog is visible and gets focus
        dialog.setWindowFlags(
            Qt.WindowType.Window |  # Create as a window
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.X11BypassWindowManagerHint |  # More forceful on Linux
            Qt.WindowType.Tool |  # Makes it a tool window which typically has higher z-order
            Qt.WindowType.FramelessWindowHint  # Remove frame for better focus
        )
        
        print(f"DEBUG: Dialog window flags: {dialog.windowFlags()}")
        
        dialog.setMinimumWidth(400)
        dialog.setModal(True)
        
        # Apply theme-appropriate styling with strong border for visibility
        dialog_border = "3px solid #FF9500"  # Orange border for visibility
        if self.is_dark:
            dialog.setStyleSheet(f"""
                QDialog {{ 
                    background-color: #232629; 
                    color: #f0f0f0; 
                    border: {dialog_border};
                    border-radius: 6px;
                }}
                QLabel {{ color: #f0f0f0; font-size: 14px; }}
                QLineEdit {{ 
                    background-color: #323639; 
                    color: #f0f0f0; 
                    border: 1px solid #444; 
                    border-radius: 4px; 
                    padding: 6px;
                    font-size: 14px;
                }}
                QPushButton {{ 
                    background-color: #323639; 
                    color: #f0f0f0; 
                    border: 1px solid #444; 
                    border-radius: 4px; 
                    padding: 6px 16px;
                    min-width: 80px;
                }}
                QPushButton:hover {{ background-color: #3a3f44; }}
                QPushButton:pressed {{ background-color: #232629; }}
            """)
        else:
            dialog.setStyleSheet(f"""
                QDialog {{ 
                    background-color: #f4f4f4; 
                    color: #232629; 
                    border: {dialog_border};
                    border-radius: 6px;
                }}
                QLabel {{ color: #232629; font-size: 14px; }}
                QLineEdit {{ 
                    background-color: #ffffff; 
                    color: #232629; 
                    border: 1px solid #bbb; 
                    border-radius: 4px; 
                    padding: 6px;
                    font-size: 14px;
                }}
                QPushButton {{ 
                    background-color: #f4f4f4; 
                    color: #232629; 
                    border: 1px solid #bbb; 
                    border-radius: 4px; 
                    padding: 6px 16px;
                    min-width: 80px;
                }}
                QPushButton:hover {{ background-color: #e0e0e0; }}
                QPushButton:pressed {{ background-color: #eaeaea; }}
            """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Add instruction label
        instruction = QLabel("Enter a descriptive name for this visual check point:")
        instruction.setWordWrap(True)
        layout.addWidget(instruction)
        
        # Add line edit for check name with default value
        from PyQt6.QtWidgets import QLineEdit
        line_edit = QLineEdit(f"Check_{len(self.action_editor.get_actions()) + 1}")
        line_edit.selectAll()  # Select all text for easy editing
        line_edit.setMinimumHeight(32)
        layout.addWidget(line_edit)
        
        # Add spacer
        layout.addSpacing(10)
        
        # Add buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.setMinimumHeight(32)
        cancel_button.setMinimumHeight(32)
        ok_button.setDefault(True)  # Make OK the default button (Enter key)
        
        # Connect buttons
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)
        
        # Center the dialog on the screen
        dialog.adjustSize()  # Make sure dialog is properly sized before centering
        center_point = QApplication.primaryScreen().availableGeometry().center()
        dialog_rect = dialog.frameGeometry()
        dialog_rect.moveCenter(center_point)
        dialog.move(dialog_rect.topLeft())
        
        # Set up focus and input focus
        line_edit.setFocus()  # Pre-set the focus to the line edit
        
        # Force dialog to the foreground
        dialog.setWindowState(dialog.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
        
        # Set up a timer to ensure dialog gets focus - important for external window activation
        def force_focus():
            dialog.activateWindow()
            dialog.raise_()
            line_edit.setFocus()
            
            # Windows-specific focus handling
            if try_windows_focus:
                try:
                    # Get dialog window handle
                    hwnd = int(dialog.winId())
                    print(f"DEBUG: Comment dialog window handle: {hwnd}")
                    
                    # Windows constants
                    HWND_TOPMOST = -1
                    HWND_NOTOPMOST = -2
                    SWP_NOSIZE = 0x0001
                    SWP_NOMOVE = 0x0002
                    
                    # Force window to top and give it focus
                    user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
                    user32.SetForegroundWindow(hwnd)
                    user32.SetFocus(hwnd)
                    user32.SetActiveWindow(hwnd)
                    
                    # Flash window in taskbar to get user attention
                    user32.FlashWindow(hwnd, True)
                    
                    print("DEBUG: Windows focus methods applied")
                except Exception as e:
                    print(f"DEBUG: Windows focus error: {e}")
                    traceback.print_exc()
        
        # Use multiple timers with different delays to handle race conditions with window managers
        print("DEBUG: Setting up focus timers")
        QTimer.singleShot(50, force_focus)
        QTimer.singleShot(150, force_focus)
        QTimer.singleShot(300, force_focus)
        QTimer.singleShot(600, force_focus)  # Add an extra longer timer
        
        # Short delay before showing dialog to let the system prepare
        # This helps with focus issues on some platforms
        print("DEBUG: Pre-show delay")
        time.sleep(0.2)  # Slightly longer delay than check dialog
        
        # Set up keyboard handling to improve focus
        def keyPressEvent(event):
            print(f"DEBUG: Dialog key press: {event.key()}")
            if event.key() == Qt.Key.Key_Escape:
                dialog.reject()
            elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                dialog.accept()
            else:
                # Pass other key events to line_edit if not already focused
                if not line_edit.hasFocus():
                    line_edit.setFocus()
                    # If it's a character key, set the text to that character
                    if event.text() and event.text().isprintable():
                        line_edit.setText(event.text())
                        line_edit.setCursorPosition(len(event.text()))
                
        # Install the key press handler
        dialog.keyPressEvent = keyPressEvent
        
        print("DEBUG: Showing comment dialog")
        # Show dialog and get result - exec() will block until dialog is closed
        result = dialog.exec()
        print(f"DEBUG: Dialog result: {result}")
        
        # Get the check name if OK was clicked
        if result == QDialog.DialogCode.Accepted:
            check_name = line_edit.text()
            ok = True
        else:
            check_name = ""
            ok = False
        
        # Resume recording if it was active before
        if was_recording:
            print("DEBUG: Resuming recording after check dialog")
            # Resume and make sure listeners are active
            self.session_manager.resume()
            self.update_pause_resume_button(paused=False)
            self.status_label.setText("Recording...")
            # Restart polling for events
            self._poll_actions()
        
        if not ok:
            # User canceled, but recording has already been resumed if needed
            return
        
        # Default name if user provided empty string
        if not check_name.strip():
            check_name = f"Check_{len(self.action_editor.get_actions()) + 1}"
            
        # Capture the active window
        img = ScreenshotUtil.capture_active_window()
        action = {
            'type': 'check',
            'check_type': 'image',
            'image': img,
            'timestamp': time.time() - (self.session_manager.listener.start_time or time.time()),
            'region': None,
            'check_name': check_name  # Store the user-provided name
        }
        actions = self.action_editor.get_actions()
        actions.append(action)
        self.action_editor.set_actions(actions)
        self.session_manager.listener.events = self.action_editor.get_actions()
        self.update_action_list()
        
        # Show confirmation in status bar with more detail
        self.status_label.setText(f"Visual check '{check_name}' added - Window size: {img.width}x{img.height}")
        # Also play a sound or show color flash to make feedback more noticeable
        self.error_status.setText(f"Visual check '{check_name}' added")
        self.error_status.setStyleSheet("color: #44AA44; font-weight: bold;")
        QTimer.singleShot(500, lambda: self.error_status.setText(""))
        QTimer.singleShot(3000, lambda: self.status_label.setText(
            "Recording..." if self.session_manager.state == 'recording' else 
            "Paused" if self.session_manager.state == 'paused' else "Stopped"))
            
    def on_visual_check_failed(self, ref_img, test_img):
        """Called from background thread when a visual check fails"""
        self.failed_check_images = (ref_img, test_img)
        # Emit signal to update UI in main thread
        self.signals.update_error_panel.emit(ref_img, test_img)
        
    def _on_update_error_panel(self, ref_img, test_img):
        """Slot connected to update_error_panel signal (runs in main thread)"""
        if ref_img is None or test_img is None:
            # Hide the panel if null images
            self.error_panel.hide()
            return
            
        # Make sure the continue event is reset so we wait for user input
        self.check_event.clear()
        
        # Restore window from minimized state when a check fails
        self.setWindowState(Qt.WindowState.WindowActive)
        self.activateWindow()
        self.raise_()
            
        # Convert PIL images to QPixmap for display
        ref_qimg = ImageQt.ImageQt(ref_img)
        test_qimg = ImageQt.ImageQt(test_img)
        
        ref_pixmap = QPixmap.fromImage(ref_qimg)
        test_pixmap = QPixmap.fromImage(test_qimg)
        
        # Scale pixmaps to fit in the labels while maintaining aspect ratio
        ref_pixmap = ref_pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio)
        test_pixmap = test_pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio)
        
        # Update the labels
        self.ref_image.setPixmap(ref_pixmap)
        self.test_image.setPixmap(test_pixmap)
        
        # Update status text with more details
        from utils.image_compare import images_are_similar
        mean_diff = 0
        try:
            # Calculate difference for display
            diff = ImageChops.difference(ref_img, test_img)
            stat = ImageStat.Stat(diff)
            mean_diff = sum(stat.mean) / len(stat.mean)
        except Exception:
            pass
            
        # Get tolerance level name and value
        tolerance_level = self.tolerance_combo.currentText()
        tolerance_value = self.get_tolerance_value()
            
        self.error_status.setText(
            f"Visual check failed! Images differ by {mean_diff:.2f} units (tolerance: {tolerance_level} ({tolerance_value})).\n"
            f"The current screen doesn't match what was expected."
        )
        self.error_status.setStyleSheet("color: #FF4444; font-weight: bold;")
        
        # Ensure continue and stop buttons are enabled
        self.continue_button.setEnabled(True)
        self.dont_continue_button.setEnabled(True)
        
        # Show the error panel
        self.error_panel.show()
    
    def _on_playback_finished(self, success):
        """Slot connected to playback_finished signal (runs in main thread)"""
        self.set_controls_state(True)
        
        # Restore window from minimized state
        self.setWindowState(Qt.WindowState.WindowActive)
        self.activateWindow()
        self.raise_()
        
        # Show popup with test results
        if success:
            QMessageBox.information(self, "Test Complete", "Playback completed successfully!")
            self.status_label.setText("Playback completed successfully")
        else:
            QMessageBox.warning(self, "Test Complete", "Playback completed with errors. Check the error panel for details.")
            self.status_label.setText("Playback completed with errors")
    
    def stop_after_error(self):
        """User clicked Stop Test button after an error"""
        # Disable both buttons to prevent multiple clicks
        self.continue_button.setEnabled(False)
        self.dont_continue_button.setEnabled(False)
        
        self.continue_after_fail = False
        self.error_panel.hide()
        self.check_event.set()  # Signal the waiting thread to continue but with stop flag set to false

    def continue_after_error(self):
        """User clicked Continue button after an error"""
        # Disable both buttons to prevent multiple clicks
        self.continue_button.setEnabled(False)
        self.dont_continue_button.setEnabled(False)
        
        self.continue_after_fail = True
        self.error_panel.hide()
        
        # Minimize the window before continuing 
        self.showMinimized()
        
        self.check_event.set()  # Signal the waiting thread to continue

    def test_check_failure(self):
        """Force a check failure to test the mechanism works properly"""
        # First check if there are any check actions
        has_check = False
        for action in self.action_editor.get_actions():
            if action['type'] == 'check' and action['check_type'] == 'image':
                has_check = True
                break
                
        if not has_check:
            # No check actions found, inform the user
            QMessageBox.information(
                self, 
                "No Check Actions", 
                "No visual check actions found. Add a check first using the 'Check' button or F7 key."
            )
            return
            
        # Prompt for confirmation
        response = QMessageBox.question(
            self,
            "Test Check Failure",
            "This will play back your actions with visual checks forced to fail.\n\n"
            "Use this to verify that your error handling works correctly.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if response == QMessageBox.StandardButton.No:
            return
            
        # Run playback with forced failure for checks
        def run_test_failure():
            try:
                result = True
                fail_info = None
                
                # Setup for playback
                self.signals.update_error_panel.emit(None, None)  # Clear error panel
                self.check_event.clear()  # Reset event
                self.continue_after_fail = False
                
                # Get all actions
                all_actions = self.action_editor.get_actions()
                start_index = 0
                
                while start_index < len(all_actions):
                    # Log what we're about to do for debugging
                    print(f"DEBUG: Starting test failure from index {start_index} (of {len(all_actions)} total)")
                    
                    # Create a slice of the actions from current position to the end
                    actions_slice = all_actions[start_index:]
                    if len(actions_slice) > 0:
                        next_action = actions_slice[0]
                        print(f"DEBUG: Next action type: {next_action.get('type', 'unknown')}")
                    
                    # Create a modified copy of the actions for testing,
                    # with force_fail set for all check actions
                    test_actions = []
                    for action in actions_slice:
                        action_copy = action.copy()
                        if action_copy['type'] == 'check' and action_copy['check_type'] == 'image':
                            # Add force_fail flag to check actions
                            action_copy['force_fail'] = True
                        test_actions.append(action_copy)
                    
                    # Run playback with the configured tolerance and test actions
                    tolerance = self.get_tolerance_value()
                    print(f"DEBUG: Submitting {len(test_actions)} actions to play_actions")
                    result, fail_info, last_action_index = play_actions(
                        test_actions, 
                        tolerance=tolerance, 
                        fail_callback=self.on_visual_check_failed,
                        start_index=0  # We're always starting from the beginning of test_actions
                    )
                    
                    # Adjust the index to be relative to the original list
                    actual_last_index = start_index + last_action_index
                    print(f"DEBUG: Test playback returned result={result}, last_action_index={last_action_index}, actual_last_index={actual_last_index}")
                    
                    # If playback failed due to visual check (which it should)
                    if not result and fail_info:
                        # Wait for user to decide whether to continue
                        print("DEBUG: Waiting for user decision on check failure")
                        self.check_event.wait()  # Wait until user makes a decision
                        print(f"DEBUG: User decided to {'continue' if self.continue_after_fail else 'stop'}")
                        
                        # If user chose to continue, restart playback from the next action
                        if self.continue_after_fail:
                            # Continue from the action after the one that failed
                            start_index = actual_last_index + 1
                            print(f"DEBUG: Continuing test from index {start_index}")
                            continue
                        else:
                            # User chose to stop
                            print("DEBUG: User chose to stop test playback")
                            break
                    
                    # If we got here, playback completed without errors
                    break
            except Exception as e:
                print(f"Test failure playback error: {e}")
                traceback.print_exc()  # Print full stack trace for better diagnosis
                result = False
            finally:
                # Signal that playback is finished
                self.signals.playback_finished.emit(result)
        
        # Clean up any existing thread
        if self.playback_thread and self.playback_thread.is_alive():
            self.check_event.set()  # Just in case it's waiting
            self.playback_thread.join(0.5)  # Wait a bit for it to end
        
        # Start new playback thread
        self.set_controls_state(False)
        
        # Minimize window before starting playback
        self.showMinimized()
        
        self.playback_thread = threading.Thread(target=run_test_failure, daemon=True)
        self.playback_thread.start()

    def resume_recording(self):
        """Resume recording after it was paused"""
        print("DEBUG: Manual resume requested")
        
        # Only resume if we're actually paused
        if self.session_manager.state == 'paused':
            self.session_manager.resume()
            self.status_label.setText("Recording...")
            self.update_pause_resume_button(paused=False)
            # Make sure polling is restarted
            self._poll_actions()

    def update_pause_resume_button(self, paused=True):
        if paused:
            self.pause_button.setText("Resume Recording (F9)")
            self.pause_button.clicked.disconnect()
            self.pause_button.clicked.connect(self.resume_recording)
        else:
            self.pause_button.setText("Pause Recording (F8)")
            self.pause_button.clicked.disconnect()
            self.pause_button.clicked.connect(self.pause_recording)

    def get_tolerance_value(self):
        """Convert the selected tolerance level to a numeric value"""
        index = self.tolerance_combo.currentIndex()
        if index == 0:  # Low
            return 3
        elif index == 1:  # Medium
            return 7
        elif index == 2:  # High
            return 10
        return 7  # Default to Medium

    def add_comment_action(self):
        """Called from the hotkey thread when F6 is pressed"""
        # Use signal to execute in the main thread
        self.signals.add_comment.emit()
        
    def _execute_add_comment(self):
        """Executes in the main thread via signal/slot mechanism"""
        # Store current recording state
        was_recording = self.session_manager.state == 'recording'
        current_state = self.session_manager.state
        
        print(f"DEBUG: Executing add comment. Current state: {current_state}")
        print(f"DEBUG: Window focus fix for comment dialog (F6) initiated")
        
        # Pause recording temporarily while showing the dialog
        if was_recording:
            print("DEBUG: Pausing recording for comment dialog")
            self.session_manager.pause()
            # Update the UI to show the paused state
            self.update_pause_resume_button(paused=True)
            
        # On Windows, prepare for better window focus handling
        try_windows_focus = False
        if sys.platform == 'win32':
            try:
                import ctypes
                user32 = ctypes.windll.user32
                # Remember the current foreground window so we can force focus later
                foreground_hwnd = user32.GetForegroundWindow()
                print(f"DEBUG: Current foreground window handle: {foreground_hwnd}")
                try_windows_focus = True
            except Exception as e:
                print(f"DEBUG: Windows focus utilities not available: {e}")
                traceback.print_exc()  # Print full stack trace for better diagnosis
                pass
        
        # Create a custom dialog that will stay on top of all windows
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
        from PyQt6.QtCore import Qt
        
        dialog = QDialog(None)  # Create with no parent to ensure it's a true top-level window
        dialog.setWindowTitle("Enter Your Comment")
        
        # Set strong always-on-top flags to ensure dialog is visible and gets focus
        dialog.setWindowFlags(
            Qt.WindowType.Window |  # Create as a window
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.MSWindowsFixedSizeDialogHint |  # Windows-specific flag for better focus
            Qt.WindowType.X11BypassWindowManagerHint |  # More forceful on Linux
            Qt.WindowType.Tool |  # Makes it a tool window which typically has higher z-order
            Qt.WindowType.FramelessWindowHint  # Remove frame for better focus
        )
        
        print(f"DEBUG: Comment dialog window flags: {dialog.windowFlags()}")
        
        dialog.setMinimumWidth(400)
        dialog.setModal(True)
        
        # Apply theme-appropriate styling with strong border for visibility
        dialog_border = "3px solid #FF9500"  # Orange border for visibility
        if self.is_dark:
            dialog.setStyleSheet(f"""
                QDialog {{ 
                    background-color: #232629; 
                    color: #f0f0f0; 
                    border: {dialog_border};
                    border-radius: 6px;
                }}
                QLabel {{ color: #f0f0f0; font-size: 14px; }}
                QLineEdit {{ 
                    background-color: #323639; 
                    color: #f0f0f0; 
                    border: 1px solid #444; 
                    border-radius: 4px; 
                    padding: 6px;
                    font-size: 14px;
                }}
                QPushButton {{ 
                    background-color: #323639; 
                    color: #f0f0f0; 
                    border: 1px solid #444; 
                    border-radius: 4px; 
                    padding: 6px 16px;
                    min-width: 80px;
                }}
                QPushButton:hover {{ background-color: #3a3f44; }}
                QPushButton:pressed {{ background-color: #232629; }}
            """)
        else:
            dialog.setStyleSheet(f"""
                QDialog {{ 
                    background-color: #f4f4f4; 
                    color: #232629; 
                    border: {dialog_border};
                    border-radius: 6px;
                }}
                QLabel {{ color: #232629; font-size: 14px; }}
                QLineEdit {{ 
                    background-color: #ffffff; 
                    color: #232629; 
                    border: 1px solid #bbb; 
                    border-radius: 4px; 
                    padding: 6px;
                    font-size: 14px;
                }}
                QPushButton {{ 
                    background-color: #f4f4f4; 
                    color: #232629; 
                    border: 1px solid #bbb; 
                    border-radius: 4px; 
                    padding: 6px 16px;
                    min-width: 80px;
                }}
                QPushButton:hover {{ background-color: #e0e0e0; }}
                QPushButton:pressed {{ background-color: #eaeaea; }}
            """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Add instruction label
        instruction = QLabel("Enter your comment:")
        instruction.setWordWrap(True)
        layout.addWidget(instruction)
        
        # Add line edit for comment with default value
        from PyQt6.QtWidgets import QLineEdit
        line_edit = QLineEdit(f"Comment_{len(self.action_editor.get_actions()) + 1}")
        line_edit.selectAll()  # Select all text for easy editing
        line_edit.setMinimumHeight(32)
        layout.addWidget(line_edit)
        
        # Add spacer
        layout.addSpacing(10)
        
        # Add buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.setMinimumHeight(32)
        cancel_button.setMinimumHeight(32)
        ok_button.setDefault(True)  # Make OK the default button (Enter key)
        
        # Connect buttons
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)
        
        # Center the dialog on the screen
        dialog.adjustSize()  # Make sure dialog is properly sized before centering
        center_point = QApplication.primaryScreen().availableGeometry().center()
        dialog_rect = dialog.frameGeometry()
        dialog_rect.moveCenter(center_point)
        dialog.move(dialog_rect.topLeft())
        
        # Set up focus and input focus
        line_edit.setFocus()  # Pre-set the focus to the line edit
        
        # Force dialog to the foreground
        dialog.setWindowState(dialog.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
        
        # Set up a timer to ensure dialog gets focus - important for external window activation
        def force_focus():
            try:
                print("DEBUG: Applying comment dialog focus")
                dialog.activateWindow()
                dialog.raise_()
                line_edit.setFocus()
                
                # Windows-specific focus handling
                if try_windows_focus and sys.platform == 'win32':
                    try:
                        # Get dialog window handle
                        hwnd = int(dialog.winId())
                        print(f"DEBUG: Comment dialog window handle: {hwnd}")
                        
                        # Windows constants
                        HWND_TOPMOST = -1
                        HWND_NOTOPMOST = -2
                        SWP_NOSIZE = 0x0001
                        SWP_NOMOVE = 0x0002
                        SWP_SHOWWINDOW = 0x0040
                        SWP_NOACTIVATE = 0x0010
                        
                        # Force window to top and give it focus - multiple techniques for redundancy
                        user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
                        user32.SetForegroundWindow(hwnd)
                        user32.SetFocus(hwnd)
                        user32.SetActiveWindow(hwnd)
                        
                        # Get current thread ID and foreground window thread ID
                        current_thread_id = user32.GetCurrentThreadId()
                        foreground_thread_id = user32.GetWindowThreadProcessId(user32.GetForegroundWindow(), None)
                        
                        # Attach our thread input to foreground to help with focus
                        if current_thread_id != foreground_thread_id:
                            user32.AttachThreadInput(current_thread_id, foreground_thread_id, True)
                            user32.SetForegroundWindow(hwnd)
                            user32.AttachThreadInput(current_thread_id, foreground_thread_id, False)
                            
                        # Flash window in taskbar to get user attention - use multiple flashes
                        user32.FlashWindow(hwnd, True)
                        
                        print("DEBUG: Windows focus methods applied for comment dialog")
                    except Exception as e:
                        print(f"DEBUG: Windows focus error: {e}")
                        traceback.print_exc()  # Print full stack trace for better diagnosis
            except Exception as e:
                print(f"DEBUG: Focus error: {e}")
                traceback.print_exc()  # Print full stack trace for better diagnosis
        
        # Use multiple timers with different delays to handle race conditions with window managers
        # Use more timing attempts with shorter initial delay
        print("DEBUG: Setting up comment dialog focus timers")
        QTimer.singleShot(20, force_focus)  # Try immediately
        QTimer.singleShot(50, force_focus)  # Try after short delay
        QTimer.singleShot(150, force_focus)
        QTimer.singleShot(300, force_focus)
        QTimer.singleShot(600, force_focus)  # Add an extra longer timer
        QTimer.singleShot(1000, force_focus)  # Add an extra very long timer as a fallback
        
        # Short delay before showing dialog to let the system prepare
        # This helps with focus issues on some platforms
        print("DEBUG: Pre-show delay for comment dialog")
        time.sleep(0.2)  # 200ms delay
        
        # Set up keyboard handling to improve focus
        def keyPressEvent(event):
            print(f"DEBUG: Comment dialog key press: {event.key()}")
            if event.key() == Qt.Key.Key_Escape:
                dialog.reject()
            elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                dialog.accept()
            else:
                # Pass other key events to line_edit if not already focused
                if not line_edit.hasFocus():
                    line_edit.setFocus()
                    # If it's a character key, set the text to that character
                    if event.text() and event.text().isprintable():
                        line_edit.setText(event.text())
                        line_edit.setCursorPosition(len(event.text()))
                
        # Install the key press handler
        dialog.keyPressEvent = keyPressEvent
        
        print("DEBUG: Showing comment dialog")
        # Show dialog and get result - exec() will block until dialog is closed
        result = dialog.exec()
        print(f"DEBUG: Comment dialog result: {result}")
        
        # Get the comment if OK was clicked
        if result == QDialog.DialogCode.Accepted:
            comment = line_edit.text()
            ok = True
        else:
            comment = ""
            ok = False
        
        # Resume recording if it was active before
        if was_recording:
            print("DEBUG: Resuming recording after comment dialog")
            # Resume and make sure listeners are active
            self.session_manager.resume()
            self.update_pause_resume_button(paused=False)
            self.status_label.setText("Recording...")
            # Restart polling for events
            self._poll_actions()
        
        if not ok:
            # User canceled, but recording has already been resumed if needed
            return
        
        # Default comment if user provided empty string
        if not comment.strip():
            comment = f"Comment_{len(self.action_editor.get_actions()) + 1}"
            
        # Capture the active window
        img = ScreenshotUtil.capture_active_window()
        action = {
            'type': 'comment',
            'comment': comment,
            'timestamp': time.time() - (self.session_manager.listener.start_time or time.time()),
            'region': None
        }
        actions = self.action_editor.get_actions()
        actions.append(action)
        self.action_editor.set_actions(actions)
        self.session_manager.listener.events = self.action_editor.get_actions()
        self.update_action_list()
        
        # Show confirmation in status bar with more detail
        self.status_label.setText(f"Comment '{comment}' added")
        # Also play a sound or show color flash to make feedback more noticeable
        self.error_status.setText(f"Comment '{comment}' added")
        self.error_status.setStyleSheet("color: #44AA44; font-weight: bold;")
        QTimer.singleShot(500, lambda: self.error_status.setText(""))
        QTimer.singleShot(3000, lambda: self.status_label.setText(
            "Recording..." if self.session_manager.state == 'recording' else 
            "Paused" if self.session_manager.state == 'paused' else "Stopped"))
            
    def get_session_state(self):
        """Return the current session state for hotkey manager"""
        return self.session_manager.state

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 