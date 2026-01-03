"""
Property-based tests for onboarding management.

Feature: Kliply
"""

import pytest
from hypothesis import given, strategies as st
from PyQt6.QtWidgets import QApplication

from src.Kliply.models import Settings
from src.Kliply.settings_manager import SettingsManager
from src.Kliply.onboarding_manager import OnboardingManager


@given(st.booleans())
def test_property_21_welcome_screen_shows_on_first_launch(first_launch_complete):
    """
    Property 21: Welcome screen shows on first launch
    Validates: Requirements 11.1
    
    For any fresh installation of Kliply (first_launch_complete=False),
    when the application is launched, the welcome screen should be displayed.
    For any installation where first launch is complete (first_launch_complete=True),
    the welcome screen should not be displayed.
    """
    # Ensure QApplication exists
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Create settings with the given first_launch_complete status
    settings = Settings(first_launch_complete=first_launch_complete)
    settings_manager = SettingsManager(settings)
    
    # Create onboarding manager
    onboarding_manager = OnboardingManager(settings_manager)
    
    # Check if welcome should be shown
    should_show = onboarding_manager.should_show_welcome()
    
    # Verify the property: welcome should show only when first_launch_complete is False
    if first_launch_complete:
        assert should_show is False, "Welcome screen should not show when first launch is complete"
    else:
        assert should_show is True, "Welcome screen should show on first launch"


@given(st.booleans())
def test_property_21_mark_welcome_complete_prevents_future_display(initial_state):
    """
    Property 21: Welcome screen shows on first launch - completion tracking
    Validates: Requirements 11.1, 11.7
    
    For any onboarding manager, after marking welcome as complete,
    should_show_welcome() should return False.
    """
    # Ensure QApplication exists
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Create settings with the given initial state
    settings = Settings(first_launch_complete=initial_state)
    settings_manager = SettingsManager(settings)
    
    # Create onboarding manager
    onboarding_manager = OnboardingManager(settings_manager)
    
    # Mark welcome as complete
    onboarding_manager.mark_welcome_complete()
    
    # Verify welcome should not show after marking complete
    assert onboarding_manager.should_show_welcome() is False, \
        "Welcome screen should not show after being marked complete"
    
    # Verify the settings were updated
    updated_settings = settings_manager.get_settings()
    assert updated_settings.first_launch_complete is True, \
        "first_launch_complete flag should be set to True"


def test_property_21_fresh_install_scenario():
    """
    Property 21: Welcome screen shows on first launch - fresh install
    Validates: Requirements 11.1
    
    Verify that a fresh installation (default Settings) shows the welcome screen.
    """
    # Ensure QApplication exists
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Create default settings (simulating fresh install)
    settings_manager = SettingsManager()  # Uses default Settings
    onboarding_manager = OnboardingManager(settings_manager)
    
    # Verify welcome should show on fresh install
    assert onboarding_manager.should_show_welcome() is True, \
        "Welcome screen should show on fresh installation"
    
    # Verify the default settings have first_launch_complete=False
    settings = settings_manager.get_settings()
    assert settings.first_launch_complete is False, \
        "Fresh install should have first_launch_complete=False"
