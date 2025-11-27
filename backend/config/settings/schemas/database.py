"""Database configuration schemas.

Defines Pydantic models for database connection settings with validation
and DSN generation capabilities.
"""

from enum import StrEnum
from functools import cached_property

from pydantic import Field, PostgresDsn, SecretStr, field_validator
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

from config.paths import PROJECT_ENV_FILE


class DatabaseEngineEnum(StrEnum):
    """Available database engine types."""

    POSTGRESQL = "postgresql"


class DatabaseConfig(BaseSettings):
    """Base database configuration with validation."""

    engine: DatabaseEngineEnum = DatabaseEngineEnum.POSTGRESQL
    name: str = Field(
        default="",
        description="Database name (required)",
    )
    user: str = Field(
        default="",
        description="Database user (required)",
    )
    password: SecretStr = Field(
        default=SecretStr(""),
        description="Database password (required, stored securely)",
    )

    host: str = Field(
        default="localhost",
        description="Database host address",
    )
    port: int = Field(
        default=5432,
        ge=1,
        le=65535,
        description="Database port number",
    )

    model_config = SettingsConfigDict(
        env_file=PROJECT_ENV_FILE,
        env_prefix="DATABASE_",
        extra="ignore",
        validate_default=True,
    )

    @field_validator("name", "user", mode="after")
    @classmethod
    def validate_required_fields(cls, v: str, info) -> str:
        """Ensure required database fields are not empty."""
        if not v or not v.strip():
            raise ValueError(
                f"DATABASE_{info.field_name.upper()} is required and cannot be empty"
            )
        return v.strip()

    @field_validator("password", mode="after")
    @classmethod
    def validate_password(cls, v: SecretStr) -> SecretStr:
        """Ensure password is not empty."""
        if not v or not v.get_secret_value().strip():
            raise ValueError("DATABASE_PASSWORD is required and cannot be empty")
        return v

    @cached_property
    def django_engine(self) -> str:
        """Get Django database engine string."""
        return "django.db.backends." + self.engine


class PostgresDBConfig(DatabaseConfig):
    """PostgreSQL-specific database configuration."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ENV_FILE,
        env_prefix="DATABASE_",
        extra="ignore",
    )

    @cached_property
    def url(self) -> PostgresDsn:
        """Generate PostgreSQL connection URL."""
        password = self.password.get_secret_value()
        return PostgresDsn(
            f"postgresql://{self.user}:{password}@{self.host}:{self.port}/{self.name}"
        )


class DatabaseConfigFactory:
    """Factory for creating database configuration based on engine type."""

    def __call__(
        self, engine: DatabaseEngineEnum | str = DatabaseEngineEnum.POSTGRESQL
    ) -> DatabaseConfig:
        """Create appropriate database config instance.

        Args:
            engine: Database engine type from DatabaseEngineEnum or valid string

        Returns:
            DatabaseConfig subclass instance for the specified engine

        Raises:
            ValueError: If engine string is not a valid DatabaseEngineEnum value
        """
        # Convert string to enum if needed
        if isinstance(engine, str):
            try:
                engine = DatabaseEngineEnum(engine)
            except ValueError as e:
                valid_engines = ", ".join([e.value for e in DatabaseEngineEnum])
                raise ValueError(
                    f"Invalid database engine '{engine}'. "
                    f"Must be one of: {valid_engines}"
                ) from e

        if engine == DatabaseEngineEnum.POSTGRESQL:
            return PostgresDBConfig()

        return DatabaseConfig()


# Lazy instantiation - created when accessed
database_config = DatabaseConfigFactory()(DatabaseEngineEnum.POSTGRESQL)
