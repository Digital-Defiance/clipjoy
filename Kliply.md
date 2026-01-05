# Kliply - macOS Clipboard Manager

A macOS clone of Win+V clipboard utility written in SwiftUI.

## Core Features

### Permissions & Hotkey
- Handle triggering the accessibility prompt for hotkey permission
- Detect when permission is granted and restart the app if needed
- Handle revocation of hotkey permission gracefully while running
- Register hotkey: Cmd+Shift+V (default, customizable in settings)
- Allow users to customize the hotkey in Settings menu

### Clipboard Monitoring
- Event-driven architecture to track clipboard changes
- Track the most recent N clipboard entries (default: 10, configurable in Settings)
- **Memory-only storage** - no persistence to disk
- Skip consecutive duplicate entries
- Support multiple clipboard data types:
  - Plain text
  - Rich text (rendered or stripped)
  - Images
  - URLs (with preview showing website title/favicon)
  - Files (TBD: research how other clipboard apps handle this)
  - Other copyable items

### Popup Window
- Trigger: User presses hotkey (Cmd+Shift+V by default)
- Position: Center of screen
- Size: Dynamically sized based on screen, large enough to show ~10 items
- Displays clipboard history with visual previews
- Search/filter bar to quickly find items
- Category/type filters (Text, Images, URLs, Files, etc.)

### Keyboard Navigation
- Arrow keys: Navigate through items
- Enter: Select and paste item
- Shift+Enter: Paste in alternate format (when multiple formats available)
- Esc: Close popup without pasting
- Tab: Switch between filters

### Paste Behavior
- Track current app/UI focus before popup appears
- On selection:
  1. Place selected item on clipboard
  2. Re-activate previously focused app/UI element
  3. Paste into that element
  4. Choose rich text or plain text as appropriate (TBD: research what other clipboard apps do)

### History Management
- Clear all history (button in popup or menu)
- Clear selected items individually
- Maximum item size: TBD (e.g., 10MB to prevent memory issues)

## Settings & Preferences

Accessible via Menu Bar icon:

- History depth (default: 10)
- Hotkey customization
- Plain text preference (TBD: research standard behavior)
- Dark mode support (respect system appearance settings)
- High contrast mode (if easy to implement)
- Font size options (if easy to implement)
- **Excluded Apps** (configurable list):
  - Allow users to add/remove application bundle identifiers or app names (e.g., "1Password 7", "com.agilebits.onepassword7")
  - Clipboard changes from excluded apps are never added to history
  - Useful for password managers, banking apps, and other sensitive applications
  - Stored in user defaults (persistent across app restarts)

## UI Components

### Menu Bar
- Icon with hover states
- Active indicator when popup is showing
- Access to:
  - Settings
  - Clear History
  - About window
  - Quit

### About Window
- App name and version
- License: MIT
- Credits
- Link to help documentation (if available)

### Empty State
- Friendly message when no clipboard history exists

## Apple Store Requirements

### Privacy & Security
- Privacy Manifest documenting clipboard access
- Privacy Policy explaining clipboard monitoring
- No data collection or storage beyond in-memory history
- Handle sandboxing requirements (determine entitlements needed)

### Metadata
- App icon (1024x1024)
- Screenshots for various macOS versions
- App description, keywords, categories

### Code Signing
- Apple Developer account
- Code signing certificates
- Notarization for distribution

## Testing Requirements

- Unit tests for core clipboard monitoring logic
- Unit tests for data models and state management
- UI tests for hotkey registration
- UI tests for popup display and item selection
- Integration tests for end-to-end workflows
- Performance tests with large history and large items
- Memory leak tests for long-running sessions
- Test permission denial and revocation scenarios
- Accessibility tests (VoiceOver compatibility - future)

### Excluded Apps Testing

- Unit tests for exclusion list model (add, remove, contains operations)
- Unit tests for bundle identifier detection and matching
- Unit tests for app name detection (e.g., "1Password 7", "com.agilebits.onepassword7")
- Unit tests to verify excluded app clipboard changes are not recorded
- Unit tests to verify non-excluded app clipboard changes are recorded normally
- Unit tests for persistence of excluded apps list to user defaults
- Unit tests for exclusion list retrieval from user defaults after app restart
- UI tests for adding apps to exclusion list (manual entry, app picker)
- UI tests for removing apps from exclusion list
- UI tests for displaying current exclusion list in settings
- Integration tests for clipboard monitoring with various excluded/included apps
- Edge case tests: empty exclusion list, duplicate entries, invalid bundle IDs, case sensitivity
- Performance tests with large exclusion lists (100+ apps)
- Test clearing app history when changing exclusion settings
- Test that monitored clipboard history excludes items from previously-included apps when they're added to exclusion list
- Test exclusion works across app updates/reinstalls with same bundle ID

## Future Wishlist

- Launch at login option
- Automatic update mechanism
- VoiceOver and screen reader support
- Localization for multiple languages
- Enhanced font size and accessibility options
- Crash reporting/analytics (with user consent)
- Sound effects for UI actions

## Development Notes

- Event-driven architecture should handle performance concerns
- Need to research standard clipboard app behavior for:
  - Plain text vs rich text pasting preferences
  - File handling/display
- First-run onboarding may be helpful to explain permissions
