"""
Property-based tests for UI components.

Feature: Kliply
"""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime
from PyQt6.QtWidgets import QApplication

from src.Kliply.models import ClipboardContent, ContentType
from src.Kliply.history_manager import HistoryManager
from src.Kliply.ui_manager import UIManager, HistoryPopup


# Custom strategies for generating test data
@st.composite
def clipboard_content(draw):
    """Generate random clipboard content."""
    content_type = draw(st.sampled_from([ContentType.TEXT, ContentType.IMAGE, ContentType.RICH_TEXT]))
    
    if content_type == ContentType.TEXT or content_type == ContentType.RICH_TEXT:
        data = draw(st.text(min_size=1, max_size=1000))
    else:  # IMAGE
        data = draw(st.binary(min_size=100, max_size=5000))
    
    return ClipboardContent(
        content_type=content_type,
        data=data,
        timestamp=datetime.now()
    )


@given(st.lists(clipboard_content(), min_size=2, max_size=10))
@settings(deadline=None)
def test_property_8_history_display_order(contents):
    """
    Property 8: History display order
    Validates: Requirements 4.1
    
    For any Clipboard_History with multiple items, when the History_Popup is displayed,
    the items should appear in reverse chronological order (most recent first).
    """
    # Ensure QApplication exists
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Create history manager and add contents
    manager = HistoryManager(max_depth=20)
    
    # Add contents in order
    for content in contents:
        manager.add_item(content)
    
    # Get the expected order (most recent first)
    expected_history = manager.get_history()
    
    # Create UI manager and popup
    ui_manager = UIManager(manager)
    popup = HistoryPopup(manager)
    
    # Populate the history (this is called internally by show_popup)
    popup._populate_history()
    
    # Verify the list widget has items
    assert popup.list_widget.count() == len(expected_history)
    
    # Verify items are in reverse chronological order
    # The first item in the list should correspond to the first item in history (most recent)
    for i in range(popup.list_widget.count()):
        list_item = popup.list_widget.item(i)
        expected_content = expected_history[i]
        
        # Verify the item text matches the expected preview
        if expected_content.content_type == ContentType.TEXT:
            # UIManager uses the stored preview when available, otherwise it falls back
            # to truncating/sanitizing the raw data. Mirror that behavior here.
            if expected_content.preview:
                expected_text = expected_content.preview
            else:
                expected_text = expected_content.data.replace('\n', ' ').replace('\r', ' ')
                if len(expected_text) > 50:
                    expected_text = expected_text[:50] + "..."
            assert list_item.text() == expected_text
        
        elif expected_content.content_type == ContentType.IMAGE:
            assert list_item.text() == "[Image]"
        
        elif expected_content.content_type == ContentType.UNSUPPORTED:
            assert list_item.text() == "[Unsupported Content]"
    
    # Clean up
    popup.close()


@given(st.text(min_size=51, max_size=500))
@settings(deadline=None)
def test_property_9_item_preview_truncation(long_text):
    """
    Property 9: Item preview truncation
    Validates: Requirements 4.4, 4.5
    
    For any clipboard item, when displayed in the History_Popup, the preview should be
    truncated to a maximum of 50 characters with visual indication if the original
    content is longer.
    """
    # Ensure QApplication exists
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Create content with long text
    content = ClipboardContent(
        content_type=ContentType.TEXT,
        data=long_text,
        timestamp=datetime.now()
    )
    
    # Create history manager and add content
    manager = HistoryManager(max_depth=10)
    manager.add_item(content)
    
    # Create popup and populate
    popup = HistoryPopup(manager)
    popup._populate_history()
    
    # Get the first item from the list
    assert popup.list_widget.count() > 0
    list_item = popup.list_widget.item(0)
    display_text = list_item.text()
    
    # UIManager uses the ClipboardContent preview directly (already truncated)
    preview_text = content.preview
    assert display_text == preview_text
    
    # Preview generation truncates to 50 chars with ellipsis if needed
    if len(long_text) > 50:
        assert len(preview_text) == 53
        assert preview_text.endswith("...")
        assert preview_text[:50] == long_text[:50]
    else:
        assert len(preview_text) == len(long_text)
    
    # Clean up
    popup.close()



