"""Точка входа FastAPI.

Отличия от прежнего `main.py`:
  * схема БД больше НЕ создаётся на старте (`Base.metadata.create_all` удалён) —
    единственный источник схемы теперь Alembic;
  * CORS-источники берутся из настроек, а не захардкожены;
  * есть `/health` (жив) и `/ready` (готов принимать трафик) — их различие
    существенно для оркестратора: перезапускать нужно по первому, а выводить
    из балансировки по второму;
  * каждому запросу присваивается `request_id`, он же уходит в лог и в тело ошибки.
"""

import time
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.requests import Request

from app.api.routers import (
    achievements,
    ai,
    auth,
    clans,
    courses,
    flashcards,
    hints,
    leaderboard,
    lessons,
    messages,
    notifications,
    peer_reviews,
    progress,
    store,
    streaks,
    submissions,
    tasks,
    users,
    ws,
)
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.db.session import async_engine, engine

settings = get_settings()
log = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    log.info("startup", environment=settings.environment)
    yield
    # Оба пула закрываем явно: иначе при остановке остаются висящие соединения,
    # а у управляемого Postgres их лимит невелик.
    await async_engine.dispose()
    engine.dispose()
    log.info("shutdown")


app = FastAPI(
    title="OverCoding API",
    description="Backend for the OverCoding programming learning platform",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
    request.state.request_id = request_id
    structlog.contextvars.bind_contextvars(request_id=request_id, path=request.url.path)

    started = time.perf_counter()
    try:
        response = await call_next(request)
    finally:
        structlog.contextvars.clear_contextvars()

    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    log.info(
        "request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=elapsed_ms,
    )
    return response


register_exception_handlers(app)


@app.get("/health", tags=["ops"], summary="Liveness — процесс жив")
def health() -> dict[str, str]:
    """Никаких внешних зависимостей: отвечает, пока процесс способен отвечать.

    По этой проверке контейнер перезапускают, поэтому падение базы не должно
    её ронять — иначе оркестратор устроит бесконечный перезапуск здорового
    приложения из-за недоступной БД.
    """
    return {"status": "ok", "version": app.version}


@app.get("/ready", tags=["ops"], summary="Readiness — готов принимать трафик")
def ready() -> JSONResponse:
    """Проверяет зависимости. По ней выводят из балансировки, но не перезапускают."""
    checks: dict[str, str] = {}

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:
        log.warning("readiness_database_failed", error=str(exc))
        checks["database"] = "unavailable"

    healthy = all(v == "ok" for v in checks.values())
    return JSONResponse(
        status_code=status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "ready" if healthy else "not_ready", "checks": checks},
    )


for _router in (
    auth,
    users,
    courses,
    lessons,
    submissions,
    progress,
    achievements,
    ai,
    ws,
    store,
    clans,
    streaks,
    flashcards,
    notifications,
    messages,
    leaderboard,
    peer_reviews,
    tasks,
    hints,
):
    app.include_router(_router.router)
