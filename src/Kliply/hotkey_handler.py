"""
Hotkey Handler for Kliply clipboard manager.

This module handles global keyboard shortcuts for activating the history popup.
"""

from typing import Callable, Optional
import logging

from pynput import keyboard


class HotkeyHandler:
    """
    Handles global keyboard shortcuts for Kliply.
    
    This class registers and manages global hotkeys that work regardless of
    which application is currently focused. It prevents duplicate activations
    and handles macOS permission requests.
    
    Attributes:
        _callback: Function to call when hotkey is pressed
        _hotkey: Current hotkey string (e.g., "Cmd+Shift+V")
        _listener: pynput keyboard listener for global hotkey detection
        _is_popup_visible: Flag to prevent duplicate activations
    """
    
    def __init__(self, callback: Callable[[], None]):
        """
        Initialize the HotkeyHandler.
        
        Args:
            callback: Function to call when the hotkey is pressed
        """
        self._callback = callback
        self._hotkey: Optional[str] = None
        self._listener: Optional[keyboard.Listener] = None
        self._is_popup_visible = False
        
        # Set up logging
        self._logger = logging.getLogger(__name__)
    
    def register_hotkey(self, hotkey: str = "Cmd+Shift+V") -> bool:
        """
        Register a global hotkey.
        
        This method sets up a global keyboard listener that monitors for the
        specified hotkey combination. On macOS, this requires Accessibility
        permissions.
        
        Args:
            hotkey: The hotkey string to register (default: "Cmd+Shift+V")
        
        Returns:
            True if registration was successful, False otherwise
        """
        try:
            # Unregister existing hotkey if any
            if self._listener is not None:
                self.unregister_hotkey()
            
            self._hotkey = hotkey
            
            # Parse the hotkey string to get the key combination
            # Format: "Cmd+Shift+V" -> Command + Shift + V
            keys = self._parse_hotkey(hotkey)
            
            if not keys:
                self._logger.error(f"Failed to parse hotkey: {hotkey}")
                return False
            
            # Create a global hotkey using pynput
            # We'll use a combination listener
            self._current_keys = set()
            
            def on_press(key):
                """Handle key press events."""
                try:
                    # Add key to current pressed keys
                    key_name = self._get_key_name(key)
                    if key_name:
                        self._current_keys.add(key_name)
                    
                    # Check if all required keys are pressed
                    if self._check_hotkey_match(keys):
                        # Prevent duplicate activations
                        if not self._is_popup_visible:
                            self._is_popup_visible = True
                            try:
                                self._callback()
                            except Exception as e:
                                self._logger.error(f"Error in hotkey callback: {e}", exc_info=True)
                
                except Exception as e:
                    self._logger.error(f"Error in hotkey press handler: {e}", exc_info=True)
            
            def on_release(key):
                """Handle key release events."""
                try:
                    # Remove key from current pressed keys
                    key_name = self._get_key_name(key)
                    if key_name:
                        self._current_keys.discard(key_name)
                    
                    # Reset popup visible flag when hotkey is released
                    if not self._check_hotkey_match(keys):
                        self._is_popup_visible = False
                
                except Exception as e:
                    self._logger.error(f"Error in hotkey release handler: {e}", exc_info=True)
            
            # Start the listener
            try:
                # Wrap listener creation in try-except to catch any initialization errors
                try:
                    self._listener = keyboard.Listener(
                        on_press=on_press,
                        on_release=on_release,
                        suppress=False  # Don't suppress keys, just monitor
                    )
                except Exception as listener_error:
                    self._logger.error(
                        f"Failed to create keyboard listener: {listener_error}",
                        exc_info=True
                    )
                    return False
                
                # Start the listener - this may crash on macOS if permissions aren't granted
                try:
                    self._listener.start()
                except Exception as start_error:
                    self._logger.error(
                        f"Failed to start keyboard listener: {start_error}",
                        exc_info=True
                    )
                    self._listener = None
                    return False
                
                self._logger.info(f"Registered global hotkey: {hotkey}")
                return True
            
            except Exception as e:
                # This may fail due to permission issues on macOS
                self._logger.error(
                    f"Failed to register keyboard listener (may need Accessibility permissions): {e}",
                    exc_info=True
                )
                self._listener = None
                return False
        
        except Exception as e:
            self._logger.error(f"Failed to register hotkey: {e}", exc_info=True)
            return False
    
    def unregister_hotkey(self) -> None:
        """
        Unregister the current hotkey and clean up resources.
        
        This method stops the keyboard listener and releases all resources.
        """
        if self._listener is not None:
            try:
                self._listener.stop()
                self._listener = None
                self._hotkey = None
                self._current_keys = set()
                self._is_popup_visible = False
                self._logger.info("Unregistered hotkey")
            except Exception as e:
                self._logger.error(f"Error unregistering hotkey: {e}")
    
    def _parse_hotkey(self, hotkey: str) -> list[str]:
        """
        Parse a hotkey string into a list of key names.
        
        Args:
            hotkey: Hotkey string (e.g., "Cmd+Shift+V")
        
        Returns:
            List of normalized key names
        """
        if not hotkey:
            return []
        
        # Split by '+' and normalize
        parts = [part.strip().lower() for part in hotkey.split('+')]
        
        # Normalize key names
        normalized = []
        for part in parts:
            if part in ['cmd', 'command']:
                normalized.append('cmd')
            elif part in ['shift']:
                normalized.append('shift')
            elif part in ['ctrl', 'control']:
                normalized.append('ctrl')
            elif part in ['alt', 'option']:
                normalized.append('alt')
            else:
                # Regular key (like 'v')
                normalized.append(part)
        
        return normalized
    
    def _get_key_name(self, key) -> Optional[str]:
        """
        Get a normalized key name from a pynput key object.
        
        Args:
            key: pynput Key or KeyCode object
        
        Returns:
            Normalized key name string, or None if key cannot be identified
        """
        try:
            # Handle special keys
            if hasattr(key, 'name'):
                name = key.name.lower()
                # Normalize special key names
                if name in ['cmd', 'cmd_l', 'cmd_r']:
                    return 'cmd'
                elif name in ['shift', 'shift_l', 'shift_r']:
                    return 'shift'
                elif name in ['ctrl', 'ctrl_l', 'ctrl_r']:
                    return 'ctrl'
                elif name in ['alt', 'alt_l', 'alt_r']:
                    return 'alt'
                else:
                    return name
            
            # Handle character keys
            if hasattr(key, 'char') and key.char:
                return key.char.lower()
            
            return None
        
        except Exception:
            return None
    
    def _check_hotkey_match(self, required_keys: list[str]) -> bool:
        """
        Check if the currently pressed keys match the required hotkey.
        
        Args:
            required_keys: List of required key names
        
        Returns:
            True if all required keys are currently pressed
        """
        # Check if all required keys are in the current pressed keys
        return all(key in self._current_keys for key in required_keys)
    
    def reset_popup_state(self) -> None:
        """
        Reset the popup visible state.
        
        This should be called when the popup is closed to allow the hotkey
        to be triggered again.
        """
        self._is_popup_visible = False
