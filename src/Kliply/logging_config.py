"""
Logging configuration for Kliply clipboard manager.

This module sets up comprehensive logging with both file and console handlers.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional


# Default log file location
DEFAULT_LOG_DIR = Path.home() / ".Kliply" / "logs"
DEFAULT_LOG_FILE = "Kliply.log"

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    log_level: int = logging.INFO,
    log_dir: Optional[Path] = None,
    log_file: Optional[str] = None,
    console_output: bool = True
) -> None:
    """
    Set up logging configuration with file and console handlers.
    
    This function configures the root logger with:
    - File handler with rotation (10MB max, 5 backup files)
    - Console handler (optional)
    - Consistent formatting across all handlers
    
    Args:
        log_level: Logging level (default: logging.INFO)
        log_dir: Directory for log files (default: ~/.Kliply/logs)
        log_file: Log file name (default: Kliply.log)
        console_output: Whether to output logs to console (default: True)
    """
    # Use defaults if not provided
    if log_dir is None:
        log_dir = DEFAULT_LOG_DIR
    if log_file is None:
        log_file = DEFAULT_LOG_FILE
    
    # Create log directory if it doesn't exist
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create log directory {log_dir}: {e}")
        # Fall back to current directory
        log_dir = Path(".")
    
    # Full path to log file
    log_path = log_dir / log_file
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    
    # File handler with rotation
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create file handler: {e}")
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Log initial message
    logging.info("Logging initialized")
    logging.info(f"Log file: {log_path}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (typically __name__ of the module)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
