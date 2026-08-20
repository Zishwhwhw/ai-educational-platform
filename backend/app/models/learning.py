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


class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"))
    code = Column(Text)
    status = Column(String, default="pending")
    points_awarded = Column(Integer, default=0)
    hint_level = Column(Integer, default=0)
    feedback = Column(Text, nullable=True)
    started_at = Column(DateTime, default=utcnow)
    submitted_at = Column(DateTime, default=utcnow)
    user = relationship("User", back_populates="submissions")
    task = relationship("Task", back_populates="submissions")
    # Итог прогона: сколько тестов прошло и какой частичный балл.
    language = Column(String(32), default="python")
    tests_passed = Column(Integer, default=0, nullable=False)
    tests_total = Column(Integer, default=0, nullable=False)
    score = Column(Float, default=0.0, nullable=False)

    reviews = relationship("PeerReview", back_populates="submission")
    results = relationship(
        "SubmissionResult", back_populates="submission", cascade="all, delete-orphan"
    )


class SubmissionResult(Base):
    """Исход одного теста в рамках одной отправки.

    Хранится отдельной строкой, а не свёрткой в JSON: по этим данным строятся
    подсказки третьей ступени («какой именно тест не прошёл») и статистика
    сложности заданий.
    """

    __tablename__ = "submission_results"

    id = Column(Integer, primary_key=True)
    submission_id = Column(
        Integer, ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    test_case_id = Column(Integer, ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False)

    passed = Column(Boolean, default=False, nullable=False)
    status = Column(String(24), default="ok", nullable=False)
    actual_stdout = Column(Text, default="")
    stderr = Column(Text, default="")
    time_ms = Column(Integer, nullable=True)
    memory_kb = Column(Integer, nullable=True)

    submission = relationship("Submission", back_populates="results")


class Progress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    is_completed = Column(Boolean, default=False)
    points_awarded = Column(Integer, default=0)
    time_spent = Column(Integer, default=0)
    started_at = Column(DateTime, default=utcnow)
    completed_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="progress")


class PeerReview(Base):
    __tablename__ = "peer_reviews"
    id = Column(Integer, primary_key=True, index=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    submission_id = Column(Integer, ForeignKey("submissions.id"))
    score = Column(Integer, default=0)
    feedback = Column(Text)
    created_at = Column(DateTime, default=utcnow)
    reviewer = relationship("User")
    submission = relationship("Submission", back_populates="reviews")
