"""
UI Manager for Kliply clipboard manager.

This module handles the history popup window and other UI components.
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QListWidget, QListWidgetItem, QVBoxLayout, QLabel, QApplication,
    QDialog, QSlider, QCheckBox, QHBoxLayout, QGroupBox, QPushButton, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QImage, QPalette, QColor, QIcon
from typing import Optional
from pynput.keyboard import Controller, Key
import subprocess

try:
    from AppKit import NSWorkspace, NSRunningApplication
except ImportError:
    NSWorkspace = None
    NSRunningApplication = None

from src.Kliply.history_manager import HistoryManager
from src.Kliply.settings_manager import SettingsManager
from src.Kliply.models import ClipboardContent, ContentType


class HistoryPopup(QWidget):
    """
    Frameless popup window that displays clipboard history.
    
    This widget provides a modern, macOS-style popup interface for viewing
    and selecting clipboard history items.
    """
    
    def __init__(self, history_manager: HistoryManager):
        """
        Initialize the History Popup.
        
        Args:
            history_manager: The HistoryManager instance to retrieve history from
        """
        super().__init__()
        self.history_manager = history_manager
        self.list_widget: Optional[QListWidget] = None
        self._is_closing = False  # Flag to prevent duplicate close operations
        self._on_close_callback = None  # Callback to call when popup closes
        self._logger = logging.getLogger(__name__)
        self._keyboard = Controller()  # For simulating paste
        self._previous_app = None  # Store previously active application
        self._should_paste = False  # Safety flag for paste simulation
        
        try:
            self._setup_window()
            self._setup_ui()
            self._setup_event_handlers()
            self._logger.debug("HistoryPopup initialized successfully")
        except Exception as e:
            self._logger.error(f"Failed to initialize HistoryPopup: {e}", exc_info=True)
            raise
    
    def _setup_window(self):
        """Configure window properties."""
        # Frameless window with rounded corners
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Set window size
        self.setFixedSize(500, 400)
        
        # Set background color with transparency
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set window opacity
        self.setWindowOpacity(0.95)
    
    def _setup_ui(self):
        """Set up the UI components."""
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Title label
        title_label = QLabel("📋 Clipboard History")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
            }
        """)
        layout.addWidget(title_label)
        
        # List widget for history items
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #1E1E1E;
                color: #EEEEEE;
                border: 1px solid #444444;
                border-radius: 8px;
                padding: 5px;
                font-family: 'Menlo', 'Monaco', monospace;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: #007AFF;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #2A2A2A;
            }
        """)
        
        # Set icon size for thumbnails
        self.list_widget.setIconSize(QSize(40, 40))
        
        layout.addWidget(self.list_widget)
        
        # Set main widget background
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                border-radius: 10px;
            }
        """)
        
        self.setLayout(layout)
    
    def _setup_event_handlers(self):
        """Set up event handlers for user interactions."""
        # Single-click handler - copy item to clipboard
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        
        # Double-click handler - copy and close
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
    
    def _on_item_clicked(self, item: QListWidgetItem):
        """
        Handle single-click on an item - copy to clipboard.
        
        Args:
            item: The clicked list item
        """
        self._copy_selected_item_to_clipboard()
    
    def _on_item_double_clicked(self, item: QListWidgetItem):
        """
        Handle double-click on an item - copy to clipboard, paste, and close.
        
        Args:
            item: The double-clicked list item
        """
        self._copy_and_paste_selected_item()
    
    def _copy_selected_item_to_clipboard(self):
        """Copy the currently selected item to the system clipboard."""
        current_row = self.list_widget.currentRow()
        if current_row < 0:
            return
        
        # Get the corresponding history item
        history = self.history_manager.get_history()
        if current_row >= len(history):
            return
        
        content = history[current_row]
        
        # Copy to system clipboard
        clipboard = QApplication.clipboard()
        mime_data = content.to_clipboard_format()
        clipboard.setMimeData(mime_data)
    
    def _copy_and_paste_selected_item(self):
        """Copy the selected item to clipboard and simulate Cmd+V to paste it."""
        self._logger.info("=== _copy_and_paste_selected_item called ===")
        
        # First copy to clipboard
        self._copy_selected_item_to_clipboard()
        
        # Log previous app
        if self._previous_app:
            try:
                self._logger.info(f"Will paste into: {self._previous_app.localizedName()}")
            except Exception as e:
                self._logger.error(f"Error getting app name: {e}")
        
        # Store that we want to paste
        self._should_paste = True
        self._logger.info(f"Set _should_paste to True")
        
        # Close the popup first
        self.close_popup()
        self._logger.info("Popup closed, scheduling paste in 400ms")
        
        # Just use AppleScript for paste
        QTimer.singleShot(400, self._do_paste_with_applescript)
    
    def _do_paste_with_applescript(self):
        """Use AppleScript to activate app and paste."""
        self._logger.info("=== _do_paste_with_applescript called ===")
        
        if not getattr(self, '_should_paste', False):
            self._logger.warning("_should_paste is False, aborting")
            return
        
        if self.isVisible():
            self._logger.warning("Window still visible, waiting...")
            QTimer.singleShot(100, self._do_paste_with_applescript)
            return
        
        self._logger.info("Window is hidden, attempting paste")
        
        # Get app name
        app_name = None
        if self._previous_app:
            try:
                app_name = self._previous_app.localizedName()
                self._logger.info(f"Target app: {app_name}")
            except Exception as e:
                self._logger.error(f"Failed to get app name: {e}")
        
        if not app_name:
            self._logger.error("No app to paste into, aborting")
            self._should_paste = False
            return
        
        try:
            # Escape quotes in app name
            safe_app_name = app_name.replace('"', '\\"').replace('\\', '\\\\')
            
            # Simple AppleScript: activate then keystroke
            applescript = f'''tell application "{safe_app_name}"
    activate
end tell
delay 0.3
tell application "System Events"
    keystroke "v" using command down
end tell'''
            
            self._logger.info(f"Executing AppleScript for {app_name}")
            self._logger.debug(f"AppleScript: {applescript}")
            
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode == 0:
                self._logger.info("*** PASTE SUCCESSFUL ***")
            else:
                self._logger.error(f"AppleScript error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self._logger.error("AppleScript timed out")
        except Exception as e:
            self._logger.error(f"Paste failed: {e}", exc_info=True)
        finally:
            self._should_paste = False
    
    def _activate_and_paste(self):
        """Activate the previous app and then paste using AppleScript."""
        if not getattr(self, '_should_paste', False):
            self._logger.info("Skipping paste - _should_paste is False")
            return
        
        # Make absolutely sure our window is hidden
        if self.isVisible():
            self._logger.warning("Window still visible during paste, hiding now")
            self.hide()
            # Wait a bit more
            QTimer.singleShot(100, self._activate_and_paste)
            return
        
        # Get the previous app name
        app_name = None
        if self._previous_app_for_paste:
            try:
                app_name = self._previous_app_for_paste.localizedName()
                self._logger.info(f"Previous app captured: {app_name}")
            except Exception as e:
                self._logger.error(f"Error getting app name: {e}", exc_info=True)
        
        if not app_name:
            self._logger.warning("No previous app name available, will paste to frontmost app")
        
        # Use AppleScript to activate the app and paste
        try:
            if app_name:
                # Activate specific app then paste with longer delay
                applescript = f'''
                tell application "{app_name}"
                    activate
                end tell
                delay 0.3
                tell application "System Events"
                    key code 9 using command down
                end tell
                '''
            else:
                # Just paste to whatever app gets focus
                applescript = '''
                delay 0.2
                tell application "System Events"
                    key code 9 using command down
                end tell
                '''
            
            self._logger.info(f"Running AppleScript to paste (app: {app_name or 'frontmost'})")
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode == 0:
                self._logger.info("AppleScript paste successful")
                self._should_paste = False
            else:
                self._logger.error(f"AppleScript failed: {result.stderr}")
                # Fallback to pynput
                self._logger.info("Falling back to pynput for paste")
                QTimer.singleShot(100, self._simulate_paste)
                
        except Exception as e:
            self._logger.error(f"Failed to execute AppleScript: {e}", exc_info=True)
            # Fallback to pynput
            self._logger.info("Exception occurred, falling back to pynput")
            QTimer.singleShot(100, self._simulate_paste)
    
    def _simulate_paste(self):
        """Simulate Cmd+V keystroke to paste into the active application."""
        # Safety check - only paste if we're supposed to
        if not getattr(self, '_should_paste', False):
            self._logger.info("Skipping paste - _should_paste is False")
            return
        
        self._logger.info(f"Attempting paste - window visible: {self.isVisible()}")
        
        try:
            self._logger.info("Simulating paste (Cmd+V)")
            # Simulate Cmd+V
            with self._keyboard.pressed(Key.cmd):
                self._keyboard.press('v')
                self._keyboard.release('v')
            self._logger.info("Paste simulation complete")
        except Exception as e:
            self._logger.error(f"Failed to simulate paste: {e}", exc_info=True)
        finally:
            # Reset the paste flag
            self._should_paste = False
    
    def keyPressEvent(self, event):
        """
        Handle keyboard events.
        
        Args:
            event: The key press event
        """
        key = event.key()
        
        # Enter key - copy selected item, paste, and close
        if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            self._copy_and_paste_selected_item()
            event.accept()
        
        # Escape key - close popup without pasting
        elif key == Qt.Key.Key_Escape:
            self.close_popup()
            event.accept()
        
        # Arrow keys - navigate through list
        elif key == Qt.Key.Key_Up:
            current_row = self.list_widget.currentRow()
            if current_row > 0:
                self.list_widget.setCurrentRow(current_row - 1)
            event.accept()
        
        elif key == Qt.Key.Key_Down:
            current_row = self.list_widget.currentRow()
            if current_row < self.list_widget.count() - 1:
                self.list_widget.setCurrentRow(current_row + 1)
            event.accept()
        
        else:
            # Pass other keys to parent
            super().keyPressEvent(event)
    
    def show(self):
        """Override show to install event filter and capture previous app."""
        # Capture the currently active application (before we take focus)
        if NSWorkspace:
            try:
                workspace = NSWorkspace.sharedWorkspace()
                self._previous_app = workspace.frontmostApplication()
                if self._previous_app:
                    self._logger.info(f"Captured previous app: {self._previous_app.localizedName()}")
                else:
                    self._logger.warning("Could not capture previous app")
            except Exception as e:
                self._logger.error(f"Failed to capture previous app: {e}", exc_info=True)
        
        self._logger.info("Showing popup and installing event filter")
        super().show()
        # Install event filter only on this widget (not entire application)
        self.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """
        Filter events to detect when popup loses focus.
        Only processes WindowDeactivate events for this specific window.
        
        Args:
            obj: The object receiving the event
            event: The event
            
        Returns:
            False to allow event to continue processing
        """
        try:
            # ONLY check if this is OUR window and it's WindowDeactivate
            # This avoids processing thousands of unrelated events
            if obj == self and event.type() == event.Type.WindowDeactivate:
                self._logger.info("Window deactivated, closing popup")
                # Use QTimer.singleShot to defer closing
                QTimer.singleShot(0, self.close_popup)
        except Exception as e:
            self._logger.error(f"Error in eventFilter: {e}", exc_info=True)
        return False  # Always let events pass through
    
    def focusOutEvent(self, event):
        """
        Handle focus loss event - close popup.
        
        Args:
            event: The focus out event
        """
        self._logger.info("focusOutEvent triggered - closing popup")
        # Close popup when it loses focus
        self.close_popup()
        super().focusOutEvent(event)
    
    def closeEvent(self, event):
        """
        Handle close event.
        
        Args:
            event: The close event
        """
        self._logger.info("closeEvent triggered")
        # Call the close callback
        self._call_close_callback()
        super().closeEvent(event)
    
    def hideEvent(self, event):
        """
        Handle hide event - ensure callback is called even when just hiding.
        
        Args:
            event: The hide event
        """
        self._logger.info("hideEvent triggered")
        # Call the close callback when hiding
        self._call_close_callback()
        super().hideEvent(event)
    
    def close_popup(self):
        """Close the popup window."""
        if not self._is_closing:
            self._is_closing = True
            self._logger.info("close_popup: Removing event filter and hiding window")
            # Remove event filter
            try:
                self.removeEventFilter(self)
            except Exception as e:
                self._logger.warning(f"Error removing event filter: {e}")
            self.hide()
            self._logger.info("close_popup: Window hidden, calling callback")
            # Explicitly call the callback since hideEvent may not fire
            self._call_close_callback()
            self._is_closing = False
    
    def _call_close_callback(self):
        """Call the close callback if set."""
        self._logger.info("_call_close_callback called")
        # Emit a signal or call a callback when popup closes
        # This will be used to reset the hotkey handler state
        if hasattr(self, '_on_close_callback') and self._on_close_callback:
            self._logger.info("Calling close callback")
            try:
                self._on_close_callback()
                self._logger.info("Close callback executed successfully")
            except Exception as e:
                self._logger.error(f"Error in close callback: {e}", exc_info=True)
        else:
            self._logger.warning(f"No close callback set (hasattr={hasattr(self, '_on_close_callback')}, callback={getattr(self, '_on_close_callback', None)})")
    
    def _populate_history(self):
        """Populate the list widget with history items."""
        try:
            self.list_widget.clear()
            
            # Get history in reverse chronological order (most recent first)
            history = self.history_manager.get_history()
            
            for content in history:
                try:
                    item = QListWidgetItem()
                    
                    # Set item text based on content type
                    if content.content_type == ContentType.TEXT:
                        # Use preview which is already truncated
                        item.setText(content.preview if content.preview else self._truncate_text(content.data, 50))
                    
                    elif content.content_type == ContentType.RICH_TEXT:
                        # Use preview which extracts plain text from HTML
                        item.setText(content.preview if content.preview else "[Rich Text]")
                    
                    elif content.content_type == ContentType.IMAGE:
                        # Show thumbnail for images
                        item.setText("[Image]")
                        thumbnail = self._create_thumbnail(content.data)
                        if thumbnail:
                            item.setIcon(QIcon(thumbnail))
                    
                    elif content.content_type == ContentType.UNSUPPORTED:
                        # Show type indicator for unsupported content
                        item.setText("[Unsupported Content]")
                    
                    self.list_widget.addItem(item)
                
                except Exception as e:
                    self._logger.error(f"Error rendering history item: {e}", exc_info=True)
                    # Continue with next item
                    continue
            
            # Pre-select the most recent item (first item)
            if self.list_widget.count() > 0:
                self.list_widget.setCurrentRow(0)
        
        except Exception as e:
            self._logger.error(f"Error populating history: {e}", exc_info=True)
            # Show error message in popup
            error_item = QListWidgetItem("Error loading history")
            self.list_widget.addItem(error_item)
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """
        Truncate text to maximum length with ellipsis.
        
        Args:
            text: The text to truncate
            max_length: Maximum length before truncation
        
        Returns:
            Truncated text with "..." if longer than max_length
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Replace newlines with spaces for display
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text
    
    def _create_thumbnail(self, image_data: bytes) -> Optional[QPixmap]:
        """
        Create a thumbnail from image data.
        
        Args:
            image_data: Raw image bytes
        
        Returns:
            QPixmap thumbnail scaled to 40x40, or None if conversion fails
        """
        try:
            # Convert bytes to QImage
            image = QImage()
            if isinstance(image_data, bytes):
                image.loadFromData(image_data)
            
            if image.isNull():
                self._logger.warning("Failed to load image data for thumbnail")
                return None
            
            # Create pixmap and scale to thumbnail size
            pixmap = QPixmap.fromImage(image)
            thumbnail = pixmap.scaled(
                40, 40,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            return thumbnail
        except Exception as e:
            self._logger.error(f"Error creating thumbnail: {e}", exc_info=True)
            return None
    
    def set_on_close_callback(self, callback):
        """
        Set a callback to be called when the popup closes.
        
        Args:
            callback: Function to call when popup closes
        """
        self._logger.info(f"HistoryPopup.set_on_close_callback called with: {callback}")
        self._on_close_callback = callback
        self._logger.info(f"HistoryPopup._on_close_callback is now: {self._on_close_callback}")
    
    def show_popup(self):
        """Show the popup window with animation."""
        try:
            self._logger.info("show_popup: Starting")
            
            # Populate history before showing
            self._logger.info("show_popup: Populating history")
            self._populate_history()
            
            # Center window on screen
            self._logger.info("show_popup: Centering on screen")
            self._center_on_screen()
            
            # Show the window
            self._logger.info("show_popup: Calling self.show()")
            self.show()
            self._logger.info(f"show_popup: Window visible={self.isVisible()}")
            
            # Raise the window to front
            self._logger.info("show_popup: Raising window")
            self.raise_()
            
            # Set focus to the list widget
            self._logger.info("show_popup: Setting focus")
            self.list_widget.setFocus()
            
            # Activate window to ensure it's on top
            self._logger.info("show_popup: Activating window")
            self.activateWindow()
            
            # Fade-in animation
            self._logger.info("show_popup: Starting fade-in animation")
            self._fade_in()
            
            self._logger.info("History popup displayed successfully")
        
        except Exception as e:
            self._logger.error(f"Error showing history popup: {e}", exc_info=True)
            # Try to show anyway, even if there were errors
            try:
                self.show()
            except Exception:
                pass
    
    def _center_on_screen(self):
        """Center the window on the screen."""
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)
    
    def _fade_in(self):
        """Animate fade-in effect."""
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(200)  # 200ms animation
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(0.95)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.start()


class SettingsPanel(QDialog):
    """
    Settings panel window for configuring Kliply preferences.
    
    This dialog provides controls for clipboard depth, hotkey configuration,
    launch at login, and displays app information.
    """
    
    def __init__(self, settings_manager: SettingsManager, history_manager: HistoryManager):
        """
        Initialize the Settings Panel.
        
        Args:
            settings_manager: The SettingsManager instance for reading/writing settings
            history_manager: The HistoryManager instance for applying depth changes
        """
        super().__init__()
        self.settings_manager = settings_manager
        self.history_manager = history_manager
        
        self._setup_window()
        self._setup_ui()
    
    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle("Kliply Settings")
        self.setFixedSize(500, 450)
        
        # Native macOS window style
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)
    
    def _setup_ui(self):
        """Set up the UI components."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("⚙️ Settings")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333333;
                padding-bottom: 10px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # Clipboard Depth Section
        depth_group = self._create_depth_section()
        main_layout.addWidget(depth_group)
        
        # Hotkey Section
        hotkey_group = self._create_hotkey_section()
        main_layout.addWidget(hotkey_group)
        
        # Launch at Login Section
        launch_group = self._create_launch_section()
        main_layout.addWidget(launch_group)
        
        # About Section
        about_group = self._create_about_section()
        main_layout.addWidget(about_group)
        
        # Add stretch to push everything to the top
        main_layout.addStretch()
        
        # Close button
        close_button = QPushButton("Close")
        close_button.setFixedWidth(100)
        close_button.clicked.connect(self.accept)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0051D5;
            }
        """)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # Apply overall styling
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
            }
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #333333;
            }
            QLabel {
                color: #666666;
            }
        """)
    
    def _create_depth_section(self) -> QGroupBox:
        """Create the clipboard depth control section."""
        group = QGroupBox("Clipboard History Depth")
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Description
        desc_label = QLabel("Maximum number of clipboard items to remember:")
        desc_label.setStyleSheet("font-weight: normal; font-size: 12px;")
        layout.addWidget(desc_label)
        
        # Slider and value label container
        slider_layout = QHBoxLayout()
        
        # Slider
        self.depth_slider = QSlider(Qt.Orientation.Horizontal)
        self.depth_slider.setMinimum(5)
        self.depth_slider.setMaximum(100)
        self.depth_slider.setValue(self.settings_manager.get_clipboard_depth())
        self.depth_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.depth_slider.setTickInterval(10)
        self.depth_slider.valueChanged.connect(self._on_depth_changed)
        
        # Value label
        self.depth_value_label = QLabel(str(self.settings_manager.get_clipboard_depth()))
        self.depth_value_label.setStyleSheet("""
            font-weight: bold;
            font-size: 16px;
            color: #007AFF;
            min-width: 40px;
        """)
        self.depth_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        slider_layout.addWidget(self.depth_slider)
        slider_layout.addWidget(self.depth_value_label)
        
        layout.addLayout(slider_layout)
        
        # Range label
        range_label = QLabel("Range: 5 - 100 items")
        range_label.setStyleSheet("font-weight: normal; font-size: 11px; color: #999999;")
        layout.addWidget(range_label)
        
        group.setLayout(layout)
        return group
    
    def _create_hotkey_section(self) -> QGroupBox:
        """Create the hotkey configuration section."""
        group = QGroupBox("Keyboard Shortcut")
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Description
        desc_label = QLabel("Press this shortcut to open clipboard history:")
        desc_label.setStyleSheet("font-weight: normal; font-size: 12px;")
        layout.addWidget(desc_label)
        
        # Hotkey display (read-only for now)
        hotkey_layout = QHBoxLayout()
        
        self.hotkey_display = QLineEdit()
        self.hotkey_display.setText(self.settings_manager.get_hotkey())
        self.hotkey_display.setReadOnly(True)
        self.hotkey_display.setStyleSheet("""
            QLineEdit {
                background-color: #F0F0F0;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
                color: #333333;
            }
        """)
        
        hotkey_layout.addWidget(self.hotkey_display)
        layout.addLayout(hotkey_layout)
        
        # Note about changing hotkey
        note_label = QLabel("Note: Hotkey customization will be available in a future update")
        note_label.setStyleSheet("font-weight: normal; font-size: 11px; color: #999999; font-style: italic;")
        layout.addWidget(note_label)
        
        group.setLayout(layout)
        return group
    
    def _create_launch_section(self) -> QGroupBox:
        """Create the launch at login section."""
        group = QGroupBox("Startup")
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Launch at login checkbox
        self.launch_checkbox = QCheckBox("Launch Kliply at system login")
        self.launch_checkbox.setChecked(self.settings_manager.get_launch_at_login())
        self.launch_checkbox.stateChanged.connect(self._on_launch_changed)
        self.launch_checkbox.setStyleSheet("""
            QCheckBox {
                font-weight: normal;
                font-size: 13px;
                color: #333333;
            }
        """)
        
        layout.addWidget(self.launch_checkbox)
        
        group.setLayout(layout)
        return group
    
    def _create_about_section(self) -> QGroupBox:
        """Create the about section with app information."""
        group = QGroupBox("About")
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        # App name and version
        app_label = QLabel("Kliply")
        app_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #333333;")
        layout.addWidget(app_label)
        
        version_label = QLabel("Version 1.0.0")
        version_label.setStyleSheet("font-weight: normal; font-size: 12px; color: #666666;")
        layout.addWidget(version_label)
        
        # Description
        desc_label = QLabel("A professional macOS clipboard manager")
        desc_label.setStyleSheet("font-weight: normal; font-size: 12px; color: #666666;")
        layout.addWidget(desc_label)
        
        group.setLayout(layout)
        return group
    
    def _on_depth_changed(self, value: int):
        """
        Handle clipboard depth slider changes.
        
        Args:
            value: The new depth value from the slider
        """
        # Update the value label
        self.depth_value_label.setText(str(value))
        
        # Update settings
        if self.settings_manager.set_clipboard_depth(value):
            # Apply to history manager immediately
            self.history_manager.set_max_depth(value)
    
    def _on_launch_changed(self, state: int):
        """
        Handle launch at login checkbox changes.
        
        Args:
            state: The checkbox state (Qt.CheckState)
        """
        enabled = state == Qt.CheckState.Checked.value
        self.settings_manager.set_launch_at_login(enabled)


