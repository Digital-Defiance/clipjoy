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
    
    private init() {}
    
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
