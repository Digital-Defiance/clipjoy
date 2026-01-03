#!/bin/bash
# Install Kliply to /Applications

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
DIST_APP="$PROJECT_DIR/dist/Kliply.app"
INSTALL_PATH="/Applications/Kliply.app"

echo "========================================="
echo "Installing Kliply to /Applications"
echo "========================================="
echo ""

# Check if built app exists
if [ ! -d "$DIST_APP" ]; then
    echo "✗ Kliply.app not found in dist/"
    echo "  Please run ./scripts/build.sh first"
    exit 1
fi

# Kill any running instances (more aggressive)
echo "→ Stopping any running instances..."
pkill -9 -f Kliply 2>/dev/null || true
killall -9 Kliply 2>/dev/null || true
killall -9 python 2>/dev/null || true
sleep 2

# Remove existing installation
if [ -d "$INSTALL_PATH" ]; then
    echo "→ Removing existing installation..."
    rm -rf "$INSTALL_PATH"
    
    # Reset Accessibility permissions to avoid stale signature issues (multiple attempts)
    echo "→ Resetting Accessibility permissions..."
    tccutil reset Accessibility com.Kliply.app 2>/dev/null || true
    tccutil reset All com.Kliply.app 2>/dev/null || true
    
    # Give macOS more time to process the permission reset
    sleep 2
fi

# Copy app to /Applications
echo "→ Copying Kliply.app to /Applications..."
cp -R "$DIST_APP" "$INSTALL_PATH"

# Clear any quarantine attributes
echo "→ Clearing quarantine attributes..."
xattr -cr "$INSTALL_PATH" 2>/dev/null || true

# Try to open System Settings for manual permission reset
echo "→ Opening Accessibility settings for manual permission reset..."
open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility" 2>/dev/null || true

echo ""
echo "========================================="
echo "✓ Installation complete!"
echo "========================================="
echo ""
echo "Kliply installed to: $INSTALL_PATH"
echo ""
echo "⚠️  IMPORTANT: Manual permission reset required"
echo ""
echo "Due to code signature changes, you need to manually reset permissions:"
echo ""
echo "1. Open: System Settings → Privacy & Security → Accessibility"
echo "2. Find 'Kliply' in the list (if present)"
echo "3. Click the (-) button to REMOVE it"
echo "4. Click 'Done'"
echo "5. Launch Kliply and grant permissions when prompted"
echo ""
echo "Or run: open \"x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility\""
echo ""
echo "To launch the application:"
echo "  open /Applications/Kliply.app"
echo ""
