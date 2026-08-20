"""Загрузка курсов из файлов репозитория.

Курс живёт в YAML, а не в базе, по трём причинам:

* его видно в истории изменений — правку формулировки можно найти и откатить;
* его правит человек без SQL, а позже — конструктор курсов, который будет
  писать тот же формат;
* его можно проверять при сборке: сломанный тест-кейс должен ронять CI,
  а не всплывать у ученика.

Загрузка идемпотентна по `slug`: повторный запуск обновляет курс, а не
создаёт второй. Дерево модулей и шагов пересобирается целиком — это проще
и надёжнее, чем сверять по одному, но **стирает прогресс по этому курсу**,
поэтому требует явного подтверждения.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models import (
    Course,
    Lesson,
    Module,
    Step,
    Task,
    TaskHint,
    TaskLanguage,
    TestCase,
)
from app.services.steps import STEP_TYPES

log = get_logger(__name__)

CONTENT_DIR = Path(__file__).parent / "courses"


class ContentError(Exception):
    """Курс в файле собран неправильно. Лучше упасть здесь, чем у ученика."""


@dataclass(frozen=True, slots=True)
class LoadStats:
    slug: str
    modules: int
    lessons: int
    steps: int
    tasks: int
    points: int


def _require(node: dict[str, Any], key: str, where: str) -> Any:
    if key not in node:
        raise ContentError(f"{where}: missing required field {key!r}")
    return node[key]


def validate(doc: dict[str, Any]) -> None:
    """Проверить курс до записи в базу.

    Проверяется то, что ломает продукт молча: неизвестный тип шага, шаг
    с выбором без правильного ответа, задание без тестов. Такие ошибки
    у ученика выглядят как «платформа не работает».
    """
    _require(doc, "slug", "course")
    _require(doc, "title", "course")

    for mi, module in enumerate(doc.get("modules", []), 1):
        where_m = f"module {mi}"
        _require(module, "title", where_m)

        for li, lesson in enumerate(module.get("lessons", []), 1):
            where_l = f"{where_m}, lesson {li}"
            _require(lesson, "title", where_l)

            for si, step in enumerate(lesson.get("steps", []), 1):
                where_s = f"{where_l}, step {si}"
                kind = _require(step, "type", where_s)
                if kind not in STEP_TYPES:
                    raise ContentError(f"{where_s}: unknown step type {kind!r}")

                grading = step.get("grading") or {}
                if kind == "choice_single" and not grading.get("correct"):
                    raise ContentError(f"{where_s}: choice_single needs grading.correct")
                if kind == "choice_multiple" and not grading.get("correct"):
                    raise ContentError(f"{where_s}: choice_multiple needs grading.correct")
                if kind == "input_string" and not grading.get("answers"):
                    raise ContentError(f"{where_s}: input_string needs grading.answers")
                if kind == "input_number" and "value" not in grading:
                    raise ContentError(f"{where_s}: input_number needs grading.value")
                if kind in ("matching", "ordering") and not (
                    grading.get("pairs") or grading.get("order")
                ):
                    raise ContentError(f"{where_s}: {kind} needs grading.pairs or grading.order")

                # Варианты выбора должны иметь те же идентификаторы, что и ответ,
                # иначе шаг непроходим: правильного варианта в списке просто нет.
                if kind in ("choice_single", "choice_multiple"):
                    ids = {o.get("id") for o in (step.get("content") or {}).get("options", [])}
                    correct = grading["correct"]
                    expected = {correct} if isinstance(correct, str) else set(correct)
                    missing = expected - ids
                    if missing:
                        raise ContentError(
                            f"{where_s}: grading.correct references unknown options {missing}"
                        )

            for ti, task in enumerate(lesson.get("tasks", []), 1):
                where_t = f"{where_l}, task {ti}"
                _require(task, "prompt", where_t)
                if not task.get("tests"):
                    raise ContentError(f"{where_t}: a coding task without tests checks nothing")
                if not task.get("languages"):
                    raise ContentError(f"{where_t}: task needs at least one language")


def load_file(path: Path) -> dict[str, Any]:
    doc: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
    validate(doc)
    return doc


def apply(db: Session, doc: dict[str, Any]) -> LoadStats:
    """Записать курс в базу, заменив предыдущую версию с тем же slug."""
    slug = str(doc["slug"])

    existing = db.execute(select(Course).where(Course.slug == slug)).scalar_one_or_none()
    if existing is not None:
        # Именно db.delete, а не delete(): массовое удаление идёт мимо ORM,
        # а внешний ключ modules.course_id каскада на уровне БД не имеет —
        # такой вызов падает на FK-нарушении при повторной загрузке.
        db.delete(existing)
        db.flush()

    course = Course(
        slug=slug,
        title=doc["title"],
        description=doc.get("description", ""),
        language=doc.get("language", "python"),
        difficulty=doc.get("difficulty", "beginner"),
        is_preinstalled=bool(doc.get("preinstalled", True)),
        target_points=int(doc.get("target_points", 1700)),
    )
    db.add(course)
    db.flush()

    counts = {"modules": 0, "lessons": 0, "steps": 0, "tasks": 0, "points": 0}

    for m_order, m in enumerate(doc.get("modules", []), 1):
        module = Module(course_id=course.id, title=m["title"], order=m_order)
        db.add(module)
        db.flush()
        counts["modules"] += 1

        for l_order, les in enumerate(m.get("lessons", []), 1):
            lesson = Lesson(
                module_id=module.id,
                title=les["title"],
                order=l_order,
                points_value=int(les.get("points", 5)),
            )
            db.add(lesson)
            db.flush()
            counts["lessons"] += 1

            for s_order, st in enumerate(les.get("steps", []), 1):
                points = int(st.get("points", 5))
                db.add(
                    Step(
                        lesson_id=lesson.id,
                        type=st["type"],
                        ordering=s_order,
                        points_value=points,
                        content=st.get("content") or {},
                        grading=st.get("grading") or {},
                    )
                )
                counts["steps"] += 1
                counts["points"] += points

            for t in les.get("tasks", []):
                points = int(t.get("points", 25))
                task = Task(
                    lesson_id=lesson.id,
                    prompt=t["prompt"],
                    difficulty=t.get("difficulty", "easy"),
                    points_value=points,
                    comparison=t.get("comparison", "trim"),
                )
                db.add(task)
                db.flush()
                counts["tasks"] += 1
                counts["points"] += points

                for lang in t["languages"]:
                    db.add(
                        TaskLanguage(
                            task_id=task.id,
                            language=lang["name"],
                            starter_code=lang.get("starter", ""),
                            reference_solution=lang.get("solution", ""),
                            time_limit_ms=int(lang.get("time_limit_ms", 5000)),
                            memory_limit_mb=int(lang.get("memory_limit_mb", 128)),
                        )
                    )

                for i, case in enumerate(t["tests"]):
                    db.add(
                        TestCase(
                            task_id=task.id,
                            name=case.get("name", f"test {i + 1}"),
                            stdin=case.get("stdin", ""),
                            expected_stdout=str(case.get("stdout", "")),
                            is_hidden=bool(case.get("hidden", False)),
                            weight=int(case.get("weight", 1)),
                            ordering=i,
                        )
                    )

                for i, hint in enumerate(t.get("hints", [])):
                    db.add(
                        TaskHint(
                            task_id=task.id,
                            text=hint["text"],
                            symptom=hint.get("symptom", ""),
                            ordering=i,
                        )
                    )

    db.commit()
    return LoadStats(slug=slug, **counts)


def load_all(db: Session) -> list[LoadStats]:
    return [apply(db, load_file(p)) for p in sorted(CONTENT_DIR.glob("*.yaml"))]
