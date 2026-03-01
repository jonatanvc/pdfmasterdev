from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore", env_file=[Path(".env.test"), Path(".env")], env_file_encoding="utf-8"
    )

    telegram_token: str = Field(...)
    google_fonts_token: str | None = Field(default=None)
    ga_api_secret: str | None = Field(default=None)
    ga_measurement_id: str | None = Field(default=None)
    sentry_dsn: str | None = Field(default=None)

    # PostgreSQL database configuration (Neon Serverless)
    database_url: str = Field(..., description="PostgreSQL connection string")

    admin_telegram_id: int = Field(...)

    request_connection_pool_size: int = 12
    request_read_timeout: int = 45
    request_write_timeout: int = 45
    request_connect_timeout: int = 45
    request_pool_timeout: int = 45

    telegram_max_retries: int = 2
