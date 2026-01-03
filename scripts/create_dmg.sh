#!/bin/bash
# Create a DMG installer for Kliply

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
APP_BUNDLE="$PROJECT_DIR/dist/Kliply.app"
DMG_FILE="$PROJECT_DIR/dist/Kliply-1.0.0.dmg"
TEMP_DMG="$PROJECT_DIR/dist/temp.dmg"
VOLUME_NAME="Kliply"

echo "========================================="
echo "Creating Kliply DMG Installer"
echo "========================================="
echo ""

# Check if app bundle exists
if [ ! -d "$APP_BUNDLE" ]; then
    echo "✗ Application bundle not found: $APP_BUNDLE"
    echo ""
    echo "Please build the application first:"
    echo "  bash scripts/build.sh"
    exit 1
fi

# Calculate DMG size dynamically with generous headroom unless overridden
APP_SIZE_KB=$(du -sk "$APP_BUNDLE" | awk '{print $1}')
APP_SIZE_MB=$(awk "BEGIN {printf \"%.2f\", $APP_SIZE_KB/1024}")

if [ -n "$DMG_SIZE_KB" ]; then
    VOLUME_SIZE_KB=$DMG_SIZE_KB
    echo "→ Using DMG size override: ${VOLUME_SIZE_KB}k"
else
    HEADROOM_KB=$((APP_SIZE_KB * 2))
    PADDING_KB=$((1024 * 1024))
    VOLUME_SIZE_KB=$((APP_SIZE_KB + HEADROOM_KB + PADDING_KB))
fi

VOLUME_SIZE="${VOLUME_SIZE_KB}k"
echo "→ Calculated DMG size: $VOLUME_SIZE (app size ${APP_SIZE_MB} MB)"

# Remove existing DMG files
rm -f "$DMG_FILE" "$TEMP_DMG"

# Create a temporary DMG
echo "→ Creating temporary disk image..."
hdiutil create -size "$VOLUME_SIZE" -fs HFS+ -volname "$VOLUME_NAME" "$TEMP_DMG"

# Mount the temporary DMG
echo "→ Mounting disk image..."
MOUNT_DIR=$(hdiutil attach "$TEMP_DMG" | grep "/Volumes/$VOLUME_NAME" | awk '{print $3}')

if [ -z "$MOUNT_DIR" ]; then
    echo "✗ Failed to mount disk image"
    exit 1
fi

echo "  Mounted at: $MOUNT_DIR"

# Copy the application to the DMG
echo "→ Copying application to disk image..."
cp -R "$APP_BUNDLE" "$MOUNT_DIR/"

# Create a symbolic link to /Applications
echo "→ Creating Applications symlink..."
ln -s /Applications "$MOUNT_DIR/Applications"

# Create a README file
echo "→ Creating README..."
cat > "$MOUNT_DIR/README.txt" << 'EOF'
Kliply - Professional macOS Clipboard Manager
===============================================

Installation Instructions:
1. Drag Kliply.app to the Applications folder
2. Launch Kliply from your Applications folder
3. Follow the on-screen instructions to grant necessary permissions

Features:
- Clipboard history management
- Quick access via Cmd+Shift+V
- Support for text, rich text, and images
- Configurable history depth (5-100 items)

For more information, visit: https://digital-defiance.github.io/Kliply/

Copyright © 2026 Kliply Team
EOF

# Set custom icon and background (if available)
if [ -f "$PROJECT_DIR/resources/dmg_background.png" ]; then
    echo "→ Setting DMG background..."
    mkdir -p "$MOUNT_DIR/.background"
    cp "$PROJECT_DIR/resources/dmg_background.png" "$MOUNT_DIR/.background/"
fi

# Set DMG window properties using AppleScript
echo "→ Configuring DMG window..."
osascript << EOF
tell application "Finder"
    tell disk "$VOLUME_NAME"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {100, 100, 700, 500}
        set viewOptions to the icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 128
        set position of item "Kliply.app" of container window to {150, 200}
        set position of item "Applications" of container window to {450, 200}
        set position of item "README.txt" of container window to {300, 350}
        close
        open
        update without registering applications
        delay 2
    end tell
end tell
EOF

# Unmount the temporary DMG
echo "→ Unmounting disk image..."
hdiutil detach "$MOUNT_DIR"

# Convert to compressed, read-only DMG
echo "→ Converting to final DMG..."
hdiutil convert "$TEMP_DMG" -format UDZO -o "$DMG_FILE"

# Remove temporary DMG
rm -f "$TEMP_DMG"

# Sign the DMG if signing identity is available
if [ ! -z "$SIGNING_IDENTITY" ]; then
    echo "→ Signing DMG..."
    codesign --sign "$SIGNING_IDENTITY" "$DMG_FILE"
fi

echo ""
echo "========================================="
echo "✓ DMG created successfully!"
echo "========================================="
echo ""
echo "DMG file: $DMG_FILE"
echo ""
echo "To test the installer:"
echo "  open $DMG_FILE"
echo ""
echo "To distribute:"
echo "  1. Test installation on a clean macOS system"
echo "  2. Verify code signature and notarization"
echo "  3. Upload to your distribution channel"
