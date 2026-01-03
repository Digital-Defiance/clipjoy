#!/usr/bin/env python3
"""
Manual test script to visually verify the Settings Panel UI.

Run this script to see the settings panel in action.
"""

import sys
from PyQt6.QtWidgets import QApplication
from src.Kliply.history_manager import HistoryManager
from src.Kliply.settings_manager import SettingsManager
from src.Kliply.ui_manager import SettingsPanel

def main():
    """Run the settings panel for manual testing."""
    app = QApplication(sys.argv)
    
    # Create managers
    history_manager = HistoryManager(max_depth=10)
    settings_manager = SettingsManager()
    
    # Create and show settings panel
    panel = SettingsPanel(settings_manager, history_manager)
    
    print("Settings Panel opened!")
    print(f"Initial clipboard depth: {settings_manager.get_clipboard_depth()}")
    print(f"Initial hotkey: {settings_manager.get_hotkey()}")
    print(f"Initial launch at login: {settings_manager.get_launch_at_login()}")
    
    # Show the panel (blocking)
    result = panel.exec()
    
    print("\nSettings Panel closed!")
    print(f"Final clipboard depth: {settings_manager.get_clipboard_depth()}")
    print(f"Final hotkey: {settings_manager.get_hotkey()}")
    print(f"Final launch at login: {settings_manager.get_launch_at_login()}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
