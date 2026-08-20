"""Адаптер Judge0.

Работает и с публичным Judge0 CE (бесплатно, без ключа), и со своим экземпляром —
разница только в базовом адресе и наличии токена.

Публичный экземпляр годится для разработки и не годится для боя: нет гарантий
доступности, есть ограничение частоты, и чужой сервис видит код учеников.
Перед запуском поднимается свой; смена — это адрес в конфиге, код не меняется.
"""

import asyncio

import httpx

from app.core.logging import get_logger
from app.services.execution.base import (
    ExecStatus,
    ExecutionRequest,
    ExecutionResult,
    UnsupportedLanguageError,
)

log = get_logger(__name__)

# Судья различает языки числовыми идентификаторами. Версии зафиксированы:
# «последняя доступная» менялась бы под ногами и ломала бы задания, которые
# зависят от особенностей версии.
LANGUAGE_IDS: dict[str, int] = {
    "python": 71,  # 3.8.1
    "javascript": 102,  # Node.js 22
    "typescript": 101,
    "java": 91,  # JDK 17
    "go": 107,  # 1.23
    "rust": 108,
    "c": 103,  # GCC 14
    "cpp": 105,  # GCC 14
    "csharp": 51,
    "php": 68,
    "ruby": 72,
    "kotlin": 111,
    "swift": 83,
    "sql": 82,  # SQLite
    "bash": 46,
}

# Классификация исходов. Коды 7–12 — разные варианты аварийного завершения
# (сигналы, выход за пределы памяти в рантайме, ненулевой код возврата);
# для ученика все они означают одно: «программа упала».
_STATUS_MAP: dict[int, ExecStatus] = {
    3: ExecStatus.OK,
    4: ExecStatus.OK,  # «Wrong Answer» судьи: сравнение делаем мы, а не он
    5: ExecStatus.TIMEOUT,
    6: ExecStatus.COMPILE_ERROR,
    7: ExecStatus.RUNTIME_ERROR,
    8: ExecStatus.RUNTIME_ERROR,
    9: ExecStatus.RUNTIME_ERROR,
    10: ExecStatus.RUNTIME_ERROR,
    11: ExecStatus.RUNTIME_ERROR,
    12: ExecStatus.RUNTIME_ERROR,
    13: ExecStatus.ENGINE_ERROR,
    14: ExecStatus.ENGINE_ERROR,
}


class Judge0Engine:
    def __init__(
        self,
        base_url: str,
        *,
        auth_token: str | None = None,
        timeout_s: float = 30.0,
        max_attempts: int = 3,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_s = timeout_s
        self._max_attempts = max_attempts
        headers = {"Content-Type": "application/json"}
        if auth_token:
            headers["X-Auth-Token"] = auth_token
        self._headers = headers

    async def run(self, request: ExecutionRequest) -> ExecutionResult:
        language_id = LANGUAGE_IDS.get(request.language.lower())
        if language_id is None:
            raise UnsupportedLanguageError(request.language, sorted(LANGUAGE_IDS))

        payload = {
            "language_id": language_id,
            "source_code": request.source,
            "stdin": request.stdin,
            # Judge0 принимает лимит времени в секундах дробным числом.
            "cpu_time_limit": max(1, round(request.time_limit_ms / 1000)),
            "wall_time_limit": max(2, round(request.time_limit_ms / 1000) + 2),
            "memory_limit": request.memory_limit_mb * 1024,  # килобайты
            # Сеть в песочнице выключена: иначе решение может «сходить за ответом»,
            # выкачать что угодно или использовать платформу как прокси.
            "enable_network": False,
        }

        last_error = ""
        for attempt in range(1, self._max_attempts + 1):
            try:
                async with httpx.AsyncClient(timeout=self._timeout_s) as client:
                    resp = await client.post(
                        f"{self._base_url}/submissions",
                        params={"base64_encoded": "false", "wait": "true"},
                        json=payload,
                        headers=self._headers,
                    )
                if resp.status_code == httpx.codes.TOO_MANY_REQUESTS:
                    # Публичный экземпляр ограничивает частоту. Ждём с нарастанием.
                    await asyncio.sleep(2**attempt)
                    last_error = "rate limited"
                    continue
                resp.raise_for_status()
                return self._to_result(resp.json())
            except httpx.HTTPError as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                log.warning("judge0_attempt_failed", attempt=attempt, error=last_error)
                if attempt < self._max_attempts:
                    await asyncio.sleep(1.5 * attempt)

        # Недоступность движка — не ошибка ученика: попытка не должна засчитываться
        # как неудачная, иначе сбой инфраструктуры съедает подсказки и баллы.
        return ExecutionResult(
            status=ExecStatus.ENGINE_ERROR,
            engine_message=f"engine unavailable after {self._max_attempts} attempts: {last_error}",
        )

    @staticmethod
    def _to_result(data: dict[str, object]) -> ExecutionResult:
        raw_status = data.get("status") or {}
        status_id = int(raw_status.get("id", 13)) if isinstance(raw_status, dict) else 13
        status = _STATUS_MAP.get(status_id, ExecStatus.ENGINE_ERROR)

        stderr = str(data.get("stderr") or "")
        # Выход за память судья иногда отдаёт как обычное аварийное завершение —
        # уточняем по тексту, иначе ученик увидит «упало» вместо «не хватило памяти».
        if status is ExecStatus.RUNTIME_ERROR and "memory" in stderr.lower():
            status = ExecStatus.MEMORY_EXCEEDED

        time_raw = data.get("time")
        return ExecutionResult(
            status=status,
            stdout=str(data.get("stdout") or ""),
            stderr=stderr,
            compile_output=str(data.get("compile_output") or ""),
            exit_code=data.get("exit_code") if isinstance(data.get("exit_code"), int) else None,
            time_ms=int(float(time_raw) * 1000) if time_raw else None,
            memory_kb=int(data["memory"]) if isinstance(data.get("memory"), int | float) else None,
            engine_message=str(raw_status.get("description", ""))
            if isinstance(raw_status, dict)
            else "",
        )

    async def languages(self) -> list[str]:
        return sorted(LANGUAGE_IDS)

    async def healthy(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{self._base_url}/languages", headers=self._headers)
            return resp.status_code == httpx.codes.OK
        except httpx.HTTPError:
            return False
