"""Loguru integration for Django.

Provides centralized logging setup using Loguru with Django integration.
Loguru logs are automatically coordinated with Django's logging configuration.
"""

import logging
import sys

from loguru import logger

from config.settings.schemas import config_registry as config


def setup_logging() -> None:
    """Configure Loguru for the application.

    This function:
    - Removes default handlers
    - Adds console handler with configured format
    - Adds file handlers only if write_to_file is True (production)
    - Sets up rotation and retention
    - Intercepts Python logging to Loguru
    """
    # Remove default handler
    logger.remove()

    # Add console handler (development-friendly with colors)
    logger.add(
        sys.stderr,
        format=config.logging.format,
        level=config.logging.level,
        colorize=True,
    )

    # Add file handlers only in production
    if config.logging.write_to_file:
        # Add main application log file
        logger.add(
            str(config.logging.log_file_path),
            format=config.logging.format,
            level=config.logging.level,
            rotation=config.logging.rotation,
            retention=config.logging.retention,
            compression=config.logging.compression,
        )

        # Add Django-specific log file
        logger.add(
            str(config.logging.django_log_file_path),
            format=config.logging.format,
            level=config.logging.level,
            rotation=config.logging.rotation,
            retention=config.logging.retention,
            compression=config.logging.compression,
            filter=lambda record: "django" in (record.get("name") or "").lower(),
        )

    # Redirect Python logging to Loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0)


class InterceptHandler(logging.Handler):
    """Redirect Python standard logging to Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record using Loguru.

        Args:
            record: The log record to process.
        """
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Log through Loguru
        logger.bind(name=record.name).log(
            level,
            record.getMessage(),
        )


# Export logger for application use
__all__ = ["logger", "setup_logging"]
