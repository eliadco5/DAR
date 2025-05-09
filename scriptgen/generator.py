# Converts sessions to Python scripts
import base64
import string

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
    pressed_modifiers = set()
    i = 0
    while i < len(actions):
        action = actions[i]
        t = action.get('timestamp', 0)
        wait = t - last_time if t > last_time else 0
        if action['type'] == 'mouse' and action['event'] == 'move':
            move_count += 1
            if move_count % move_event_stride != 0:
                i += 1
                last_time = t
                continue
        else:
            move_count = 0
        if action['type'] == 'mouse' and action['event'] == 'move':
            pass
        elif wait >= 0.1:
            lines.append(f'time.sleep({wait:.3f})')
        # Modifier tracking
        if action['type'] == 'keyboard':
            key = action['key']
            if action['event'] == 'down' and key in {'ctrl', 'alt', 'shift'}:
                pressed_modifiers.add(key)
                i += 1
                last_time = t
                continue
            elif action['event'] == 'up' and key in {'ctrl', 'alt', 'shift'}:
                pressed_modifiers.discard(key)
                i += 1
                last_time = t
                continue
            # If keydown of non-modifier
            elif action['event'] == 'down' and key not in {'ctrl', 'alt', 'shift'}:
                if pressed_modifiers:
                    hotkey_args = ', '.join(repr(m) for m in sorted(pressed_modifiers)) + f', {repr(key)}'
                    lines.append(f'pyautogui.hotkey({hotkey_args})')
                    # skip the up event if present
                    if (i + 1 < len(actions)
                        and actions[i + 1]['type'] == 'keyboard'
                        and actions[i + 1]['event'] == 'up'
                        and actions[i + 1]['key'] == key):
                        i += 1
                else:
                    # Group printable key downs into write()
                    if isinstance(key, str) and len(key) == 1 and key in string.printable and key not in '\r\n\t':
                        text = ''
                        j = i
                        while (j < len(actions)
                               and actions[j]['type'] == 'keyboard'
                               and actions[j]['event'] == 'down'
                               and isinstance(actions[j]['key'], str)
                               and len(actions[j]['key']) == 1
                               and actions[j]['key'] in string.printable
                               and actions[j]['key'] not in '\r\n\t'):
                            text += actions[j]['key']
                            # skip the up event if present
                            if (j + 1 < len(actions)
                                and actions[j + 1]['type'] == 'keyboard'
                                and actions[j + 1]['event'] == 'up'
                                and actions[j + 1]['key'] == actions[j]['key']):
                                j += 2
                            else:
                                j += 1
                        if text:
                            lines.append(f'pyautogui.write({repr(text)})')
                            i = j
                            last_time = t
                            continue
                    # Use press for special keys
                    lines.append(f'pyautogui.press({repr(key)})')
                    # skip the up event if present
                    if (i + 1 < len(actions)
                        and actions[i + 1]['type'] == 'keyboard'
                        and actions[i + 1]['event'] == 'up'
                        and actions[i + 1]['key'] == key):
                        i += 1
        # Mouse click detection
        if action['type'] == 'mouse' and action['event'] == 'down':
            if (i + 1 < len(actions)
                and actions[i + 1]['type'] == 'mouse'
                and actions[i + 1]['event'] == 'up'
                and actions[i + 1]['x'] == action['x']
                and actions[i + 1]['y'] == action['y']):
                lines.append(f'pyautogui.click({action["x"]}, {action["y"]})')
                i += 2
                last_time = t
                continue
            else:
                lines.append(f'pyautogui.moveTo({action["x"]}, {action["y"]})')
                lines.append(f'pyautogui.mouseDown()')
        elif action['type'] == 'mouse' and action['event'] == 'up':
            lines.append(f'pyautogui.moveTo({action["x"]}, {action["y"]})')
            lines.append(f'pyautogui.mouseUp()')
        elif action['type'] == 'mouse' and action['event'] == 'move':
            lines.append(f'pyautogui.moveTo({action["x"]}, {action["y"]})')
        elif action['type'] == 'mouse' and action['event'] == 'scroll':
            lines.append(f'pyautogui.scroll({action["dy"]}, x={action["x"]}, y={action["y"]})')
        last_time = t
        i += 1
    return '\n'.join(lines)

class ScriptGenerator:
    def __init__(self):
        # TODO: Initialize script generator
        pass 