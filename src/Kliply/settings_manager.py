"""
Settings Manager for Kliply clipboard manager.

This module manages user preferences in memory and provides configuration interface.
"""

import logging
import threading
from typing import Optional
from .models import Settings


class SettingsManager:
    """
    Manages user preferences in memory.
    
    This class provides thread-safe access to application settings including
    clipboard depth, hotkey configuration, and launch preferences.
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize the SettingsManager with default or provided settings.
        
        Args:
            settings: Optional Settings object. If None, uses default Settings.
        """
        self._logger = logging.getLogger(__name__)
        
        try:
            self._settings = settings if settings is not None else Settings()
            self._lock = threading.Lock()
            
            # Validate initial settings
            if not self._settings.validate():
                self._logger.warning("Initial settings validation failed, using defaults")
                self._settings = Settings()
            
            self._logger.info("SettingsManager initialized successfully")
        
        except Exception as e:
            self._logger.error(f"Failed to initialize SettingsManager: {e}", exc_info=True)
            # Fall back to default settings
            self._settings = Settings()
            self._lock = threading.Lock()
    
    def get_clipboard_depth(self) -> int:
        """
        Get the current clipboard depth setting.
        
        Returns:
            The maximum number of clipboard items to retain.
        """
        with self._lock:
            return self._settings.clipboard_depth
    
    def set_clipboard_depth(self, depth: int) -> bool:
        """
        Set the clipboard depth with validation.
        
        Args:
            depth: The new clipboard depth (must be between 5 and 100).
        
        Returns:
            True if the depth was set successfully, False if validation failed.
        
        Raises:
            ValueError: If depth is not an integer or is out of range
        """
        try:
            # Validate depth is an integer
            if not isinstance(depth, int):
                self._logger.error(f"Invalid depth type: {type(depth)}, expected int")
                raise ValueError(f"Depth must be an integer, got {type(depth)}")
            
            # Validate depth is between 5 and 100
            if not (5 <= depth <= 100):
                self._logger.warning(f"Invalid depth value: {depth}, must be between 5 and 100")
                return False
            
            with self._lock:
                self._settings.clipboard_depth = depth
            
            self._logger.info(f"Clipboard depth set to {depth}")
            return True
        
        except Exception as e:
            self._logger.error(f"Error setting clipboard depth: {e}", exc_info=True)
            return False
    
    def get_hotkey(self) -> str:
        """
        Get the current hotkey setting.
        
        Returns:
            The keyboard shortcut string (e.g., "Cmd+Shift+V").
        """
        with self._lock:
            return self._settings.hotkey
    
    def set_hotkey(self, hotkey: str) -> None:
        """
        Set the hotkey for activating the history popup.
        
        Args:
            hotkey: The new keyboard shortcut string.
        
        Raises:
            ValueError: If hotkey is not a string or is empty
        """
        try:
            if not isinstance(hotkey, str):
                self._logger.error(f"Invalid hotkey type: {type(hotkey)}, expected str")
                raise ValueError(f"Hotkey must be a string, got {type(hotkey)}")
            
            if not hotkey.strip():
                self._logger.error("Hotkey cannot be empty")
                raise ValueError("Hotkey cannot be empty")
            
            with self._lock:
                self._settings.hotkey = hotkey
            
            self._logger.info(f"Hotkey set to {hotkey}")
        
        except Exception as e:
            self._logger.error(f"Error setting hotkey: {e}", exc_info=True)
            raise
    
    def get_launch_at_login(self) -> bool:
        """
        Get the launch at login setting.
        
        Returns:
            True if the app should launch at system login, False otherwise.
        """
        with self._lock:
            return self._settings.launch_at_login
    
    def set_launch_at_login(self, enabled: bool) -> None:
        """
        Set whether the app should launch at system login.
        
        Args:
            enabled: True to enable launch at login, False to disable.
        """
        with self._lock:
            self._settings.launch_at_login = enabled
    
    def get_settings(self) -> Settings:
        """
        Get a copy of the current settings.
        
        Returns:
            A copy of the Settings object.
        """
        with self._lock:
            return Settings(
                clipboard_depth=self._settings.clipboard_depth,
                hotkey=self._settings.hotkey,
                launch_at_login=self._settings.launch_at_login,
                first_launch_complete=self._settings.first_launch_complete
            )
