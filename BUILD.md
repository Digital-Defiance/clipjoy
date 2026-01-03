# Kliply - Build and Development Guide

## Building the Project

### Prerequisites
- macOS 13.0 or later
- Xcode 15.0 or later
- Swift 6.2 or later

### Build from Command Line

```bash
# Build the project
swift build

# Build in release mode
swift build -c release

# Run the application
swift run

# Run tests
swift test
```

### Build with Xcode

1. Generate Xcode project:
```bash
swift package generate-xcodeproj
```

2. Open the generated `.xcodeproj` file in Xcode

3. Select the Kliply scheme and build (⌘B)

4. Run the application (⌘R)

## First-Time Setup

When you first run Kliply, you'll need to grant accessibility permissions:

1. The app will prompt you for accessibility access
2. Go to System Settings > Privacy & Security > Accessibility
3. Enable Kliply in the list
4. The app will automatically detect the permission and activate the hotkey

## Development Structure

```
Sources/
  Kliply/
    kliply.swift              # Main app entry point
    Models/
      ClipboardItem.swift     # Data model for clipboard entries
      AppSettings.swift       # App settings and preferences
    Services/
      ClipboardMonitor.swift  # Clipboard monitoring service
      HotkeyManager.swift     # Global hotkey registration
      URLMetadataFetcher.swift # URL title fetching
    ViewModels/
      AppState.swift          # Main app state manager
    Views/
      PopupWindow.swift       # Main popup UI
      SettingsView.swift      # Settings window
      ContentPreviewView.swift # Rich content previews
      KeyboardNavigation.swift # Keyboard handling
    Info.plist              # App metadata
    Kliply.entitlements     # Security entitlements
    PrivacyInfo.xcprivacy   # Privacy manifest

Tests/
  KliplyTests/
    KliplyTests.swift       # Unit tests
```

## Key Features Implemented

✅ Menu bar app with no dock icon
✅ Global hotkey registration (Cmd+Shift+V, customizable)
✅ Accessibility permission handling with auto-detection
✅ Clipboard monitoring with duplicate skipping
✅ Memory-only storage (no persistence)
✅ Popup window with search and filtering
✅ Keyboard navigation (arrows, Enter, Esc, Tab, Delete)
✅ Support for text, rich text, images, URLs, and files
✅ URL title fetching for previews
✅ Settings window with history depth and preferences
✅ Clear history (all or individual items)
✅ Dark mode support (automatic)
✅ Comprehensive unit tests
✅ Privacy manifest for App Store

## Testing

### Run Unit Tests

```bash
swift test
```

### Manual Testing Checklist

- [ ] App launches and appears in menu bar
- [ ] Accessibility permission prompt appears
- [ ] Hotkey (Cmd+Shift+V) opens popup
- [ ] Clipboard items are captured
- [ ] Search filters items correctly
- [ ] Category filters work (Text, Images, URLs, Files, All)
- [ ] Keyboard navigation works (up/down arrows, Enter, Esc)
- [ ] Shift+Enter pastes as plain text
- [ ] Delete key removes items
- [ ] Clear All button works
- [ ] Settings window opens and saves preferences
- [ ] History depth limit is enforced
- [ ] Consecutive duplicates are skipped
- [ ] Dark mode follows system appearance
- [ ] About window displays correctly

## Known Limitations

- URL title fetching is async and may show URL first, then update with title
- File previews show filename only (no icons or thumbnails)
- Hotkey customization UI is basic (shows placeholder)
- No persistence means history is lost on quit
- No exclude list for apps (future feature)

## App Store Preparation

### Required Before Submission

1. **App Icon**: Create icon set in Assets.xcassets
   - 1024x1024 PNG for App Store
   - All required sizes for macOS

2. **Code Signing**: 
   - Apple Developer account required
   - Configure signing in Xcode
   - Create provisioning profiles

3. **Notarization**:
   - Archive the app (Product > Archive)
   - Submit for notarization via Xcode Organizer

4. **Testing**:
   - Test on multiple macOS versions
   - Verify all permissions work correctly
   - Check memory usage with large history

5. **Metadata**:
   - Update GitHub URL in About window
   - Prepare App Store description
   - Take screenshots for App Store listing
   - Write privacy policy (explain clipboard monitoring)

6. **Review Privacy Manifest**:
   - Ensure PrivacyInfo.xcprivacy is complete
   - Document all accessed APIs

## Future Enhancements

See Kliply.md for complete wishlist, including:
- Launch at login option
- Automatic updates
- App exclude list (requires persistence)
- Enhanced accessibility support
- Localization
- Crash reporting (with consent)

## Troubleshooting

**Hotkey doesn't work:**
- Check accessibility permissions in System Settings
- Restart the app after granting permissions

**App crashes on launch:**
- Check Console.app for crash logs
- Verify macOS version is 13.0+

**Clipboard not monitoring:**
- Ensure app is running (check menu bar)
- Try copying text to test

**Build errors:**
- Clean build folder: `swift package clean`
- Update dependencies: `swift package update`
- Verify Swift version: `swift --version`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - See LICENSE file for details
