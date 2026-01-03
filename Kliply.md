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

## Future Wishlist

- Launch at login option
- Automatic update mechanism
- Exclude list for specific apps (requires persistence)
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
