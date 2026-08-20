"""Конфигурация обязана падать на небезопасных значениях, а не тихо стартовать."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def _settings(**over: object) -> Settings:
    base: dict[str, object] = {
        "secret_key": "x" * 40,
        "environment": "development",
        "_env_file": None,
    }
    return Settings(**{**base, **over})  # type: ignore[arg-type]


def test_rejects_short_secret() -> None:
    with pytest.raises(ValidationError):
        _settings(secret_key="short")


def test_rejects_placeholder_secret_from_old_code() -> None:
    with pytest.raises(ValidationError):
        _settings(secret_key="ai-code-platform-secret-key-2026-change-in-production")


def test_production_forbids_sql_echo() -> None:
    with pytest.raises(ValidationError):
        _settings(environment="production", db_echo=True, cors_origins=["https://overcoding.app"])


def test_production_requires_https_origins() -> None:
    with pytest.raises(ValidationError):
        _settings(environment="production", cors_origins=["http://localhost:3000"])


def test_valid_development_settings() -> None:
    s = _settings()
    assert not s.is_production


class TestAsyncpgSslNormalization:
    """`sslmode=` в asyncpg-URL ломает подключение через SQLAlchemy.

    Драйвер asyncpg понимает `sslmode`, когда сам разбирает DSN, но диалект
    SQLAlchemy разбирает URL первым и передаёт параметры как именованные
    аргументы в `asyncpg.connect()`:
        TypeError: connect() got an unexpected keyword argument 'sslmode'
    Ошибка проявляется только при живом подключении, поэтому зафиксирована тестом.
    """

    def test_sslmode_becomes_ssl_for_asyncpg(self) -> None:
        s = _settings(
            database_url="postgresql+asyncpg://u:p@host/db?sslmode=require",
        )
        assert s.database_url.endswith("?ssl=require")
        assert "sslmode" not in s.database_url

    def test_sync_url_keeps_sslmode(self) -> None:
        """psycopg — это libpq, ему `sslmode` как раз и нужен."""
        url = "postgresql+psycopg://u:p@host/db?sslmode=require"
        assert _settings(database_url_sync=url).database_url_sync == url

    def test_url_without_ssl_is_untouched(self) -> None:
        url = "postgresql+asyncpg://u:p@localhost:5432/db"
        assert _settings(database_url=url).database_url == url

    def test_other_params_survive(self) -> None:
        s = _settings(
            database_url="postgresql+asyncpg://u:p@host/db?application_name=oc&sslmode=require",
        )
        assert "application_name=oc" in s.database_url
        assert "ssl=require" in s.database_url
