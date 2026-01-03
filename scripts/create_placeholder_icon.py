#!/usr/bin/env python3
"""
Create a simple placeholder icon for Kliply during development.
This generates a basic 1024x1024 PNG that can be converted to .icns.
"""

from PyQt6.QtGui import QImage, QPainter, QColor, QFont, QPen
from PyQt6.QtCore import Qt, QRect
import sys
import os

def create_placeholder_icon(output_path: str):
    """Create a simple placeholder icon with clipboard design."""
    size = 1024
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Background rounded rectangle (clipboard)
    margin = 100
    painter.setPen(QPen(QColor(100, 100, 100), 20))
    painter.setBrush(QColor(240, 240, 240))
    painter.drawRoundedRect(margin, margin, size - 2*margin, size - 2*margin, 80, 80)
    
    # Clipboard clip at top
    clip_width = 200
    clip_height = 80
    clip_x = (size - clip_width) // 2
    clip_y = margin - 20
    painter.setBrush(QColor(150, 150, 150))
    painter.drawRoundedRect(clip_x, clip_y, clip_width, clip_height, 20, 20)
    
    # Draw stacked papers effect (history)
    paper_margin = 200
    paper_offset = 40
    for i in range(3):
        y_offset = paper_margin + i * paper_offset
        painter.setPen(QPen(QColor(80, 80, 80), 8))
        painter.setBrush(QColor(255, 255, 255))
        painter.drawRoundedRect(
            paper_margin, 
            y_offset, 
            size - 2*paper_margin, 
            150, 
            20, 20
        )
    
    # Add "CJ" text
    painter.setPen(QColor(60, 60, 60))
    font = QFont("Helvetica", 200, QFont.Weight.Bold)
    painter.setFont(font)
    text_rect = QRect(0, size // 2 + 50, size, 300)
    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "CJ")
    
    painter.end()
    
    # Save the image
    if image.save(output_path):
        print(f"✓ Placeholder icon created: {output_path}")
        return True
    else:
        print(f"✗ Failed to save icon: {output_path}")
        return False

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    resources_dir = os.path.join(os.path.dirname(script_dir), "resources")
    output_path = os.path.join(resources_dir, "icon.png")
    
    # Ensure resources directory exists
    os.makedirs(resources_dir, exist_ok=True)
    
    # Create the icon
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    success = create_placeholder_icon(output_path)
    sys.exit(0 if success else 1)
