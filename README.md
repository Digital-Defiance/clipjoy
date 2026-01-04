# Kliply

A powerful clipboard manager for macOS, inspired by Windows' Win+V clipboard history feature.

![Platform](https://img.shields.io/badge/platform-macOS%2013.0%2B-lightgrey)
![Swift](https://img.shields.io/badge/swift-6.2-orange)
![License](https://img.shields.io/badge/license-MIT-blue)

## Features

- 🔥 **Global Hotkey**: Quick access with Cmd+Shift+V (customizable)
- 📋 **Smart Clipboard Tracking**: Automatically captures text, rich text, images, URLs, and files
- 🔍 **Instant Search**: Find any clipboard item instantly
- 🏷️ **Category Filters**: Filter by Text, Images, URLs, or Files
- ⌨️ **Keyboard Navigation**: Navigate with arrows, select with Enter, close with Esc
- 🎨 **Rich Previews**: See formatted text, images, and URL metadata
- 🌓 **Dark Mode**: Seamlessly integrates with macOS appearance
- 🔒 **Privacy-Focused**: All history stored in memory only, no disk writes
- ⚡ **Lightning Fast**: Event-driven architecture for instant response
- 🎯 **Smart Paste**: Automatically pastes back to the previously focused app

## Installation

### Download Release (Recommended)

**[Download Kliply v1.0.5](https://github.com/Digital-Defiance/Kliply/releases/tag/v1.0.5)**

The release includes a signed and notarized DMG for easy installation:

1. Download `Kliply.dmg` from the GitHub release
2. Open the DMG and drag Kliply to your Applications folder
3. Launch Kliply and grant accessibility permissions

**App Store release coming soon!**

### From Source (For Adventurous Developers)

1. Clone the repository:
```bash
git clone https://github.com/Digital-Defiance/kliply.git
cd kliply
```

2. Build and run:
```bash
swift build -c release
swift run
```

### First Launch

On first launch, Kliply will request accessibility permissions:

1. Grant permission when prompted
2. Go to **System Settings > Privacy & Security > Accessibility**
3. Enable Kliply
4. The app will automatically activate

## Usage

### Basic Usage

1. **Launch Kliply** - It appears as a clipboard icon in your menu bar
2. **Copy anything** - Text, images, URLs, or files
3. **Press Cmd+Shift+V** - Opens the clipboard history popup
4. **Select an item**:
   - Use arrow keys to navigate
   - Press Enter to paste
   - Press Shift+Enter to paste as plain text
   - Press Esc to close without pasting

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd+Shift+V` | Open/close popup |
| `↑` / `↓` | Navigate items |
| `Enter` | Select and paste |
| `Shift+Enter` | Paste as plain text |
| `Tab` | Cycle through filters |
| `Delete` | Remove selected item |
| `Esc` | Close popup |

### Search & Filter

- **Search**: Type in the search bar to filter items by content
- **Category Filters**: Click pills to filter by type (Text, Images, URLs, Files, All)
- **Clear History**: Click "Clear" button or use menu bar > Clear History

### Settings

Access settings via the menu bar icon:

- **History Depth**: Number of items to keep (default: 10)
- **Hotkey**: Customize the global keyboard shortcut
- **Paste Behavior**: Always paste as plain text option
- **Preview Options**: Toggle image previews

## System Requirements

- macOS 13.0 (Ventura) or later
- Accessibility permissions (required for global hotkeys)

## Privacy

Kliply takes your privacy seriously:

- ✅ All clipboard history stored in **memory only**
- ✅ **No data** written to disk
- ✅ **No analytics** or tracking
- ✅ **No network requests** except for URL title fetching (optional)
- ✅ History cleared automatically on app quit

See [PrivacyInfo.xcprivacy](Sources/Kliply/PrivacyInfo.xcprivacy) for details.

## Development

See [BUILD.md](BUILD.md) for detailed build instructions and development guide.

### Quick Start

```bash
# Build
swift build

# Run tests
swift test

# Run the app
swift run
```

### Project Structure

- `Sources/Kliply/` - Main application code
  - `Models/` - Data models
  - `Services/` - Background services (clipboard, hotkey)
  - `ViewModels/` - App state management
  - `Views/` - SwiftUI views
- `Tests/` - Unit tests

## Roadmap

- [ ] App Store submission
- [ ] Launch at login option
- [ ] Automatic updates via Sparkle
- [ ] App exclude list (ignore clipboard from certain apps)
- [ ] Enhanced VoiceOver support
- [ ] Localization (multiple languages)
- [ ] Export/import history
- [ ] Pin favorite items
- [ ] Sync across devices (iCloud)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new features
4. Ensure all tests pass (`swift test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Troubleshooting

**Hotkey doesn't work?**
- Verify accessibility permissions in System Settings
- Restart Kliply after granting permissions

**Items not appearing in history?**
- Check that the app is running (icon in menu bar)
- Ensure history depth setting is not 0

**App crashes or freezes?**
- Check Console.app for error logs
- Report issues on GitHub with crash details

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Inspired by Windows 10/11 clipboard history (Win+V)
- Built with SwiftUI and modern macOS APIs
- Icon from SF Symbols

## Support

- 📧 Report issues: [GitHub Issues](https://github.com/Digital-Defiance/kliply/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/Digital-Defiance/kliply/discussions)
- ⭐ Star the repo if you find it useful!

---

Made with ❤️ for macOS
