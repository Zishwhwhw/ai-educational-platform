from datetime import timedelta

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.time import utcnow
from app.db.base import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    # Колонка `role` удалена: роли живут в таблице `user_roles` (решение B4).
    subscription_tier = Column(String, default="free")
    points = Column(Integer, default=0)
    coins = Column(Integer, default=0)
    xp_multiplier = Column(Float, default=1.0)
    streak_days = Column(Integer, default=0)
    streak_freeze_count = Column(Integer, default=2)
    longest_streak = Column(Integer, default=0)
    last_activity = Column(DateTime, default=utcnow)
    is_shadowbanned = Column(Boolean, default=False)
    is_in_trial = Column(Boolean, default=True)
    trial_end_date = Column(DateTime, default=lambda: utcnow() + timedelta(days=30))
    daily_coins_earned = Column(Integer, default=0)
    daily_coin_limit = Column(Integer, default=100)
    avatar_url = Column(String, default="")
    bio = Column(Text, default="")
    github_url = Column(String, default="")
    theme = Column(String, default="dark")
    level = Column(String, default="Junior")
    clan_id = Column(Integer, ForeignKey("clans.id"), nullable=True)
    focus_mode = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)

    courses_taught = relationship("Course", back_populates="teacher")
    progress = relationship("Progress", back_populates="user")
    submissions = relationship("Submission", back_populates="user")
    achievements = relationship("UserAchievement", back_populates="user")
    purchases = relationship("UserPurchase", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    flashcards = relationship("Flashcard", back_populates="user")
    sent_messages = relationship(
        "PrivateMessage", foreign_keys="PrivateMessage.sender_id", back_populates="sender"
    )
    received_messages = relationship(
        "PrivateMessage", foreign_keys="PrivateMessage.receiver_id", back_populates="receiver"
    )
    comments = relationship("Comment", back_populates="user")
    roles = relationship("Role", secondary="user_roles", back_populates="users", lazy="selectin")
    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
