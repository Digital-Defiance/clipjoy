#!/bin/bash
set -e

# Script 5: Build for Mac App Store
# Uses Xcode project for proper App Store submission

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================"
echo "Building Kliply for Mac App Store"
echo "======================================"

# Configuration
APP_NAME="Kliply"
BUNDLE_ID="com.kliply"
XCODE_PROJECT="Kliply.xcodeproj"

# Paths
BUILD_DIR="./build"
ARCHIVE_PATH="$BUILD_DIR/${APP_NAME}.xcarchive"
EXPORT_PATH="$BUILD_DIR/export"

# Check for required environment variables
if [ -z "$APPLE_TEAM_ID" ]; then
    echo -e "${RED}Error: APPLE_TEAM_ID environment variable not set${NC}"
    echo "Set it with: export APPLE_TEAM_ID='YOUR_TEAM_ID'"
    echo "Find your Team ID at: https://developer.apple.com/account"
    exit 1
fi

# Check for Xcode project
if [ ! -d "$XCODE_PROJECT" ]; then
    echo -e "${RED}Error: Xcode project not found at ${XCODE_PROJECT}${NC}"
    echo "The Xcode project is required for App Store submission."
    exit 1
fi

# Check for provisioning profile
PROFILE_DIR="$HOME/Library/MobileDevice/Provisioning Profiles"
if [ ! -d "$PROFILE_DIR" ] || [ -z "$(ls -A "$PROFILE_DIR" 2>/dev/null)" ]; then
    echo -e "${RED}Error: No provisioning profiles found${NC}"
    echo ""
    echo "To create a Mac App Store provisioning profile:"
    echo "  1. Go to https://developer.apple.com/account/resources/profiles/list"
    echo "  2. Click '+' to create a new profile"
    echo "  3. Select 'Mac App Store Connect' under Distribution"
    echo "  4. Select your App ID (${BUNDLE_ID})"
    echo "  5. Select your '3rd Party Mac Developer Application' certificate"
    echo "  6. Download and double-click to install"
    exit 1
fi

# Find App Store certificates
echo -e "${YELLOW}Finding App Store certificates...${NC}"
APP_CERTS=$(security find-identity -v -p codesigning | grep "3rd Party Mac Developer Application" | sed 's/^[[:space:]]*[0-9]*)//g' | awk '!seen[$1]++')
INSTALLER_CERTS=$(security find-identity -v | grep "3rd Party Mac Developer Installer" | sed 's/^[[:space:]]*[0-9]*)//g' | awk '!seen[$1]++')

if [ -z "$APP_CERTS" ]; then
    echo -e "${RED}Error: No '3rd Party Mac Developer Application' certificate found${NC}"
    echo ""
    echo "Available certificates:"
    security find-identity -v -p codesigning
    echo ""
    echo "To get App Store certificates:"
    echo "  1. Go to https://developer.apple.com/account/resources/certificates/list"
    echo "  2. Click '+' to create a new certificate"
    echo "  3. Under 'Software', select 'Mac App Distribution'"
    echo "  4. Upload a Certificate Signing Request (CSR)"
    echo "  5. Download and install the certificate"
    echo ""
    echo "  Repeat for 'Mac Installer Distribution' certificate"
    exit 1
fi

if [ -z "$INSTALLER_CERTS" ]; then
    echo -e "${RED}Error: No '3rd Party Mac Developer Installer' certificate found${NC}"
    echo ""
    echo "To get a certificate:"
    echo "  1. Go to https://developer.apple.com/account/resources/certificates/list"
    echo "  2. Click '+' to create a new certificate"
    echo "  3. Under 'Software', select 'Mac Installer Distribution'"
    echo "  4. Upload a Certificate Signing Request (CSR)"
    echo "  5. Download and install the certificate"
    exit 1
fi

echo ""
echo "Available App certificates (duplicates removed):"
echo "$APP_CERTS" | nl -w2 -s') '
echo ""

# Count certificates
APP_CERT_COUNT=$(echo "$APP_CERTS" | wc -l | tr -d ' ')

if [ "$APP_CERT_COUNT" -eq 1 ]; then
    APP_CERT_NAME=$(echo "$APP_CERTS" | grep -o '"[^"]*"' | tr -d '"')
    echo -e "${GREEN}Using App certificate: ${APP_CERT_NAME}${NC}"
