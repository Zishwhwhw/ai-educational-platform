"""Проверка решений.

Движок подменяется заглушкой: правила подсчёта не должны зависеть от чужого
сервиса, а тесты — ходить в сеть.
"""

from dataclasses import dataclass

import pytest

# TestCase импортируется под другим именем: pytest собирает всё, что начинается
# с `Test`, и пытался бы инстанцировать модель как тестовый класс.
from app.models import Task, TaskLanguage
from app.models import TestCase as TaskTestCase
from app.services.execution import ExecStatus, ExecutionRequest, ExecutionResult
from app.services.grading import grade, outputs_match


@dataclass
class FakeEngine:
    """Отдаёт заранее заданные ответы по очереди."""

    results: list[ExecutionResult]
    calls: int = 0

    async def run(self, request: ExecutionRequest) -> ExecutionResult:
        r = self.results[min(self.calls, len(self.results) - 1)]
        self.calls += 1
        return r

    async def languages(self) -> list[str]:
        return ["python"]

    async def healthy(self) -> bool:
        return True


def _ok(stdout: str) -> ExecutionResult:
    return ExecutionResult(status=ExecStatus.OK, stdout=stdout, time_ms=10)


def _task(points: int = 40, comparison: str = "trim") -> Task:
    return Task(id=1, points_value=points, comparison=comparison, float_tolerance=1e-6)


def _lang() -> TaskLanguage:
    return TaskLanguage(id=1, task_id=1, language="python", time_limit_ms=2000, memory_limit_mb=128)


def _cases(*specs: tuple[str, int, bool]) -> list[TaskTestCase]:
    return [
        TaskTestCase(
            id=i + 1,
            task_id=1,
            name=f"t{i + 1}",
            stdin="",
            expected_stdout=out,
            weight=w,
            is_hidden=hidden,
            ordering=i,
        )
        for i, (out, w, hidden) in enumerate(specs)
    ]


class TestScoring:
    async def test_all_passed_gives_full_points(self) -> None:
        r = await grade(
            engine=FakeEngine([_ok("1"), _ok("2")]),
            task=_task(40),
            language_spec=_lang(),
            test_cases=_cases(("1", 1, False), ("2", 1, True)),
            source="x",
        )
        assert r.all_passed
        assert r.score == 1.0
        assert r.points == 40

    async def test_partial_score_is_weighted(self) -> None:
        """Тест на граничный случай может стоить дороже тривиального,
        поэтому балл считается по весам, а не по количеству."""
        r = await grade(
            engine=FakeEngine([_ok("1"), _ok("WRONG")]),
            task=_task(40),
            language_spec=_lang(),
            test_cases=_cases(("1", 1, False), ("2", 3, False)),
            source="x",
        )
        assert r.passed_count == 1
        assert r.score == pytest.approx(0.25)  # 1 из 4 по весу
        assert r.points == 10

    async def test_points_round_down(self) -> None:
        """27 из 40 честнее, чем 28 «в подарок»."""
        r = await grade(
            engine=FakeEngine([_ok("1"), _ok("2"), _ok("NOPE")]),
            task=_task(40),
            language_spec=_lang(),
            test_cases=_cases(("1", 1, False), ("2", 1, False), ("3", 1, False)),
            source="x",
        )
        assert r.score == pytest.approx(2 / 3)
        assert r.points == 26  # 40 * 0.666… = 26.67 → 26

    async def test_nothing_passed(self) -> None:
        r = await grade(
            engine=FakeEngine([_ok("nope")]),
            task=_task(),
            language_spec=_lang(),
            test_cases=_cases(("1", 1, False)),
            source="x",
        )
        assert r.points == 0
        assert not r.all_passed


class TestFailureModes:
    async def test_engine_failure_does_not_count_as_attempt(self) -> None:
        """Недоступность песочницы — не ошибка ученика: попытка не должна
        засчитываться, иначе сбой инфраструктуры съедает баллы и подсказки."""
        r = await grade(
            engine=FakeEngine([ExecutionResult(status=ExecStatus.ENGINE_ERROR)]),
            task=_task(),
            language_spec=_lang(),
            test_cases=_cases(("1", 1, False), ("2", 1, False)),
            source="x",
        )
        assert r.engine_failed
        assert r.points == 0
        assert r.outcomes == []

    async def test_compile_error_stops_and_marks_all_failed(self) -> None:
        engine = FakeEngine(
            [ExecutionResult(status=ExecStatus.COMPILE_ERROR, compile_output="boom")]
        )
        r = await grade(
            engine=engine,
            task=_task(),
            language_spec=_lang(),
            test_cases=_cases(("1", 1, False), ("2", 1, False), ("3", 1, False)),
            source="x",
        )
        assert engine.calls == 1, "остальные тесты прогонять бессмысленно"
        assert len(r.outcomes) == 3
        assert not any(o.passed for o in r.outcomes)
        assert r.compile_output == "boom"

    async def test_timeout_is_a_failed_test_not_an_engine_error(self) -> None:
        r = await grade(
            engine=FakeEngine([ExecutionResult(status=ExecStatus.TIMEOUT)]),
            task=_task(),
            language_spec=_lang(),
            test_cases=_cases(("1", 1, False)),
            source="while True: pass",
        )
        assert not r.engine_failed
        assert r.outcomes[0].status is ExecStatus.TIMEOUT
        assert not r.outcomes[0].passed

    async def test_stop_on_first_failure_for_draft_runs(self) -> None:
        engine = FakeEngine([_ok("nope")])
        await grade(
            engine=engine,
            task=_task(),
            language_spec=_lang(),
            test_cases=_cases(("1", 1, False), ("2", 1, False), ("3", 1, False)),
            source="x",
            stop_on_first_failure=True,
        )
        assert engine.calls == 1


class TestOutputComparison:
    @pytest.mark.parametrize(
        ("actual", "expected", "mode", "want"),
        [
            ("10\n", "10", "trim", True),
            ("10   \n\n", "10", "trim", True),
            ("10\n", "10", "exact", False),
            ("Hello", "hello", "ignore_case", True),
            ("Hello", "hello", "trim", False),
            ("0.30000000000000004", "0.3", "numeric", True),
            ("result=0.3000001", "result=0.3", "numeric", True),
            ("result=0.4", "result=0.3", "numeric", False),
            ("other=0.3", "result=0.3", "numeric", False),
            ("1\n2", "1\n2\n", "trim", True),
        ],
    )
    def test_modes(self, actual: str, expected: str, mode: str, want: bool) -> None:
        assert outputs_match(actual, expected, mode, 1e-6) is want

    def test_trailing_whitespace_is_the_classic_false_negative(self) -> None:
        """Самая частая жалоба на автопроверку — «решение верное, но не принимается»
        из-за лишнего перевода строки. В режиме trim это не должно проваливаться."""
        assert outputs_match("42\n", "42", "trim", 1e-6)
