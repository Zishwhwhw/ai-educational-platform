from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.time import utcnow
from app.db.base import Base


class TaskHint(Base):
    """Заготовленная автором наводка — вторая ступень лестницы.

    Автор знает, где спотыкаются на его задаче, поэтому заготовка дешевле
    и точнее генерации. `symptom` связывает наводку с конкретным провалившимся
    тестом; наводка без симптома — общая, показывается когда ни одна
    не подошла.
    """

    __tablename__ = "task_hints"

    id = Column(Integer, primary_key=True)
    task_id = Column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    text = Column(Text, nullable=False)
    symptom = Column(String(120), default="")
    ordering = Column(Integer, default=0, nullable=False)

    task = relationship("Task", back_populates="hints")


class HintEvent(Base):
    """Журнал раскрытий.

    Нужен по трём причинам: посчитать штраф к награде, не брать деньги дважды
    за одну и ту же ступень, и увидеть на каких задачах все доходят до пятой —
    это признак сломанного задания, а не слабых учеников.
    """

    __tablename__ = "hint_events"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    task_id = Column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    submission_id = Column(
        Integer, ForeignKey("submissions.id", ondelete="SET NULL"), nullable=True
    )

    level = Column(Integer, nullable=False)
    generated = Column(Boolean, default=False, nullable=False)
    cost_usd = Column(Float, default=0.0, nullable=False)
    revealed_at = Column(DateTime, default=utcnow, nullable=False)
