# Replays actions with timing and error handling
import pyautogui
import time

def play_actions(actions, move_event_stride=5):
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
        except Exception as e:
            print(f"Playback error at action {i}: {e}")
        last_time = t

class Player:
    def __init__(self):
        # TODO: Initialize player
        pass 