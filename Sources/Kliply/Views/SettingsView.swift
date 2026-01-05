import SwiftUI
import AppKit

struct SettingsView: View {
    @Environment(AppSettings.self) private var settings
    @Environment(\.dismiss) private var dismiss
    @State private var windowMonitor: NSObjectProtocol?
    
    var body: some View {
        TabView {
            GeneralSettingsView()
                .tabItem {
                    Label("General", systemImage: "gear")
                }
            
            HotkeySettingsView()
                .tabItem {
                    Label("Hotkey", systemImage: "keyboard")
                }
            
            ExcludedAppsSettingsView()
                .tabItem {
                    Label("Exclusions", systemImage: "lock.circle")
                }
            
            AboutView()
                .tabItem {
                    Label("About", systemImage: "info.circle")
                }
        }
        .frame(width: 500, height: 500)
        .onAppear {
            bringWindowToFront()
            setupWindowMonitoring()
        }
        .onDisappear {
            removeWindowMonitoring()
        }
    }
    
    private func bringWindowToFront() {
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            // Activate the app to bring it to foreground
            NSApp.activate(ignoringOtherApps: true)
            
            if let window = NSApplication.shared.windows.first(where: { $0.isKeyWindow }) {
                window.level = .floating
                window.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary]
                window.makeKeyAndOrderFront(nil)
            }
        }
    }
    
    private func setupWindowMonitoring() {
        // Monitor when the window becomes key (focused) again
        windowMonitor = NotificationCenter.default.addObserver(
            forName: NSWindow.didBecomeKeyNotification,
            object: nil,
            queue: .main
        ) { [self] notification in
            guard let window = notification.object as? NSWindow else { return }
            
            // Check if this is a Settings window
            if window.title.contains("Settings") || window.isKeyWindow {
                self.bringWindowToFront()
            }
        }
    }
    
    private func removeWindowMonitoring() {
        if let monitor = windowMonitor {
            NotificationCenter.default.removeObserver(monitor)
        }
    }
}

struct GeneralSettingsView: View {
    @Environment(AppSettings.self) private var settings
    
    var body: some View {
        Form {
            Section {
                HStack {
                    Text("History Depth:")
                    Spacer()
                    TextField("", value: Binding(
                        get: { settings.historyDepth },
                        set: { settings.historyDepth = $0 }
                    ), format: .number)
                    .frame(width: 60)
                    .textFieldStyle(.roundedBorder)
                    
                    Stepper("", value: Binding(
                        get: { settings.historyDepth },
                        set: { settings.historyDepth = $0 }
                    ), in: 1...100)
                    .labelsHidden()
                }
                
                Text("Number of clipboard items to keep in memory")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            } header: {
                Text("Clipboard History")
            }
            
            Section {
                Toggle("Launch at login", isOn: Binding(
                    get: { settings.launchAtLogin },
                    set: { settings.launchAtLogin = $0 }
                ))
                
                Text("Automatically start Kliply when you log in")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            } header: {
                Text("Startup")
            }
            
            Section {
                Toggle("Always paste as plain text", isOn: Binding(
                    get: { settings.alwaysPastePlainText },
                    set: { settings.alwaysPastePlainText = $0 }
                ))
                
                Toggle("Show image previews", isOn: Binding(
                    get: { settings.showPreviewImages },
                    set: { settings.showPreviewImages = $0 }
                ))
            } header: {
                Text("Paste Behavior")
            }
        }
        .formStyle(.grouped)
        .padding()
    }
}

struct HotkeySettingsView: View {
    @Environment(AppSettings.self) private var settings
    @State private var isRecording = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Global Hotkey")
                .font(.headline)
            
            HStack {
                Text("Current Hotkey:")
                
                Text(settings.hotkeyDescription)
                    .font(.system(.body, design: .monospaced))
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(Color(nsColor: .controlBackgroundColor))
                    .cornerRadius(6)
                
                Spacer()
                
                Button(isRecording ? "Recording..." : "Change") {
                    isRecording.toggle()
                }
            }
            
            if isRecording {
                Text("Press your desired key combination...")
                    .font(.callout)
                    .foregroundStyle(.secondary)
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(Color.accentColor.opacity(0.1))
                    .cornerRadius(8)
            }
            
            Divider()
            
            VStack(alignment: .leading, spacing: 8) {
                Text("Tips:")
                    .font(.headline)
                
                Text("• The hotkey works system-wide when Kliply is running")
                Text("• Recommended modifiers: ⌘ (Command) or ⇧ (Shift)")
                Text("• Avoid conflicting with common system shortcuts")
            }
            .font(.callout)
            .foregroundStyle(.secondary)
            
            Spacer()
        }
        .padding()
    }
}

struct ExcludedAppsSettingsView: View {
    @Environment(AppSettings.self) private var settings
    @State private var newAppName: String = ""
    @State private var detectedApps: [String] = []
    
