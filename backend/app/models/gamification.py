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


class Achievement(Base):
    __tablename__ = "achievements"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(Text)
    icon = Column(String, default="🏆")
    category = Column(String, default="general")
    required_value = Column(Integer, default=1)


class UserAchievement(Base):
    __tablename__ = "user_achievements"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    achievement_id = Column(Integer, ForeignKey("achievements.id"))
    unlocked_at = Column(DateTime, default=utcnow)
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement")


class StoreItem(Base):
    __tablename__ = "store_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text)
    price_coins = Column(Integer)
    item_type = Column(String, default="theme")
    image_url = Column(String, default="")
    rarity = Column(String, default="common")


class UserPurchase(Base):
    __tablename__ = "user_purchases"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(Integer, ForeignKey("store_items.id"))
    purchased_at = Column(DateTime, default=utcnow)
    user = relationship("User", back_populates="purchases")
    item = relationship("StoreItem")


class Flashcard(Base):
    __tablename__ = "flashcards"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question = Column(Text)
    answer = Column(Text)
    next_review = Column(DateTime, default=utcnow)
    interval_days = Column(Integer, default=1)
    ease_factor = Column(Float, default=2.5)
    repetitions = Column(Integer, default=0)
    user = relationship("User", back_populates="flashcards")


class DoubleXPEvent(Base):
    __tablename__ = "double_xp_events"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    multiplier = Column(Float, default=2.0)
    starts_at = Column(DateTime)
    ends_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
