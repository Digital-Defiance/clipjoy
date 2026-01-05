import Foundation
import SwiftUI
import Carbon

/// Application settings and preferences
@Observable
@MainActor
class AppSettings {
    static let shared = AppSettings()
    
    // History settings
    var historyDepth: Int = 10 {
        didSet {
            if historyDepth < 1 { historyDepth = 1 }
            if historyDepth > 100 { historyDepth = 100 }
        }
    }
    
    // Hotkey settings
    var hotkeyModifiers: UInt32 = UInt32(cmdKey | shiftKey) // Cmd+Shift
    var hotkeyKeyCode: UInt32 = UInt32(kVK_ANSI_V) // V key
    
    // Paste behavior
    var alwaysPastePlainText: Bool = false
    
    // UI settings
    var showPreviewImages: Bool = true
    var maxImagePreviewHeight: CGFloat = 200
    
    // Startup settings
    var launchAtLogin: Bool = true {
        didSet {
            if launchAtLogin != oldValue {
                Task { @MainActor in
                    await LoginItemManager.shared.setLaunchAtLogin(launchAtLogin)
                }
            }
        }
    }
    
    // Exclusion settings
    private(set) var excludedApps: [String] = [] {
        didSet {
            UserDefaults.standard.set(excludedApps, forKey: "excludedApps")
        }
    }
    
    private init() {
        // Check initial login item status
        Task { @MainActor in
            self.launchAtLogin = await LoginItemManager.shared.isEnabled()
        }
        
        // Load excluded apps from UserDefaults
        if let saved = UserDefaults.standard.array(forKey: "excludedApps") as? [String] {
            self.excludedApps = saved
        }
    }
    
    func isAppExcluded(bundleIdentifier: String) -> Bool {
        excludedApps.contains(where: { excludedApp in
            bundleIdentifier.lowercased().contains(excludedApp.lowercased()) ||
            excludedApp.lowercased().contains(bundleIdentifier.lowercased())
        })
    }
    
    func addExcludedApp(_ app: String) {
        if !excludedApps.contains(app) {
            excludedApps.append(app)
            UserDefaults.standard.set(excludedApps, forKey: "excludedApps")
        }
    }
    
    func removeExcludedApp(_ app: String) {
        excludedApps.removeAll { $0 == app }
        UserDefaults.standard.set(excludedApps, forKey: "excludedApps")
    }
    
    /// Detects commonly used password managers and sensitive apps installed on the system
    func detectSensitiveApps() -> [String] {
        let sensitiveApps: [(bundleIds: [String], displayName: String, appNames: [String])] = [
            // 1Password - multiple versions
            (["com.agilebits.onepassword7", "com.agilebits.onepassword8", "com.agilebits.onepassword", "com.1password.1password"], "1Password", ["1Password 7", "1Password", "1Password 8"]),
            // LastPass
            (["com.lastpass.lpmac"], "LastPass", ["LastPass"]),
            // Dashlane
            (["com.dashlane.mac"], "Dashlane", ["Dashlane"]),
            // Avast
            (["com.avast.SecurePasswordManager"], "Avast Passwords", ["Avast Passwords"]),
            // Bitwarden
            (["com.bitwarden.desktop"], "Bitwarden", ["Bitwarden"]),
            // KeePass
            (["org.keepassxc.KeePassXC"], "KeePassXC", ["KeePassXC"]),
            // Keychain
            (["com.apple.keychainaccess"], "Keychain Access", ["Keychain Access"]),
            // 2FA Apps
            (["com.microsoft.authenticator"], "Microsoft Authenticator", ["Microsoft Authenticator"]),
            (["com.google.authenticator"], "Google Authenticator", ["Google Authenticator"]),
            // Browsers
            (["org.chromium.Chromium", "com.google.Chrome"], "Chrome", ["Google Chrome", "Chromium", "Chrome"]),
            (["com.apple.Safari"], "Safari", ["Safari"]),
            (["org.mozilla.firefox"], "Firefox", ["Firefox"]),
            (["com.operasoftware.Opera"], "Opera", ["Opera"]),
            // System
            (["com.apple.finder"], "Finder", ["Finder"]),
            // Dev Tools
            (["net.telerik.Fiddler"], "Fiddler", ["Fiddler"]),
            (["com.telerik.fiddlereverywhere"], "Fiddler Everywhere", ["Fiddler Everywhere"]),
        ]
        
        let workspace = NSWorkspace.shared
        let fileManager = FileManager.default
        var detected: [String] = []
        
        for appGroup in sensitiveApps {
            var found = false
            
            // Try bundle ID lookup first
            for bundleId in appGroup.bundleIds {
                if let _ = workspace.absolutePathForApplication(withBundleIdentifier: bundleId) {
                    detected.append(appGroup.displayName)
                    found = true
                    break
                }
            }
            
            if found { continue }
            
            // Try looking in common app directories
            let appDirs = ["/Applications", "\(NSHomeDirectory())/Applications"]
            for dir in appDirs {
                if !fileManager.fileExists(atPath: dir) { continue }
                
                guard let contents = try? fileManager.contentsOfDirectory(atPath: dir) else { continue }
                
                for appName in appGroup.appNames {
                    for content in contents {
                        if content.contains(appName) && content.hasSuffix(".app") {
                            detected.append(appGroup.displayName)
                            found = true
                            break
                        }
                    }
                    if found { break }
                }
                if found { break }
            }
        }
        
        return detected.sorted()
    }
    
    var hotkeyDescription: String {
        var modifiers: [String] = []
        if hotkeyModifiers & UInt32(cmdKey) != 0 { modifiers.append("⌘") }
        if hotkeyModifiers & UInt32(optionKey) != 0 { modifiers.append("⌥") }
        if hotkeyModifiers & UInt32(controlKey) != 0 { modifiers.append("⌃") }
        if hotkeyModifiers & UInt32(shiftKey) != 0 { modifiers.append("⇧") }
        
        let keyName = keyCodeToString(hotkeyKeyCode)
        return modifiers.joined() + keyName
    }
    
    private func keyCodeToString(_ keyCode: UInt32) -> String {
        switch Int(keyCode) {
        case kVK_ANSI_V: return "V"
        case kVK_ANSI_C: return "C"
        case kVK_ANSI_X: return "X"
        case kVK_ANSI_A: return "A"
        case kVK_Space: return "Space"
        case kVK_Return: return "↩"
        case kVK_Escape: return "⎋"
        default: return "?"
        }
    }
}
