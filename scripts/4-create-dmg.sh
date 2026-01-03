#!/bin/bash

# Script 4: Create a DMG installer
# Creates a nice disk image for distribution

set -e

echo "======================================"
echo "Creating Kliply.dmg"
echo "======================================"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

APP_BUNDLE="build/Kliply.app"
DMG_NAME="Kliply"
DMG_FILE="build/${DMG_NAME}.dmg"
VOLUME_NAME="Kliply"
DMG_TEMP="build/dmg_temp"

if [ ! -d "${APP_BUNDLE}" ]; then
    echo -e "${RED}Error: App bundle not found${NC}"
    echo "Run previous scripts first"
    exit 1
fi

# Clean up old DMG
echo -e "${YELLOW}Cleaning up old DMG...${NC}"
rm -f "${DMG_FILE}"
rm -rf "${DMG_TEMP}"
rm -f build/pack.temp.dmg

# Create temporary DMG folder
echo -e "${YELLOW}Creating DMG structure...${NC}"
mkdir -p "${DMG_TEMP}"
cp -R "${APP_BUNDLE}" "${DMG_TEMP}/"

# Create symlink to Applications folder
ln -s /Applications "${DMG_TEMP}/Applications"

# Create a README
cat > "${DMG_TEMP}/README.txt" << EOF
Kliply - Clipboard Manager for macOS

INSTALLATION:
1. Drag Kliply.app to the Applications folder
2. Open Kliply from Applications
3. Grant accessibility permissions when prompted
4. Use Cmd+Shift+V to open clipboard history

USAGE:
- Cmd+Shift+V: Open clipboard history
- Click menu bar icon: Access menu
- Cmd+, (when popup open): Open settings

For more information, visit:
https://github.com/Digital-Defiance/kliply

License: MIT
© 2026 Digital Defiance, Jessica Mulein
EOF

# Calculate size
SIZE=$(du -sk "${DMG_TEMP}" | cut -f1)
SIZE=$((SIZE * 15 / 10))  # Add 50% padding

# Minimum 10MB
if [ $SIZE -lt 10240 ]; then
    SIZE=10240
fi

# Create DMG
echo -e "${YELLOW}Creating DMG image...${NC}"
hdiutil create -srcfolder "${DMG_TEMP}" \
    -volname "${VOLUME_NAME}" \
    -fs HFS+ \
    -fsargs "-c c=64,a=16,e=16" \
    -format UDRW \
    -size ${SIZE}k \
    "build/pack.temp.dmg"

# Mount it
echo -e "${YELLOW}Mounting DMG for customization...${NC}"
DEVICE=$(hdiutil attach -readwrite -noverify "build/pack.temp.dmg" | \
    egrep '^/dev/' | sed 1q | awk '{print $1}')

sleep 2

# Customize appearance with AppleScript
echo -e "${YELLOW}Customizing DMG appearance...${NC}"
echo '
   tell application "Finder"
     tell disk "'${VOLUME_NAME}'"
           open
           set current view of container window to icon view
           set toolbar visible of container window to false
           set statusbar visible of container window to false
           set the bounds of container window to {400, 100, 920, 440}
           set viewOptions to the icon view options of container window
           set arrangement of viewOptions to not arranged
           set icon size of viewOptions to 72
           set position of item "Kliply.app" of container window to {130, 150}
           set position of item "Applications" of container window to {390, 150}
           close
           open
           update without registering applications
           delay 2
     end tell
   end tell
' | osascript || true

sleep 2

# Unmount
echo -e "${YELLOW}Finalizing DMG...${NC}"
sync
hdiutil detach "${DEVICE}" || true

# Convert to compressed read-only
hdiutil convert "build/pack.temp.dmg" \
    -format UDZO \
    -imagekey zlib-level=9 \
    -o "${DMG_FILE}"

# Clean up
rm -f "build/pack.temp.dmg"
rm -rf "${DMG_TEMP}"

# Sign the DMG if certificate available
if security find-identity -v -p codesigning | grep -q "Developer ID Application"; then
    echo -e "${YELLOW}Signing DMG...${NC}"
    # Get unique certificates and use the first one's hash
    CERT=$(security find-identity -v -p codesigning | grep "Developer ID Application" | awk '!seen[$2]++' | head -1 | awk '{print $2}')
    codesign --force --sign "$CERT" "${DMG_FILE}"
fi

echo -e "${GREEN}✓ DMG created successfully: ${DMG_FILE}${NC}"
echo ""
echo "Distribution file ready!"
echo "  Size: $(du -h "${DMG_FILE}" | cut -f1)"
echo ""
echo "You can now distribute ${DMG_FILE} to users."
