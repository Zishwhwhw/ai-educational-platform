"""Пароли и токены.

Заменяет самописные `app/auth/jwt_handler.py` и `app/auth/password.py`.

Что было и почему заменено:

* **Пароль** — PBKDF2-SHA256, 100 000 итераций. Не катастрофа, но PBKDF2 хорошо
  параллелится на GPU. Argon2id устойчив к этому по построению (требует памяти)
  и является текущей рекомендацией OWASP.
* **JWT** — собирался вручную из base64 и hmac. Подпись сравнивалась через
  `compare_digest`, то есть очевидной дыры не было, но самописный разбор токена
  легко ломается при доработках. PyJWT проверяет `exp`, `iat`, `nbf`, `aud`
  и фиксирует алгоритм — то, что в ручной реализации приходится помнить самому.

Refresh-токены здесь **не JWT**: это случайные строки, в базе лежат только их
хеши. JWT нельзя отозвать, а refresh отзывать необходимо.
"""

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from app.core.config import get_settings

_settings = get_settings()
_hasher = PasswordHasher()

ALGORITHM = "HS256"
TokenType = Literal["access", "refresh"]


# --- пароли -------------------------------------------------------------------


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        _hasher.verify(hashed, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False
    return True


def password_needs_rehash(hashed: str) -> bool:
    """True, если хеш сделан старыми параметрами и стоит пересчитать при входе."""
    try:
        return _hasher.check_needs_rehash(hashed)
    except InvalidHashError:
        # Хеш из старой самописной схемы (`salt:key`) — пересчитать обязательно.
        return True


# --- access-токен ---------------------------------------------------------------


class TokenError(Exception):
    """Токен отсутствует, испорчен, просрочен или не того типа."""


def create_access_token(*, user_id: int, roles: list[str]) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "roles": roles,
        "typ": "access",
        "jti": uuid.uuid4().hex,
        "iat": now,
        "exp": now + timedelta(minutes=_settings.access_token_ttl_minutes),
    }
    return jwt.encode(payload, _settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            _settings.secret_key,
            algorithms=[ALGORITHM],  # список фиксирован: защита от подмены alg
            options={"require": ["exp", "iat", "sub", "typ"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise TokenError("Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise TokenError("Invalid token") from exc

    if payload.get("typ") != "access":
        # Иначе refresh-токен сгодился бы как access, и короткий срок жизни
        # access-токена терял бы смысл.
        raise TokenError("Wrong token type")
    return payload


# --- refresh-токен ---------------------------------------------------------------


def generate_refresh_token() -> str:
    """Непрозрачная случайная строка. В базу кладётся только её хеш."""
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    """SHA-256, а не argon2: токен и так случайный на 384 бита, растягивать нечего,
    а проверять его приходится на каждом обновлении сессии."""
    return hashlib.sha256(token.encode()).hexdigest()


def refresh_token_expiry() -> datetime:
    return datetime.now(UTC) + timedelta(days=_settings.refresh_token_ttl_days)
