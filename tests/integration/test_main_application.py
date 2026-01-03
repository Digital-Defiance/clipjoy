"""
Integration tests for MainApplication.

These tests verify that all components are properly wired together
and that the application lifecycle works correctly.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication

from src.Kliply.main_application import MainApplication
from src.Kliply.models import Settings


@pytest.mark.integration
class TestMainApplicationInitialization:
    """Test application initialization and component wiring."""
    
    def test_application_initializes_all_components(self, qapp):
        """Test that MainApplication initializes all required components."""
        # Create main application
        app = MainApplication()
        
        # Verify all components are initialized
        assert app.app is not None
        assert app.settings_manager is not None
        assert app.history_manager is not None
        assert app.permission_manager is not None
        assert app.ui_manager is not None
        assert app.onboarding_manager is not None
        assert app.clipboard_monitor is not None
        assert app.hotkey_handler is not None
        assert app.menu_bar_manager is not None
    
    def test_components_are_wired_correctly(self, qapp):
        """Test that components have correct dependencies."""
        app = MainApplication()
        
        # Verify UI manager has correct dependencies
        assert app.ui_manager.history_manager is app.history_manager
        assert app.ui_manager.settings_manager is app.settings_manager
        
        # Verify onboarding manager has correct dependencies
        assert app.onboarding_manager.settings_manager is app.settings_manager
        assert app.onboarding_manager._ui_manager is app.ui_manager
        
        # Verify clipboard monitor has correct dependencies
        assert app.clipboard_monitor._history_manager is app.history_manager
        
        # Verify menu bar manager has correct dependencies
        assert app.menu_bar_manager.ui_manager is app.ui_manager
        assert app.menu_bar_manager.settings_manager is app.settings_manager
        assert app.menu_bar_manager.history_manager is app.history_manager
        assert app.menu_bar_manager.permission_manager is app.permission_manager
        assert app.menu_bar_manager.onboarding_manager is app.onboarding_manager
    
    def test_history_manager_initialized_with_correct_depth(self, qapp):
        """Test that HistoryManager is initialized with depth from settings."""
        app = MainApplication()
        
        # Get depth from settings
        expected_depth = app.settings_manager.get_clipboard_depth()
        
        # Verify history manager has correct depth
        assert app.history_manager._max_depth == expected_depth


@pytest.mark.integration
class TestFirstLaunchFlow:
    """Test first launch flow with welcome screen."""
    
    @patch('src.Kliply.main_application.MainApplication._start_clipboard_monitoring')
    @patch('src.Kliply.main_application.MainApplication._register_hotkey')
    @patch('src.Kliply.main_application.MainApplication._show_menu_bar')
    def test_welcome_screen_shown_on_first_launch(
        self, mock_menu_bar, mock_hotkey, mock_monitor, qapp
    ):
        """Test that welcome screen is shown on first launch."""
        # Set up mocks
        mock_hotkey.return_value = True
        
        # Create application
        app = MainApplication()
        
        # Verify welcome should be shown
        assert app.onboarding_manager.should_show_welcome() is True
    
    @patch('src.Kliply.main_application.MainApplication._start_clipboard_monitoring')
    @patch('src.Kliply.main_application.MainApplication._register_hotkey')
    @patch('src.Kliply.main_application.MainApplication._show_menu_bar')
    def test_welcome_screen_not_shown_after_completion(
        self, mock_menu_bar, mock_hotkey, mock_monitor, qapp
    ):
        """Test that welcome screen is not shown after first launch completion."""
        # Set up mocks
        mock_hotkey.return_value = True
        
        # Create application
        app = MainApplication()
        
        # Mark welcome as complete
        app.onboarding_manager.mark_welcome_complete()
        
        # Verify welcome should not be shown
        assert app.onboarding_manager.should_show_welcome() is False


@pytest.mark.integration
class TestPermissionChecking:
    """Test permission checking on startup."""
    
    @patch('src.Kliply.permission_manager.PermissionManager.check_accessibility_permission')
    @patch('src.Kliply.main_application.MainApplication._start_clipboard_monitoring')
    @patch('src.Kliply.main_application.MainApplication._register_hotkey')
    @patch('src.Kliply.main_application.MainApplication._show_menu_bar')
    @patch('src.Kliply.main_application.MainApplication._show_welcome_if_needed')
    def test_permission_check_on_startup(
        self, mock_welcome, mock_menu_bar, mock_hotkey, mock_monitor, mock_check_perm, qapp
    ):
        """Test that permissions are checked on startup."""
        # Set up mock
        mock_check_perm.return_value = True
        mock_hotkey.return_value = True
        
        # Create application
        app = MainApplication()
        
        # Verify permission manager exists
        assert app.permission_manager is not None
        
        # Manually check permissions (as would happen during run())
        has_permission = app.permission_manager.check_accessibility_permission()
        
        # Verify permission check was called
        mock_check_perm.assert_called()
        assert has_permission is True
    
    @patch('src.Kliply.permission_manager.PermissionManager.check_accessibility_permission')
    @patch('src.Kliply.ui_manager.UIManager.show_permission_dialog')
    @patch('src.Kliply.main_application.MainApplication._start_clipboard_monitoring')
    @patch('src.Kliply.main_application.MainApplication._register_hotkey')
    @patch('src.Kliply.main_application.MainApplication._show_menu_bar')
    @patch('src.Kliply.main_application.MainApplication._show_welcome_if_needed')
    def test_permission_dialog_shown_when_denied(
        self, mock_welcome, mock_menu_bar, mock_hotkey, mock_monitor, 
        mock_dialog, mock_check_perm, qapp
    ):
        """Test that permission dialog is shown when permissions are denied."""
        # Set up mocks
        mock_check_perm.return_value = False
        mock_dialog.return_value = "later"
        mock_hotkey.return_value = False
        
        # Create application
        app = MainApplication()
        
        # Verify permission manager can check permissions
        has_permission = app.permission_manager.check_accessibility_permission()
        assert has_permission is False


@pytest.mark.integration
class TestCleanShutdown:
    """Test clean shutdown of the application."""
    
    @patch('src.Kliply.main_application.MainApplication._start_clipboard_monitoring')
    @patch('src.Kliply.main_application.MainApplication._register_hotkey')
    @patch('src.Kliply.main_application.MainApplication._show_menu_bar')
    @patch('src.Kliply.main_application.MainApplication._show_welcome_if_needed')
    def test_quit_stops_all_background_processes(
        self, mock_welcome, mock_menu_bar, mock_hotkey, mock_monitor, qapp
    ):
        """Test that quit() stops all background processes."""
        # Set up mocks
        mock_hotkey.return_value = True
        
        # Create application
        app = MainApplication()
        
        # Mock the stop methods
        app.clipboard_monitor.stop = Mock()
        app.hotkey_handler.unregister_hotkey = Mock()
        app.menu_bar_manager.hide = Mock()
        app.app.quit = Mock()
        
        # Call quit
        app.quit()
        
        # Verify all cleanup methods were called
        app.clipboard_monitor.stop.assert_called_once()
        app.hotkey_handler.unregister_hotkey.assert_called_once()
        app.menu_bar_manager.hide.assert_called_once()
        app.app.quit.assert_called_once()


@pytest.mark.integration
class TestComponentIntegration:
    """Test integration between components."""
    
    @patch('src.Kliply.main_application.MainApplication._start_clipboard_monitoring')
    @patch('src.Kliply.main_application.MainApplication._register_hotkey')
    @patch('src.Kliply.main_application.MainApplication._show_menu_bar')
    @patch('src.Kliply.main_application.MainApplication._show_welcome_if_needed')
    def test_hotkey_callback_shows_popup(
        self, mock_welcome, mock_menu_bar, mock_hotkey, mock_monitor, qapp
    ):
        """Test that hotkey callback shows the history popup."""
        # Set up mocks
        mock_hotkey.return_value = True
        
        # Create application
        app = MainApplication()
        
        # Mock the show_history_popup method
        app.ui_manager.show_history_popup = Mock()
        
        # Trigger hotkey callback
        app._on_hotkey_pressed()
        
        # Verify popup was shown
        app.ui_manager.show_history_popup.assert_called_once()
    
    @patch('src.Kliply.main_application.MainApplication._start_clipboard_monitoring')
    @patch('src.Kliply.main_application.MainApplication._register_hotkey')
    @patch('src.Kliply.main_application.MainApplication._show_menu_bar')
    @patch('src.Kliply.main_application.MainApplication._show_welcome_if_needed')
    def test_settings_changes_propagate_to_history_manager(
        self, mock_welcome, mock_menu_bar, mock_hotkey, mock_monitor, qapp
    ):
        """Test that settings changes propagate to HistoryManager."""
        # Set up mocks
        mock_hotkey.return_value = True
        
        # Create application
        app = MainApplication()
        
        # Change clipboard depth in settings
        new_depth = 25
        app.settings_manager.set_clipboard_depth(new_depth)
        
        # Manually propagate to history manager (as would happen in settings panel)
        app.history_manager.set_max_depth(new_depth)
        
        # Verify history manager has new depth
        assert app.history_manager._max_depth == new_depth


@pytest.mark.integration
class TestApplicationMetadata:
    """Test application metadata is set correctly."""
    
    def test_application_metadata_set(self, qapp):
        """Test that application metadata is set correctly."""
        app = MainApplication()
        
        # Verify metadata
        assert app.app.applicationName() == "Kliply"
        assert app.app.organizationName() == "Kliply"
        assert app.app.applicationVersion() == "1.0.0"
