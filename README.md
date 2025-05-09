# Desktop Automation Recorder

A user-friendly desktop application to record and replay user interactions for automation and testing, using Python and PyAutoGUI.

## Features
- Record mouse and keyboard actions
- Element-based and image-based recording
- Edit, save, and replay sessions
- Export to runnable Python scripts

## Limitations
- **System/global shortcuts (e.g., ALT+TAB, WIN+R):**
  - These may be recorded, but cannot be reliably replayed due to operating system restrictions. PyAutoGUI and similar libraries cannot trigger system-level shortcuts during playback.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python main.py
   ```

## Project Structure
See code for details. 