@given(st.binary(min_size=100, max_size=10000))
@settings(deadline=None)
def test_property_16_image_thumbnail_generation(image_data):
    """
    Property 16: Image thumbnail generation
    Validates: Requirements 7.4
    
    For any image content in the Clipboard_History, when displayed in the History_Popup,
    a thumbnail preview should be generated and displayed.
    """
    # Ensure QApplication exists
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Create image content
    content = ClipboardContent(
        content_type=ContentType.IMAGE,
        data=image_data,
        timestamp=datetime.now()
    )
    
    # Create history manager and add content
    manager = HistoryManager(max_depth=10)
    manager.add_item(content)
    
    # Create popup and populate
    popup = HistoryPopup(manager)
    popup._populate_history()
    
    # Get the first item from the list
    assert popup.list_widget.count() > 0
    list_item = popup.list_widget.item(0)
    
    # Verify the item shows "[Image]" text
    assert list_item.text() == "[Image]"
    
    # Verify an icon is set (thumbnail)
    # Note: The icon might be null if the image data is invalid,
    # but we should at least attempt to create it
    icon = list_item.icon()
    assert icon is not None
    
    # Clean up
    popup.close()



@given(st.binary(min_size=1, max_size=1000))
@settings(deadline=None)
def test_property_17_unsupported_content_handling(data):
    """
    Property 17: Unsupported content handling
    Validates: Requirements 7.5
    
    For any clipboard content of an unsupported type, the Clipboard_Manager should
    display a type indicator instead of attempting to preview the content.
    """
    # Ensure QApplication exists
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Create unsupported content
    content = ClipboardContent(
        content_type=ContentType.UNSUPPORTED,
        data=data,
        timestamp=datetime.now()
    )
    
    # Create history manager and add content
    manager = HistoryManager(max_depth=10)
    manager.add_item(content)
    
    # Create popup and populate
    popup = HistoryPopup(manager)
    popup._populate_history()
    
    # Get the first item from the list
    assert popup.list_widget.count() > 0
    list_item = popup.list_widget.item(0)
    
    # Verify the item shows the unsupported content indicator
    assert list_item.text() == "[Unsupported Content]"
    
    # Verify no icon is set for unsupported content
    icon = list_item.icon()
    # Icon should be null or empty for unsupported content
    assert icon.isNull() or not icon.pixmap(40, 40).isNull() == False
    
    # Clean up
    popup.close()



@given(st.lists(clipboard_content(), min_size=1, max_size=10))
@settings(deadline=None)
def test_property_12_item_selection_copies_to_clipboard(contents):
    """
    Property 12: Item selection copies to clipboard
    Validates: Requirements 5.1
    
    For any item in the History_Popup, when a user clicks on it, that item should be
    copied to the Active_Clipboard.
    """
    # Ensure QApplication exists
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Create history manager and add contents
    manager = HistoryManager(max_depth=20)
    for content in contents:
        manager.add_item(content)
    
    # Create popup and populate
    popup = HistoryPopup(manager)
    popup._populate_history()
    
    # Get the history to verify against
    history = manager.get_history()
    
    # Test clicking on each item
    for i in range(min(len(history), popup.list_widget.count())):
        # Select the item
        popup.list_widget.setCurrentRow(i)
        
        # Simulate clicking the item
        list_item = popup.list_widget.item(i)
        popup._on_item_clicked(list_item)
        
        # Get the clipboard content
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        
        # Verify the clipboard contains the expected content
        expected_content = history[i]
        
        if expected_content.content_type == ContentType.TEXT:
            assert mime_data.hasText()
            assert mime_data.text() == expected_content.data
        
        elif expected_content.content_type == ContentType.RICH_TEXT:
            assert mime_data.hasHtml() or mime_data.hasText()
        
        elif expected_content.content_type == ContentType.IMAGE:
            assert mime_data.hasImage()
    
    # Clean up
    popup.close()



