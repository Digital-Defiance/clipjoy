import SwiftUI
import AppKit

/// Extended preview support for rich text and images
struct ContentPreviewView: View {
    let content: ClipboardContent
    @Environment(AppSettings.self) private var settings
    
    var body: some View {
        switch content {
        case .text(let string):
            Text(string)
                .lineLimit(3)
                .textSelection(.enabled)
            
        case .richText(let attributed):
            if settings.showPreviewImages {
                RichTextPreview(attributedString: attributed)
            } else {
                Text(attributed.string)
                    .lineLimit(3)
                    .textSelection(.enabled)
            }
            
        case .image(let nsImage):
            if settings.showPreviewImages {
                Image(nsImage: nsImage)
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .frame(maxHeight: settings.maxImagePreviewHeight)
                    .cornerRadius(8)
            } else {
                Label("Image", systemImage: "photo")
            }
            
        case .url(let url, let title):
            VStack(alignment: .leading, spacing: 4) {
                if let title = title {
                    Text(title)
                        .font(.body)
                        .fontWeight(.medium)
                }
                Text(url.absoluteString)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
            }
            
        case .fileURLs(let urls):
            VStack(alignment: .leading, spacing: 4) {
                ForEach(urls.prefix(3), id: \.self) { url in
                    HStack {
                        Image(systemName: "doc")
                        Text(url.lastPathComponent)
                            .lineLimit(1)
                    }
                    .font(.caption)
                }
                if urls.count > 3 {
                    Text("and \(urls.count - 3) more...")
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                }
            }
            
        case .unknown:
            Text("Unknown content type")
                .foregroundStyle(.secondary)
        }
    }
}

struct RichTextPreview: NSViewRepresentable {
    let attributedString: NSAttributedString
    
    func makeNSView(context: Context) -> NSTextView {
        let textView = NSTextView()
        textView.isEditable = false
        textView.isSelectable = true
        textView.backgroundColor = .clear
        textView.textContainerInset = NSSize(width: 0, height: 0)
        textView.textContainer?.lineFragmentPadding = 0
        textView.textContainer?.maximumNumberOfLines = 3
        textView.textContainer?.lineBreakMode = .byTruncatingTail
        return textView
    }
    
    func updateNSView(_ nsView: NSTextView, context: Context) {
        nsView.textStorage?.setAttributedString(attributedString)
    }
}
