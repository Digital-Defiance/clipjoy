"""
Kliply - Professional macOS Clipboard Manager
"""

from setuptools import setup, find_packages
import sys

# py2app configuration for macOS application bundle
APP = ['src/Kliply/main_application.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'resources/icon.icns',
    'plist': {
        'CFBundleName': 'Kliply',
        'CFBundleDisplayName': 'Kliply',
        'CFBundleIdentifier': 'com.Kliply.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleExecutable': 'Kliply',
        'CFBundleIconFile': 'icon.icns',
        'LSMinimumSystemVersion': '10.15.0',
        'LSUIElement': True,  # Hide from Dock
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'NSHumanReadableCopyright': 'Copyright © 2026 Kliply Team',
        # Privacy usage descriptions
        'NSAccessibilityUsageDescription': 'Kliply needs Accessibility permissions to register global keyboard shortcuts (Cmd+Shift+V) so you can quickly access your clipboard history from any application.',
    },
    'packages': ['PyQt6', 'Kliply', 'pynput'],
    'includes': [
        'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', 'PyQt6.QtSvg',
        'pynput.keyboard', 'pynput.keyboard._darwin',
        'pynput.mouse', 'pynput.mouse._darwin',
        'pynput._util', 'pynput._util.darwin',
    ],
    'excludes': ['tkinter', 'matplotlib', 'numpy', 'scipy'],
    'strip': False,  # Disable stripping to avoid permission errors on case-sensitive filesystems
    'optimize': 2,
}

# Base setup configuration
setup_kwargs = {
    "name": "Kliply",
    "version": "1.0.0",
    "description": "Professional macOS clipboard manager with Windows 11-style functionality",
    "author": "Kliply Team",
    "python_requires": ">=3.9",
    "packages": find_packages(where="src"),
    "package_dir": {"": "src"},
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
}

# Add py2app specific options when building
if 'py2app' in sys.argv:
    setup_kwargs['app'] = APP
    setup_kwargs['data_files'] = DATA_FILES
    setup_kwargs['options'] = {'py2app': OPTIONS}
    setup_kwargs['setup_requires'] = ['py2app']
else:
    # Only include these when NOT building with py2app
    setup_kwargs['install_requires'] = [
        "PyQt6>=6.6.0",
    ]
    setup_kwargs['extras_require'] = {
        "dev": [
            "pytest>=7.4.0",
            "pytest-qt>=4.2.0",
            "pytest-mock>=3.12.0",
            "hypothesis>=6.92.0",
            "coverage>=7.3.0",
        ],
        "build": [
            "py2app>=0.28.0",
        ],
    }
    setup_kwargs['entry_points'] = {
        "console_scripts": [
            "Kliply=Kliply.main_application:main",
        ],
    }

setup(**setup_kwargs)
