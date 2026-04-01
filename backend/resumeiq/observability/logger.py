"""
Logger - Centralized logging configuration.
"""

import logging
import logging.handlers
import os
from typing import Optional

from resumeiq.config.settings import settings


def setup_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up a logger with file and console handlers.

    Args:
        name: Logger name
        log_file: Optional file to log to

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.log_level))

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file or settings.log_file:
        file_path = log_file or settings.log_file
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            file_path, maxBytes=10485760, backupCount=5
        )
        file_handler.setLevel(getattr(logging, settings.log_level))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Create root logger
root_logger = setup_logger("resumeiq")
