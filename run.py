import threading
from pynput import keyboard
from src.daemon import start_watcher
from src.ui import ClipboardUI

ui_manager = ClipboardUI()

def on_hotkey():
    threading.Thread(target=ui_manager.show, daemon=True).start()

# Cmd + Shift + V
hotkey_map = {'<cmd>+<shift>+v': on_hotkey}

# Start background watcher
threading.Thread(target=start_watcher, daemon=True).start()

print("🚀 Clipboard Pro is active!")
print("Shortcut: Cmd + Shift + V")

with keyboard.GlobalHotKeys(hotkey_map) as h:
    h.join()