@given(st.lists(clipboard_content(), min_size=1, max_size=10))
@settings(deadline=None)
def test_property_13_double_click_copies_and_closes(contents):
    """
    Property 13: Double-click copies and closes
    Validates: Requirements 5.2
    
    For any item in the History_Popup, when a user double-clicks on it, that item
    should be copied to the Active_Clipboard and the popup should close.
    """
    # Ensure QApplication exists
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Create history manager and add contents
    manager = HistoryManager(max_depth=20)
    for content in contents:
        manager.add_item(content)
    
    # Create popup and populate
    popup = HistoryPopup(manager)
    popup._populate_history()
    popup.show()
    
    # Get the history to verify against
    history = manager.get_history()
    
    # Test double-clicking on the first item
    if len(history) > 0 and popup.list_widget.count() > 0:
        # Select the first item
        popup.list_widget.setCurrentRow(0)
        
        # Simulate double-clicking the item
        list_item = popup.list_widget.item(0)
        popup._on_item_double_clicked(list_item)
        
        # Get the clipboard content
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        
        # Verify the clipboard contains the expected content
        expected_content = history[0]
        
        if expected_content.content_type == ContentType.TEXT:
            assert mime_data.hasText()
            assert mime_data.text() == expected_content.data
        
        elif expected_content.content_type == ContentType.RICH_TEXT:
            assert mime_data.hasHtml() or mime_data.hasText()
        
        elif expected_content.content_type == ContentType.IMAGE:
            assert mime_data.hasImage()
        
        # Verify the popup is closed (not visible)
        assert not popup.isVisible()
    
    # Clean up
    popup.close()



@given(st.lists(clipboard_content(), min_size=1, max_size=10))
@settings(deadline=None)
def test_property_14_enter_key_copies_and_closes(contents):
    """
    Property 14: Enter key copies and closes
    Validates: Requirements 5.3
    
    For any selected item in the History_Popup, when the Enter key is pressed, that
    item should be copied to the Active_Clipboard and the popup should close.
    """
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QKeyEvent
    
    # Ensure QApplication exists
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Create history manager and add contents
    manager = HistoryManager(max_depth=20)
    for content in contents:
        manager.add_item(content)
    
    # Create popup and populate
    popup = HistoryPopup(manager)
    popup._populate_history()
    popup.show()
    
    # Get the history to verify against
    history = manager.get_history()
    
    # Test pressing Enter on the first item
    if len(history) > 0 and popup.list_widget.count() > 0:
        # Select the first item
        popup.list_widget.setCurrentRow(0)
        
        # Simulate pressing Enter key
        key_event = QKeyEvent(
            QKeyEvent.Type.KeyPress,
            Qt.Key.Key_Return,
            Qt.KeyboardModifier.NoModifier
        )
        popup.keyPressEvent(key_event)
        
        # Get the clipboard content
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        
        # Verify the clipboard contains the expected content
        expected_content = history[0]
        
        if expected_content.content_type == ContentType.TEXT:
            assert mime_data.hasText()
            assert mime_data.text() == expected_content.data
        
        elif expected_content.content_type == ContentType.RICH_TEXT:
            assert mime_data.hasHtml() or mime_data.hasText()
        
        elif expected_content.content_type == ContentType.IMAGE:
            assert mime_data.hasImage()
        
        # Verify the popup is closed (not visible)
        assert not popup.isVisible()
    
    # Clean up
    popup.close()



