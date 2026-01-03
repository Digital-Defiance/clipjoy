"""
Unit tests for OnboardingManager.

Feature: Kliply
"""

import pytest
from unittest.mock import Mock, MagicMock
from PyQt6.QtWidgets import QApplication

from src.Kliply.models import Settings
from src.Kliply.settings_manager import SettingsManager
from src.Kliply.onboarding_manager import OnboardingManager


@pytest.fixture
def qapp():
    """Provide QApplication instance for Qt tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def settings_manager():
    """Provide a SettingsManager instance with default settings."""
    return SettingsManager()


@pytest.fixture
def onboarding_manager(settings_manager):
    """Provide an OnboardingManager instance."""
    return OnboardingManager(settings_manager)


def test_first_launch_detection_default(qapp, onboarding_manager):
    """
    Test first launch detection with default settings.
    Validates: Requirements 11.1
    """
    # Default settings should have first_launch_complete=False
    assert onboarding_manager.should_show_welcome() is True


def test_first_launch_detection_completed(qapp):
    """
    Test first launch detection when already completed.
    Validates: Requirements 11.1
    """
    # Create settings with first_launch_complete=True
    settings = Settings(first_launch_complete=True)
    settings_manager = SettingsManager(settings)
    onboarding_manager = OnboardingManager(settings_manager)
    
    # Should not show welcome when already completed
    assert onboarding_manager.should_show_welcome() is False


def test_mark_welcome_complete(qapp, onboarding_manager):
    """
    Test marking welcome as complete.
    Validates: Requirements 11.7
    """
    # Initially should show welcome
    assert onboarding_manager.should_show_welcome() is True
    
    # Mark as complete
    onboarding_manager.mark_welcome_complete()
    
    # Should no longer show welcome
    assert onboarding_manager.should_show_welcome() is False


def test_mark_welcome_complete_updates_settings(qapp, settings_manager):
    """
    Test that marking welcome complete updates the settings.
    Validates: Requirements 11.7
    """
    onboarding_manager = OnboardingManager(settings_manager)
    
    # Verify initial state
    settings = settings_manager.get_settings()
    assert settings.first_launch_complete is False
    
    # Mark as complete
    onboarding_manager.mark_welcome_complete()
    
    # Verify settings were updated
    updated_settings = settings_manager.get_settings()
    assert updated_settings.first_launch_complete is True


def test_show_welcome_screen_delegates_to_ui_manager(qapp, onboarding_manager):
    """
    Test that show_welcome_screen delegates to UIManager.
    Validates: Requirements 11.1
    """
    # Create a mock UI manager
    mock_ui_manager = Mock()
    onboarding_manager.set_ui_manager(mock_ui_manager)
    
    # Call show_welcome_screen
    onboarding_manager.show_welcome_screen()
    
    # Verify UIManager's show_welcome_screen was called
    mock_ui_manager.show_welcome_screen.assert_called_once()


def test_show_welcome_screen_without_ui_manager(qapp, onboarding_manager):
    """
    Test that show_welcome_screen handles missing UIManager gracefully.
    Validates: Requirements 11.1
    """
    # Don't set a UI manager
    # This should not raise an exception
    onboarding_manager.show_welcome_screen()


def test_demonstrate_popup(qapp, onboarding_manager):
    """
    Test the "Try It Now" demonstration feature.
    Validates: Requirements 11.5, 11.6
    """
    # Create a mock UI manager
    mock_ui_manager = Mock()
    onboarding_manager.set_ui_manager(mock_ui_manager)
    
    # Call demonstrate_popup
    onboarding_manager.demonstrate_popup()
    
    # Verify UIManager's show_history_popup was called
    mock_ui_manager.show_history_popup.assert_called_once()


def test_demonstrate_popup_without_ui_manager(qapp, onboarding_manager):
    """
    Test that demonstrate_popup handles missing UIManager gracefully.
    Validates: Requirements 11.5, 11.6
    """
    # Don't set a UI manager
    # This should not raise an exception
    onboarding_manager.demonstrate_popup()


def test_set_ui_manager(qapp, onboarding_manager):
    """
    Test setting the UI manager.
    """
    mock_ui_manager = Mock()
    
    # Set the UI manager
    onboarding_manager.set_ui_manager(mock_ui_manager)
    
    # Verify it was set
    assert onboarding_manager._ui_manager is mock_ui_manager


def test_welcome_screen_display_logic_sequence(qapp, settings_manager):
    """
    Test the complete welcome screen display logic sequence.
    Validates: Requirements 11.1, 11.7
    """
    onboarding_manager = OnboardingManager(settings_manager)
    mock_ui_manager = Mock()
    onboarding_manager.set_ui_manager(mock_ui_manager)
    
    # Step 1: First launch - should show welcome
    assert onboarding_manager.should_show_welcome() is True
    
    # Step 2: Show welcome screen
    onboarding_manager.show_welcome_screen()
    mock_ui_manager.show_welcome_screen.assert_called_once()
    
    # Step 3: User completes welcome
    onboarding_manager.mark_welcome_complete()
    
    # Step 4: Should not show welcome again
    assert onboarding_manager.should_show_welcome() is False
    
    # Step 5: Verify settings persisted
    settings = settings_manager.get_settings()
    assert settings.first_launch_complete is True


def test_idempotent_mark_complete(qapp, onboarding_manager):
    """
    Test that marking welcome complete multiple times is idempotent.
    Validates: Requirements 11.7
    """
    # Mark complete multiple times
    onboarding_manager.mark_welcome_complete()
    onboarding_manager.mark_welcome_complete()
    onboarding_manager.mark_welcome_complete()
    
    # Should still be marked complete
    assert onboarding_manager.should_show_welcome() is False
    
    # Settings should still be correct
    settings = onboarding_manager.settings_manager.get_settings()
    assert settings.first_launch_complete is True
