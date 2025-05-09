# Save/load sessions (custom format or script)
import json
import base64
from io import BytesIO
from PIL import Image

def encode_image(img):
    if img is None:
        return None
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def decode_image(data):
    if data is None:
        return None
    buffer = BytesIO(base64.b64decode(data))
    return Image.open(buffer)

def save_actions(filepath, actions):
    serializable = []
    for action in actions:
        action_copy = action.copy()
        if 'screenshot' in action_copy and action_copy['screenshot'] is not None:
            action_copy['screenshot'] = encode_image(action_copy['screenshot'])
        serializable.append(action_copy)
    with open(filepath, 'w') as f:
        json.dump(serializable, f)

def load_actions(filepath):
    with open(filepath, 'r') as f:
        actions = json.load(f)
    for action in actions:
        if 'screenshot' in action and action['screenshot'] is not None:
            action['screenshot'] = decode_image(action['screenshot'])
    return actions

class SaveLoad:
    def __init__(self):
        # TODO: Initialize save/load functionality
        pass 