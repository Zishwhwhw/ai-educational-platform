"""Лестница подсказок.

LLM не вызывается: третья и четвёртая ступени проверяются в режиме
«наставник недоступен» — именно он и работает, пока ключ не задан.
"""

import pytest

from app.models import Submission, SubmissionResult, Task, TaskHint, TaskLanguage
from app.models import TestCase as TaskTestCase
from app.services.hints import (
    MAX_LEVEL,
    PENALTY,
    HintNotUnlockedError,
    is_unlocked,
    reveal,
    reward_multiplier,
)


def _fixture(*, hints: list[TaskHint] | None = None, solution: str = "print(1)"):  # type: ignore[no-untyped-def]
    cases = [
        TaskTestCase(
            id=1, task_id=1, name="two numbers", expected_stdout="3", weight=1, ordering=0
        ),
        TaskTestCase(id=2, task_id=1, name="single", expected_stdout="7", weight=1, ordering=1),
    ]
    task = Task(id=1, prompt="Sum the numbers", points_value=40, comparison="trim")
    task.test_cases = cases
    task.hints = hints or []
    spec = TaskLanguage(id=1, task_id=1, language="python", reference_solution=solution)
    sub = Submission(id=1, user_id=1, task_id=1, code="print(0)", language="python")
    sub.results = [
        SubmissionResult(submission_id=1, test_case_id=1, passed=True, status="ok"),
        SubmissionResult(submission_id=1, test_case_id=2, passed=False, status="ok"),
    ]
    return task, spec, sub


class TestUnlocking:
    """Ступени открываются по числу неудачных попыток, а не по желанию."""

    @pytest.mark.parametrize(
        ("level", "failures", "expected"),
        [
            (1, 0, False),
            (1, 1, True),
            (2, 1, True),
            (3, 1, False),
            (3, 2, True),
            (4, 2, False),
            (4, 3, True),
            (5, 3, False),
            (5, 4, True),
        ],
    )
    def test_unlock_thresholds(self, level: int, failures: int, expected: bool) -> None:
        assert is_unlocked(level, failures) is expected

    async def test_locked_level_raises(self) -> None:
        task, spec, sub = _fixture()
        with pytest.raises(HintNotUnlockedError) as exc:
            await reveal(level=5, task=task, language_spec=spec, submission=sub, failed_attempts=1)
        assert exc.value.required_failures == 4

    async def test_level_out_of_range_rejected(self) -> None:
        task, spec, sub = _fixture()
        for bad in (0, MAX_LEVEL + 1):
            with pytest.raises(ValueError, match="Hint level"):
                await reveal(
                    level=bad, task=task, language_spec=spec, submission=sub, failed_attempts=9
                )


class TestPenalties:
    def test_first_level_is_free(self) -> None:
        """Назвать провалившийся тест — не подсказка, за это не штрафуют."""
        assert reward_multiplier(1) == 1.0

    def test_penalty_grows_with_level(self) -> None:
        muls = [PENALTY[i] for i in range(1, 6)]
        assert muls == sorted(muls, reverse=True), "штраф обязан расти со ступенью"

    def test_last_level_zeroes_reward(self) -> None:
        """Получив готовое решение, ученик задачу не решил."""
        assert reward_multiplier(5) == 0.0


class TestDeterministicLevels:
    """Первая, вторая и пятая обязаны работать без LLM."""

    async def test_level_one_names_the_failing_test(self) -> None:
        task, spec, sub = _fixture()
        h = await reveal(level=1, task=task, language_spec=spec, submission=sub, failed_attempts=1)
        assert "single" in h.text
        assert not h.generated

    async def test_level_two_picks_hint_matching_the_symptom(self) -> None:
        hints = [
            TaskHint(id=1, task_id=1, text="Generic nudge", symptom="", ordering=1),
            TaskHint(
                id=2, task_id=1, text="Watch the one-element case", symptom="single", ordering=0
            ),
        ]
        task, spec, sub = _fixture(hints=hints)
        h = await reveal(level=2, task=task, language_spec=spec, submission=sub, failed_attempts=1)
        assert h.text == "Watch the one-element case"

    async def test_level_two_falls_back_to_generic(self) -> None:
        hints = [TaskHint(id=1, task_id=1, text="Generic nudge", symptom="", ordering=0)]
        task, spec, sub = _fixture(hints=hints)
        h = await reveal(level=2, task=task, language_spec=spec, submission=sub, failed_attempts=1)
        assert h.text == "Generic nudge"

    async def test_level_two_says_so_when_author_left_nothing(self) -> None:
        """Пустую наводку не выдумываем."""
        task, spec, sub = _fixture(hints=[])
        h = await reveal(level=2, task=task, language_spec=spec, submission=sub, failed_attempts=1)
        assert "No author hint" in h.text

    async def test_level_five_returns_reference_solution(self) -> None:
        task, spec, sub = _fixture(solution="print(sum(x))")
        h = await reveal(level=5, task=task, language_spec=spec, submission=sub, failed_attempts=4)
        assert "print(sum(x))" in h.text
        assert h.reward_multiplier == 0.0


class TestWithoutLLM:
    """Без ключа третья и четвёртая ступени недоступны — и не берут баллов."""

    @pytest.mark.parametrize("level", [3, 4])
    async def test_no_penalty_when_tutor_unavailable(self, level: int) -> None:
        task, spec, sub = _fixture()
        h = await reveal(
            level=level, task=task, language_spec=spec, submission=sub, failed_attempts=4
        )
        assert h.reward_multiplier == 1.0, "нельзя снимать баллы за неполученную подсказку"
        assert not h.generated
        assert "not configured" in h.text or "unavailable" in h.text
