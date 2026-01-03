# Kliply Resources

## App Icon

The app icon should be a 1024x1024 PNG file that will be converted to .icns format for the macOS application bundle.

### Creating the Icon

1. Create a 1024x1024 PNG file named `icon.png` in this directory
2. Run the icon generation script:
   ```bash
   ./scripts/generate_icon.sh
   ```

This will create `icon.icns` which is used by py2app for the application bundle.

### Icon Design Guidelines

- Use a simple, recognizable design
- Consider the clipboard metaphor (e.g., clipboard with history layers)
- Ensure it looks good at small sizes (16x16, 32x32)
- Follow macOS Big Sur icon design guidelines:
  - Rounded square shape
  - Subtle gradients
  - Depth and dimension
  - Consistent lighting

### Temporary Icon

Until a proper icon is created, a placeholder icon will be generated automatically during the build process.
