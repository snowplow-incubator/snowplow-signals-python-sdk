"""Logging configuration for Snowplow Signals SDK"""

import logging
import sys
from typing import Optional, cast

# Define custom log levels
SUCCESS = 25
logging.addLevelName(SUCCESS, "SUCCESS")


class SnowplowLogger(logging.Logger):
    """Custom logger with success level support"""

    def success(self, msg, *args, **kwargs):
        """Log a success message"""
        if self.isEnabledFor(SUCCESS):
            self._log(SUCCESS, msg, args, **kwargs)


# Replace the default logger class
logging.setLoggerClass(SnowplowLogger)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging level and format with consistent styling.

    Args:
        verbose: Whether to enable verbose logging (INFO level) or minimal logging (WARNING level)
    """
    # Set root logger to INFO level to capture all messages
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Create a formatter
    formatter = logging.Formatter("%(message)s")  # Simplified format for cleaner output

    # Configure console handler with appropriate level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    # Set level to SUCCESS for non-verbose mode to show success messages
    console_handler.setLevel(SUCCESS if not verbose else logging.INFO)

    # Add handler to root logger
    root_logger.addHandler(console_handler)

    # Always suppress HTTP request logs
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("http.client").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: Optional[str] = None) -> SnowplowLogger:
    """Get a logger instance with success level support.

    Args:
        name: Optional name for the logger. If None, returns the root logger.

    Returns:
        SnowplowLogger: Logger instance with success level support
    """
    return cast(SnowplowLogger, logging.getLogger(name))
