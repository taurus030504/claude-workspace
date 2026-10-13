import pytest

from tests.conftest import make_page


@pytest.fixture
def corpus(client):
    pages = {
        "gdd": make_page(client, "게임 설계 문서", "# 개요\n중세 배경의 등반 게임입니다.\n\n# 핵심 메커니즘\n창을 벽에 꽂아 고정하고 반동 점프를 합니다."),
        "controls": make_page(client, "캐릭터 조작 설계", "이동, 점프, 창 던지기 입력을 정의한다.\n\n## 카메라\n3인칭 시점"),
        "physics": make_page(client, "Spear Physics System", "The spear anchors into walls. Bounce jump uses spring force."),
        "recipe": make_page(client, "김치찌개 레시피", "돼지고기와 김치를 볶는다."),
    }
    return {k: v["page_id"] for k, v in pages.items()}


def ids(resp):
    return [h["entity_id"] for h in resp.json()["items"]]


def test_two_syllable_korean_term(client, corpus):
    r = client.get("/api/v1/search", params={"q": "게임"})
    assert r.json()["tokenizer"] == "trigram"
    assert ids(r)[0] == corpus["gdd"]
    assert corpus["recipe"] not in ids(r)


def test_particles_in_query_are_ignored(client, corpus):
    r = client.get("/api/v1/search", params={"q": "등반 게임에서는 창을 어떻게 고정하나요?"})
    assert ids(r)[0] == corpus["gdd"]
    assert "고정" in r.json()["terms"]


def test_long_terms_use_fts_and_english_is_case_insensitive(client, corpus):
    r = client.get("/api/v1/search", params={"q": "BOUNCE jump"})
    assert ids(r) == [corpus["physics"]]
    r = client.get("/api/v1/search", params={"q": "메커니즘"})
    assert ids(r) == [corpus["gdd"]]


def test_title_and_heading_are_reported_with_snippet_highlights(client, corpus):
    hit = client.get("/api/v1/search", params={"q": "카메라 시점"}).json()["items"][0]
    assert hit["title"] == "캐릭터 조작 설계"
    assert hit["heading"] == "카메라"
    s, e = hit["highlights"][0]
    assert hit["snippet"][s:e].lower() in ("카메라", "시점")


def test_grouped_vs_chunk_results(client, corpus):
    grouped = client.get("/api/v1/search", params={"q": "창 고정 점프"}).json()["items"]
    assert len(ids_from(grouped)) == len(set(ids_from(grouped)))
    chunks = client.get("/api/v1/search", params={"q": "점프", "group": "false"}).json()["items"]
    assert all(h["chunk_id"] for h in chunks)


def ids_from(items):
    return [h["entity_id"] for h in items]


def test_updates_are_reflected_immediately(client, corpus):
    pid = corpus["recipe"]
    client.patch(f"/api/v1/wiki/pages/{pid}", json={"expected_revision": 1, "content": "된장찌개로 바꿨다"})
    assert pid not in ids(client.get("/api/v1/search", params={"q": "돼지고기"}))
    assert pid in ids(client.get("/api/v1/search", params={"q": "된장찌개"}))


@pytest.mark.parametrize("q", ['"', "AND OR NOT", "NEAR(a b)", "*", "a:b", "'; DROP TABLE wiki_pages; --", "%_\\"])
def test_fts_syntax_in_queries_is_harmless(client, corpus, q):
    r = client.get("/api/v1/search", params={"q": q})
    assert r.status_code == 200
    assert client.get("/api/v1/wiki/pages").json()["total"] == 4


def test_empty_after_analysis(client, corpus):
    r = client.get("/api/v1/search", params={"q": "어떻게 알려줘"})
    assert r.json()["items"] == [] and r.json()["terms"] == []
