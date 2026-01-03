"""
Clipboard Monitor for Kliply clipboard manager.

This module monitors the system clipboard for changes and notifies the
HistoryManager when new content is detected.
"""

import logging
from datetime import datetime
from typing import Optional

from PyQt6.QtGui import QClipboard, QGuiApplication
from PyQt6.QtWidgets import QApplication

from src.Kliply.models import ClipboardContent, ContentType
from src.Kliply.history_manager import HistoryManager

# Maximum size for clipboard items (10MB)
MAX_CONTENT_SIZE_BYTES = 10 * 1024 * 1024


class ClipboardMonitor:
    """
    Monitors the system clipboard for changes and updates history.
    
    This class uses Qt's dataChanged signal to detect clipboard changes
    in an event-driven manner, which is much more efficient than polling.
    
    Attributes:
        _history_manager: The HistoryManager to notify of clipboard changes
        _clipboard: QClipboard instance for accessing system clipboard
        _last_hash: Hash of the last processed clipboard content
    """
    
    def __init__(self, history_manager: HistoryManager):
        """
        Initialize the ClipboardMonitor.
        
        Args:
            history_manager: The HistoryManager to update with clipboard changes
        """
        self._history_manager = history_manager
        self._logger = logging.getLogger(__name__)
        
        try:
            # Get QClipboard instance
            app = QApplication.instance()
            if app is None:
                app = QGuiApplication([])
            self._clipboard = app.clipboard()
            
            # Connect to clipboard's dataChanged signal (event-driven)
            self._clipboard.dataChanged.connect(self._on_clipboard_change)
            
            # Track last clipboard content hash to detect changes
            self._last_hash: Optional[str] = None
            
            self._logger.info("ClipboardMonitor initialized successfully (event-driven)")
        
        except Exception as e:
            self._logger.error(f"Failed to initialize ClipboardMonitor: {e}", exc_info=True)
            raise
    
    def start(self) -> None:
        """
        Start monitoring the clipboard.
        
        With event-driven monitoring, this just captures the initial state.
        The dataChanged signal is already connected and will fire automatically.
        """
        try:
            # Capture initial clipboard state
            self._on_clipboard_change()
            self._logger.info("Clipboard monitoring started (event-driven)")
        
        except Exception as e:
            self._logger.error(f"Failed to start clipboard monitoring: {e}", exc_info=True)
            raise
    
    def stop(self) -> None:
        """
        Stop monitoring the clipboard.
        
        Disconnects the signal handler.
        """
        try:
            self._clipboard.dataChanged.disconnect(self._on_clipboard_change)
            self._logger.info("Clipboard monitoring stopped")
        except Exception as e:
            self._logger.error(f"Error stopping clipboard monitoring: {e}", exc_info=True)
    
    def force_check(self) -> None:
        """
        Force an immediate check of the clipboard.
        
        Useful when showing the history popup to ensure the latest
        clipboard content is captured, even if the signal hasn't fired yet.
        """
        self._on_clipboard_change()
    
    def _on_clipboard_change(self) -> None:
        """
        Handle clipboard change detection.
        
        This method is called automatically by Qt when the clipboard changes.
        It extracts the content type and data, creates a ClipboardContent object,
        and adds it to the HistoryManager.
        
        Implements error recovery: logs errors and continues monitoring.
        """
        try:
            # Try to access clipboard immediately
            try:
                mime_data = self._clipboard.mimeData()
            except Exception as e:
                self._logger.warning(f"Clipboard access error: {e}")
                return
            
            if mime_data is None:
                return
            
            # Extract content type and data
            content_type, data = self._extract_content(mime_data)
            
            if content_type is None or data is None:
                return
            
            # Check content size (memory pressure handling)
            content_size = self._estimate_content_size(content_type, data)
            if content_size > MAX_CONTENT_SIZE_BYTES:
                self._logger.warning(
                    f"Clipboard content too large ({content_size} bytes), "
                    f"exceeds limit of {MAX_CONTENT_SIZE_BYTES} bytes. Skipping."
                )
                return
            
            # Create ClipboardContent object
            content = ClipboardContent(
                content_type=content_type,
                data=data,
                timestamp=datetime.now()
            )
            
            # Check if content has changed
            current_hash = content.get_hash()
            if current_hash == self._last_hash:
                return
            
            # Update last hash and add to history
            self._last_hash = current_hash
            self._history_manager.add_item(content)
            self._logger.debug(f"Added clipboard item: {content_type.value}")
            
        except Exception as e:
            # Log error and continue monitoring (error recovery)
            self._logger.error(f"Error during clipboard monitoring: {e}", exc_info=True)
    
    def _extract_content(self, mime_data) -> tuple[Optional[ContentType], Optional[any]]:
        """
        Extract content type and data from QMimeData.
        
        Args:
            mime_data: QMimeData object from the clipboard
        
        Returns:
            A tuple of (ContentType, data) or (None, None) if extraction fails
        """
        try:
            # Check for image data first
            if mime_data.hasImage():
                image = mime_data.imageData()
                if image is not None:
                    try:
                        # Convert QImage to bytes
                        from PyQt6.QtCore import QBuffer, QIODevice
                        from PyQt6.QtGui import QImage
                        
                        buffer = QBuffer()
                        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
                        image.save(buffer, "PNG")
                        image_bytes = buffer.data().data()
                        
                        return ContentType.IMAGE, image_bytes
                    except Exception as e:
                        self._logger.error(f"Error converting image data: {e}", exc_info=True)
                        return None, None
            
            # Check for HTML/rich text
            if mime_data.hasHtml():
                html = mime_data.html()
                if html:
                    return ContentType.RICH_TEXT, html
            
            # Check for plain text
            if mime_data.hasText():
                text = mime_data.text()
                if text:
                    return ContentType.TEXT, text
            
            # Unsupported content type
            self._logger.debug("Clipboard contains unsupported content type")
            return ContentType.UNSUPPORTED, "[Unsupported Content]"
            
        except Exception as e:
            self._logger.error(f"Error extracting clipboard content: {e}", exc_info=True)
            return None, None
    
    def _estimate_content_size(self, content_type: ContentType, data: any) -> int:
        """
        Estimate the size of clipboard content in bytes.
        
        Args:
            content_type: Type of the content
            data: The content data
        
        Returns:
            Estimated size in bytes
        """
        try:
            if content_type == ContentType.IMAGE:
                return len(data) if isinstance(data, bytes) else 0
            elif content_type in (ContentType.TEXT, ContentType.RICH_TEXT):
                return len(data.encode('utf-8')) if isinstance(data, str) else 0
            else:
                return 0
        except Exception as e:
            self._logger.warning(f"Error estimating content size: {e}")
            return 0

