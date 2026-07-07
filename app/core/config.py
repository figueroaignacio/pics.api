from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "Pics API"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    DATABASE_URL: str = Field(..., description="PostgreSQL async connection URL")

    R2_ACCOUNT_ID: str = Field(..., description="Cloudflare account ID")
    R2_ACCESS_KEY_ID: str = Field(..., description="R2 access key ID")
    R2_SECRET_ACCESS_KEY: str = Field(..., description="R2 secret access key")
    R2_BUCKET_NAME: str = Field(..., description="R2 bucket name")
    R2_PUBLIC_URL: str = Field(..., description="Public base URL for the R2 bucket")

    CORS_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    PAGINATION_DEFAULT_PAGE: int = 1
    PAGINATION_DEFAULT_SIZE: int = 20
    PAGINATION_MAX_SIZE: int = 100

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

        if v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)

        parsed = urlparse(v)
        params = parse_qs(parsed.query, keep_blank_values=True)
        params.pop("channel_binding", None)

        if "sslmode" in params:
            sslmode = params.pop("sslmode")[0]
            if sslmode in ("require", "verify-ca", "verify-full"):
                params.setdefault("ssl", ["require"])

        new_query = urlencode({k: v[0] for k, v in params.items()})
        return urlunparse(parsed._replace(query=new_query))

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
