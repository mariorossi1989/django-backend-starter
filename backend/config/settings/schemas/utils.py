"""Configuration utility classes.

Provides factory patterns and utilities for environment-based configuration.
"""

from collections.abc import Callable
from typing import Generic, TypeVar

from pydantic_settings import BaseSettings

from config.settings.schemas.environment import EnvStateEnum

BaseSettingsT = TypeVar("BaseSettingsT", bound=BaseSettings)


class EnvironmentBasedFactory(Generic[BaseSettingsT]):
    """Generic factory that returns settings based on environment state.

    Uses lazy initialization: configurations are only instantiated when requested,
    preventing validation errors for unused environments.

    Args:
        factory_mapping: Dictionary mapping EnvStateEnum values to callables
                        that return the corresponding settings instances.
    """

    def __init__(
        self,
        factory_mapping: dict[EnvStateEnum, Callable[[], BaseSettingsT]],
    ) -> None:
        self._factory_mapping = factory_mapping
        self._cache: dict[EnvStateEnum, BaseSettingsT] = {}

    def __call__(self, state: EnvStateEnum) -> BaseSettingsT:
        """Returns the setting associated with the current environment state.

        Settings are instantiated on first access and cached for subsequent calls.

        Returns:
            The setting value for the current environment.

        Raises:
            KeyError: If current env state is not in mapping.
        """
        if state not in self._cache:
            factory = self._factory_mapping[state]
            self._cache[state] = factory()
        return self._cache[state]
