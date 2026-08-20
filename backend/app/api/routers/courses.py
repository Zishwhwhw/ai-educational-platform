"""Каталог курсов и структура курса.

Что исправлено по сравнению с прежней версией:

1. **`teacher_id` больше не приходит от клиента.** Было
   `create_course(course, teacher_id: int | None = None)` параметром запроса
   без всякой проверки — курс создавался от имени любого преподавателя.
   Тот же класс дыры, что `user_id: int = 1` в других роутерах.
2. **Создание требует роли `teacher`.** Раньше создать курс мог кто угодно,
   включая анонима.
3. **Появилась структура курса с прогрессом** — без неё в задание неоткуда
   попасть и некуда идти после решения.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import CurrentUser, require_roles
from app.core.errors import NotFoundError, PermissionDeniedError
from app.db.session import get_db
from app.models import Course, Lesson, Module, Progress, Submission, Task, User
from app.schemas.course import (
    CourseCardResponse,
    CourseCreate,
    CourseOutlineResponse,
    CourseResponse,
    LessonOutlineResponse,
    ModuleCreate,
    ModuleOutlineResponse,
    ModuleResponse,
    TaskOutlineResponse,
)

router = APIRouter(prefix="/courses", tags=["courses"])

TeacherUser = Annotated[User, Depends(require_roles("teacher", "admin", "owner"))]


def _earned_points(db: Session, user_id: int, course_id: int) -> int:
    """Сколько баллов набрано в курсе: за уроки и за задания.

    Считается запросом, а не обходом связей: иначе на курсе из ста уроков
    получается сотня запросов к базе.
    """
    lesson_points = db.execute(
        select(func.coalesce(func.sum(Progress.points_awarded), 0)).where(
            Progress.user_id == user_id,
            Progress.course_id == course_id,
            Progress.is_completed,
        )
    ).scalar_one()

    task_points = db.execute(
        select(func.coalesce(func.sum(Submission.points_awarded), 0))
        .select_from(Submission)
        .join(Task, Task.id == Submission.task_id)
        .join(Lesson, Lesson.id == Task.lesson_id)
        .join(Module, Module.id == Lesson.module_id)
        .where(Submission.user_id == user_id, Module.course_id == course_id)
    ).scalar_one()

    return int(lesson_points) + int(task_points)


@router.get("/", response_model=list[CourseCardResponse])
def list_courses(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    language: str | None = None,
    difficulty: str | None = None,
    search: str | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(24, ge=1, le=100),
) -> list[CourseCardResponse]:
    stmt = select(Course)
    if language:
        stmt = stmt.where(Course.language == language)
    if difficulty:
        stmt = stmt.where(Course.difficulty == difficulty)
    if search:
        stmt = stmt.where(Course.title.ilike(f"%{search}%"))

    courses = db.execute(stmt.order_by(Course.id).offset(offset).limit(limit)).scalars().all()
    if not courses:
        return []

    # Количество уроков одним запросом на всю страницу, а не по курсу.
    counts = dict(
        db.execute(
            select(Module.course_id, func.count(Lesson.id))
            .join(Lesson, Lesson.module_id == Module.id)
            .where(Module.course_id.in_([c.id for c in courses]))
            .group_by(Module.course_id)
        ).all()
    )

    return [
        CourseCardResponse(
            id=int(c.id),
            title=str(c.title or ""),
            description=str(c.description or ""),
            language=str(c.language),
            difficulty=str(c.difficulty),
            is_preinstalled=bool(c.is_preinstalled),
            target_points=int(c.target_points),
            image_url=str(c.image_url or ""),
            lesson_count=int(counts.get(c.id, 0)),
            earned_points=_earned_points(db, int(current_user.id), int(c.id)),
        )
        for c in courses
    ]


@router.get("/{course_id}", response_model=CourseOutlineResponse)
def get_course_outline(
    course_id: int,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> CourseOutlineResponse:
    course = db.execute(
        select(Course)
        .options(
            selectinload(Course.modules).selectinload(Module.lessons).selectinload(Lesson.tasks)
        )
        .where(Course.id == course_id)
    ).scalar_one_or_none()
    if course is None:
        raise NotFoundError("Course not found")

    solved_task_ids = set(
        db.execute(
            select(Submission.task_id).where(
                Submission.user_id == current_user.id, Submission.status == "correct"
            )
        )
        .scalars()
        .all()
    )
    completed_lesson_ids = set(
        db.execute(
            select(Progress.lesson_id).where(
                Progress.user_id == current_user.id, Progress.is_completed
            )
        )
        .scalars()
        .all()
    )

    next_task_id: int | None = None
    modules: list[ModuleOutlineResponse] = []

    for module in sorted(course.modules, key=lambda m: int(m.order or 0)):
        lessons: list[LessonOutlineResponse] = []
        for lesson in sorted(module.lessons, key=lambda x: int(x.order or 0)):
            tasks = [
                TaskOutlineResponse(
                    id=int(t.id),
                    difficulty=str(t.difficulty),
                    points_value=int(t.points_value),
                    is_solved=int(t.id) in solved_task_ids,
                )
                for t in lesson.tasks
            ]
            # Первое нерешённое задание — цель кнопки «Continue».
            if next_task_id is None:
                unsolved = next((t for t in tasks if not t.is_solved), None)
                if unsolved is not None:
                    next_task_id = unsolved.id

            lessons.append(
                LessonOutlineResponse(
                    id=int(lesson.id),
                    title=str(lesson.title or ""),
                    content_type=str(lesson.content_type),
                    points_value=int(lesson.points_value),
                    order=int(lesson.order or 0),
                    is_completed=int(lesson.id) in completed_lesson_ids,
                    tasks=tasks,
                )
            )
        modules.append(
            ModuleOutlineResponse(
                id=int(module.id),
                title=str(module.title or ""),
                order=int(module.order or 0),
                lessons=lessons,
            )
        )

    return CourseOutlineResponse(
        id=int(course.id),
        title=str(course.title or ""),
        description=str(course.description or ""),
        language=str(course.language),
        difficulty=str(course.difficulty),
        target_points=int(course.target_points),
        earned_points=_earned_points(db, int(current_user.id), int(course.id)),
        modules=modules,
        next_task_id=next_task_id,
    )


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    payload: CourseCreate,
    teacher: TeacherUser,
    db: Annotated[Session, Depends(get_db)],
) -> CourseResponse:
    # Автор — тот, кто прислал запрос. Прежняя версия брала `teacher_id`
    # из параметров запроса, то есть автором можно было назначить кого угодно.
    course = Course(**payload.model_dump(), teacher_id=teacher.id)
    db.add(course)
    db.commit()
    db.refresh(course)
    return CourseResponse.model_validate(course)


@router.post(
    "/{course_id}/modules", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED
)
def create_module(
    course_id: int,
    payload: ModuleCreate,
    teacher: TeacherUser,
    db: Annotated[Session, Depends(get_db)],
) -> ModuleResponse:
    course = db.get(Course, course_id)
    if course is None:
        raise NotFoundError("Course not found")
    # Роли `teacher` мало: она не даёт права править чужой курс.
    if course.teacher_id is not None and int(course.teacher_id) != int(teacher.id):
        raise PermissionDeniedError("You can only add modules to your own courses")

    module = Module(**payload.model_dump(), course_id=course_id)
    db.add(module)
    db.commit()
    db.refresh(module)
    return ModuleResponse.model_validate(module)
