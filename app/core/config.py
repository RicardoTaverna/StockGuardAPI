"""Application configuration loaded from environment variables."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Runtime settings."""
    app_name: str = "StockGuard API"
    app_env: str = "local"
    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30
    bootstrap_user: str
    bootstrap_password: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
