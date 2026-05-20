from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Lifestyle Coach API")
    app_version: str = Field(default="0.1.0")
    environment: Literal["local", "development", "test", "staging", "production"] = Field(
        default="local"
    )
    api_v1_prefix: str = Field(default="/api/v1")
    database_url: str = Field(default=...)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
