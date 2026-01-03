# Implementation Plan: Kliply

## Overview

This implementation plan breaks down Kliply into discrete, incremental coding tasks. Each task builds on previous work to create a professional macOS clipboard manager with Windows 11-style functionality. The implementation uses Python with PyQt6 for native macOS integration and App Store compatibility.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create proper Python package structure with src/ directory
  - Set up requirements.txt with PyQt6, hypothesis, pytest dependencies
  - Configure pytest and hypothesis for testing
  - Create basic __init__.py files for package imports
  - _Requirements: 8.1, 8.2_

- [x] 2. Implement core data models
  - [x] 2.1 Create ContentType enum and ClipboardContent dataclass
    - Define ContentType enum (TEXT, IMAGE, RICH_TEXT, UNSUPPORTED)
    - Implement ClipboardContent dataclass with all fields
    - Add get_hash() method for content comparison
    - Add to_clipboard_format() method for QMimeData conversion
    - _Requirements: 7.1, 7.2, 7.3, 7.5_
  
  - [x] 2.2 Write property test for content type support
    - **Property 15: Content type support**
    - **Validates: Requirements 7.1, 7.2, 7.3**
  
  - [x] 2.3 Create Settings and PermissionStatus dataclasses
    - Define Settings dataclass with clipboard_depth, hotkey, launch_at_login, first_launch_complete
    - Define PermissionStatus dataclass with accessibility flag and last_checked timestamp
    - Implement validate() method for settings validation
    - Set default values (depth=10, hotkey="Cmd+Shift+V", first_launch_complete=False)
    - _Requirements: 2.2, 3.3, 11.7, 13.6_
  
  - [x] 2.4 Write property test for depth validation
    - **Property 5: Depth validation**
    - **Validates: Requirements 2.6**

- [x] 3. Implement HistoryManager
  - [x] 3.1 Create HistoryManager class with thread-safe operations
    - Implement __init__ with configurable max_depth
    - Use collections.deque for efficient history storage
    - Add threading.Lock for thread safety
    - Implement add_item() method
    - Implement get_history() method
    - Implement set_max_depth() method
    - Implement clear_history() method
    - Implement get_item() method
    - _Requirements: 1.2, 1.3, 1.4, 2.3, 2.4_
  
  - [x] 3.2 Write property test for new content addition
    - **Property 1: New content is added to history**
    - **Validates: Requirements 1.2**
  
  - [x] 3.3 Write property test for duplicate handling
    - **Property 2: Duplicate content moves to front**
    - **Validates: Requirements 1.3**
  
  - [x] 3.4 Write property test for depth limit
    - **Property 3: History respects depth limit**
    - **Validates: Requirements 1.4**
  
  - [x] 3.5 Write property test for depth changes
    - **Property 4: Depth changes are applied immediately**
    - **Validates: Requirements 2.3, 2.4**
  
  - [x] 3.6 Write unit tests for HistoryManager
    - Test initialization with empty history
    - Test edge cases (empty content, very long text)
    - _Requirements: 1.5_

- [x] 4. Checkpoint - Ensure core data layer tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement ClipboardMonitor
  - [x] 5.1 Create ClipboardMonitor class with QClipboard integration
    - Implement __init__ with HistoryManager dependency
    - Set up QClipboard instance
    - Implement start() method with QTimer for polling (500ms interval)
    - Implement stop() method to clean up timer
    - Implement _on_clipboard_change() to detect and process changes
    - Extract content type from QMimeData
    - Create ClipboardContent objects from clipboard data
    - _Requirements: 1.1, 1.2, 6.2_
  
  - [x] 5.2 Write property test for format preservation
    - **Property 18: Format preservation round-trip**
    - **Validates: Requirements 7.6**
  
  - [x] 5.3 Write property test for error recovery
    - **Property 19: Error recovery during monitoring**
    - **Validates: Requirements 9.5**
  
  - [x] 5.4 Write unit tests for ClipboardMonitor
    - Test monitoring starts immediately
    - Test content type detection
    - Test error handling during monitoring
    - _Requirements: 6.2_

