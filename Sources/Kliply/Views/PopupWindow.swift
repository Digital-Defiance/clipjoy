import SwiftUI

struct PopupWindow: View {
    @Environment(AppState.self) private var appState
    @FocusState private var isSearchFocused: Bool
    
    var body: some View {
        VStack(spacing: 0) {
            // Header with search and filters
            VStack(spacing: 12) {
                // Title bar with close button
                HStack {
                    Text("Clipboard History")
                        .font(.headline)
                    Spacer()
                    Button(action: { appState.isPopupVisible = false }) {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundStyle(.secondary)
                            .font(.title3)
                    }
                    .buttonStyle(.plain)
                }
                
                // Search bar
                HStack {
                    Image(systemName: "magnifyingglass")
                        .foregroundStyle(.secondary)
                    TextField("Search clipboard...", text: Binding(
                        get: { appState.searchQuery },
                        set: { appState.searchQuery = $0 }
                    ))
                    .textFieldStyle(.plain)
                    .focused($isSearchFocused)
                    
                    if !appState.searchQuery.isEmpty {
                        Button(action: { appState.searchQuery = "" }) {
                            Image(systemName: "xmark.circle.fill")
                                .foregroundStyle(.secondary)
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(8)
                .background(Color(nsColor: .controlBackgroundColor))
                .cornerRadius(8)
                
                // Filter pills
                HStack(spacing: 8) {
                    ForEach(ContentFilter.allCases, id: \.self) { filter in
                        FilterPill(
                            title: filter.rawValue,
                            isSelected: appState.selectedFilter == filter,
                            action: { appState.selectedFilter = filter }
                        )
                    }
                    
                    Spacer()
                    
                    Button(action: { appState.clearHistory() }) {
                        Label("Clear", systemImage: "trash")
                            .font(.caption)
                    }
                    .buttonStyle(.plain)
                    .foregroundStyle(.red)
                }
            }
            .padding()
            
            Divider()
            
            // History list
            if appState.filteredHistory.isEmpty {
                EmptyHistoryView()
            } else {
                ScrollView {
                    LazyVStack(spacing: 0) {
                        ForEach(Array(appState.filteredHistory.enumerated()), id: \.element.id) { index, item in
                            ClipboardItemRow(
                                item: item,
                                isSelected: appState.selectedItemIndex == index,
                                action: { appState.selectItem(at: index) },
                                onDelete: { appState.removeItem(at: index) }
                            )
                            
                            if index < appState.filteredHistory.count - 1 {
                                Divider()
                            }
                        }
                    }
                }
            }
            
            Divider()
            
            // Footer with shortcuts
            HStack {
                KeyboardShortcutHint(key: "↑↓", description: "Navigate")
                Spacer()
                KeyboardShortcutHint(key: "↩", description: "Select")
                Spacer()
                KeyboardShortcutHint(key: "⇧↩", description: "Alt Format")
                Spacer()
                KeyboardShortcutHint(key: "⌘,", description: "Settings")
                Spacer()
                KeyboardShortcutHint(key: "⎋", description: "Close")
            }
            .padding(.horizontal)
            .padding(.vertical, 8)
            .background(Color(nsColor: .controlBackgroundColor).opacity(0.5))
        }
        .frame(width: 600, height: 500)
        .background(Color(nsColor: .windowBackgroundColor))
        .focusable()
        .onKeyPress(.escape) {
            appState.isPopupVisible = false
            return .handled
        }
        .onAppear {
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                isSearchFocused = true
            }
        }
    }
}

struct FilterPill: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.caption)
                .padding(.horizontal, 12)
                .padding(.vertical, 4)
                .background(isSelected ? Color.accentColor : Color(nsColor: .controlBackgroundColor))
                .foregroundStyle(isSelected ? .white : .primary)
                .cornerRadius(12)
        }
        .buttonStyle(.plain)
    }
}

struct ClipboardItemRow: View {
    let item: ClipboardItem
    let isSelected: Bool
    let action: () -> Void
    let onDelete: () -> Void
    
    var body: some View {
        HStack(spacing: 12) {
            // Type icon
            Image(systemName: iconName)
                .font(.title3)
                .foregroundStyle(.secondary)
                .frame(width: 30)
            
            // Content preview
            VStack(alignment: .leading, spacing: 4) {
                Text(item.content.previewText)
                    .lineLimit(3)
                    .font(.body)
                
                HStack {
                    Text(item.content.displayType)
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                    
                    Text("•")
                        .foregroundStyle(.secondary)
                    
                    Text(relativeTime(from: item.timestamp))
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                }
            }
            
            Spacer()
            
            // Delete button
            Button(action: onDelete) {
                Image(systemName: "xmark.circle.fill")
                    .foregroundStyle(.secondary)
            }
            .buttonStyle(.plain)
            .opacity(isSelected ? 1 : 0)
        }
        .padding(.horizontal)
        .padding(.vertical, 12)
        .background(isSelected ? Color.accentColor.opacity(0.2) : Color.clear)
        .contentShape(Rectangle())
        .onTapGesture(perform: action)
    }
    
    private var iconName: String {
        switch item.content {
        case .text: return "doc.text"
        case .richText: return "doc.richtext"
        case .image: return "photo"
        case .url: return "link"
        case .fileURLs: return "doc.on.doc"
        case .unknown: return "questionmark.circle"
        }
    }
    
    private func relativeTime(from date: Date) -> String {
        let seconds = Date.now.timeIntervalSince(date)
        
        if seconds < 60 {
            return "Just now"
        } else if seconds < 3600 {
            let minutes = Int(seconds / 60)
            return "\(minutes)m ago"
        } else if seconds < 86400 {
            let hours = Int(seconds / 3600)
            return "\(hours)h ago"
        } else {
            let days = Int(seconds / 86400)
            return "\(days)d ago"
        }
    }
}

struct EmptyHistoryView: View {
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "clipboard")
                .font(.system(size: 60))
                .foregroundStyle(.secondary)
            
            Text("No Clipboard History")
                .font(.title2)
                .fontWeight(.semibold)
            
            Text("Copy something to get started")
                .font(.body)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

struct KeyboardShortcutHint: View {
    let key: String
    let description: String
    
    var body: some View {
        HStack(spacing: 4) {
            Text(key)
                .font(.caption)
                .fontWeight(.medium)
                .padding(.horizontal, 6)
                .padding(.vertical, 2)
                .background(Color(nsColor: .controlBackgroundColor))
                .cornerRadius(4)
            
            Text(description)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
    }
}

#Preview {
    @Previewable @State var appState = AppState.shared
    PopupWindow()
        .environment(appState)
}
