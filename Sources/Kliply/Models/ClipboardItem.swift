import Foundation
import AppKit

/// Represents a single clipboard entry
struct ClipboardItem: Identifiable, Equatable {
    let id: UUID
    let timestamp: Date
    let content: ClipboardContent
    
    init(id: UUID = UUID(), timestamp: Date = Date(), content: ClipboardContent) {
        self.id = id
        self.timestamp = timestamp
        self.content = content
    }
    
    static func == (lhs: ClipboardItem, rhs: ClipboardItem) -> Bool {
        lhs.content == rhs.content
    }
}

/// Different types of clipboard content
enum ClipboardContent: Equatable {
    case text(String)
    case richText(NSAttributedString)
    case image(NSImage)
    case url(URL, title: String?)
    case fileURLs([URL])
    case unknown
    
    static func == (lhs: ClipboardContent, rhs: ClipboardContent) -> Bool {
        switch (lhs, rhs) {
        case (.text(let a), .text(let b)):
            return a == b
        case (.richText(let a), .richText(let b)):
            return a.isEqual(to: b)
        case (.image(let a), .image(let b)):
            return a.tiffRepresentation == b.tiffRepresentation
        case (.url(let a, let titleA), .url(let b, let titleB)):
            return a == b && titleA == titleB
        case (.fileURLs(let a), .fileURLs(let b)):
            return a == b
        case (.unknown, .unknown):
            return true
        default:
            return false
        }
    }
    
    var displayType: String {
        switch self {
        case .text: return "Text"
        case .richText: return "Rich Text"
        case .image: return "Image"
        case .url: return "URL"
        case .fileURLs: return "Files"
        case .unknown: return "Unknown"
        }
    }
    
    /// Get a preview string for display
    var previewText: String {
        switch self {
        case .text(let str):
            return str.trimmingCharacters(in: .whitespacesAndNewlines)
        case .richText(let attr):
            return attr.string.trimmingCharacters(in: .whitespacesAndNewlines)
        case .image:
            return "[Image]"
        case .url(let url, let title):
            return title ?? url.absoluteString
        case .fileURLs(let urls):
            if urls.count == 1 {
                return urls[0].lastPathComponent
            } else {
                return "\(urls.count) files"
            }
        case .unknown:
            return "[Unknown content]"
        }
    }
}
