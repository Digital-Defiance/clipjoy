# Building and Distributing Kliply

This directory contains scripts to build, sign, notarize, and package Kliply for distribution.

## Prerequisites

### 1. Apple Developer Account
- Enroll at https://developer.apple.com/programs/
- Cost: $99/year

### 2. Developer ID Certificate
1. Go to https://developer.apple.com/account/resources/certificates/list
2. Click "+" to create a new certificate
3. Select "Developer ID Application"
4. Upload Certificate Signing Request (or create one with Keychain Access)
5. Download and install the certificate

### 3. App-Specific Password (for notarization)
1. Go to https://appleid.apple.com/account/manage
2. Sign in with your Apple ID
3. Under "Security" → "App-Specific Passwords", generate a new password
4. Save it (you'll need it once)

### 4. Set Environment Variables
```bash
export APPLE_ID="your@email.com"
export APPLE_TEAM_ID="XXXXXXXXXX"  # Find at developer.apple.com/account
```

### 5. Store Notarization Credentials
```bash
xcrun notarytool store-credentials "AC_PASSWORD" \
  --apple-id "$APPLE_ID" \
  --team-id "$APPLE_TEAM_ID" \
  --password "xxxx-xxxx-xxxx-xxxx"  # Your app-specific password
```

## Quick Start

### Option 1: Build Everything (Recommended)
```bash
chmod +x scripts/*.sh
./scripts/build-all.sh
```

This runs all steps automatically and creates `build/Kliply.dmg`.

### Option 2: Step by Step

#### Step 1: Build the App
```bash
./scripts/1-build-app.sh
```
Creates `build/Kliply.app`

#### Step 2: Sign the App
```bash
./scripts/2-sign-app.sh
```
Code signs with your Developer ID certificate

#### Step 3: Notarize with Apple
```bash
./scripts/3-notarize-app.sh
```
Submits to Apple for notarization (takes 5-10 minutes)

#### Step 4: Create DMG
```bash
./scripts/4-create-dmg.sh
```
Creates `build/Kliply.dmg` installer

## What Each Script Does

### 1-build-app.sh
- Compiles release build for both Apple Silicon and Intel
- Creates .app bundle structure
- Copies executable, Info.plist, icons
- Sets proper permissions

### 2-sign-app.sh
- Finds your Developer ID certificate
- Signs app with hardened runtime
- Verifies signature

### 3-notarize-app.sh
- Creates zip of signed app
- Submits to Apple's notarization service
- Waits for approval
- Staples notarization ticket to app

### 4-create-dmg.sh
- Creates disk image with app
- Adds Applications folder symlink
- Adds README
- Customizes appearance
- Compresses and signs DMG

## Troubleshooting

### "No Developer ID certificate found"
- Install certificate from developer.apple.com/account
- Check it's in Keychain Access under "My Certificates"

### "App-specific password not found"
- Run the `xcrun notarytool store-credentials` command above

### "Notarization failed"
Get detailed logs:
```bash
# Get submission ID from error message
xcrun notarytool log <submission-id> --keychain-profile AC_PASSWORD
```

### "Certificate not trusted"
Users seeing this need to:
1. Right-click app → Open (first time only)
2. Or: System Settings → Privacy & Security → "Open Anyway"

This shouldn't happen if notarization succeeds.

## Testing

### Test the built app
```bash
open build/Kliply.app
```

### Test the DMG
```bash
open build/Kliply.dmg
```

### Verify code signature
```bash
codesign --verify --deep --strict --verbose=2 build/Kliply.app
```

### Verify notarization
```bash
spctl --assess --verbose=2 build/Kliply.app
```

Should say "accepted" with "source=Notarized Developer ID"

## Distribution

Once you have `Kliply.dmg`:

1. **GitHub Release**: Upload to GitHub releases
2. **Website**: Host on your website
3. **Direct**: Share via email/cloud storage

Users just double-click the DMG and drag to Applications.

## Cost Summary

- Apple Developer Program: $99/year (required)
- All tools and signing: Included with membership

## Resources

- [Apple Notarization Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [Code Signing Guide](https://developer.apple.com/support/code-signing/)
- [Xcode Help](https://help.apple.com/xcode/)
