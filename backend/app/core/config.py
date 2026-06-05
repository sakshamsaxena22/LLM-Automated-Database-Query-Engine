"""
Application settings loaded from environment variables via pydantic-settings.

All configuration is centralized here. Values are read from backend/.env
and can be overridden by real environment variables (12-factor style).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed, validated application configuration."""

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[2] / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── MongoDB ────────────────────────────────────────────────────────
    MONGODB_URI: str
    DATABASE_NAME: str = "enterprise_db"

    # ── Groq / LLM ────────────────────────────────────────────────────
    GROQ_API_KEY: str
    LLM_MODEL: str = "llama-3.1-8b-instant"

    # ── JWT / Auth ─────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Redis ──────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379"

    # ── Application ────────────────────────────────────────────────────
    MAX_RESULTS: int = 100
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # ── Derived helpers (not env vars) ─────────────────────────────────
    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()  # type: ignore[call-arg]

# ── Configure root logger once at import time ─────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
