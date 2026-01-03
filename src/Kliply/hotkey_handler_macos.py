"""
Native macOS Hotkey Handler using Carbon Event Manager.

This module provides global hotkey support on macOS using the Carbon Event Manager
API, which is the proper way to register global hotkeys on macOS.
"""

import logging
from typing import Callable, Optional

try:
    from Cocoa import NSEvent
    from Quartz import (
        CGEventMaskBit,
        CGEventTapCreate,
        CGEventTapEnable,
        kCGEventKeyDown,
        kCGHeadInsertEventTap,
        kCGSessionEventTap,
        CFMachPortCreateRunLoopSource,
        CFRunLoopAddSource,
        CFRunLoopGetCurrent,
        kCFRunLoopCommonModes,
    )
    from ApplicationServices import (
        AXIsProcessTrusted,
        AXIsProcessTrustedWithOptions,
        kAXTrustedCheckOptionPrompt,
    )
    PYOBJC_AVAILABLE = True
except ImportError:
    PYOBJC_AVAILABLE = False


class HotkeyHandlerMacOS:
    """
    Native macOS hotkey handler using Carbon Event Manager.
    
    This implementation uses CGEventTap to monitor keyboard events globally,
    which is the proper way to implement global hotkeys on macOS.
    """
    
    def __init__(self, callback: Callable[[], None]):
        """
        Initialize the hotkey handler.
        
        Args:
            callback: Function to call when hotkey is pressed
        """
        self._callback = callback
        self._hotkey: Optional[str] = None
        self._event_tap = None
        self._run_loop_source = None
        self._is_popup_visible = False
        self._required_modifiers = 0
        self._required_key = None
        
        self._logger = logging.getLogger(__name__)
        
        if not PYOBJC_AVAILABLE:
            self._logger.error("PyObjC not available - hotkeys will not work")
    
    def register_hotkey(self, hotkey: str = "Cmd+Shift+V") -> bool:
        """
        Register a global hotkey using Carbon Event Manager.
        
        Args:
            hotkey: Hotkey string (e.g., "Cmd+Shift+V")
        
        Returns:
            True if registration successful, False otherwise
        """
        if not PYOBJC_AVAILABLE:
            self._logger.error("PyObjC not available")
            return False
        
        try:
            # Check if we have Accessibility permissions
            # This will trigger the permission prompt if not already granted
            trusted = AXIsProcessTrustedWithOptions({
                kAXTrustedCheckOptionPrompt: True
            })
            
            if not trusted:
                self._logger.warning("Accessibility permissions not granted")
                self._logger.warning("A system dialog should have appeared requesting permission")
                self._logger.warning("Please grant permission in System Settings > Privacy & Security > Accessibility")
                return False
            
            # Parse the hotkey
            modifiers, key = self._parse_hotkey(hotkey)
            if modifiers is None or key is None:
                self._logger.error(f"Failed to parse hotkey: {hotkey}")
                return False
            
            self._hotkey = hotkey
            self._required_modifiers = modifiers
            self._required_key = key
            
            # Create event tap for keyboard events
            event_mask = CGEventMaskBit(kCGEventKeyDown)
            
            self._event_tap = CGEventTapCreate(
                kCGSessionEventTap,
                kCGHeadInsertEventTap,
                0,  # Active filter
                event_mask,
                self._event_callback,
                None
            )
            
            if self._event_tap is None:
                self._logger.error("Failed to create event tap even with permissions granted")
                return False
            
            # Create run loop source and add to current run loop
            self._run_loop_source = CFMachPortCreateRunLoopSource(None, self._event_tap, 0)
            CFRunLoopAddSource(CFRunLoopGetCurrent(), self._run_loop_source, kCFRunLoopCommonModes)
            
            # Enable the event tap
            CGEventTapEnable(self._event_tap, True)
            
            self._logger.info(f"Registered global hotkey: {hotkey}")
            return True
        
        except Exception as e:
            self._logger.error(f"Failed to register hotkey: {e}", exc_info=True)
            return False
    
    def unregister_hotkey(self) -> None:
        """Unregister the hotkey and clean up resources."""
        if self._event_tap is not None:
            try:
                CGEventTapEnable(self._event_tap, False)
                self._event_tap = None
                self._run_loop_source = None
                self._logger.info("Unregistered hotkey")
            except Exception as e:
                self._logger.error(f"Error unregistering hotkey: {e}")
    
    def _event_callback(self, proxy, event_type, event, refcon):
        """
        Callback for keyboard events.
        
        This is called by the system for every keyboard event.
        The event parameter is a CGEventRef from Quartz.
        """
        try:
            from Quartz import (
                CGEventGetFlags,
                kCGEventFlagMaskCommand,
                kCGEventFlagMaskShift,
                kCGEventFlagMaskControl,
                kCGEventFlagMaskAlternate,
                CGEventKeyboardGetUnicodeString
            )
            import objc
            
            # Get the modifiers from the CGEvent
            flags = CGEventGetFlags(event)
            
            # Extract modifier flags using Quartz constants
            cmd_pressed = bool(flags & kCGEventFlagMaskCommand)
            shift_pressed = bool(flags & kCGEventFlagMaskShift)
            ctrl_pressed = bool(flags & kCGEventFlagMaskControl)
            alt_pressed = bool(flags & kCGEventFlagMaskAlternate)
            
            # Check if this matches our hotkey modifiers
            modifiers_match = True
            if self._required_modifiers & (1 << 0):  # Cmd required
                modifiers_match = modifiers_match and cmd_pressed
            if self._required_modifiers & (1 << 1):  # Shift required
                modifiers_match = modifiers_match and shift_pressed
            if self._required_modifiers & (1 << 2):  # Ctrl required
                modifiers_match = modifiers_match and ctrl_pressed
            if self._required_modifiers & (1 << 3):  # Alt required
                modifiers_match = modifiers_match and alt_pressed
            
            # Get the character from the CGEvent
            # Create a buffer for the unicode string
            max_string_length = 4
            unicode_string = objc.NULL
            actual_string_length = objc.NULL
            
            # Call CGEventKeyboardGetUnicodeString with proper NULL values
            CGEventKeyboardGetUnicodeString(
                event, 
                max_string_length, 
                actual_string_length,
                unicode_string
            )
            
            # Alternative approach: use NSEvent to get the character
            # Convert CGEvent to NSEvent
            from Cocoa import NSEvent
            ns_event = NSEvent.eventWithCGEvent_(event)
            
            if ns_event:
                chars = ns_event.charactersIgnoringModifiers()
                if chars and len(chars) > 0:
                    char = chars[0].lower()
                    
                    if modifiers_match and char == self._required_key:
                        # Hotkey matched!
                        if not self._is_popup_visible:
                            self._is_popup_visible = True
                            try:
                                self._callback()
                            except Exception as e:
                                self._logger.error(f"Error in hotkey callback: {e}", exc_info=True)
        
        except Exception as e:
            self._logger.error(f"Error in event callback: {e}", exc_info=True)
        
        # Pass the event through
        return event
    
    def _parse_hotkey(self, hotkey: str) -> tuple:
        """
        Parse hotkey string into modifiers and key.
        
        Args:
            hotkey: Hotkey string (e.g., "Cmd+Shift+V")
        
        Returns:
            Tuple of (modifiers_mask, key_char) or (None, None) if invalid
        """
        if not hotkey:
            return (None, None)
        
        parts = [p.strip().lower() for p in hotkey.split('+')]
        
        modifiers = 0
        key = None
        
        for part in parts:
            if part in ['cmd', 'command']:
                modifiers |= (1 << 0)
            elif part == 'shift':
                modifiers |= (1 << 1)
            elif part in ['ctrl', 'control']:
                modifiers |= (1 << 2)
            elif part in ['alt', 'option']:
                modifiers |= (1 << 3)
            else:
                # This is the key
                if len(part) == 1:
                    key = part
                else:
                    self._logger.warning(f"Invalid key in hotkey: {part}")
                    return (None, None)
        
        if key is None:
            self._logger.warning("No key specified in hotkey")
            return (None, None)
        
        return (modifiers, key)
    
    def reset_popup_state(self) -> None:
        """Reset the popup visible state."""
        self._is_popup_visible = False
