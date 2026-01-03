"""
Property-based tests for history management.

Feature: Kliply
"""

import pytest
from hypothesis import given, strategies as st
from datetime import datetime

from src.Kliply.models import ClipboardContent, ContentType
from src.Kliply.history_manager import HistoryManager


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


@given(clipboard_content())
def test_property_1_new_content_added(content):
    """
    Property 1: New content is added to history
    Validates: Requirements 1.2
    
    For any clipboard content, when it is copied to the system clipboard,
    it should appear in the Clipboard_History.
    """
    manager = HistoryManager()
    
    # Add the content
    manager.add_item(content)
    
    # Verify it appears in history
    history = manager.get_history()
    assert len(history) > 0
    
    # Verify the content is in the history (by hash comparison)
    content_hash = content.get_hash()
    history_hashes = [item.get_hash() for item in history]
    assert content_hash in history_hashes



@given(clipboard_content(), st.lists(clipboard_content(), min_size=1, max_size=5))
def test_property_2_duplicate_moves_to_front(duplicate_content, other_contents):
    """
    Property 2: Duplicate content moves to front
    Validates: Requirements 1.3
    
    For any clipboard content that already exists in the history, when it is
    copied again, it should move to the front of the Clipboard_History and
    the total history size should not increase.
    """
    manager = HistoryManager(max_depth=20)
    
    # Add the duplicate content first
    manager.add_item(duplicate_content)
    
    # Add other contents
    for content in other_contents:
        manager.add_item(content)
    
    # Get history size before re-adding duplicate
    history_before = manager.get_history()
    size_before = len(history_before)
    
    # Re-add the duplicate content
    manager.add_item(duplicate_content)
    
    # Get history after
    history_after = manager.get_history()
    size_after = len(history_after)
    
    # Verify size did not increase
    assert size_after == size_before
    
    # Verify the duplicate is now at the front (index 0)
    assert history_after[0].get_hash() == duplicate_content.get_hash()
    
    # Verify the duplicate appears only once in history
    duplicate_hash = duplicate_content.get_hash()
    count = sum(1 for item in history_after if item.get_hash() == duplicate_hash)
    assert count == 1



@given(st.integers(min_value=5, max_value=20), st.lists(clipboard_content(), min_size=1, max_size=50))
def test_property_3_history_respects_depth_limit(max_depth, contents):
    """
    Property 3: History respects depth limit
    Validates: Requirements 1.4
    
    For any sequence of clipboard items exceeding the configured Clipboard_Depth,
    the Clipboard_History should never exceed the depth limit and should remove
    the oldest entries first.
    """
    manager = HistoryManager(max_depth=max_depth)
    
    # Add all contents
    for content in contents:
        manager.add_item(content)
    
    # Get history
    history = manager.get_history()
    
    # Verify history never exceeds max_depth
    assert len(history) <= max_depth
    
    # Count unique items in contents (by hash)
    unique_hashes = []
    for content in contents:
        h = content.get_hash()
        if h not in unique_hashes:
            unique_hashes.append(h)
    
    # The history size should be min(max_depth, number of unique items)
    expected_size = min(max_depth, len(unique_hashes))
    assert len(history) == expected_size
    
    # All items in history should be from the contents we added
    content_hashes = [c.get_hash() for c in contents]
    for item in history:
        assert item.get_hash() in content_hashes



@given(
    st.integers(min_value=10, max_value=20),
    st.integers(min_value=5, max_value=9),
    st.lists(clipboard_content(), min_size=15, max_size=25)
)
def test_property_4_depth_changes_applied_immediately(initial_depth, new_depth, contents):
    """
    Property 4: Depth changes are applied immediately
    Validates: Requirements 2.3, 2.4
    
    For any new Clipboard_Depth value (including reductions below current history size),
    when the depth is changed, the Clipboard_History should immediately reflect the new
    limit by removing the oldest entries if necessary.
    """
    manager = HistoryManager(max_depth=initial_depth)
    
    # Add contents to fill history beyond new_depth
    for content in contents:
        manager.add_item(content)
    
    # Get history before depth change
    history_before = manager.get_history()
    
    # Change depth to a smaller value
    manager.set_max_depth(new_depth)
    
    # Get history after depth change
    history_after = manager.get_history()
    
    # Verify new depth is applied immediately
    assert len(history_after) <= new_depth
    
    # If history was larger than new_depth, verify it was trimmed
    if len(history_before) > new_depth:
        assert len(history_after) == new_depth
        
        # Verify the most recent items were kept
        # (first new_depth items from history_before)
        kept_hashes = [item.get_hash() for item in history_before[:new_depth]]
        after_hashes = [item.get_hash() for item in history_after]
        
        assert kept_hashes == after_hashes
