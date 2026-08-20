"""Пятиступенчатая лестница подсказок.

Заменяет `app/services/hints.py`, где подсказка была заготовленным текстом
вроде «проверь синтаксис» — одинаковым для любой задачи и любого кода ученика.

Ступени по спеке:

    1  просто «неправильно»
    2  лёгкая наводка
    3  где ошибка
    4  точная ошибка и как исправить
    5  готовый ответ

Два свойства важнее остальных:

* **Ступени 1, 2 и 5 детерминированы и не требуют LLM.** Первая называет
  провалившийся тест, вторая берёт заготовку автора, пятая отдаёт эталон.
  Значит подсказки работают и без ключа, и при сбое провайдера.
* **Ступени необратимы и стоят баллов.** Раскрытие уменьшает награду,
  пятая обнуляет. Поэтому подтверждение спрашивается до раскрытия,
  а размер штрафа называется заранее.
"""

from dataclasses import dataclass

from app.models import Submission, Task, TaskLanguage
from app.services.llm import get_llm

MAX_LEVEL = 5

# Во сколько раз уменьшается награда после раскрытия ступени.
# Пятая обнуляет: получив готовое решение, ученик задачу не решил.
PENALTY: dict[int, float] = {0: 1.0, 1: 1.0, 2: 0.9, 3: 0.8, 4: 0.6, 5: 0.0}

# Сколько неудачных попыток нужно, чтобы ступень открылась. Первая и вторая
# доступны сразу после первого провала: держать ученика в неведении, какой
# тест упал, — это не сложность, а плохой интерфейс.
UNLOCK_AFTER_FAILURES: dict[int, int] = {1: 1, 2: 1, 3: 2, 4: 3, 5: 4}


@dataclass(frozen=True, slots=True)
class Hint:
    level: int
    text: str
    # True, если текст сгенерирован моделью, а не взят из данных.
    generated: bool = False
    # Множитель награды после раскрытия этой ступени.
    reward_multiplier: float = 1.0
    cost_usd: float = 0.0


class HintNotUnlockedError(Exception):
    def __init__(self, level: int, required_failures: int, actual: int) -> None:
        super().__init__(
            f"Hint level {level} unlocks after {required_failures} failed attempts "
            f"({actual} so far)"
        )
        self.level = level
        self.required_failures = required_failures
        self.actual = actual


def reward_multiplier(level: int) -> float:
    return PENALTY.get(level, 0.0)


def is_unlocked(level: int, failed_attempts: int) -> bool:
    return failed_attempts >= UNLOCK_AFTER_FAILURES.get(level, MAX_LEVEL)


def _failed_test_names(submission: Submission, task: Task) -> list[str]:
    by_id = {c.id: c for c in task.test_cases}
    return [
        str(by_id[r.test_case_id].name or f"test {i + 1}")
        for i, r in enumerate(submission.results)
        if not r.passed and r.test_case_id in by_id
    ]


def _level_one(submission: Submission, task: Task) -> Hint:
    """«Неправильно», но не бесполезно.

    Спека говорит «просто неправильно». Буквальное прочтение бессмысленно:
    ученик и так видит красные строки. Первая ступень называет, какой тест
    упал, и ничего не объясняет — этого достаточно, чтобы направить взгляд.
    """
    failed = _failed_test_names(submission, task)
    if not failed:
        text = "Not quite yet. Run the tests to see what fails."
    elif len(failed) == 1:
        text = f'Not quite. The test "{failed[0]}" does not pass.'
    else:
        text = f'Not quite. {len(failed)} tests do not pass, starting with "{failed[0]}".'
    return Hint(level=1, text=text, reward_multiplier=PENALTY[1])