class PermissionDialog(QDialog):
    """
    Permission explanation dialog for macOS permissions.
    
    This dialog provides user-friendly explanations for why permissions
    are needed and guides users through the process of granting them.
    """
    
    def __init__(self, permission_type: str = "accessibility"):
        """
        Initialize the Permission Dialog.
        
        Args:
            permission_type: The type of permission being requested (default: "accessibility")
        """
        super().__init__()
        self.permission_type = permission_type
        self.user_choice = None  # Will be "open_preferences" or "later"
        
        self._setup_window()
        self._setup_ui()
    
    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle("Permission Required")
        self.setFixedSize(550, 500)
        
        # Native macOS window style
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
    
    def _setup_ui(self):
        """Set up the UI components."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Icon and title
        title_layout = QHBoxLayout()
        
        icon_label = QLabel("🔐")
        icon_label.setStyleSheet("font-size: 48px;")
        title_layout.addWidget(icon_label)
        
        title_label = QLabel("Kliply Needs Your Permission")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #333333;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        main_layout.addLayout(title_layout)
        
        # Explanation text
        if self.permission_type == "accessibility":
            explanation = (
                "Kliply needs <b>Accessibility</b> permission to register the global "
                "keyboard shortcut (Cmd+Shift+V) that lets you quickly access your "
                "clipboard history from any application.\n\n"
                "Without this permission, you'll only be able to access Kliply through "
                "the menu bar icon."
            )
        else:
            explanation = "Kliply needs additional permissions to function properly."
        
        explanation_label = QLabel(explanation)
        explanation_label.setWordWrap(True)
        explanation_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #555555;
                line-height: 1.5;
            }
        """)
        main_layout.addWidget(explanation_label)
        
        # Instructions section
        instructions_label = QLabel("<b>How to grant permission:</b>")
        instructions_label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: #333333;
                margin-top: 10px;
            }
        """)
        main_layout.addWidget(instructions_label)
        
        # Step-by-step instructions
        steps = [
            "1. Click the button below to open System Settings",
            "2. Find <b>Kliply</b> in the list of applications",
            "3. Toggle the switch next to Kliply to <b>ON</b>",
            "4. Return to Kliply - it will detect the change automatically"
        ]
        
        for step in steps:
            step_label = QLabel(step)
            step_label.setWordWrap(True)
            step_label.setStyleSheet("""
                QLabel {
                    font-size: 13px;
                    color: #555555;
                    padding: 5px 0px 5px 20px;
                }
            """)
            main_layout.addWidget(step_label)
        
        # Visual hint section
        hint_label = QLabel(
            "<i>💡 Tip: Look for 'Privacy & Security' → 'Accessibility' in System Settings</i>"
        )
        hint_label.setWordWrap(True)
        hint_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #888888;
                padding: 10px;
                background-color: #F8F8F8;
                border-radius: 5px;
                margin-top: 10px;
            }
        """)
        main_layout.addWidget(hint_label)
        
        # Add stretch to push buttons to bottom
        main_layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # "I'll Do This Later" button
        later_button = QPushButton("I'll Do This Later")
        later_button.setFixedHeight(40)
        later_button.clicked.connect(self._on_later_clicked)
        later_button.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #333333;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
        """)
        
        # "Open System Settings" button
        open_button = QPushButton("Open System Settings")
        open_button.setFixedHeight(40)
        open_button.clicked.connect(self._on_open_clicked)
        open_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0051D5;
            }
        """)
        
        button_layout.addWidget(later_button)
        button_layout.addWidget(open_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # Apply overall styling
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
        """)
    
    def _on_open_clicked(self):
        """Handle 'Open System Settings' button click."""
        self.user_choice = "open_preferences"
        self.accept()
    
    def _on_later_clicked(self):
        """Handle 'I'll Do This Later' button click."""
        self.user_choice = "later"
        self.reject()
    
    def get_user_choice(self) -> str:
        """
        Get the user's choice from the dialog.
        
        Returns:
            "open_preferences" if user chose to open settings,
            "later" if user chose to do it later,
            None if dialog was closed without a choice.
        """
        return self.user_choice


class WelcomeScreen(QDialog):
    """
    Welcome screen dialog for first-time users.
    
    This dialog provides a friendly introduction to Kliply and explains
    the keyboard shortcut for accessing clipboard history.
    """
    
    def __init__(self, onboarding_manager=None):
        """
        Initialize the Welcome Screen.
        
        Args:
            onboarding_manager: Optional OnboardingManager instance for callbacks
        """
        super().__init__()
        self.onboarding_manager = onboarding_manager
        self.dont_show_again = False
        
        self._setup_window()
        self._setup_ui()
    
    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle("Welcome to Kliply")
        self.setFixedSize(600, 650)
        
        # Native macOS window style
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
    
    def _setup_ui(self):
        """Set up the UI components."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(40, 50, 40, 40)
        
        # Kliply branding with emoji
        branding_layout = QVBoxLayout()
        branding_layout.setSpacing(15)
        
        icon_label = QLabel("📋")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 64px;")
        branding_layout.addWidget(icon_label)
        
        title_label = QLabel("Welcome to Kliply!")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;
                color: #333333;
                padding: 10px 0px;
                line-height: 1.3;
            }
        """)
        branding_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Your clipboard history, always at your fingertips")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #666666;
            }
        """)
        branding_layout.addWidget(subtitle_label)
        
        main_layout.addLayout(branding_layout)
        
        # Keyboard shortcut visual
        shortcut_container = QWidget()
        shortcut_container.setStyleSheet("""
            QWidget {
                background-color: #F8F8F8;
                border-radius: 10px;
            }
        """)
        shortcut_layout = QVBoxLayout()
        shortcut_layout.setSpacing(20)
        shortcut_layout.setContentsMargins(25, 25, 25, 25)
        
        shortcut_title = QLabel("Quick Access Shortcut")
        shortcut_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        shortcut_title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #555555;
                padding: 5px 0px;
            }
        """)
        shortcut_layout.addWidget(shortcut_title)
        
        # Large keyboard shortcut display
        shortcut_display = QLabel("⌘ Cmd + ⇧ Shift + V")
        shortcut_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        shortcut_display.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: #007AFF;
                padding: 20px 15px;
                background-color: white;
                border-radius: 8px;
                line-height: 1.3;
            }
        """)
        shortcut_layout.addWidget(shortcut_display)
        
        shortcut_container.setLayout(shortcut_layout)
        main_layout.addWidget(shortcut_container)
        
        # Explanation text
        explanation = QLabel(
            "Press <b>Cmd+Shift+V</b> anytime to see your clipboard history. "
            "Kliply runs quietly in the background, remembering everything you copy."
        )
        explanation.setWordWrap(True)
        explanation.setAlignment(Qt.AlignmentFlag.AlignCenter)
        explanation.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #555555;
                line-height: 1.6;
            }
        """)
        main_layout.addWidget(explanation)
        
        # Add stretch to push buttons to bottom
        main_layout.addStretch()
        
        # "Don't show this again" checkbox
        self.dont_show_checkbox = QCheckBox("Don't show this again")
        self.dont_show_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                color: #666666;
            }
        """)
        self.dont_show_checkbox.stateChanged.connect(self._on_checkbox_changed)
        
        checkbox_layout = QHBoxLayout()
        checkbox_layout.addStretch()
        checkbox_layout.addWidget(self.dont_show_checkbox)
        checkbox_layout.addStretch()
        main_layout.addLayout(checkbox_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # "Try It Now" button
        try_button = QPushButton("Try It Now")
        try_button.setFixedHeight(45)
        try_button.clicked.connect(self._on_try_clicked)
        try_button.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #333333;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
        """)
        
        # "Get Started" button
        start_button = QPushButton("Get Started")
        start_button.setFixedHeight(45)
        start_button.clicked.connect(self._on_start_clicked)
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0051D5;
            }
        """)
        
        button_layout.addWidget(try_button)
        button_layout.addWidget(start_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # Apply overall styling
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
        """)
    
    def _on_checkbox_changed(self, state: int):
        """
        Handle checkbox state changes.
        
        Args:
            state: The checkbox state
        """
        self.dont_show_again = state == Qt.CheckState.Checked.value
    
    def _on_try_clicked(self):
        """Handle 'Try It Now' button click."""
        # Demonstrate the popup
        if self.onboarding_manager is not None:
            self.onboarding_manager.demonstrate_popup()
    
    def _on_start_clicked(self):
        """Handle 'Get Started' button click."""
        # Mark welcome as complete if checkbox is checked
        if self.dont_show_again and self.onboarding_manager is not None:
            self.onboarding_manager.mark_welcome_complete()
        
        self.accept()
    
    def should_mark_complete(self) -> bool:
        """
        Check if the welcome should be marked as complete.
        
        Returns:
            True if the "Don't show this again" checkbox was checked
        """
        return self.dont_show_again


