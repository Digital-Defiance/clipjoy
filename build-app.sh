#!/bin/bash
set -e

echo "Building Kliply.app..."

# Build release binary
swift build -c release

# Create app bundle structure
APP_DIR="Kliply.app"
rm -rf "$APP_DIR"
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

# Copy binary
cp .build/release/Kliply "$APP_DIR/Contents/MacOS/Kliply"

# Copy icon if available
if [ -f "Sources/Kliply/Resources/Assets.xcassets/AppIcon.appiconset/icon_512x512.png" ]; then
    cp "Sources/Kliply/Resources/Assets.xcassets/AppIcon.appiconset/icon_512x512.png" "$APP_DIR/Contents/Resources/AppIcon.icns"
fi

# Create Info.plist
cat > "$APP_DIR/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>Kliply</string>
    <key>CFBundleExecutable</key>
    <string>Kliply</string>
    <key>CFBundleIdentifier</key>
    <string>com.kliply</string>
    <key>CFBundleName</key>
    <string>Kliply</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.5</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>14.0</string>
    <key>LSUIElement</key>
    <true/>
    <key>NSHumanReadableCopyright</key>
    <string>Copyright © 2026 Kliply Contributors. All rights reserved.</string>
    <key>NSAppleEventsUsageDescription</key>
    <string>Kliply needs permission to send paste events to other applications.</string>
</dict>
</plist>
EOF

echo "✅ Kliply.app created successfully!"
echo "To run: open Kliply.app"
echo "Or double-click Kliply.app in Finder"
