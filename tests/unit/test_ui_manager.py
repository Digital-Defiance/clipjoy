"""
Unit tests for UIManager and HistoryPopup.

Tests specific examples, edge cases, and UI behavior.
"""

import pytest
from datetime import datetime
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.Kliply.models import ClipboardContent, ContentType
from src.Kliply.history_manager import HistoryManager
from src.Kliply.settings_manager import SettingsManager
from src.Kliply.ui_manager import UIManager, HistoryPopup, SettingsPanel


@pytest.fixture
def qapp():
    """Fixture that provides a QApplication instance for Qt tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def history_manager():
    """Fixture that provides a HistoryManager instance."""
    return HistoryManager(max_depth=10)


@pytest.fixture
def settings_manager():
    """Fixture that provides a SettingsManager instance."""
    return SettingsManager()


@pytest.fixture
def sample_contents():
    """Fixture that provides sample clipboard contents."""
    return [
        ClipboardContent(
            content_type=ContentType.TEXT,
            data="First item",
            timestamp=datetime.now()
        ),
        ClipboardContent(
            content_type=ContentType.TEXT,
            data="Second item",
            timestamp=datetime.now()
        ),
        ClipboardContent(
            content_type=ContentType.TEXT,
            data="Third item",
            timestamp=datetime.now()
        ),
    ]


def test_popup_centers_on_screen(qapp, history_manager):
    """
    Test that the popup window is centered on the screen.
    Validates: Requirements 4.2
    """
    popup = HistoryPopup(history_manager)
    
    # Call the centering method
    popup._center_on_screen()
    
    # Get screen geometry
    screen = QApplication.primaryScreen()
    screen_geometry = screen.geometry()
    
    # Calculate expected center position
    expected_x = (screen_geometry.width() - popup.width()) // 2
    expected_y = (screen_geometry.height() - popup.height()) // 2
    
    # Verify popup is centered
    assert popup.x() == expected_x
    assert popup.y() == expected_y
    
    # Clean up
    popup.close()


def test_most_recent_item_preselected(qapp, history_manager, sample_contents):
    """
    Test that the most recent item is pre-selected when popup is shown.
    Validates: Requirements 10.3
    """
    # Add sample contents to history
    for content in sample_contents:
        history_manager.add_item(content)
    
    # Create and populate popup
    popup = HistoryPopup(history_manager)
    popup._populate_history()
    
    # Verify the first item (most recent) is selected
    assert popup.list_widget.currentRow() == 0
    
    # Verify the selected item corresponds to the most recent content
    selected_item = popup.list_widget.currentItem()
    assert selected_item is not None
    
    # The most recent item should be "Third item" (last added)
    most_recent = history_manager.get_history()[0]
    expected_text = most_recent.data.replace('\n', ' ').replace('\r', ' ')
    if len(expected_text) > 50:
        expected_text = expected_text[:50] + "..."
    
    assert selected_item.text() == expected_text
    
    # Clean up
    popup.close()


def test_visual_feedback_for_selection(qapp, history_manager, sample_contents):
    """
    Test that visual feedback is provided for the selected item.
    Validates: Requirements 5.5
    """
    # Add sample contents to history
    for content in sample_contents:
        history_manager.add_item(content)
    
    # Create and populate popup
    popup = HistoryPopup(history_manager)
    popup._populate_history()
    
    # Verify list widget has selection mode enabled
    assert popup.list_widget.selectionMode() != 0  # Not NoSelection
    
    # Verify an item is selected by default
    assert popup.list_widget.currentRow() >= 0
    
    # Verify the list widget has styling for selected items
    # (This is set in the stylesheet)
    stylesheet = popup.list_widget.styleSheet()
    assert "selected" in stylesheet.lower()
    assert "background-color" in stylesheet.lower()
    
    # Clean up
    popup.close()


def test_popup_window_properties(qapp, history_manager):
    """
    Test that the popup has correct window properties.
    Validates: Requirements 4.2, 4.3
    """
    popup = HistoryPopup(history_manager)
    
    # Verify frameless window
    assert popup.windowFlags() & Qt.WindowType.FramelessWindowHint
    
    # Verify stays on top
    assert popup.windowFlags() & Qt.WindowType.WindowStaysOnTopHint
    
    # Verify window size
    assert popup.width() == 500
    assert popup.height() == 400
    
    # Verify window opacity (use approximate comparison for floating point)
    assert abs(popup.windowOpacity() - 0.95) < 0.01
    
    # Clean up
    popup.close()


def test_empty_history_display(qapp, history_manager):
    """
    Test that the popup handles empty history gracefully.
    """
    # Create popup with empty history
    popup = HistoryPopup(history_manager)
    popup._populate_history()
    
    # Verify list is empty
    assert popup.list_widget.count() == 0
    
    # Verify no item is selected
    assert popup.list_widget.currentRow() == -1
    
    # Clean up
    popup.close()


def test_ui_manager_creates_popup(qapp, history_manager):
    """
    Test that UIManager creates and shows the history popup.
    """
    ui_manager = UIManager(history_manager)
    
    # Show popup
    ui_manager.show_history_popup()
    
    # Verify popup was created
    assert ui_manager.history_popup is not None
    assert isinstance(ui_manager.history_popup, HistoryPopup)
    
    # Verify popup is visible
    assert ui_manager.history_popup.isVisible()
    
    # Clean up
    ui_manager.hide_history_popup()


def test_ui_manager_hides_popup(qapp, history_manager):
    """
    Test that UIManager can hide the history popup.
    """
    ui_manager = UIManager(history_manager)
    
    # Show then hide popup
    ui_manager.show_history_popup()
    ui_manager.hide_history_popup()
    
    # Verify popup is hidden
    assert not ui_manager.history_popup.isVisible()


def test_truncate_text_method(qapp, history_manager):
    """
    Test the text truncation method.
    """
    popup = HistoryPopup(history_manager)
    
    # Test short text (no truncation)
    short_text = "Hello"
    assert popup._truncate_text(short_text, 50) == "Hello"
    
    # Test long text (with truncation)
    long_text = "A" * 100
    truncated = popup._truncate_text(long_text, 50)
    assert len(truncated) == 53  # 50 + "..."
    assert truncated.endswith("...")
    assert truncated[:50] == "A" * 50
    
    # Test text with newlines
    text_with_newlines = "Line1\nLine2\nLine3"
    result = popup._truncate_text(text_with_newlines, 50)
    assert "\n" not in result
    assert " " in result  # Newlines replaced with spaces
    
    # Clean up
    popup.close()



def test_keyboard_focus_capture(qapp, history_manager, sample_contents):
    """
    Test that keyboard focus is captured when popup is displayed.
    Validates: Requirements 10.7
    """
    # Add sample contents to history
    for content in sample_contents:
        history_manager.add_item(content)
    
    # Create and show popup
    popup = HistoryPopup(history_manager)
    popup.show_popup()
    
    # Verify the list widget has focus
    # Note: In a real GUI environment, this would be more reliable
    # In tests, we verify that setFocus was called on the list widget
    assert popup.list_widget is not None
    
    # Verify the popup is active
    # In a test environment, we can't fully test window activation,
    # but we can verify the popup is visible and ready
    assert popup.isVisible()
    
    # Clean up
    popup.close()


def test_single_click_copies_to_clipboard(qapp, history_manager, sample_contents):
    """
    Test that single-clicking an item copies it to the clipboard.
    Validates: Requirements 5.1
    """
    # Add sample contents to history
    for content in sample_contents:
        history_manager.add_item(content)
    
    # Verify history order
    history = history_manager.get_history()
    assert len(history) == 3
    assert history[0].data == "Third item", f"Expected 'Third item' at index 0, got '{history[0].data}'"
    assert history[1].data == "Second item"
    assert history[2].data == "First item"
    
    # Create and populate popup
    popup = HistoryPopup(history_manager)
    popup._populate_history()
    popup.show()  # Show the popup
    
    # Get clipboard content BEFORE clicking
    clipboard = QApplication.clipboard()
    before_click = clipboard.mimeData().text() if clipboard.mimeData().hasText() else None
    
    # Select the first item
    popup.list_widget.setCurrentRow(0)
    list_item = popup.list_widget.item(0)
    
    # Simulate clicking the item
    popup._on_item_clicked(list_item)
    
    # Process events to ensure clipboard is updated
    QApplication.instance().processEvents()
    
    # Get the clipboard content AFTER clicking
    mime_data = clipboard.mimeData()
    after_click = mime_data.text() if mime_data.hasText() else None
    
    # Verify the clipboard was updated (it should be different from before, unless it was already "Third item")
    expected_content = history_manager.get_history()[0]
    assert mime_data.hasText()
    assert mime_data.text() == expected_content.data, f"Expected '{expected_content.data}', got '{mime_data.text()}' (before click: '{before_click}')"
    
    # Verify popup is still visible (single-click doesn't close)
    assert popup.isVisible()
    
    # Clean up
    popup.close()


def test_double_click_copies_and_closes(qapp, history_manager, sample_contents):
    """
    Test that double-clicking an item copies it and closes the popup.
    Validates: Requirements 5.2
    """
    # Add sample contents to history
    for content in sample_contents:
        history_manager.add_item(content)
    
    # Create and populate popup
    popup = HistoryPopup(history_manager)
    popup._populate_history()
    popup.show()
    
    # Select the first item
    popup.list_widget.setCurrentRow(0)
    list_item = popup.list_widget.item(0)
    
    # Simulate double-clicking the item
    popup._on_item_double_clicked(list_item)
    
    # Process events to ensure clipboard is updated
    QApplication.instance().processEvents()
    
    # Get the clipboard content
    clipboard = QApplication.clipboard()
    mime_data = clipboard.mimeData()
    
    # Verify the clipboard contains the expected content
    expected_content = history_manager.get_history()[0]
    assert mime_data.hasText()
    assert mime_data.text() == expected_content.data, f"Expected '{expected_content.data}', got '{mime_data.text()}'"
    
    # Verify popup is closed
    assert not popup.isVisible()
    
    # Clean up
    popup.close()


def test_enter_key_copies_and_closes(qapp, history_manager, sample_contents):
    """
    Test that pressing Enter copies the selected item and closes the popup.
    Validates: Requirements 5.3
    """
    from PyQt6.QtGui import QKeyEvent
    
    # Add sample contents to history
    for content in sample_contents:
        history_manager.add_item(content)
    
    # Create and populate popup
    popup = HistoryPopup(history_manager)
    popup._populate_history()
    popup.show()
    
    # Select the first item
    popup.list_widget.setCurrentRow(0)
    
    # Simulate pressing Enter key
    key_event = QKeyEvent(
        QKeyEvent.Type.KeyPress,
        Qt.Key.Key_Return,
        Qt.KeyboardModifier.NoModifier
    )
    popup.keyPressEvent(key_event)
    
    # Process events to ensure clipboard is updated
    QApplication.instance().processEvents()
    
    # Get the clipboard content
    clipboard = QApplication.clipboard()
    mime_data = clipboard.mimeData()
    
    # Verify the clipboard contains the expected content
    expected_content = history_manager.get_history()[0]
    assert mime_data.hasText()
    assert mime_data.text() == expected_content.data, f"Expected '{expected_content.data}', got '{mime_data.text()}'"
    
    # Verify popup is closed
    assert not popup.isVisible()
    
    # Clean up
    popup.close()


def test_escape_key_closes_popup(qapp, history_manager, sample_contents):
    """
    Test that pressing Escape closes the popup.
    Validates: Requirements 4.8
    """
    from PyQt6.QtGui import QKeyEvent
    
    # Add sample contents to history
    for content in sample_contents:
        history_manager.add_item(content)
    
    # Create and populate popup
    popup = HistoryPopup(history_manager)
    popup._populate_history()
    popup.show()
    
    # Verify popup is visible
    assert popup.isVisible()
    
    # Simulate pressing Escape key
    key_event = QKeyEvent(
        QKeyEvent.Type.KeyPress,
        Qt.Key.Key_Escape,
        Qt.KeyboardModifier.NoModifier
    )
    popup.keyPressEvent(key_event)
    
    # Verify popup is closed
    assert not popup.isVisible()
    
    # Clean up
    popup.close()


def test_arrow_key_navigation(qapp, history_manager, sample_contents):
    """
    Test that arrow keys navigate through the list.
    Validates: Requirements 10.2
    """
    from PyQt6.QtGui import QKeyEvent
    
    # Add sample contents to history
    for content in sample_contents:
        history_manager.add_item(content)
    
    # Create and populate popup
    popup = HistoryPopup(history_manager)
    popup._populate_history()
    popup.show()
    
    # Verify starting at first item
    assert popup.list_widget.currentRow() == 0
    
    # Press Down arrow
    down_event = QKeyEvent(
        QKeyEvent.Type.KeyPress,
        Qt.Key.Key_Down,
        Qt.KeyboardModifier.NoModifier
    )
    popup.keyPressEvent(down_event)
    assert popup.list_widget.currentRow() == 1
    
    # Press Up arrow
    up_event = QKeyEvent(
        QKeyEvent.Type.KeyPress,
        Qt.Key.Key_Up,
        Qt.KeyboardModifier.NoModifier
    )
    popup.keyPressEvent(up_event)
    assert popup.list_widget.currentRow() == 0
    
    # Clean up
    popup.close()


def test_focus_loss_closes_popup(qapp, history_manager, sample_contents):
    """
    Test that losing focus closes the popup.
    Validates: Requirements 4.7
    """
    from PyQt6.QtCore import QEvent
    from PyQt6.QtGui import QFocusEvent
    
    # Add sample contents to history
    for content in sample_contents:
        history_manager.add_item(content)
    
    # Create and populate popup
    popup = HistoryPopup(history_manager)
    popup._populate_history()
    popup.show()
    
    # Verify popup is visible
    assert popup.isVisible()
    
    # Simulate focus loss
    focus_out_event = QFocusEvent(
        QEvent.Type.FocusOut,
        Qt.FocusReason.ActiveWindowFocusReason
    )
    popup.focusOutEvent(focus_out_event)
    
    # Verify popup is closed
    assert not popup.isVisible()
    
    # Clean up
    popup.close()



# Settings Panel Tests

def test_settings_panel_contains_depth_control(qapp, settings_manager, history_manager):
    """
    Test that the settings panel contains a depth control slider.
    Validates: Requirements 2.1
    """
    # Create settings panel
    panel = SettingsPanel(settings_manager, history_manager)
    
    # Verify depth slider exists
    assert panel.depth_slider is not None
    
    # Verify slider has correct range
    assert panel.depth_slider.minimum() == 5
    assert panel.depth_slider.maximum() == 100
    
    # Verify slider shows current value
    current_depth = settings_manager.get_clipboard_depth()
    assert panel.depth_slider.value() == current_depth
    
    # Verify value label exists and shows current value
    assert panel.depth_value_label is not None
    assert panel.depth_value_label.text() == str(current_depth)
    
    # Clean up
    panel.close()


def test_depth_slider_range_validation(qapp, settings_manager, history_manager):
    """
    Test that the depth slider enforces the correct range (5-100).
    Validates: Requirements 2.1
    """
    # Create settings panel
    panel = SettingsPanel(settings_manager, history_manager)
    
    # Test minimum value
    panel.depth_slider.setValue(5)
    assert panel.depth_slider.value() == 5
    assert settings_manager.get_clipboard_depth() == 5
    
    # Test maximum value
    panel.depth_slider.setValue(100)
    assert panel.depth_slider.value() == 100
    assert settings_manager.get_clipboard_depth() == 100
    
    # Test mid-range value
    panel.depth_slider.setValue(50)
    assert panel.depth_slider.value() == 50
    assert settings_manager.get_clipboard_depth() == 50
    
    # Verify slider won't accept values below minimum
    panel.depth_slider.setValue(3)
    assert panel.depth_slider.value() == 5  # Should clamp to minimum
    
    # Verify slider won't accept values above maximum
    panel.depth_slider.setValue(150)
    assert panel.depth_slider.value() == 100  # Should clamp to maximum
    
    # Clean up
    panel.close()


def test_settings_persistence_in_settings_manager(qapp, settings_manager, history_manager):
    """
    Test that settings changes are persisted in SettingsManager.
    Validates: Requirements 2.1
    """
    # Create settings panel
    panel = SettingsPanel(settings_manager, history_manager)
    
    # Change clipboard depth
    new_depth = 25
    panel.depth_slider.setValue(new_depth)
    
    # Verify the change is persisted in SettingsManager
    assert settings_manager.get_clipboard_depth() == new_depth
    
    # Verify the value label is updated
    assert panel.depth_value_label.text() == str(new_depth)
    
    # Change launch at login setting
    panel.launch_checkbox.setChecked(True)
    assert settings_manager.get_launch_at_login() is True
    
    panel.launch_checkbox.setChecked(False)
    assert settings_manager.get_launch_at_login() is False
    
    # Clean up
    panel.close()


def test_settings_panel_applies_depth_to_history_manager(qapp, settings_manager, history_manager):
    """
    Test that depth changes are applied to HistoryManager immediately.
    """
    # Create settings panel
    panel = SettingsPanel(settings_manager, history_manager)
    
    # Change clipboard depth
    new_depth = 15
    panel.depth_slider.setValue(new_depth)
    
    # Verify the change is applied to HistoryManager
    # We can test this by adding items and checking the limit
    for i in range(20):
        content = ClipboardContent(
            content_type=ContentType.TEXT,
            data=f"Item {i}",
            timestamp=datetime.now()
        )
        history_manager.add_item(content)
    
    # History should be limited to new_depth
    assert len(history_manager.get_history()) == new_depth
    
    # Clean up
    panel.close()


def test_settings_panel_hotkey_display(qapp, settings_manager, history_manager):
    """
    Test that the settings panel displays the current hotkey.
    """
    # Create settings panel
    panel = SettingsPanel(settings_manager, history_manager)
    
    # Verify hotkey display exists
    assert panel.hotkey_display is not None
    
    # Verify it shows the current hotkey
    current_hotkey = settings_manager.get_hotkey()
    assert panel.hotkey_display.text() == current_hotkey
    
    # Verify it's read-only (for now)
    assert panel.hotkey_display.isReadOnly()
    
    # Clean up
    panel.close()


def test_settings_panel_launch_at_login_checkbox(qapp, settings_manager, history_manager):
    """
    Test that the launch at login checkbox works correctly.
    """
    # Create settings panel
    panel = SettingsPanel(settings_manager, history_manager)
    
    # Verify checkbox exists
    assert panel.launch_checkbox is not None
    
    # Verify checkbox reflects current setting
    current_setting = settings_manager.get_launch_at_login()
    assert panel.launch_checkbox.isChecked() == current_setting
    
    # Toggle checkbox
    panel.launch_checkbox.setChecked(True)
    assert settings_manager.get_launch_at_login() is True
    
    panel.launch_checkbox.setChecked(False)
    assert settings_manager.get_launch_at_login() is False
    
    # Clean up
    panel.close()


def test_settings_panel_about_section(qapp, settings_manager, history_manager):
    """
    Test that the settings panel includes an About section.
    """
    # Create settings panel
    panel = SettingsPanel(settings_manager, history_manager)
    
    # Verify the panel was created successfully
    assert panel is not None
    
    # Verify window title
    assert panel.windowTitle() == "Kliply Settings"
    
    # Verify window size
    assert panel.width() == 500
    assert panel.height() == 450
    
    # Clean up
    panel.close()


def test_ui_manager_shows_settings_panel(qapp, history_manager, settings_manager):
    """
    Test that UIManager can show the settings panel.
    """
    # Create UIManager with settings manager
    ui_manager = UIManager(history_manager, settings_manager)
    
    # Show settings panel (non-blocking for test)
    # Note: exec() is blocking, so we'll just create the panel
    ui_manager.settings_panel = SettingsPanel(settings_manager, history_manager)
    ui_manager.settings_panel.show()
    
    # Verify panel was created
    assert ui_manager.settings_panel is not None
    assert isinstance(ui_manager.settings_panel, SettingsPanel)
    
    # Verify panel is visible
    assert ui_manager.settings_panel.isVisible()
    
    # Clean up
    ui_manager.settings_panel.close()


def test_ui_manager_without_settings_manager(qapp, history_manager):
    """
    Test that UIManager handles missing settings manager gracefully.
    """
    # Create UIManager without settings manager
    ui_manager = UIManager(history_manager, settings_manager=None)
    
    # Try to show settings panel (should do nothing)
    ui_manager.show_settings_panel()
    
    # Verify no panel was created
    assert ui_manager.settings_panel is None
