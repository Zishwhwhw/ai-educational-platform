"""Раскрытие подсказок.

Прежний эндпоинт жил в роутере отправки и возвращал заготовленный текст,
не связанный ни с задачей, ни с кодом ученика. Здесь ступень раскрывается
для конкретной отправки, штраф к награде считается и запоминается.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.core.errors import AppError, NotFoundError
from app.db.session import get_db
from app.models import HintEvent, Submission, Task
from app.services.hints import (
    MAX_LEVEL,
    UNLOCK_AFTER_FAILURES,
    HintNotUnlockedError,
    reveal,
    reward_multiplier,
)

router = APIRouter(prefix="/hints", tags=["hints"])


class HintLockedError(AppError):
    code = "hint_locked"
    status_code = status.HTTP_409_CONFLICT
    message = "This hint level is not unlocked yet"


class RevealRequest(BaseModel):
    submission_id: int
    level: int = Field(ge=1, le=MAX_LEVEL)


class HintResponse(BaseModel):
    level: int
    text: str
    generated: bool
    reward_multiplier: float
    max_level: int = MAX_LEVEL


class HintStateResponse(BaseModel):
    """Состояние лестницы для одной задачи.

    Отдаётся до раскрытия, чтобы интерфейс мог назвать штраф заранее:
    ступени необратимы, и узнавать цену после оплаты неприемлемо.
    """

    failed_attempts: int
    revealed_level: int
    next_level: int | None
    next_unlocks_after_failures: int | None
    next_reward_multiplier: float | None
    revealed: list[HintResponse]


def _load(db: Session, submission_id: int, user_id: int) -> tuple[Submission, Task]:
    submission = db.get(Submission, submission_id)
    # 404 на чужую отправку, а не 403: иначе перебором идентификаторов
    # можно узнать, какие отправки существуют.
    if submission is None or int(submission.user_id) != user_id:
        raise NotFoundError("Submission not found")
    task = db.get(Task, submission.task_id)
    if task is None:
        raise NotFoundError("Task not found")
    return submission, task


def _failed_attempts(db: Session, user_id: int, task_id: int) -> int:
    return int(
        db.execute(
            select(func.count())
            .select_from(Submission)
            .where(
                Submission.user_id == user_id,
                Submission.task_id == task_id,
                Submission.status != "correct",
            )
        ).scalar_one()
    )


def _revealed_level(db: Session, user_id: int, task_id: int) -> int:
    return int(
        db.execute(
            select(func.coalesce(func.max(HintEvent.level), 0)).where(
                HintEvent.user_id == user_id, HintEvent.task_id == task_id
            )
        ).scalar_one()
    )


@router.get("/task/{task_id}", response_model=HintStateResponse)
def get_state(
    task_id: int,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> HintStateResponse:
    failed = _failed_attempts(db, int(current_user.id), task_id)
    revealed = _revealed_level(db, int(current_user.id), task_id)
    nxt = revealed + 1 if revealed < MAX_LEVEL else None

    return HintStateResponse(
        failed_attempts=failed,
        revealed_level=revealed,
        next_level=nxt,
        next_unlocks_after_failures=UNLOCK_AFTER_FAILURES.get(nxt) if nxt else None,
        next_reward_multiplier=reward_multiplier(nxt) if nxt else None,
        revealed=[],
    )


@router.post("/reveal", response_model=HintResponse)
async def reveal_hint(
    payload: RevealRequest,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> HintResponse:
    submission, task = _load(db, payload.submission_id, int(current_user.id))

    spec = next((s for s in task.languages if str(s.language) == str(submission.language)), None)
    if spec is None:
        raise NotFoundError("Task language configuration not found")

    failed = _failed_attempts(db, int(current_user.id), int(task.id))

    try:
        hint = await reveal(
            level=payload.level,
            task=task,
            language_spec=spec,
            submission=submission,
            failed_attempts=failed,
        )
    except HintNotUnlockedError as exc:
        raise HintLockedError(
            str(exc), level=exc.level, required_failures=exc.required_failures
        ) from exc

    # Записываем только реально выданные подсказки: если наставник недоступен,
    # ступень не считается раскрытой и баллы не снимаются.
    if hint.reward_multiplier < 1.0:
        db.add(
            HintEvent(
                user_id=current_user.id,
                task_id=task.id,
                submission_id=submission.id,
                level=hint.level,
                generated=hint.generated,
                cost_usd=hint.cost_usd,
            )
        )
        db.commit()

    return HintResponse(
        level=hint.level,
        text=hint.text,
        generated=hint.generated,
        reward_multiplier=hint.reward_multiplier,
    )
