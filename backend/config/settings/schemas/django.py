"""Django configuration schemas.

Defines environment-specific Django configurations with Pydantic validation,
including development and production settings.
"""

from enum import StrEnum

from pydantic import Field, field_validator
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)
from zxcvbn import zxcvbn

from config.paths import PROJECT_ENV_FILE
from config.settings.schemas.environment import EnvStateEnum
from config.settings.schemas.utils import EnvironmentBasedFactory


class DjangoSettingsModuleEnum(StrEnum):
    DEVELOPMENT = "config.settings.django.development"
    PRODUCTION = "config.settings.django.production"


class DjangoConfig(BaseSettings):
    """Project settings loaded from pyproject.toml."""

    settings_module: DjangoSettingsModuleEnum

    secret_key: str = ""

    debug: bool = True

    allowed_hosts: list[str] = Field(default_factory=list)

    model_config = SettingsConfigDict(
        env_file=PROJECT_ENV_FILE, env_prefix="DJANGO_", extra="ignore"
    )


class DjangoDevConfig(DjangoConfig):
    settings_module: DjangoSettingsModuleEnum = DjangoSettingsModuleEnum.DEVELOPMENT
    allowed_hosts: list[str] = Field(default_factory=lambda: ["*"])


class DjangoProdConfig(DjangoConfig):
    settings_module: DjangoSettingsModuleEnum = DjangoSettingsModuleEnum.PRODUCTION

    debug: bool = False
    allowed_hosts: list[str] = Field(default_factory=lambda: [])

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate that the secret key meets minimum security requirements.

        Uses zxcvbn to assess password strength. Requires a score of at least 3
        (out of 4) for production environments.
        """
        if not v:
            raise ValueError("SECRET_KEY must not be empty in production")

        if len(v) < 50:
            raise ValueError(
                "SECRET_KEY must be at least 50 characters long in production"
            )

        # Use zxcvbn to check password strength
        # Score: 0 (too guessable) to 4 (very unguessable)
        result = zxcvbn(v)
        score = result["score"]

        if score < 3:
            feedback = result.get("feedback", {})
            warning = feedback.get("warning", "Secret key is too weak")
            suggestions = feedback.get("suggestions", [])

            error_msg = (
                f"SECRET_KEY strength insufficient (score: {score}/4). {warning}"
            )
            if suggestions:
                error_msg += f" Suggestions: {'; '.join(suggestions)}"

            raise ValueError(error_msg)

        return v


_django_config_mapping = {
    EnvStateEnum.DEVELOPMENT: DjangoDevConfig,
    EnvStateEnum.PRODUCTION: DjangoProdConfig,
}

django_config_factory = EnvironmentBasedFactory(_django_config_mapping)
