import Foundation
import AppKit

/// Service to fetch URL metadata for preview
actor URLMetadataFetcher {
    static let shared = URLMetadataFetcher()
    
    private var cache: [URL: String] = [:]
    
    private init() {}
    
    func fetchTitle(for url: URL) async -> String? {
        // Check cache first
        if let cached = cache[url] {
            return cached
        }
        
        // Fetch HTML and parse title
        guard url.scheme == "http" || url.scheme == "https" else {
            return nil
        }
        
        do {
            let (data, _) = try await URLSession.shared.data(from: url)
            if let html = String(data: data, encoding: .utf8) {
                let title = extractTitle(from: html)
                cache[url] = title
                return title
            }
        } catch {
            print("Failed to fetch URL metadata: \(error)")
        }
        
        return nil
    }
    
    private func extractTitle(from html: String) -> String? {
        // Simple regex to extract <title> tag
        let pattern = "<title>([^<]+)</title>"
        if let regex = try? NSRegularExpression(pattern: pattern, options: .caseInsensitive) {
            let nsString = html as NSString
            if let match = regex.firstMatch(in: html, range: NSRange(location: 0, length: nsString.length)) {
                if match.numberOfRanges > 1 {
                    let titleRange = match.range(at: 1)
                    return nsString.substring(with: titleRange)
                        .trimmingCharacters(in: .whitespacesAndNewlines)
                }
            }
        }
        return nil
    }
}

extension ClipboardMonitor {
    /// Enhanced clipboard reading with URL metadata
    func readClipboardContentWithMetadata() async -> ClipboardContent? {
        guard let content = readClipboardContent() else { return nil }
        
        // If it's a URL, fetch the title
        if case .url(let url, _) = content {
            if let title = await URLMetadataFetcher.shared.fetchTitle(for: url) {
                return .url(url, title: title)
            }
        }
        
        return content
    }
}
