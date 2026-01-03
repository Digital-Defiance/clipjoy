#!/usr/bin/env python3
"""
Convert SVG to PNG using PyQt6 (no external dependencies needed)
"""

import sys
import os
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtCore import QSize

def convert_svg_to_png(svg_path: str, png_path: str, size: int = 1024):
    """Convert SVG file to PNG at specified size."""
    
    # Check if SVG file exists
    if not os.path.exists(svg_path):
        print(f"Error: SVG file not found: {svg_path}")
        return False
    
    # Create SVG renderer
    renderer = QSvgRenderer(svg_path)
    
    if not renderer.isValid():
        print(f"Error: Invalid SVG file: {svg_path}")
        return False
    
    # Create image with specified size
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(0)  # Transparent background
    
    # Render SVG to image
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()
    
    # Save as PNG
    if image.save(png_path, "PNG"):
        print(f"✓ PNG created: {png_path}")
        print(f"  Size: {size}x{size}")
        return True
    else:
        print(f"✗ Failed to save PNG: {png_path}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 convert_svg_to_png.py <input.svg> [output.png] [size]")
        print("")
        print("Examples:")
        print("  python3 convert_svg_to_png.py icon.svg")
        print("  python3 convert_svg_to_png.py icon.svg output.png")
        print("  python3 convert_svg_to_png.py icon.svg output.png 2048")
        sys.exit(1)
    
    svg_path = sys.argv[1]
    
    # Default output path
    if len(sys.argv) >= 3:
        png_path = sys.argv[2]
    else:
        png_path = os.path.join("resources", "icon.png")
    
    # Default size
    size = 1024
    if len(sys.argv) >= 4:
        try:
            size = int(sys.argv[3])
        except ValueError:
            print(f"Warning: Invalid size '{sys.argv[3]}', using default 1024")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(png_path) if os.path.dirname(png_path) else ".", exist_ok=True)
    
    # Import QApplication (required for Qt)
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # Convert
    success = convert_svg_to_png(svg_path, png_path, size)
    
    sys.exit(0 if success else 1)