- [x] 6. Implement SettingsManager
  - [x] 6.1 Create SettingsManager class for in-memory preferences
    - Implement __init__ with default Settings
    - Implement get_clipboard_depth() method
    - Implement set_clipboard_depth() with validation
    - Implement get_hotkey() method
    - Implement set_hotkey() method
    - Implement get_launch_at_login() method
    - Implement set_launch_at_login() method
    - _Requirements: 2.1, 2.2, 2.3, 2.6, 3.3_
  
  - [x] 6.2 Write unit tests for SettingsManager
    - Test default values
    - Test validation for clipboard depth
    - Test settings getters and setters
    - _Requirements: 2.2, 3.3_

- [x] 7. Implement HotkeyHandler
  - [x] 7.1 Create HotkeyHandler class with global hotkey support
    - Implement __init__ with callback parameter
    - Implement register_hotkey() using PyQt6 or pynput
    - Implement unregister_hotkey() for cleanup
    - Handle macOS permission requests
    - Prevent duplicate activations with state flag
    - _Requirements: 3.1, 3.2, 3.4_
  
  - [x] 7.2 Write property test for hotkey display
    - **Property 6: Hotkey displays popup**
    - **Validates: Requirements 3.2**
  
  - [x] 7.3 Write property test for hotkey idempotence
    - **Property 7: Hotkey press idempotence**
    - **Validates: Requirements 3.4**
  
  - [x] 7.4 Write unit tests for HotkeyHandler
    - Test hotkey registration on startup
    - Test default hotkey value
    - Test duplicate activation prevention
    - _Requirements: 3.1, 3.3_

- [x] 8. Checkpoint - Ensure background services tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Implement History Popup UI
  - [x] 9.1 Create UIManager class with History Popup
    - Implement __init__ with HistoryManager dependency
    - Create show_history_popup() method
    - Design frameless window with rounded corners (500x400px)
    - Center window on screen
    - Set window to stay on top
    - Implement custom list widget for history items
    - Render text items with 50-char truncation
    - Render image items with 40x40px thumbnails
    - Render unsupported items with type indicator
    - Display items in reverse chronological order
    - Pre-select most recent item
    - Add smooth fade-in animation
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 7.4, 7.5, 10.3_
  
  - [x] 9.2 Write property test for display order
    - **Property 8: History display order**
    - **Validates: Requirements 4.1**
  
  - [x] 9.3 Write property test for truncation
    - **Property 9: Item preview truncation**
    - **Validates: Requirements 4.4, 4.5**
  
  - [x] 9.4 Write property test for image thumbnails
    - **Property 16: Image thumbnail generation**
    - **Validates: Requirements 7.4**
  
  - [x] 9.5 Write property test for unsupported content
    - **Property 17: Unsupported content handling**
    - **Validates: Requirements 7.5**
  
  - [x] 9.6 Write unit tests for History Popup
    - Test popup centers on screen
    - Test most recent item pre-selected
    - Test visual feedback for selection
    - _Requirements: 4.2, 5.5, 10.3_

- [x] 10. Implement popup interaction handlers
  - [x] 10.1 Add click and keyboard handlers to History Popup
    - Implement single-click handler to copy item to clipboard
    - Implement double-click handler to copy and close
    - Implement Enter key handler to copy and close
    - Implement Escape key handler to close popup
    - Implement focus-loss handler to close popup
    - Implement arrow key navigation (up/down)
    - Capture keyboard focus on popup display
    - _Requirements: 4.7, 4.8, 5.1, 5.2, 5.3, 10.2, 10.7_
  
  - [x] 10.2 Write property test for item selection
    - **Property 12: Item selection copies to clipboard**
    - **Validates: Requirements 5.1**
  
  - [x] 10.3 Write property test for double-click
    - **Property 13: Double-click copies and closes**
    - **Validates: Requirements 5.2**
  
  - [x] 10.4 Write property test for Enter key
    - **Property 14: Enter key copies and closes**
    - **Validates: Requirements 5.3**
  
  - [x] 10.5 Write property test for focus loss
    - **Property 10: Popup closes on focus loss**
    - **Validates: Requirements 4.7**
  
  - [x] 10.6 Write property test for Escape key
    - **Property 11: Popup closes on Escape**
    - **Validates: Requirements 4.8**
  
  - [x] 10.7 Write property test for keyboard navigation
    - **Property 20: Keyboard navigation**
    - **Validates: Requirements 10.2**
  
  - [x] 10.8 Write unit tests for popup interactions
    - Test keyboard focus capture
    - Test all interaction methods
    - _Requirements: 10.7_

