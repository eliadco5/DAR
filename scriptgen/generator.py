# Converts sessions to Python scripts
import base64
import string

def pyautogui_key_name(key):
    if isinstance(key, str) and key.startswith('Key.'):
        return key[4:]
    return key

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
    emitted_modifiers = set()
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
        # Modifier tracking and keyDown/keyUp
        if action['type'] == 'keyboard':
            key = action['key']
            if action['event'] == 'down' and key in {'ctrl', 'alt', 'shift'}:
                pressed_modifiers.add(key)
                if key not in emitted_modifiers:
                    lines.append(f'pyautogui.keyDown({repr(pyautogui_key_name(key))})')
                    emitted_modifiers.add(key)
                i += 1
                last_time = t
                continue
            elif action['event'] == 'up' and key in {'ctrl', 'alt', 'shift'}:
                pressed_modifiers.discard(key)
                if key in emitted_modifiers:
                    lines.append(f'pyautogui.keyUp({repr(pyautogui_key_name(key))})')
                    emitted_modifiers.remove(key)
                i += 1
                last_time = t
                continue
            # If keydown of non-modifier
            elif action['event'] == 'down' and key not in {'ctrl', 'alt', 'shift'}:
                # If any modifiers are held, they are already down
                lines.append(f'pyautogui.press({repr(pyautogui_key_name(key))})')
                # skip the up event if present
                if (i + 1 < len(actions)
                    and actions[i + 1]['type'] == 'keyboard'
                    and actions[i + 1]['event'] == 'up'
                    and actions[i + 1]['key'] == key):
                    i += 1
                # No continue here, allow grouping of printable keys below if no modifiers
        # Group printable key downs into write() if no modifiers are held
        if (action['type'] == 'keyboard' and action['event'] == 'down' and not pressed_modifiers
            and isinstance(action['key'], str) and len(action['key']) == 1 and action['key'] in string.printable and action['key'] not in '\r\n\t'):
            text = ''
            j = i
            while (j < len(actions)
                   and actions[j]['type'] == 'keyboard'
                   and actions[j]['event'] == 'down'
                   and not pressed_modifiers
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
    # Release any modifiers still held at the end
    for mod in list(emitted_modifiers):
        lines.append(f'pyautogui.keyUp({repr(pyautogui_key_name(mod))})')
    return '\n'.join(lines)

class ScriptGenerator:
    def __init__(self):
        # TODO: Initialize script generator
        pass 