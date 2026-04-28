from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os


@dataclass(frozen=True)
class Settings:
    database_url: str
    app_env: str
    cors_origins: list[str]
    auth_secret_key: str
    access_token_expire_minutes: int


def _parse_cors_origins(value: str) -> list[str]:
    return [origin.strip() for origin in value.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    app_env = os.getenv("APP_ENV", "development")
    default_database_url = "sqlite:///./dpdp_privacyops_dev.db"
    default_cors_origins = "http://localhost:3000,http://127.0.0.1:3000"
    default_auth_secret = "local-mvp-change-me"
    return Settings(
        database_url=os.getenv("DATABASE_URL", default_database_url),
        app_env=app_env,
        cors_origins=_parse_cors_origins(os.getenv("CORS_ORIGINS", default_cors_origins)),
        auth_secret_key=os.getenv("AUTH_SECRET_KEY", default_auth_secret),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")),
    )
