"""Выдача задания ученику.

Отдельный роутер, потому что правило видимости здесь важнее всего:
**скрытые тесты не попадают в ответ вовсе**, ученик знает только их количество.
Видимые отдаются целиком — они объясняют, чего от него хотят.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.core.errors import NotFoundError
from app.db.session import get_db
from app.models import Task
from app.schemas.course import (
    TaskDetailResponse,
    TaskLanguageResponse,
    VisibleTestCaseResponse,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/{task_id}", response_model=TaskDetailResponse)
def get_task(
    task_id: int,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> TaskDetailResponse:
    task = db.get(Task, task_id)
    if task is None:
        raise NotFoundError("Task not found")

    visible = [c for c in task.test_cases if not bool(c.is_hidden)]
    hidden_count = sum(1 for c in task.test_cases if bool(c.is_hidden))

    return TaskDetailResponse(
        id=int(task.id),
        lesson_id=int(task.lesson_id),
        prompt=str(task.prompt or ""),
        difficulty=str(task.difficulty),
        points_value=int(task.points_value),
        comparison=str(task.comparison),
        languages=[TaskLanguageResponse.model_validate(s) for s in task.languages],
        visible_tests=[VisibleTestCaseResponse.model_validate(c) for c in visible],
        hidden_test_count=hidden_count,
    )
