import tkinter as tk
import pyperclip
from .state import get_history

class ClipboardUI:
    def __init__(self):
        self.root = None

    def show(self):
        if self.root and self.root.winfo_exists():
            return
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#1e1e1e")
        
        w, h = 400, 350
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        frame = tk.Frame(self.root, bg="#1e1e1e", highlightbackground="#444", highlightthickness=1)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="📋 CLIPBOARD HISTORY", bg="#1e1e1e", fg="#888", font=("Arial", 10, "bold")).pack(pady=10)

        listbox = tk.Listbox(frame, bg="#1e1e1e", fg="#eee", font=("Menlo", 11), 
                            borderwidth=0, highlightthickness=0, selectbackground="#007AFF", activestyle='none')
        listbox.pack(fill="both", expand=True, padx=15, pady=5)

        items = get_history()
        for item in items:
            listbox.insert(tk.END, f" {item.replace('\n', ' ')[:50]}")

        def select_item(event=None):
            selection = listbox.curselection()
            if selection:
                pyperclip.copy(items[selection[0]])
                self.root.destroy()

        listbox.bind('<Double-Button-1>', select_item)
        listbox.bind('<Return>', select_item)
        self.root.bind("<FocusOut>", lambda e: self.root.destroy())
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.mainloop()
