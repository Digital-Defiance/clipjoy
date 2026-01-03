#!/bin/bash

# Script to help grant Accessibility permissions to Kliply

echo "========================================="
echo "Kliply Accessibility Permission Setup"
echo "========================================="
echo ""
echo "Kliply needs Accessibility permissions to register global hotkeys."
echo ""
echo "To grant permission:"
echo "1. Open System Settings (or System Preferences)"
echo "2. Go to Privacy & Security > Accessibility"
echo "3. Click the lock icon and enter your password"
echo "4. Click the '+' button"
echo "5. Navigate to: $(pwd)/dist/Kliply.app"
echo "6. Select Kliply.app and click 'Open'"
echo "7. Make sure the checkbox next to Kliply is enabled"
echo ""
echo "Opening System Settings now..."
echo ""

# Open System Settings to Accessibility
open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"

echo "After granting permission, restart Kliply for the hotkey to work."
