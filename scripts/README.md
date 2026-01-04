# Building and Distributing Kliply

This directory contains scripts to build, sign, notarize, and package Kliply for distribution.

## Distribution Methods

### Direct Distribution (DMG)
For distributing outside the Mac App Store via your website, GitHub, etc.
- Uses Developer ID certificates
- Requires notarization
- Creates a `.dmg` installer

### Mac App Store
For distributing through the Mac App Store.
- Uses 3rd Party Mac Developer certificates
- Requires provisioning profile
- Creates a `.pkg` for upload to App Store Connect

## Prerequisites

### 1. Apple Developer Account
- Enroll at https://developer.apple.com/programs/
- Cost: $99/year

### 2. Certificates

#### For Direct Distribution (DMG):
1. Go to https://developer.apple.com/account/resources/certificates/list
2. Click "+" to create a new certificate
3. Select "Developer ID Application"
4. Upload Certificate Signing Request (or create one with Keychain Access)
5. Download and install the certificate

#### For Mac App Store:
1. Create "Mac App Distribution" certificate (3rd Party Mac Developer Application)
2. Create "Mac Installer Distribution" certificate (3rd Party Mac Developer Installer)
3. Create a Mac App Store provisioning profile:
   - Go to https://developer.apple.com/account/resources/profiles/list
   - Click "+" and select "Mac App Store Connect"
   - Select your App ID and certificate
   - Download and double-click to install

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

### Option 1: Build Everything for Direct Distribution
```bash
chmod +x scripts/*.sh
./scripts/build-all.sh
```

This runs all steps automatically and creates `build/Kliply.dmg`.

### Option 2: Build for Mac App Store
```bash
export APPLE_TEAM_ID="YOUR_TEAM_ID"
./scripts/5-build-for-app-store.sh
```

Creates `build/export/Kliply.pkg` for upload to App Store Connect.

### Option 3: Step by Step (Direct Distribution)

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

### 5-build-for-app-store.sh
- Uses Xcode project (Kliply.xcodeproj) for proper App Store metadata
- Archives with xcodebuild
- Signs with 3rd Party Mac Developer certificates
- Exports signed .pkg for App Store Connect
- Ready for upload via Transporter app

## Troubleshooting

### "No Developer ID certificate found"
- Install certificate from developer.apple.com/account
- Check it's in Keychain Access under "My Certificates"

### "errSecInternalComponent" or "unable to build chain to self-signed root"
This means your certificate has incorrect trust settings. Fix it by:
1. Open Keychain Access
2. Find your certificate under "My Certificates"
3. Double-click it → Trust → set to "Use System Defaults"
4. Or run: `security find-certificate -c "YOUR_CERT_NAME" -p ~/Library/Keychains/login.keychain-db > /tmp/cert.pem && security remove-trusted-cert /tmp/cert.pem`

You may also need to install Apple's intermediate certificates:
```bash
curl -sO https://www.apple.com/certificateauthority/DeveloperIDG2CA.cer
sudo security import DeveloperIDG2CA.cer -k /Library/Keychains/System.keychain
```

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
