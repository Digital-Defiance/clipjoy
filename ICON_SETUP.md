# Setting Up Your Kliply Icon

You mentioned you have an SVG icon for Kliply. Here's how to use it:

## Quick Setup

1. **Save your SVG icon** somewhere accessible (e.g., Desktop, Downloads)

2. **Run the conversion script**:
   ```bash
   bash scripts/convert_svg_icon.sh /path/to/your/icon.svg
   ```

   For example:
   ```bash
   bash scripts/convert_svg_icon.sh ~/Desktop/Kliply-icon.svg
   ```

3. **Done!** The script will create:
   - `resources/icon.png` (1024x1024 PNG)
   - `resources/icon.icns` (macOS icon bundle)

## Requirements

The conversion script requires `librsvg`. If you don't have it:

```bash
brew install librsvg
```

## Alternative: Manual Conversion

If you prefer to convert manually:

1. **Convert SVG to PNG** (1024x1024):
   - Use any tool (Inkscape, Affinity Designer, online converter)
   - Save as `resources/icon.png`

2. **Generate .icns**:
   ```bash
   bash scripts/generate_icon.sh
   ```

## Verify Your Icon

After conversion, verify the files exist:

```bash
ls -lh resources/icon.png resources/icon.icns
```

You should see both files listed.

## Using the Icon

Once your icon is set up, it will automatically be used when you build the application:

```bash
bash scripts/build.sh
```

The built application at `dist/Kliply.app` will use your icon.

## Icon Design Tips

For best results, your SVG icon should:
- Be square (1:1 aspect ratio)
- Look good at small sizes (16x16, 32x32)
- Follow macOS Big Sur icon guidelines:
  - Rounded square shape
  - Subtle gradients
  - Depth and dimension
  - Consistent lighting from above

## Need Help?

If you encounter issues:
1. Check that your SVG file is valid
2. Ensure `librsvg` is installed
3. Try manual conversion as a fallback
4. See `scripts/README.md` for more details
