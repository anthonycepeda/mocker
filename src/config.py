from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or .env file."""

    app_name: str = "Mocker API"
    description: str = "Generates realistic mock data from internal FastAPI OpenAPI schemas."
    host: str = "0.0.0.0"
    port: int = 8080
    environment: str = "development"
    debug: bool = False

    model_config = SettingsConfigDict(env_prefix="MOCKER_", env_file=".env")


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance for use as a FastAPI dependency."""
    return Settings()
