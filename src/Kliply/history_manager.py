"""
History Manager for Kliply clipboard manager.

This module manages the in-memory clipboard history with thread-safe operations.
"""

from collections import deque
from threading import Lock
from typing import List, Optional

from src.Kliply.models import ClipboardContent


class HistoryManager:
    """
    Manages the in-memory clipboard history with configurable depth.
    
    This class provides thread-safe operations for adding, retrieving, and
    managing clipboard history items. It uses a deque for efficient operations
    and maintains a maximum depth limit.
    
    Attributes:
        _max_depth: Maximum number of items to store in history
        _history: Deque storing clipboard content items
        _lock: Threading lock for thread-safe operations
    """
    
    def __init__(self, max_depth: int = 10):
        """
        Initialize the HistoryManager.
        
        Args:
            max_depth: Maximum number of clipboard items to retain (default: 10)
        """
        self._max_depth = max_depth
        self._history: deque[ClipboardContent] = deque(maxlen=max_depth)
        self._lock = Lock()
    
    def add_item(self, content: ClipboardContent) -> None:
        """
        Add a new item to the clipboard history.
        
        If the item already exists (based on content hash), it is moved to the
        front. Otherwise, it is added to the front. If the history exceeds
        max_depth, the oldest item is automatically removed.
        
        Args:
            content: The ClipboardContent to add to history
        """
        with self._lock:
            content_hash = content.get_hash()
            
            # Check if content already exists in history
            existing_index = None
            for i, item in enumerate(self._history):
                if item.get_hash() == content_hash:
                    existing_index = i
                    break
            
            # If duplicate found, remove it (we'll add it to front)
            if existing_index is not None:
                # Convert deque to list, remove item, convert back
                temp_list = list(self._history)
                temp_list.pop(existing_index)
                self._history = deque(temp_list, maxlen=self._max_depth)
            
            # Add new item to the front
            self._history.appendleft(content)
    
    def get_history(self) -> List[ClipboardContent]:
        """
        Get the current clipboard history.
        
        Returns:
            A list of ClipboardContent items in reverse chronological order
            (most recent first)
        """
        with self._lock:
            return list(self._history)
    
    def set_max_depth(self, depth: int) -> None:
        """
        Set the maximum depth of the clipboard history.
        
        If the new depth is less than the current history size, the oldest
        entries are removed immediately to match the new limit.
        
        Args:
            depth: The new maximum depth
        """
        with self._lock:
            self._max_depth = depth
            
            # If current history exceeds new depth, trim it
            if len(self._history) > depth:
                # Keep only the most recent 'depth' items
                temp_list = list(self._history)[:depth]
                self._history = deque(temp_list, maxlen=depth)
            else:
                # Just update the maxlen
                self._history = deque(self._history, maxlen=depth)
    
    def clear_history(self) -> None:
        """
        Clear all items from the clipboard history.
        """
        with self._lock:
            self._history.clear()
    
    def get_item(self, index: int) -> Optional[ClipboardContent]:
        """
        Get a specific item from the history by index.
        
        Args:
            index: The index of the item (0 is most recent)
        
        Returns:
            The ClipboardContent at the specified index, or None if index is invalid
        """
        with self._lock:
            if 0 <= index < len(self._history):
                return self._history[index]
            return None
