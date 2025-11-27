"""PyProject.toml configuration schema.

Loads and validates project metadata from pyproject.toml file.
"""

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    PyprojectTomlConfigSettingsSource,
    SettingsConfigDict,
)

from config.paths import PROJECT_DIR

TOML_FILE = PROJECT_DIR / "pyproject.toml"


class PyProjectSettings(BaseSettings):
    name: str = "backend"
    version: str = "0.1.0"
    description: str = ""
    python_version: str = Field(default=">3.11", alias="requires-python")
    dependencies: list[str] = []

    model_config = SettingsConfigDict(
        pyproject_toml_table_header=("project",),
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (PyprojectTomlConfigSettingsSource(cls, toml_file=TOML_FILE),)


py_project_settings = PyProjectSettings()
