"""
Basic setup verification tests.
"""

import pytest
from hypothesis import given, strategies as st


def test_pytest_working():
    """Verify pytest is working correctly."""
    assert True


@pytest.mark.property
@given(st.integers())
def test_hypothesis_working(x):
    """Verify Hypothesis is working correctly."""
    assert isinstance(x, int)


def test_imports():
    """Verify core imports are available."""
    import PyQt6
    import PyQt6.QtCore
    import PyQt6.QtWidgets
    assert PyQt6 is not None
