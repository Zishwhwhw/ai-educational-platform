"""Шаг урока.

До этого урок мог содержать только задания на код. Курс из одних задач
выматывает: спека требует разнообразия шагов, и это не украшение —
чередование теории, проверки понимания и практики держит человека дольше.

Модель полиморфная: тип шага — строка, а его данные лежат в двух полях JSONB.
Альтернативы были хуже:

* таблица на каждый тип — девять почти одинаковых таблиц и миграция
  на каждый новый тип;
* одна плоская таблица со всеми возможными колонками — большинство пустые.

**Разделение `content` и `grading` — главное здесь.** `content` уходит клиенту,
`grading` не уходит никогда: в нём лежат правильные ответы. Если хранить их
вместе, рано или поздно кто-нибудь отдаст объект целиком, и все шаги
с выбором ответа обесценятся молча.
"""

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

from app.core.time import utcnow
from app.db.base import Base

# JSONB на Postgres, обычный JSON на SQLite в тестах.
JSONType = JSON().with_variant(JSONB(), "postgresql")


class Step(Base):
    __tablename__ = "steps"

    id = Column(Integer, primary_key=True)
    lesson_id = Column(
        Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Строка, а не enum: добавление типа не должно требовать миграции.
    # Допустимые значения проверяет реестр обработчиков.
    type = Column(String(32), nullable=False)
    ordering = Column(Integer, default=0, nullable=False)
    points_value = Column(Integer, default=5, nullable=False)

    # Публичная часть: вопрос, варианты, текст теории. Уходит клиенту как есть.
    content = Column(JSONType, nullable=False, default=dict)
    # Приватная часть: правильные ответы. Клиенту не уходит никогда.
    grading = Column(JSONType, nullable=False, default=dict)

    lesson = relationship("Lesson", back_populates="steps")
    attempts = relationship("StepAttempt", back_populates="step", cascade="all, delete-orphan")


class StepAttempt(Base):
    """Попытка прохождения шага.

    Хранится каждая, а не только последняя: по числу попыток работает
    эскалация подсказок, а распределение попыток по шагам показывает,
    какие из них сформулированы плохо.
    """

    __tablename__ = "step_attempts"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    step_id = Column(
        Integer, ForeignKey("steps.id", ondelete="CASCADE"), nullable=False, index=True
    )

    is_correct = Column(Boolean, default=False, nullable=False)
    score = Column(Float, default=0.0, nullable=False)
    points_awarded = Column(Integer, default=0, nullable=False)
    answer = Column(JSONType, nullable=False, default=dict)
    submitted_at = Column(DateTime, default=utcnow, nullable=False)

    step = relationship("Step", back_populates="attempts")
