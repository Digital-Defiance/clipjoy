#!/bin/bash
# Build Kliply macOS application bundle using py2app

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
BUILD_DIR="$PROJECT_DIR/build"
DIST_DIR="$PROJECT_DIR/dist"

echo "========================================="
echo "Building Kliply macOS Application"
echo "========================================="
echo ""

# Change to project directory
cd "$PROJECT_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "→ Activating virtual environment..."
    source venv/bin/activate
fi

# Check if py2app is installed
if ! python3 -c "import py2app" 2>/dev/null; then
    echo "✗ py2app not found. Installing..."
    pip3 install py2app>=0.28.0
fi

# Create placeholder icon if it doesn't exist
if [ ! -f "resources/icon.png" ]; then
    echo "→ Creating placeholder icon..."
    python3 scripts/create_placeholder_icon.py
fi

# Generate .icns file from PNG
if [ -f "resources/icon.png" ] && [ ! -f "resources/icon.icns" ]; then
    echo "→ Generating .icns file..."
    bash scripts/generate_icon.sh
fi

# Clean previous builds
echo "→ Cleaning previous builds..."
# For case-sensitive filesystems, we need to be more aggressive
if [ -d "$BUILD_DIR" ]; then
    # Remove attributes and make writable
    xattr -rc "$BUILD_DIR" 2>/dev/null || true
    chmod -R u+w "$BUILD_DIR" 2>/dev/null || true
    rm -rf "$BUILD_DIR" 2>/dev/null || true
    # If still exists, try harder
    if [ -d "$BUILD_DIR" ]; then
        find "$BUILD_DIR" -type f -exec chmod u+w {} \; 2>/dev/null || true
        rm -rf "$BUILD_DIR" || true
    fi
fi
if [ -d "$DIST_DIR" ]; then
    # Remove attributes and make writable
    xattr -rc "$DIST_DIR" 2>/dev/null || true
    chmod -R u+w "$DIST_DIR" 2>/dev/null || true
    rm -rf "$DIST_DIR" 2>/dev/null || true
    # If still exists, try harder
    if [ -d "$DIST_DIR" ]; then
        find "$DIST_DIR" -type f -exec chmod u+w {} \; 2>/dev/null || true
        rm -rf "$DIST_DIR" || true
    fi
fi

# Build the application
echo "→ Building application bundle..."
python3 setup.py py2app

# Check if build was successful
if [ -d "$DIST_DIR/Kliply.app" ]; then
    echo ""
    echo "========================================="
    echo "✓ Build successful!"
    echo "========================================="
    echo ""
    echo "Application bundle: $DIST_DIR/Kliply.app"
    echo ""
    echo "To test the application:"
    echo "  open $DIST_DIR/Kliply.app"
    echo ""
    echo "To create a DMG for distribution:"
    echo "  bash scripts/create_dmg.sh"
    echo ""
else
    echo ""
    echo "✗ Build failed!"
    exit 1
fi