    var body: some View {
        VStack(spacing: 16) {
            VStack(alignment: .leading, spacing: 8) {
                Text("Excluded Apps")
                    .font(.headline)
                
                Text("Clipboard changes from these apps won't be saved to history")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            
            HStack(spacing: 8) {
                TextField("App name or bundle ID (e.g., 1Password, com.agilebits.onepassword7)", text: $newAppName)
                    .textFieldStyle(.roundedBorder)
                
                Button(action: addApp) {
                    Image(systemName: "plus.circle.fill")
                }
                .disabled(newAppName.trimmingCharacters(in: .whitespaces).isEmpty)
                
                Button(action: loadDetectedApps) {
                    Image(systemName: "sparkles")
                }
                .help("Auto-detect password managers and sensitive apps")
            }
            
            if !detectedApps.isEmpty {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Detected Apps")
                        .font(.caption)
                        .fontWeight(.semibold)
                        .foregroundStyle(.secondary)
                    
                    VStack(spacing: 6) {
                        ForEach(detectedApps, id: \.self) { app in
                            HStack {
                                Image(systemName: "lock.shield")
                                    .foregroundStyle(.orange)
                                    .font(.caption)
                                
                                Text(app)
                                    .font(.caption)
                                
                                Spacer()
                                
                                if settings.excludedApps.contains(app) {
                                    Image(systemName: "checkmark.circle.fill")
                                        .foregroundStyle(.green)
                                        .font(.caption)
                                } else {
                                    Button(action: { addDetectedApp(app) }) {
                                        Image(systemName: "plus.circle")
                                            .foregroundStyle(.blue)
                                    }
                                    .buttonStyle(.plain)
                                }
                            }
                            .padding(.horizontal, 8)
                            .padding(.vertical, 6)
                            .background(Color(nsColor: .controlBackgroundColor).opacity(0.5))
                            .cornerRadius(4)
                        }
                    }
                }
                .padding(.vertical, 8)
            }
            
            if settings.excludedApps.isEmpty {
                VStack(spacing: 12) {
                    Image(systemName: "list.bullet.indent")
                        .font(.system(size: 32))
                        .foregroundStyle(.secondary)
                    
                    Text("No excluded apps")
                        .foregroundStyle(.secondary)
                    
                    Text("Add apps to prevent their clipboard changes from being saved")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .multilineTextAlignment(.center)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(Color(nsColor: .controlBackgroundColor).opacity(0.5))
                .cornerRadius(8)
            } else {
                List {
                    ForEach(settings.excludedApps, id: \.self) { app in
                        HStack {
                            VStack(alignment: .leading, spacing: 4) {
                                Text(app)
                                    .font(.body)
                                
                                Text("Clipboard changes ignored")
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                            }
                            
                            Spacer()
                            
                            Button(action: { removeApp(app) }) {
                                Image(systemName: "xmark.circle.fill")
                                    .foregroundStyle(.secondary)
                            }
                            .buttonStyle(.plain)
                        }
                    }
                }
            }
            
            Spacer()
        }
        .padding()
        .onAppear {
            loadDetectedApps()
        }
    }
    
    private func addApp() {
        let trimmed = newAppName.trimmingCharacters(in: .whitespaces)
        if !trimmed.isEmpty {
            settings.addExcludedApp(trimmed)
            newAppName = ""
        }
    }
    
    private func addDetectedApp(_ app: String) {
        settings.addExcludedApp(app)
    }
    
    private func removeApp(_ app: String) {
        settings.removeExcludedApp(app)
    }
    
    private func loadDetectedApps() {
        detectedApps = settings.detectSensitiveApps().filter { !settings.excludedApps.contains($0) }
    }
}

struct AboutView: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "clipboard")
                .font(.system(size: 60))
                .foregroundStyle(.tint)
            
            Text("Kliply")
                .font(.title)
                .fontWeight(.bold)
            
            Text("Version 1.0.7")
                .foregroundStyle(.secondary)
            
            Divider()
                .padding(.horizontal, 40)
            
            VStack(spacing: 8) {
                Text("A powerful clipboard manager for macOS")
                    .multilineTextAlignment(.center)
                
                Text("Inspired by Windows' Win+V clipboard history")
                    .font(.callout)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
            }
            
            Spacer()
            
            VStack(spacing: 12) {
                Link("GitHub Repository", destination: URL(string: "https://github.com/Digital-Defiance/kliply")!)
                
                Text("Licensed under MIT License")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                
                Text("© 2026 Digital Defiance, Jessica Mulein")
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }
            .padding(.bottom)
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

#Preview("Settings") {
    @Previewable @State var settings = AppSettings.shared
    SettingsView()
        .environment(settings)
}

#Preview("About") {
    AboutView()
}
