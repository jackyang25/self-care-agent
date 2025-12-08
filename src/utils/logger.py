"""logger configuration for docker-friendly logging."""

import logging
import sys
from typing import Optional

_logger: Optional[logging.Logger] = None


def get_logger(name: str = "app") -> logging.Logger:
    """get or create logger instance."""
    global _logger

    if _logger is None:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        # prevent duplicate handlers
        if logger.handlers:
            return logger

        # create console handler with docker-friendly format
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)

        # format: timestamp, level, name, message
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        _logger = logger

    return _logger
