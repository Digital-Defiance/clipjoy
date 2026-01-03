"""
Property-based tests for clipboard monitoring.

Feature: Kliply
"""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.Kliply.models import ClipboardContent, ContentType
from src.Kliply.history_manager import HistoryManager
from src.Kliply.clipboard_monitor import ClipboardMonitor


@given(st.integers(min_value=1, max_value=10))
@settings(deadline=None)
def test_property_19_error_recovery_during_monitoring(num_errors):
    """
    Property 19: Error recovery during monitoring
    Validates: Requirements 9.5
    
    For any error that occurs during clipboard monitoring, the Clipboard_Manager
    should log the error and continue monitoring without crashing.
    """
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QMimeData
    
    # Ensure QApplication exists
    app = QApplication.instance()
    if app is None:
        from PyQt6.QtGui import QGuiApplication
        app = QGuiApplication([])
    
    history_manager = HistoryManager()
    monitor = ClipboardMonitor(history_manager)
    
    # Mock the clipboard to raise errors
    error_count = 0
    original_mimeData = monitor._clipboard.mimeData
    
    def mock_mimeData():
        nonlocal error_count
        if error_count < num_errors:
            error_count += 1
            raise RuntimeError(f"Simulated clipboard error {error_count}")
        # After errors, return valid data
        mime_data = QMimeData()
        mime_data.setText("Test content after error")
        return mime_data
    
    monitor._clipboard.mimeData = mock_mimeData
    
    # Call _on_clipboard_change multiple times
    # It should handle errors gracefully and continue
    for i in range(num_errors + 2):
        try:
            monitor._on_clipboard_change()
        except Exception as e:
            # The monitor should NOT raise exceptions - it should catch them
            pytest.fail(f"Monitor raised exception instead of handling it: {e}")
    
    # Verify that after errors, the monitor continues to work
    # The last call should have added content to history
    history = history_manager.get_history()
    assert len(history) > 0
    assert history[0].data == "Test content after error"
    
    # Restore original method
    monitor._clipboard.mimeData = original_mimeData
