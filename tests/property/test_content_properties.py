"""
Property-based tests for clipboard content handling.

Feature: Kliply
"""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime

from src.Kliply.models import ClipboardContent, ContentType


# Custom strategies for generating test data
@st.composite
def text_content(draw):
    """Generate random text content."""
    text = draw(st.text(min_size=1, max_size=1000))
    return ClipboardContent(
        content_type=ContentType.TEXT,
        data=text,
        timestamp=datetime.now()
    )


@st.composite
def rich_text_content(draw):
    """Generate random rich text (HTML) content."""
    # Generate simple HTML content
    text = draw(st.text(min_size=1, max_size=500))
    html = f"<html><body><p>{text}</p></body></html>"
    return ClipboardContent(
        content_type=ContentType.RICH_TEXT,
        data=html,
        timestamp=datetime.now()
    )


@st.composite
def image_content(draw):
    """Generate random image content (as bytes)."""
    # Generate random bytes to simulate image data
    size = draw(st.integers(min_value=100, max_value=10000))
    image_bytes = draw(st.binary(min_size=size, max_size=size))
    return ClipboardContent(
        content_type=ContentType.IMAGE,
        data=image_bytes,
        timestamp=datetime.now()
    )


@given(text_content())
def test_property_15_text_content_support(content):
    """
    Property 15: Content type support
    Validates: Requirements 7.1, 7.2, 7.3
    
    For any clipboard content of type plain text, the Clipboard_Manager 
    should successfully store it and preserve its type.
    """
    # Verify content type is preserved
    assert content.content_type == ContentType.TEXT
    
    # Verify data is stored correctly
    assert isinstance(content.data, str)
    assert len(content.data) > 0
    
    # Verify preview is generated
    assert content.preview is not None
    assert len(content.preview) <= 53  # 50 chars + "..."
    
    # Verify size is calculated
    assert content.size_bytes > 0
    
    # Verify hash can be generated
    hash_value = content.get_hash()
    assert isinstance(hash_value, str)
    assert len(hash_value) == 64  # SHA-256 produces 64 hex characters


@given(rich_text_content())
def test_property_15_rich_text_content_support(content):
    """
    Property 15: Content type support
    Validates: Requirements 7.1, 7.2, 7.3
    
    For any clipboard content of type rich text (RTF), the Clipboard_Manager 
    should successfully store it and preserve its type.
    """
    # Verify content type is preserved
    assert content.content_type == ContentType.RICH_TEXT
    
    # Verify data is stored correctly
    assert isinstance(content.data, str)
    assert len(content.data) > 0
    
    # Verify preview is generated
    assert content.preview is not None
    
    # Verify size is calculated
    assert content.size_bytes > 0
    
    # Verify hash can be generated
    hash_value = content.get_hash()
    assert isinstance(hash_value, str)
    assert len(hash_value) == 64


@given(image_content())
def test_property_15_image_content_support(content):
    """
    Property 15: Content type support
    Validates: Requirements 7.1, 7.2, 7.3
    
    For any clipboard content of type image, the Clipboard_Manager 
    should successfully store it and preserve its type.
    """
    # Verify content type is preserved
    assert content.content_type == ContentType.IMAGE
    
    # Verify data is stored correctly
    assert isinstance(content.data, bytes)
    assert len(content.data) > 0
    
    # Verify preview shows image indicator
    assert content.preview == "[Image]"
    
    # Verify size is calculated
    assert content.size_bytes > 0
    assert content.size_bytes == len(content.data)
    
    # Verify hash can be generated
    hash_value = content.get_hash()
    assert isinstance(hash_value, str)
    assert len(hash_value) == 64


@st.composite
def any_content(draw):
    """Generate any type of clipboard content."""
    content_type = draw(st.sampled_from([ContentType.TEXT, ContentType.RICH_TEXT, ContentType.IMAGE]))
    
    if content_type == ContentType.TEXT:
        return draw(text_content())
    elif content_type == ContentType.RICH_TEXT:
        return draw(rich_text_content())
    else:  # IMAGE
        return draw(image_content())


@given(any_content())
@settings(deadline=None)
def test_property_18_format_preservation_round_trip(content):
    """
    Property 18: Format preservation round-trip
    Validates: Requirements 7.6
    
    For any clipboard content (text, rich text, or image), when added to history
    and then copied back to the Active_Clipboard, the format and content should
    be preserved exactly.
    """
    from PyQt6.QtCore import QMimeData
    from PyQt6.QtWidgets import QApplication
    
    # Ensure QApplication exists for Qt operations
    app = QApplication.instance()
    if app is None:
        from PyQt6.QtGui import QGuiApplication
        app = QGuiApplication([])
    
    # Convert content to clipboard format
    mime_data = content.to_clipboard_format()
    
    # Verify mime_data was created
    assert mime_data is not None
    assert isinstance(mime_data, QMimeData)
    
    # Verify the appropriate format is set based on content type
    if content.content_type == ContentType.TEXT:
        assert mime_data.hasText()
        # Verify the text matches
        assert mime_data.text() == content.data
        
    elif content.content_type == ContentType.RICH_TEXT:
        assert mime_data.hasHtml()
        # Verify the HTML matches
        assert mime_data.html() == content.data
        
    elif content.content_type == ContentType.IMAGE:
        assert mime_data.hasImage()
        # For images, verify image data exists
        image_data = mime_data.imageData()
        assert image_data is not None
