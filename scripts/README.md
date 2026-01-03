# Kliply Build Scripts

This directory contains scripts for building, signing, and distributing Kliply as a native macOS application.

## Quick Reference

### Icon Management

```bash
# Convert SVG to PNG and .icns
./convert_svg_icon.sh path/to/icon.svg

# Generate .icns from existing PNG
./generate_icon.sh

# Create placeholder icon for development
python3 create_placeholder_icon.py
```

### Build Pipeline

```bash
# 1. Build application bundle
./build.sh

# 2. Code sign (requires Developer ID)
export SIGNING_IDENTITY="Developer ID Application: Your Name (TEAM_ID)"
./sign.sh

# 3. Notarize with Apple (requires credentials)
export APPLE_ID="your@email.com"
export APPLE_ID_PASSWORD="app-specific-password"
export TEAM_ID="TEAM_ID"
./notarize.sh

# 4. Create DMG installer
./create_dmg.sh
```

## Script Details

### build.sh
Builds the macOS application bundle using py2app.

**Output**: `dist/Kliply.app`

**What it does**:
- Activates virtual environment
- Installs py2app if needed
- Creates placeholder icon if needed
- Cleans previous builds
- Runs py2app build

**Usage**:
```bash
./build.sh
```

### sign.sh
Code signs the application bundle with Developer ID certificate.

**Requirements**:
- Developer ID Application certificate installed in Keychain
- Built application at `dist/Kliply.app`

**Environment Variables**:
- `SIGNING_IDENTITY`: Your Developer ID (optional, will prompt if not set)

**Usage**:
```bash
export SIGNING_IDENTITY="Developer ID Application: Your Name (TEAM_ID)"
./sign.sh
```

### notarize.sh
Submits the application to Apple for notarization.

**Requirements**:
- Signed application at `dist/Kliply.app`
- Apple Developer account
- App-specific password

**Environment Variables**:
- `APPLE_ID`: Your Apple ID email
- `APPLE_ID_PASSWORD`: App-specific password (not your Apple ID password)
- `TEAM_ID`: Your Team ID from App Store Connect

**Usage**:
```bash
export APPLE_ID="your@email.com"
export APPLE_ID_PASSWORD="xxxx-xxxx-xxxx-xxxx"
export TEAM_ID="XXXXXXXXXX"
./notarize.sh
```

**Note**: Generate an app-specific password at [appleid.apple.com](https://appleid.apple.com/account/manage)

### create_dmg.sh
Creates a DMG installer for distribution.

**Requirements**:
- Built application at `dist/Kliply.app`

**Output**: `dist/Kliply-1.0.0.dmg`

**What it does**:
- Creates temporary disk image
- Copies application
- Adds Applications symlink
- Adds README
- Configures window layout
- Converts to compressed DMG
- Signs DMG (if signing identity is set)

**Usage**:
```bash
./create_dmg.sh
```

### convert_svg_icon.sh
Converts SVG icon to PNG and .icns formats.

**Requirements**:
- `librsvg` installed (`brew install librsvg`)

**Output**:
- `resources/icon.png` (1024x1024)
- `resources/icon.icns` (macOS icon bundle)

**Usage**:
```bash
./convert_svg_icon.sh path/to/icon.svg
```

### generate_icon.sh
Generates .icns file from existing PNG.

**Requirements**:
- `resources/icon.png` (1024x1024)

**Output**: `resources/icon.icns`

**Usage**:
```bash
./generate_icon.sh
```

### create_placeholder_icon.py
Creates a simple placeholder icon for development.

**Output**: `resources/icon.png` (1024x1024)

**Usage**:
```bash
python3 create_placeholder_icon.py
```

## Complete Build Example

```bash
# Prepare your environment
cd /path/to/Kliply
source venv/bin/activate

# If you have an SVG icon
./scripts/convert_svg_icon.sh ~/Desktop/Kliply-icon.svg

# Build
./scripts/build.sh

# Sign (you'll be prompted for identity if not set)
./scripts/sign.sh

# Notarize (you'll be prompted for credentials if not set)
./scripts/notarize.sh

# Create DMG
./scripts/create_dmg.sh

# Test
open dist/Kliply-1.0.0.dmg
```

## Troubleshooting

### "py2app not found"
```bash
pip install py2app>=0.28.0
```

### "rsvg-convert not found"
```bash
brew install librsvg
```

### "No signing identity found"
```bash
# List available identities
security find-identity -v -p codesigning
```

### "Notarization failed"
```bash
# Get detailed logs
xcrun notarytool log <submission-id> \
  --apple-id "$APPLE_ID" \
  --password "$APPLE_ID_PASSWORD" \
  --team-id "$TEAM_ID"
```

## Environment Variables Reference

| Variable | Description | Required For |
|----------|-------------|--------------|
| `SIGNING_IDENTITY` | Developer ID Application certificate | Code signing |
| `APPLE_ID` | Apple ID email | Notarization |
| `APPLE_ID_PASSWORD` | App-specific password | Notarization |
| `TEAM_ID` | Team ID from App Store Connect | Notarization |

## See Also

- [BUILD.md](../docs/BUILD.md) - Comprehensive build documentation
- [README.md](../README.md) - Project overview and setup
- [Apple Developer Portal](https://developer.apple.com/account/)
- [App Store Connect](https://appstoreconnect.apple.com/)
