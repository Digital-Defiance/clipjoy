import SwiftUI

@main
struct KliplyApp: App {
    @State private var appState = AppState.shared
    @State private var settings = AppSettings.shared
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    
    var body: some Scene {
        // Menu Bar App - no main window
        MenuBarExtra("Kliply", systemImage: "clipboard") {
            MenuBarView()
                .environment(appState)
                .environment(settings)
        }
        .menuBarExtraStyle(.menu)
        
        // Settings window
        Settings {
            SettingsView()
                .environment(settings)
        }
    }
}

class AppDelegate: NSObject, NSApplicationDelegate {
    var popupWindow: NSWindow?
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        // Start the app state
        Task { @MainActor in
            AppState.shared.start()
        }
        
        // Hide from Dock
        NSApp.setActivationPolicy(.accessory)
        
        // Monitor for popup visibility changes
        setupPopupMonitoring()
    }
    
    func applicationWillTerminate(_ notification: Notification) {
        AppState.shared.stop()
    }
    
    private func setupPopupMonitoring() {
        Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in
            guard let self = self else { return }
            
            Task { @MainActor in
                let shouldShow = AppState.shared.isPopupVisible
                
                if shouldShow && self.popupWindow == nil {
                    self.showPopup()
                } else if !shouldShow && self.popupWindow != nil {
                    self.hidePopup()
                }
            }
        }
    }
    
    @MainActor
    private func showPopup() {
        let contentView = PopupWindow()
            .environment(AppState.shared)
        
        let hostingController = NSHostingController(rootView: contentView)
        
        let window = NSWindow(contentViewController: hostingController)
        window.styleMask = [.titled, .closable, .fullSizeContentView]
        window.titlebarAppearsTransparent = true
        window.titleVisibility = .hidden
        window.isMovableByWindowBackground = true
        window.backgroundColor = NSColor.windowBackgroundColor
        window.isOpaque = true
        window.level = .floating
        window.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary]
        window.hidesOnDeactivate = false
        
        // Center on screen
        if let screen = NSScreen.main {
            let screenRect = screen.visibleFrame
            let windowRect = window.frame
            let x = screenRect.midX - windowRect.width / 2
            let y = screenRect.midY - windowRect.height / 2
            window.setFrameOrigin(NSPoint(x: x, y: y))
        }
        
        // Make window key and activate app
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
        
        self.popupWindow = window
    }
    
    @MainActor
    private func hidePopup() {
        popupWindow?.close()
        popupWindow = nil
    }
}

struct MenuBarView: View {
    @Environment(AppState.self) private var appState
    @Environment(\.openSettings) private var openSettings
    
    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            Button("Show Clipboard") {
                appState.togglePopup()
            }
            .keyboardShortcut("v", modifiers: [.command, .shift])
            
            Divider()
            
            if appState.clipboardHistory.isEmpty {
                Text("No History")
                    .foregroundStyle(.secondary)
                    .padding(.horizontal)
            } else {
                Text("\(appState.clipboardHistory.count) items in history")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .padding(.horizontal)
                
                Button("Clear History") {
                    appState.clearHistory()
                }
                .disabled(appState.clipboardHistory.isEmpty)
            }
            
            Divider()
            
            Button("Settings...") {
                openSettings()
            }
            .keyboardShortcut(",")
            
            Divider()
            
            if !appState.isAccessibilityPermissionGranted {
                HStack {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .foregroundStyle(.yellow)
                    Text("Accessibility permission required")
                        .font(.caption)
                }
                .padding(.horizontal)
                
                Divider()
            }
            
            Button("Quit Kliply") {
                NSApplication.shared.terminate(nil)
            }
            .keyboardShortcut("q")
        }
        .padding(.vertical, 4)
    }
}
