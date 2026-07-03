from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "ProjectBrain"
    app_version: str = "0.1.0-dev"

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_prefix="PROJECTBRAIN_",
        case_sensitive=False,
    )


settings = Settings()