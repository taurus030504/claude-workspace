"""Model-agnostic LLM interface.

Services depend only on :class:`LLMProvider`; Ollama is one implementation.
A future provider (another local runtime, or a cloud API the user explicitly
enables) implements the same three methods.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, Literal, Protocol, runtime_checkable

Role = Literal["system", "user", "assistant"]


@dataclass(frozen=True)
class ChatTurn:
    role: Role
    content: str


@dataclass
class ProviderStatus:
    provider: str
    base_url: str
    reachable: bool
    version: str | None = None
    models: list[str] = field(default_factory=list)
    error: str | None = None


@runtime_checkable
class LLMProvider(Protocol):
    name: str
    base_url: str

    def status(self) -> ProviderStatus:
        """Cheap health probe. Never raises."""
        ...

    def chat_stream(
        self, messages: list[ChatTurn], *, model: str, temperature: float | None = None
    ) -> Iterator[str]:
        """Yield response text pieces. Raises LLMUnavailableError when the
        runtime or model is missing (before the first piece if possible)."""
        ...


def model_available(configured: str, models: list[str]) -> bool:
    """Ollama lists 'gemma3:4b'; a bare 'gemma3' means 'gemma3:latest'."""
    wanted = configured if ":" in configured else f"{configured}:latest"
    return wanted in models or configured in models


def complete(provider: LLMProvider, messages: list[ChatTurn], *, model: str, temperature: float | None = None) -> str:
    return "".join(provider.chat_stream(messages, model=model, temperature=temperature))
