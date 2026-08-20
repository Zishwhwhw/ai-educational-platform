from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RunRequest(BaseModel):
    """Черновой прогон: только видимые тесты, попытка не расходуется."""

    task_id: int
    language: str = Field(min_length=1, max_length=32)
    source: str = Field(min_length=1, max_length=200_000)


class SubmitRequest(RunRequest):
    """Зачёт: все тесты, включая скрытые, попытка расходуется."""


class TestOutcomeResponse(BaseModel):
    """Исход одного теста.

    Для скрытого теста наружу уходят только имя и статус. Вход и ожидаемый выход
    не отдаются **никогда**, даже после отправки: иначе тест выносится
    из платформы и задание обесценивается для всех остальных.
    """

    name: str
    is_hidden: bool
    passed: bool
    status: str
    time_ms: int | None = None
    # Заполняются только для видимых тестов.
    stdin: str | None = None
    expected_stdout: str | None = None
    actual_stdout: str | None = None
    stderr: str | None = None


class RunResponse(BaseModel):
    passed_count: int
    total_count: int
    outcomes: list[TestOutcomeResponse]
    compile_output: str = ""
    engine_available: bool = True


class SubmissionResponse(BaseModel):
    id: int
    task_id: int
    language: str
    status: str
    tests_passed: int
    tests_total: int
    score: float
    points_awarded: int
    attempt_number: int
    submitted_at: datetime
    outcomes: list[TestOutcomeResponse]
    compile_output: str = ""

    model_config = ConfigDict(from_attributes=True)


class HintRequest(BaseModel):
    submission_id: int


class HintResponse(BaseModel):
    hint_level: int
    hint_text: str


class ProgressCreate(BaseModel):
    lesson_id: int
    course_id: int | None = None
    time_spent: int = 0


class ProgressResponse(BaseModel):
    id: int
    user_id: int
    lesson_id: int
    course_id: int | None
    is_completed: bool
    points_awarded: int
    time_spent: int
    started_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class PeerReviewCreate(BaseModel):
    submission_id: int
    score: int = Field(ge=1, le=10)
    comment: str = Field(default="", max_length=2000)


class PeerReviewResponse(BaseModel):
    id: int
    submission_id: int
    reviewer_id: int
    score: int
    comment: str

    model_config = ConfigDict(from_attributes=True)
