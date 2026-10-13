"""Real Ollama integration tests (not mocks).

Skipped unless PAW_TEST_OLLAMA=1. Requires a running Ollama with the model
named by PAW_TEST_OLLAMA_MODEL (default gemma3:4b) already pulled:

    set PAW_TEST_OLLAMA=1
    python -m pytest -m ollama
"""

import os

import pytest

from app.ai.llm_provider import ChatTurn, complete, model_available
from app.ai.ollama_provider import OllamaProvider

pytestmark = [
    pytest.mark.ollama,
    pytest.mark.skipif(os.environ.get("PAW_TEST_OLLAMA") != "1", reason="set PAW_TEST_OLLAMA=1 to run against real Ollama"),
]

MODEL = os.environ.get("PAW_TEST_OLLAMA_MODEL", "gemma3:4b")
BASE = os.environ.get("PAW_OLLAMA_BASE_URL", "http://127.0.0.1:11434")


def test_real_ollama_status_and_model_present():
    st = OllamaProvider(BASE).status()
    assert st.reachable, st.error
    assert model_available(MODEL, st.models), f"run: ollama pull {MODEL}"


def test_real_ollama_short_korean_answer():
    out = complete(
        OllamaProvider(BASE, num_ctx=2048),
        [ChatTurn("system", "한 문장으로만 답하세요."), ChatTurn("user", "대한민국의 수도는?")],
        model=MODEL,
        temperature=0,
    )
    assert "서울" in out
