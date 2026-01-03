#!/bin/bash
# Generate .icns file from PNG for macOS application bundle

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RESOURCES_DIR="$SCRIPT_DIR/../resources"
ICON_PNG="$RESOURCES_DIR/icon.png"
ICON_ICNS="$RESOURCES_DIR/icon.icns"
ICONSET_DIR="$RESOURCES_DIR/icon.iconset"

# Check if source PNG exists
if [ ! -f "$ICON_PNG" ]; then
    echo "Error: icon.png not found in resources directory"
    echo "Please create a 1024x1024 PNG file at: $ICON_PNG"
    exit 1
fi

# Create iconset directory
mkdir -p "$ICONSET_DIR"

# Generate all required icon sizes
echo "Generating icon sizes..."
sips -z 16 16     "$ICON_PNG" --out "$ICONSET_DIR/icon_16x16.png" > /dev/null
sips -z 32 32     "$ICON_PNG" --out "$ICONSET_DIR/icon_16x16@2x.png" > /dev/null
sips -z 32 32     "$ICON_PNG" --out "$ICONSET_DIR/icon_32x32.png" > /dev/null
sips -z 64 64     "$ICON_PNG" --out "$ICONSET_DIR/icon_32x32@2x.png" > /dev/null
sips -z 128 128   "$ICON_PNG" --out "$ICONSET_DIR/icon_128x128.png" > /dev/null
sips -z 256 256   "$ICON_PNG" --out "$ICONSET_DIR/icon_128x128@2x.png" > /dev/null
sips -z 256 256   "$ICON_PNG" --out "$ICONSET_DIR/icon_256x256.png" > /dev/null
sips -z 512 512   "$ICON_PNG" --out "$ICONSET_DIR/icon_256x256@2x.png" > /dev/null
sips -z 512 512   "$ICON_PNG" --out "$ICONSET_DIR/icon_512x512.png" > /dev/null
sips -z 1024 1024 "$ICON_PNG" --out "$ICONSET_DIR/icon_512x512@2x.png" > /dev/null

# Convert iconset to icns
echo "Creating .icns file..."
iconutil -c icns "$ICONSET_DIR" -o "$ICON_ICNS"

# Clean up iconset directory
rm -rf "$ICONSET_DIR"

echo "✓ Icon generated successfully: $ICON_ICNS"
