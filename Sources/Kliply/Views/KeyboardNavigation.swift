import SwiftUI

/// Handles keyboard navigation in the popup window
struct KeyboardNavigationModifier: ViewModifier {
    @Environment(AppState.self) private var appState
    let onEscape: () -> Void
    @State private var isShiftPressed = false
    
    func body(content: Content) -> some View {
        content
            .onKeyPress(.upArrow) {
                if !appState.filteredHistory.isEmpty {
                    appState.selectedItemIndex = max(0, appState.selectedItemIndex - 1)
                }
                return .handled
            }
            .onKeyPress(.downArrow) {
                if !appState.filteredHistory.isEmpty {
                    appState.selectedItemIndex = min(appState.filteredHistory.count - 1, appState.selectedItemIndex + 1)
                }
                return .handled
            }
            .onKeyPress(.return) {
                if isShiftPressed {
                    // Shift+Enter: Alternative format (plain text)
                    selectItemWithAlternateFormat()
                } else {
                    // Enter: Select normally
                    if !appState.filteredHistory.isEmpty {
                        appState.selectItem(at: appState.selectedItemIndex)
                    }
                }
                return .handled
            }
            .onKeyPress(.escape) {
                onEscape()
                return .handled
            }
            .onKeyPress(.tab) {
                cycleFilter()
                return .handled
            }
            .onKeyPress(.delete) {
                if !appState.filteredHistory.isEmpty && !appState.searchQuery.isEmpty {
                    // Only allow delete if not typing in search
                    return .ignored
                }
                if !appState.filteredHistory.isEmpty {
                    appState.removeItem(at: appState.selectedItemIndex)
                }
                return .handled
            }
    }
    
    private func selectItemWithAlternateFormat() {
        guard !appState.filteredHistory.isEmpty else { return }
        let item = appState.filteredHistory[appState.selectedItemIndex]
        
        // Create plain text version if it's rich text
        let plainContent: ClipboardContent
        switch item.content {
        case .richText(let attributed):
            plainContent = .text(attributed.string)
        case .text(let str):
            plainContent = .text(str)
        default:
            // For non-text items, just use the original
            appState.selectItem(at: appState.selectedItemIndex)
            return
        }
        
        // Write plain text version
        let clipboardMonitor = ClipboardMonitor()
        clipboardMonitor.writeToClipboard(plainContent)
        
        appState.isPopupVisible = false
        
        // Simulate paste
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            let source = CGEventSource(stateID: .hidSystemState)
            let keyVDown = CGEvent(keyboardEventSource: source, virtualKey: 0x09, keyDown: true)
            keyVDown?.flags = .maskCommand
            keyVDown?.post(tap: .cghidEventTap)
            
            let keyVUp = CGEvent(keyboardEventSource: source, virtualKey: 0x09, keyDown: false)
            keyVUp?.flags = .maskCommand
            keyVUp?.post(tap: .cghidEventTap)
        }
    }
    
    private func cycleFilter() {
        let filters = ContentFilter.allCases
        if let currentIndex = filters.firstIndex(of: appState.selectedFilter) {
            let nextIndex = (currentIndex + 1) % filters.count
            appState.selectedFilter = filters[nextIndex]
        }
    }
}

extension View {
    func handleKeyboardNavigation(onEscape: @escaping () -> Void) -> some View {
        modifier(KeyboardNavigationModifier(onEscape: onEscape))
    }
}
