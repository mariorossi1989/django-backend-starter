"""Logging configuration schemas.

Defines Pydantic models for centralized logging configuration with
environment-specific settings and log file management.
"""

from enum import StrEnum
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.paths import PROJECT_DIR, PROJECT_ENV_FILE
from config.settings.schemas.environment import EnvStateEnum
from config.settings.schemas.utils import EnvironmentBasedFactory


class LogLevelEnum(StrEnum):
    """Available logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LoggingConfig(BaseSettings):
    """Base logging configuration."""

    level: LogLevelEnum = LogLevelEnum.INFO
    log_dir: str = Field(
        default=str(PROJECT_DIR / "logs"),
        description="Directory for log files",
    )
    format: str = Field(
        default=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "  # noqa: RUF027
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        description="Log message format string",
    )
    rotation: str = Field(
        default="500 MB",
        description="Log file rotation size",
    )
    retention: str = Field(
        default="7 days",
        description="Log file retention period",
    )
    compression: str = Field(
        default="zip",
        description="Log file compression format",
    )
    write_to_file: bool = Field(
        default=False,
        description="Whether to write logs to file",
    )

    model_config = SettingsConfigDict(
        env_file=PROJECT_ENV_FILE,
        env_prefix="LOG_",
        extra="ignore",
    )

    @property
    def log_file_path(self) -> Path:
        """Get the full path to the main log file."""
        log_dir_path = Path(self.log_dir)
        log_dir_path.mkdir(parents=True, exist_ok=True)
        return log_dir_path / "app.log"

    @property
    def django_log_file_path(self) -> Path:
        """Get the full path to the Django-specific log file."""
        log_dir_path = Path(self.log_dir)
        log_dir_path.mkdir(parents=True, exist_ok=True)
        return log_dir_path / "django.log"


class LoggingDevConfig(LoggingConfig):
    """Development-specific logging configuration."""

    level: LogLevelEnum = LogLevelEnum.DEBUG
    write_to_file: bool = False  # Only console in development


class LoggingProductionConfig(LoggingConfig):
    """Production-specific logging configuration."""

    level: LogLevelEnum = LogLevelEnum.INFO
    retention: str = Field(
        default="30 days",
        description="Production logs retention period",
    )
    write_to_file: bool = True  # Write to file in production


_logging_config_mapping = {
    EnvStateEnum.DEVELOPMENT: LoggingDevConfig,
    EnvStateEnum.PRODUCTION: LoggingProductionConfig,
}


logging_config_factory = EnvironmentBasedFactory(_logging_config_mapping)
