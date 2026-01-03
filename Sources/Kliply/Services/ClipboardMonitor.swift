import Foundation
import AppKit

/// Monitors the system clipboard for changes
@Observable
@MainActor
class ClipboardMonitor {
    private var timer: Timer?
    private var lastChangeCount: Int = 0
    private let pasteboard = NSPasteboard.general
    
    var onClipboardChange: ((ClipboardContent?) -> Void)?
    
    init() {
        lastChangeCount = pasteboard.changeCount
    }
    
    func startMonitoring() {
        timer = Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { [weak self] _ in
            Task { @MainActor [weak self] in
                self?.checkClipboard()
            }
        }
    }
    
    func stopMonitoring() {
        timer?.invalidate()
        timer = nil
    }
    
    private func checkClipboard() {
        guard pasteboard.changeCount != lastChangeCount else { return }
        lastChangeCount = pasteboard.changeCount
        
        let content = readClipboardContent()
        onClipboardChange?(content)
    }
    
    func readClipboardContent() -> ClipboardContent? {
        // Check for file URLs first
        if let fileURLs = pasteboard.readObjects(forClasses: [NSURL.self], options: nil) as? [URL],
           !fileURLs.isEmpty {
            return .fileURLs(fileURLs)
        }
        
        // Check for images
        if let image = NSImage(pasteboard: pasteboard) {
            return .image(image)
        }
        
        // Check for URLs
        if let urlString = pasteboard.string(forType: .string),
           let url = URL(string: urlString),
           (url.scheme == "http" || url.scheme == "https") {
            return .url(url, title: nil) // Title will be fetched later if needed
        }
        
        // Check for rich text
        if let rtfData = pasteboard.data(forType: .rtf),
           let attributedString = NSAttributedString(rtf: rtfData, documentAttributes: nil) {
            return .richText(attributedString)
        }
        
        // Check for HTML
        if let htmlData = pasteboard.data(forType: .html),
           let attributedString = NSAttributedString(html: htmlData, documentAttributes: nil) {
            return .richText(attributedString)
        }
        
        // Check for plain text
        if let string = pasteboard.string(forType: .string), !string.isEmpty {
            return .text(string)
        }
        
        return nil
    }
    
    func writeToClipboard(_ content: ClipboardContent) {
        pasteboard.clearContents()
        
        switch content {
        case .text(let string):
            pasteboard.setString(string, forType: .string)
            
        case .richText(let attributedString):
            if let rtfData = attributedString.rtf(from: NSRange(location: 0, length: attributedString.length)) {
                pasteboard.setData(rtfData, forType: .rtf)
            }
            pasteboard.setString(attributedString.string, forType: .string)
            
        case .image(let image):
            pasteboard.writeObjects([image])
            
        case .url(let url, _):
            pasteboard.setString(url.absoluteString, forType: .string)
            
        case .fileURLs(let urls):
            pasteboard.writeObjects(urls as [NSURL])
            
        case .unknown:
            break
        }
        
        lastChangeCount = pasteboard.changeCount
    }
}
