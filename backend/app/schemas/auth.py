from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_serializer

from app.models import Role


class RegisterRequest(BaseModel):
    """Поля `role` здесь намеренно нет.

    В прежней версии оно было — `role: str = "student"` — и принималось от клиента,
    то есть любой мог зарегистрироваться владельцем платформы. Роль назначает
    только сервер.
    """

    username: str = Field(min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_-]+$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1, max_length=256)


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    roles: list[Role]
    subscription_tier: str
    points: int
    coins: int
    streak_days: int
    longest_streak: int
    level: str
    avatar_url: str
    bio: str
    github_url: str
    theme: str
    is_in_trial: bool
    daily_coins_earned: int
    daily_coin_limit: int
    xp_multiplier: float
    focus_mode: bool

    # `is_shadowbanned` наружу не отдаётся: смысл теневого бана в том,
    # что нарушитель о нём не знает.

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    @field_serializer("roles")
    def _roles_as_names(self, roles: list[Role]) -> list[str]:
        return sorted(str(r.name) for r in roles)


class SessionResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=32)
    bio: str | None = Field(default=None, max_length=1000)
    avatar_url: str | None = None
    github_url: str | None = None
    theme: str | None = None
    focus_mode: bool | None = None
