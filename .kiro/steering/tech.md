# Technology Stack

## Language & Runtime

- **Python 3.9+** (use `python3` and `pip3` commands)
- **Virtual Environment**: Always use venv for dependency isolation

## Core Dependencies

- **PyQt6 >= 6.6.0**: UI framework and Qt bindings
- **pynput >= 1.7.6**: Global hotkey handling and keyboard monitoring

## Testing Stack

- **pytest >= 7.4.0**: Test runner and framework
- **pytest-qt >= 4.2.0**: PyQt6 testing utilities
- **pytest-mock >= 3.12.0**: Mocking support
- **hypothesis >= 6.92.0**: Property-based testing
- **coverage >= 7.3.0**: Code coverage analysis

## Setup Commands

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt

# Install in development mode
pip3 install -e .

# Install with dev dependencies
pip3 install -e ".[dev]"
```

## Common Commands

```bash
# Run all tests
pytest

# Run specific test categories
python3 -m pytest -m unit          # Unit tests only
python3 -m pytest -m property      # Property-based tests only
python3 -m pytest -m integration   # Integration tests only

# Run with coverage
python3 -m pytest --cov=src/Kliply --cov-report=html

# Hypothesis profiles for property tests
python3 -m pytest --hypothesis-profile=dev    # 10 examples (fast)
python3 -m pytest --hypothesis-profile=default # 100 examples (standard)
python3 -m pytest --hypothesis-profile=ci     # 1000 examples (thorough)
```

## Platform Requirements

- **macOS only**: Native clipboard and Accessibility API integration
- **Accessibility permissions**: Required for global hotkey functionality

## Code Quality

- Use type hints where appropriate
- Follow dataclass patterns for models (see `models.py`)
- Property-based tests use Hypothesis strategies
- All tests must be marked with appropriate pytest markers (unit, property, integration, ui)
