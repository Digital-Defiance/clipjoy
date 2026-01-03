"""
Unit tests for PermissionManager.

Tests permission checking, System Preferences opening, and degraded mode behavior.
"""

import pytest
from unittest.mock import Mock, patch, call
from datetime import datetime, timedelta

from src.Kliply.permission_manager import PermissionManager
from src.Kliply.models import PermissionStatus


class TestPermissionManager:
    """Test suite for PermissionManager class."""
    
    def test_initialization(self):
        """Test that PermissionManager initializes with default PermissionStatus."""
        manager = PermissionManager()
        
        # Verify status object exists
        assert isinstance(manager.status, PermissionStatus)
        
        # Verify default values
        assert manager.status.accessibility is False
        assert isinstance(manager.status.last_checked, datetime)
    
    @patch('ApplicationServices.AXIsProcessTrusted')
    def test_check_accessibility_permission_granted(self, mock_ax):
        """Test checking accessibility permission when granted."""
        manager = PermissionManager()
        
        # Mock successful permission check
        mock_ax.return_value = True
        
        # Check permission
        result = manager.check_accessibility_permission()
        
        # Verify result
        assert result is True
        assert manager.status.accessibility is True
        
        # Verify AXIsProcessTrusted was called
        mock_ax.assert_called_once()
    
    @patch('ApplicationServices.AXIsProcessTrusted')
    def test_check_accessibility_permission_denied(self, mock_ax):
        """Test checking accessibility permission when denied."""
        manager = PermissionManager()
        
        # Mock failed permission check
        mock_ax.return_value = False
        
        # Check permission
        result = manager.check_accessibility_permission()
        
        # Verify result
        assert result is False
        assert manager.status.accessibility is False
    
    @patch('ApplicationServices.AXIsProcessTrusted')
    def test_check_accessibility_permission_updates_timestamp(self, mock_ax):
        """Test that permission check updates the last_checked timestamp."""
        manager = PermissionManager()
        
        # Mock permission check
        mock_ax.return_value = True
        
        # Record time before check
        time_before = datetime.now()
        
        # Check permission
        manager.check_accessibility_permission()
        
        # Verify timestamp is updated and recent
        assert manager.status.last_checked >= time_before
        time_diff = datetime.now() - manager.status.last_checked
        assert time_diff < timedelta(seconds=1)
    
    @patch('ApplicationServices.AXIsProcessTrusted')
    def test_check_accessibility_permission_timeout(self, mock_ax):
        """Test handling of timeout/exception during permission check."""
        manager = PermissionManager()
        
        # Mock exception (simulating any error)
        mock_ax.side_effect = Exception("Test error")
        
        # Check permission
        result = manager.check_accessibility_permission()
        
        # Verify graceful handling - should return False on error
        assert result is False
    
    @patch('ApplicationServices.AXIsProcessTrusted')
    def test_check_accessibility_permission_exception(self, mock_ax):
        """Test handling of exceptions during permission check."""
        manager = PermissionManager()
        
        # Mock exception
        mock_ax.side_effect = Exception("Test error")
        
        # Check permission
        result = manager.check_accessibility_permission()
        
        # Verify graceful handling
        assert result is False
    
    @patch('subprocess.run')
    def test_request_accessibility_permission(self, mock_run):
        """Test requesting accessibility permission."""
        manager = PermissionManager()
        
        # Mock subprocess call
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        # Request permission (should not raise exception)
        manager.request_accessibility_permission()
        
        # Verify subprocess was called
        mock_run.assert_called_once()
        args = mock_run.call_args[0]
        assert args[0][0] == 'osascript'
    
    @patch('subprocess.run')
    def test_request_accessibility_permission_exception(self, mock_run):
        """Test handling of exceptions when requesting permission."""
        manager = PermissionManager()
        
        # Mock exception
        mock_run.side_effect = Exception("Test error")
        
        # Request permission (should not raise exception)
        manager.request_accessibility_permission()
        
        # Should handle gracefully without raising
    
    @patch('subprocess.run')
    def test_check_all_permissions(self, mock_run):
        """Test checking all permissions returns correct dictionary."""
        manager = PermissionManager()
        
        # Mock permission check
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = 'true'
        mock_run.return_value = mock_result
        
        # Check all permissions
        permissions = manager.check_all_permissions()
        
        # Verify result structure
        assert isinstance(permissions, dict)
        assert 'accessibility' in permissions
        assert permissions['accessibility'] is True
    
    @patch('subprocess.run')
    def test_open_system_preferences_security(self, mock_run):
        """Test opening System Preferences to security pane."""
        manager = PermissionManager()
        
        # Mock subprocess call
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        # Open System Preferences
        manager.open_system_preferences("security")
        
        # Verify subprocess was called with correct URL
        mock_run.assert_called()
        args = mock_run.call_args[0]
        assert args[0][0] == 'open'
        assert 'Privacy_Accessibility' in args[0][1]
    
    @patch('subprocess.run')
    def test_open_system_preferences_accessibility(self, mock_run):
        """Test opening System Preferences to accessibility pane."""
        manager = PermissionManager()
        
        # Mock subprocess call
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        # Open System Preferences
        manager.open_system_preferences("accessibility")
        
        # Verify subprocess was called
        mock_run.assert_called()
        args = mock_run.call_args[0]
        assert args[0][0] == 'open'
    
    @patch('subprocess.run')
    def test_open_system_preferences_fallback(self, mock_run):
        """Test fallback when opening System Preferences fails."""
        manager = PermissionManager()
        
        # Mock first call failing, second succeeding
        mock_result_fail = Mock()
        mock_result_fail.returncode = 1
        mock_result_success = Mock()
        mock_result_success.returncode = 0
        mock_run.side_effect = [mock_result_fail, mock_result_success]
        
        # Open System Preferences
        manager.open_system_preferences("security")
        
        # Verify both calls were made (fallback)
        assert mock_run.call_count == 2
    
    @patch('subprocess.run')
    def test_open_system_preferences_exception(self, mock_run):
        """Test handling of exceptions when opening System Preferences."""
        manager = PermissionManager()
        
        # Mock exception
        mock_run.side_effect = Exception("Test error")
        
        # Open System Preferences (should not raise exception)
        manager.open_system_preferences("security")
        
        # Should handle gracefully without raising
    
    @patch('ApplicationServices.AXIsProcessTrusted')
    def test_get_permission_status(self, mock_ax):
        """Test getting permission status."""
        manager = PermissionManager()
        
        # Mock permission check
        mock_ax.return_value = True
        
        # Get status
        status = manager.get_permission_status()
        
        # Verify status is returned and refreshed
        assert isinstance(status, PermissionStatus)
        assert status.accessibility is True
        
        # Verify check was called
        mock_ax.assert_called()
    
    @patch('ApplicationServices.AXIsProcessTrusted')
    def test_is_degraded_mode_when_permissions_denied(self, mock_ax):
        """Test degraded mode detection when permissions are denied."""
        manager = PermissionManager()
        
        # Mock denied permission
        mock_ax.return_value = False
        
        # Check permission first
        manager.check_accessibility_permission()
        
        # Verify degraded mode
        assert manager.is_degraded_mode() is True
    
    @patch('ApplicationServices.AXIsProcessTrusted')
    def test_is_degraded_mode_when_permissions_granted(self, mock_ax):
        """Test degraded mode detection when permissions are granted."""
        manager = PermissionManager()
        
        # Mock granted permission
        mock_ax.return_value = True
        
        # Check permission first
        manager.check_accessibility_permission()
        
        # Verify not in degraded mode
        assert manager.is_degraded_mode() is False
    
    @patch('ApplicationServices.AXIsProcessTrusted')
    def test_permission_status_all_granted(self, mock_ax):
        """Test PermissionStatus.all_granted() method."""
        manager = PermissionManager()
        
        # Test when permission is denied
        mock_ax.return_value = False
        
        manager.check_accessibility_permission()
        assert manager.status.all_granted() is False
        
        # Test when permission is granted
        mock_ax.return_value = True
        
        manager.check_accessibility_permission()
        assert manager.status.all_granted() is True