else
    echo "Multiple App certificates found."
    read -p "Enter number for App certificate (1-$APP_CERT_COUNT): " CHOICE
    
    if ! [[ "$CHOICE" =~ ^[0-9]+$ ]] || [ "$CHOICE" -lt 1 ] || [ "$CHOICE" -gt "$APP_CERT_COUNT" ]; then
        echo -e "${RED}Invalid choice${NC}"
        exit 1
    fi
    
    APP_CERT_NAME=$(echo "$APP_CERTS" | sed -n "${CHOICE}p" | grep -o '"[^"]*"' | tr -d '"')
    echo -e "${GREEN}Selected App certificate: ${APP_CERT_NAME}${NC}"
fi

echo ""

# Step 1: Clean build directory
echo -e "${GREEN}Step 1: Clean build directory...${NC}"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Step 2: Archive with xcodebuild
echo -e "${GREEN}Step 2: Building archive with xcodebuild...${NC}"
xcodebuild -project "$XCODE_PROJECT" \
    -scheme "$APP_NAME" \
    -configuration Release \
    -archivePath "$ARCHIVE_PATH" \
    archive \
    CODE_SIGN_IDENTITY="$APP_CERT_NAME" \
    CODE_SIGN_STYLE=Manual \
    DEVELOPMENT_TEAM="$APPLE_TEAM_ID" \
    | grep -E "(Signing Identity|ARCHIVE SUCCEEDED|ARCHIVE FAILED|error:|warning:)" || true

# Verify archive was created
if [ ! -d "$ARCHIVE_PATH" ]; then
    echo -e "${RED}Error: Archive creation failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Archive created successfully${NC}"

# Step 3: Find provisioning profile name
echo -e "${GREEN}Step 3: Finding provisioning profile...${NC}"
PROFILE_NAME=""
for profile in "$PROFILE_DIR"/*.provisionprofile; do
    if [ -f "$profile" ]; then
        # Extract the profile name
        PROFILE_NAME=$(security cms -D -i "$profile" 2>/dev/null | plutil -extract Name raw - 2>/dev/null || basename "$profile" .provisionprofile)
        if security cms -D -i "$profile" 2>/dev/null | grep -q "$BUNDLE_ID"; then
            echo -e "${GREEN}Found matching profile: ${PROFILE_NAME}${NC}"
            break
        fi
    fi
done

if [ -z "$PROFILE_NAME" ]; then
    PROFILE_NAME="Kliply"
    echo -e "${YELLOW}Warning: Could not find matching profile, using default name: ${PROFILE_NAME}${NC}"
fi

# Step 4: Create ExportOptions.plist
echo -e "${GREEN}Step 4: Creating ExportOptions.plist...${NC}"
cat > "$BUILD_DIR/ExportOptions.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>destination</key>
    <string>export</string>
    <key>method</key>
    <string>app-store-connect</string>
    <key>signingStyle</key>
    <string>manual</string>
    <key>teamID</key>
    <string>${APPLE_TEAM_ID}</string>
    <key>uploadSymbols</key>
    <true/>
    <key>signingCertificate</key>
    <string>3rd Party Mac Developer Application</string>
    <key>installerSigningCertificate</key>
    <string>3rd Party Mac Developer Installer</string>
    <key>provisioningProfiles</key>
    <dict>
        <key>${BUNDLE_ID}</key>
        <string>${PROFILE_NAME}</string>
    </dict>
</dict>
</plist>
EOF

# Step 5: Export archive
echo -e "${GREEN}Step 5: Exporting for App Store...${NC}"
xcodebuild -exportArchive \
    -archivePath "$ARCHIVE_PATH" \
    -exportPath "$EXPORT_PATH" \
    -exportOptionsPlist "$BUILD_DIR/ExportOptions.plist" \
    2>&1 | grep -E "(Exported|EXPORT SUCCEEDED|EXPORT FAILED|error:)" || true

# Verify export succeeded
if [ ! -f "$EXPORT_PATH/${APP_NAME}.pkg" ]; then
    echo -e "${RED}Error: Export failed${NC}"
    echo "Check the logs at: /var/folders/*/Kliply_*.xcdistributionlogs"
    exit 1
fi

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}✓ App Store build complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Package location: $EXPORT_PATH/${APP_NAME}.pkg"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Open the Transporter app (download from Mac App Store if needed)"
echo "2. Sign in with your Apple ID"
echo "3. Drag and drop: $EXPORT_PATH/${APP_NAME}.pkg"
echo "4. Click 'Deliver'"
echo ""
echo "Or upload via command line:"
echo "  xcrun altool --upload-app -f \"$EXPORT_PATH/${APP_NAME}.pkg\" \\"
echo "    -t macos --apiKey YOUR_API_KEY --apiIssuer YOUR_ISSUER_ID"
echo ""
echo "After upload, go to App Store Connect to submit for review."
