"""Central configuration registry.

Provides a unified interface to access all configuration settings including
Django, database, environment, logging, and pyproject.toml configurations.
"""

from functools import cached_property, lru_cache

from django.core.exceptions import ImproperlyConfigured
from pydantic import ValidationError

from config.settings.schemas.database import BaseDatabaseConfig, database_config
from config.settings.schemas.django import DjangoConfig, django_config_factory
from config.settings.schemas.environment import EnvSettings, env_settings
from config.settings.schemas.logging import LoggingConfig, logging_config_factory
from config.settings.schemas.py_project import PyProjectSettings, py_project_settings


class _SettingsRegistry:
    @cached_property
    def env(self) -> EnvSettings:
        return env_settings

    @cached_property
    def env_state(self):
        return self.env.state

    @cached_property
    def django(self) -> DjangoConfig:
        return django_config_factory(self.env_state)

    @cached_property
    def django_settings_module(self) -> str:
        return self.django.settings_module.value

    @cached_property
    def pyproject(self) -> PyProjectSettings:
        return py_project_settings

    @cached_property
    def database(self) -> dict[str, BaseDatabaseConfig]:
        return database_config

    @cached_property
    def logging(self) -> LoggingConfig:
        return logging_config_factory(self.env_state)


@lru_cache(maxsize=1)
def get_registry() -> _SettingsRegistry:
    """Get the global project settings instance."""
    try:
        return _SettingsRegistry()
    except ValidationError as e:
        details = "; ".join([f"{err['loc']}: {err['msg']}" for err in e.errors()])
        raise ImproperlyConfigured(
            f"Invalid environment configuration: {details}"
        ) from e


def reload_registry() -> None:
    """Clear the registry cache and reload settings."""
    get_registry.cache_clear()
    global config_registry
    config_registry = get_registry()


# Global config instance
config_registry = get_registry()
