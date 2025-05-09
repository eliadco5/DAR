# Replays actions with timing and error handling
import pyautogui
import time
from utils.image_compare import images_are_similar
from recorder.screenshot import ScreenshotUtil

def play_actions(actions, move_event_stride=5, tolerance=15, fail_callback=None):
    last_time = 0
    move_count = 0
    for i, action in enumerate(actions):
        t = action.get('timestamp', 0)
        wait = t - last_time if t > last_time else 0
        if action['type'] == 'mouse' and action['event'] == 'move':
            move_count += 1
            if move_count % move_event_stride != 0:
                continue
        else:
            move_count = 0
        if action['type'] == 'mouse' and action['event'] == 'move':
            pass  # No sleep before move events
        elif wait >= 0.1:
            time.sleep(wait)
        try:
            if action['type'] == 'mouse':
                if action['event'] == 'move':
                    pyautogui.moveTo(action['x'], action['y'])
                elif action['event'] == 'down':
                    # Visual assertion: compare screenshot if present
                    if 'screenshot' in action and action['screenshot'] is not None:
                        x, y = action['x'], action['y']
                        ref_img = action['screenshot']
                        test_img = ScreenshotUtil.capture_region(x, y, ref_img.width, ref_img.height)
                        if not images_are_similar(ref_img, test_img, tolerance=tolerance):
                            print(f"[ERROR] Visual check failed at click ({x}, {y}) - screenshot does not match.")
                            if fail_callback:
                                fail_callback(ref_img, test_img)
                            return False, (ref_img, test_img)
                    pyautogui.moveTo(action['x'], action['y'])
                    pyautogui.mouseDown()
                elif action['event'] == 'up':
                    pyautogui.moveTo(action['x'], action['y'])
                    pyautogui.mouseUp()
                elif action['event'] == 'scroll':
                    pyautogui.scroll(action['dy'], x=action['x'], y=action['y'])
            elif action['type'] == 'keyboard':
                key = action.get('key', '').replace("'", "")
                if action['event'] == 'down':
                    pyautogui.keyDown(key)
                elif action['event'] == 'up':
                    pyautogui.keyUp(key)
            elif action['type'] == 'check' and action['check_type'] == 'image':
                # Handle manual check actions
                if 'image' in action and action['image'] is not None:
                    ref_img = action['image']
                    # For manual checks, we need to capture the same region as the reference image
                    if action['region'] is not None:
                        # If region is specified, use it
                        x, y, w, h = action['region']
                        test_img = ScreenshotUtil.capture_region(x, y, w, h)
                    else:
                        # Otherwise capture the active window as we did during recording
                        test_img = ScreenshotUtil.capture_active_window()
                        # Resize test image to match reference image dimensions
                        if test_img.size != ref_img.size:
                            test_img = test_img.resize(ref_img.size)
                    
                    if not images_are_similar(ref_img, test_img, tolerance=tolerance):
                        print(f"[ERROR] Manual visual check failed - screenshot does not match.")
                        if fail_callback:
                            fail_callback(ref_img, test_img)
                        return False, (ref_img, test_img)
        except Exception as e:
            print(f"Playback error at action {i}: {e}")
            return False, None
        last_time = t
    return True, None

class Player:
    def __init__(self):
        # TODO: Initialize player
        pass 