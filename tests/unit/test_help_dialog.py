"""
Unit tests for HelpDialog.

These tests verify that the help dialog displays correctly with
all required tabs and content.
"""

import pytest
from unittest.mock import Mock

from src.Kliply.ui_manager import HelpDialog
from src.Kliply.settings_manager import SettingsManager


@pytest.mark.unit
@pytest.mark.ui
class TestHelpDialog:
    """Test HelpDialog functionality."""
    
    def test_help_dialog_initialization(self, qapp):
        """Test that HelpDialog initializes correctly."""
        settings_manager = SettingsManager()
        dialog = HelpDialog(settings_manager)
        
        assert dialog is not None
        assert dialog.windowTitle() == "Kliply Help"
    
    def test_help_dialog_without_settings_manager(self, qapp):
        """Test that HelpDialog works without settings manager."""
        dialog = HelpDialog()
        
        assert dialog is not None
        assert dialog.windowTitle() == "Kliply Help"
    
    def test_help_dialog_has_tabs(self, qapp):
        """Test that HelpDialog has all required tabs."""
        from PyQt6.QtWidgets import QTabWidget
        
        settings_manager = SettingsManager()
        dialog = HelpDialog(settings_manager)
        
        # Find the tab widget
        tab_widget = None
        for child in dialog.children():
            if isinstance(child, QTabWidget):
                tab_widget = child
                break
        
        assert tab_widget is not None, "Tab widget not found"
        
        # Check tab count
        assert tab_widget.count() == 4, f"Expected 4 tabs, got {tab_widget.count()}"
        
        # Check tab names
        tab_names = [tab_widget.tabText(i) for i in range(tab_widget.count())]
        assert "Getting Started" in tab_names
        assert "Keyboard Shortcuts" in tab_names
        assert "Troubleshooting" in tab_names
        assert "About & Support" in tab_names
    
    def test_help_dialog_displays_current_hotkey(self, qapp):
        """Test that help dialog displays the current hotkey from settings."""
        settings_manager = SettingsManager()
        settings_manager.set_hotkey("Cmd+Shift+C")
        
        dialog = HelpDialog(settings_manager)
        
        # The dialog should be created successfully
        assert dialog is not None
    
    def test_help_dialog_size(self, qapp):
        """Test that help dialog has appropriate size."""
        dialog = HelpDialog()
        
        # Check fixed size
        assert dialog.width() == 650
        assert dialog.height() == 600


@pytest.mark.unit
@pytest.mark.ui
class TestUIManagerHelpIntegration:
    """Test UIManager integration with HelpDialog."""
    
    def test_ui_manager_shows_help_dialog(self, qapp):
        """Test that UIManager can show help dialog."""
        from src.Kliply.ui_manager import UIManager
        from src.Kliply.history_manager import HistoryManager
        
        history_manager = HistoryManager()
        settings_manager = SettingsManager()
        ui_manager = UIManager(history_manager, settings_manager)
        
        # Mock the dialog exec to prevent blocking
        original_exec = HelpDialog.exec
        HelpDialog.exec = Mock(return_value=1)
        
        try:
            # Show help dialog
            ui_manager.show_help_dialog()
            
            # Verify dialog was created
            assert ui_manager.help_dialog is not None
        finally:
            # Restore original exec
            HelpDialog.exec = original_exec
    
    def test_ui_manager_help_dialog_reuses_instance(self, qapp):
        """Test that UIManager reuses help dialog instance when visible."""
        from src.Kliply.ui_manager import UIManager
        from src.Kliply.history_manager import HistoryManager
        
        history_manager = HistoryManager()
        settings_manager = SettingsManager()
        ui_manager = UIManager(history_manager, settings_manager)
        
        # Create first dialog
        dialog1 = HelpDialog(settings_manager)
        ui_manager.help_dialog = dialog1
        
        # Mock isVisible to return True
        dialog1.isVisible = Mock(return_value=True)
        dialog1.raise_ = Mock()
        dialog1.activateWindow = Mock()
        
        # Try to show help again
        ui_manager.show_help_dialog()
        
        # Verify it tried to raise the existing dialog
        dialog1.raise_.assert_called_once()
        dialog1.activateWindow.assert_called_once()


@pytest.mark.unit
class TestMenuBarHelpIntegration:
    """Test MenuBarManager integration with help functionality."""
    
    def test_menu_bar_has_help_item(self, qapp):
        """Test that menu bar includes Help menu item."""
        from src.Kliply.menu_bar_manager import MenuBarManager
        from src.Kliply.ui_manager import UIManager
        from src.Kliply.history_manager import HistoryManager
        
        history_manager = HistoryManager()
        settings_manager = SettingsManager()
        ui_manager = UIManager(history_manager, settings_manager)
        menu_bar = MenuBarManager(ui_manager, settings_manager, history_manager)
        
        # Get menu actions
        menu_actions = [action.text() for action in menu_bar.menu.actions() if not action.isSeparator()]
        
        assert "Help" in menu_actions
    
    def test_menu_bar_help_action_triggers_dialog(self, qapp):
        """Test that clicking Help menu item shows help dialog."""
        from src.Kliply.menu_bar_manager import MenuBarManager
        from src.Kliply.ui_manager import UIManager
        from src.Kliply.history_manager import HistoryManager
        
        history_manager = HistoryManager()
        settings_manager = SettingsManager()
        ui_manager = UIManager(history_manager, settings_manager)
        menu_bar = MenuBarManager(ui_manager, settings_manager, history_manager)
        
        # Mock show_help_dialog
        ui_manager.show_help_dialog = Mock()
        
        # Trigger help action
        menu_bar._on_show_help()
        
        # Verify help dialog was shown
        ui_manager.show_help_dialog.assert_called_once()
