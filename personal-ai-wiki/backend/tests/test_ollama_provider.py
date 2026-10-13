"""OllamaProvider against a fake Ollama HTTP API (httpx.MockTransport).
These are mock tests: they check request/response handling, not a real model.
Real-model tests live in test_ollama_integration.py."""

import json

import httpx
import pytest

from app.ai.llm_provider import ChatTurn, complete, model_available
from app.ai.ollama_provider import OllamaProvider
from app.core.errors import LLMUnavailableError


def fake_ollama(installed=("gemma3:4b",), seen=None):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/version":
            return httpx.Response(200, json={"version": "0.12.0"})
        if request.url.path == "/api/tags":
            return httpx.Response(200, json={"models": [{"name": n} for n in installed]})
        if request.url.path == "/api/chat":
            body = json.loads(request.content)
            if seen is not None:
                seen.append(body)
            if body["model"] not in installed:
                return httpx.Response(404, json={"error": f"model '{body['model']}' not found"})
            lines = [
                {"message": {"role": "assistant", "content": "안녕"}, "done": False},
                {"message": {"role": "assistant", "content": "하세요"}, "done": False},
                {"message": {"role": "assistant", "content": ""}, "done": True, "eval_count": 2},
            ]
            return httpx.Response(200, content="\n".join(json.dumps(x) for x in lines).encode())
        return httpx.Response(404)

    return httpx.MockTransport(handler)


def test_status_lists_models():
    p = OllamaProvider("http://127.0.0.1:11434", transport=fake_ollama())
    st = p.status()
    assert st.reachable and st.version == "0.12.0" and st.models == ["gemma3:4b"]


def test_streaming_chat_and_request_shape():
    seen: list[dict] = []
    p = OllamaProvider("http://127.0.0.1:11434", num_ctx=2048, transport=fake_ollama(seen=seen))
    out = complete(p, [ChatTurn("system", "s"), ChatTurn("user", "u")], model="gemma3:4b", temperature=0.1)
    assert out == "안녕하세요"
    assert seen[0]["stream"] is True
    assert seen[0]["options"] == {"num_ctx": 2048, "temperature": 0.1}
    assert seen[0]["messages"][1] == {"role": "user", "content": "u"}


def test_missing_model_maps_to_pull_instruction():
    p = OllamaProvider("http://127.0.0.1:11434", transport=fake_ollama())
    with pytest.raises(LLMUnavailableError) as e:
        complete(p, [ChatTurn("user", "x")], model="qwen2.5:3b")
    assert e.value.details["reason"] == "model_missing"
    assert "ollama pull qwen2.5:3b" in e.value.message


def test_unreachable_server():
    def refuse(request):
        raise httpx.ConnectError("refused", request=request)

    p = OllamaProvider("http://127.0.0.1:11434", transport=httpx.MockTransport(refuse))
    assert p.status().reachable is False
    with pytest.raises(LLMUnavailableError) as e:
        complete(p, [ChatTurn("user", "x")], model="gemma3:4b")
    assert e.value.details["reason"] == "unreachable"


def test_model_name_matching():
    assert model_available("gemma3", ["gemma3:latest"])
    assert model_available("gemma3:4b", ["gemma3:4b"])
    assert not model_available("gemma3:4b", ["gemma3:12b"])
