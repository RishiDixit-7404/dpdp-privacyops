from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os


@dataclass(frozen=True)
class Settings:
    database_url: str
    app_env: str
    cors_origins: list[str]


def _parse_cors_origins(value: str) -> list[str]:
    return [origin.strip() for origin in value.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    app_env = os.getenv("APP_ENV", "development")
    default_database_url = "sqlite:///./dpdp_privacyops_dev.db"
    return Settings(
        database_url=os.getenv("DATABASE_URL", default_database_url),
        app_env=app_env,
        cors_origins=_parse_cors_origins(os.getenv("CORS_ORIGINS", "http://localhost:3000")),
    )

