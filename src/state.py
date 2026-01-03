clipboard_history = []
MAX_ITEMS = 20

def add_to_memory(text):
    global clipboard_history
    if text in clipboard_history:
        clipboard_history.remove(text)
    clipboard_history.insert(0, text)
    if len(clipboard_history) > MAX_ITEMS:
        clipboard_history = clipboard_history[:MAX_ITEMS]

def get_history():
    return clipboard_history