class HelpDialog(QDialog):
    """
    Help dialog showing documentation and keyboard shortcuts.
    
    This dialog provides users with quick reference documentation,
    keyboard shortcuts, and troubleshooting tips.
    """
    
    def __init__(self, settings_manager: Optional[SettingsManager] = None):
        """
        Initialize the Help Dialog.
        
        Args:
            settings_manager: Optional SettingsManager to get current hotkey
        """
        super().__init__()
        self.settings_manager = settings_manager
        
        self._setup_window()
        self._setup_ui()
    
    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle("Kliply Help")
        self.setFixedSize(650, 600)
        
        # Native macOS window style
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
    
    def _setup_ui(self):
        """Set up the UI components."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_layout = QHBoxLayout()
        
        icon_label = QLabel("📚")
        icon_label.setStyleSheet("font-size: 36px;")
        title_layout.addWidget(icon_label)
        
        title_label = QLabel("Kliply Help")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333333;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        main_layout.addLayout(title_layout)
        
        # Create tabbed sections
        from PyQt6.QtWidgets import QTabWidget, QTextBrowser
        
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #E0E0E0;
                color: #333333;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: white;
                font-weight: bold;
            }
        """)
        
        # Getting Started tab
        getting_started = self._create_getting_started_tab()
        tab_widget.addTab(getting_started, "Getting Started")
        
        # Keyboard Shortcuts tab
        shortcuts = self._create_shortcuts_tab()
        tab_widget.addTab(shortcuts, "Keyboard Shortcuts")
        
        # Troubleshooting tab
        troubleshooting = self._create_troubleshooting_tab()
        tab_widget.addTab(troubleshooting, "Troubleshooting")
        
        # About & Support tab
        about = self._create_about_tab()
        tab_widget.addTab(about, "About & Support")
        
        main_layout.addWidget(tab_widget)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.setFixedWidth(100)
        close_button.clicked.connect(self.accept)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0051D5;
            }
        """)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # Apply overall styling
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
            }
        """)
    
    def _create_getting_started_tab(self) -> QWidget:
        """Create the Getting Started tab content."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Get current hotkey
        hotkey = "Cmd+Shift+V"
        if self.settings_manager:
            hotkey = self.settings_manager.get_hotkey()
        
        content = f"""
        <h2 style="color: #333333;">Welcome to Kliply!</h2>
        
        <p style="font-size: 14px; color: #555555; line-height: 1.6;">
        Kliply is a professional clipboard manager that remembers everything you copy,
        making it easy to access your clipboard history anytime.
        </p>
        
        <h3 style="color: #007AFF; margin-top: 20px;">Quick Start</h3>
        
        <ol style="font-size: 13px; color: #555555; line-height: 1.8;">
            <li><b>Copy anything</b> - Text, images, or rich content</li>
            <li><b>Press {hotkey}</b> to open your clipboard history</li>
            <li><b>Select an item</b> using mouse or arrow keys</li>
            <li><b>Press Enter</b> or double-click to paste</li>
        </ol>
        
        <h3 style="color: #007AFF; margin-top: 20px;">Key Features</h3>
        
        <ul style="font-size: 13px; color: #555555; line-height: 1.8;">
            <li><b>Smart History</b> - Automatically tracks all clipboard items</li>
            <li><b>Duplicate Detection</b> - Copying the same item moves it to the top</li>
            <li><b>Multiple Content Types</b> - Supports text, images, and rich text</li>
            <li><b>Configurable Depth</b> - Store 5-100 items (default: 10)</li>
            <li><b>Always Available</b> - Runs quietly in the background</li>
        </ul>
        
        <h3 style="color: #007AFF; margin-top: 20px;">Menu Bar Access</h3>
        
        <p style="font-size: 13px; color: #555555; line-height: 1.6;">
        Click the Kliply icon in your menu bar to access:
        </p>
        
        <ul style="font-size: 13px; color: #555555; line-height: 1.8;">
            <li>Show History</li>
            <li>Settings</li>
            <li>Clear History</li>
            <li>Help (this window)</li>
        </ul>
        """
        
        from PyQt6.QtWidgets import QTextBrowser
        text_browser = QTextBrowser()
        text_browser.setHtml(content)
        text_browser.setOpenExternalLinks(True)
        text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: white;
                border: none;
                padding: 10px;
            }
        """)
        
        layout.addWidget(text_browser)
        widget.setLayout(layout)
        return widget
    
    def _create_shortcuts_tab(self) -> QWidget:
        """Create the Keyboard Shortcuts tab content."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Get current hotkey
        hotkey = "Cmd+Shift+V"
        if self.settings_manager:
            hotkey = self.settings_manager.get_hotkey()
        
        content = f"""
        <h2 style="color: #333333;">Keyboard Shortcuts</h2>
        
        <h3 style="color: #007AFF; margin-top: 20px;">Global Shortcuts</h3>
        
        <table style="width: 100%; font-size: 13px; color: #555555; line-height: 2.0;">
            <tr>
                <td style="padding: 8px; background-color: #F8F8F8;"><b>{hotkey}</b></td>
                <td style="padding: 8px;">Open clipboard history popup</td>
            </tr>
        </table>
        
        <h3 style="color: #007AFF; margin-top: 20px;">In History Popup</h3>
        
        <table style="width: 100%; font-size: 13px; color: #555555; line-height: 2.0;">
            <tr>
                <td style="padding: 8px; background-color: #F8F8F8; width: 200px;"><b>↑ / ↓ Arrow Keys</b></td>
                <td style="padding: 8px;">Navigate through history items</td>
            </tr>
            <tr>
                <td style="padding: 8px; background-color: #F8F8F8;"><b>Enter</b></td>
                <td style="padding: 8px;">Copy selected item and close popup</td>
            </tr>
            <tr>
                <td style="padding: 8px; background-color: #F8F8F8;"><b>Escape</b></td>
                <td style="padding: 8px;">Close popup without copying</td>
            </tr>
            <tr>
                <td style="padding: 8px; background-color: #F8F8F8;"><b>Single Click</b></td>
                <td style="padding: 8px;">Copy item to clipboard</td>
            </tr>
            <tr>
                <td style="padding: 8px; background-color: #F8F8F8;"><b>Double Click</b></td>
                <td style="padding: 8px;">Copy item and close popup</td>
            </tr>
        </table>
        
        <h3 style="color: #007AFF; margin-top: 20px;">Tips</h3>
        
        <ul style="font-size: 13px; color: #555555; line-height: 1.8;">
            <li>The most recent item is always pre-selected</li>
            <li>The popup automatically closes when it loses focus</li>
            <li>You can customize the hotkey in Settings</li>
        </ul>
        """
        
        from PyQt6.QtWidgets import QTextBrowser
        text_browser = QTextBrowser()
        text_browser.setHtml(content)
        text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: white;
                border: none;
                padding: 10px;
            }
        """)
        
        layout.addWidget(text_browser)
        widget.setLayout(layout)
        return widget
    
    def _create_troubleshooting_tab(self) -> QWidget:
        """Create the Troubleshooting tab content."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        content = """
        <h2 style="color: #333333;">Troubleshooting</h2>
        
        <h3 style="color: #007AFF; margin-top: 20px;">Hotkey Not Working</h3>
        
        <p style="font-size: 13px; color: #555555; line-height: 1.6;">
        If the global hotkey isn't responding:
        </p>
        
        <ol style="font-size: 13px; color: #555555; line-height: 1.8;">
            <li><b>Check Accessibility Permissions</b>
                <ul>
                    <li>Open System Settings → Privacy & Security → Accessibility</li>
                    <li>Ensure Kliply is in the list and enabled</li>
                    <li>If not listed, click the menu bar icon and select "Permissions Required"</li>
                </ul>
            </li>
            <li><b>Check for Conflicts</b>
                <ul>
                    <li>Another app might be using the same hotkey</li>
                    <li>Try changing the hotkey in Settings</li>
                </ul>
            </li>
            <li><b>Restart Kliply</b>
                <ul>
                    <li>Quit from the menu bar and relaunch</li>
                </ul>
            </li>
        </ol>
        
        <h3 style="color: #007AFF; margin-top: 20px;">Clipboard Not Being Tracked</h3>
        
        <p style="font-size: 13px; color: #555555; line-height: 1.6;">
        If items aren't appearing in your history:
        </p>
        
        <ul style="font-size: 13px; color: #555555; line-height: 1.8;">
            <li>Ensure Kliply is running (check menu bar icon)</li>
            <li>Try copying something new</li>
            <li>Check if history is full (increase depth in Settings)</li>
            <li>Some apps use private clipboard formats that can't be captured</li>
        </ul>
        
        <h3 style="color: #007AFF; margin-top: 20px;">Performance Issues</h3>
        
        <p style="font-size: 13px; color: #555555; line-height: 1.6;">
        If Kliply is running slowly:
        </p>
        
        <ul style="font-size: 13px; color: #555555; line-height: 1.8;">
            <li>Reduce clipboard depth in Settings (fewer items = faster)</li>
            <li>Clear history to free up memory</li>
            <li>Large images take more memory - consider clearing them</li>
        </ul>
        
        <h3 style="color: #007AFF; margin-top: 20px;">Still Having Issues?</h3>
        
        <p style="font-size: 13px; color: #555555; line-height: 1.6;">
        Check the About & Support tab for contact information and additional resources.
        </p>
        """
        
        from PyQt6.QtWidgets import QTextBrowser
        text_browser = QTextBrowser()
        text_browser.setHtml(content)
        text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: white;
                border: none;
                padding: 10px;
            }
        """)
        
        layout.addWidget(text_browser)
        widget.setLayout(layout)
        return widget
    
    def _create_about_tab(self) -> QWidget:
        """Create the About & Support tab content."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        content = """
        <h2 style="color: #333333;">About Kliply</h2>
        
        <p style="font-size: 14px; color: #555555; line-height: 1.6;">
        <b>Kliply</b> is a professional macOS clipboard manager that provides
        Windows 11-style clipboard history functionality with a native macOS experience.
        </p>
        
        <table style="width: 100%; font-size: 13px; color: #555555; line-height: 2.0; margin-top: 20px;">
            <tr>
                <td style="padding: 8px; background-color: #F8F8F8; width: 150px;"><b>Version</b></td>
                <td style="padding: 8px;">1.0.0</td>
            </tr>
            <tr>
                <td style="padding: 8px; background-color: #F8F8F8;"><b>Platform</b></td>
                <td style="padding: 8px;">macOS 10.15+</td>
            </tr>
            <tr>
                <td style="padding: 8px; background-color: #F8F8F8;"><b>License</b></td>
                <td style="padding: 8px;">Proprietary</td>
            </tr>
        </table>
        
        <h3 style="color: #007AFF; margin-top: 30px;">Support & Resources</h3>
        
        <p style="font-size: 13px; color: #555555; line-height: 1.8;">
        <b>Support Email:</b> <a href="mailto:support@muleinstudios.com" style="color: #007AFF;">support@muleinstudios.com</a><br>
        <b>Website:</b> <a href="https://digital-defiance.github.io/Kliply/" style="color: #007AFF;">digital-defiance.github.io/Kliply</a>
        </p>
        
        <h3 style="color: #007AFF; margin-top: 30px;">Privacy</h3>
        
        <p style="font-size: 13px; color: #555555; line-height: 1.6;">
        Kliply stores your clipboard history locally on your Mac. No data is sent
        to external servers. Your clipboard content remains private and secure.
        </p>
        
        <h3 style="color: #007AFF; margin-top: 30px;">Acknowledgments</h3>
        
        <p style="font-size: 13px; color: #555555; line-height: 1.6;">
        Built with PyQt6 and designed for macOS with love.
        </p>
        
        <p style="font-size: 12px; color: #999999; margin-top: 30px; text-align: center;">
        © 2026 Digital Defiance, Jessica Mulein. All rights reserved.
        </p>
        """
        
        from PyQt6.QtWidgets import QTextBrowser
        text_browser = QTextBrowser()
        text_browser.setHtml(content)
        text_browser.setOpenExternalLinks(True)
        text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: white;
                border: none;
                padding: 10px;
            }
        """)
        
        layout.addWidget(text_browser)
        widget.setLayout(layout)
        return widget


