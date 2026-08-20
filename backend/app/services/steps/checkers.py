"""Проверка ответов на шаги.

Реестр обработчиков: один тип шага — одна функция. Добавление типа это новая
функция и строка в реестре, без миграции и без правки вызывающего кода.

Общее правило для всех типов: **частичный балл там, где он осмыслен.**
Выбрать три правильных варианта из четырёх — не то же самое, что не выбрать
ничего, и оценка должна это различать. Но угадывание не поощряется:
за лишние выбранные варианты балл снижается.
"""

from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

STEP_TYPES = (
    "text",
    "video",
    "choice_single",
    "choice_multiple",
    "input_string",
    "input_number",
    "matching",
    "ordering",
    "code",
)

# Шаги, которые засчитываются самим фактом прохождения: читать теорию
# «правильно» нельзя.
PASSIVE_TYPES = frozenset({"text", "video"})


@dataclass(frozen=True, slots=True)
class CheckResult:
    is_correct: bool
    score: float
    """Доля от 0.0 до 1.0. Балл шага умножается на неё."""
    feedback: str = ""
    # Что показать разбором: например, какие пары сопоставлены неверно.
    detail: dict[str, Any] | None = None


class InvalidAnswerError(ValueError):
    """Ответ не той формы, какую ожидает тип шага."""


def _as_str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise InvalidAnswerError(f"{field} must be a list of strings")
    return value


def check_passive(_grading: dict[str, Any], _answer: dict[str, Any]) -> CheckResult:
    """Теория и видео: засчитываются фактом прохождения.

    Настоящая проверка «прочитал ли» невозможна, а таймер на чтение —
    отдельный механизм античита, не проверка ответа.
    """
    return CheckResult(is_correct=True, score=1.0)


def check_choice_single(grading: dict[str, Any], answer: dict[str, Any]) -> CheckResult:
    correct = grading.get("correct")
    chosen = answer.get("choice")
    if not isinstance(chosen, str):
        raise InvalidAnswerError("choice must be a string option id")
    ok = chosen == correct
    return CheckResult(is_correct=ok, score=1.0 if ok else 0.0)


def check_choice_multiple(grading: dict[str, Any], answer: dict[str, Any]) -> CheckResult:
    """Частичный балл с наказанием за лишние варианты.

    Без наказания выгоднее отметить всё подряд: выбрав все варианты, ученик
    гарантированно поймает все правильные. Поэтому лишний выбор вычитается
    наравне с пропущенным правильным.
    """
    correct = set(_as_str_list(grading.get("correct", []), "correct"))
    chosen = set(_as_str_list(answer.get("choices", []), "choices"))
    if not correct:
        raise InvalidAnswerError("step has no correct answers configured")

    hits = len(correct & chosen)
    extra = len(chosen - correct)
    score = max(0.0, (hits - extra) / len(correct))
    return CheckResult(
        is_correct=chosen == correct,
        score=score,
        detail={"selected": len(chosen), "correct_total": len(correct)},
    )


def check_input_string(grading: dict[str, Any], answer: dict[str, Any]) -> CheckResult:
    """Свободный ввод: сверка со списком принимаемых ответов.

    Список, а не одна строка: у большинства вопросов есть несколько
    равноправных формулировок, и заставлять угадывать авторскую — не проверка
    знания, а лотерея.
    """
    accepted = _as_str_list(grading.get("answers", []), "answers")
    given = answer.get("text")
    if not isinstance(given, str):
        raise InvalidAnswerError("text must be a string")

    norm = given.strip()
    if grading.get("ignore_case", True):
        norm = norm.casefold()
        accepted = [a.strip().casefold() for a in accepted]
    else:
        accepted = [a.strip() for a in accepted]

    ok = norm in accepted
    return CheckResult(is_correct=ok, score=1.0 if ok else 0.0)


def check_input_number(grading: dict[str, Any], answer: dict[str, Any]) -> CheckResult:
    """Число с допуском: 0.333 должно приниматься за 1/3."""
    try:
        expected = Decimal(str(grading["value"]))
        tolerance = Decimal(str(grading.get("tolerance", 0)))
    except (KeyError, InvalidOperation) as exc:
        raise InvalidAnswerError("step has no numeric answer configured") from exc

    raw = answer.get("value")
    try:
        given = Decimal(str(raw).strip().replace(",", "."))
    except (InvalidOperation, AttributeError, TypeError) as exc:
        raise InvalidAnswerError("value must be a number") from exc

    ok = abs(given - expected) <= tolerance
    return CheckResult(is_correct=ok, score=1.0 if ok else 0.0)


def check_matching(grading: dict[str, Any], answer: dict[str, Any]) -> CheckResult:
    """Сопоставление: частичный балл по числу верных пар."""
    pairs = grading.get("pairs")
    given = answer.get("pairs")
    if not isinstance(pairs, dict) or not pairs:
        raise InvalidAnswerError("step has no pairs configured")
    if not isinstance(given, dict):
        raise InvalidAnswerError("pairs must be an object of left -> right ids")

    hits = sum(1 for left, right in pairs.items() if given.get(left) == right)
    score = hits / len(pairs)
    return CheckResult(
        is_correct=hits == len(pairs),
        score=score,
        detail={"matched": hits, "total": len(pairs)},
    )


def check_ordering(grading: dict[str, Any], answer: dict[str, Any]) -> CheckResult:
    """Сортировка: частичный балл по числу элементов на своих местах.

    Считаются именно позиции, а не соседства: перепутав два соседних
    элемента, ученик теряет два места из N, а не весь балл.
    """
    expected = _as_str_list(grading.get("order", []), "order")
    given = _as_str_list(answer.get("order", []), "order")
    if not expected:
        raise InvalidAnswerError("step has no order configured")
    if sorted(given) != sorted(expected):
        raise InvalidAnswerError("order must contain exactly the step's items")

    hits = sum(1 for i, item in enumerate(expected) if i < len(given) and given[i] == item)
    return CheckResult(
        is_correct=given == expected,
        score=hits / len(expected),
        detail={"in_place": hits, "total": len(expected)},
    )


CHECKERS: dict[str, Callable[[dict[str, Any], dict[str, Any]], CheckResult]] = {
    "text": check_passive,
    "video": check_passive,
    "choice_single": check_choice_single,
    "choice_multiple": check_choice_multiple,
    "input_string": check_input_string,
    "input_number": check_input_number,
    "matching": check_matching,
    "ordering": check_ordering,
    # "code" здесь намеренно отсутствует: его проверяет песочница через
    # services/grading, а не сравнение с сохранённым ответом.
}


def check(step_type: str, grading: dict[str, Any], answer: dict[str, Any]) -> CheckResult:
    checker = CHECKERS.get(step_type)
    if checker is None:
        raise InvalidAnswerError(f"Step type {step_type!r} is not answerable here")
    return checker(grading or {}, answer or {})


def public_content(step_type: str, content: dict[str, Any]) -> dict[str, Any]:
    """Что из шага можно показать ученику.

    Дополнительная защита поверх разделения полей: даже если правильный ответ
    по недосмотру окажется в `content`, он не уйдёт наружу.
    """
    safe = dict(content or {})
    for leaked in ("correct", "answers", "pairs", "order", "value", "solution"):
        safe.pop(leaked, None)
    if step_type in ("choice_single", "choice_multiple"):
        # У вариантов оставляем только идентификатор и текст: признак
        # правильности рядом с вариантом — классическая утечка.
        options = safe.get("options")
        if isinstance(options, list):
            safe["options"] = [
                {"id": o.get("id"), "text": o.get("text")} for o in options if isinstance(o, dict)
            ]
    return safe
