#!/bin/bash

# Script 1: Build the macOS app bundle
# This compiles the app and creates a .app bundle

set -e  # Exit on error

echo "======================================"
echo "Building Kliply.app"
echo "======================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Clean previous builds
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -rf .build/release
rm -rf build/
mkdir -p build

# Build for release
echo -e "${YELLOW}Building universal binary...${NC}"

# Build for arm64 (Apple Silicon)
echo -e "${YELLOW}  - Building for arm64...${NC}"
swift build -c release --arch arm64

# Build for x86_64 (Intel)
echo -e "${YELLOW}  - Building for x86_64...${NC}"
swift build -c release --arch x86_64

# Create universal binary with lipo
echo -e "${YELLOW}  - Combining architectures...${NC}"
mkdir -p .build/universal
lipo -create \
    .build/arm64-apple-macosx/release/Kliply \
    .build/x86_64-apple-macosx/release/Kliply \
    -output .build/universal/Kliply

echo -e "${GREEN}✓ Universal binary created${NC}"

# Create app bundle structure
echo -e "${YELLOW}Creating app bundle structure...${NC}"
APP_NAME="Kliply"
APP_BUNDLE="build/${APP_NAME}.app"
CONTENTS="${APP_BUNDLE}/Contents"
MACOS="${CONTENTS}/MacOS"
RESOURCES="${CONTENTS}/Resources"

mkdir -p "${MACOS}"
mkdir -p "${RESOURCES}"

# Copy executable
echo -e "${YELLOW}Copying executable...${NC}"
cp .build/release/${APP_NAME} "${MACOS}/"

# Copy Info.plist
echo -e "${YELLOW}Copying Info.plist...${NC}"
cp Sources/Kliply/Info.plist "${CONTENTS}/"

# Copy icon if exists
if [ -f "Sources/Kliply/Resources/Assets.xcassets/AppIcon.appiconset/icon_512x512.png" ]; then
    echo -e "${YELLOW}Creating app icon...${NC}"
    # Create .icns from PNG
    ICONSET="${APP_NAME}.iconset"
    mkdir -p "${ICONSET}"
    
    # Copy all icon sizes with proper naming for iconutil
    cp "Sources/Kliply/Resources/Assets.xcassets/AppIcon.appiconset/icon_16x16.png" "${ICONSET}/icon_16x16.png"
    cp "Sources/Kliply/Resources/Assets.xcassets/AppIcon.appiconset/icon_16x16@2x.png" "${ICONSET}/icon_16x16@2x.png"
    cp "Sources/Kliply/Resources/Assets.xcassets/AppIcon.appiconset/icon_32x32.png" "${ICONSET}/icon_32x32.png"
    cp "Sources/Kliply/Resources/Assets.xcassets/AppIcon.appiconset/icon_32x32@2x.png" "${ICONSET}/icon_32x32@2x.png"
    cp "Sources/Kliply/Resources/Assets.xcassets/AppIcon.appiconset/icon_128x128.png" "${ICONSET}/icon_128x128.png"
    cp "Sources/Kliply/Resources/Assets.xcassets/AppIcon.appiconset/icon_128x128@2x.png" "${ICONSET}/icon_128x128@2x.png"
    cp "Sources/Kliply/Resources/Assets.xcassets/AppIcon.appiconset/icon_256x256.png" "${ICONSET}/icon_256x256.png"
    cp "Sources/Kliply/Resources/Assets.xcassets/AppIcon.appiconset/icon_256x256@2x.png" "${ICONSET}/icon_256x256@2x.png"
    cp "Sources/Kliply/Resources/Assets.xcassets/AppIcon.appiconset/icon_512x512.png" "${ICONSET}/icon_512x512.png"
    cp "Sources/Kliply/Resources/Assets.xcassets/AppIcon.appiconset/icon_512x512@2x.png" "${ICONSET}/icon_512x512@2x.png"
    
    # Convert to icns
    iconutil -c icns "${ICONSET}" -o "${RESOURCES}/${APP_NAME}.icns"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Icon created successfully${NC}"
    else
        echo -e "${RED}✗ Icon creation failed${NC}"
    fi
    
    rm -rf "${ICONSET}"
else
    echo -e "${YELLOW}Warning: Icon files not found, skipping icon creation${NC}"
fi

# Set executable permissions
chmod +x "${MACOS}/${APP_NAME}"

echo -e "${GREEN}✓ App bundle created successfully at: ${APP_BUNDLE}${NC}"
echo ""
echo "Next steps:"
echo "  1. Run ./scripts/2-sign-app.sh to code sign"
echo "  2. Run ./scripts/3-notarize-app.sh to notarize"
echo "  3. Run ./scripts/4-create-dmg.sh to create installer"
