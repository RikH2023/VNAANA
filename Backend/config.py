"""App settings, read from environment variables or a .env file."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://vnaana:vnaana@localhost:5432/vnaana"
    sql_echo: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
