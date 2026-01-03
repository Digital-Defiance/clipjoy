"""
Permission Manager for Kliply clipboard manager.

This module handles macOS permission requests and status checking,
particularly for Accessibility permissions required for global hotkeys.
"""

import subprocess
import logging
from datetime import datetime
from typing import Dict

from src.Kliply.models import PermissionStatus


logger = logging.getLogger(__name__)


class PermissionManager:
    """
    Manages macOS permissions for Kliply.
    
    This class handles checking and requesting Accessibility permissions,
    which are required for global hotkey functionality on macOS.
    """
    
    def __init__(self):
        """Initialize the PermissionManager."""
        self.status = PermissionStatus()
    
    def check_accessibility_permission(self) -> bool:
        """
        Check if Accessibility permissions are granted.
        
        Uses the ApplicationServices framework to check if the process is trusted
        for accessibility features.
        
        Returns:
            True if Accessibility permissions are granted, False otherwise.
        """
        try:
            # Use the ApplicationServices framework to check accessibility trust
            # This is the correct API for checking accessibility permissions
            from ApplicationServices import AXIsProcessTrusted
            
            has_permission = AXIsProcessTrusted()
            
            # Update status
            self.status.accessibility = has_permission
            self.status.last_checked = datetime.now()
            
            logger.info(f"Accessibility permission check: {has_permission}")
            return has_permission
            
        except Exception as e:
            logger.error(f"Error checking accessibility permission: {e}")
            # Fallback to False if we can't check
            return False
    
    def request_accessibility_permission(self) -> None:
        """
        Request Accessibility permissions from the user.
        
        This method attempts to trigger the system permission prompt by
        trying to access accessibility features. On modern macOS versions,
        this will show the system dialog asking the user to grant permissions.
        
        Note: The actual permission granting happens in System Preferences,
        so this method primarily serves to trigger the initial prompt.
        """
        try:
            # Attempt to access accessibility features to trigger the prompt
            # This will cause macOS to show the permission dialog if not already granted
            script = '''
            tell application "System Events"
                try
                    set frontApp to name of first application process whose frontmost is true
                    return frontApp
                on error
                    return "error"
                end try
            end tell
            '''
            
            subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            logger.info("Accessibility permission request triggered")
            
        except Exception as e:
            logger.error(f"Error requesting accessibility permission: {e}")
    
    def check_all_permissions(self) -> Dict[str, bool]:
        """
        Check all required permissions and return their status.
        
        Returns:
            Dictionary mapping permission names to their status (True/False).
            Currently only checks 'accessibility' permission.
        """
        return {
            'accessibility': self.check_accessibility_permission()
        }
    
    def open_system_preferences(self, pane: str = "security") -> None:
        """
        Open macOS System Preferences to a specific pane.
        
        Args:
            pane: The preference pane to open. Options include:
                  - "security" (default): Opens Security & Privacy preferences
                  - "accessibility": Opens Accessibility preferences (macOS 13+)
        
        Note: On macOS 13 (Ventura) and later, System Preferences was renamed
        to System Settings with a different URL scheme.
        """
        try:
            if pane == "security" or pane == "accessibility":
                # Try modern System Settings first (macOS 13+)
                # The accessibility settings are under Privacy & Security
                url = "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
                
                result = subprocess.run(
                    ['open', url],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode != 0:
                    # Fallback to older System Preferences (macOS 12 and earlier)
                    url = "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
                    subprocess.run(
                        ['open', url],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                
                logger.info(f"Opened System Preferences: {pane}")
            else:
                logger.warning(f"Unknown preference pane: {pane}")
                
        except Exception as e:
            logger.error(f"Error opening System Preferences: {e}")
    
    def get_permission_status(self) -> PermissionStatus:
        """
        Get the current permission status.
        
        Returns:
            PermissionStatus object with current permission states.
        """
        # Refresh status before returning
        self.check_accessibility_permission()
        return self.status
    
    def is_degraded_mode(self) -> bool:
        """
        Check if the application is running in degraded mode.
        
        Degraded mode means required permissions are not granted,
        so some features (like global hotkeys) will not work.
        
        Returns:
            True if running in degraded mode, False if all permissions granted.
        """
        return not self.status.all_granted()
