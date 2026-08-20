"""Проверка курсов, лежащих в репозитории.

Структурные проверки идут всегда и быстро. Прогон эталонных решений через
песочницу вынесен под метку: он требует сети и занимает минуты — но именно
он ловит задание, которое невозможно решить.
"""

import os
import pathlib

import pytest
import yaml

from app.content.loader import CONTENT_DIR, ContentError, validate

COURSES = sorted(CONTENT_DIR.glob("*.yaml"))


def _load(path: pathlib.Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("path", COURSES, ids=lambda p: p.stem)
class TestCourseStructure:
    def test_passes_validation(self, path: pathlib.Path) -> None:
        validate(_load(path))

    def test_every_task_has_a_reference_solution(self, path: pathlib.Path) -> None:
        """Без эталона нельзя ни проверить задание, ни выдать пятую подсказку."""
        doc = _load(path)
        missing = [
            lesson["title"]
            for module in doc["modules"]
            for lesson in module["lessons"]
            for task in lesson.get("tasks", [])
            for lang in task["languages"]
            if not lang.get("solution")
        ]
        assert not missing, f"нет эталонного решения: {missing}"

    def test_every_task_has_a_hidden_test(self, path: pathlib.Path) -> None:
        """Только видимые тесты означают, что решение можно подогнать под ответ."""
        doc = _load(path)
        weak = [
            lesson["title"]
            for module in doc["modules"]
            for lesson in module["lessons"]
            for task in lesson.get("tasks", [])
            if not any(c.get("hidden") for c in task["tests"]) and len(task["tests"]) > 1
        ]
        assert not weak, f"задания без скрытых тестов: {weak}"

    def test_step_ids_are_unique_within_a_step(self, path: pathlib.Path) -> None:
        doc = _load(path)
        for module in doc["modules"]:
            for lesson in module["lessons"]:
                for step in lesson.get("steps", []):
                    for field in ("options", "items", "left", "right"):
                        entries = (step.get("content") or {}).get(field, [])
                        ids = [e["id"] for e in entries]
                        assert len(ids) == len(set(ids)), (
                            f"{lesson['title']}: повторяющиеся id в {field}"
                        )


class TestValidatorCatchesBrokenContent:
    """Валидатор существует ради этих случаев — проверяем, что он их ловит."""

    def test_unknown_step_type(self) -> None:
        doc = {
            "slug": "x",
            "title": "X",
            "modules": [
                {"title": "M", "lessons": [{"title": "L", "steps": [{"type": "telepathy"}]}]}
            ],
        }
        with pytest.raises(ContentError, match="unknown step type"):
            validate(doc)

    def test_choice_without_correct_answer(self) -> None:
        doc = {
            "slug": "x",
            "title": "X",
            "modules": [
                {
                    "title": "M",
                    "lessons": [
                        {
                            "title": "L",
                            "steps": [
                                {"type": "choice_single", "content": {"options": [{"id": "a"}]}}
                            ],
                        }
                    ],
                }
            ],
        }
        with pytest.raises(ContentError, match="needs grading.correct"):
            validate(doc)

    def test_correct_answer_not_among_options(self) -> None:
        """Самый коварный случай: шаг выглядит целым, но непроходим."""
        doc = {
            "slug": "x",
            "title": "X",
            "modules": [
                {
                    "title": "M",
                    "lessons": [
                        {
                            "title": "L",
                            "steps": [
                                {
                                    "type": "choice_single",
                                    "content": {"options": [{"id": "a"}, {"id": "b"}]},
                                    "grading": {"correct": "z"},
                                }
                            ],
                        }
                    ],
                }
            ],
        }
        with pytest.raises(ContentError, match="unknown options"):
            validate(doc)

    def test_task_without_tests(self) -> None:
        doc = {
            "slug": "x",
            "title": "X",
            "modules": [
                {
                    "title": "M",
                    "lessons": [
                        {
                            "title": "L",
                            "tasks": [{"prompt": "do it", "languages": [{"name": "python"}]}],
                        }
                    ],
                }
            ],
        }
        with pytest.raises(ContentError, match="without tests checks nothing"):
            validate(doc)


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("RUN_CONTENT_INTEGRATION") != "1",
    reason="прогоняет эталоны через песочницу; включается RUN_CONTENT_INTEGRATION=1",
)
@pytest.mark.parametrize("path", COURSES, ids=lambda p: p.stem)
async def test_reference_solutions_pass_their_own_tests(path: pathlib.Path) -> None:
    """Задание, которое не решается собственным эталоном, сломано.

    Для ученика это выглядит как «правильный ответ не принимают» — самая
    разрушительная для доверия ошибка в учебном продукте.
    """
    from app.services.execution import ExecStatus, ExecutionRequest, get_engine
    from app.services.grading import outputs_match

    engine = get_engine()
    doc = _load(path)
    failures: list[str] = []

    for module in doc["modules"]:
        for lesson in module["lessons"]:
            for task in lesson.get("tasks", []):
                lang = task["languages"][0]
                for case in task["tests"]:
                    result = await engine.run(
                        ExecutionRequest(
                            language=lang["name"],
                            source=lang["solution"],
                            stdin=case.get("stdin", ""),
                            time_limit_ms=int(lang.get("time_limit_ms", 5000)),
                        )
                    )
                    ok = result.status is ExecStatus.OK and outputs_match(
                        result.stdout,
                        str(case.get("stdout", "")),
                        task.get("comparison", "trim"),
                        1e-6,
                    )
                    if not ok:
                        failures.append(
                            f"{lesson['title']} / {case.get('name')}: "
                            f"got {result.stdout.strip()!r}, want {str(case.get('stdout')).strip()!r}"
                        )

    assert not failures, "эталон не проходит свои тесты:\n" + "\n".join(failures)