class RestartDialog(QDialog):
    """
    Dialog prompting user to restart Kliply after granting permissions.
    
    This dialog appears after the user grants Accessibility permission
    and explains that they need to restart Kliply for the hotkey to work.
    """
    
    def __init__(self):
        """Initialize the Restart Dialog."""
        super().__init__()
        self.user_choice = None  # Will be "restart" or "later"
        
        self._setup_window()
        self._setup_ui()
    
    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle("Restart Required")
        self.setFixedSize(600, 480)
        
        # Native macOS window style
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
    
    def _setup_ui(self):
        """Set up the UI components."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(45, 50, 45, 45)
        
        # Icon and title
        title_layout = QHBoxLayout()
        title_layout.setSpacing(15)
        
        icon_label = QLabel("✅")
        icon_label.setStyleSheet("font-size: 40px;")
        title_layout.addWidget(icon_label)
        
        title_label = QLabel("Permission Granted!")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #333333;
                padding: 5px 0px;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        main_layout.addLayout(title_layout)
        
        # Explanation text
        explanation = (
            "Great! Kliply now has Accessibility permission.\n\n"
            "To activate the global hotkey (Cmd+Shift+V), you need to "
            "<b>restart Kliply</b>.\n\n"
            "You can restart now or continue using Kliply through the menu bar "
            "and restart later."
        )
        
        explanation_label = QLabel(explanation)
        explanation_label.setWordWrap(True)
        explanation_label.setTextFormat(Qt.TextFormat.RichText)
        explanation_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #555555;
                line-height: 1.5;
                padding: 5px 0px;
            }
        """)
        main_layout.addWidget(explanation_label)
        
        # Visual hint
        hint_label = QLabel(
            "<i>💡 Tip: After restarting, press Cmd+Shift+V from any app to access your clipboard history</i>"
        )
        hint_label.setWordWrap(True)
        hint_label.setTextFormat(Qt.TextFormat.RichText)
        hint_label.setTextFormat(Qt.TextFormat.RichText)
        hint_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #888888;
                padding: 15px;
                background-color: #F8F8F8;
                border-radius: 5px;
                margin-top: 10px;
                line-height: 1.5;
            }
        """)
        main_layout.addWidget(hint_label)
        
        # Add stretch to push buttons to bottom
        main_layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # "Restart Later" button
        later_button = QPushButton("Restart Later")
        later_button.setFixedHeight(40)
        later_button.clicked.connect(self._on_later_clicked)
        later_button.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #333333;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
        """)
        
        # "Restart Now" button
        restart_button = QPushButton("Restart Now")
        restart_button.setFixedHeight(40)
        restart_button.clicked.connect(self._on_restart_clicked)
        restart_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0051D5;
            }
        """)
        
        button_layout.addWidget(later_button)
        button_layout.addWidget(restart_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # Apply overall styling
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
        """)
    
    def _on_restart_clicked(self):
        """Handle 'Restart Now' button click."""
        self.user_choice = "restart"
        self.accept()
    
    def _on_later_clicked(self):
        """Handle 'Restart Later' button click."""
        self.user_choice = "later"
        self.reject()
    
    def get_user_choice(self) -> str:
        """
        Get the user's choice from the dialog.
        
        Returns:
            "restart" if user chose to restart now,
            "later" if user chose to restart later,
            None if dialog was closed without a choice.
        """
        return self.user_choice


