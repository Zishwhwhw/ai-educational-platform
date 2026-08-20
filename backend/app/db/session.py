"""Подключение к базе и выдача сессии.

Здесь сосуществуют два движка, и это осознанно.

**Async** (`get_async_db`) — для всего нового кода.

**Sync** (`get_db`) — для 39 унаследованных эндпоинтов. Они объявлены как `def`,
а FastAPI выполняет такие в пуле потоков, поэтому синхронный доступ к базе там
не блокирует событийный цикл. Массовая конвертация была бы оптимизацией, а не
исправлением, и переписывать эти роутеры всё равно предстоит — тогда они
и переедут на async, по одному.

Sync-движок подлежит удалению, когда последний роутер перейдёт на async.
"""

from collections.abc import AsyncIterator, Iterator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

_settings = get_settings()

# --- async: основной путь -----------------------------------------------------

async_engine = create_async_engine(
    _settings.database_url,
    pool_size=_settings.db_pool_size,
    max_overflow=_settings.db_max_overflow,
    # Управляемый Postgres (Neon и подобные) засыпает при простое и рвёт
    # соединения. Без pre_ping первый запрос после паузы падает.
    pool_pre_ping=True,
    pool_recycle=300,
    echo=_settings.db_echo,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # объекты остаются пригодны после commit
)


async def get_async_db() -> AsyncIterator[AsyncSession]:
    """Зависимость FastAPI. Откатывает транзакцию при исключении."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


# --- sync: только для унаследованных роутеров ---------------------------------

engine = create_engine(
    _settings.database_url_sync,
    pool_size=_settings.db_pool_size,
    max_overflow=_settings.db_max_overflow,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=_settings.db_echo,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
