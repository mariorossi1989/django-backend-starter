"""Database configuration schemas.

Defines Pydantic models for database connection settings with validation
and DSN generation capabilities.
"""

from enum import StrEnum
from functools import cached_property
from typing import Generic, TypeVar

from loguru import logger
from pydantic import Field, PostgresDsn, SecretStr, field_validator
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

from config.paths import PROJECT_ENV_FILE

# Type variable for database URL types
DatabaseUrlType = TypeVar("DatabaseUrlType")


class DatabaseEngineEnum(StrEnum):
    """Available database engine types."""

    POSTGRESQL = "postgresql"
    # Future engines can be added here, e.g. MYSQL = "mysql"


class BaseDatabaseConfig(BaseSettings, Generic[DatabaseUrlType]):
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

    alias: str = Field(
        default="default",
        description="Database alias/identifier for multi-db setups",
    )

    model_config = SettingsConfigDict(
        env_file=PROJECT_ENV_FILE,
        env_prefix="DB_",
        extra="ignore",
        validate_default=True,
    )

    @field_validator("name", "user", mode="after")
    @classmethod
    def validate_required_fields(cls, v: str, info) -> str:
        """Ensure required database fields are not empty."""
        if not v or not v.strip():
            raise ValueError(
                f"DB_{info.field_name.upper()} is required and cannot be empty"
            )
        return v.strip()

    @field_validator("password", mode="after")
    @classmethod
    def validate_password(cls, v: SecretStr) -> SecretStr:
        """Ensure password is not empty."""
        if not v or not v.get_secret_value().strip():
            raise ValueError("DB_PASSWORD is required and cannot be empty")
        return v

    @classmethod
    def with_prefix(cls, prefix: str, **kwargs):
        """Create an instance with a custom environment variable prefix.

        Args:
            prefix: Custom environment variable prefix (e.g., "PRIMARY_DB_")
            **kwargs: Additional configuration parameters

        Returns:
            DatabaseConfig instance configured with the specified prefix

        Example:
            >>> primary_db = DatabaseConfig.with_prefix("PRIMARY_DB_")
            >>> secondary_db = DatabaseConfig.with_prefix("SECONDARY_DB_")
        """

        class CustomPrefixConfig(cls):
            model_config = SettingsConfigDict(
                env_file=PROJECT_ENV_FILE,
                env_prefix=prefix,
                extra="ignore",
                validate_default=True,
            )

        return CustomPrefixConfig(**kwargs)

    @cached_property
    def django_engine(self) -> str:
        """Get Django database engine string."""
        return "django.db.backends." + self.engine

    @cached_property
    def url(self) -> DatabaseUrlType:
        """Get database connection URL.

        Must be implemented by subclasses for specific database engines.
        The return type is determined by the TypeVar bound to each subclass.
        """
        raise NotImplementedError(
            f"URL generation not implemented for {self.__class__.__name__}"
        )


class PostgreSQLDatabaseConfig(BaseDatabaseConfig[PostgresDsn]):
    """PostgreSQL-specific database configuration."""

    engine: DatabaseEngineEnum = DatabaseEngineEnum.POSTGRESQL

    model_config = SettingsConfigDict(
        env_file=PROJECT_ENV_FILE,
        env_prefix="DB_",
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

    def __call__(self, engine: DatabaseEngineEnum | str) -> BaseDatabaseConfig:
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
            return PostgreSQLDatabaseConfig()

        raise ValueError(f"Unsupported database engine: {engine}")


class DatabaseAliasManager(BaseSettings):
    aliases: list[str] = Field(
        default_factory=lambda: ["default"],
        description="List of database aliases to load configurations for",
    )

    model_config = SettingsConfigDict(
        env_file=PROJECT_ENV_FILE,
        env_prefix="DB_",
        extra="ignore",
    )


class MultiDatabaseConfigLoader:
    """Loader for creating database configurations based on environment aliases."""

    def __call__(self) -> dict[str, BaseDatabaseConfig]:
        """Load all database configurations from environment.

        Returns:
            Dictionary mapping database aliases to their configurations.
        """
        return self._load_all_databases()

    def _load_all_databases(self) -> dict[str, BaseDatabaseConfig]:
        """Load all database configurations detected from environment."""
        manager = DatabaseAliasManager()
        aliases = manager.aliases
        configs: dict[str, BaseDatabaseConfig] = {}

        for alias in aliases:
            try:
                # Determine environment variable prefix
                env_prefix = "DB_" if alias == "default" else f"DB_{alias.upper()}_"

                db_config = BaseDatabaseConfig.with_prefix(env_prefix, alias=alias)
                configs[alias] = db_config

            except Exception as e:
                if alias == "default":
                    raise ValueError(
                        f"Failed to load default database configuration: {e}"
                    ) from e
                # Log warning for optional databases
                logger.warning(f"Warning: Could not load database '{alias}': {e}")

        return configs


# Lazy instantiation - created when accessed
database_config = MultiDatabaseConfigLoader()()
