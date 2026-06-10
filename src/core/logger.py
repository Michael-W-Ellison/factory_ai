"""
Logging Infrastructure - Centralized logging configuration for the game.

Provides:
- Configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Console and file logging handlers
- Named loggers for different modules
- Integration with game settings
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional


# Default log format
DEFAULT_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
SIMPLE_FORMAT = '%(levelname)s: %(message)s'
DEBUG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'

# Log level mapping
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}

# Global state
_initialized = False
_log_file_path: Optional[str] = None


def setup_logging(
    level: str = 'INFO',
    log_file: Optional[str] = None,
    log_dir: str = 'data/logs',
    console: bool = True,
    debug_format: bool = False
) -> None:
    """
    Configure application-wide logging.

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file name. If None, no file logging.
        log_dir: Directory for log files
        console: Whether to output to console
        debug_format: Whether to use detailed debug format with line numbers
    """
    global _initialized, _log_file_path

    # Get numeric log level
    numeric_level = LOG_LEVELS.get(level.upper(), logging.INFO)

    # Choose format
    if debug_format or numeric_level == logging.DEBUG:
        log_format = DEBUG_FORMAT
    else:
        log_format = DEFAULT_FORMAT

    # Create formatter
    formatter = logging.Formatter(log_format)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear existing handlers (avoid duplicates on re-initialization)
    root_logger.handlers.clear()

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File handler
    if log_file:
        try:
            # Ensure log directory exists
            os.makedirs(log_dir, exist_ok=True)

            # Add timestamp to log file name if not already present
            if not any(c in log_file for c in ['%', '{', '}']):
                base, ext = os.path.splitext(log_file)
                if not ext:
                    ext = '.log'
                timestamp = datetime.now().strftime('%Y%m%d')
                log_file = f"{base}_{timestamp}{ext}"

            _log_file_path = os.path.join(log_dir, log_file)

            file_handler = logging.FileHandler(_log_file_path, encoding='utf-8')
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        except Exception as e:
            # Fall back to console-only logging if file fails
            print(f"Warning: Could not create log file: {e}")
            _log_file_path = None

    _initialized = True


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger for a specific module.

    Args:
        name: Logger name (typically __name__ of the calling module)

    Returns:
        Configured logger instance
    """
    if not _initialized:
        # Auto-initialize with defaults if not explicitly configured
        setup_logging()

    return logging.getLogger(name)


def set_level(level: str, logger_name: Optional[str] = None) -> None:
    """
    Change log level at runtime.

    Args:
        level: New log level string
        logger_name: Optional specific logger name, or None for root logger
    """
    numeric_level = LOG_LEVELS.get(level.upper(), logging.INFO)

    if logger_name:
        logger = logging.getLogger(logger_name)
    else:
        logger = logging.getLogger()

    logger.setLevel(numeric_level)

    # Update handler levels too
    for handler in logger.handlers:
        handler.setLevel(numeric_level)


def get_log_file_path() -> Optional[str]:
    """Get the current log file path, if file logging is enabled."""
    return _log_file_path


def is_initialized() -> bool:
    """Check if logging has been initialized."""
    return _initialized


class LoggerMixin:
    """
    Mixin class to add logging capability to any class.

    Usage:
        class MyClass(LoggerMixin):
            def __init__(self):
                self.log.info("MyClass initialized")
    """

    @property
    def log(self) -> logging.Logger:
        """Get logger for this class."""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger


# Convenience functions for quick logging without getting a logger first
def debug(msg: str, *args, **kwargs) -> None:
    """Log a debug message."""
    get_logger('game').debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs) -> None:
    """Log an info message."""
    get_logger('game').info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs) -> None:
    """Log a warning message."""
    get_logger('game').warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs) -> None:
    """Log an error message."""
    get_logger('game').error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs) -> None:
    """Log a critical message."""
    get_logger('game').critical(msg, *args, **kwargs)


def exception(msg: str, *args, **kwargs) -> None:
    """Log an exception with traceback."""
    get_logger('game').exception(msg, *args, **kwargs)
