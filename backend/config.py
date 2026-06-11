from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["development", "test", "production"] = "development"
    database_url: str = "sqlite+aiosqlite:///./data/companion.db"
    redis_url: str = "redis://localhost:6379/0"
    support_email: str = "support@example.com"
    cors_allowed_origins: str = "http://localhost:3000"
    cookie_domain: str | None = None
    session_cookie_name: str = "companion_session"
    csrf_cookie_name: str = "companion_csrf"
    session_days: int = Field(default=7, ge=1, le=30)
    deleted_conversation_retention_days: int = Field(default=30, ge=1)
    security_log_retention_days: int = Field(default=90, ge=1)
    provider_timeout_seconds: float = Field(default=6.0, ge=1, le=15)
    insight_cache_seconds: int = Field(default=900, ge=60)
    log_level: str = "INFO"

    @field_validator("database_url")
    @classmethod
    def validate_production_database(cls, value: str, info):
        if info.data.get("app_env") == "production" and not value.startswith(
            ("postgresql+asyncpg://", "postgresql://")
        ):
            raise ValueError("Production DATABASE_URL must use PostgreSQL")
        return value

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def allowed_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_allowed_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
