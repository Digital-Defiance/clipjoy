"""
Property-based tests for settings management.

Feature: Kliply
"""

import pytest
from hypothesis import given, strategies as st

from src.Kliply.models import Settings


@given(st.integers(min_value=5, max_value=100))
def test_property_5_depth_validation_valid_range(depth):
    """
    Property 5: Depth validation
    Validates: Requirements 2.6
    
    For any integer value between 5 and 100 (inclusive), when setting 
    the Clipboard_Depth, the value should be accepted.
    """
    settings = Settings(clipboard_depth=depth)
    
    # Verify the depth is set correctly
    assert settings.clipboard_depth == depth
    
    # Verify validation passes
    assert settings.validate() is True


@given(st.one_of(
    st.integers(max_value=4),  # Values below 5
    st.integers(min_value=101)  # Values above 100
))
def test_property_5_depth_validation_invalid_range(depth):
    """
    Property 5: Depth validation
    Validates: Requirements 2.6
    
    For any integer value outside the range [5, 100], when setting 
    the Clipboard_Depth, the value should be rejected.
    """
    settings = Settings(clipboard_depth=depth)
    
    # Verify validation fails for out-of-range values
    assert settings.validate() is False


@given(st.integers(min_value=5, max_value=100))
def test_property_5_depth_validation_boundary_values(depth):
    """
    Property 5: Depth validation - boundary testing
    Validates: Requirements 2.6
    
    Verify that boundary values (5 and 100) are correctly accepted.
    """
    settings = Settings(clipboard_depth=depth)
    
    # All values in valid range should pass validation
    assert settings.validate() is True
    
    # Verify the depth is stored correctly
    assert 5 <= settings.clipboard_depth <= 100
