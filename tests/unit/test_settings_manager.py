"""
Unit tests for SettingsManager.

Tests default values, validation for clipboard depth, and settings getters/setters.
"""

import pytest
from src.Kliply.settings_manager import SettingsManager
from src.Kliply.models import Settings


class TestSettingsManager:
    """Test suite for SettingsManager class."""
    
    def test_initialization_with_defaults(self):
        """Test that SettingsManager initializes with default Settings values."""
        manager = SettingsManager()
        
        # Verify default values from Settings dataclass
        assert manager.get_clipboard_depth() == 10
        assert manager.get_hotkey() == "Cmd+Shift+V"
        assert manager.get_launch_at_login() is False
    
    def test_initialization_with_custom_settings(self):
        """Test that SettingsManager can be initialized with custom Settings."""
        custom_settings = Settings(
            clipboard_depth=25,
            hotkey="Cmd+V",
            launch_at_login=True,
            first_launch_complete=True
        )
        manager = SettingsManager(custom_settings)
        
        assert manager.get_clipboard_depth() == 25
        assert manager.get_hotkey() == "Cmd+V"
        assert manager.get_launch_at_login() is True
    
    def test_get_clipboard_depth(self):
        """Test getting clipboard depth."""
        manager = SettingsManager()
        depth = manager.get_clipboard_depth()
        
        assert isinstance(depth, int)
        assert depth == 10  # Default value
    
    def test_set_clipboard_depth_valid(self):
        """Test setting clipboard depth with valid values."""
        manager = SettingsManager()
        
        # Test minimum valid value
        assert manager.set_clipboard_depth(5) is True
        assert manager.get_clipboard_depth() == 5
        
        # Test maximum valid value
        assert manager.set_clipboard_depth(100) is True
        assert manager.get_clipboard_depth() == 100
        
        # Test middle value
        assert manager.set_clipboard_depth(50) is True
        assert manager.get_clipboard_depth() == 50
    
    def test_set_clipboard_depth_invalid_below_minimum(self):
        """Test that clipboard depth below 5 is rejected."""
        manager = SettingsManager()
        original_depth = manager.get_clipboard_depth()
        
        # Test below minimum
        assert manager.set_clipboard_depth(4) is False
        assert manager.get_clipboard_depth() == original_depth
        
        assert manager.set_clipboard_depth(0) is False
        assert manager.get_clipboard_depth() == original_depth
        
        assert manager.set_clipboard_depth(-1) is False
        assert manager.get_clipboard_depth() == original_depth
    
    def test_set_clipboard_depth_invalid_above_maximum(self):
        """Test that clipboard depth above 100 is rejected."""
        manager = SettingsManager()
        original_depth = manager.get_clipboard_depth()
        
        # Test above maximum
        assert manager.set_clipboard_depth(101) is False
        assert manager.get_clipboard_depth() == original_depth
        
        assert manager.set_clipboard_depth(200) is False
        assert manager.get_clipboard_depth() == original_depth
    
    def test_get_hotkey(self):
        """Test getting hotkey."""
        manager = SettingsManager()
        hotkey = manager.get_hotkey()
        
        assert isinstance(hotkey, str)
        assert hotkey == "Cmd+Shift+V"  # Default value
    
    def test_set_hotkey(self):
        """Test setting hotkey."""
        manager = SettingsManager()
        
        # Set new hotkey
        manager.set_hotkey("Ctrl+Alt+V")
        assert manager.get_hotkey() == "Ctrl+Alt+V"
        
        # Set another hotkey
        manager.set_hotkey("Cmd+C")
        assert manager.get_hotkey() == "Cmd+C"
    
    def test_get_launch_at_login(self):
        """Test getting launch at login setting."""
        manager = SettingsManager()
        launch_at_login = manager.get_launch_at_login()
        
        assert isinstance(launch_at_login, bool)
        assert launch_at_login is False  # Default value
    
    def test_set_launch_at_login(self):
        """Test setting launch at login."""
        manager = SettingsManager()
        
        # Enable launch at login
        manager.set_launch_at_login(True)
        assert manager.get_launch_at_login() is True
        
        # Disable launch at login
        manager.set_launch_at_login(False)
        assert manager.get_launch_at_login() is False
    
    def test_thread_safety(self):
        """Test that SettingsManager operations are thread-safe."""
        import threading
        import time
        
        manager = SettingsManager()
        results = []
        
        def set_depth_repeatedly():
            for i in range(10, 20):
                manager.set_clipboard_depth(i)
                time.sleep(0.001)
        
        def get_depth_repeatedly():
            for _ in range(10):
                depth = manager.get_clipboard_depth()
                results.append(depth)
                time.sleep(0.001)
        
        # Run multiple threads
        threads = [
            threading.Thread(target=set_depth_repeatedly),
            threading.Thread(target=get_depth_repeatedly),
            threading.Thread(target=set_depth_repeatedly)
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify all retrieved depths are valid
        for depth in results:
            assert 5 <= depth <= 100
    
    def test_get_settings_returns_copy(self):
        """Test that get_settings returns a copy of settings."""
        manager = SettingsManager()
        
        # Get settings
        settings = manager.get_settings()
        
        # Modify the returned settings
        settings.clipboard_depth = 99
        settings.hotkey = "Modified"
        
        # Verify original settings are unchanged
        assert manager.get_clipboard_depth() == 10
        assert manager.get_hotkey() == "Cmd+Shift+V"
