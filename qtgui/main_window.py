from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLabel, QStatusBar, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt
import sys

DARK_STYLE = """
QWidget {
    background-color: #232629;
    color: #f0f0f0;
}
QFrame#Sidebar {
    background-color: #181a1b;
}
QLabel#Header {
    color: #f0f0f0;
    font-size: 22px;
    font-weight: bold;
}
QPushButton {
    background-color: #323639;
    color: #f0f0f0;
    border: 1px solid #444;
    border-radius: 6px;
    padding: 8px 0;
}
QPushButton:hover {
    background-color: #3a3f44;
}
QPushButton:pressed {
    background-color: #232629;
}
QListWidget {
    background-color: #232629;
    color: #f0f0f0;
    border: 1px solid #444;
}
QStatusBar {
    background: #181a1b;
    color: #f0f0f0;
}
QLabel {
    color: #f0f0f0;
}
"""

LIGHT_STYLE = """
QWidget { background-color: #f4f4f4; color: #232629; }
QFrame#Sidebar { background-color: #eaeaea; }
QLabel#Header { color: #232629; font-size: 22px; font-weight: bold; }
QPushButton { background-color: #f4f4f4; color: #232629; border: 1px solid #bbb; border-radius: 6px; padding: 8px 0; }
QPushButton:hover { background-color: #e0e0e0; }
QPushButton:pressed { background-color: #eaeaea; }
QListWidget { background-color: #fff; color: #232629; border: 1px solid #bbb; }
QStatusBar { background: #eaeaea; color: #232629; }
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

        self.header = QLabel('Recorder')
        self.header.setObjectName('Header')
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(self.header)

        self.start_button = QPushButton('Start Recording')
        self.pause_button = QPushButton('Pause Recording')
        self.stop_button = QPushButton('Stop Recording')
        self.preview_button = QPushButton('Preview')
        self.save_button = QPushButton('Save')
        self.load_button = QPushButton('Load')
        self.export_script_button = QPushButton('Generate Script')
        for btn in [self.start_button, self.pause_button, self.stop_button, self.preview_button, self.save_button, self.load_button, self.export_script_button]:
            btn.setMinimumHeight(40)
            sidebar_layout.addWidget(btn)

        # Theme toggle button
        self.is_dark = True
        self.toggle_theme_button = QPushButton('☀️ Light Mode')
        self.toggle_theme_button.setMinimumHeight(40)
        self.toggle_theme_button.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(self.toggle_theme_button)

        # Main area
        main_area = QWidget()
        main_layout = QVBoxLayout()
        main_area.setLayout(main_layout)

        self.action_list = QListWidget()
        main_layout.addWidget(QLabel('Recorded Actions'))
        main_layout.addWidget(self.action_list)

        # Edit controls
        edit_controls = QHBoxLayout()
        self.delete_button = QPushButton('Delete')
        self.move_up_button = QPushButton('Move Up')
        self.move_down_button = QPushButton('Move Down')
        self.view_screenshot_button = QPushButton('View Screenshot')
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
        self.status.showMessage('Idle')

        # Apply dark mode stylesheet by default
        self.setStyleSheet(DARK_STYLE)

    def toggle_theme(self):
        if self.is_dark:
            self.setStyleSheet(LIGHT_STYLE)
            self.toggle_theme_button.setText('🌙 Dark Mode')
        else:
            self.setStyleSheet(DARK_STYLE)
            self.toggle_theme_button.setText('☀️ Light Mode')
        self.is_dark = not self.is_dark

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 