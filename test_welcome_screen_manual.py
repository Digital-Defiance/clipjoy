#!/usr/bin/env python3
"""
Manual test script for the Welcome Screen UI.

This script displays the welcome screen so you can visually verify
the design and functionality.
"""

import sys
from PyQt6.QtWidgets import QApplication

from src.Kliply.models import Settings
from src.Kliply.settings_manager import SettingsManager
from src.Kliply.history_manager import HistoryManager
from src.Kliply.ui_manager import UIManager
from src.Kliply.onboarding_manager import OnboardingManager


def main():
    """Run the manual test."""
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Create managers
    settings_manager = SettingsManager()
    history_manager = HistoryManager()
    ui_manager = UIManager(history_manager, settings_manager)
    onboarding_manager = OnboardingManager(settings_manager)
    
    # Wire up the managers
    onboarding_manager.set_ui_manager(ui_manager)
    ui_manager.set_onboarding_manager(onboarding_manager)
    
    # Show the welcome screen
    print("Displaying welcome screen...")
    print("Test the following:")
    print("  1. Visual design and layout")
    print("  2. 'Try It Now' button (should show history popup)")
    print("  3. 'Get Started' button (should close the dialog)")
    print("  4. 'Don't show this again' checkbox")
    print()
    
    result = ui_manager.show_welcome_screen()
    
    if result:
        print("User checked 'Don't show this again'")
        print(f"First launch complete: {settings_manager.get_settings().first_launch_complete}")
    else:
        print("User did not check 'Don't show this again'")
    
    sys.exit(0)


if __name__ == "__main__":
    main()
