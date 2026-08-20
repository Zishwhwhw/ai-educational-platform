"""Контракт движка исполнения кода.

Движок спрятан за интерфейсом намеренно: он меняется по мере роста проекта,
и смена не должна затрагивать проверку заданий, подсказки и античит.

  разработка  → публичный Judge0 CE (бесплатный, без ключа, без гарантий)
  продакшен   → свой Judge0 или Piston в изолированной среде

Движок отвечает только на вопрос «что вывела программа», но **не** на вопрос
«правильно ли решение» — сравнение с ожидаемым выводом живёт выше, в проверке
заданий. Это разделение позволяет менять правила сравнения, не трогая песочницу.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol


class ExecStatus(StrEnum):
    OK = "ok"  # программа завершилась сама, код возврата 0
    RUNTIME_ERROR = "runtime_error"  # исключение или ненулевой код возврата
    COMPILE_ERROR = "compile_error"
    TIMEOUT = "timeout"
    MEMORY_EXCEEDED = "memory_exceeded"
    ENGINE_ERROR = "engine_error"  # не вина пользователя: движок недоступен


@dataclass(frozen=True, slots=True)
class ExecutionRequest:
    language: str
    source: str
    stdin: str = ""
    time_limit_ms: int = 5_000
    memory_limit_mb: int = 128
    # Некоторые языки требуют конкретного имени файла (Java — по имени класса).
    filename: str | None = None


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    status: ExecStatus
    stdout: str = ""
    stderr: str = ""
    compile_output: str = ""
    exit_code: int | None = None
    time_ms: int | None = None
    memory_kb: int | None = None
    # Текст для журнала, наружу пользователю не отдаётся.
    engine_message: str = ""

    @property
    def ran(self) -> bool:
        """Программа действительно выполнилась, и вывод можно сравнивать."""
        return self.status in (ExecStatus.OK, ExecStatus.RUNTIME_ERROR)


@dataclass(frozen=True, slots=True)
class LanguageSpec:
    """Как язык называется у нас и чем он является для конкретного движка."""

    name: str
    display: str
    default_filename: str = "main"
    aliases: tuple[str, ...] = field(default=())


class ExecutionEngine(Protocol):
    """Реализации: Judge0, Piston, локальный Docker."""

    async def run(self, request: ExecutionRequest) -> ExecutionResult: ...

    async def languages(self) -> list[str]: ...

    async def healthy(self) -> bool: ...


class UnsupportedLanguageError(Exception):
    def __init__(self, language: str, supported: list[str]) -> None:
        super().__init__(f"Language {language!r} is not supported by this engine")
        self.language = language
        self.supported = supported
