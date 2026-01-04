import SwiftUI

struct SettingsView: View {
    @Environment(AppSettings.self) private var settings
    @Environment(\.dismiss) private var dismiss
    
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
            
            AboutView()
                .tabItem {
                    Label("About", systemImage: "info.circle")
                }
        }
        .frame(width: 500, height: 400)
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

struct AboutView: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "clipboard")
                .font(.system(size: 60))
                .foregroundStyle(.tint)
            
            Text("Kliply")
                .font(.title)
                .fontWeight(.bold)
            
            Text("Version 1.0.5")
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
