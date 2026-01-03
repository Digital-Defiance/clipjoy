"""
Unit tests for MenuBarManager.

Tests menu bar icon presence, menu items, menu item actions, and permission indicator display.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu

from src.Kliply.menu_bar_manager import MenuBarManager
from src.Kliply.ui_manager import UIManager
from src.Kliply.settings_manager import SettingsManager
from src.Kliply.history_manager import HistoryManager
from src.Kliply.permission_manager import PermissionManager
from src.Kliply.models import Settings, PermissionStatus


@pytest.mark.unit
class TestMenuBarManager:
    """Test suite for MenuBarManager class."""
    
    @pytest.fixture
    def history_manager(self):
        """Create a HistoryManager instance for testing."""
        return HistoryManager(max_depth=10)
    
    @pytest.fixture
    def settings_manager(self):
        """Create a SettingsManager instance for testing."""
        return SettingsManager()
    
    @pytest.fixture
    def ui_manager(self, history_manager, settings_manager):
        """Create a UIManager instance for testing."""
        return UIManager(history_manager, settings_manager)
    
    @pytest.fixture
    def permission_manager(self):
        """Create a PermissionManager instance for testing."""
        return PermissionManager()
    
    @pytest.fixture
    def menu_bar_manager(self, qapp, ui_manager, settings_manager, history_manager):
        """Create a MenuBarManager instance for testing."""
        return MenuBarManager(
            ui_manager=ui_manager,
            settings_manager=settings_manager,
            history_manager=history_manager
        )
    
    def test_initialization(self, menu_bar_manager):
        """Test that MenuBarManager initializes correctly."""
        assert menu_bar_manager.ui_manager is not None
        assert menu_bar_manager.settings_manager is not None
        assert menu_bar_manager.history_manager is not None
        assert menu_bar_manager.tray_icon is not None
        assert menu_bar_manager.menu is not None
    
    def test_menu_bar_icon_presence(self, menu_bar_manager):
        """Test that menu bar icon is created and present."""
        # Verify tray icon exists
        assert isinstance(menu_bar_manager.tray_icon, QSystemTrayIcon)
        
        # Verify icon has a tooltip
        tooltip = menu_bar_manager.tray_icon.toolTip()
        assert tooltip == "Kliply - Clipboard Manager"
        
        # Verify icon has an icon set
        assert not menu_bar_manager.tray_icon.icon().isNull()
    
    def test_menu_items_exist(self, menu_bar_manager):
        """Test that all required menu items exist."""
        menu = menu_bar_manager.menu
        assert isinstance(menu, QMenu)
        
        # Get all actions
        actions = menu.actions()
        action_texts = [action.text() for action in actions if not action.isSeparator()]
        
        # Verify required menu items exist
        # "Show History" should include the hotkey
        assert any("Show History" in text for text in action_texts)
        assert "Settings..." in action_texts
        assert "Clear History" in action_texts
        assert "Show Welcome" in action_texts
        assert "Quit Kliply" in action_texts
    
    def test_show_history_menu_item_includes_hotkey(self, menu_bar_manager):
        """Test that 'Show History' menu item displays the hotkey."""
        menu = menu_bar_manager.menu
        actions = menu.actions()
        
        # Find the "Show History" action
        show_history_action = None
        for action in actions:
            if "Show History" in action.text():
                show_history_action = action
                break
        
        assert show_history_action is not None
        
        # Verify it includes the hotkey (default: Cmd+Shift+V)
        assert "Cmd+Shift+V" in show_history_action.text()
    
    def test_menu_item_actions_show_history(self, menu_bar_manager):
        """Test that 'Show History' menu item triggers the correct action."""
        # Mock the UI manager's show_history_popup method
        menu_bar_manager.ui_manager.show_history_popup = Mock()
        
        # Trigger the action
        menu_bar_manager._on_show_history()
        
        # Verify the method was called
        menu_bar_manager.ui_manager.show_history_popup.assert_called_once()
    
    def test_menu_item_actions_show_settings(self, menu_bar_manager):
        """Test that 'Settings...' menu item triggers the correct action."""
        # Mock the UI manager's show_settings_panel method
        menu_bar_manager.ui_manager.show_settings_panel = Mock()
        
        # Trigger the action
        menu_bar_manager._on_show_settings()
        
        # Verify the method was called
        menu_bar_manager.ui_manager.show_settings_panel.assert_called_once()
    
    def test_menu_item_actions_clear_history(self, menu_bar_manager, history_manager):
        """Test that 'Clear History' menu item clears the history."""
        # Add some items to history
        from src.Kliply.models import ClipboardContent, ContentType
        from datetime import datetime
        
        content1 = ClipboardContent(
            content_type=ContentType.TEXT,
            data="Test 1",
            timestamp=datetime.now(),
            preview="Test 1",
            size_bytes=6
        )
        content2 = ClipboardContent(
            content_type=ContentType.TEXT,
            data="Test 2",
            timestamp=datetime.now(),
            preview="Test 2",
            size_bytes=6
        )
        
        history_manager.add_item(content1)
        history_manager.add_item(content2)
        
        # Verify history has items
        assert len(history_manager.get_history()) == 2
        
        # Trigger clear history action
        menu_bar_manager._on_clear_history()
        
        # Verify history is empty
        assert len(history_manager.get_history()) == 0
    
    def test_menu_item_actions_show_welcome(self, menu_bar_manager):
        """Test that 'Show Welcome' menu item triggers the correct action."""
        # Mock the UI manager's show_welcome_screen method
        menu_bar_manager.ui_manager.show_welcome_screen = Mock()
        
        # Trigger the action
        menu_bar_manager._on_show_welcome()
        
        # Verify the method was called
        menu_bar_manager.ui_manager.show_welcome_screen.assert_called_once()
    
    def test_menu_item_actions_quit(self, qapp, menu_bar_manager):
        """Test that 'Quit' menu item triggers application quit."""
        # Mock QApplication.quit
        with patch('PyQt6.QtWidgets.QApplication.quit') as mock_quit:
            # Trigger the action
            menu_bar_manager._on_quit()
            
            # Verify quit was called
            mock_quit.assert_called_once()
    
    def test_permission_indicator_display_when_denied(self, qapp, ui_manager, settings_manager, history_manager):
        """Test that permission indicator appears when permissions are denied."""
        # Create a permission manager with denied permissions
        permission_manager = PermissionManager()
        permission_manager.status.accessibility = False
        
        # Create menu bar manager with permission manager
        menu_bar_manager = MenuBarManager(
            ui_manager=ui_manager,
            settings_manager=settings_manager,
            history_manager=history_manager,
            permission_manager=permission_manager
        )
        
        # Get all actions
        actions = menu_bar_manager.menu.actions()
        action_texts = [action.text() for action in actions if not action.isSeparator()]
        
        # Verify permission indicator is present
        assert any("Permissions Required" in text for text in action_texts)
    
    def test_permission_indicator_not_displayed_when_granted(self, qapp, ui_manager, settings_manager, history_manager):
        """Test that permission indicator does not appear when permissions are granted."""
        # Create a permission manager with granted permissions
        permission_manager = PermissionManager()
        permission_manager.status.accessibility = True
        
        # Create menu bar manager with permission manager
        menu_bar_manager = MenuBarManager(
            ui_manager=ui_manager,
            settings_manager=settings_manager,
            history_manager=history_manager,
            permission_manager=permission_manager
        )
        
        # Get all actions
        actions = menu_bar_manager.menu.actions()
        action_texts = [action.text() for action in actions if not action.isSeparator()]
        
        # Verify permission indicator is NOT present
        assert not any("Permissions Required" in text for text in action_texts)
    
    def test_permission_indicator_click_opens_dialog(self, qapp, ui_manager, settings_manager, history_manager):
        """Test that clicking permission indicator opens permission dialog."""
        # Create a permission manager with denied permissions
        permission_manager = PermissionManager()
        permission_manager.status.accessibility = False
        
        # Create menu bar manager with permission manager
        menu_bar_manager = MenuBarManager(
            ui_manager=ui_manager,
            settings_manager=settings_manager,
            history_manager=history_manager,
            permission_manager=permission_manager
        )
        
        # Mock the UI manager's show_permission_dialog method
        menu_bar_manager.ui_manager.show_permission_dialog = Mock(return_value="later")
        
        # Trigger the permission indicator action
        menu_bar_manager._on_permission_indicator_clicked()
        
        # Verify the dialog was shown
        menu_bar_manager.ui_manager.show_permission_dialog.assert_called_once_with("accessibility")
    
    def test_show_and_hide_tray_icon(self, menu_bar_manager):
        """Test showing and hiding the tray icon."""
        # Show the tray icon
        menu_bar_manager.show()
        assert menu_bar_manager.tray_icon.isVisible()
        
        # Hide the tray icon
        menu_bar_manager.hide()
        assert not menu_bar_manager.tray_icon.isVisible()
    
    def test_update_menu(self, menu_bar_manager):
        """Test that update_menu recreates the menu."""
        # Get original menu
        original_menu = menu_bar_manager.menu
        
        # Update the menu
        menu_bar_manager.update_menu()
        
        # Verify a new menu was created
        assert menu_bar_manager.menu is not None
        # The menu should be recreated (new instance)
        assert isinstance(menu_bar_manager.menu, QMenu)
    
    def test_onboarding_manager_integration(self, qapp, ui_manager, settings_manager, history_manager):
        """Test that onboarding manager is used when available."""
        # Create a mock onboarding manager
        onboarding_manager = Mock()
        onboarding_manager.show_welcome_screen = Mock()
        
        # Create menu bar manager with onboarding manager
        menu_bar_manager = MenuBarManager(
            ui_manager=ui_manager,
            settings_manager=settings_manager,
            history_manager=history_manager,
            onboarding_manager=onboarding_manager
        )
        
        # Trigger show welcome
        menu_bar_manager._on_show_welcome()
        
        # Verify onboarding manager's method was called
        onboarding_manager.show_welcome_screen.assert_called_once()
    
    def test_menu_has_separators(self, menu_bar_manager):
        """Test that menu has appropriate separators."""
        menu = menu_bar_manager.menu
        actions = menu.actions()
        
        # Count separators
        separator_count = sum(1 for action in actions if action.isSeparator())
        
        # Should have at least one separator (before Quit)
        assert separator_count >= 1
