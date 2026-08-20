"""Зависимости FastAPI: текущий пользователь и проверка ролей.

До этого модуля защиты не было вообще: эндпоинты принимали `user_id: int = 1`
параметром запроса, то есть любой запрос выполнялся от имени любого пользователя.

Здесь два набора зависимостей — синхронный и асинхронный. Синхронный нужен
унаследованным роутерам (39 эндпоинтов объявлены как `def`), асинхронный —
новому коду. Логика разбора токена общая, дублируется только доступ к базе.
"""

from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from app.core.errors import AppError, PermissionDeniedError
from app.core.security import TokenError, decode_access_token
from app.db.session import get_async_db, get_db
from app.models import User

# auto_error=False: без заголовка хотим свою ошибку в общем формате,
# а не стандартную от Starlette.
_bearer = HTTPBearer(auto_error=False)


class NotAuthenticatedError(AppError):
    code = "not_authenticated"
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Authentication required"


def _user_id_from_token(creds: HTTPAuthorizationCredentials | None) -> int:
    if creds is None or not creds.credentials:
        raise NotAuthenticatedError("Missing bearer token")
    try:
        payload = decode_access_token(creds.credentials)
    except TokenError as exc:
        raise NotAuthenticatedError(str(exc)) from exc
    try:
        return int(payload["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise NotAuthenticatedError("Malformed token subject") from exc


def _ensure_usable(user: User | None) -> User:
    if user is None:
        # Токен подписан нами, но пользователя нет — учётку удалили.
        # Отвечаем 401, а не 404: наличие или отсутствие чужой учётки не наше дело.
        raise NotAuthenticatedError("User no longer exists")
    if bool(user.is_shadowbanned):
        # Теневой бан: пользователь работает как обычно, но исключён из
        # рейтингов и наград. Блокировать вход здесь нельзя — иначе бан
        # перестаёт быть теневым.
        pass
    return user


# --- синхронные (унаследованные роутеры) ---------------------------------------


def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    user_id = _user_id_from_token(creds)
    user = db.execute(
        select(User).options(selectinload(User.roles)).where(User.id == user_id)
    ).scalar_one_or_none()
    return _ensure_usable(user)


def get_current_user_optional(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    db: Annotated[Session, Depends(get_db)],
) -> User | None:
    if creds is None:
        return None
    try:
        return get_current_user(creds, db)
    except NotAuthenticatedError:
        return None


# --- асинхронные (новый код) ----------------------------------------------------


async def get_current_user_async(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> User:
    user_id = _user_id_from_token(creds)
    result = await db.execute(
        select(User).options(selectinload(User.roles)).where(User.id == user_id)
    )
    return _ensure_usable(result.scalar_one_or_none())


# --- проверка ролей --------------------------------------------------------------


def user_role_names(user: User) -> set[str]:
    return {str(r.name) for r in user.roles}


def require_roles(*required: str) -> Callable[[User], User]:
    """Пускает, если у пользователя есть **любая** из перечисленных ролей.

    Роли аддитивны, поэтому проверка «есть ли хоть одна» — верная семантика:
    `require_roles("moderator", "admin")` пропустит и модератора, и админа.
    """
    allowed = set(required)

    def dependency(user: Annotated[User, Depends(get_current_user)]) -> User:
        if not (allowed & user_role_names(user)):
            raise PermissionDeniedError(
                f"Requires one of: {', '.join(sorted(allowed))}",
                required_roles=sorted(allowed),
            )
        return user

    return dependency


def require_roles_async(*required: str) -> Callable[[User], Awaitable[User]]:
    allowed = set(required)

    async def dependency(user: Annotated[User, Depends(get_current_user_async)]) -> User:
        if not (allowed & user_role_names(user)):
            raise PermissionDeniedError(
                f"Requires one of: {', '.join(sorted(allowed))}",
                required_roles=sorted(allowed),
            )
        return user

    return dependency


def client_fingerprint(request: Request) -> tuple[str, str]:
    """User-Agent и IP для журнала сессий. Нужны при расследовании кражи токена."""
    forwarded = request.headers.get("X-Forwarded-For", "")
    ip = (
        forwarded.split(",")[0].strip()
        if forwarded
        else (request.client.host if request.client else "")
    )
    return request.headers.get("User-Agent", "")[:400], ip[:45]


CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentUserAsync = Annotated[User, Depends(get_current_user_async)]
