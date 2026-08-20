"""Шаги урока: выдача и проверка ответов.

Правило видимости здесь то же, что у скрытых тестов: **поле `grading`
не покидает сервер ни при каких условиях.** Клиенту уходит только `content`,
и дополнительно прогоняется через фильтр — на случай, если правильный ответ
по недосмотру окажется не в том поле.
"""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.core.errors import AppError, NotFoundError
from app.db.session import get_db
from app.models import Lesson, Step, StepAttempt
from app.services.steps import InvalidAnswerError, check, public_content

router = APIRouter(tags=["steps"])


class BadAnswerError(AppError):
    code = "invalid_answer"
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    message = "Answer has the wrong shape for this step type"


class StepResponse(BaseModel):
    id: int
    type: str
    ordering: int
    points_value: int
    content: dict[str, Any]
    # Прогресс текущего пользователя по шагу.
    is_completed: bool
    best_score: float
    attempts: int


class AnswerRequest(BaseModel):
    answer: dict[str, Any] = Field(default_factory=dict)


class AnswerResponse(BaseModel):
    is_correct: bool
    score: float
    points_awarded: int
    attempts: int
    detail: dict[str, Any] | None = None


def _progress(db: Session, user_id: int, step_ids: list[int]) -> dict[int, tuple[float, int, bool]]:
    """Лучший результат, число попыток и признак прохождения — одним запросом."""
    if not step_ids:
        return {}
    rows = db.execute(
        select(
            StepAttempt.step_id,
            func.max(StepAttempt.score),
            func.count(StepAttempt.id),
            func.bool_or(StepAttempt.is_correct),
        )
        .where(StepAttempt.user_id == user_id, StepAttempt.step_id.in_(step_ids))
        .group_by(StepAttempt.step_id)
    ).all()
    return {int(r[0]): (float(r[1] or 0.0), int(r[2]), bool(r[3])) for r in rows}


@router.get("/lessons/{lesson_id}/steps", response_model=list[StepResponse])
def list_steps(
    lesson_id: int,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> list[StepResponse]:
    lesson = db.get(Lesson, lesson_id)
    if lesson is None:
        raise NotFoundError("Lesson not found")

    steps = sorted(lesson.steps, key=lambda s: int(s.ordering))
    progress = _progress(db, int(current_user.id), [int(s.id) for s in steps])

    return [
        StepResponse(
            id=int(s.id),
            type=str(s.type),
            ordering=int(s.ordering),
            points_value=int(s.points_value),
            # `grading` сюда не попадает. Никогда.
            content=public_content(str(s.type), dict(s.content or {})),
            best_score=progress.get(int(s.id), (0.0, 0, False))[0],
            attempts=progress.get(int(s.id), (0.0, 0, False))[1],
            is_completed=progress.get(int(s.id), (0.0, 0, False))[2],
        )
        for s in steps
    ]


@router.post("/steps/{step_id}/answer", response_model=AnswerResponse)
def answer_step(
    step_id: int,
    payload: AnswerRequest,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> AnswerResponse:
    step = db.get(Step, step_id)
    if step is None:
        raise NotFoundError("Step not found")

    try:
        result = check(str(step.type), dict(step.grading or {}), payload.answer)
    except InvalidAnswerError as exc:
        raise BadAnswerError(str(exc)) from exc

    points = int(int(step.points_value) * result.score)

    db.add(
        StepAttempt(
            user_id=current_user.id,
            step_id=step.id,
            is_correct=result.is_correct,
            score=result.score,
            points_awarded=points,
            answer=payload.answer,
        )
    )
    db.commit()

    attempts = int(
        db.execute(
            select(func.count())
            .select_from(StepAttempt)
            .where(StepAttempt.user_id == current_user.id, StepAttempt.step_id == step.id)
        ).scalar_one()
    )

    return AnswerResponse(
        is_correct=result.is_correct,
        score=result.score,
        points_awarded=points,
        attempts=attempts,
        detail=result.detail,
    )
