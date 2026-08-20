from pydantic import BaseModel, ConfigDict


class CourseCreate(BaseModel):
    title: str
    description: str
    language: str = "python"
    difficulty: str = "beginner"
    base_price: float = 0.0


class CourseResponse(BaseModel):
    id: int
    title: str
    description: str
    language: str
    difficulty: str
    teacher_id: int | None
    is_ai_generated: bool
    is_preinstalled: bool
    base_price: float
    target_points: int
    image_url: str

    model_config = ConfigDict(from_attributes=True)


class ModuleCreate(BaseModel):
    title: str
    order: int = 0


class ModuleResponse(BaseModel):
    id: int
    course_id: int
    title: str
    order: int

    model_config = ConfigDict(from_attributes=True)


class LessonCreate(BaseModel):
    title: str
    content_type: str = "text"
    content: str | None = None
    video_url: str | None = None
    min_read_time: int = 300
    points_value: int = 5
    order: int = 0


class LessonResponse(BaseModel):
    id: int
    module_id: int
    title: str
    content_type: str
    content: str | None
    video_url: str | None
    min_read_time: int
    points_value: int
    order: int

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(BaseModel):
    prompt: str
    difficulty: str = "easy"
    expected_output: str | None = None
    test_cases: str | None = None
    points_value: int = 25


class TaskResponse(BaseModel):
    id: int
    lesson_id: int
    difficulty: str
    prompt: str
    points_value: int

    model_config = ConfigDict(from_attributes=True)


class TaskLanguageResponse(BaseModel):
    language: str
    starter_code: str
    time_limit_ms: int
    memory_limit_mb: int

    model_config = ConfigDict(from_attributes=True)


class VisibleTestCaseResponse(BaseModel):
    """Видимый тест целиком. Скрытые в этот список не попадают вовсе —
    ученик знает только их количество."""

    name: str
    stdin: str
    expected_stdout: str

    model_config = ConfigDict(from_attributes=True)


class TaskDetailResponse(BaseModel):
    id: int
    lesson_id: int
    prompt: str
    difficulty: str
    points_value: int
    comparison: str
    languages: list[TaskLanguageResponse]
    visible_tests: list[VisibleTestCaseResponse]
    hidden_test_count: int

    model_config = ConfigDict(from_attributes=True)


class CourseCardResponse(BaseModel):
    """Карточка в каталоге. Прогресс считается для текущего пользователя."""

    id: int
    title: str
    description: str
    language: str
    difficulty: str
    is_preinstalled: bool
    target_points: int
    image_url: str
    lesson_count: int
    earned_points: int


class TaskOutlineResponse(BaseModel):
    id: int
    difficulty: str
    points_value: int
    is_solved: bool


class LessonOutlineResponse(BaseModel):
    id: int
    title: str
    content_type: str
    points_value: int
    order: int
    is_completed: bool
    tasks: list[TaskOutlineResponse]


class ModuleOutlineResponse(BaseModel):
    id: int
    title: str
    order: int
    lessons: list[LessonOutlineResponse]


class CourseOutlineResponse(BaseModel):
    id: int
    title: str
    description: str
    language: str
    difficulty: str
    target_points: int
    earned_points: int
    modules: list[ModuleOutlineResponse]
    # Куда ведёт кнопка «Continue»: первое нерешённое задание.
    next_task_id: int | None
