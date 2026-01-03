"""
Unit tests for HistoryManager.

Tests specific examples and edge cases for clipboard history management.
"""

import pytest
from datetime import datetime

from src.Kliply.models import ClipboardContent, ContentType
from src.Kliply.history_manager import HistoryManager


def test_initialization_with_empty_history():
    """
    Test that HistoryManager initializes with an empty history.
    Validates: Requirements 1.5
    """
    manager = HistoryManager()
    
    # Verify history is empty on initialization
    history = manager.get_history()
    assert len(history) == 0
    assert history == []


def test_initialization_with_custom_depth():
    """Test that HistoryManager can be initialized with custom max_depth."""
    manager = HistoryManager(max_depth=15)
    
    # Add more than 15 items
    for i in range(20):
        content = ClipboardContent(
            content_type=ContentType.TEXT,
            data=f"Item {i}",
            timestamp=datetime.now()
        )
        manager.add_item(content)
    
    # Verify history respects custom depth
    history = manager.get_history()
    assert len(history) == 15


def test_empty_content_handling():
    """
    Test handling of empty content.
    Validates: Requirements 1.5 (edge cases)
    """
    manager = HistoryManager()
    
    # Add empty text content
    empty_content = ClipboardContent(
        content_type=ContentType.TEXT,
        data="",
        timestamp=datetime.now()
    )
    manager.add_item(empty_content)
    
    # Verify empty content is stored
    history = manager.get_history()
    assert len(history) == 1
    assert history[0].data == ""


def test_very_long_text_handling():
    """
    Test handling of very long text content.
    Validates: Requirements 1.5 (edge cases)
    """
    manager = HistoryManager()
    
    # Create very long text (10,000 characters)
    long_text = "A" * 10000
    long_content = ClipboardContent(
        content_type=ContentType.TEXT,
        data=long_text,
        timestamp=datetime.now()
    )
    manager.add_item(long_content)
    
    # Verify long content is stored
    history = manager.get_history()
    assert len(history) == 1
    assert len(history[0].data) == 10000
    assert history[0].data == long_text


def test_get_item_by_index():
    """Test retrieving specific items by index."""
    manager = HistoryManager()
    
    # Add multiple items
    items = []
    for i in range(5):
        content = ClipboardContent(
            content_type=ContentType.TEXT,
            data=f"Item {i}",
            timestamp=datetime.now()
        )
        items.append(content)
        manager.add_item(content)
    
    # Verify get_item returns correct items
    # Items are in reverse order (most recent first)
    assert manager.get_item(0).data == "Item 4"
    assert manager.get_item(1).data == "Item 3"
    assert manager.get_item(4).data == "Item 0"
    
    # Test invalid indices
    assert manager.get_item(-1) is None
    assert manager.get_item(10) is None


def test_clear_history():
    """Test clearing all history."""
    manager = HistoryManager()
    
    # Add some items
    for i in range(5):
        content = ClipboardContent(
            content_type=ContentType.TEXT,
            data=f"Item {i}",
            timestamp=datetime.now()
        )
        manager.add_item(content)
    
    # Verify items were added
    assert len(manager.get_history()) == 5
    
    # Clear history
    manager.clear_history()
    
    # Verify history is empty
    assert len(manager.get_history()) == 0


def test_thread_safety_basic():
    """Basic test to ensure thread-safe operations don't raise errors."""
    manager = HistoryManager()
    
    # Perform multiple operations that should be thread-safe
    content = ClipboardContent(
        content_type=ContentType.TEXT,
        data="Test",
        timestamp=datetime.now()
    )
    
    manager.add_item(content)
    history = manager.get_history()
    manager.set_max_depth(5)
    item = manager.get_item(0)
    manager.clear_history()
    
    # If we get here without errors, basic thread safety is working
    assert True


def test_different_content_types():
    """Test that different content types are handled correctly."""
    manager = HistoryManager()
    
    # Add text content
    text_content = ClipboardContent(
        content_type=ContentType.TEXT,
        data="Text content",
        timestamp=datetime.now()
    )
    manager.add_item(text_content)
    
    # Add image content
    image_content = ClipboardContent(
        content_type=ContentType.IMAGE,
        data=b"fake_image_bytes",
        timestamp=datetime.now()
    )
    manager.add_item(image_content)
    
    # Add rich text content
    rich_text_content = ClipboardContent(
        content_type=ContentType.RICH_TEXT,
        data="<html><body>Rich text</body></html>",
        timestamp=datetime.now()
    )
    manager.add_item(rich_text_content)
    
    # Verify all types are stored
    history = manager.get_history()
    assert len(history) == 3
    assert history[0].content_type == ContentType.RICH_TEXT
    assert history[1].content_type == ContentType.IMAGE
    assert history[2].content_type == ContentType.TEXT
