#!/bin/bash

# Script 2: Code sign the app bundle
# Requires: Apple Developer ID certificate installed in Keychain

set -e

echo "======================================"
echo "Code Signing Kliply.app"
echo "======================================"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

APP_BUNDLE="build/Kliply.app"

if [ ! -d "${APP_BUNDLE}" ]; then
    echo -e "${RED}Error: App bundle not found at ${APP_BUNDLE}${NC}"
    echo "Run ./scripts/1-build-app.sh first"
    exit 1
fi

# Find Developer ID certificate
echo -e "${YELLOW}Finding Developer ID certificates...${NC}"
CERTS=$(security find-identity -v -p codesigning | grep "Developer ID Application" | awk '!seen[$2]++' | sed 's/^[[:space:]]*[0-9]*)//')

if [ -z "$CERTS" ]; then
    echo -e "${RED}Error: No Developer ID Application certificate found${NC}"
    echo ""
    echo "Available certificates:"
    security find-identity -v -p codesigning
    echo ""
    echo "To get a certificate:"
    echo "  1. Go to https://developer.apple.com/account/resources/certificates/list"
    echo "  2. Create a 'Developer ID Application' certificate"
    echo "  3. Download and install it"
    exit 1
fi

echo ""
echo "Available Developer ID certificates (duplicates removed):"
echo "$CERTS" | nl -w2 -s') '
echo ""

# Count certificates
CERT_COUNT=$(echo "$CERTS" | wc -l | tr -d ' ')

if [ "$CERT_COUNT" -eq 1 ]; then
    CERT=$(echo "$CERTS" | awk '{print $1}')
    CERT_NAME=$(echo "$CERTS" | grep -o '"[^"]*"' | tr -d '"')
    echo -e "${GREEN}Using: ${CERT_NAME}${NC}"
else
    echo "Multiple certificates found."
    echo "If one fails with 'key not found', try the other one."
    echo ""
    read -p "Enter number (1-$CERT_COUNT): " CHOICE
    
    if ! [[ "$CHOICE" =~ ^[0-9]+$ ]] || [ "$CHOICE" -lt 1 ] || [ "$CHOICE" -gt "$CERT_COUNT" ]; then
        echo -e "${RED}Invalid choice${NC}"
        exit 1
    fi
    
    # Extract the SHA-1 hash (first field) instead of the name
    CERT=$(echo "$CERTS" | sed -n "${CHOICE}p" | awk '{print $1}')
    CERT_NAME=$(echo "$CERTS" | sed -n "${CHOICE}p" | grep -o '"[^"]*"' | tr -d '"')
    echo -e "${GREEN}Selected: ${CERT_NAME}${NC}"
    echo -e "${GREEN}Using hash: ${CERT}${NC}"
fi

# Sign the app with hardened runtime
echo -e "${YELLOW}Signing app bundle...${NC}"
codesign --force --options runtime --deep --sign "$CERT" "${APP_BUNDLE}"

# Verify signature
echo -e "${YELLOW}Verifying signature...${NC}"
codesign --verify --deep --strict --verbose=2 "${APP_BUNDLE}"

echo -e "${GREEN}✓ App signed successfully${NC}"
echo ""
echo "Next step:"
echo "  Run ./scripts/3-notarize-app.sh to notarize with Apple"
