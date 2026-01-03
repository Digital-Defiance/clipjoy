# Kliply

Professional macOS clipboard manager with Windows 11-style functionality.

## Features

- **Clipboard History**: Automatically tracks and stores clipboard items (text, rich text, images)
- **Keyboard Activation**: Quick access via Cmd+Shift+V hotkey
- **Smart Deduplication**: Duplicate items move to front instead of creating new entries
- **Configurable Depth**: History size limit between 5-100 items (default: 10)
- **Native macOS Integration**: Menu bar icon, native UI, and system permissions

## Running Kliply

### Main Application (Recommended)

```bash
# Using the entry point script
python3 run_Kliply.py

# Or directly
python3 -m src.Kliply.main_application
```

### Legacy Run Script

```bash
python3 run.py
```

## Usage

1. **First Launch**: On first launch, Kliply will show a welcome screen and request Accessibility permissions
2. **Activate History**: Press `Cmd+Shift+V` to open the clipboard history popup
3. **Select Item**: Click or use arrow keys to select an item, press Enter to paste
4. **Settings**: Click the menu bar icon and select "Settings..." to configure
5. **Clear History**: Use the menu bar to clear clipboard history

## Building for Distribution

Kliply can be packaged as a native macOS application bundle for distribution.

### Prerequisites

1. **Install build dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Prepare your icon** (optional):
   - Place an SVG icon at the project root or provide the path
   - Run: `bash scripts/convert_svg_icon.sh path/to/icon.svg`
   - Or let the build process create a placeholder icon

### Build Process

#### 1. Build the Application Bundle

```bash
bash scripts/build.sh
```

This will:
- Create a placeholder icon if needed
- Build the .app bundle using py2app
- Output to `dist/Kliply.app`

#### 2. Code Sign the Application (Required for Distribution)

```bash
export SIGNING_IDENTITY="Developer ID Application: Your Name (TEAM_ID)"
bash scripts/sign.sh
```

Or the script will prompt you for your signing identity.

To find your signing identities:
```bash
security find-identity -v -p codesigning
```

#### 3. Notarize with Apple (Required for Distribution)

```bash
export APPLE_ID="your@email.com"
export APPLE_ID_PASSWORD="app-specific-password"
export TEAM_ID="YOUR_TEAM_ID"
bash scripts/notarize.sh
```

**Note**: Use an app-specific password, not your Apple ID password. Generate one at [appleid.apple.com](https://appleid.apple.com/account/manage).

#### 4. Create DMG Installer

```bash
bash scripts/create_dmg.sh
```

This creates `dist/Kliply-1.0.0.dmg` ready for distribution.

### Complete Build Pipeline

For a complete build from source to DMG:

```bash
# 1. Build
bash scripts/build.sh

# 2. Sign
export SIGNING_IDENTITY="Developer ID Application: Your Name (TEAM_ID)"
bash scripts/sign.sh

# 3. Notarize
export APPLE_ID="your@email.com"
export APPLE_ID_PASSWORD="app-specific-password"
export TEAM_ID="YOUR_TEAM_ID"
bash scripts/notarize.sh

# 4. Create DMG
bash scripts/create_dmg.sh
```

### Testing the Build

1. **Test the app bundle**:
   ```bash
   open dist/Kliply.app
   ```

2. **Test the DMG installer**:
   ```bash
   open dist/Kliply-1.0.0.dmg
   ```

3. **Verify code signature**:
   ```bash
   codesign --verify --deep --strict --verbose=2 dist/Kliply.app
   ```

4. **Check notarization**:
   ```bash
   spctl --assess --verbose=2 dist/Kliply.app
   ```

### Distribution Checklist

Before distributing Kliply:

- [ ] Test on a clean macOS system (not your development machine)
- [ ] Verify Accessibility permissions prompt appears
- [ ] Test all core features (clipboard monitoring, hotkey, history popup)
- [ ] Verify code signature: `codesign --verify --deep dist/Kliply.app`
- [ ] Verify notarization: `spctl --assess --verbose=2 dist/Kliply.app`
- [ ] Test DMG installation process
- [ ] Verify app launches from Applications folder
- [ ] Test with Gatekeeper enabled

## Project Structure

```
Kliply/
├── src/
│   └── Kliply/          # Main application package
│       ├── __init__.py   # Package initialization
│       └── models.py     # Data models
├── tests/
│   ├── unit/             # Unit tests
│   ├── property/         # Property-based tests (Hypothesis)
│   ├── integration/      # Integration tests
│   └── conftest.py       # Pytest configuration and fixtures
├── scripts/              # Build and distribution scripts
│   ├── build.sh          # Build application bundle
│   ├── sign.sh           # Code sign the application
│   ├── notarize.sh       # Notarize with Apple
│   ├── create_dmg.sh     # Create DMG installer
│   ├── convert_svg_icon.sh  # Convert SVG to icon formats
│   └── generate_icon.sh  # Generate .icns from PNG
├── resources/            # Application resources
│   ├── entitlements.plist   # App sandboxing entitlements
│   ├── Info.plist.template  # Bundle metadata template
│   └── icon.icns         # Application icon (generated)
├── requirements.txt      # Project dependencies
├── setup.py             # Package setup with py2app configuration
├── pytest.ini           # Pytest configuration
└── README.md            # This file
```

## Setup

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install in Development Mode

```bash
pip install -e .
```

### Install with Development Dependencies

```bash
pip install -e ".[dev]"
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest -m unit

# Property-based tests only
pytest -m property

# Integration tests only
pytest -m integration
```

### Run with Coverage

```bash
pytest --cov=src/Kliply --cov-report=html
```

### Hypothesis Profiles

The project uses Hypothesis for property-based testing with different profiles:

- `default`: 100 examples per test (standard development)
- `dev`: 10 examples per test (quick feedback during development)
- `ci`: 1000 examples per test (thorough CI testing)

To use a specific profile:

```bash
pytest --hypothesis-profile=dev
```

## Development

This project follows the Kliply specification located in `.kiro/specs/Kliply/`.

Key documents:
- `requirements.md`: Feature requirements
- `design.md`: System design and architecture
- `tasks.md`: Implementation task list

## Requirements

- Python 3.9+
- macOS (for native clipboard and UI integration)
- PyQt6 for UI framework
- py2app (for building application bundles)

## App Store Submission

For App Store submission, additional steps are required:

1. **Create App Store Connect listing**
2. **Prepare screenshots** (1280x800 for macOS)
3. **Write app description and keywords**
4. **Set pricing and availability**
5. **Submit for review**

See Apple's [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/) for requirements.

## License

Copyright © 2026 Digital Defiance, Jessica Mulein
