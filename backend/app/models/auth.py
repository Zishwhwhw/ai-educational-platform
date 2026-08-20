from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.time import utcnow
from app.db.base import Base

# Роли аддитивны: преподаватель одновременно ученик, модератор одновременно
# ученик. Одна колонка `role` этого выразить не может, поэтому many-to-many.
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="RESTRICT"), primary_key=True),
    Column("granted_at", DateTime, default=utcnow, nullable=False),
)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True, nullable=False, index=True)
    description = Column(String(200), default="")

    users = relationship("User", secondary=user_roles, back_populates="roles")


class RefreshToken(Base):
    """Сессия пользователя.

    Хранится только SHA-256 от токена: утечка базы не даёт войти под чужой учёткой.

    `family_id` связывает цепочку обновлений одной сессии. При обновлении старый
    токен помечается использованным и выдаётся новый из той же семьи. Если
    предъявлен уже использованный токен — значит его украли и им воспользовались
    параллельно; вся семья отзывается разом.
    """

    __tablename__ = "refresh_tokens"
    __table_args__ = (UniqueConstraint("token_hash", name="uq_refresh_tokens_token_hash"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_hash = Column(String(64), nullable=False, index=True)
    family_id = Column(String(32), nullable=False, index=True)

    issued_at = Column(DateTime, default=utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)

    # Для расследования: с какого устройства и адреса выдан токен.
    user_agent = Column(String(400), default="")
    ip_address = Column(String(45), default="")

    is_active = Column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="refresh_tokens")
