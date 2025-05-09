# Converts sessions to Python scripts
import base64
import string
import os
from PIL import Image
import shutil

def pyautogui_key_name(key):
    if isinstance(key, str) and key.startswith('Key.'):
        return key[4:]
    return key

def save_screenshots(actions, script_path):
    """Save screenshots from actions to a folder next to the script"""
    # Create screenshots directory
    script_dir = os.path.dirname(os.path.abspath(script_path))
    screenshots_dir = os.path.join(script_dir, 'screenshots')
    
    # Ensure empty screenshots directory exists
    if os.path.exists(screenshots_dir):
        shutil.rmtree(screenshots_dir)
    os.makedirs(screenshots_dir)
    
    # Track which actions have screenshots
    screenshot_map = {}
    
    # Save screenshots
    for i, action in enumerate(actions):
        if action['type'] == 'mouse' and action['event'] == 'down' and 'screenshot' in action and action['screenshot'] is not None:
            screenshot_path = os.path.join(screenshots_dir, f'screenshot_{i}.png')
            action['screenshot'].save(screenshot_path)
            screenshot_map[i] = screenshot_path
        elif action['type'] == 'check' and action['check_type'] == 'image' and 'image' in action and action['image'] is not None:
            screenshot_path = os.path.join(screenshots_dir, f'check_{i}.png')
            action['image'].save(screenshot_path)
            screenshot_map[i] = screenshot_path
    
    return screenshot_map

def generate_script(actions, move_event_stride=5, output_path=None):
    screenshot_map = {}
    if output_path:
        screenshot_map = save_screenshots(actions, output_path)
    
    # Add imports and helper functions
    lines = [
        'import pyautogui',
        'import time',
        'import os',
        'from PIL import Image, ImageChops, ImageStat',
        '',
        'pyautogui.FAILSAFE = True',
        '',
        '# Visual verification settings',
        'TOLERANCE = 15  # Adjust as needed',
        'VERIFICATION_ENABLED = True  # Set to False to disable visual verification',
        '',
        'def images_are_similar(img1, img2, tolerance=TOLERANCE):',
        '    """Compare two images and return True if they are similar within tolerance"""',
        '    if img1.size != img2.size:',
        '        return False',
        '    diff = ImageChops.difference(img1, img2)',
        '    stat = ImageStat.Stat(diff)',
        '    mean_diff = sum(stat.mean) / len(stat.mean)',
        '    return mean_diff <= tolerance',
        '',
        'def verify_screenshot(ref_img_path, x, y, width=100, height=100):',
        '    """Verify the current screen matches reference screenshot"""',
        '    if not VERIFICATION_ENABLED or not os.path.exists(ref_img_path):',
        '        return True  # Skip verification if disabled or image missing',
        '    ref_img = Image.open(ref_img_path)',
        '    left = max(x - width // 2, 0)',
        '    top = max(y - height // 2, 0)',
        '    test_img = pyautogui.screenshot(region=(left, top, width, height))',
        '    if not images_are_similar(ref_img, test_img):',
        '        print(f"[ERROR] Visual check failed at ({x}, {y}) - screenshot does not match.")',
        '        if input("Continue anyway? (y/n): ").lower() != "y":',
        '            raise Exception("Visual verification failed")',
        '    return True',
        '',
        'def verify_window_screenshot(ref_img_path):',
        '    """Verify the current active window matches reference screenshot"""',
        '    if not VERIFICATION_ENABLED or not os.path.exists(ref_img_path):',
        '        return True  # Skip verification if disabled or image missing',
        '    ref_img = Image.open(ref_img_path)',
        '    ',
        '    # Capture active window',
        '    try:',
        '        import ctypes',
        '        hwnd = ctypes.windll.user32.GetForegroundWindow()',
        '        rect = ctypes.wintypes.RECT()',
        '        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))',
        '        width = rect.right - rect.left',
        '        height = rect.bottom - rect.top',
        '        test_img = pyautogui.screenshot(region=(rect.left, rect.top, width, height))',
        '    except Exception:',
        '        # Fallback to full screen',
        '        test_img = pyautogui.screenshot()',
        '    ',
        '    # Resize test image to match reference if needed',
        '    if test_img.size != ref_img.size:',
        '        test_img = test_img.resize(ref_img.size)',
        '    ',
        '    if not images_are_similar(ref_img, test_img):',
        '        print(f"[ERROR] Window visual check failed - screenshot does not match.")',
        '        if input("Continue anyway? (y/n): ").lower() != "y":',
        '            raise Exception("Visual verification failed")',
        '    return True',
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
            # Check if we have a screenshot for this action
            has_screenshot = i in screenshot_map

            if (i + 1 < len(actions)
                and actions[i + 1]['type'] == 'mouse'
                and actions[i + 1]['event'] == 'up'
                and actions[i + 1]['x'] == action['x']
                and actions[i + 1]['y'] == action['y']):
                # Complete click (down + up)
                if has_screenshot:
                    screenshot_path = screenshot_map[i]
                    rel_path = os.path.join('screenshots', os.path.basename(screenshot_path))
                    # Add visual verification before click
                    lines.append(f'verify_screenshot(os.path.join(os.path.dirname(__file__), {repr(rel_path)}), {action["x"]}, {action["y"]})')
                lines.append(f'pyautogui.click({action["x"]}, {action["y"]})')
                i += 2
                last_time = t
                continue
            else:
                # Just mouse down
                if has_screenshot:
                    screenshot_path = screenshot_map[i]
                    rel_path = os.path.join('screenshots', os.path.basename(screenshot_path))
                    # Add visual verification before mouse down
                    lines.append(f'verify_screenshot(os.path.join(os.path.dirname(__file__), {repr(rel_path)}), {action["x"]}, {action["y"]})')
                lines.append(f'pyautogui.moveTo({action["x"]}, {action["y"]})')
                lines.append(f'pyautogui.mouseDown()')
        elif action['type'] == 'mouse' and action['event'] == 'up':
            lines.append(f'pyautogui.moveTo({action["x"]}, {action["y"]})')
            lines.append(f'pyautogui.mouseUp()')
        elif action['type'] == 'mouse' and action['event'] == 'move':
            lines.append(f'pyautogui.moveTo({action["x"]}, {action["y"]})')
        elif action['type'] == 'mouse' and action['event'] == 'scroll':
            lines.append(f'pyautogui.scroll({action["dy"]}, x={action["x"]}, y={action["y"]})')
        # Handle manual check actions
        elif action['type'] == 'check' and action['check_type'] == 'image':
            if i in screenshot_map:
                screenshot_path = screenshot_map[i]
                rel_path = os.path.join('screenshots', os.path.basename(screenshot_path))
                # Add visual verification for the check point
                lines.append(f'print("Performing manual visual check...")')
                lines.append(f'verify_window_screenshot(os.path.join(os.path.dirname(__file__), {repr(rel_path)}))')
                lines.append(f'print("Visual check passed!")')
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