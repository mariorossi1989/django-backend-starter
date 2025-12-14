"""Environment configuration schemas.

Defines environment states and settings loaded from .env file,
including factory pattern for environment-based configuration selection.
"""

from enum import StrEnum
from typing import Generic, TypeVar

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

from config.paths import PROJECT_ENV_FILE

BaseSettingsT = TypeVar("BaseSettingsT", bound=BaseSettings)


class EnvStateEnum(StrEnum):
    """Available environment states."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"


class EnvSettings(BaseSettings):
    """Environment settings loaded from .env file."""

    state: EnvStateEnum = Field(default=EnvStateEnum.DEVELOPMENT)

    model_config = SettingsConfigDict(
        env_file=PROJECT_ENV_FILE, env_prefix="ENV_", extra="ignore"
    )


class EnvBasedConfigFactory(Generic[BaseSettingsT]):
    """Generic factory that returns settings based on environment state.

    Args:
        mapping: Dictionary mapping EnvStateEnum values to corresponding settings.
    """

    def __init__(self, mapping: dict[EnvStateEnum, BaseSettingsT]) -> None:
        self.mapping = mapping

    def __call__(self, state: EnvStateEnum) -> BaseSettingsT:
        """Returns the setting associated with the current environment state.

        Returns:
            The setting value for the current environment.

        Raises:
            KeyError: If current env state is not in mapping.
        """
        return self.mapping[state]


env_settings = EnvSettings()
