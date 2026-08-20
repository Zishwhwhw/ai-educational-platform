"""Проверки эндпоинтов эксплуатации и базовой сборки приложения."""

from fastapi.testclient import TestClient


def test_health_is_independent_of_database(plain_client: TestClient) -> None:
    """`/health` обязан отвечать 200 даже без базы — иначе оркестратор будет
    бесконечно перезапускать здоровое приложение из-за недоступной БД."""
    r = plain_client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_ready_reports_database_state(plain_client: TestClient) -> None:
    """`/ready` проверяет зависимости: 200 если база доступна, 503 если нет.
    Оба исхода валидны — тест фиксирует контракт, а не наличие базы."""
    r = plain_client.get("/ready")
    assert r.status_code in (200, 503)
    body = r.json()
    assert body["checks"]["database"] in ("ok", "unavailable")
    assert (body["status"] == "ready") == (r.status_code == 200)


def test_request_id_is_returned(plain_client: TestClient) -> None:
    r = plain_client.get("/health")
    assert r.headers.get("X-Request-ID")


def test_request_id_is_echoed_when_supplied(plain_client: TestClient) -> None:
    r = plain_client.get("/health", headers={"X-Request-ID": "abc123"})
    assert r.headers["X-Request-ID"] == "abc123"


def test_all_models_are_registered(plain_client: TestClient) -> None:
    """Разбиение `models.py` на модули не должно терять таблицы.

    Проверяется состав, а не количество: число меняется при каждой миграции
    и превращает тест в постоянно ломающийся счётчик, ничего не гарантирующий.
    """
    from app.db.base import Base

    expected = {
        # учебное ядро
        "users",
        "courses",
        "modules",
        "lessons",
        "tasks",
        "submissions",
        "progress",
        # авторизация
        "roles",
        "user_roles",
        "refresh_tokens",
        # геймификация
        "achievements",
        "user_achievements",
        "store_items",
        "user_purchases",
        "flashcards",
        "double_xp_events",
        # социальное
        "clans",
        "clan_members",
        "comments",
        "private_messages",
        "notifications",
        "peer_reviews",
        # честность
        "antifraud_logs",
        "appeals",
    }
    missing = expected - set(Base.metadata.tables)
    assert not missing, f"потеряны таблицы: {sorted(missing)}"


def test_routers_are_mounted(plain_client: TestClient) -> None:
    paths = plain_client.app.openapi()["paths"]  # type: ignore[attr-defined]
    assert len(paths) > 30
    for expected in ("/auth/login", "/courses/", "/submissions/"):
        assert expected in paths
