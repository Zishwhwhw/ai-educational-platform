"""Выбор движка исполнения по настройкам."""

from functools import lru_cache

from app.core.config import get_settings
from app.services.execution.base import (
    ExecStatus,
    ExecutionEngine,
    ExecutionRequest,
    ExecutionResult,
    UnsupportedLanguageError,
)
from app.services.execution.judge0 import Judge0Engine

__all__ = [
    "ExecStatus",
    "ExecutionEngine",
    "ExecutionRequest",
    "ExecutionResult",
    "UnsupportedLanguageError",
    "get_engine",
]


@lru_cache
def get_engine() -> ExecutionEngine:
    s = get_settings()
    if s.execution_engine == "judge0":
        return Judge0Engine(s.judge0_url, auth_token=s.judge0_token or None)
    raise ValueError(f"Unknown execution engine: {s.execution_engine}")
