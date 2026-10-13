import pytest

from app.config import Settings
from app.db.connection import connect
from app.main import create_app
from tests.conftest import make_page


def test_health_and_status(client, settings):
    h = client.get("/api/v1/health").json()
    assert h["status"] == "ok" and h["schema_version"] == 1
    make_page(client, "a", "b")
    st = client.get("/api/v1/system/status").json()
    assert st["page_count"] == 1 and st["fts_tokenizer"] == "trigram"
    assert st["data_dir"] == str(settings.data_dir)
    assert st["external_network_allowed"] is False


def test_llm_status_and_guidance(client, provider):
    st = client.get("/api/v1/system/llm").json()
    assert st["reachable"] and st["model_available"] and st["guidance"] == []

    client.patch("/api/v1/settings", json={"llm_model": "gemma3:4b"})
    st = client.get("/api/v1/system/llm").json()
    assert not st["model_available"]
    assert any("ollama pull gemma3:4b" in g for g in st["guidance"])

    provider.available = False
    st = client.get("/api/v1/system/llm").json()
    assert not st["reachable"]
    assert any("ollama.com/download" in g for g in st["guidance"])


def test_settings_roundtrip(client):
    s = client.get("/api/v1/settings").json()
    assert s["search_wiki"] is True and s["available_search_sources"] == ["wiki"]
    s = client.patch("/api/v1/settings", json={"llm_model": " exaone3.5:2.4b ", "search_memory": False}).json()
    assert s["llm_model"] == "exaone3.5:2.4b" and s["search_memory"] is False and s["search_wiki"] is True


def test_backup_endpoint_writes_verified_copy(client, settings):
    make_page(client, "백업 대상", "내용")
    r = client.post("/api/v1/system/backup").json()
    copy = connect(r["path"])
    assert copy.execute("SELECT title FROM wiki_pages").fetchone()[0] == "백업 대상"


def test_reindex_and_startup_repair(client, settings, provider):
    make_page(client, "인덱스 문서", "재색인 확인용 본문")
    conn = connect(settings.db_path)
    conn.execute("DELETE FROM search_index")
    conn.close()
    assert client.get("/api/v1/search", params={"q": "재색인"}).json()["items"] == []
    assert client.post("/api/v1/system/reindex").json() == {"pages_indexed": 1}
    assert client.get("/api/v1/search", params={"q": "재색인"}).json()["items"]

    # an out-of-sync index is also rebuilt automatically at startup
    conn = connect(settings.db_path)
    conn.execute("DELETE FROM search_index")
    conn.close()
    create_app(settings, provider)
    conn = connect(settings.db_path)
    assert conn.execute("SELECT count(*) FROM search_index").fetchone()[0] == 1


def test_token_is_stable_across_restarts(settings, provider, app):
    again = create_app(settings, provider)
    assert again.state.api_token == app.state.api_token
    assert settings.token_path.read_text().strip() == app.state.api_token


@pytest.mark.parametrize(
    "overrides, message",
    [
        ({"host": "0.0.0.0"}, "not a loopback"),
        ({"ollama_base_url": "http://192.168.0.10:11434"}, "non-local host"),
    ],
)
def test_network_policy_refuses_unsafe_config(tmp_path, overrides, message):
    with pytest.raises(ValueError, match=message):
        Settings(data_dir=tmp_path, **overrides).validate_network_policy()


def test_network_policy_allows_explicit_opt_in(tmp_path):
    Settings(data_dir=tmp_path, host="0.0.0.0", allow_remote_bind=True).validate_network_policy()
    Settings(data_dir=tmp_path, ollama_base_url="http://10.0.0.5:11434", allow_external_network=True).validate_network_policy()
    Settings(data_dir=tmp_path, ollama_base_url="http://localhost:11434").validate_network_policy()
