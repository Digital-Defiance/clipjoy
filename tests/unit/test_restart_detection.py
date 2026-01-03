"""
Unit tests for restart detection after permission grant.

These tests verify that the restart dialog is shown only when
permissions change from denied to granted.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtCore import QTimer

from src.Kliply.main_application import MainApplication


@pytest.mark.unit
class TestRestartDetection:
    """Test restart detection after permission grant."""
    
    @patch('src.Kliply.main_application.MainApplication._start_clipboard_monitoring')
    @patch('src.Kliply.main_application.MainApplication._register_hotkey')
    @patch('src.Kliply.main_application.MainApplication._show_menu_bar')
    @patch('src.Kliply.main_application.MainApplication._show_welcome_if_needed')
    def test_restart_dialog_shown_when_permission_changes_from_false_to_true(
        self, mock_welcome, mock_menu_bar, mock_hotkey, mock_monitor, qapp
    ):
        """Test that restart dialog is shown when permission changes from False to True."""
        # Create application
        app = MainApplication()
        
        # Mock the permission manager to return False initially
        app.permission_manager.check_accessibility_permission = Mock(return_value=False)
        
        # Mock the UI manager's show_restart_dialog
        app.ui_manager.show_restart_dialog = Mock()
        
        # Start permission monitoring (should record initial state as False)
        app._start_permission_monitoring()
        
        # Verify initial state was recorded as False
        assert app._initial_permission_state is False
        
        # Now simulate permission being granted
        app.permission_manager.check_accessibility_permission = Mock(return_value=True)
        
        # Manually call the check method that the timer invokes
        import time
        app._permission_last_check_time = time.time() - 3.0  # Force check
        app._check_permission_status()
        
        # Process events to allow callbacks to execute
        qapp.processEvents()
        
        # Verify restart dialog was shown
        app.ui_manager.show_restart_dialog.assert_called_once()
    
    @patch('src.Kliply.main_application.MainApplication._start_clipboard_monitoring')
    @patch('src.Kliply.main_application.MainApplication._register_hotkey')
    @patch('src.Kliply.main_application.MainApplication._show_menu_bar')
    @patch('src.Kliply.main_application.MainApplication._show_welcome_if_needed')
    def test_restart_dialog_not_shown_when_permission_already_granted(
        self, mock_welcome, mock_menu_bar, mock_hotkey, mock_monitor, qapp
    ):
        """Test that restart dialog is NOT shown when permission is already granted."""
        # Create application
        app = MainApplication()
        
        # Mock the permission manager to return True initially
        app.permission_manager.check_accessibility_permission = Mock(return_value=True)
        
        # Mock the UI manager's show_restart_dialog
        app.ui_manager.show_restart_dialog = Mock()
        
        # Start permission monitoring (should record initial state as True)
        app._start_permission_monitoring()
        
        # Verify initial state was recorded as True
        assert app._initial_permission_state is True
        
        # Permission remains True
        app.permission_manager.check_accessibility_permission = Mock(return_value=True)
        
        # Manually call the check method
        import time
        app._permission_last_check_time = time.time() - 3.0  # Force check
        app._check_permission_status()
        
        # Process events
        qapp.processEvents()
        
        # Verify restart dialog was NOT shown (because permission didn't change)
        app.ui_manager.show_restart_dialog.assert_not_called()
    
    @patch('src.Kliply.main_application.MainApplication._start_clipboard_monitoring')
    @patch('src.Kliply.main_application.MainApplication._register_hotkey')
    @patch('src.Kliply.main_application.MainApplication._show_menu_bar')
    @patch('src.Kliply.main_application.MainApplication._show_welcome_if_needed')
    def test_permission_monitoring_stops_after_permission_granted(
        self, mock_welcome, mock_menu_bar, mock_hotkey, mock_monitor, qapp
    ):
        """Test that permission monitoring stops after permission is granted."""
        # Create application
        app = MainApplication()
        
        # Mock the permission manager to return False initially
        app.permission_manager.check_accessibility_permission = Mock(return_value=False)
        
        # Mock the UI manager's show_restart_dialog
        app.ui_manager.show_restart_dialog = Mock()
        
        # Start permission monitoring
        app._start_permission_monitoring()
        
        # Verify monitoring is active
        assert app._permission_monitoring_active
        
        # Now simulate permission being granted
        app.permission_manager.check_accessibility_permission = Mock(return_value=True)
        
        # Manually call the check method
        import time
        app._permission_last_check_time = time.time() - 3.0  # Force check
        app._check_permission_status()
        
        # Process events
        qapp.processEvents()
        
        # Verify monitoring was stopped
        assert not app._permission_monitoring_active
    
    @patch('src.Kliply.main_application.MainApplication._start_clipboard_monitoring')
    @patch('src.Kliply.main_application.MainApplication._register_hotkey')
    @patch('src.Kliply.main_application.MainApplication._show_menu_bar')
    @patch('src.Kliply.main_application.MainApplication._show_welcome_if_needed')
    def test_permission_monitoring_stops_after_timeout(
        self, mock_welcome, mock_menu_bar, mock_hotkey, mock_monitor, qapp
    ):
        """Test that permission monitoring stops after max attempts."""
        # Create application
        app = MainApplication()
        
        # Mock the permission manager to always return False
        app.permission_manager.check_accessibility_permission = Mock(return_value=False)
        
        # Mock the UI manager's show_restart_dialog
        app.ui_manager.show_restart_dialog = Mock()
        
        # Start permission monitoring
        app._start_permission_monitoring()
        
        # Simulate max attempts by setting the counter
        app._permission_check_count = app._max_permission_checks
        
        # Manually call the check method
        import time
        app._permission_last_check_time = time.time() - 3.0  # Force check
        app._check_permission_status()
        
        # Process events
        qapp.processEvents()
        
        # Verify monitoring was stopped
        assert not app._permission_monitoring_active
        
        # Verify restart dialog was NOT shown
        app.ui_manager.show_restart_dialog.assert_not_called()

    @patch('src.Kliply.main_application.MainApplication._start_clipboard_monitoring')
    @patch('src.Kliply.main_application.MainApplication._register_hotkey')
    @patch('src.Kliply.main_application.MainApplication._show_menu_bar')
    @patch('src.Kliply.main_application.MainApplication._show_welcome_if_needed')
    def test_permission_revocation_disables_hotkey_and_prompts_user(
        self, mock_welcome, mock_menu_bar, mock_hotkey, mock_monitor, qapp
    ):
        """Ensure revoking permissions disables the hotkey and informs the user."""
        app = MainApplication()
        app._hotkey_registered = True
        app._last_permission_state = True
        app.hotkey_handler.unregister_hotkey = Mock()
        app.menu_bar_manager.update_menu = Mock()
        app.ui_manager.show_permission_dialog = Mock()
        app.permission_manager.check_accessibility_permission = Mock(return_value=False)
        
        with patch.object(app, '_start_permission_monitoring') as mock_start_monitor:
            app._check_permission_revocation()
        
        app.hotkey_handler.unregister_hotkey.assert_called_once()
        app.menu_bar_manager.update_menu.assert_called_once()
        app.ui_manager.show_permission_dialog.assert_called_once()
        mock_start_monitor.assert_called_once()
        assert app._hotkey_registered is False
        assert app._permission_revocation_notified is True
    
    @patch('src.Kliply.main_application.MainApplication._start_clipboard_monitoring')
    @patch('src.Kliply.main_application.MainApplication._register_hotkey')
    @patch('src.Kliply.main_application.MainApplication._show_menu_bar')
    @patch('src.Kliply.main_application.MainApplication._show_welcome_if_needed')
    def test_permission_revocation_notification_resets_when_restored(
        self, mock_welcome, mock_menu_bar, mock_hotkey, mock_monitor, qapp
    ):
        """Ensure notification flag clears once permission returns."""
        app = MainApplication()
        app._permission_revocation_notified = True
        app._last_permission_state = False
        app.permission_manager.check_accessibility_permission = Mock(return_value=True)
        
        app._check_permission_revocation()
        
        assert app._permission_revocation_notified is False
        assert app._last_permission_state is True
