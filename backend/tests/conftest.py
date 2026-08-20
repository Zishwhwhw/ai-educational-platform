"""Общие фикстуры.

`SECRET_KEY` подставляется до импорта приложения: конфиг обязателен и приложение
намеренно не стартует без него.

Тесты работают на отдельной SQLite-базе, а не на настоящем Postgres: они должны
запускаться без внешних зависимостей и не портить общую базу разработки.
Интеграционные проверки против Postgres живут в CI, где сервис поднимается рядом.
"""

import os
from collections.abc import Iterator
from pathlib import Path

os.environ.setdefault("SECRET_KEY", "test-secret-key-at-least-32-characters-long")
os.environ.setdefault("ENVIRONMENT", "development")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Role

ROLE_NAMES = ("student", "teacher", "moderator", "admin", "owner")


@pytest.fixture(scope="session")
def _engine(tmp_path_factory: pytest.TempPathFactory):  # type: ignore[no-untyped-def]
    path: Path = tmp_path_factory.mktemp("db") / "test.sqlite"
    engine = create_engine(f"sqlite:///{path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db(_engine) -> Iterator[Session]:  # type: ignore[no-untyped-def]
    """Чистая база на каждый тест: таблицы пересоздаются, роли засеваются заново."""
    Base.metadata.drop_all(_engine)
    Base.metadata.create_all(_engine)

    maker = sessionmaker(bind=_engine, autocommit=False, autoflush=False)
    session = maker()
    # Роли в бою засевает миграция 0002; здесь повторяем то же самое.
    session.add_all([Role(id=i, name=n) for i, n in enumerate(ROLE_NAMES, start=1)])
    session.commit()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db: Session) -> Iterator[TestClient]:
    """Клиент, у которого `get_db` подменён на тестовую сессию."""

    def _override() -> Iterator[Session]:
        yield db

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def plain_client() -> Iterator[TestClient]:
    """Клиент без подмены базы — для проверок, не зависящих от неё."""
    with TestClient(app) as c:
        yield c
