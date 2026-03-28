import logging
import os

from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logger(
    level: str | int = "INFO",
    log_file: Optional[Path] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    json_format: bool = False,
) -> logging.Logger:
    """
    Setup logger.

    Args:
        name: Logger name (usually __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging output
        max_bytes: Max file size before rotation
        backup_count: Number of rotated files to keep
        json_format: Enable JSON log formatting

    Returns:
        Configured logger instance
    """

    # Allow environment override
    env_level = os.getenv("LOG_LEVEL")
    if env_level:
        level = env_level

    logger = logging.getLogger()

    # Prevent duplicate handlers in case of re-import
    if logger.handlers:
        return logger

    logger.setLevel(level if isinstance(level, int) else level.upper())
    logger.propagate = False  # Avoid double logging via root

    # ---- Formatter ----
    if json_format:
        formatter = logging.Formatter(
            '{"time": "%(asctime)s", '
            '"level": "%(levelname)s", '
            '"name": "%(name)s", '
            '"message": "%(message)s"}'
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # ---- Console Handler ----
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ---- File Handler (Optional) ----
    if log_file:
        # Create parent of log file if not exists
        log_file.parent.mkdir(exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
