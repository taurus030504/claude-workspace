"""Ollama HTTP client (https://github.com/ollama/ollama/blob/main/docs/api.md).

Uses ``/api/version`` and ``/api/tags`` for status and ``/api/chat`` with
streaming NDJSON for generation.
"""

from __future__ import annotations

import json
import logging
from typing import Iterator

import httpx

from app.ai.llm_provider import ChatTurn, ProviderStatus
from app.core.errors import LLMUnavailableError

log = logging.getLogger(__name__)


class OllamaProvider:
    name = "ollama"

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 300.0,
        num_ctx: int = 4096,
        default_temperature: float = 0.3,
        transport: httpx.BaseTransport | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.num_ctx = num_ctx
        self.default_temperature = default_temperature
        # Long read timeout: CPU inference on a cold model can take a while to emit the first token.
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=httpx.Timeout(connect=3.0, read=timeout, write=30.0, pool=5.0),
            transport=transport,
            trust_env=False,  # never route local model traffic through a system proxy
        )

    def close(self) -> None:
        self._client.close()

    def status(self) -> ProviderStatus:
        try:
            version = self._client.get("/api/version", timeout=3.0).json().get("version")
            tags = self._client.get("/api/tags", timeout=5.0)
            tags.raise_for_status()
            models = sorted(m["name"] for m in tags.json().get("models", []))
            return ProviderStatus(self.name, self.base_url, True, version, models)
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            return ProviderStatus(self.name, self.base_url, False, error=str(exc) or type(exc).__name__)

    def chat_stream(
        self, messages: list[ChatTurn], *, model: str, temperature: float | None = None
    ) -> Iterator[str]:
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": True,
            "keep_alive": "10m",
            "options": {
                "num_ctx": self.num_ctx,
                "temperature": self.default_temperature if temperature is None else temperature,
            },
        }
        try:
            with self._client.stream("POST", "/api/chat", json=payload) as resp:
                if resp.status_code != 200:
                    body = resp.read().decode("utf-8", "replace")
                    raise _http_error(resp.status_code, body, model)
                for line in resp.iter_lines():
                    if not line.strip():
                        continue
                    data = json.loads(line)
                    if "error" in data:
                        raise LLMUnavailableError(f"Ollama error: {data['error']}")
                    piece = (data.get("message") or {}).get("content", "")
                    if piece:
                        yield piece
                    if data.get("done"):
                        log.info(
                            "ollama done model=%s eval_count=%s total_ms=%s",
                            model, data.get("eval_count"), int(data.get("total_duration", 0) / 1e6),
                        )
                        return
        except httpx.ConnectError as exc:
            raise LLMUnavailableError(
                f"Ollama에 연결할 수 없습니다 ({self.base_url}). Ollama가 실행 중인지 확인하세요.",
                details={"reason": "unreachable"},
            ) from exc
        except httpx.TimeoutException as exc:
            raise LLMUnavailableError(
                "Ollama 응답 시간이 초과되었습니다. 더 작은 모델을 쓰거나 잠시 후 다시 시도하세요.",
                details={"reason": "timeout"},
            ) from exc


def _http_error(status: int, body: str, model: str) -> LLMUnavailableError:
    try:
        message = json.loads(body).get("error", body)
    except ValueError:
        message = body
    if status == 404 or "not found" in message.lower():
        return LLMUnavailableError(
            f"모델 '{model}'이(가) 설치되어 있지 않습니다. 터미널에서 'ollama pull {model}'을 실행하세요.",
            details={"reason": "model_missing", "model": model},
        )
    return LLMUnavailableError(f"Ollama 오류 ({status}): {message}", details={"reason": "http_error"})