- [x] 11. Checkpoint - Ensure UI tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 12. Implement Settings Panel UI
  - [x] 12.1 Create Settings Panel window
    - Add show_settings_panel() method to UIManager
    - Create native macOS preferences window
    - Add slider widget for clipboard depth (5-100 range)
    - Add label showing current depth value
    - Add hotkey recorder widget
    - Add launch at login checkbox
    - Add About section with app version
    - Wire settings changes to SettingsManager
    - Wire settings changes to HistoryManager (for depth updates)
    - _Requirements: 2.1, 2.3, 2.4, 2.6_
  
  - [x] 12.2 Write unit tests for Settings Panel
    - Test settings panel contains depth control
    - Test depth slider range validation
    - Test settings persistence in SettingsManager
    - _Requirements: 2.1_

- [x] 13. Implement PermissionManager
  - [x] 13.1 Create PermissionManager class for macOS permissions
    - Implement check_accessibility_permission() using PyObjC or subprocess
    - Implement request_accessibility_permission() method
    - Implement check_all_permissions() returning status dict
    - Implement open_system_preferences() to open specific panes
    - Add permission status monitoring
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.6_
  
  - [x] 13.2 Create permission dialog UI
    - Add show_permission_dialog() method to UIManager
    - Design friendly permission explanation dialog
    - Include screenshots showing System Preferences steps
    - Add "Open System Preferences" button
    - Add "I'll Do This Later" option
    - Use non-technical, user-friendly language
    - _Requirements: 13.2, 13.7_
  
  - [x] 13.3 Write property test for permission detection
    - **Property 22: Permission detection and recovery**
    - **Validates: Requirements 13.3**
  
  - [x] 13.4 Write unit tests for PermissionManager
    - Test permission checking
    - Test System Preferences opening
    - Test degraded mode behavior
    - _Requirements: 13.4, 13.5_

- [x] 14. Implement OnboardingManager and welcome screen
  - [x] 14.1 Create OnboardingManager class
    - Implement should_show_welcome() checking first launch flag
    - Implement show_welcome_screen() method
    - Implement mark_welcome_complete() method
    - Implement demonstrate_popup() for "Try It Now" feature
    - _Requirements: 11.1, 11.7_
  
  - [x] 14.2 Create welcome screen UI
    - Add show_welcome_screen() method to UIManager
    - Design friendly welcome dialog with Kliply branding
    - Add large visual showing Cmd+Shift+V keyboard shortcut
    - Add brief explanation text
    - Add "Try It Now" button that demonstrates popup
    - Add "Get Started" button to dismiss
    - Add "Don't show this again" checkbox
    - _Requirements: 11.1, 11.5, 11.6, 11.7_
  
  - [x] 14.3 Write property test for welcome screen
    - **Property 21: Welcome screen shows on first launch**
    - **Validates: Requirements 11.1**
  
  - [x] 14.4 Write unit tests for OnboardingManager
    - Test first launch detection
    - Test welcome screen display logic
    - Test "Try It Now" demonstration
    - _Requirements: 11.1, 11.7_

- [x] 15. Implement MenuBarManager
  - [x] 15.1 Create MenuBarManager class with system tray integration
    - Implement __init__ with UIManager and SettingsManager dependencies
    - Create menu bar icon using QSystemTrayIcon
    - Implement create_menu() method
    - Add "Show History" menu item with hotkey label
    - Add "Settings..." menu item
    - Add "Clear History" menu item
    - Add "Show Welcome" menu item (for re-accessing onboarding)
    - Add separator
    - Add "Quit" menu item
    - Wire menu items to appropriate handlers
    - Add permission status indicator when permissions denied
    - _Requirements: 6.3, 6.4, 13.5_
  
  - [x] 15.2 Write unit tests for MenuBarManager
    - Test menu bar icon presence
    - Test menu items exist
    - Test menu item actions
    - Test permission indicator display
    - _Requirements: 6.3, 6.4_

