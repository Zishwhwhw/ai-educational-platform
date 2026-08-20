"""Регистрация, вход, обновление сессии, выход.

Что исправлено по сравнению с прежней версией:

1. **Роль больше не принимается от клиента.** Было `role=user.role`, где `role`
   приходил в теле запроса со значением по умолчанию `"student"` — то есть любой
   мог зарегистрироваться владельцем платформы. Теперь новому пользователю
   всегда выдаётся ровно роль `student`.
2. **Одинаковый ответ на несуществующий email и неверный пароль.** Раньше разницы
   не было по тексту, но была по времени: при отсутствии пользователя проверка
   пароля не выполнялась вовсе, и ответ приходил заметно быстрее. Это позволяло
   перебором выяснять, какие адреса зарегистрированы. Теперь хеш проверяется
   всегда, даже против пустышки.
3. **Появились refresh-токены** с ротацией и обнаружением повторного использования.
   Access-токен живёт 15 минут вместо суток.
"""

import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, client_fingerprint
from app.core.errors import AppError, ConflictError
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    password_needs_rehash,
    refresh_token_expiry,
    verify_password,
)
from app.db.session import get_db
from app.models import RefreshToken, Role, User
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    SessionResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])

# Хеш заведомо недостижимого пароля: сверяемся с ним, когда пользователь не найден,
# чтобы время ответа не выдавало наличие учётной записи.
_DUMMY_HASH = hash_password("not-a-real-password-" + uuid.uuid4().hex)


class InvalidCredentialsError(AppError):
    code = "invalid_credentials"
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid email or password"


class InvalidRefreshTokenError(AppError):
    code = "invalid_refresh_token"
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Refresh token is invalid or expired"


def _issue_session(
    db: Session, user: User, request: Request, *, family_id: str | None = None
) -> SessionResponse:
    """Выдать пару токенов. `family_id` продолжает существующую сессию."""
    raw_refresh = generate_refresh_token()
    user_agent, ip = client_fingerprint(request)

    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(raw_refresh),
            family_id=family_id or uuid.uuid4().hex,
            expires_at=refresh_token_expiry(),
            user_agent=user_agent,
            ip_address=ip,
        )
    )
    db.commit()

    roles = sorted(str(r.name) for r in user.roles)
    return SessionResponse(
        access_token=create_access_token(user_id=int(user.id), roles=roles),
        refresh_token=raw_refresh,
        user=UserResponse.model_validate(user),
    )


@router.post("/register", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> SessionResponse:
    exists = db.execute(
        select(User).where((User.email == payload.email) | (User.username == payload.username))
    ).scalar_one_or_none()
    if exists is not None:
        # Один текст на оба случая: иначе форма регистрации превращается
        # в способ проверять, занят ли адрес.
        raise ConflictError("Email or username is already taken")

    student_role = db.execute(select(Role).where(Role.name == "student")).scalar_one()

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    # Роль назначается сервером и только `student`. Повышение — отдельной
    # операцией администратора, недоступной при регистрации.
    user.roles.append(student_role)

    db.add(user)
    db.commit()
    db.refresh(user)
    return _issue_session(db, user, request)


@router.post("/login", response_model=SessionResponse)
def login(
    payload: LoginRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> SessionResponse:
    user = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()

    # Проверяем хеш в любом случае — против перебора существующих адресов по времени ответа.
    stored_hash = str(user.hashed_password) if user else _DUMMY_HASH
    password_ok = verify_password(payload.password, stored_hash)

    if user is None or not password_ok:
        raise InvalidCredentialsError

    # Прозрачный переход со старой схемы хеширования: пересчитываем при первом входе.
    if password_needs_rehash(stored_hash):
        user.hashed_password = hash_password(payload.password)
        db.commit()

    return _issue_session(db, user, request)


@router.post("/refresh", response_model=SessionResponse)
def refresh(
    payload: RefreshRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> SessionResponse:
    token = db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_refresh_token(payload.refresh_token)
        )
    ).scalar_one_or_none()

    if token is None:
        raise InvalidRefreshTokenError

    now = datetime.now(UTC).replace(tzinfo=None)

    if token.used_at is not None:
        # Токен уже обменивали. Значит копия попала к кому-то ещё и была
        # использована параллельно. Кто именно легитимен — неизвестно, поэтому
        # обрываем всю цепочку: настоящему пользователю придётся войти заново.
        db.query(RefreshToken).filter(
            RefreshToken.family_id == token.family_id,
            RefreshToken.revoked_at.is_(None),
        ).update({"revoked_at": now, "is_active": False})
        db.commit()
        raise InvalidRefreshTokenError("Token reuse detected — all sessions revoked")

    if token.revoked_at is not None or not token.is_active or token.expires_at <= now:
        raise InvalidRefreshTokenError

    user = db.execute(select(User).where(User.id == token.user_id)).scalar_one_or_none()
    if user is None:
        raise InvalidRefreshTokenError

    token.used_at = now
    token.is_active = False
    return _issue_session(db, user, request, family_id=str(token.family_id))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    payload: RefreshRequest,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    """Отзывает всю семью токенов — выходит вся сессия, а не одно обновление."""
    token = db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_refresh_token(payload.refresh_token)
        )
    ).scalar_one_or_none()
    if token is not None:
        now = datetime.now(UTC).replace(tzinfo=None)
        db.query(RefreshToken).filter(
            RefreshToken.family_id == token.family_id,
            RefreshToken.revoked_at.is_(None),
        ).update({"revoked_at": now, "is_active": False})
        db.commit()
    # 204 в любом случае: несуществующий токен не повод сообщать об этом.
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserResponse)
def me(user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(user)
