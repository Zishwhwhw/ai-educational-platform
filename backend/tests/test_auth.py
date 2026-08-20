"""Проверки авторизации.

Каждый тест здесь соответствует конкретной дыре, найденной в аудите кода,
и существует, чтобы она не вернулась.
"""

from typing import Any, ClassVar

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

REGISTER = {"username": "alice", "email": "alice@example.com", "password": "correct-horse-99"}


def _register(client: TestClient, **over: object) -> dict[str, Any]:
    r = client.post("/auth/register", json={**REGISTER, **over})
    assert r.status_code == 201, r.text
    body: dict[str, Any] = r.json()
    return body


class TestRegistration:
    def test_new_user_gets_student_role_only(self, client: TestClient) -> None:
        assert _register(client)["user"]["roles"] == ["student"]

    def test_role_cannot_be_set_by_client(self, client: TestClient) -> None:
        """Главная дыра: раньше `role` принимался из тела запроса, и любой
        мог зарегистрироваться владельцем платформы."""
        r = client.post("/auth/register", json={**REGISTER, "role": "owner"})
        assert r.status_code == 201
        assert r.json()["user"]["roles"] == ["student"]

    def test_duplicate_email_is_rejected(self, client: TestClient) -> None:
        _register(client)
        r = client.post("/auth/register", json={**REGISTER, "username": "bob"})
        assert r.status_code == 409

    def test_short_password_rejected(self, client: TestClient) -> None:
        r = client.post("/auth/register", json={**REGISTER, "password": "short"})
        assert r.status_code == 422

    def test_invalid_email_rejected(self, client: TestClient) -> None:
        r = client.post("/auth/register", json={**REGISTER, "email": "nope"})
        assert r.status_code == 422

    def test_password_is_not_stored_in_plain_text(self, client: TestClient, db: Session) -> None:
        _register(client)
        from app.models import User

        stored = db.query(User).one().hashed_password
        assert REGISTER["password"] not in stored
        assert stored.startswith("$argon2")


class TestLogin:
    def test_login_returns_tokens(self, client: TestClient) -> None:
        _register(client)
        r = client.post(
            "/auth/login",
            json={"email": REGISTER["email"], "password": REGISTER["password"]},
        )
        assert r.status_code == 200
        assert r.json()["access_token"] and r.json()["refresh_token"]

    def test_wrong_password_rejected(self, client: TestClient) -> None:
        _register(client)
        r = client.post(
            "/auth/login", json={"email": REGISTER["email"], "password": "wrong-password"}
        )
        assert r.status_code == 401

    def test_unknown_email_gives_same_error_as_wrong_password(self, client: TestClient) -> None:
        """Разные ответы позволяли бы перебором выяснять, какие адреса заняты."""
        _register(client)
        a = client.post("/auth/login", json={"email": "nobody@example.com", "password": "x" * 12})
        b = client.post("/auth/login", json={"email": REGISTER["email"], "password": "y" * 12})
        assert a.status_code == b.status_code == 401
        assert a.json()["error"]["code"] == b.json()["error"]["code"]


class TestProtectedEndpoints:
    """Восемь эндпоинтов принимали `user_id: int = 1` параметром запроса,
    то есть выполнялись от имени любого пользователя без токена."""

    ANONYMOUS: ClassVar[list[tuple[str, str, dict[str, Any] | None]]] = [
        ("post", "/submissions/", {"task_id": 1, "language": "python", "source": "x"}),
        ("post", "/submissions/run", {"task_id": 1, "language": "python", "source": "x"}),
        ("post", "/peer-reviews/", {"submission_id": 1, "score": 5, "comment": "ok"}),
        ("post", "/clans/", {"name": "c", "description": "d"}),
        ("post", "/clans/1/join", None),
        ("post", "/flashcards/", {"question": "q", "answer": "a"}),
        ("post", "/progress/complete", {"lesson_id": 1, "time_spent": 300}),
        ("post", "/messages/", {"receiver_id": 2, "content": "hi"}),
        ("get", "/messages/conversation/2", None),
    ]

    def test_all_reject_anonymous(self, client: TestClient) -> None:
        for method, path, body in self.ANONYMOUS:
            r = getattr(client, method)(path, json=body) if body else getattr(client, method)(path)
            assert r.status_code == 401, (
                f"{method.upper()} {path} пустил без токена ({r.status_code})"
            )

    def test_me_requires_token(self, client: TestClient) -> None:
        assert client.get("/auth/me").status_code == 401

    def test_me_returns_current_user(self, client: TestClient) -> None:
        token = _register(client)["access_token"]
        r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json()["username"] == REGISTER["username"]

    def test_garbage_token_rejected(self, client: TestClient) -> None:
        r = client.get("/auth/me", headers={"Authorization": "Bearer not.a.token"})
        assert r.status_code == 401

    def test_shadowban_is_not_visible_to_user(self, client: TestClient) -> None:
        """Смысл теневого бана в том, что о нём не сообщают."""
        token = _register(client)["access_token"]
        body = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"}).json()
        assert "is_shadowbanned" not in body


class TestRefreshRotation:
    def test_refresh_returns_new_pair(self, client: TestClient) -> None:
        old = _register(client)["refresh_token"]
        r = client.post("/auth/refresh", json={"refresh_token": old})
        assert r.status_code == 200
        assert r.json()["refresh_token"] != old

    def test_reused_token_revokes_whole_family(self, client: TestClient) -> None:
        """Повторное предъявление означает, что копию токена украли.
        Кто легитимен — неизвестно, поэтому обрывается вся цепочка."""
        first = _register(client)["refresh_token"]
        second = client.post("/auth/refresh", json={"refresh_token": first}).json()["refresh_token"]

        assert client.post("/auth/refresh", json={"refresh_token": first}).status_code == 401
        # и выданный следом токен тоже перестал работать
        assert client.post("/auth/refresh", json={"refresh_token": second}).status_code == 401

    def test_logout_revokes_session(self, client: TestClient) -> None:
        token = _register(client)["refresh_token"]
        assert client.post("/auth/logout", json={"refresh_token": token}).status_code == 204
        assert client.post("/auth/refresh", json={"refresh_token": token}).status_code == 401

    def test_unknown_refresh_token_rejected(self, client: TestClient) -> None:
        assert client.post("/auth/refresh", json={"refresh_token": "nope"}).status_code == 401