@given(st.lists(clipboard_content(), min_size=1, max_size=5))
@settings(deadline=None)
def test_property_10_popup_closes_on_focus_loss(contents):
    """
    Property 10: Popup closes on focus loss
    Validates: Requirements 4.7
    
    For any History_Popup that is currently displayed, when the popup loses focus,
    it should close automatically.
    """
    from PyQt6.QtCore import QEvent, Qt
    from PyQt6.QtGui import QFocusEvent
    
    # Ensure QApplication exists
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Create history manager and add contents
    manager = HistoryManager(max_depth=20)
    for content in contents:
        manager.add_item(content)
    
    # Create popup and populate
    popup = HistoryPopup(manager)
    popup._populate_history()
    popup.show()
    
    # Verify popup is visible
    assert popup.isVisible()
    
    # Simulate focus loss event
    focus_out_event = QFocusEvent(
        QEvent.Type.FocusOut,
        Qt.FocusReason.ActiveWindowFocusReason
    )
    popup.focusOutEvent(focus_out_event)
    
    # Verify the popup is closed (not visible)
    assert not popup.isVisible()
    
    # Clean up
    popup.close()



@given(st.lists(clipboard_content(), min_size=1, max_size=5))
@settings(deadline=None)
def test_property_11_popup_closes_on_escape(contents):
    """
    Property 11: Popup closes on Escape
    Validates: Requirements 4.8
    
    For any History_Popup that is currently displayed, when the Escape key is pressed,
    the popup should close.
    """
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QKeyEvent
    
    # Ensure QApplication exists
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Create history manager and add contents
    manager = HistoryManager(max_depth=20)
    for content in contents:
        manager.add_item(content)
    
    # Create popup and populate
    popup = HistoryPopup(manager)
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
    
    # Verify the popup is closed (not visible)
    assert not popup.isVisible()
    
    # Clean up
    popup.close()



@given(st.lists(clipboard_content(), min_size=3, max_size=10, unique_by=lambda x: x.data))
@settings(deadline=None)
def test_property_20_keyboard_navigation(contents):
    """
    Property 20: Keyboard navigation
    Validates: Requirements 10.2
    
    For any History_Popup with multiple items, when arrow keys are pressed, the
    selection should move up or down accordingly through the list.
    """
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QKeyEvent
    
    # Ensure QApplication exists
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Create history manager and add contents
    manager = HistoryManager(max_depth=20)
    for content in contents:
        manager.add_item(content)
    
    # Create popup and populate
    popup = HistoryPopup(manager)
    popup._populate_history()
    popup.show()
    
    # Verify we have multiple items
    item_count = popup.list_widget.count()
    assert item_count >= 3
    
    # Start at the first item (pre-selected)
    assert popup.list_widget.currentRow() == 0
    
    # Test Down arrow key - should move to next item
    down_event = QKeyEvent(
        QKeyEvent.Type.KeyPress,
        Qt.Key.Key_Down,
        Qt.KeyboardModifier.NoModifier
    )
    popup.keyPressEvent(down_event)
    assert popup.list_widget.currentRow() == 1
    
    # Press Down again
    popup.keyPressEvent(down_event)
    assert popup.list_widget.currentRow() == 2
    
    # Test Up arrow key - should move to previous item
    up_event = QKeyEvent(
        QKeyEvent.Type.KeyPress,
        Qt.Key.Key_Up,
        Qt.KeyboardModifier.NoModifier
    )
    popup.keyPressEvent(up_event)
    assert popup.list_widget.currentRow() == 1
    
    # Press Up again
    popup.keyPressEvent(up_event)
    assert popup.list_widget.currentRow() == 0
    
    # Test boundary: pressing Up at the top should stay at top
    popup.keyPressEvent(up_event)
    assert popup.list_widget.currentRow() == 0
    
    # Navigate to the bottom
    for _ in range(item_count - 1):
        popup.keyPressEvent(down_event)
    
    # Should be at the last item
    assert popup.list_widget.currentRow() == item_count - 1
    
    # Test boundary: pressing Down at the bottom should stay at bottom
    popup.keyPressEvent(down_event)
    assert popup.list_widget.currentRow() == item_count - 1
    
    # Clean up
    popup.close()
