"""Deterministic provider for tests and for running the app without Ollama
(``PAW_LLM_PROVIDER=mock``). Answers are clearly labelled as mock output."""

from __future__ import annotations

import re
from typing import Iterator

from app.ai.llm_provider import ChatTurn, ProviderStatus
from app.core.errors import LLMUnavailableError

_SOURCE_RE = re.compile(r'<source id="(\d+)"')


class MockProvider:
    name = "mock"
    base_url = "mock://local"

    def __init__(self, *, available: bool = True, models: list[str] | None = None, fail_after: int | None = None):
        self.available = available
        self.models = models if models is not None else ["mock-model:latest"]
        self.fail_after = fail_after
        self.calls: list[list[ChatTurn]] = []

    def status(self) -> ProviderStatus:
        if not self.available:
            return ProviderStatus(self.name, self.base_url, False, error="mock provider set unavailable")
        return ProviderStatus(self.name, self.base_url, True, "mock", list(self.models))

    def chat_stream(self, messages: list[ChatTurn], *, model: str, temperature: float | None = None) -> Iterator[str]:
        if not self.available:
            raise LLMUnavailableError("mock provider unavailable", details={"reason": "unreachable"})
        self.calls.append(list(messages))
        question = next((m.content for m in reversed(messages) if m.role == "user"), "")
        source_ids = sorted({int(n) for m in messages for n in _SOURCE_RE.findall(m.content)})
        cite = "".join(f"[{n}]" for n in source_ids[:2])
        answer = f"[모의 응답] 질문: {question.strip()[:60]}" + (f" 참고 자료 {cite}" if cite else " 참고 자료 없음")
        pieces = [answer[i : i + 8] for i in range(0, len(answer), 8)]
        for i, piece in enumerate(pieces):
            if self.fail_after is not None and i >= self.fail_after:
                raise LLMUnavailableError("mock failure mid-stream", details={"reason": "stream_interrupted"})
            yield piece
