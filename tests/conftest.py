"""
Pytest configuration and shared fixtures for Kliply tests.
"""

import pytest
from hypothesis import settings, Verbosity

# Configure Hypothesis for property-based testing
settings.register_profile("default", max_examples=100, verbosity=Verbosity.normal)
settings.register_profile("ci", max_examples=1000, verbosity=Verbosity.verbose)
settings.register_profile("dev", max_examples=10, verbosity=Verbosity.verbose)

# Load the default profile
settings.load_profile("default")


@pytest.fixture(autouse=True)
def clear_clipboard():
    """
    Automatically clear the clipboard before and after each test.
    This prevents test pollution from clipboard state.
    """
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QMimeData
    import time
    
    # Ensure QApplication exists
    app = QApplication.instance()
    if app is not None:
        clipboard = app.clipboard()
        # Clear by setting empty mime data
        empty_mime = QMimeData()
        clipboard.setMimeData(empty_mime)
        # Process events multiple times to ensure clipboard is cleared
        for _ in range(5):
            app.processEvents()
        time.sleep(0.01)  # Small delay to ensure clipboard is cleared
    
    yield
    
    # Clear after test
    app = QApplication.instance()
    if app is not None:
        clipboard = app.clipboard()
        empty_mime = QMimeData()
        clipboard.setMimeData(empty_mime)
        for _ in range(5):
            app.processEvents()


@pytest.fixture
def qapp(qapp):
    """
    Fixture that provides a QApplication instance for Qt tests.
    This extends pytest-qt's qapp fixture.
    """
    return qapp
