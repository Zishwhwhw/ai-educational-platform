"""Обращение к Claude.

Единственное место, где проект знает про LLM. Всё остальное работает через
`generate_json`, поэтому смена модели или провайдера не расходится по коду.

Два свойства заложены с самого начала, потому что дописать их потом дорого:

* **Учёт расхода.** Каждый вызов возвращает потраченные токены. Без этого
  экономика подписки не проверяется, а она в этом продукте под вопросом:
  генерация курса стоит дороже месяца подписки.
* **Работа без ключа.** Если ключ не задан, клиент не падает, а сообщает
  об этом флагом. Подсказки первого, второго и пятого уровня детерминированы
  и обязаны работать всегда — LLM нужен только третьему и четвёртому.
"""

import json
from dataclasses import dataclass
from typing import Any

import anthropic
from anthropic import APIStatusError, AsyncAnthropic

from app.core.config import get_settings
from app.core.logging import get_logger

log = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class LLMResult:
    ok: bool
    data: dict[str, Any] | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""
    # Причина отказа для журнала; пользователю не показывается.
    failure: str = ""

    @property
    def cost_usd(self) -> float:
        """Оценка стоимости вызова.

        Цены зашиты в конфиг, а не в код: они меняются, и пересобирать образ
        ради этого не нужно.
        """
        s = get_settings()
        return (
            self.input_tokens * s.llm_input_price_per_mtok
            + self.output_tokens * s.llm_output_price_per_mtok
        ) / 1_000_000


class LLMClient:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._client: AsyncAnthropic | None = None
        if self._settings.anthropic_api_key:
            self._client = AsyncAnthropic(
                api_key=self._settings.anthropic_api_key,
                timeout=self._settings.llm_timeout_s,
                max_retries=2,
            )

    @property
    def available(self) -> bool:
        return self._client is not None

    async def generate_json(
        self,
        *,
        system: str,
        prompt: str,
        schema: dict[str, Any],
        max_tokens: int = 1024,
        effort: str = "low",
    ) -> LLMResult:
        """Запросить ответ, гарантированно соответствующий схеме.

        `output_config.format` заставляет модель вернуть валидный JSON —
        разбирать текст регулярками не нужно.

        `effort` по умолчанию низкий: подсказка это короткий ответ на понятный
        вопрос, и платить за глубокое рассуждение здесь незачем.
        """
        if self._client is None:
            return LLMResult(ok=False, failure="no_api_key")

        try:
            response = await self._client.messages.create(
                model=self._settings.llm_model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": prompt}],
                output_config={
                    "effort": effort,
                    "format": {"type": "json_schema", "schema": schema},
                },
            )
        except APIStatusError as exc:
            log.warning("llm_api_error", status=exc.status_code, error=str(exc)[:200])
            return LLMResult(ok=False, failure=f"api_error_{exc.status_code}")
        except anthropic.APIError as exc:
            log.warning("llm_transport_error", error=str(exc)[:200])
            return LLMResult(ok=False, failure="transport_error")

        # Отказ классификатора безопасности приходит с кодом 200 — проверять
        # надо stop_reason, а не только статус ответа.
        if response.stop_reason == "refusal":
            log.warning("llm_refusal", model=self._settings.llm_model)
            return LLMResult(ok=False, failure="refusal")

        text = next((b.text for b in response.content if b.type == "text"), "")
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return LLMResult(ok=False, failure="invalid_json")

        return LLMResult(
            ok=True,
            data=data,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            model=self._settings.llm_model,
        )


_client: LLMClient | None = None


def get_llm() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
