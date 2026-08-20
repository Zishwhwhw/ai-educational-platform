"""Проверка решений: запуск кода по тестам и подсчёт балла.

Заменяет прежнюю «проверку» из `routers/submissions.py`:

    if task.expected_output and task.expected_output.strip() in sub.code:
        is_correct = True

Она проверяла, встречается ли **ожидаемый вывод** внутри **исходного текста**
программы. Задание проходилось вставкой ответа в комментарий, а код не запускался
никогда. Здесь код действительно исполняется в песочнице, и вывод сравнивается
с ожидаемым по правилам, заданным автором задания.
"""

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from app.models import Task, TaskLanguage, TestCase
from app.services.execution import (
    ExecStatus,
    ExecutionEngine,
    ExecutionRequest,
    ExecutionResult,
)

# Как сравнивать вывод. Значение хранится в задании: для задачи на форматирование
# важен каждый пробел, для арифметической — нет.
COMPARISON_MODES = ("exact", "trim", "ignore_case", "numeric")


@dataclass(frozen=True, slots=True)
class TestOutcome:
    test_case_id: int
    name: str
    is_hidden: bool
    weight: int
    passed: bool
    status: ExecStatus
    stdout: str
    stderr: str
    expected: str
    time_ms: int | None
    memory_kb: int | None


@dataclass(frozen=True, slots=True)
class GradingResult:
    outcomes: list[TestOutcome]
    passed_count: int
    total_count: int
    score: float
    """Доля набранного веса от общего, 0.0–1.0."""
    points: int
    engine_failed: bool
    """True, если песочница была недоступна. Тогда попытку засчитывать нельзя."""
    compile_output: str = ""

    @property
    def all_passed(self) -> bool:
        return self.total_count > 0 and self.passed_count == self.total_count


def _normalize(text: str, mode: str) -> str:
    # Хвостовые пробелы и перевод строки в конце — самая частая причина
    # «правильное решение не принимается». Убираются во всех режимах, кроме exact.
    if mode == "exact":
        return text
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    out = "\n".join(lines)
    return out.lower() if mode == "ignore_case" else out


_NUMBER = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")


def _numeric_equal(actual: str, expected: str, tolerance: float) -> bool:
    """Сравнение с допуском: 0.30000000000000004 должно совпадать с 0.3.

    Числа сравниваются по значению, весь остальной текст — как есть.
    """
    a_nums, e_nums = _NUMBER.findall(actual), _NUMBER.findall(expected)
    if len(a_nums) != len(e_nums):
        return False
    if _NUMBER.sub("#", actual) != _NUMBER.sub("#", expected):
        return False
    for a, e in zip(a_nums, e_nums, strict=True):
        try:
            if abs(Decimal(a) - Decimal(e)) > Decimal(str(tolerance)):
                return False
        except (InvalidOperation, ValueError):
            return False
    return True


def outputs_match(actual: str, expected: str, mode: str, tolerance: float) -> bool:
    a, e = _normalize(actual, mode), _normalize(expected, mode)
    if mode == "numeric":
        return _numeric_equal(a, e, tolerance)
    return a == e


async def grade(
    *,
    engine: ExecutionEngine,
    task: Task,
    language_spec: TaskLanguage,
    test_cases: list[TestCase],
    source: str,
    stop_on_first_failure: bool = False,
) -> GradingResult:
    """Прогнать решение по тестам.

    `stop_on_first_failure` используется для черновых прогонов: ученику нужен
    быстрый отклик, а не полный отчёт. При зачёте прогоняются все тесты —
    иначе не посчитать частичный балл.
    """
    outcomes: list[TestOutcome] = []
    compile_output = ""
    engine_failed = False

    for case in test_cases:
        result: ExecutionResult = await engine.run(
            ExecutionRequest(
                language=language_spec.language,
                source=source,
                stdin=case.stdin or "",
                time_limit_ms=int(language_spec.time_limit_ms),
                memory_limit_mb=int(language_spec.memory_limit_mb),
            )
        )

        if result.status is ExecStatus.ENGINE_ERROR:
            # Сбой песочницы — не вина ученика. Прерываемся и сообщаем наверх,
            # чтобы попытка не засчиталась и подсказка не эскалировала.
            engine_failed = True
            break

        if result.status is ExecStatus.COMPILE_ERROR:
            # Код не собрался — прогонять остальные тесты бессмысленно.
            compile_output = result.compile_output or result.stderr
            outcomes = [
                TestOutcome(
                    test_case_id=int(c.id),
                    name=str(c.name or f"test {i + 1}"),
                    is_hidden=bool(c.is_hidden),
                    weight=int(c.weight),
                    passed=False,
                    status=ExecStatus.COMPILE_ERROR,
                    stdout="",
                    stderr="",
                    expected=str(c.expected_stdout or ""),
                    time_ms=None,
                    memory_kb=None,
                )
                for i, c in enumerate(test_cases)
            ]
            break

        passed = result.status is ExecStatus.OK and outputs_match(
            result.stdout,
            str(case.expected_stdout or ""),
            str(task.comparison),
            float(task.float_tolerance),
        )

        outcomes.append(
            TestOutcome(
                test_case_id=int(case.id),
                name=str(case.name or f"test {len(outcomes) + 1}"),
                is_hidden=bool(case.is_hidden),
                weight=int(case.weight),
                passed=passed,
                status=result.status,
                stdout=result.stdout,
                stderr=result.stderr,
                expected=str(case.expected_stdout or ""),
                time_ms=result.time_ms,
                memory_kb=result.memory_kb,
            )
        )

        if not passed and stop_on_first_failure:
            break

    if engine_failed:
        return GradingResult([], 0, len(test_cases), 0.0, 0, engine_failed=True)

    total_weight = sum(int(c.weight) for c in test_cases) or 1
    earned = sum(o.weight for o in outcomes if o.passed)
    score = earned / total_weight

    # Частичный балл округляется вниз: 27 из 40 честнее, чем 28 «в подарок».
    points = int(int(task.points_value) * score)

    return GradingResult(
        outcomes=outcomes,
        passed_count=sum(1 for o in outcomes if o.passed),
        total_count=len(test_cases),
        score=score,
        points=points,
        engine_failed=False,
        compile_output=compile_output,
    )
