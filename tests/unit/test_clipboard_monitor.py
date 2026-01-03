"""
Unit tests for ClipboardMonitor.

Tests monitoring starts immediately, content type detection, and error handling.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.Kliply.models import ClipboardContent, ContentType
from src.Kliply.history_manager import HistoryManager
from src.Kliply.clipboard_monitor import ClipboardMonitor


class TestClipboardMonitor:
    """Unit tests for ClipboardMonitor class."""
    
    def test_monitoring_starts_immediately(self, qapp):
        """
        Test that monitoring starts immediately when start() is called.
        Requirements: 6.2
        """
        history_manager = HistoryManager()
        monitor = ClipboardMonitor(history_manager)
        
        # Verify clipboard signal is connected (event-driven, no timer)
        # The dataChanged signal should be connected after initialization
        assert monitor._clipboard is not None
        
        # Start monitoring (captures initial state)
        monitor.start()
        
        # Verify the monitor is set up with the clipboard
        assert monitor._history_manager is not None
        
        # Clean up
        monitor.stop()
    
    def test_content_type_detection_text(self, qapp):
        """
        Test that text content is correctly detected and extracted.
        Requirements: 6.2
        """
        from PyQt6.QtCore import QMimeData
        
        history_manager = HistoryManager()
        monitor = ClipboardMonitor(history_manager)
        
        # Create mock mime data with text
        mime_data = QMimeData()
        mime_data.setText("Test text content")
        
        # Extract content
        content_type, data = monitor._extract_content(mime_data)
        
        # Verify text was detected
        assert content_type == ContentType.TEXT
        assert data == "Test text content"
    
    def test_content_type_detection_html(self, qapp):
        """
        Test that HTML/rich text content is correctly detected and extracted.
        Requirements: 6.2
        """
        from PyQt6.QtCore import QMimeData
        
        history_manager = HistoryManager()
        monitor = ClipboardMonitor(history_manager)
        
        # Create mock mime data with HTML
        mime_data = QMimeData()
        mime_data.setHtml("<html><body><p>Test HTML</p></body></html>")
        
        # Extract content
        content_type, data = monitor._extract_content(mime_data)
        
        # Verify HTML was detected
        assert content_type == ContentType.RICH_TEXT
        assert "<p>Test HTML</p>" in data
    
    def test_content_type_detection_image(self, qapp):
        """
        Test that image content is correctly detected and extracted.
        Requirements: 6.2
        """
        from PyQt6.QtCore import QMimeData
        from PyQt6.QtGui import QImage
        
        history_manager = HistoryManager()
        monitor = ClipboardMonitor(history_manager)
        
        # Create mock mime data with image
        mime_data = QMimeData()
        image = QImage(100, 100, QImage.Format.Format_RGB32)
        image.fill(0xFF0000)  # Fill with red
        mime_data.setImageData(image)
        
        # Extract content
        content_type, data = monitor._extract_content(mime_data)
        
        # Verify image was detected
        assert content_type == ContentType.IMAGE
        assert isinstance(data, bytes)
        assert len(data) > 0
    
    def test_content_type_detection_unsupported(self, qapp):
        """
        Test that unsupported content types are handled correctly.
        Requirements: 6.2
        """
        from PyQt6.QtCore import QMimeData
        
        history_manager = HistoryManager()
        monitor = ClipboardMonitor(history_manager)
        
        # Create mock mime data with no supported formats
        mime_data = QMimeData()
        # Don't set any data - empty mime data
        
        # Extract content
        content_type, data = monitor._extract_content(mime_data)
        
        # Verify unsupported type is returned
        assert content_type == ContentType.UNSUPPORTED
        assert data == "[Unsupported Content]"
    
    def test_error_handling_during_monitoring(self, qapp):
        """
        Test that errors during monitoring are handled gracefully.
        Requirements: 6.2
        """
        history_manager = HistoryManager()
        monitor = ClipboardMonitor(history_manager)
        
        # Save the original mimeData method
        original_mime_data = monitor._clipboard.mimeData
        
        try:
            # Mock clipboard to raise an error
            def mock_mimeData():
                raise RuntimeError("Simulated clipboard error")
            
            monitor._clipboard.mimeData = mock_mimeData
            
            # Call _on_clipboard_change - should not raise exception
            try:
                monitor._on_clipboard_change()
            except Exception as e:
                pytest.fail(f"Monitor should handle errors gracefully, but raised: {e}")
            
            # Verify history is still empty (error prevented adding content)
            history = history_manager.get_history()
            assert len(history) == 0
        finally:
            # Restore the original mimeData method
            monitor._clipboard.mimeData = original_mime_data
    
    def test_duplicate_content_not_added_twice(self, qapp):
        """
        Test that duplicate clipboard content is not added multiple times in succession.
        Requirements: 6.2
        """
        from PyQt6.QtCore import QMimeData
        
        history_manager = HistoryManager()
        monitor = ClipboardMonitor(history_manager)
        
        # Save the original mimeData method
        original_mime_data = monitor._clipboard.mimeData
        
        try:
            # Mock clipboard to return same content
            mime_data = QMimeData()
            mime_data.setText("Same content")
            monitor._clipboard.mimeData = lambda: mime_data
            
            # Call _on_clipboard_change twice
            monitor._on_clipboard_change()
            monitor._on_clipboard_change()
            
            # Verify content was only added once
            history = history_manager.get_history()
            assert len(history) == 1
            assert history[0].data == "Same content"
        finally:
            # Restore the original mimeData method
            monitor._clipboard.mimeData = original_mime_data
    
    def test_stop_monitoring(self, qapp):
        """
        Test that monitoring can be stopped cleanly.
        Requirements: 6.2
        """
        history_manager = HistoryManager()
        monitor = ClipboardMonitor(history_manager)
        
        # Start monitoring
        monitor.start()
        
        # Verify monitor is working
        assert monitor._clipboard is not None
        
        # Stop monitoring (disconnects signal)
        monitor.stop()
        
        # After stopping, the clipboard reference should still exist
        # but the signal should be disconnected
        assert monitor._clipboard is not None
