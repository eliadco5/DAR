# Replays actions with timing and error handling
import pyautogui
import time
from utils.image_compare import images_are_similar
from recorder.screenshot import ScreenshotUtil
import logging
from PIL import Image, ImageChops, ImageStat

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Player")

def play_actions(actions, move_event_stride=5, tolerance=15, fail_callback=None, start_index=0):
    print(f"DEBUG: play_actions called with start_index={start_index}, total actions={len(actions)}")
    last_time = 0
    move_count = 0
    
    # If we're starting from the middle, adjust the timing
    if start_index > 0 and start_index < len(actions):
        # Get the timestamp of the previous action for timing purposes
        prev_index = start_index - 1
        while prev_index >= 0:
            if 'timestamp' in actions[prev_index]:
                last_time = actions[prev_index].get('timestamp', 0)
                print(f"DEBUG: Using timestamp {last_time} from action at index {prev_index}")
                break
            prev_index -= 1
    
    # Track the actual index in the original action list for proper reporting
    original_action_index = start_index
    
    for i in range(0, len(actions)):  # Always start at 0 for the provided actions
        action = actions[i]
        original_action_index = start_index + i  # Track position in original list if caller is using a subset
        
        # Log action type for debugging
        action_type = action.get('type', 'unknown')
        print(f"DEBUG: Processing action {i} (original index {original_action_index}): type={action_type}")
        
        if action_type == 'mouse':
            event_type = action.get('event', 'unknown')
            logger.info(f"Playing action {i+1}/{len(actions)}: {action_type} {event_type}")
        elif action_type == 'check':
            logger.info(f"Playing action {i+1}/{len(actions)}: VISUAL CHECK")
            print(f"\n[VISUAL CHECK] Verifying the active window matches recorded screenshot...")
        else:
            logger.info(f"Playing action {i+1}/{len(actions)}: {action_type}")
            
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
            print(f"DEBUG: Waiting {wait:.2f} seconds before action {i}")
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
                            logger.error(f"Visual check failed at mouse click ({x}, {y})")
                            if fail_callback:
                                fail_callback(ref_img, test_img)
                            print(f"DEBUG: Returning from play_actions due to failed mouse check at index {i} (original {original_action_index})")
                            return False, (ref_img, test_img), original_action_index
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
                # Handle manual check actions (F7 hotkey)
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
                        
                        # Debug window sizes
                        logger.info(f"Reference image size: {ref_img.size}, Test image size: {test_img.size}")
                        
                        # Resize test image to match reference image dimensions
                        if test_img.size != ref_img.size:
                            logger.info(f"Resizing test image from {test_img.size} to {ref_img.size}")
                            test_img = test_img.resize(ref_img.size)
                    
                    # Calculate difference manually for additional verification
                    diff = ImageChops.difference(ref_img, test_img)
                    stat = ImageStat.Stat(diff)
                    mean_diff = sum(stat.mean) / len(stat.mean)
                    
                    # Check if test is forced to fail (for testing purposes)
                    force_fail = action.get('force_fail', False)
                    if force_fail:
                        logger.warning("Force fail flag detected in check action - forcing failure for testing")
                        print(f"[WARNING] Test mode: Forcing visual check to fail for testing purposes.")
                    
                    # Compare images with tolerance
                    result = images_are_similar(ref_img, test_img, tolerance=tolerance, force_fail=force_fail)
                    
                    # Log result with detailed metrics
                    logger.info(f"Visual check comparison: difference={mean_diff:.2f}, tolerance={tolerance}, passed={result}")
                    
                    if result:
                        print(f"[SUCCESS] Visual check passed! Window appears as expected.")
                        print(f"[INFO] Image difference: {mean_diff:.2f}, Tolerance: {tolerance}")
                        logger.info(f"Visual check passed")
                    else:
                        print(f"[ERROR] Visual check FAILED - Window appearance has changed.")
                        print(f"[ERROR] Image difference: {mean_diff:.2f}, Tolerance: {tolerance}")
                        print(f"[ERROR] Difference exceeds acceptable threshold.")
                        logger.error(f"Visual check failed: difference={mean_diff:.2f}, tolerance={tolerance}")
                        if fail_callback:
                            fail_callback(ref_img, test_img)
                        print(f"DEBUG: Returning from play_actions due to failed visual check at index {i} (original {original_action_index})")
                        return False, (ref_img, test_img), original_action_index
                else:
                    logger.warning(f"Check action at index {i} has no image data")
        except Exception as e:
            print(f"Playback error at action {i}: {e}")
            logger.exception(f"Playback error at action {i}")
            return False, None, original_action_index
        last_time = t
    
    # Return the last index in the original action list
    final_index = start_index + len(actions) - 1
    print(f"DEBUG: Playback completed successfully, final index = {final_index}")
    logger.info("Playback completed successfully")
    return True, None, final_index

class Player:
    def __init__(self):
        # TODO: Initialize player
        pass 