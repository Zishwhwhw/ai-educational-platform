"""Прогон и отправка решений.

Два действия с разными последствиями, и разница должна быть явной:

* `POST /submissions/run` — черновой прогон. Только видимые тесты, останавливается
  на первом провале, ничего не сохраняет, попытку не расходует. Нужен, чтобы
  ученик мог свободно пробовать.
* `POST /submissions/` — зачёт. Все тесты, включая скрытые, результат сохраняется,
  начисляются баллы, попытка расходуется и влияет на ступень подсказки.

Прежняя версия этого файла не запускала код вообще: «правильность» определялась
поиском ожидаемого вывода внутри исходного текста программы.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.core.errors import AppError, NotFoundError
from app.core.time import utcnow
from app.db.session import get_db
from app.models import Submission, SubmissionResult, Task, TaskLanguage
from app.schemas.learning import (
    RunRequest,
    RunResponse,
    SubmissionResponse,
    SubmitRequest,
    TestOutcomeResponse,
)
from app.services.execution import UnsupportedLanguageError, get_engine
from app.services.grading import GradingResult, TestOutcome, grade

router = APIRouter(prefix="/submissions", tags=["submissions"])


class EngineUnavailableError(AppError):
    code = "execution_unavailable"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    message = "Code execution is temporarily unavailable. Your attempt was not counted."


class LanguageNotAllowedError(AppError):
    code = "language_not_allowed"
    status_code = status.HTTP_400_BAD_REQUEST
    message = "This task does not accept that language"


def _load_task(db: Session, task_id: int, language: str) -> tuple[Task, TaskLanguage]:
    task = db.get(Task, task_id)
    if task is None:
        raise NotFoundError("Task not found")
    spec = next((s for s in task.languages if str(s.language) == language.lower()), None)
    if spec is None:
        raise LanguageNotAllowedError(
            f"Task accepts: {', '.join(sorted(str(s.language) for s in task.languages))}"
        )
    return task, spec


def _to_response(outcome: TestOutcome) -> TestOutcomeResponse:
    """Скрытый тест отдаётся без содержимого.

    Ни входа, ни ожидаемого выхода, ни фактического вывода — даже после отправки.
    Иначе достаточно одной отправки, чтобы вынести тесты наружу, и задание
    перестаёт что-либо проверять для всех остальных.
    """
    visible = not outcome.is_hidden
    return TestOutcomeResponse(
        name=outcome.name,
        is_hidden=outcome.is_hidden,
        passed=outcome.passed,
        status=outcome.status.value,
        time_ms=outcome.time_ms,
        expected_stdout=outcome.expected if visible else None,
        actual_stdout=outcome.stdout if visible else None,
        stderr=outcome.stderr if visible else None,
    )


@router.post("/run", response_model=RunResponse)
async def run_draft(
    payload: RunRequest,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> RunResponse:
    task, spec = _load_task(db, payload.task_id, payload.language)
    visible = [c for c in task.test_cases if not bool(c.is_hidden)]

    try:
        result = await grade(
            engine=get_engine(),
            task=task,
            language_spec=spec,
            test_cases=visible,
            source=payload.source,
            # Черновику нужен быстрый отклик, а не полный отчёт.
            stop_on_first_failure=True,
        )
    except UnsupportedLanguageError as exc:
        raise LanguageNotAllowedError(str(exc)) from exc

    if result.engine_failed:
        raise EngineUnavailableError

    return RunResponse(
        passed_count=result.passed_count,
        total_count=len(visible),
        outcomes=[_to_response(o) for o in result.outcomes],
        compile_output=result.compile_output,
    )


@router.post("/", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def submit(
    payload: SubmitRequest,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> SubmissionResponse:
    task, spec = _load_task(db, payload.task_id, payload.language)
    cases = list(task.test_cases)

    try:
        result = await grade(
            engine=get_engine(),
            task=task,
            language_spec=spec,
            test_cases=cases,
            source=payload.source,
        )
    except UnsupportedLanguageError as exc:
        raise LanguageNotAllowedError(str(exc)) from exc

    if result.engine_failed:
        # Ничего не сохраняем: попытка не должна пропасть из-за чужого сбоя.
        raise EngineUnavailableError

    attempt_number = (
        db.execute(
            select(func.count())
            .select_from(Submission)
            .where(Submission.user_id == current_user.id, Submission.task_id == task.id)
        ).scalar_one()
        + 1
    )

    submission = _persist(db, current_user.id, task, payload, result, attempt_number)

    return SubmissionResponse(
        id=int(submission.id),
        task_id=int(task.id),
        language=payload.language.lower(),
        status=str(submission.status),
        tests_passed=result.passed_count,
        tests_total=result.total_count,
        score=result.score,
        points_awarded=int(submission.points_awarded),
        attempt_number=attempt_number,
        submitted_at=submission.submitted_at,
        outcomes=[_to_response(o) for o in result.outcomes],
        compile_output=result.compile_output,
    )


def _persist(
    db: Session,
    user_id: int,
    task: Task,
    payload: SubmitRequest,
    result: GradingResult,
    attempt_number: int,
) -> Submission:
    submission = Submission(
        user_id=user_id,
        task_id=task.id,
        code=payload.source,
        language=payload.language.lower(),
        status="correct" if result.all_passed else "incorrect",
        points_awarded=result.points,
        tests_passed=result.passed_count,
        tests_total=result.total_count,
        score=result.score,
        hint_level=max(0, attempt_number - 1),
        submitted_at=utcnow(),
    )
    db.add(submission)
    db.flush()

    db.add_all(
        SubmissionResult(
            submission_id=submission.id,
            test_case_id=o.test_case_id,
            passed=o.passed,
            status=o.status.value,
            # Вывод скрытого теста в базе храним: он нужен для подсказок
            # и разбора, наружу его не отдаёт слой представления.
            actual_stdout=o.stdout[:10_000],
            stderr=o.stderr[:10_000],
            time_ms=o.time_ms,
            memory_kb=o.memory_kb,
        )
        for o in result.outcomes
    )
    db.commit()
    db.refresh(submission)
    return submission


@router.get("/{submission_id}", response_model=SubmissionResponse)
def get_submission(
    submission_id: int,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> SubmissionResponse:
    submission = db.get(Submission, submission_id)
    # 404, а не 403, на чужую отправку: иначе перебором идентификаторов
    # можно узнать, какие отправки существуют.
    if submission is None or int(submission.user_id) != int(current_user.id):
        raise NotFoundError("Submission not found")

    by_case = {c.id: c for c in submission.task.test_cases}
    outcomes = [
        TestOutcomeResponse(
            name=str(by_case[r.test_case_id].name or ""),
            is_hidden=bool(by_case[r.test_case_id].is_hidden),
            passed=bool(r.passed),
            status=str(r.status),
            time_ms=r.time_ms,
            expected_stdout=(
                str(by_case[r.test_case_id].expected_stdout)
                if not by_case[r.test_case_id].is_hidden
                else None
            ),
            actual_stdout=str(r.actual_stdout) if not by_case[r.test_case_id].is_hidden else None,
        )
        for r in submission.results
        if r.test_case_id in by_case
    ]

    return SubmissionResponse(
        id=int(submission.id),
        task_id=int(submission.task_id),
        language=str(submission.language),
        status=str(submission.status),
        tests_passed=int(submission.tests_passed),
        tests_total=int(submission.tests_total),
        score=float(submission.score),
        points_awarded=int(submission.points_awarded),
        attempt_number=int(submission.hint_level) + 1,
        submitted_at=submission.submitted_at,
        outcomes=outcomes,
    )
