# App Store Submission Guide

This guide walks you through submitting Kliply to the Mac App Store.

## Prerequisites

1. **Active Apple Developer Program membership** ($99/year)
   - Sign up at: https://developer.apple.com/programs/

2. **Create App in App Store Connect**
   - Go to: https://appstoreconnect.apple.com
   - Click "My Apps" → "+" → "New App"
   - Fill in:
     - Platform: macOS
     - Name: Kliply
     - Primary Language: English (U.S.)
     - Bundle ID: `com.digitaldefiance.kliply` (must match your code)
     - SKU: `kliply-macos` (unique identifier)

## Step 1: Create Certificates and Provisioning Profiles

### 1.1 Create App Store Distribution Certificate

```bash
# Generate Certificate Signing Request (CSR)
# Open Keychain Access > Certificate Assistant > Request a Certificate from a Certificate Authority
# Save as: CertificateSigningRequest.certSigningRequest
```

Then:
1. Go to https://developer.apple.com/account/resources/certificates
2. Click "+" to create new certificate
3. Select "Mac App Distribution"
4. Upload your CSR file
5. Download the certificate and double-click to install in Keychain

### 1.2 Create Mac Installer Distribution Certificate

Repeat the above process but select "Mac Installer Distribution" instead.

### 1.3 Create App Store Provisioning Profile

1. Go to https://developer.apple.com/account/resources/profiles
2. Click "+" to create new profile
3. Select "Mac App Store" under Distribution
4. Choose your App ID (com.digitaldefiance.kliply)
   - If it doesn't exist, create it at https://developer.apple.com/account/resources/identifiers
   - Type: App IDs
   - Bundle ID: `com.digitaldefiance.kliply`
   - Capabilities: Check "App Sandbox"
5. Select your Mac App Distribution certificate
6. Name it: "Kliply App Store"
7. Download and double-click to install

## Step 2: Set Up Environment Variables

```bash
# Find your Team ID at https://developer.apple.com/account
export APPLE_TEAM_ID="YOUR_TEAM_ID_HERE"

# Optional: Customize signing identity (default works for most)
export SIGNING_IDENTITY="3rd Party Mac Developer Application"
```

Add to your `~/.zshrc` to make permanent:
```bash
echo 'export APPLE_TEAM_ID="YOUR_TEAM_ID_HERE"' >> ~/.zshrc
source ~/.zshrc
```

## Step 3: Update Entitlements for App Store

The app needs App Store-specific entitlements. Update `Sources/Kliply/Kliply.entitlements`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- App Sandbox (REQUIRED for App Store) -->
    <key>com.apple.security.app-sandbox</key>
    <true/>
    
    <!-- Clipboard access -->
    <key>com.apple.security.automation.apple-events</key>
    <true/>
    
    <!-- Required for global hotkey -->
    <key>com.apple.security.temporary-exception.apple-events</key>
    <array>
        <string>com.apple.systemevents</string>
    </array>
    
    <!-- Allow reading from pasteboard -->
    <key>com.apple.security.cs.allow-jit</key>
    <false/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <false/>
    <key>com.apple.security.cs.allow-dyld-environment-variables</key>
    <false/>
</dict>
</plist>
```

## Step 4: Build for App Store

```bash
cd /Volumes/Code/source/repos/kliply
chmod +x scripts/5-build-for-app-store.sh
./scripts/5-build-for-app-store.sh
```

This creates: `build/export/Kliply.pkg`

## Step 5: Upload to App Store Connect

### Option A: Transporter App (Recommended)

1. Download "Transporter" from Mac App Store
2. Open Transporter
3. Sign in with your Apple ID
4. Drag `build/export/Kliply.pkg` into Transporter
5. Click "Deliver"

### Option B: Command Line

First, create an app-specific password:
1. Go to https://appleid.apple.com/account/manage
2. Sign in
3. Under Security → App-Specific Passwords → "+"
4. Name it "App Store Upload"
5. Copy the password

Store in Keychain:
```bash
xcrun altool --store-password-in-keychain-item "AC_PASSWORD" \
    -u "your@email.com" \
    -p "app-specific-password"
```

Upload:
```bash
xcrun altool --upload-app \
    --type osx \
    --file "build/export/Kliply.pkg" \
    --username "your@email.com" \
    --password "@keychain:AC_PASSWORD"
```

## Step 6: Complete App Store Listing

Go to App Store Connect and fill in:

### App Information
- **Subtitle**: "Clipboard History Manager for macOS"
- **Privacy Policy URL**: https://digitaldefiance.github.io/Kliply/privacy
- **Category**: Utilities
- **Secondary Category**: Productivity

### Pricing
- Choose your pricing (Free or Paid)
- Available in all territories

### App Privacy
Answer questions about data collection:
- **Do you collect data?** → No
- This matches your privacy-first approach

### Version Information
- **Screenshots**: Upload 3-5 screenshots at these sizes:
  - 1280 x 800 pixels (required)
  - 1440 x 900 pixels
  - 2560 x 1600 pixels
  - 2880 x 1800 pixels

- **Description**: 
```
Kliply brings the beloved Windows clipboard history feature (Win+V) to macOS. Access your clipboard history instantly with a customizable global hotkey.

FEATURES:
• Instant access with Cmd+Shift+V (customizable)
• Smart clipboard tracking for text, images, URLs, and files
• Keyboard-first navigation for power users
• Rich content previews
• Search and filter your history
• Memory-only storage - nothing saved to disk
• 100% open source and privacy-focused

PRIVACY FIRST:
All clipboard data is stored in memory only. When you quit Kliply, your history is gone. No cloud sync, no analytics, no tracking.

Perfect for developers, writers, and anyone who copies and pastes frequently.
```

- **Keywords**: clipboard, manager, history, productivity, utility, paste, copy
- **Support URL**: https://github.com/Digital-Defiance/Kliply
- **Marketing URL**: https://digitaldefiance.github.io/Kliply/

### Build Selection
- Select the build you just uploaded
- Add "What's New" text for this version

## Step 7: Submit for Review

1. Review all information
2. Click "Submit for Review"
3. Answer App Review questions:
   - Export Compliance: No (doesn't use encryption)
   - Advertising Identifier: No

## Common Issues

### "Invalid Code Signature"
```bash
# List available signing identities
security find-identity -v -p codesigning

# Make sure you have both:
# - "3rd Party Mac Developer Application"
# - "3rd Party Mac Developer Installer"
```

### "Provisioning Profile Not Found"
Make sure the provisioning profile name in ExportOptions.plist matches exactly what you named it in the Developer Portal.

### "Missing Required Entitlements"
App Store apps MUST have `com.apple.security.app-sandbox` set to `true`.

## Review Timeline

- Typical review time: 1-3 days
- Check status at App Store Connect
- You'll receive email updates

## After Approval

Your app will be live on the Mac App Store! Users can:
- Search for "Kliply"
- Direct link: https://apps.apple.com/app/kliply/idXXXXXXXX

## Updating Your App

For future updates:
1. Increment version in `CFBundleShortVersionString`
2. Increment build in `CFBundleVersion`
3. Run build script again
4. Upload new build
5. Create new version in App Store Connect
6. Submit for review

## Resources

- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [App Sandbox Guide](https://developer.apple.com/documentation/security/app_sandbox)
- [Code Signing Guide](https://developer.apple.com/support/code-signing/)
