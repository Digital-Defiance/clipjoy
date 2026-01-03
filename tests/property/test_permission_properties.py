"""
Property-based tests for permission management.

Feature: Kliply
"""

import pytest
from hypothesis import given, strategies as st
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.Kliply.permission_manager import PermissionManager
from src.Kliply.models import PermissionStatus


@pytest.mark.property
@given(st.booleans())
def test_property_22_permission_detection_and_recovery(permission_state):
    """
    Property 22: Permission detection and recovery
    Validates: Requirements 13.3
    
    For any permission state change (granted or revoked), when Kliply checks 
    permissions, it should detect the change and update its behavior accordingly 
    without requiring a restart.
    """
    manager = PermissionManager()
    
    # Mock the ApplicationServices AXIsProcessTrusted call to simulate permission state
    with patch('ApplicationServices.AXIsProcessTrusted') as mock_ax:
        # Configure mock to return the permission state
        mock_ax.return_value = permission_state
        
        # Check permission - should detect the state
        detected_state = manager.check_accessibility_permission()
        
        # Verify the detected state matches the simulated state
        assert detected_state == permission_state
        
        # Verify the status object is updated
        assert manager.status.accessibility == permission_state
        
        # Verify last_checked timestamp is recent (within last 5 seconds)
        time_diff = datetime.now() - manager.status.last_checked
        assert time_diff < timedelta(seconds=5)
        
        # Verify degraded mode reflects permission state
        assert manager.is_degraded_mode() == (not permission_state)


@pytest.mark.property
@given(st.booleans())
def test_property_22_permission_state_transitions(initial_state):
    """
    Property 22: Permission detection and recovery - state transitions
    Validates: Requirements 13.3
    
    For any permission state, when the state changes, the manager should 
    detect the new state on the next check without requiring a restart.
    """
    manager = PermissionManager()
    
    with patch('ApplicationServices.AXIsProcessTrusted') as mock_ax:
        # Set initial state
        mock_ax.return_value = initial_state
        
        # First check - establish initial state
        first_check = manager.check_accessibility_permission()
        assert first_check == initial_state
        
        # Simulate state change (flip the permission)
        new_state = not initial_state
        mock_ax.return_value = new_state
        
        # Second check - should detect the change
        second_check = manager.check_accessibility_permission()
        assert second_check == new_state
        
        # Verify the status reflects the new state
        assert manager.status.accessibility == new_state


@pytest.mark.property
def test_property_22_check_all_permissions_consistency():
    """
    Property 22: Permission detection and recovery - consistency
    Validates: Requirements 13.3
    
    For any permission check, check_all_permissions() should return 
    consistent results with individual permission checks.
    """
    manager = PermissionManager()
    
    with patch('ApplicationServices.AXIsProcessTrusted') as mock_ax:
        # Mock a permission state
        mock_ax.return_value = True
        
        # Check individual permission
        individual_check = manager.check_accessibility_permission()
        
        # Check all permissions
        all_permissions = manager.check_all_permissions()
        
        # Verify consistency
        assert all_permissions['accessibility'] == individual_check
        assert all_permissions['accessibility'] == manager.status.accessibility


@pytest.mark.property
@given(st.booleans())
def test_property_22_permission_status_object_updates(permission_state):
    """
    Property 22: Permission detection and recovery - status object
    Validates: Requirements 13.3
    
    For any permission check, the PermissionStatus object should be 
    updated with the current state and timestamp.
    """
    manager = PermissionManager()
    
    with patch('ApplicationServices.AXIsProcessTrusted') as mock_ax:
        # Configure mock
        mock_ax.return_value = permission_state
        
        # Record time before check
        time_before = datetime.now()
        
        # Perform check
        manager.check_accessibility_permission()
        
        # Get status
        status = manager.get_permission_status()
        
        # Verify status is updated
        assert status.accessibility == permission_state
        assert status.last_checked >= time_before
        assert status.all_granted() == permission_state
