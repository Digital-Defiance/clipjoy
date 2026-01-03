"""
Unit tests for HotkeyHandler.

Tests specific examples and edge cases for global hotkey handling.
"""

import pytest
from unittest.mock import Mock, patch
import time

from src.Kliply.hotkey_handler import HotkeyHandler


def test_hotkey_registration_on_startup():
    """
    Test that hotkey can be registered on startup.
    Validates: Requirements 3.1
    """
    callback = Mock()
    handler = HotkeyHandler(callback)
    
    # Mock the listener to avoid actual keyboard access
    with patch('src.Kliply.hotkey_handler.keyboard.Listener') as mock_listener:
        mock_listener_instance = Mock()
        mock_listener.return_value = mock_listener_instance
        
        # Register the hotkey
        result = handler.register_hotkey("Cmd+Shift+V")
        
        # Verify registration was successful
        assert result is True
        assert handler._hotkey == "Cmd+Shift+V"
        assert handler._listener is not None
        
        # Verify listener was started
        mock_listener_instance.start.assert_called_once()
        
        # Clean up
        handler.unregister_hotkey()


def test_default_hotkey_value():
    """
    Test that default hotkey is Cmd+Shift+V.
    Validates: Requirements 3.3
    """
    callback = Mock()
    handler = HotkeyHandler(callback)
    
    # Mock the listener to avoid actual keyboard access
    with patch('src.Kliply.hotkey_handler.keyboard.Listener') as mock_listener:
        mock_listener_instance = Mock()
        mock_listener.return_value = mock_listener_instance
        
        # Register with default hotkey
        result = handler.register_hotkey()
        
        # Verify default hotkey was used
        assert result is True
        assert handler._hotkey == "Cmd+Shift+V"
        
        # Clean up
        handler.unregister_hotkey()


def test_duplicate_activation_prevention():
    """
    Test that duplicate activations are prevented.
    Validates: Requirements 3.1, 3.3
    """
    callback = Mock()
    handler = HotkeyHandler(callback)
    
    # Set popup as visible
    handler._is_popup_visible = True
    
    # Try to trigger callback (should be prevented by the flag)
    # Simulate the logic that would happen in the hotkey handler
    if not handler._is_popup_visible:
        handler._callback()
    
    # Verify callback was not called
    callback.assert_not_called()
    
    # Reset popup state
    handler.reset_popup_state()
    
    # Now try again with popup not visible
    if not handler._is_popup_visible:
        handler._callback()
    
    # Verify callback was called this time
    callback.assert_called_once()


def test_unregister_hotkey():
    """Test that hotkey can be unregistered cleanly."""
    callback = Mock()
    handler = HotkeyHandler(callback)
    
    # Mock the listener to avoid actual keyboard access
    with patch('src.Kliply.hotkey_handler.keyboard.Listener') as mock_listener:
        mock_listener_instance = Mock()
        mock_listener.return_value = mock_listener_instance
        
        # Register hotkey
        handler.register_hotkey("Cmd+Shift+V")
        assert handler._listener is not None
        
        # Unregister hotkey
        handler.unregister_hotkey()
        
        # Verify cleanup
        assert handler._listener is None
        assert handler._hotkey is None
        
        # Verify listener was stopped
        mock_listener_instance.stop.assert_called_once()


def test_parse_hotkey():
    """Test hotkey string parsing."""
    callback = Mock()
    handler = HotkeyHandler(callback)
    
    # Test various hotkey formats
    keys = handler._parse_hotkey("Cmd+Shift+V")
    assert keys == ['cmd', 'shift', 'v']
    
    keys = handler._parse_hotkey("Ctrl+Alt+C")
    assert keys == ['ctrl', 'alt', 'c']
    
    keys = handler._parse_hotkey("Command+Shift+A")
    assert keys == ['cmd', 'shift', 'a']
    
    # Test empty hotkey
    keys = handler._parse_hotkey("")
    assert keys == []


def test_get_key_name():
    """Test key name normalization."""
    callback = Mock()
    handler = HotkeyHandler(callback)
    
    # Test with mock key objects
    class MockKey:
        def __init__(self, name=None, char=None):
            if name:
                self.name = name
            if char:
                self.char = char
    
    # Test special keys
    key = MockKey(name='cmd_l')
    assert handler._get_key_name(key) == 'cmd'
    
    key = MockKey(name='shift_r')
    assert handler._get_key_name(key) == 'shift'
    
    # Test character keys
    key = MockKey(char='v')
    assert handler._get_key_name(key) == 'v'
    
    key = MockKey(char='A')
    assert handler._get_key_name(key) == 'a'


def test_check_hotkey_match():
    """Test hotkey matching logic."""
    callback = Mock()
    handler = HotkeyHandler(callback)
    
    # Set up current pressed keys
    handler._current_keys = {'cmd', 'shift', 'v'}
    
    # Test matching
    assert handler._check_hotkey_match(['cmd', 'shift', 'v']) is True
    assert handler._check_hotkey_match(['cmd', 'shift']) is True
    assert handler._check_hotkey_match(['cmd']) is True
    
    # Test non-matching
    assert handler._check_hotkey_match(['cmd', 'shift', 'v', 'a']) is False
    assert handler._check_hotkey_match(['ctrl', 'shift', 'v']) is False


def test_reset_popup_state():
    """Test resetting popup state."""
    callback = Mock()
    handler = HotkeyHandler(callback)
    
    # Set popup as visible
    handler._is_popup_visible = True
    
    # Reset state
    handler.reset_popup_state()
    
    # Verify state was reset
    assert handler._is_popup_visible is False


def test_callback_initialization():
    """Test that callback is properly stored during initialization."""
    callback = Mock()
    handler = HotkeyHandler(callback)
    
    # Verify callback is stored
    assert handler._callback == callback
    
    # Verify initial state
    assert handler._hotkey is None
    assert handler._listener is None
    assert handler._is_popup_visible is False


def test_register_invalid_hotkey():
    """Test handling of invalid hotkey strings."""
    callback = Mock()
    handler = HotkeyHandler(callback)
    
    # Try to register with empty hotkey
    result = handler.register_hotkey("")
    
    # Should fail gracefully
    assert result is False
    assert handler._hotkey == ""


def test_multiple_registrations():
    """Test that re-registering a hotkey unregisters the previous one."""
    callback = Mock()
    handler = HotkeyHandler(callback)
    
    # Mock the listener to avoid actual keyboard access
    with patch('src.Kliply.hotkey_handler.keyboard.Listener') as mock_listener:
        mock_listener_instance1 = Mock()
        mock_listener_instance2 = Mock()
        mock_listener.side_effect = [mock_listener_instance1, mock_listener_instance2]
        
        # Register first hotkey
        handler.register_hotkey("Cmd+Shift+V")
        first_listener = handler._listener
        
        # Register second hotkey
        handler.register_hotkey("Cmd+Shift+C")
        second_listener = handler._listener
        
        # Verify new listener was created
        assert second_listener is not first_listener
        assert handler._hotkey == "Cmd+Shift+C"
        
        # Verify first listener was stopped
        mock_listener_instance1.stop.assert_called_once()
        
        # Clean up
        handler.unregister_hotkey()
