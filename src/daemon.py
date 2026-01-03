import pyperclip
import time
from .state import add_to_memory

def start_watcher():
    last_clip = ""
    while True:
        try:
            current_clip = pyperclip.paste()
            if current_clip != last_clip and current_clip.strip():
                add_to_memory(current_clip)
                last_clip = current_clip
        except Exception:
            pass
        time.sleep(0.5)
