# Converts sessions to Python scripts
import base64

def generate_script(actions, move_event_stride=5):
    lines = [
        'import pyautogui',
        'import time',
        '',
        'pyautogui.FAILSAFE = True',
        '',
        'time.sleep(2)  # Wait before starting',
    ]
    last_time = 0
    move_count = 0
    for i, action in enumerate(actions):
        t = action.get('timestamp', 0)
        wait = t - last_time if t > last_time else 0
        # Only insert sleep if not a move event and wait >= 0.1s
        if action['type'] == 'mouse' and action['event'] == 'move':
            move_count += 1
            if move_count % move_event_stride != 0:
                continue  # Skip this move event
        else:
            move_count = 0  # Reset on non-move event
        if action['type'] == 'mouse' and action['event'] == 'move':
            pass  # No sleep before move events
        elif wait >= 0.1:
            lines.append(f'time.sleep({wait:.3f})')
        if action['type'] == 'mouse':
            if action['event'] == 'move':
                lines.append(f'pyautogui.moveTo({action["x"]}, {action["y"]})')
            elif action['event'] == 'down':
                lines.append(f'pyautogui.moveTo({action["x"]}, {action["y"]})')
                lines.append(f'pyautogui.mouseDown()')
            elif action['event'] == 'up':
                lines.append(f'pyautogui.moveTo({action["x"]}, {action["y"]})')
                lines.append(f'pyautogui.mouseUp()')
            elif action['event'] == 'scroll':
                lines.append(f'pyautogui.scroll({action["dy"]}, x={action["x"]}, y={action["y"]})')
        elif action['type'] == 'keyboard':
            key = action.get('key', '').replace("'", "")
            if action['event'] == 'down':
                lines.append(f'pyautogui.keyDown({repr(key)})')
            elif action['event'] == 'up':
                lines.append(f'pyautogui.keyUp({repr(key)})')
        last_time = t
    return '\n'.join(lines)

class ScriptGenerator:
    def __init__(self):
        # TODO: Initialize script generator
        pass 