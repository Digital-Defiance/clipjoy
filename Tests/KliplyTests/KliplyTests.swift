import XCTest
@testable import Kliply

@MainActor
final class ClipboardItemTests: XCTestCase {
    
    func testTextContentEquality() {
        let content1 = ClipboardContent.text("Hello, World!")
        let content2 = ClipboardContent.text("Hello, World!")
        let content3 = ClipboardContent.text("Different text")
        
        XCTAssertEqual(content1, content2)
        XCTAssertNotEqual(content1, content3)
    }
    
    func testClipboardItemEquality() {
        let content = ClipboardContent.text("Test")
        let item1 = ClipboardItem(id: UUID(), content: content)
        let item2 = ClipboardItem(id: UUID(), content: content)
        
        // Items should be equal based on content, not ID
        XCTAssertEqual(item1, item2)
    }
    
    func testDisplayType() {
        XCTAssertEqual(ClipboardContent.text("test").displayType, "Text")
        XCTAssertEqual(ClipboardContent.richText(NSAttributedString(string: "test")).displayType, "Rich Text")
        XCTAssertEqual(ClipboardContent.url(URL(string: "https://example.com")!, title: nil).displayType, "URL")
    }
    
    func testPreviewText() {
        let textContent = ClipboardContent.text("  Hello  \n")
        XCTAssertEqual(textContent.previewText, "Hello")
        
        let urlContent = ClipboardContent.url(URL(string: "https://example.com")!, title: "Example")
        XCTAssertEqual(urlContent.previewText, "Example")
        
        let urlContentNoTitle = ClipboardContent.url(URL(string: "https://example.com")!, title: nil)
        XCTAssertEqual(urlContentNoTitle.previewText, "https://example.com")
    }
    
    func testFileURLsPreview() {
        let urls = [
            URL(fileURLWithPath: "/path/to/file1.txt"),
            URL(fileURLWithPath: "/path/to/file2.txt")
        ]
        let content = ClipboardContent.fileURLs(urls)
        XCTAssertEqual(content.previewText, "2 files")
        
        let singleURL = [URL(fileURLWithPath: "/path/to/file.txt")]
        let singleContent = ClipboardContent.fileURLs(singleURL)
        XCTAssertEqual(singleContent.previewText, "file.txt")
    }
}

@MainActor
final class AppSettingsTests: XCTestCase {
    
    @MainActor
    func testHistoryDepthBounds() {
        let settings = AppSettings.shared
        
        settings.historyDepth = 50
        XCTAssertEqual(settings.historyDepth, 50)
        
        settings.historyDepth = 0
        XCTAssertEqual(settings.historyDepth, 1) // Should clamp to minimum
        
        settings.historyDepth = 150
        XCTAssertEqual(settings.historyDepth, 100) // Should clamp to maximum
    }
    
    @MainActor
    func testHotkeyDescription() {
        let settings = AppSettings.shared
        let description = settings.hotkeyDescription
        
        XCTAssertTrue(description.contains("⌘"))
        XCTAssertTrue(description.contains("⇧"))
        XCTAssertTrue(description.contains("V"))
    }
}

@MainActor
final class AppStateTests: XCTestCase {
    
    func testAddToHistory() {
        let appState = AppState.shared
        appState.clipboardHistory.removeAll()
        
        let content = ClipboardContent.text("Test item")
        appState.addToHistory(content: content)
        
        XCTAssertEqual(appState.clipboardHistory.count, 1)
        XCTAssertEqual(appState.clipboardHistory[0].content, content)
    }
    
    func testSkipConsecutiveDuplicates() {
        let appState = AppState.shared
        appState.clipboardHistory.removeAll()
        
        let content = ClipboardContent.text("Test item")
        appState.addToHistory(content: content)
        appState.addToHistory(content: content) // Duplicate
        
        XCTAssertEqual(appState.clipboardHistory.count, 1)
    }
    
    func testHistoryDepthLimit() {
        let appState = AppState.shared
        let settings = AppSettings.shared
        
        appState.clipboardHistory.removeAll()
        settings.historyDepth = 3
        
        // Add 5 items
        for i in 1...5 {
            appState.addToHistory(content: .text("Item \(i)"))
        }
        
        XCTAssertEqual(appState.clipboardHistory.count, 3)
        XCTAssertEqual(appState.clipboardHistory[0].content, .text("Item 5"))
        XCTAssertEqual(appState.clipboardHistory[2].content, .text("Item 3"))
    }
    
    func testClearHistory() {
        let appState = AppState.shared
        appState.clipboardHistory.removeAll()
        
        appState.addToHistory(content: .text("Item 1"))
        appState.addToHistory(content: .text("Item 2"))
        
        XCTAssertEqual(appState.clipboardHistory.count, 2)
        
        appState.clearHistory()
        
        XCTAssertEqual(appState.clipboardHistory.count, 0)
    }
    
    func testFilteredHistory() {
        let appState = AppState.shared
        appState.clipboardHistory.removeAll()
        
        appState.addToHistory(content: .text("Text item"))
        appState.addToHistory(content: .url(URL(string: "https://example.com")!, title: nil))
        appState.addToHistory(content: .text("Another text"))
        
        // Test text filter
        appState.selectedFilter = .text
        XCTAssertEqual(appState.filteredHistory.count, 2)
        
        // Test URL filter
        appState.selectedFilter = .urls
        XCTAssertEqual(appState.filteredHistory.count, 1)
        
        // Test all filter
        appState.selectedFilter = .all
        XCTAssertEqual(appState.filteredHistory.count, 3)
    }
    
    func testSearchFiltering() {
        let appState = AppState.shared
        appState.clipboardHistory.removeAll()
        
        appState.addToHistory(content: .text("Hello World"))
        appState.addToHistory(content: .text("Goodbye World"))
        appState.addToHistory(content: .text("Something else"))
        
        appState.searchQuery = "World"
        XCTAssertEqual(appState.filteredHistory.count, 2)
        
        appState.searchQuery = "Hello"
        XCTAssertEqual(appState.filteredHistory.count, 1)
        
        appState.searchQuery = ""
        XCTAssertEqual(appState.filteredHistory.count, 3)
    }
}

final class ClipboardMonitorTests: XCTestCase {
    
    @MainActor
    func testReadClipboardContent() {
        let monitor = ClipboardMonitor()
        
        // Test with text
        NSPasteboard.general.clearContents()
        NSPasteboard.general.setString("Test text", forType: .string)
        
        let content = monitor.readClipboardContent()
        
        if case .text(let string) = content {
            XCTAssertEqual(string, "Test text")
        } else {
            XCTFail("Expected text content")
        }
    }
    
    @MainActor
    func testWriteToClipboard() {
        let monitor = ClipboardMonitor()
        
        let content = ClipboardContent.text("Test write")
        monitor.writeToClipboard(content)
        
        let readContent = monitor.readClipboardContent()
        XCTAssertEqual(readContent, content)
    }
    
    @MainActor
    func testURLDetection() {
        let monitor = ClipboardMonitor()
        
        NSPasteboard.general.clearContents()
        NSPasteboard.general.setString("https://example.com", forType: .string)
        
        let content = monitor.readClipboardContent()
        
        if case .url(let url, _) = content {
            XCTAssertEqual(url.absoluteString, "https://example.com")
        } else {
            XCTFail("Expected URL content")
        }
    }
}
