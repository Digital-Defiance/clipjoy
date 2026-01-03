#!/bin/bash
# Notarize Kliply application bundle with Apple

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
APP_BUNDLE="$PROJECT_DIR/dist/Kliply.app"
ZIP_FILE="$PROJECT_DIR/dist/Kliply.zip"

echo "========================================="
echo "Notarizing Kliply"
echo "========================================="
echo ""

# Check if app bundle exists
if [ ! -d "$APP_BUNDLE" ]; then
    echo "✗ Application bundle not found: $APP_BUNDLE"
    echo ""
    echo "Please build and sign the application first:"
    echo "  bash scripts/build.sh"
    echo "  bash scripts/sign.sh"
    exit 1
fi

# Check if app is signed
if ! codesign --verify "$APP_BUNDLE" 2>/dev/null; then
    echo "✗ Application is not signed"
    echo ""
    echo "Please sign the application first:"
    echo "  bash scripts/sign.sh"
    exit 1
fi

# Get Apple ID credentials
if [ -z "$APPLE_ID" ]; then
    read -p "Enter your Apple ID email: " APPLE_ID
fi

if [ -z "$APPLE_ID_PASSWORD" ]; then
    echo ""
    echo "Note: Use an app-specific password, not your Apple ID password"
    echo "Generate one at: https://appleid.apple.com/account/manage"
    read -sp "Enter your app-specific password: " APPLE_ID_PASSWORD
    echo ""
fi

if [ -z "$TEAM_ID" ]; then
    echo ""
    read -p "Enter your Team ID (found in App Store Connect): " TEAM_ID
fi

# Create a zip file for notarization
echo ""
echo "→ Creating zip archive for notarization..."
cd "$PROJECT_DIR/dist"
rm -f "Kliply.zip"
ditto -c -k --keepParent "Kliply.app" "Kliply.zip"

# Submit for notarization
echo ""
echo "→ Submitting to Apple for notarization..."
echo "  This may take several minutes..."
echo ""

NOTARIZE_OUTPUT=$(xcrun notarytool submit "$ZIP_FILE" \
    --apple-id "$APPLE_ID" \
    --password "$APPLE_ID_PASSWORD" \
    --team-id "$TEAM_ID" \
    --wait)

echo "$NOTARIZE_OUTPUT"

# Check if notarization was successful
if echo "$NOTARIZE_OUTPUT" | grep -q "status: Accepted"; then
    echo ""
    echo "✓ Notarization successful!"
    
    # Staple the notarization ticket
    echo ""
    echo "→ Stapling notarization ticket..."
    xcrun stapler staple "$APP_BUNDLE"
    
    echo ""
    echo "========================================="
    echo "✓ Notarization complete!"
    echo "========================================="
    echo ""
    echo "The application is now notarized and ready for distribution."
    echo ""
    echo "To create a DMG:"
    echo "  bash scripts/create_dmg.sh"
else
    echo ""
    echo "✗ Notarization failed!"
    echo ""
    echo "To get more details, extract the submission ID from the output above and run:"
    echo "  xcrun notarytool log <submission-id> --apple-id $APPLE_ID --password <password> --team-id $TEAM_ID"
    exit 1
fi
