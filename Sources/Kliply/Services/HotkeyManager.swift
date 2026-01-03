import Foundation
@preconcurrency import Carbon
import AppKit

/// Manages global hotkey registration and events
@MainActor
class HotkeyManager {
    private var eventHandler: EventHandlerRef?
    private var hotKeyRef: EventHotKeyRef?
    private let hotkeyID = EventHotKeyID(signature: OSType(0x4B4C5059), id: 1) // 'KLPY'
    
    var onHotkeyPressed: (() -> Void)?
    
    init() {}
    
    func registerHotkey(keyCode: UInt32, modifiers: UInt32) -> Bool {
        // Unregister existing hotkey first
        unregisterHotkey()
        
        // Check for accessibility permissions
        guard checkAccessibilityPermissions() else {
            return false
        }
        
        // Install event handler
        var eventType = EventTypeSpec(eventClass: OSType(kEventClassKeyboard), eventKind: UInt32(kEventHotKeyPressed))
        let status = InstallEventHandler(
            GetApplicationEventTarget(),
            { (_, event, userData) -> OSStatus in
                guard let userData = userData else { return OSStatus(eventNotHandledErr) }
                let manager = Unmanaged<HotkeyManager>.fromOpaque(userData).takeUnretainedValue()
                
                var eventID = EventHotKeyID()
                GetEventParameter(
                    event,
                    EventParamName(kEventParamDirectObject),
                    EventParamType(typeEventHotKeyID),
                    nil,
                    MemoryLayout<EventHotKeyID>.size,
                    nil,
                    &eventID
                )
                
                if eventID.id == manager.hotkeyID.id {
                    DispatchQueue.main.async {
                        manager.onHotkeyPressed?()
                    }
                    return noErr
                }
                
                return OSStatus(eventNotHandledErr)
            },
            1,
            &eventType,
            Unmanaged.passUnretained(self).toOpaque(),
            &eventHandler
        )
        
        guard status == noErr else {
            print("Failed to install event handler: \(status)")
            return false
        }
        
        // Register the hotkey
        let registerStatus = RegisterEventHotKey(
            keyCode,
            modifiers,
            hotkeyID,
            GetApplicationEventTarget(),
            0,
            &hotKeyRef
        )
        
        guard registerStatus == noErr else {
            print("Failed to register hotkey: \(registerStatus)")
            return false
        }
        
        return true
    }
    
    func unregisterHotkey() {
        if let hotKeyRef = hotKeyRef {
            UnregisterEventHotKey(hotKeyRef)
            self.hotKeyRef = nil
        }
        
        if let eventHandler = eventHandler {
            RemoveEventHandler(eventHandler)
            self.eventHandler = nil
        }
    }
    
    nonisolated func checkAccessibilityPermissions() -> Bool {
        // Access C API global - safe as it's a constant
        let promptKey = kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String
        let options = [promptKey: true]
        return AXIsProcessTrustedWithOptions(options as CFDictionary)
    }
    
    nonisolated func isPermissionGranted() -> Bool {
        return AXIsProcessTrusted()
    }
    
    deinit {
        // Clean up resources - skip in deinit due to concurrency restrictions
        // Resources will be cleaned up when app terminates
    }
}
