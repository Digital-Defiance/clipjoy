# Kliply Build and Distribution Guide

This guide covers building, signing, notarizing, and distributing Kliply as a native macOS application.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Icon Preparation](#icon-preparation)
3. [Building the Application](#building-the-application)
4. [Code Signing](#code-signing)
5. [Notarization](#notarization)
6. [Creating a DMG](#creating-a-dmg)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)
9. [App Store Submission](#app-store-submission)

## Prerequisites

### Required Tools

- **macOS 10.15+**: Required for building and testing
- **Xcode Command Line Tools**: Install with `xcode-select --install`
- **Python 3.9+**: System Python or via Homebrew
- **Apple Developer Account**: Required for code signing and notarization

### Required Credentials

1. **Developer ID Application Certificate**:
   - Obtain from [Apple Developer Portal](https://developer.apple.com/account/resources/certificates)
   - Install in Keychain Access

2. **App-Specific Password**:
   - Generate at [appleid.apple.com](https://appleid.apple.com/account/manage)
   - Used for notarization (not your Apple ID password)

3. **Team ID**:
   - Find in [App Store Connect](https://appstoreconnect.apple.com) under Membership

### Install Dependencies

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install all dependencies including build tools
pip install -r requirements.txt
```

## Icon Preparation

### Option 1: Use Your SVG Icon

If you have an SVG icon:

```bash
bash scripts/convert_svg_icon.sh path/to/your/icon.svg
```

This requires `librsvg` (install with `brew install librsvg`).

### Option 2: Create a PNG Icon

Create a 1024x1024 PNG file and save it as `resources/icon.png`, then:

```bash
bash scripts/generate_icon.sh
```

### Option 3: Use Placeholder

The build script will automatically create a placeholder icon if none exists.

## Building the Application

### Quick Build

```bash
bash scripts/build.sh
```

This will:
1. Activate the virtual environment
2. Install py2app if needed
3. Create/generate icon if needed
4. Clean previous builds
5. Build the application bundle
6. Output to `dist/Kliply.app`

### Manual Build

```bash
# Activate virtual environment
source venv/bin/activate

# Build with py2app
python3 setup.py py2app

# Output: dist/Kliply.app
```

### Build Configuration

The build is configured in `setup.py` with these key settings:

- **Bundle Identifier**: `com.Kliply.app`
- **LSUIElement**: `True` (hides from Dock)
- **Minimum macOS**: 10.15.0
- **Privacy Descriptions**: Accessibility usage explanation
- **Entitlements**: Defined in `resources/entitlements.plist`

## Code Signing

Code signing is **required** for distribution outside the App Store.

### Set Up Signing Identity

```bash
# Find your signing identities
security find-identity -v -p codesigning

# Set the identity (use the full name from the output above)
export SIGNING_IDENTITY="Developer ID Application: Your Name (TEAM_ID)"
```

### Sign the Application

```bash
bash scripts/sign.sh
```

The script will:
1. Sign all embedded frameworks and libraries
2. Sign the main application bundle with entitlements
3. Apply hardened runtime
4. Add timestamp for long-term validity
5. Verify the signature

### Verify Signing

```bash
# Verify signature
codesign --verify --deep --strict --verbose=2 dist/Kliply.app

# Check signature details
codesign -dv --verbose=4 dist/Kliply.app

# Test with Gatekeeper
spctl --assess --verbose=2 dist/Kliply.app
```

## Notarization

Notarization is **required** for distribution outside the App Store to avoid Gatekeeper warnings.

### Set Up Credentials

```bash
export APPLE_ID="your@email.com"
export APPLE_ID_PASSWORD="xxxx-xxxx-xxxx-xxxx"  # App-specific password
export TEAM_ID="XXXXXXXXXX"
```

### Notarize the Application

```bash
bash scripts/notarize.sh
```

The script will:
1. Create a zip archive of the app
2. Submit to Apple's notarization service
3. Wait for notarization to complete (usually 2-5 minutes)
4. Staple the notarization ticket to the app

### Check Notarization Status

```bash
# If notarization fails, get detailed logs
xcrun notarytool log <submission-id> \
  --apple-id "$APPLE_ID" \
  --password "$APPLE_ID_PASSWORD" \
  --team-id "$TEAM_ID"
```

### Verify Notarization

```bash
# Check if notarization ticket is stapled
stapler validate dist/Kliply.app

# Test with Gatekeeper
spctl --assess --verbose=2 dist/Kliply.app
```

## Creating a DMG

Create a distributable DMG installer:

```bash
bash scripts/create_dmg.sh
```

The script will:
1. Create a temporary disk image
2. Copy the application
3. Add an Applications symlink
4. Add a README file
5. Configure the window layout
6. Convert to compressed, read-only DMG
7. Sign the DMG (if signing identity is set)

Output: `dist/Kliply-1.0.0.dmg`

### Customize DMG Appearance

To customize the DMG background:
1. Create a 600x400 PNG image
2. Save as `resources/dmg_background.png`
3. Run `bash scripts/create_dmg.sh`

## Testing

### Test the Application Bundle

```bash
# Launch the app
open dist/Kliply.app

# Check logs
tail -f ~/Library/Logs/Kliply/Kliply.log
```

### Test the DMG

```bash
# Open the DMG
open dist/Kliply-1.0.0.dmg

# Drag to Applications and test
```

### Test on Clean System

**Critical**: Always test on a clean macOS system before distribution:

1. Use a separate Mac or VM
2. Do not have Xcode or development tools installed
3. Test the complete installation flow:
   - Open DMG
   - Drag to Applications
   - Launch from Applications
   - Grant permissions
   - Test core functionality

### Verification Checklist

- [ ] App launches without errors
- [ ] Accessibility permission prompt appears
- [ ] Global hotkey (Cmd+Shift+V) works
- [ ] Clipboard monitoring works
- [ ] History popup displays correctly
- [ ] Settings panel works
- [ ] Menu bar icon appears
- [ ] No Gatekeeper warnings
- [ ] Code signature is valid
- [ ] Notarization is valid

## Troubleshooting

### Build Issues

**Problem**: `py2app` not found
```bash
pip install py2app>=0.28.0
```

**Problem**: Icon not found
```bash
# Create placeholder icon
python3 scripts/create_placeholder_icon.py
bash scripts/generate_icon.sh
```

**Problem**: Module import errors
```bash
# Reinstall in development mode
pip install -e .
```

### Signing Issues

**Problem**: No signing identity found
```bash
# List available identities
security find-identity -v -p codesigning

# If none found, create a certificate in Xcode or Apple Developer Portal
```

**Problem**: Entitlements error
```bash
# Verify entitlements file exists
ls -l resources/entitlements.plist

# Check entitlements syntax
plutil -lint resources/entitlements.plist
```

### Notarization Issues

**Problem**: Notarization rejected
```bash
# Get detailed error log
xcrun notarytool log <submission-id> \
  --apple-id "$APPLE_ID" \
  --password "$APPLE_ID_PASSWORD" \
  --team-id "$TEAM_ID"
```

Common rejection reasons:
- Missing hardened runtime
- Invalid entitlements
- Unsigned embedded libraries
- Missing Info.plist keys

**Problem**: "The executable does not have the hardened runtime enabled"
```bash
# Ensure signing script uses --options runtime
# This is already included in scripts/sign.sh
```

### Runtime Issues

**Problem**: App crashes on launch
```bash
# Check crash logs
open ~/Library/Logs/DiagnosticReports/

# Check app logs
tail -f ~/Library/Logs/Kliply/Kliply.log
```

**Problem**: Permissions not working
```bash
# Check if Accessibility is enabled
# System Preferences > Security & Privacy > Privacy > Accessibility
```

**Problem**: Gatekeeper blocks the app
```bash
# Verify notarization
spctl --assess --verbose=2 dist/Kliply.app

# If not notarized, run notarization script
bash scripts/notarize.sh
```

## App Store Submission

For App Store distribution (different from Developer ID distribution):

### 1. Update Bundle Identifier

In `setup.py`, change:
```python
'CFBundleIdentifier': 'com.yourcompany.Kliply',
```

### 2. Create App Store Provisioning Profile

1. Go to [Apple Developer Portal](https://developer.apple.com/account/resources/profiles)
2. Create a Mac App Store provisioning profile
3. Download and install

### 3. Update Entitlements

Use `resources/entitlements-appstore.plist` with App Store specific entitlements:
- Remove hardened runtime entitlements
- Add App Store specific entitlements

### 4. Build for App Store

```bash
# Build with App Store configuration
python3 setup.py py2app

# Sign with App Store certificate
codesign --force --sign "3rd Party Mac Developer Application: Your Name" \
  --entitlements resources/entitlements-appstore.plist \
  dist/Kliply.app

# Create installer package
productbuild --component dist/Kliply.app /Applications \
  --sign "3rd Party Mac Developer Installer: Your Name" \
  dist/Kliply.pkg
```

### 5. Upload to App Store Connect

```bash
# Validate the package
xcrun altool --validate-app -f dist/Kliply.pkg \
  --type osx \
  --apiKey YOUR_API_KEY \
  --apiIssuer YOUR_ISSUER_ID

# Upload
xcrun altool --upload-app -f dist/Kliply.pkg \
  --type osx \
  --apiKey YOUR_API_KEY \
  --apiIssuer YOUR_ISSUER_ID
```

### 6. Submit for Review

1. Go to [App Store Connect](https://appstoreconnect.apple.com)
2. Complete app metadata
3. Add screenshots (1280x800 for macOS)
4. Submit for review

## Complete Build Pipeline

Here's the complete process from source to distribution:

```bash
# 1. Prepare icon (if you have one)
bash scripts/convert_svg_icon.sh path/to/icon.svg

# 2. Build the application
bash scripts/build.sh

# 3. Code sign
export SIGNING_IDENTITY="Developer ID Application: Your Name (TEAM_ID)"
bash scripts/sign.sh

# 4. Notarize
export APPLE_ID="your@email.com"
export APPLE_ID_PASSWORD="xxxx-xxxx-xxxx-xxxx"
export TEAM_ID="XXXXXXXXXX"
bash scripts/notarize.sh

# 5. Create DMG
bash scripts/create_dmg.sh

# 6. Test on clean system
# (Manual step - test on a separate Mac)

# 7. Distribute
# Upload DMG to your website or distribution platform
```

## Automation

For CI/CD, you can automate the build process:

```bash
#!/bin/bash
# ci-build.sh

set -e

# Load credentials from environment or secrets
export SIGNING_IDENTITY="$CI_SIGNING_IDENTITY"
export APPLE_ID="$CI_APPLE_ID"
export APPLE_ID_PASSWORD="$CI_APPLE_PASSWORD"
export TEAM_ID="$CI_TEAM_ID"

# Build pipeline
bash scripts/build.sh
bash scripts/sign.sh
bash scripts/notarize.sh
bash scripts/create_dmg.sh

# Upload to distribution
# (Add your upload logic here)
```

## Resources

- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [Code Signing Guide](https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/)
- [Notarization Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [py2app Documentation](https://py2app.readthedocs.io/)

## Support

For issues with the build process, check:
1. This documentation
2. Project issues on GitHub
3. Apple Developer Forums
4. py2app documentation
