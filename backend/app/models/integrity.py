from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)

from app.core.time import utcnow
from app.db.base import Base


class AntiFraudLog(Base):
    __tablename__ = "antifraud_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_type = Column(String)
    details = Column(Text)
    created_at = Column(DateTime, default=utcnow)


class Appeal(Base):
    __tablename__ = "appeals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reason = Column(Text)
    status = Column(String, default="pending")
    response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)
