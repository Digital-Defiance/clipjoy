"""
Onboarding Manager for Kliply clipboard manager.

This module manages the first-run experience and user education.
"""

from typing import Optional
from src.Kliply.settings_manager import SettingsManager


class OnboardingManager:
    """
    Manages first-run experience and user education.
    
    This class handles the welcome screen display logic and tracks
    whether the user has completed the initial onboarding flow.
    """
    
    def __init__(self, settings_manager: SettingsManager):
        """
        Initialize the OnboardingManager.
        
        Args:
            settings_manager: The SettingsManager instance for tracking first launch status
        """
        self.settings_manager = settings_manager
        self._ui_manager: Optional[object] = None  # Will be set later to avoid circular import
    
    def set_ui_manager(self, ui_manager):
        """
        Set the UI manager for displaying welcome screen.
        
        Args:
            ui_manager: The UIManager instance
        """
        self._ui_manager = ui_manager
    
    def should_show_welcome(self) -> bool:
        """
        Check if the welcome screen should be displayed.
        
        Returns:
            True if this is the first launch and welcome hasn't been shown,
            False otherwise.
        """
        settings = self.settings_manager.get_settings()
        return not settings.first_launch_complete
    
    def show_welcome_screen(self) -> None:
        """
        Display the welcome screen to the user.
        
        This method delegates to the UIManager to show the actual welcome dialog.
        """
        if self._ui_manager is not None:
            self._ui_manager.show_welcome_screen()
    
    def mark_welcome_complete(self) -> None:
        """
        Mark the welcome screen as completed.
        
        This updates the settings to indicate that the first launch
        experience has been completed and the welcome screen should
        not be shown again.
        """
        # Update the first_launch_complete flag in settings
        # We need to access the internal settings object
        settings = self.settings_manager.get_settings()
        settings.first_launch_complete = True
        
        # Update the settings manager's internal state
        # Since SettingsManager doesn't have a method to set first_launch_complete,
        # we need to update it directly through the internal _settings object
        with self.settings_manager._lock:
            self.settings_manager._settings.first_launch_complete = True
    
    def demonstrate_popup(self) -> None:
        """
        Demonstrate the history popup for the "Try It Now" feature.
        
        This method shows the history popup as a demonstration during
        the welcome screen flow.
        """
        if self._ui_manager is not None:
            self._ui_manager.show_history_popup()
