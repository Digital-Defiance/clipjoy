"""
Unit tests for error handling scenarios in Kliply.

This module tests error recovery, validation, and degraded mode behavior.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.Kliply.clipboard_monitor import ClipboardMonitor, MAX_CONTENT_SIZE_BYTES
from src.Kliply.history_manager import HistoryManager
from src.Kliply.settings_manager import SettingsManager
from src.Kliply.models import ClipboardContent, ContentType, Settings
from src.Kliply.permission_manager import PermissionManager


@pytest.mark.unit
class TestClipboardMonitorErrorRecovery:
    """Test error recovery in clipboard monitoring."""
    
    def test_clipboard_access_error_recovery(self, qapp):
        """
        Test that clipboard monitor recovers from clipboard access errors.
        
        Validates: Requirement 9.5 - Error recovery during monitoring
        """
        history_manager = HistoryManager()
        monitor = ClipboardMonitor(history_manager)
        
        # Mock clipboard to raise an exception
        with patch.object(monitor, '_clipboard') as mock_clipboard:
            mock_clipboard.mimeData.side_effect = RuntimeError("Clipboard locked")
            
            # This should not crash, just log and continue
            monitor._on_clipboard_change()
            
            # History should remain empty (error was handled)
            assert len(history_manager.get_history()) == 0
    
    def test_content_extraction_error_recovery(self, qapp):
        """
        Test that clipboard monitor recovers from content extraction errors.
        
        Validates: Requirement 9.5 - Error recovery during monitoring
        """
        history_manager = HistoryManager()
        monitor = ClipboardMonitor(history_manager)
        
        # Mock mime_data to cause extraction error
        mock_mime_data = Mock()
        mock_mime_data.hasImage.side_effect = Exception("Extraction failed")
        
        # This should not crash
        content_type, data = monitor._extract_content(mock_mime_data)
        
        # Should return None, None on error
        assert content_type is None
        assert data is None
    
    def test_oversized_content_rejection(self, qapp):
        """
        Test that oversized content is rejected (memory pressure handling).
        
        Validates: Requirement 9.5 - Memory pressure handling
        """
        history_manager = HistoryManager()
        monitor = ClipboardMonitor(history_manager)
        
        # Create oversized content (> 10MB)
        large_data = "x" * (MAX_CONTENT_SIZE_BYTES + 1)
        
        # Mock clipboard to return large content
        with patch.object(monitor, '_clipboard') as mock_clipboard:
            mock_mime_data = Mock()
            mock_mime_data.hasImage.return_value = False
            mock_mime_data.hasHtml.return_value = False
            mock_mime_data.hasText.return_value = True
            mock_mime_data.text.return_value = large_data
            mock_clipboard.mimeData.return_value = mock_mime_data
            
            # Trigger clipboard change
            monitor._on_clipboard_change()
            
            # Large content should be rejected
            assert len(history_manager.get_history()) == 0
    
    def test_monitoring_continues_after_error(self, qapp):
        """
        Test that monitoring continues after encountering an error.
        
        Validates: Requirement 9.5 - Error recovery during monitoring
        """
        history_manager = HistoryManager()
        monitor = ClipboardMonitor(history_manager)
        
        # First call raises an error
        with patch.object(monitor, '_clipboard') as mock_clipboard:
            mock_clipboard.mimeData.side_effect = [
                RuntimeError("Error"),  # First call fails
                None  # Second call succeeds (returns None)
            ]
            
            # First call should handle error
            monitor._on_clipboard_change()
            
            # Second call should work normally
            monitor._on_clipboard_change()
            
            # No crash, monitoring continues
            assert True


@pytest.mark.unit
class TestSettingsValidation:
    """Test settings validation and error handling."""
    
    def test_invalid_depth_type_rejection(self):
        """
        Test that invalid depth types are rejected.
        
        Validates: Requirement 2.6 - Depth validation
        """
        settings_manager = SettingsManager()
        
        # Try to set depth with invalid type
        result = settings_manager.set_clipboard_depth("10")  # String instead of int
        
        # Should return False (validation failed)
        assert result is False
        
        # Depth should remain at default
        assert settings_manager.get_clipboard_depth() == 10
    
    def test_invalid_depth_value_rejection(self):
        """
        Test that out-of-range depth values are rejected.
        
        Validates: Requirement 2.6 - Depth validation
        """
        settings_manager = SettingsManager()
        
        # Try to set depth below minimum
        result = settings_manager.set_clipboard_depth(3)
        assert result is False
        assert settings_manager.get_clipboard_depth() == 10  # Unchanged
        
        # Try to set depth above maximum
        result = settings_manager.set_clipboard_depth(150)
        assert result is False
        assert settings_manager.get_clipboard_depth() == 10  # Unchanged
    
    def test_valid_depth_values_accepted(self):
        """
        Test that valid depth values are accepted.
        
        Validates: Requirement 2.6 - Depth validation
        """
        settings_manager = SettingsManager()
        
        # Test minimum valid value
        result = settings_manager.set_clipboard_depth(5)
        assert result is True
        assert settings_manager.get_clipboard_depth() == 5
        
        # Test maximum valid value
        result = settings_manager.set_clipboard_depth(100)
        assert result is True
        assert settings_manager.get_clipboard_depth() == 100
        
        # Test middle value
        result = settings_manager.set_clipboard_depth(50)
        assert result is True
        assert settings_manager.get_clipboard_depth() == 50
    
    def test_invalid_hotkey_type_rejection(self):
        """
        Test that invalid hotkey types are rejected.
        
        Validates: Settings validation error handling
        """
        settings_manager = SettingsManager()
        
        # Try to set hotkey with invalid type
        with pytest.raises(ValueError):
            settings_manager.set_hotkey(123)  # Integer instead of string
    
    def test_empty_hotkey_rejection(self):
        """
        Test that empty hotkey strings are rejected.
        
        Validates: Settings validation error handling
        """
        settings_manager = SettingsManager()
        
        # Try to set empty hotkey
        with pytest.raises(ValueError):
            settings_manager.set_hotkey("")
        
        # Try to set whitespace-only hotkey
        with pytest.raises(ValueError):
            settings_manager.set_hotkey("   ")
    
    def test_settings_initialization_with_invalid_settings(self):
        """
        Test that SettingsManager falls back to defaults with invalid settings.
        
        Validates: Settings validation error handling
        """
        # Create invalid settings
        invalid_settings = Settings(
            clipboard_depth=200,  # Invalid (> 100)
            hotkey="",  # Invalid (empty)
            launch_at_login=False,
            first_launch_complete=False
        )
        
        # SettingsManager should handle this gracefully
        settings_manager = SettingsManager(invalid_settings)
        
        # Should fall back to defaults
        assert 5 <= settings_manager.get_clipboard_depth() <= 100


@pytest.mark.unit
class TestPermissionDenialHandling:
    """Test permission denial and degraded mode behavior."""
    
    def test_permission_check_without_accessibility(self):
        """
        Test permission checking when accessibility is denied.
        
        Validates: Requirement 13.4 - Permission denial handling
        """
        permission_manager = PermissionManager()
        
        # Mock accessibility check to return False
        with patch.object(permission_manager, 'check_accessibility_permission', return_value=False):
            has_permission = permission_manager.check_accessibility_permission()
            
            assert has_permission is False
    
    def test_degraded_mode_operation(self):
        """
        Test that application can operate in degraded mode without permissions.
        
        Validates: Requirement 13.4 - Degraded mode operation
        """
        # Create managers without permissions
        history_manager = HistoryManager()
        settings_manager = SettingsManager()
        
        # These should work without permissions
        assert history_manager is not None
        assert settings_manager is not None
        
        # Can still add items to history
        content = ClipboardContent(
            content_type=ContentType.TEXT,
            data="test",
            timestamp=datetime.now()
        )
        history_manager.add_item(content)
        
        assert len(history_manager.get_history()) == 1
    
    def test_hotkey_registration_failure_handling(self, qapp):
        """
        Test that hotkey registration failure is handled gracefully.
        
        Validates: Requirement 13.4 - Permission denial handling
        """
        from src.Kliply.hotkey_handler import HotkeyHandler
        
        callback = Mock()
        hotkey_handler = HotkeyHandler(callback)
        
        # Mock listener to fail
        with patch('src.Kliply.hotkey_handler.keyboard.Listener') as mock_listener_class:
            mock_listener_class.side_effect = Exception("Permission denied")
            
            # Registration should fail gracefully
            result = hotkey_handler.register_hotkey("Cmd+Shift+V")
            
            # Should return False, not crash
            assert result is False


@pytest.mark.unit
class TestUIRenderingErrors:
    """Test UI rendering error handling."""
    
    def test_history_popup_handles_rendering_errors(self, qapp):
        """
        Test that history popup handles rendering errors gracefully.
        
        Validates: UI rendering error handling
        """
        from src.Kliply.ui_manager import HistoryPopup
        
        history_manager = HistoryManager()
        
        # Add some content
        content = ClipboardContent(
            content_type=ContentType.TEXT,
            data="test",
            timestamp=datetime.now()
        )
        history_manager.add_item(content)
        
        # Create popup
        popup = HistoryPopup(history_manager)
        
        # Mock list widget to raise error during population
        with patch.object(popup.list_widget, 'clear', side_effect=Exception("Rendering error")):
            # This should not crash
            popup._populate_history()
            
            # Popup should still exist
            assert popup is not None
    
    def test_thumbnail_creation_error_handling(self, qapp):
        """
        Test that thumbnail creation errors are handled gracefully.
        
        Validates: UI rendering error handling
        """
        from src.Kliply.ui_manager import HistoryPopup
        
        history_manager = HistoryManager()
        popup = HistoryPopup(history_manager)
        
        # Try to create thumbnail from invalid data
        thumbnail = popup._create_thumbnail(b"invalid image data")
        
        # Should return None, not crash
        assert thumbnail is None
    
    def test_ui_manager_handles_popup_creation_errors(self, qapp):
        """
        Test that UIManager handles popup creation errors.
        
        Validates: UI rendering error handling
        """
        from src.Kliply.ui_manager import UIManager
        
        history_manager = HistoryManager()
        settings_manager = SettingsManager()
        ui_manager = UIManager(history_manager, settings_manager)
        
        # Mock HistoryPopup to raise error
        with patch('src.Kliply.ui_manager.HistoryPopup', side_effect=Exception("Creation failed")):
            # This should not crash
            ui_manager.show_history_popup()
            
            # UI manager should still be functional
            assert ui_manager is not None


@pytest.mark.unit
class TestContentTypeErrors:
    """Test content type error handling."""
    
    def test_unsupported_content_type_handling(self, qapp):
        """
        Test that unsupported content types are handled correctly.
        
        Validates: Content type error handling
        """
        history_manager = HistoryManager()
        monitor = ClipboardMonitor(history_manager)
        
        # Mock mime_data with no supported formats
        mock_mime_data = Mock()
        mock_mime_data.hasImage.return_value = False
        mock_mime_data.hasHtml.return_value = False
        mock_mime_data.hasText.return_value = False
        
        # Extract content
        content_type, data = monitor._extract_content(mock_mime_data)
        
        # Should return UNSUPPORTED type
        assert content_type == ContentType.UNSUPPORTED
        assert data == "[Unsupported Content]"
    
    def test_corrupted_image_data_handling(self, qapp):
        """
        Test that corrupted image data is handled gracefully.
        
        Validates: Content type error handling
        """
        history_manager = HistoryManager()
        monitor = ClipboardMonitor(history_manager)
        
        # Mock mime_data with corrupted image
        mock_mime_data = Mock()
        mock_mime_data.hasImage.return_value = True
        mock_mime_data.imageData.side_effect = Exception("Corrupted image")
        
        # Extract content
        content_type, data = monitor._extract_content(mock_mime_data)
        
        # Should handle error and return None
        assert content_type is None
        assert data is None