def _level_two(task: Task, submission: Submission) -> Hint:
    """Заготовка автора, выбранная по симптому.

    Автор задания пишет наводки заранее и помечает, к какому провалу каждая
    относится. Это дешевле и надёжнее генерации: автор знает, где именно
    спотыкаются на его задаче.
    """
    failed = set(_failed_test_names(submission, task))
    hints = sorted(task.hints, key=lambda h: int(h.ordering))

    for hint in hints:
        symptom = str(hint.symptom or "")
        if symptom and symptom in failed:
            return Hint(level=2, text=str(hint.text), reward_multiplier=PENALTY[2])

    generic = next((h for h in hints if not h.symptom), None)
    if generic is not None:
        return Hint(level=2, text=str(generic.text), reward_multiplier=PENALTY[2])

    # Автор наводок не оставил — честно говорим об этом, а не выдумываем.
    return Hint(
        level=2,
        text="No author hint is available for this task. Try the next level.",
        reward_multiplier=PENALTY[2],
    )


def _level_five(spec: TaskLanguage) -> Hint:
    solution = str(spec.reference_solution or "")
    if not solution:
        return Hint(
            level=5,
            text="No reference solution is available for this task.",
            reward_multiplier=PENALTY[5],
        )
    return Hint(
        level=5,
        text=f"Reference solution:\n\n```{spec.language}\n{solution}\n```",
        reward_multiplier=PENALTY[5],
    )


_SYSTEM = """You are a programming tutor helping a student debug their own code.

Hard rules:
- Never write a working solution, and never write more than two lines of code.
- Never reveal the contents of hidden tests.
- Address the student directly, in plain language, in at most three sentences.
- If the code is already correct for the failing case, say what edge case it misses.

You are given the task, the student's code and which tests failed. The student
has already been told which test fails, so do not simply repeat that."""

_LEVEL_THREE_TASK = (
    "Point at WHERE the problem is — a line, a construct, or a missing case. "
    "Do not say how to fix it."
)
_LEVEL_FOUR_TASK = (
    "State exactly WHAT is wrong and HOW to fix it, in words. "
    "You may show at most two lines of code, and they must not be the full solution."
)

_SCHEMA = {
    "type": "object",
    "properties": {"hint": {"type": "string", "maxLength": 400}},
    "required": ["hint"],
    "additionalProperties": False,
}


async def _generated(level: int, task: Task, submission: Submission) -> Hint:
    llm = get_llm()
    if not llm.available:
        # Без ключа третья и четвёртая ступени недоступны. Не выдумываем
        # текст и не берём тихо ступень ниже: ученик уже заплатил баллами.
        return Hint(
            level=level,
            text=(
                "This hint level needs the AI tutor, which is not configured "
                "right now. No points were deducted."
            ),
            reward_multiplier=1.0,
        )

    failed = _failed_test_names(submission, task)
    prompt = (
        f"Task:\n{task.prompt}\n\n"
        f"Student's code:\n```\n{submission.code}\n```\n\n"
        f"Failing tests: {', '.join(failed) or 'unknown'}\n\n"
        f"{_LEVEL_THREE_TASK if level == 3 else _LEVEL_FOUR_TASK}"
    )

    result = await llm.generate_json(system=_SYSTEM, prompt=prompt, schema=_SCHEMA, max_tokens=512)
    if not result.ok or not result.data:
        return Hint(
            level=level,
            text="The AI tutor is unavailable right now. No points were deducted.",
            reward_multiplier=1.0,
        )

    return Hint(
        level=level,
        text=str(result.data.get("hint", "")).strip(),
        generated=True,
        reward_multiplier=PENALTY[level],
        cost_usd=result.cost_usd,
    )


async def reveal(
    *,
    level: int,
    task: Task,
    language_spec: TaskLanguage,
    submission: Submission,
    failed_attempts: int,
) -> Hint:
    if level < 1 or level > MAX_LEVEL:
        raise ValueError(f"Hint level must be 1..{MAX_LEVEL}, got {level}")

    if not is_unlocked(level, failed_attempts):
        raise HintNotUnlockedError(level, UNLOCK_AFTER_FAILURES[level], failed_attempts)

    if level == 1:
        return _level_one(submission, task)
    if level == 2:
        return _level_two(task, submission)
    if level == 5:
        return _level_five(language_spec)
    return await _generated(level, task, submission)
