"""Конфигурация приложения.

Единственный источник настроек. Читается из окружения; в коде значений быть не должно.
Приложение не стартует, если обязательные переменные не заданы или заданы небезопасно —
это осознанно: тихий старт с дефолтным секретом опаснее падения при запуске.
"""

import re
from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "staging", "production"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    # --- окружение ---
    environment: Environment = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # --- база данных ---
    # asyncpg — для приложения, psycopg — для alembic (он синхронный).
    database_url: str = Field(
        default="postgresql+asyncpg://overcoding:devpassword@localhost:5432/overcoding"
    )
    database_url_sync: str = Field(
        default="postgresql+psycopg://overcoding:devpassword@localhost:5432/overcoding"
    )
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_echo: bool = False

    @field_validator("database_url")
    @classmethod
    def _normalize_asyncpg_ssl(cls, v: str) -> str:
        """Перевести `sslmode=` в `ssl=` для asyncpg-URL.

        `sslmode` — параметр libpq. Драйвер asyncpg понимает его, когда сам
        разбирает DSN, но диалект SQLAlchemy разбирает URL первым и передаёт
        параметры запроса как именованные аргументы в `asyncpg.connect()`,
        который такого аргумента не знает:

            TypeError: connect() got an unexpected keyword argument 'sslmode'

        Управляемые Postgres (Neon, Supabase, Railway) выдают строку именно
        с `sslmode=require`, поэтому нормализуем здесь — чтобы её можно было
        вставлять как есть, не помня об этой разнице.
        """
        if "+asyncpg" not in v or "sslmode=" not in v:
            return v
        # sslmode=require|verify-ca|verify-full → ssl=<то же>; disable → ssl=disable
        return re.sub(r"(?<=[?&])sslmode=", "ssl=", v)

    # --- исполнение кода ---
    execution_engine: Literal["judge0"] = "judge0"
    # По умолчанию — публичный Judge0 CE: бесплатный, без ключа, годится
    # для разработки. Для боя поднимается свой экземпляр, меняется только адрес.
    judge0_url: str = "https://ce.judge0.com"
    judge0_token: str = ""
    execution_time_limit_ms: int = 5_000
    execution_memory_limit_mb: int = 128

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- безопасность ---
    secret_key: str = Field(min_length=32)
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 30

    # --- CORS ---
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("secret_key")
    @classmethod
    def _reject_placeholder_secret(cls, v: str) -> str:
        """Не давать стартовать со значением из шаблона или из старого кода."""
        banned = {
            "ai-code-platform-secret-key-2026-change-in-production",
            "changeme",
            "secret",
        }
        if v.strip().lower() in banned:
            raise ValueError("SECRET_KEY имеет значение-заглушку. Сгенерируй: openssl rand -hex 32")
        return v

    @model_validator(mode="after")
    def _production_guardrails(self) -> "Settings":
        if self.environment == "production":
            if "ce.judge0.com" in self.judge0_url:
                raise ValueError(
                    "публичный Judge0 CE нельзя использовать в production: "
                    "нет гарантий доступности, есть ограничение частоты, "
                    "и код учеников уходит в чужой сервис"
                )
            if self.db_echo:
                raise ValueError("db_echo нельзя включать в production — утечка данных в логи")
            if any(o.startswith("http://") for o in self.cors_origins):
                raise ValueError("в production все cors_origins должны быть https")
        return self

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Кешируется: настройки читаются один раз за процесс."""
    return Settings()
