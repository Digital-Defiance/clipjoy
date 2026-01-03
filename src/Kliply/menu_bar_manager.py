"""
Menu Bar Manager for Kliply clipboard manager.

This module handles the system tray/menu bar integration, providing
quick access to Kliply features through a menu bar icon.
"""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt
import logging
from typing import Optional

from src.Kliply.ui_manager import UIManager
from src.Kliply.settings_manager import SettingsManager
from src.Kliply.history_manager import HistoryManager
from src.Kliply.permission_manager import PermissionManager


logger = logging.getLogger(__name__)


class MenuBarManager:
    """
    Manages the system tray/menu bar icon and menu for Kliply.
    
    This class provides a menu bar presence with quick access to:
    - Show History popup
    - Settings panel
    - Clear History
    - Show Welcome screen
    - Quit application
    
    It also displays a permission status indicator when permissions are denied.
    """
    
    def __init__(
        self,
        ui_manager: UIManager,
        settings_manager: SettingsManager,
        history_manager: HistoryManager,
        permission_manager: Optional[PermissionManager] = None,
        onboarding_manager: Optional[object] = None
    ):
        """
        Initialize the MenuBarManager.
        
        Args:
            ui_manager: The UIManager instance for showing UI components
            settings_manager: The SettingsManager instance for accessing settings
            history_manager: The HistoryManager instance for clearing history
            permission_manager: Optional PermissionManager for checking permission status
            onboarding_manager: Optional OnboardingManager for showing welcome screen
        """
        self.ui_manager = ui_manager
        self.settings_manager = settings_manager
        self.history_manager = history_manager
        self.permission_manager = permission_manager
        self.onboarding_manager = onboarding_manager
        
        self.tray_icon: Optional[QSystemTrayIcon] = None
        self.menu: Optional[QMenu] = None
        
        self._create_tray_icon()
        self.create_menu()
    
    def _create_tray_icon(self):
        """Create the system tray icon."""
        # Create a simple clipboard icon
        icon = self._create_clipboard_icon()
        
        self.tray_icon = QSystemTrayIcon(icon)
        self.tray_icon.setToolTip("Kliply - Clipboard Manager")
        
        logger.info("System tray icon created")
    
    def _create_clipboard_icon(self) -> QIcon:
        """
        Create a simple clipboard icon for the menu bar.
        
        Returns:
            QIcon with a clipboard symbol
        """
        # Create a 22x22 pixmap (standard menu bar icon size on macOS)
        pixmap = QPixmap(22, 22)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Draw a simple clipboard icon
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Use dark color for the icon (will be inverted by macOS in dark mode)
        painter.setPen(QColor(0, 0, 0))
        painter.setBrush(QColor(0, 0, 0))
        
        # Draw clipboard shape (simplified rectangle with clip at top)
        # Main body
        painter.drawRect(6, 8, 10, 12)
        # Clip at top
        painter.drawRect(9, 4, 4, 5)
        
        painter.end()
        
        return QIcon(pixmap)
    
    def create_menu(self):
        """
        Create the menu bar menu with all menu items.
        
        This method creates the context menu that appears when the user
        clicks on the menu bar icon.
        """
        self.menu = QMenu()
        
        # Get current hotkey for display
        hotkey = self.settings_manager.get_hotkey()
        
        # "Show History" menu item with hotkey label
        show_history_action = self.menu.addAction(f"Show History ({hotkey})")
        show_history_action.triggered.connect(self._on_show_history)
        
        # "Settings..." menu item
        settings_action = self.menu.addAction("Settings...")
        settings_action.triggered.connect(self._on_show_settings)
        
        # "Clear History" menu item
        clear_history_action = self.menu.addAction("Clear History")
        clear_history_action.triggered.connect(self._on_clear_history)
        
        # Separator
        self.menu.addSeparator()
        
        # "Help" menu item
        help_action = self.menu.addAction("Help")
        help_action.triggered.connect(self._on_show_help)
        
        # "Show Welcome" menu item (for re-accessing onboarding)
        show_welcome_action = self.menu.addAction("Show Welcome")
        show_welcome_action.triggered.connect(self._on_show_welcome)
        
        # Separator
        self.menu.addSeparator()
        
        # Permission status indicator (if permissions are denied)
        if self.permission_manager and self.permission_manager.is_degraded_mode():
            permission_action = self.menu.addAction("⚠️ Permissions Required")
            permission_action.triggered.connect(self._on_permission_indicator_clicked)
            self.menu.addSeparator()
        
        # "Quit" menu item
        quit_action = self.menu.addAction("Quit Kliply")
        quit_action.triggered.connect(self._on_quit)
        
        # Set the menu on the tray icon
        self.tray_icon.setContextMenu(self.menu)
        
        logger.info("Menu bar menu created")
    
    def update_menu(self):
        """
        Update the menu to reflect current state.
        
        This method recreates the menu to update the hotkey label
        and permission status indicator.
        """
        self.create_menu()
        logger.info("Menu bar menu updated")
    
    def show(self):
        """Show the system tray icon."""
        if self.tray_icon:
            self.tray_icon.show()
            logger.info("System tray icon shown")
    
    def hide(self):
        """Hide the system tray icon."""
        if self.tray_icon:
            self.tray_icon.hide()
            logger.info("System tray icon hidden")
    
    def _on_show_history(self):
        """Handle 'Show History' menu item click."""
        logger.info("Show History menu item clicked")
        self.ui_manager.show_history_popup()
    
    def _on_show_settings(self):
        """Handle 'Settings...' menu item click."""
        logger.info("Settings menu item clicked")
        self.ui_manager.show_settings_panel()
    
    def _on_clear_history(self):
        """Handle 'Clear History' menu item click."""
        logger.info("Clear History menu item clicked")
        self.history_manager.clear_history()
    
    def _on_show_welcome(self):
        """Handle 'Show Welcome' menu item click."""
        logger.info("Show Welcome menu item clicked")
        if self.onboarding_manager:
            self.onboarding_manager.show_welcome_screen()
        else:
            # Fallback to UI manager if no onboarding manager
            self.ui_manager.show_welcome_screen()
    
    def _on_show_help(self):
        """Handle 'Help' menu item click."""
        logger.info("Help menu item clicked")
        self.ui_manager.show_help_dialog()
    
    def _on_permission_indicator_clicked(self):
        """Handle permission indicator menu item click."""
        logger.info("Permission indicator clicked")
        if self.permission_manager:
            # Show permission dialog
            choice = self.ui_manager.show_permission_dialog("accessibility")
            if choice == "open_preferences":
                self.permission_manager.open_system_preferences("accessibility")
    
    def _on_quit(self):
        """Handle 'Quit' menu item click."""
        logger.info("Quit menu item clicked")
        # Import here to avoid circular dependency
        from PyQt6.QtWidgets import QApplication
        QApplication.quit()
