import Foundation
import SwiftUI

/// Main application state manager
@Observable
@MainActor
class AppState {
    static let shared = AppState()
    
    // Services
    private let clipboardMonitor = ClipboardMonitor()
    private let hotkeyManager = HotkeyManager()
    private let settings = AppSettings.shared
    
    // State
    var clipboardHistory: [ClipboardItem] = []
    var isPopupVisible: Bool = false
    var isAccessibilityPermissionGranted: Bool = false
    var selectedItemIndex: Int = 0
    var searchQuery: String = ""
    var selectedFilter: ContentFilter = .all
    var showSettings: Bool = false
    private var previousApp: NSRunningApplication?
    private var isPasting: Bool = false
    
    // Computed
    var filteredHistory: [ClipboardItem] {
        var items = clipboardHistory
        
        // Apply filter
        if selectedFilter != .all {
            items = items.filter { item in
                switch selectedFilter {
                case .text:
                    if case .text = item.content { return true }
                    if case .richText = item.content { return true }
                    return false
                case .images:
                    if case .image = item.content { return true }
                    return false
                case .urls:
                    if case .url = item.content { return true }
                    return false
                case .files:
                    if case .fileURLs = item.content { return true }
                    return false
                case .all:
                    return true
                }
            }
        }
        
        // Apply search
        if !searchQuery.isEmpty {
            items = items.filter { item in
                item.content.previewText.localizedCaseInsensitiveContains(searchQuery)
            }
        }
        
        return items
    }
    
    private init() {
        setupClipboardMonitor()
        setupHotkeyManager()
    }
    
    func start() {
        // Check permissions
        isAccessibilityPermissionGranted = hotkeyManager.isPermissionGranted()
        
        if !isAccessibilityPermissionGranted {
            // This will trigger the permission prompt
            _ = hotkeyManager.checkAccessibilityPermissions()
            
            // Start polling for permission grant
            startPermissionPolling()
        } else {
            registerHotkey()
        }
        
        clipboardMonitor.startMonitoring()
    }
    
    func stop() {
        clipboardMonitor.stopMonitoring()
        hotkeyManager.unregisterHotkey()
    }
    
    private func setupClipboardMonitor() {
        clipboardMonitor.onClipboardChange = { [weak self] content in
            guard let self = self, let content = content else { return }
            Task { @MainActor in
                self.addToHistory(content: content)
            }
        }
    }
    
    private func setupHotkeyManager() {
        hotkeyManager.onHotkeyPressed = { [weak self] in
            Task { @MainActor in
                guard let self = self else { return }
                // Store the currently active app BEFORE opening popup
                let workspace = NSWorkspace.shared
                let frontmost = workspace.frontmostApplication
                print("=== HOTKEY PRESSED ===")
                print("Frontmost app: \(frontmost?.localizedName ?? "nil")")
                print("Frontmost bundle: \(frontmost?.bundleIdentifier ?? "nil")")
                print("Our bundle: \(Bundle.main.bundleIdentifier ?? "nil")")
                
                self.previousApp = frontmost
                print("Stored previous app: \(self.previousApp?.localizedName ?? "nil")")
                self.togglePopup()
            }
        }
    }
    
    private func registerHotkey() {
        let success = hotkeyManager.registerHotkey(
            keyCode: settings.hotkeyKeyCode,
            modifiers: settings.hotkeyModifiers
        )
        
        if success {
            print("Hotkey registered: \(settings.hotkeyDescription)")
        } else {
            print("Failed to register hotkey")
        }
    }
    
    private func startPermissionPolling() {
        var permissionTimer: Timer?
        permissionTimer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { _ in
            Task { @MainActor [weak self] in
                guard let self = self else {
                    permissionTimer?.invalidate()
                    permissionTimer = nil
                    return
                }
                
                if self.hotkeyManager.isPermissionGranted() {
                    self.isAccessibilityPermissionGranted = true
                    self.registerHotkey()
                    permissionTimer?.invalidate()
                    permissionTimer = nil
                }
            }
        }
    }
    
    func addToHistory(content: ClipboardContent) {
        let newItem = ClipboardItem(content: content)
        
        // Skip if it's a duplicate of the most recent item
        if let lastItem = clipboardHistory.first, lastItem.content == content {
            return
        }
        
        clipboardHistory.insert(newItem, at: 0)
        
        // Trim to history depth
        if clipboardHistory.count > settings.historyDepth {
            clipboardHistory.removeLast(clipboardHistory.count - settings.historyDepth)
        }
    }
    
    func togglePopup() {
        isPopupVisible.toggle()
        
        if isPopupVisible {
            selectedItemIndex = 0
            searchQuery = ""
        }
    }
    
    func storePreviousAppAndToggle(_ app: NSRunningApplication?) {
        previousApp = app
        print("storePreviousAppAndToggle: Stored \(app?.localizedName ?? "nil")")
        togglePopup()
    }
    
    func updatePreviousApp(_ app: NSRunningApplication) {
        print("updatePreviousApp: Changing from \(previousApp?.localizedName ?? "nil") to \(app.localizedName ?? "nil")")
        previousApp = app
    }
    
    func selectItem(at index: Int) {
        print("selectItem called with index: \(index)")
        guard index < filteredHistory.count else {
            print("Index out of bounds: \(index) >= \(filteredHistory.count)")
            return
        }
        let item = filteredHistory[index]
        print("Selected item: \(item.content.previewText.prefix(50))")
        
        // Write to clipboard
        clipboardMonitor.writeToClipboard(item.content)
        print("Written to clipboard")
        
        // Store whether we should paste
        let shouldPaste = isAccessibilityPermissionGranted
        
        // Close popup first
        isPopupVisible = false
        print("Popup closed, will paste: \(shouldPaste)")
        
        // Wait for popup to close, then paste
        if shouldPaste {
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) { [weak self] in
                self?.simulatePaste()
            }
        } else {
            print("Copied to clipboard. Accessibility permission required for auto-paste.")
        }
    }
    
    func clearHistory() {
        clipboardHistory.removeAll()
    }
    
    func removeItem(at index: Int) {
        guard index < clipboardHistory.count else { return }
        clipboardHistory.remove(at: index)
    }
    
    private func simulatePaste() {
        // Prevent multiple simultaneous paste operations
        guard !isPasting else {
            print("simulatePaste: Already pasting, ignoring duplicate call")
            return
        }
        
        isPasting = true
        print("simulatePaste: Starting paste sequence")
        
        // If we have a previous app, activate it first
        if let prevApp = previousApp {
            print("simulatePaste: Activating \(prevApp.localizedName ?? "unknown")")
            prevApp.activate(options: [])
            
            // Wait for activation, then paste
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.15) { [weak self] in
                print("simulatePaste: Executing paste command")
                let script = """
                tell application "System Events"
                    keystroke "v" using command down
                end tell
                """
                
                if let appleScript = NSAppleScript(source: script) {
                    var error: NSDictionary?
                    _ = appleScript.executeAndReturnError(&error)
                    if let error = error {
                        print("Failed to simulate paste: \(error)")
                    } else {
                        print("Paste command sent successfully")
                    }
                } else {
                    print("Failed to create AppleScript")
                }
                
                // Reset pasting flag
                self?.isPasting = false
            }
        } else {
            print("simulatePaste: ERROR - No previous app stored!")
            isPasting = false
        }
    }
}

enum ContentFilter: String, CaseIterable {
    case all = "All"
    case text = "Text"
    case images = "Images"
    case urls = "URLs"
    case files = "Files"
}
