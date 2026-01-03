"""
Data models for Kliply clipboard manager.

This module defines the core data structures used throughout the application.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Union
import hashlib


class ContentType(Enum):
    """Enumeration of supported clipboard content types."""
    TEXT = "text"
    IMAGE = "image"
    RICH_TEXT = "rich_text"
    UNSUPPORTED = "unsupported"


@dataclass
class ClipboardContent:
    """
    Represents a single clipboard item with metadata.
    
    Attributes:
        content_type: The type of content (TEXT, IMAGE, RICH_TEXT, UNSUPPORTED)
        data: The actual content data (str for text, bytes for images)
        timestamp: When this content was copied
        preview: Truncated preview for display (max 50 chars)
        size_bytes: Size of the content in bytes
    """
    content_type: ContentType
    data: Union[str, bytes]
    timestamp: datetime
    preview: str = ""
    size_bytes: int = 0
    
    def __post_init__(self):
        """Initialize computed fields after dataclass initialization."""
        if not self.preview:
            self.preview = self._generate_preview()
        if self.size_bytes == 0:
            self.size_bytes = self._calculate_size()
    
    def _generate_preview(self) -> str:
        """Generate a truncated preview of the content."""
        if self.content_type == ContentType.TEXT:
            if isinstance(self.data, str):
                # Truncate to 50 characters
                if len(self.data) > 50:
                    return self.data[:50] + "..."
                return self.data
        elif self.content_type == ContentType.RICH_TEXT:
            if isinstance(self.data, str):
                # Extract plain text from HTML for preview (optimized)
                try:
                    import re
                    # Quick regex-based approach instead of full HTML parsing
                    # Remove script and style tags completely
                    text = re.sub(r'<script[^>]*>.*?</script>', '', self.data, flags=re.DOTALL | re.IGNORECASE)
                    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
                    # Remove all HTML tags
                    text = re.sub(r'<[^>]+>', '', text)
                    # Decode common HTML entities
                    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                    # Clean up whitespace
                    text = ' '.join(text.split()).strip()
                    
                    # Truncate to 50 characters
                    if len(text) > 50:
                        return text[:50] + "..."
                    return text if text else "[Rich Text]"
                except Exception:
                    # If regex fails, show a generic label
                    return "[Rich Text]"
        elif self.content_type == ContentType.IMAGE:
            return "[Image]"
        elif self.content_type == ContentType.UNSUPPORTED:
            return "[Unsupported Content]"
        return ""
    
    def _calculate_size(self) -> int:
        """Calculate the size of the content in bytes."""
        if isinstance(self.data, str):
            return len(self.data.encode('utf-8'))
        elif isinstance(self.data, bytes):
            return len(self.data)
        return 0
    
    def get_hash(self) -> str:
        """
        Generate a hash of the content for comparison.
        
        Returns:
            A SHA-256 hash string of the content.
        """
        if isinstance(self.data, str):
            content_bytes = self.data.encode('utf-8')
        elif isinstance(self.data, bytes):
            content_bytes = self.data
        else:
            content_bytes = str(self.data).encode('utf-8')
        
        return hashlib.sha256(content_bytes).hexdigest()
    
    def to_clipboard_format(self):
        """
        Convert the content to QMimeData format for clipboard operations.
        
        Returns:
            QMimeData object containing the content in the appropriate format.
        """
        from PyQt6.QtCore import QMimeData
        from PyQt6.QtGui import QImage
        
        mime_data = QMimeData()
        
        if self.content_type == ContentType.TEXT:
            mime_data.setText(self.data)
        elif self.content_type == ContentType.RICH_TEXT:
            # Set HTML for rich text
            mime_data.setHtml(self.data)
            # Also extract and set plain text from HTML for compatibility (optimized)
            try:
                import re
                # Quick regex-based text extraction
                text = re.sub(r'<script[^>]*>.*?</script>', '', self.data, flags=re.DOTALL | re.IGNORECASE)
                text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
                text = re.sub(r'<[^>]+>', '', text)
                text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                text = ' '.join(text.split()).strip()
                mime_data.setText(text if text else self.data)
            except Exception:
                # If extraction fails, just use the data as-is
                mime_data.setText(self.data)
        elif self.content_type == ContentType.IMAGE:
            # Convert bytes to QImage
            image = QImage()
            if isinstance(self.data, bytes):
                image.loadFromData(self.data)
            mime_data.setImageData(image)
        
        return mime_data


@dataclass
class Settings:
    """
    Configuration data structure for user preferences.
    
    Attributes:
        clipboard_depth: Maximum number of clipboard items to retain (5-100)
        hotkey: Keyboard shortcut to activate history popup
        launch_at_login: Whether to start Kliply at system login
        first_launch_complete: Whether the welcome screen has been shown
    """
    clipboard_depth: int = 10
    hotkey: str = "Cmd+Shift+V"
    launch_at_login: bool = False
    first_launch_complete: bool = False
    
    def validate(self) -> bool:
        """
        Validate settings values.
        
        Returns:
            True if all settings are valid, False otherwise.
        """
        # Validate clipboard depth is between 5 and 100
        if not (5 <= self.clipboard_depth <= 100):
            return False
        
        # Validate hotkey is not empty
        if not self.hotkey or not isinstance(self.hotkey, str):
            return False
        
        return True


@dataclass
class PermissionStatus:
    """
    Tracks macOS permission states.
    
    Attributes:
        accessibility: Whether Accessibility permissions are granted
        last_checked: Timestamp of last permission check
    """
    accessibility: bool = False
    last_checked: datetime = field(default_factory=datetime.now)
    
    def all_granted(self) -> bool:
        """
        Check if all required permissions are granted.
        
        Returns:
            True if all permissions are granted, False otherwise.
        """
        return self.accessibility
