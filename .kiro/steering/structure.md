# Project Structure

## Directory Layout

```
Kliply/
├── src/
│   └── Kliply/              # Main application package
│       ├── __init__.py       # Package exports
│       ├── models.py         # Data models (ClipboardContent, Settings, etc.)
│       ├── clipboard_monitor.py  # Clipboard monitoring
│       ├── history_manager.py    # History storage and management
│       ├── hotkey_handler.py     # Global hotkey handling
│       ├── settings_manager.py   # User preferences
│       └── ui_manager.py         # UI components
├── tests/
│   ├── conftest.py           # Pytest fixtures and configuration
│   ├── unit/                 # Unit tests (mark with @pytest.mark.unit)
│   ├── property/             # Property-based tests (mark with @pytest.mark.property)
│   └── integration/          # Integration tests (mark with @pytest.mark.integration)
├── .kiro/
│   ├── specs/Kliply/        # Specification documents
│   └── steering/             # AI assistant guidance (this file)
├── requirements.txt          # Python dependencies
├── setup.py                  # Package configuration
└── pytest.ini                # Pytest configuration
```

## Module Organization

### Core Models (`models.py`)
- `ContentType`: Enum for clipboard content types (TEXT, IMAGE, RICH_TEXT, UNSUPPORTED)
- `ClipboardContent`: Dataclass representing clipboard items with metadata
- `Settings`: User preferences configuration
- `PermissionStatus`: macOS permission tracking

### Component Responsibilities

- **clipboard_monitor.py**: Polls system clipboard, detects changes, extracts content
- **history_manager.py**: Maintains clipboard history, handles deduplication and depth limits
- **hotkey_handler.py**: Registers and handles global keyboard shortcuts
- **settings_manager.py**: Persists and loads user preferences
- **ui_manager.py**: Popup window and UI rendering

## Testing Conventions

- **Unit tests**: Test individual components in isolation with mocks
- **Property tests**: Use Hypothesis to test invariants across random inputs
- **Integration tests**: Test component interactions
- All tests require `qapp` fixture for PyQt6 components
- Test files mirror source structure: `test_<module_name>.py`

## Import Patterns

```python
# Internal imports use absolute paths from src
from src.Kliply.models import ClipboardContent, ContentType
from src.Kliply.history_manager import HistoryManager

# Package exports defined in __init__.py
from Kliply import ClipboardContent, ContentType
```

## Configuration Files

- **pytest.ini**: Test discovery, markers, Hypothesis profiles
- **setup.py**: Package metadata, dependencies, entry points
- **requirements.txt**: Pinned dependency versions
