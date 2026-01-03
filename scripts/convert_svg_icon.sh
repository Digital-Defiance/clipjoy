#!/bin/bash
# Convert SVG icon to PNG and .icns for macOS application bundle

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RESOURCES_DIR="$SCRIPT_DIR/../resources"

# Check for input SVG file
if [ -z "$1" ]; then
    echo "Usage: $0 <path-to-icon.svg>"
    echo ""
    echo "This script converts an SVG icon to:"
    echo "  - icon.png (1024x1024)"
    echo "  - icon.icns (macOS icon bundle)"
    exit 1
fi

SVG_FILE="$1"

if [ ! -f "$SVG_FILE" ]; then
    echo "Error: SVG file not found: $SVG_FILE"
    exit 1
fi

ICON_PNG="$RESOURCES_DIR/icon.png"

# Try to use rsvg-convert first, fall back to Python script
if command -v rsvg-convert &> /dev/null; then
    echo "→ Converting SVG to PNG using rsvg-convert (1024x1024)..."
    rsvg-convert -w 1024 -h 1024 "$SVG_FILE" -o "$ICON_PNG"
else
    echo "→ rsvg-convert not found, using Python converter..."
    echo "→ Converting SVG to PNG (1024x1024)..."
    python3 "$SCRIPT_DIR/convert_svg_to_png.py" "$SVG_FILE" "$ICON_PNG" 1024
fi

if [ ! -f "$ICON_PNG" ]; then
    echo "✗ Failed to convert SVG to PNG"
    exit 1
fi

echo "✓ PNG created: $ICON_PNG"

# Generate .icns file
echo "→ Generating .icns file..."
bash "$SCRIPT_DIR/generate_icon.sh"

echo ""
echo "✓ Icon conversion complete!"
echo ""
echo "Files created:"
echo "  - $ICON_PNG"
echo "  - $RESOURCES_DIR/icon.icns"
