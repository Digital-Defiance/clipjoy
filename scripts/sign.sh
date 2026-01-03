#!/bin/bash
# Code sign Kliply application bundle for macOS distribution

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
APP_BUNDLE="$PROJECT_DIR/dist/Kliply.app"
ENTITLEMENTS="$PROJECT_DIR/resources/entitlements.plist"

echo "========================================="
echo "Code Signing Kliply"
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

# Check if entitlements file exists
if [ ! -f "$ENTITLEMENTS" ]; then
    echo "✗ Entitlements file not found: $ENTITLEMENTS"
    exit 1
fi

# Get signing identity
if [ -z "$SIGNING_IDENTITY" ]; then
    echo "Available signing identities:"
    security find-identity -v -p codesigning
    echo ""
    read -p "Enter your Developer ID Application identity: " SIGNING_IDENTITY
fi

if [ -z "$SIGNING_IDENTITY" ]; then
    echo "✗ No signing identity provided"
    exit 1
fi

echo "→ Signing with identity: $SIGNING_IDENTITY"
echo ""

# Remove dangling symlinks that would cause Gatekeeper rejections
echo "→ Cleaning dangling symlinks..."
dangling_count=0
while IFS= read -r -d '' link; do
    relative="${link#${APP_BUNDLE}/}"
    echo "  Removing broken link: $relative"
    rm -f "$link"
    ((dangling_count++)) || true
done < <(find "$APP_BUNDLE" -type l ! -exec test -e {} \; -print0)
if [ "$dangling_count" -eq 0 ]; then
    echo "  (none found)"
fi

# Helper to sign a single binary and surface failures immediately
sign_binary() {
    local target="$1"
    echo "  Signing: ${target#${APP_BUNDLE}/}"
    codesign --force --sign "$SIGNING_IDENTITY" \
        --options runtime \
        --timestamp \
        "$target"
}

# Sign all embedded Mach-O binaries before the bundle itself
echo "→ Signing embedded frameworks and resources..."

# Sign framework bundles (codesign expects the directory)
while IFS= read -r -d '' framework; do
    sign_binary "$framework"
done < <(find "$APP_BUNDLE/Contents/Frameworks" -maxdepth 1 -type d -name "*.framework" -print0)

# Sign individual Mach-O binaries (dylib/so/executables)
while IFS= read -r -d '' file; do
    sign_binary "$file"
done < <(find "$APP_BUNDLE/Contents" \
    -type f \
    \( -name "*.dylib" -o -name "*.so" -o -perm -u+x \) \
    -print0)

# Sign the main application bundle
echo ""
echo "→ Signing main application bundle..."
codesign --force --sign "$SIGNING_IDENTITY" \
    --entitlements "$ENTITLEMENTS" \
    --options runtime \
    --timestamp \
    --deep \
    "$APP_BUNDLE"

# Verify the signature
echo ""
echo "→ Verifying signature..."
codesign --verify --deep --strict --verbose=2 "$APP_BUNDLE"

echo ""
echo "========================================="
echo "✓ Code signing complete!"
echo "========================================="
echo ""
echo "To notarize the application:"
echo "  bash scripts/notarize.sh"
