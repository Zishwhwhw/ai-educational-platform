"""Типы шагов кроме кода.

Проверки чистые: реестр обработчиков не зависит ни от базы, ни от сети.
"""

import pytest

from app.services.steps import InvalidAnswerError, check, public_content


class TestPassiveSteps:
    """Теорию и видео нельзя «пройти неправильно»."""

    @pytest.mark.parametrize("kind", ["text", "video"])
    def test_always_complete(self, kind: str) -> None:
        r = check(kind, {}, {})
        assert r.is_correct and r.score == 1.0


class TestSingleChoice:
    def test_correct(self) -> None:
        assert check("choice_single", {"correct": "b"}, {"choice": "b"}).score == 1.0

    def test_wrong(self) -> None:
        r = check("choice_single", {"correct": "b"}, {"choice": "a"})
        assert not r.is_correct and r.score == 0.0

    def test_missing_answer_rejected(self) -> None:
        with pytest.raises(InvalidAnswerError):
            check("choice_single", {"correct": "b"}, {})


class TestMultipleChoice:
    """Частичный балл есть, но угадывание не поощряется."""

    def test_all_correct(self) -> None:
        r = check("choice_multiple", {"correct": ["a", "b"]}, {"choices": ["a", "b"]})
        assert r.is_correct and r.score == 1.0

    def test_partial_credit(self) -> None:
        r = check("choice_multiple", {"correct": ["a", "b"]}, {"choices": ["a"]})
        assert not r.is_correct
        assert r.score == pytest.approx(0.5)

    def test_extra_selection_is_penalised(self) -> None:
        """Иначе выгодно отметить всё подряд — так ловятся все правильные."""
        r = check("choice_multiple", {"correct": ["a", "b"]}, {"choices": ["a", "b", "c"]})
        assert r.score == pytest.approx(0.5), "лишний вариант должен стоить как пропущенный"

    def test_selecting_everything_scores_low(self) -> None:
        r = check("choice_multiple", {"correct": ["a"]}, {"choices": ["a", "b", "c", "d"]})
        assert r.score == 0.0

    def test_score_never_negative(self) -> None:
        r = check("choice_multiple", {"correct": ["a"]}, {"choices": ["b", "c", "d"]})
        assert r.score == 0.0


class TestStringInput:
    def test_accepts_any_listed_answer(self) -> None:
        """У большинства вопросов несколько равноправных формулировок."""
        grading = {"answers": ["list", "array"]}
        assert check("input_string", grading, {"text": "array"}).is_correct

    def test_ignores_case_and_spaces_by_default(self) -> None:
        assert check("input_string", {"answers": ["List"]}, {"text": "  list "}).is_correct

    def test_case_sensitive_when_asked(self) -> None:
        grading = {"answers": ["List"], "ignore_case": False}
        assert not check("input_string", grading, {"text": "list"}).is_correct


class TestNumberInput:
    def test_tolerance(self) -> None:
        grading = {"value": 0.3333, "tolerance": 0.001}
        assert check("input_number", grading, {"value": "0.333"}).is_correct

    def test_outside_tolerance(self) -> None:
        grading = {"value": 0.3333, "tolerance": 0.0001}
        assert not check("input_number", grading, {"value": "0.33"}).is_correct

    def test_comma_decimal_separator(self) -> None:
        """Половина мира пишет 3,14 — это не повод не засчитать ответ."""
        assert check("input_number", {"value": 3.14}, {"value": "3,14"}).is_correct

    def test_non_numeric_rejected(self) -> None:
        with pytest.raises(InvalidAnswerError):
            check("input_number", {"value": 1}, {"value": "abc"})


class TestMatching:
    def test_all_pairs(self) -> None:
        g = {"pairs": {"1": "a", "2": "b"}}
        assert check("matching", g, {"pairs": {"1": "a", "2": "b"}}).score == 1.0

    def test_partial(self) -> None:
        g = {"pairs": {"1": "a", "2": "b"}}
        r = check("matching", g, {"pairs": {"1": "a", "2": "z"}})
        assert r.score == pytest.approx(0.5)
        assert r.detail == {"matched": 1, "total": 2}


class TestOrdering:
    def test_exact_order(self) -> None:
        g = {"order": ["a", "b", "c"]}
        assert check("ordering", g, {"order": ["a", "b", "c"]}).is_correct

    def test_two_swapped_costs_two_positions(self) -> None:
        """Считаются позиции, а не соседства: перепутав два соседних элемента,
        ученик теряет два места из трёх, а не весь балл."""
        g = {"order": ["a", "b", "c"]}
        r = check("ordering", g, {"order": ["b", "a", "c"]})
        assert r.score == pytest.approx(1 / 3)

    def test_wrong_items_rejected(self) -> None:
        with pytest.raises(InvalidAnswerError):
            check("ordering", {"order": ["a", "b"]}, {"order": ["a", "z"]})


class TestAnswerLeakage:
    """Правильные ответы не должны уходить клиенту ни при каком раскладе."""

    def test_code_type_is_not_answerable_here(self) -> None:
        """Код проверяет песочница, а не сравнение с сохранённым ответом."""
        with pytest.raises(InvalidAnswerError):
            check("code", {}, {})

    def test_public_content_strips_leaked_answers(self) -> None:
        content = {"question": "Pick one", "correct": "b", "answers": ["x"]}
        safe = public_content("choice_single", content)
        assert "correct" not in safe
        assert "answers" not in safe
        assert safe["question"] == "Pick one"

    def test_options_keep_only_id_and_text(self) -> None:
        """Признак правильности рядом с вариантом — классическая утечка."""
        content = {
            "question": "q",
            "options": [{"id": "a", "text": "A", "is_correct": True}],
        }
        safe = public_content("choice_single", content)
        assert safe["options"] == [{"id": "a", "text": "A"}]