class UIManager:
    """
    Manages all UI components for Kliply.
    
    This class is responsible for creating and managing the history popup,
    settings panel, and other UI elements.
    """
    
    def __init__(self, history_manager: HistoryManager, settings_manager: Optional[SettingsManager] = None, clipboard_monitor = None):
        """
        Initialize the UIManager.
        
        Args:
            history_manager: The HistoryManager instance for accessing clipboard history
            settings_manager: Optional SettingsManager instance for settings panel
            clipboard_monitor: Optional ClipboardMonitor instance for forcing clipboard checks
        """
        self.history_manager = history_manager
        self.settings_manager = settings_manager
        self.clipboard_monitor = clipboard_monitor
        self.history_popup: Optional[HistoryPopup] = None
        self.settings_panel: Optional[SettingsPanel] = None
        self.permission_dialog: Optional[PermissionDialog] = None
        self.welcome_screen: Optional[WelcomeScreen] = None
        self.help_dialog: Optional[HelpDialog] = None
        self.restart_dialog: Optional[RestartDialog] = None
        self._onboarding_manager: Optional[object] = None  # Will be set later
        self._on_popup_close_callback = None  # Callback for when popup closes
        self._logger = logging.getLogger(__name__)
        
        self._logger.info("UIManager initialized successfully")
    
    def set_on_popup_close_callback(self, callback):
        """
        Set a callback to be called when the history popup closes.
        
        Args:
            callback: Function to call when popup closes
        """
        self._logger.info(f"Setting popup close callback: {callback}")
        self._on_popup_close_callback = callback
    
    def show_history_popup(self):
        """
        Display the history popup window.
        
        If the popup is already visible, this method does nothing.
        """
        try:
            self._logger.info("show_history_popup called")
            
            # Force an immediate clipboard check to catch very recent copies
            if self.clipboard_monitor:
                self.clipboard_monitor.force_check()
            
            # Create popup if it doesn't exist or was closed
            if self.history_popup is None or not self.history_popup.isVisible():
                self._logger.info("Creating new HistoryPopup instance")
                self.history_popup = HistoryPopup(self.history_manager)
                
                # Set the close callback if we have one
                if self._on_popup_close_callback:
                    self._logger.info(f"Setting close callback on popup instance: {self._on_popup_close_callback}")
                    self.history_popup.set_on_close_callback(self._on_popup_close_callback)
                else:
                    self._logger.warning("No close callback available to set on popup!")
                
                self._logger.info("Calling show_popup on HistoryPopup")
                self.history_popup.show_popup()
                self._logger.info("show_popup completed")
            else:
                self._logger.info("History popup already visible, skipping")
            
            self._logger.debug("History popup shown")
        
        except Exception as e:
            self._logger.error(f"Error showing history popup: {e}", exc_info=True)
            # UI rendering error - log and continue
    
    def hide_history_popup(self):
        """Hide the history popup window."""
        if self.history_popup and self.history_popup.isVisible():
            self.history_popup.hide()
    
    def show_settings_panel(self):
        """
        Display the settings panel window.
        
        If the settings panel is already visible, this method brings it to front.
        If no settings_manager was provided, this method does nothing.
        """
        try:
            if self.settings_manager is None:
                self._logger.warning("Cannot show settings panel: no settings_manager provided")
                return
            
            # Create settings panel if it doesn't exist or was closed
            if self.settings_panel is None or not self.settings_panel.isVisible():
                self.settings_panel = SettingsPanel(self.settings_manager, self.history_manager)
                self.settings_panel.exec()
            else:
                # Bring existing panel to front
                self.settings_panel.raise_()
                self.settings_panel.activateWindow()
            
            self._logger.debug("Settings panel shown")
        
        except Exception as e:
            self._logger.error(f"Error showing settings panel: {e}", exc_info=True)
    
    def show_permission_dialog(self, permission_type: str = "accessibility") -> str:
        """
        Display the permission explanation dialog.
        
        Args:
            permission_type: The type of permission being requested (default: "accessibility")
        
        Returns:
            User's choice: "open_preferences", "later", or None if closed
        """
        self.permission_dialog = PermissionDialog(permission_type)
        self.permission_dialog.exec()
        return self.permission_dialog.get_user_choice()
    
    def show_restart_dialog(self) -> str:
        """
        Display the restart dialog after permission is granted.
        
        Returns:
            User's choice: "restart", "later", or None if closed
        """
        import logging
        logger = logging.getLogger(__name__)
        
        self.restart_dialog = RestartDialog()
        self.restart_dialog.exec()
        choice = self.restart_dialog.get_user_choice()
        
        if choice == "restart":
            # User wants to restart - quit and relaunch the application
            import sys
            import subprocess
            import os
            from PyQt6.QtWidgets import QApplication
            
            # Get the path to the current executable
            app_path = sys.argv[0]
            logger.info(f"Restart requested. sys.argv[0] = {app_path}")
            logger.info(f"sys.executable = {sys.executable}")
            
            # Determine the bundle path
            bundle_path = None
            
            # Method 1: Check if running from .app bundle
            if '.app/Contents/MacOS' in app_path:
                # Extract the .app bundle path
                bundle_path = app_path.split('.app/Contents/MacOS')[0] + '.app'
                logger.info(f"Detected .app bundle from argv[0]: {bundle_path}")
            
            # Method 2: Check sys.executable
            elif '.app/Contents/MacOS' in sys.executable:
                bundle_path = sys.executable.split('.app/Contents/MacOS')[0] + '.app'
                logger.info(f"Detected .app bundle from sys.executable: {bundle_path}")
            
            # Method 3: Check if we're in /Applications
            elif app_path.startswith('/Applications/') and app_path.endswith('.app'):
                bundle_path = app_path
                logger.info(f"Detected .app bundle from /Applications: {bundle_path}")
            
            # Method 4: Look for Kliply.app in /Applications
            elif os.path.exists('/Applications/Kliply.app'):
                bundle_path = '/Applications/Kliply.app'
                logger.info(f"Found Kliply.app in /Applications: {bundle_path}")
            
            if bundle_path and os.path.exists(bundle_path):
                logger.info(f"Relaunching app bundle: {bundle_path}")
                # Schedule relaunch using 'open' command with a delay
                # The delay ensures the current instance has time to quit
                subprocess.Popen([
                    'sh', '-c',
                    f'sleep 1 && open "{bundle_path}"'
                ])
            else:
                logger.warning(f"Could not determine app bundle path. Restart will require manual relaunch.")
                logger.warning(f"app_path: {app_path}")
                logger.warning(f"sys.executable: {sys.executable}")
            
            # Quit the current instance
            logger.info("Quitting current instance...")
            QApplication.instance().quit()
        
        return choice
    
    def set_onboarding_manager(self, onboarding_manager):
        """
        Set the onboarding manager for welcome screen callbacks.
        
        Args:
            onboarding_manager: The OnboardingManager instance
        """
        self._onboarding_manager = onboarding_manager
    
    def show_welcome_screen(self) -> bool:
        """
        Display the welcome screen for first-time users.
        
        Returns:
            True if the user checked "Don't show this again", False otherwise
        """
        self.welcome_screen = WelcomeScreen(self._onboarding_manager)
        result = self.welcome_screen.exec()
        
        # Return whether the welcome should be marked as complete
        return self.welcome_screen.should_mark_complete()
    
    def show_help_dialog(self):
        """
        Display the help dialog with documentation and shortcuts.
        
        If the help dialog is already visible, this method brings it to front.
        """
        # Create help dialog if it doesn't exist or was closed
        if self.help_dialog is None or not self.help_dialog.isVisible():
            self.help_dialog = HelpDialog(self.settings_manager)
            self.help_dialog.exec()
        else:
            # Bring existing dialog to front
            self.help_dialog.raise_()
            self.help_dialog.activateWindow()
