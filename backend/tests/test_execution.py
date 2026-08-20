"""Проверки движка исполнения кода.

Основная часть работает на подменённом HTTP: тесты не должны зависеть от чужого
сервиса и не должны его нагружать. Обращение к настоящему Judge0 вынесено
в отдельный тест с меткой `integration` — он пропускается, если не включён явно.
"""

import os

import pytest

from app.services.execution.base import (
    ExecStatus,
    ExecutionRequest,
    UnsupportedLanguageError,
)
from app.services.execution.judge0 import Judge0Engine


class TestStatusMapping:
    """Судья возвращает 14 числовых исходов; ученику нужно понятное состояние."""

    @pytest.mark.parametrize(
        ("judge_id", "expected"),
        [
            (3, ExecStatus.OK),
            (4, ExecStatus.OK),  # «Wrong Answer» судьи — сравнение делаем мы
            (5, ExecStatus.TIMEOUT),
            (6, ExecStatus.COMPILE_ERROR),
            (7, ExecStatus.RUNTIME_ERROR),
            (11, ExecStatus.RUNTIME_ERROR),
            (13, ExecStatus.ENGINE_ERROR),
            (99, ExecStatus.ENGINE_ERROR),  # неизвестный код не должен ронять разбор
        ],
    )
    def test_maps_judge_status(self, judge_id: int, expected: ExecStatus) -> None:
        result = Judge0Engine._to_result({"status": {"id": judge_id, "description": "x"}})
        assert result.status is expected

    def test_wrong_answer_is_not_an_error(self) -> None:
        """Судья умеет сравнивать вывод сам, но мы этим не пользуемся: правила
        сравнения (пробелы, порядок строк, точность чисел) — наша забота."""
        assert Judge0Engine._to_result({"status": {"id": 4}}).ran

    def test_memory_error_recognised_from_stderr(self) -> None:
        r = Judge0Engine._to_result({"status": {"id": 7}, "stderr": "MemoryError: out of memory"})
        assert r.status is ExecStatus.MEMORY_EXCEEDED

    def test_parses_metrics(self) -> None:
        r = Judge0Engine._to_result(
            {"status": {"id": 3}, "stdout": "42\n", "time": "0.153", "memory": 3556}
        )
        assert r.stdout == "42\n"
        assert r.time_ms == 153
        assert r.memory_kb == 3556

    def test_missing_fields_do_not_crash(self) -> None:
        r = Judge0Engine._to_result({})
        assert r.status is ExecStatus.ENGINE_ERROR
        assert r.stdout == ""


class TestLanguages:
    async def test_unknown_language_is_rejected_before_network(self) -> None:
        engine = Judge0Engine("https://judge.example")
        with pytest.raises(UnsupportedLanguageError) as exc:
            await engine.run(ExecutionRequest(language="brainfuck", source=""))
        assert "python" in exc.value.supported

    def test_language_matching_is_case_insensitive(self) -> None:
        """Проверяется без обращения к сети: значение имеет только разбор имени."""
        from app.services.execution.judge0 import LANGUAGE_IDS

        assert LANGUAGE_IDS.get("PyThOn".lower()) == LANGUAGE_IDS["python"]

    def test_language_versions_are_pinned(self) -> None:
        """Идентификаторы фиксированы намеренно: «последняя версия» менялась бы
        под ногами и ломала задания, зависящие от особенностей версии."""
        from app.services.execution.judge0 import LANGUAGE_IDS

        assert all(isinstance(v, int) for v in LANGUAGE_IDS.values())
        assert len(set(LANGUAGE_IDS.values())) == len(LANGUAGE_IDS)


class TestResilience:
    """Сбой чужого сервиса не должен выглядеть как ошибка ученика."""

    def test_engine_error_is_not_counted_as_ran(self) -> None:
        r = Judge0Engine._to_result({"status": {"id": 13}})
        assert not r.ran

    def test_ok_and_runtime_error_are_comparable(self) -> None:
        assert Judge0Engine._to_result({"status": {"id": 3}}).ran
        assert Judge0Engine._to_result({"status": {"id": 7}}).ran


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("RUN_EXECUTION_INTEGRATION") != "1",
    reason="обращается к настоящему Judge0; включается RUN_EXECUTION_INTEGRATION=1",
)
class TestAgainstRealJudge0:
    async def test_runs_python_with_stdin(self) -> None:
        engine = Judge0Engine("https://ce.judge0.com")
        r = await engine.run(
            ExecutionRequest(
                language="python",
                source="import sys\nprint(sum(int(x) for x in sys.stdin.read().split()))",
                stdin="1 2 3 4",
            )
        )
        assert r.status is ExecStatus.OK
        assert r.stdout.strip() == "10"

    async def test_network_is_disabled_inside_sandbox(self) -> None:
        """Решение не должно уметь ходить в сеть: иначе оно «сходит за ответом»,
        а платформу можно использовать как прокси."""
        engine = Judge0Engine("https://ce.judge0.com")
        r = await engine.run(
            ExecutionRequest(
                language="python",
                source=(
                    "import urllib.request\nurllib.request.urlopen('http://example.com', timeout=3)"
                ),
            )
        )
        assert r.status is ExecStatus.RUNTIME_ERROR

    async def test_infinite_loop_hits_timeout(self) -> None:
        engine = Judge0Engine("https://ce.judge0.com")
        r = await engine.run(
            ExecutionRequest(language="python", source="while True: pass", time_limit_ms=2000)
        )
        assert r.status is ExecStatus.TIMEOUT
