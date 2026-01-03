"""
Main Application for Kliply clipboard manager.

This module contains the main application class that wires all components
together and manages the application lifecycle.
"""

import sys
import signal
import logging
from typing import Optional

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from src.Kliply.logging_config import setup_logging
from src.Kliply.models import Settings
from src.Kliply.history_manager import HistoryManager
from src.Kliply.clipboard_monitor import ClipboardMonitor
from src.Kliply.settings_manager import SettingsManager
from src.Kliply.hotkey_handler_macos import HotkeyHandlerMacOS
from src.Kliply.ui_manager import UIManager
from src.Kliply.menu_bar_manager import MenuBarManager
from src.Kliply.permission_manager import PermissionManager
from src.Kliply.onboarding_manager import OnboardingManager

# Module-level logger
logger = logging.getLogger(__name__)


class MainApplication:
    """
    Main application class for Kliply.
    
    This class initializes all components, wires them together, and manages
    the application lifecycle including startup, shutdown, and signal handling.
    
    Attributes:
        app: QApplication instance
        history_manager: Manages clipboard history
        settings_manager: Manages user preferences
        clipboard_monitor: Monitors system clipboard
        ui_manager: Manages UI components
        hotkey_handler: Handles global hotkeys
        menu_bar_manager: Manages menu bar icon and menu
        permission_manager: Manages macOS permissions
        onboarding_manager: Manages first-run experience
    """
    
    def __init__(self):
        """Initialize the main application and all components."""
        # Set up logging first
        setup_logging(log_level=logging.INFO, console_output=True)
        
        logger.info("Initializing Kliply application...")
        
        try:
            # Initialize QApplication
            self.app = QApplication.instance()
            if self.app is None:
                self.app = QApplication(sys.argv)
            
            # Set application metadata
            self.app.setApplicationName("Kliply")
            self.app.setOrganizationName("Kliply")
            self.app.setApplicationVersion("1.0.0")
            
            # Initialize core managers
            self.settings_manager = SettingsManager()
            self.history_manager = HistoryManager(
                max_depth=self.settings_manager.get_clipboard_depth()
            )
            
            # Initialize permission manager
            self.permission_manager = PermissionManager()
            
            # Initialize clipboard monitor (before UI manager so it can be passed)
            self.clipboard_monitor = ClipboardMonitor(
                history_manager=self.history_manager
            )
            
            # Initialize UI manager
            self.ui_manager = UIManager(
                history_manager=self.history_manager,
                settings_manager=self.settings_manager,
                clipboard_monitor=self.clipboard_monitor
            )
            
            # Set up callback for when popup closes to reset hotkey state
            self.ui_manager.set_on_popup_close_callback(self._on_popup_closed)
            
            # Initialize onboarding manager
            self.onboarding_manager = OnboardingManager(
                settings_manager=self.settings_manager
            )
            
            # Wire onboarding manager with UI manager
            self.onboarding_manager.set_ui_manager(self.ui_manager)
            self.ui_manager.set_onboarding_manager(self.onboarding_manager)
            
            logger.info("All components initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}", exc_info=True)
            raise
        
        # Initialize hotkey handler with callback to show popup
        self.hotkey_handler = HotkeyHandlerMacOS(
            callback=self._on_hotkey_pressed
        )
        
        # Initialize menu bar manager
        self.menu_bar_manager = MenuBarManager(
            ui_manager=self.ui_manager,
            settings_manager=self.settings_manager,
            history_manager=self.history_manager,
            permission_manager=self.permission_manager,
            onboarding_manager=self.onboarding_manager
        )
        
        # Track permission state to detect runtime revocations
        self._hotkey_registered = False
        self._permission_monitoring_active = False
        self._permission_check_count = 0
        self._max_permission_checks = 0
        self._permission_last_check_time = 0.0
        self._revocation_check_interval = 5.0  # seconds between passive checks
        self._revocation_last_check_time = 0.0
        self._last_permission_state = self.permission_manager.status.accessibility
        self._permission_revocation_notified = False
        
        # Set up signal handlers for clean shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Set up a timer to allow Ctrl+C to work AND check permissions
        self._timer = QTimer()
        self._timer.timeout.connect(self._on_timer_tick)
        self._timer.start(1000)  # 1 second interval instead of 100ms
        
        logger.info("Kliply application initialized successfully")
    
    def _on_timer_tick(self):
        """
        Called every 1000ms (1 second) by the main application timer.
        
        This handles permission monitoring by checking every 2 seconds.
        """
        import time
        current_time = time.time()
        
        if self._permission_monitoring_active:
            if current_time - self._permission_last_check_time >= 2.0:
                self._permission_last_check_time = current_time
                self._check_permission_status()
            return
        
        # When not actively monitoring for a grant, periodically check for revocations
        if current_time - self._revocation_last_check_time >= self._revocation_check_interval:
            self._revocation_last_check_time = current_time
            self._check_permission_revocation()
    
    def _check_permission_revocation(self):
        """Detect accessibility permission loss while the app is running."""
        has_permission = self.permission_manager.check_accessibility_permission()
        
        if has_permission:
            # Reset notification state so we can warn again on future revocations
            self._last_permission_state = True
            self._permission_revocation_notified = False
            return
        
        if self._last_permission_state:
            self._handle_permission_loss()
        else:
            self._last_permission_state = False
    
    def _handle_permission_loss(self):
        """Disable hotkey registration if permissions were revoked."""
        logger.warning("Accessibility permission revoked - entering degraded mode")
        self._last_permission_state = False
        
        if self._hotkey_registered:
            try:
                self.hotkey_handler.unregister_hotkey()
            finally:
                self._hotkey_registered = False
            logger.warning("Global hotkey disabled due to missing permissions")
        
        # Update UI cues so the user can re-open permissions from the menu
        if self.menu_bar_manager:
            self.menu_bar_manager.update_menu()
        
        # Only show the permission dialog once per revocation event
        if not self._permission_revocation_notified:
            self._permission_revocation_notified = True
            try:
                self.ui_manager.show_permission_dialog("accessibility")
            except Exception as dialog_error:
                logger.error(f"Failed to show permission dialog: {dialog_error}", exc_info=True)
        
        # Begin polling so we can inform the user when permissions are restored
        if not self._permission_monitoring_active:
            self._start_permission_monitoring()
    
    def _on_hotkey_pressed(self):
        """
        Callback for when the global hotkey is pressed.
        
        This method is called by the HotkeyHandler when the user presses
        the configured hotkey (default: Cmd+Shift+V).
        """
        logger.info("Hotkey pressed, showing history popup")
        self.ui_manager.show_history_popup()
    
    def _on_popup_closed(self):
        """
        Callback for when the history popup closes.
        
        This resets the hotkey handler state so the hotkey can be triggered again.
        """
        logger.info("Popup closed callback triggered, resetting hotkey state")
        self.hotkey_handler.reset_popup_state()
        logger.info("Hotkey state reset complete")
    
    def _show_welcome_if_needed(self):
        """
        Show welcome screen on first launch.
        
        This method checks if this is the first launch and shows the
        welcome screen if needed.
        """
        if self.onboarding_manager.should_show_welcome():
            logger.info("First launch detected, showing welcome screen")
            
            # Show welcome screen
            should_mark_complete = self.ui_manager.show_welcome_screen()
            
            # Mark welcome as complete if user checked the box
            if should_mark_complete:
                self.onboarding_manager.mark_welcome_complete()
                logger.info("Welcome screen marked as complete")
    
    def _start_clipboard_monitoring(self):
        """
        Start the clipboard monitor.
        
        This begins monitoring the system clipboard for changes.
        """
        logger.info("Starting clipboard monitor...")
        self.clipboard_monitor.start()
        logger.info("Clipboard monitor started")
    
    def _register_hotkey(self) -> bool:
        """
        Register the global hotkey.
        
        Returns:
            True if hotkey was registered successfully, False otherwise.
        """
        hotkey = self.settings_manager.get_hotkey()
        logger.info(f"Registering global hotkey: {hotkey}")
        
        success = self.hotkey_handler.register_hotkey(hotkey)
        
        if success:
            self._hotkey_registered = True
            self._last_permission_state = True
            self._permission_revocation_notified = False
            logger.info("Global hotkey registered successfully")
        else:
            self._hotkey_registered = False
            logger.warning("Failed to register global hotkey")
            logger.warning("Application will run in degraded mode (menu bar only)")
        
        return success
    
    def _show_menu_bar(self):
        """Show the menu bar icon."""
        logger.info("Showing menu bar icon...")
        self.menu_bar_manager.show()
        logger.info("Menu bar icon shown")
    
    def _check_permission_status(self):
        """Check if permission was granted and show restart dialog."""
        if not hasattr(self, '_permission_check_count'):
            return  # Monitoring not active
            
        self._permission_check_count += 1
        logger.info(f"Permission check #{self._permission_check_count}/{self._max_permission_checks}")
        
        # Check if permission is now granted
        has_permission = self.permission_manager.check_accessibility_permission()
        logger.info(f"Current permission state: {has_permission}, Initial state: {self._initial_permission_state}")
        self._last_permission_state = has_permission
        if has_permission:
            self._permission_revocation_notified = False
        
        # Only show restart dialog if permission state changed from False to True
        if has_permission and not self._initial_permission_state:
            logger.info("Accessibility permission granted! Showing restart dialog...")
            
            # Stop monitoring
            self._permission_monitoring_active = False
            
            # Show restart dialog
            self.ui_manager.show_restart_dialog()
            
        elif self._permission_check_count >= self._max_permission_checks:
            # Stop checking after max attempts
            logger.info("Permission monitoring timeout - stopping checks")
            self._permission_monitoring_active = False
    
    def _start_permission_monitoring(self):
        """
        Start monitoring for Accessibility permission grant.
        
        This method sets up a timer that periodically checks if the user
        has granted Accessibility permission, and shows a restart dialog
        when permission is detected.
        """
        import time
        
        logger.info("Starting permission monitoring...")
        
        if self._permission_monitoring_active:
            logger.info("Permission monitoring already active")
            return
        
        # Record the initial permission state (should be False when this is called)
        self._initial_permission_state = self.permission_manager.check_accessibility_permission()
        logger.info(f"Initial permission state: {self._initial_permission_state}")
        
        # Initialize counter and timing
        self._permission_check_count = 0
        self._max_permission_checks = 30  # Check for up to 60 seconds (30 * 2s)
        self._permission_monitoring_active = True
        # Set last check time to current time so first check happens in 2 seconds
        self._permission_last_check_time = time.time()
        self._last_permission_state = self._initial_permission_state
        
        logger.info(f"Permission monitoring started - will check every 2 seconds for up to {self._max_permission_checks * 2} seconds")
        logger.info("Monitoring will use the main application timer")
    
    def _signal_handler(self, signum, frame):
        """
        Handle system signals for clean shutdown.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        logger.info(f"Received signal {signum}, initiating shutdown...")
        self.quit()
    
    def quit(self):
        """
        Quit the application and clean up resources.
        
        This method stops all background processes and exits the application.
        """
        logger.info("Shutting down Kliply...")
        
        # Stop clipboard monitor
        if hasattr(self, 'clipboard_monitor'):
            logger.info("Stopping clipboard monitor...")
            self.clipboard_monitor.stop()
        
        # Unregister hotkey
        if hasattr(self, 'hotkey_handler'):
            logger.info("Unregistering hotkey...")
            self.hotkey_handler.unregister_hotkey()
            self._hotkey_registered = False
        
        # Hide menu bar icon
        if hasattr(self, 'menu_bar_manager'):
            logger.info("Hiding menu bar icon...")
            self.menu_bar_manager.hide()
        
        # Quit the application
        logger.info("Kliply shutdown complete")
        self.app.quit()
    
    def run(self) -> int:
        """
        Start the application event loop.
        
        This method performs the following steps:
        1. Show welcome screen on first launch
        2. Start clipboard monitoring
        3. Attempt to register global hotkey (triggers permission prompt if needed)
        4. Check permissions and show dialog if registration failed
        5. Show menu bar icon
        6. Start the Qt event loop
        
        Returns:
            Exit code (0 for success, non-zero for error)
        """
        try:
            logger.info("Starting Kliply application...")
            
            # Show welcome screen on first launch
            self._show_welcome_if_needed()
            
            # Start clipboard monitoring immediately
            self._start_clipboard_monitoring()
            
            # Show menu bar icon
            self._show_menu_bar()
            
            # Delay hotkey registration until after event loop starts
            # This is required on macOS because CGEventTap needs an active run loop
            def register_hotkey_delayed():
                """Register hotkey after Qt event loop has started."""
                logger.info("Attempting to register global hotkey...")
                hotkey_registered = self._register_hotkey()
                
                # If hotkey registration failed, check permissions and show dialog
                if not hotkey_registered:
                    logger.warning("Hotkey registration failed, checking permissions...")
                    has_permissions = self.permission_manager.check_accessibility_permission()
                    
                    if not has_permissions:
                        logger.warning("Accessibility permission not granted")
                        
                        # macOS already showed its system dialog with "Open System Settings" button
                        # We just need to start monitoring for when the user grants permission
                        logger.info("Starting permission monitoring...")
                        self._start_permission_monitoring()
                        logger.info("Permission monitoring started")
                        
                        logger.warning("Application will run in degraded mode (menu bar only)")
                    else:
                        logger.warning("Permissions granted but hotkey registration failed")
                        logger.warning("Application will run in degraded mode (menu bar only)")
                else:
                    logger.info("Global hotkey registered successfully")
            
            # Use QTimer to delay hotkey registration until event loop is running
            QTimer.singleShot(100, register_hotkey_delayed)
            
            logger.info("Kliply is now running!")
            logger.info(f"Hotkey: {self.settings_manager.get_hotkey()} (will be registered shortly)")
            logger.info("Use the menu bar icon to access clipboard history")
            
            # Start the event loop
            return self.app.exec()
        
        except Exception as e:
            logger.error(f"Fatal error during application startup: {e}", exc_info=True)
            return 1


def main():
    """
    Main entry point for the Kliply application.
    
    This function creates and runs the main application.
    """
    app = MainApplication()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