- [x] 16. Implement main application entry point
  - [x] 16.1 Create main application class and wire all components
    - Create MainApplication class
    - Initialize QApplication
    - Instantiate all managers (History, Settings, Clipboard, UI, Hotkey, MenuBar, Permission, Onboarding)
    - Check permissions on startup using PermissionManager
    - Show welcome screen on first launch using OnboardingManager
    - Wire components together with proper dependencies
    - Start ClipboardMonitor
    - Register global hotkey (with permission handling)
    - Set up signal handlers for clean shutdown
    - Implement quit() method to stop all background processes
    - Create run() method to start event loop
    - _Requirements: 6.1, 6.2, 6.6, 11.1, 13.6_
  
  - [x] 16.2 Write integration tests
    - Test application initialization
    - Test component wiring
    - Test first launch flow
    - Test permission checking on startup
    - Test clean shutdown
    - _Requirements: 6.6, 11.1_

- [x] 17. Add error handling and logging
  - [x] 17.1 Implement comprehensive error handling
    - Add logging configuration with file and console handlers
    - Add try-catch blocks in ClipboardMonitor for access errors
    - Add error handling for content type errors
    - Add memory pressure handling (10MB limit per item)
    - Add error handling for hotkey registration failures with permission dialogs
    - Add error handling for UI rendering errors
    - Add settings validation error handling
    - Add permission denial handling with degraded mode
    - Log all errors with appropriate severity levels
    - _Requirements: 9.5, 13.4_
  
  - [x] 17.2 Write unit tests for error scenarios
    - Test error recovery in clipboard monitoring
    - Test oversized content rejection
    - Test invalid settings handling
    - Test permission denial handling
    - _Requirements: 9.5, 13.4_

- [x] 18. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 19. Add App Store packaging and metadata
  - [x] 19.1 Configure py2app for macOS application bundle
    - Create setup.py with py2app configuration
    - Configure app bundle identifier (com.yourcompany.Kliply)
    - Add app icon (1024x1024 PNG)
    - Configure Info.plist with required keys
    - Add entitlements for clipboard access
    - Add entitlements for global hotkey registration
    - Configure sandboxing settings
    - Add privacy usage descriptions (NSAccessibilityUsageDescription)
    - Add LSUIElement key to hide from Dock
    - _Requirements: 8.1, 8.2, 8.3, 8.6, 8.7, 12.1, 12.3, 12.4_
  
  - [x] 19.2 Create build and signing scripts
    - Create build script for py2app
    - Add code signing configuration
    - Add notarization steps
    - Document build process in README
    - Test installation from .dmg on clean system
    - _Requirements: 8.4, 12.2, 12.4_

- [ ] 20. Polish and final integration
  - [ ] 20.1 Add UI animations and polish
    - Implement smooth fade-in/out for popup
    - Add visual feedback for clipboard copy actions
    - Ensure native macOS styling throughout
    - Test welcome screen flow
    - Test permission dialog flow
    - Test on multiple macOS versions
    - _Requirements: 10.1, 10.5, 10.6, 11.1, 13.2_
  
  - [ ] 20.2 Performance optimization
    - Profile memory usage
    - Optimize clipboard polling interval
    - Optimize image thumbnail generation
    - Test responsiveness of all interactions
    - _Requirements: 9.1, 9.2, 9.3, 9.4_
  
  - [ ] 20.3 Write end-to-end integration tests
    - Test complete user workflows
    - Test first-time user experience
    - Test permission request flows
    - Test with various content types
    - Test rapid clipboard changes
    - Test concurrent operations
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 5.1, 5.2, 5.3, 11.1_

- [ ] 21. Final checkpoint - Complete testing and validation
  - Run full test suite with coverage report
  - Verify all property tests pass with 100+ iterations
  - Verify code coverage >85%
  - Test application bundle on clean macOS system
  - Test first-time installation experience
  - Test permission request flows on fresh system
  - Verify notarization and code signing
  - Test with Gatekeeper enabled
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation throughout development
- Property tests validate universal correctness properties with 100+ iterations
- Unit tests validate specific examples, edge cases, and integration points
- The implementation follows a bottom-up approach: data models → business logic → UI → integration
- All components are designed to be testable in isolation before integration
