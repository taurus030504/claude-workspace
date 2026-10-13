from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.ai.mock_provider import MockProvider
from app.config import Settings
from app.db.connection import connect
from app.main import create_app


@pytest.fixture
def settings(tmp_path) -> Settings:
    return Settings(
        data_dir=tmp_path / "paw",
        extra_allowed_hosts=["testserver"],
        llm_provider="mock",
        ollama_model="mock-model",
        chunk_max_chars=300,
    )


@pytest.fixture
def provider() -> MockProvider:
    return MockProvider()


@pytest.fixture
def app(settings, provider):
    return create_app(settings, provider)


@pytest.fixture
def client(app) -> TestClient:
    with TestClient(app) as c:
        c.headers["X-PAW-Token"] = app.state.api_token
        yield c


@pytest.fixture
def conn(settings, app):
    c = connect(settings.db_path)
    yield c
    c.close()


def make_page(client: TestClient, title: str, content: str = "", **extra) -> dict:
    r = client.post("/api/v1/wiki/pages", json={"title": title, "content": content, **extra})
    assert r.status_code == 201, r.text
    return r.json()
