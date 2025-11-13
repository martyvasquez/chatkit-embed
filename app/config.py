from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AdminUser(BaseModel):
    username: str = Field(default="admin")
    password: str = Field(default="changeme")


class Settings(BaseSettings):
    """Runtime configuration loaded from environment."""

    database_url: str = Field(
        default="sqlite+aiosqlite:///./chatkit.db",
        validation_alias="DATABASE_URL",
    )
    app_encryption_key: str = Field(
        default="",
        validation_alias="APP_ENCRYPTION_KEY",
        description="Fernet key used to encrypt API secrets at rest.",
    )
    allowed_cors_origins: List[AnyHttpUrl] = Field(
        default_factory=list, validation_alias="CORS_ORIGINS"
    )
    tortoise_database_url: str | None = Field(
        default=None, validation_alias="TORTOISE_DATABASE_URL"
    )
    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    admin_secret_key: str = Field(
        default="super-secret", validation_alias="ADMIN_SECRET"
    )
    admin_user: AdminUser = Field(
        default_factory=AdminUser,
        validation_alias="ADMIN_USER",
        description="Default FastAPI-Admin credentials.",
    )
    openai_api_base: AnyHttpUrl | None = Field(
        default=None, validation_alias="OPENAI_API_BASE"
    )
    admin_path: str = Field(default="/admin", validation_alias="ADMIN_PATH")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
