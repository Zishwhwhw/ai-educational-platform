from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.time import utcnow
from app.db.base import Base


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    language = Column(String, default="python")
    difficulty = Column(String, default="beginner")
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_ai_generated = Column(Boolean, default=False)
    is_preinstalled = Column(Boolean, default=False)
    base_price = Column(Float, default=0.0)
    target_points = Column(Integer, default=1700)
    image_url = Column(String, default="")
    created_at = Column(DateTime, default=utcnow)

    teacher = relationship("User", back_populates="courses_taught")
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")


class Module(Base):
    __tablename__ = "modules"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String)
    order = Column(Integer)
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan")


class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"))
    title = Column(String)
    content_type = Column(String, default="text")
    content = Column(Text, nullable=True)
    video_url = Column(String, nullable=True)
    min_read_time = Column(Integer, default=300)
    points_value = Column(Integer, default=5)
    order = Column(Integer, default=0)
    module = relationship("Module", back_populates="lessons")
    tasks = relationship("Task", back_populates="lesson", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="lesson")


class Task(Base):
    """Задание на написание кода.

    Прежние поля `expected_output` и `test_cases` (обе — свободный текст) удалены.
    Проверка по ним была фиктивной: код сравнивался с ожидаемым выводом
    подстрокой и никогда не запускался. Теперь тесты живут в таблице `test_cases`,
    а параметры запуска — в `task_languages`.
    """

    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    difficulty = Column(String, default="easy")
    prompt = Column(Text)
    points_value = Column(Integer, default=25)

    # Как сравнивать вывод программы с ожидаемым. Вынесено в данные, а не в код:
    # для задачи на форматирование важен каждый пробел, для задачи на арифметику —
    # нет, и автор задания должен решать это сам.
    comparison = Column(String(20), default="trim", nullable=False)
    float_tolerance = Column(Float, default=1e-6, nullable=False)

    lesson = relationship("Lesson", back_populates="tasks")
    submissions = relationship("Submission", back_populates="task")
    languages = relationship(
        "TaskLanguage", back_populates="task", cascade="all, delete-orphan", lazy="selectin"
    )
    hints = relationship(
        "TaskHint", back_populates="task", cascade="all, delete-orphan", lazy="selectin"
    )
    test_cases = relationship(
        "TestCase",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="TestCase.ordering",
        lazy="selectin",
    )


class TaskLanguage(Base):
    """Параметры задания для конкретного языка.

    Одно задание может решаться на нескольких языках, и лимиты у них разные:
    то, что Python успевает за 5 секунд, C++ делает за 50 миллисекунд.
    """

    __tablename__ = "task_languages"
    __table_args__ = (
        UniqueConstraint("task_id", "language", name="uq_task_languages_task_language"),
    )

    id = Column(Integer, primary_key=True)
    task_id = Column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    language = Column(String(32), nullable=False)

    starter_code = Column(Text, default="")
    # Эталон нужен для проверки самого задания: если он не проходит собственные
    # тесты, задание сломано и показывать его ученику нельзя.
    reference_solution = Column(Text, default="")

    time_limit_ms = Column(Integer, default=5000, nullable=False)
    memory_limit_mb = Column(Integer, default=128, nullable=False)

    task = relationship("Task", back_populates="languages")


class TestCase(Base):
    """Один тест: подаём на вход, ждём на выходе.

    `is_hidden` определяет, показывать ли содержимое ученику. Видимые тесты
    объясняют, чего от него хотят; скрытые не дают подогнать решение под ответ.
    """

    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True)
    task_id = Column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )

    name = Column(String(120), default="")
    stdin = Column(Text, default="")
    expected_stdout = Column(Text, default="")

    is_hidden = Column(Boolean, default=False, nullable=False)
    # Вес: тест на граничный случай может стоить дороже тривиального.
    weight = Column(Integer, default=1, nullable=False)
    ordering = Column(Integer, default=0, nullable=False)

    task = relationship("Task", back_populates="test_cases")
