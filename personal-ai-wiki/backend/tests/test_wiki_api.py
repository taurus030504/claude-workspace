from fastapi.testclient import TestClient

from tests.conftest import make_page


def test_auth_required_except_health(app):
    with TestClient(app) as anon:
        assert anon.get("/api/v1/health").status_code == 200
        r = anon.get("/api/v1/wiki/pages")
        assert r.status_code == 401
        assert r.json()["error"]["code"] == "unauthorized"
        assert anon.get("/api/v1/wiki/pages", headers={"X-PAW-Token": "wrong"}).status_code == 401
        ok = anon.get("/api/v1/wiki/pages", headers={"Authorization": f"Bearer {app.state.api_token}"})
        assert ok.status_code == 200


def test_unexpected_host_header_rejected(client):
    r = client.get("/api/v1/health", headers={"Host": "evil.example.com"})
    assert r.status_code == 400


def test_create_get_list_page(client):
    page = make_page(client, "  게임 설계 문서 ", "# 개요\n중세 등반 게임", folder="게임/설계", tags=["게임", "#설계", "게임"])
    assert page["title"] == "게임 설계 문서"
    assert page["folder"] == "게임/설계"
    assert page["tags"] == ["게임", "설계"]
    assert page["current_revision"] == 1
    assert len(page["page_id"]) == 36

    got = client.get(f"/api/v1/wiki/pages/{page['page_id']}").json()
    assert got["content"] == "# 개요\n중세 등반 게임"

    listing = client.get("/api/v1/wiki/pages").json()
    assert listing["total"] == 1
    assert listing["items"][0]["excerpt"].startswith("개요")
    assert "content" not in listing["items"][0]

    assert client.get("/api/v1/wiki/pages", params={"folder": "게임"}).json()["items"]  # subfolder included
    assert client.get("/api/v1/wiki/pages", params={"tag": "설계"}).json()["items"]
    assert client.get("/api/v1/wiki/folders").json() == [{"folder": "게임/설계", "page_count": 1}]
    assert {t["name"] for t in client.get("/api/v1/wiki/tags").json()} == {"게임", "설계"}


def test_validation_errors_use_error_envelope(client):
    r = client.post("/api/v1/wiki/pages", json={"title": "   "})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"
    r = client.post("/api/v1/wiki/pages", json={"title": "x", "folder": "../etc"})
    assert r.status_code == 422


def test_update_creates_revisions_and_history_is_kept(client):
    page = make_page(client, "창 물리", "v1")
    pid = page["page_id"]
    r = client.patch(f"/api/v1/wiki/pages/{pid}", json={"expected_revision": 1, "content": "v2", "change_note": "수정"})
    assert r.status_code == 200 and r.json()["current_revision"] == 2
    r = client.patch(f"/api/v1/wiki/pages/{pid}", json={"expected_revision": 2, "title": "창 물리 시스템"})
    assert r.json()["current_revision"] == 3

    revs = client.get(f"/api/v1/wiki/pages/{pid}/revisions").json()
    assert [r["revision_number"] for r in revs] == [3, 2, 1]
    assert revs[1]["change_note"] == "수정"
    assert client.get(f"/api/v1/wiki/pages/{pid}/revisions/1").json()["content"] == "v1"

    restored = client.post(f"/api/v1/wiki/pages/{pid}/revisions/1/restore", json={"expected_revision": 3}).json()
    assert restored["current_revision"] == 4
    assert restored["content"] == "v1" and restored["title"] == "창 물리"


def test_stale_editor_gets_conflict_instead_of_overwriting(client):
    pid = make_page(client, "A", "one")["page_id"]
    client.patch(f"/api/v1/wiki/pages/{pid}", json={"expected_revision": 1, "content": "two"})
    r = client.patch(f"/api/v1/wiki/pages/{pid}", json={"expected_revision": 1, "content": "stale"})
    assert r.status_code == 409
    assert r.json()["error"]["details"]["current_revision"] == 2
    assert client.get(f"/api/v1/wiki/pages/{pid}").json()["content"] == "two"


def test_unchanged_save_does_not_create_revision_and_tag_only_change(client):
    pid = make_page(client, "A", "same", tags=["x"])["page_id"]
    r = client.patch(f"/api/v1/wiki/pages/{pid}", json={"expected_revision": 1, "content": "same"})
    assert r.json()["current_revision"] == 1
    r = client.patch(f"/api/v1/wiki/pages/{pid}", json={"expected_revision": 1, "tags": ["y", "x"]})
    assert r.json()["current_revision"] == 1
    assert r.json()["tags"] == ["x", "y"]


def test_trash_restore_and_purge(client, conn):
    pid = make_page(client, "지울 문서", "삭제 테스트 내용입니다")["page_id"]
    assert client.get("/api/v1/search", params={"q": "삭제 테스트"}).json()["items"]

    # permanent delete is refused while the page is not in the trash
    assert client.delete(f"/api/v1/wiki/pages/{pid}", params={"permanent": "true"}).status_code == 409

    trashed = client.delete(f"/api/v1/wiki/pages/{pid}").json()
    assert trashed["status"] == "deleted"
    assert client.get("/api/v1/wiki/pages").json()["total"] == 0
    assert client.get("/api/v1/wiki/pages", params={"status": "deleted"}).json()["total"] == 1
    assert client.get("/api/v1/search", params={"q": "삭제 테스트"}).json()["items"] == []
    assert conn.execute("SELECT count(*) FROM wiki_chunks WHERE page_id=?", (pid,)).fetchone()[0] == 0
    r = client.patch(f"/api/v1/wiki/pages/{pid}", json={"expected_revision": 1, "content": "x"})
    assert r.status_code == 409

    client.post(f"/api/v1/wiki/pages/{pid}/restore")
    assert client.get("/api/v1/search", params={"q": "삭제 테스트"}).json()["items"]

    client.delete(f"/api/v1/wiki/pages/{pid}")
    assert client.delete(f"/api/v1/wiki/pages/{pid}", params={"permanent": "true"}).status_code == 204
    assert client.get(f"/api/v1/wiki/pages/{pid}").status_code == 404
    for table, col in (("wiki_revisions", "page_id"), ("wiki_chunks", "page_id"),
                       ("entity_tags", "entity_id"), ("timeline_events", "source_id")):
        assert conn.execute(f"SELECT count(*) FROM {table} WHERE {col}=?", (pid,)).fetchone()[0] == 0
    assert conn.execute("SELECT count(*) FROM search_index WHERE entity_id=?", (pid,)).fetchone()[0] == 0


def test_resolve_wiki_link_title(client):
    make_page(client, "Spear Physics", "x")
    page = make_page(client, "링크 문서", "참고: [[spear physics]] 와 [[없는 문서]]")
    assert page["links"] == ["spear physics", "없는 문서"]
    assert client.get("/api/v1/wiki/resolve", params={"title": "spear physics"}).json()["title"] == "Spear Physics"
    assert client.get("/api/v1/wiki/resolve", params={"title": "없는 문서"}).status_code == 404


def test_import_markdown_txt_and_cp949(client):
    md = "# 캐릭터 조작 설계\n\n이동과 점프".encode("utf-8")
    r = client.post("/api/v1/wiki/import", files={"file": ("controls.md", md)}, data={"folder": "게임", "tags": "가져옴, 설계"})
    assert r.status_code == 201, r.text
    page = r.json()
    assert page["title"] == "캐릭터 조작 설계"
    assert page["source_type"] == "import_file" and page["source_ref"] == "controls.md"
    assert page["tags"] == ["가져옴", "설계"]

    r = client.post("/api/v1/wiki/import", files={"file": ("메모.txt", "윈도우 메모장 파일".encode("cp949"))})
    assert r.status_code == 201
    assert r.json()["title"] == "메모" and r.json()["content"] == "윈도우 메모장 파일"


def test_import_rejects_unsupported_binary_and_oversized(client, settings):
    r = client.post("/api/v1/wiki/import", files={"file": ("a.pdf", b"%PDF-1.4")})
    assert r.status_code == 415 and "PDF" in r.json()["error"]["message"]
    assert client.post("/api/v1/wiki/import", files={"file": ("a.exe", b"MZ")}).status_code == 415
    assert client.post("/api/v1/wiki/import", files={"file": ("a.txt", b"ab\x00cd")}).status_code == 415
    big = b"a" * (settings.max_import_bytes + 1)
    assert client.post("/api/v1/wiki/import", files={"file": ("big.txt", big)}).status_code == 413
    assert client.get("/api/v1/wiki/pages").json()["total"] == 0


def test_timeline_records_wiki_events_and_coalesces_edits(client):
    pid = make_page(client, "타임라인 문서", "a")["page_id"]
    for i in range(1, 4):
        client.patch(f"/api/v1/wiki/pages/{pid}", json={"expected_revision": i, "content": f"edit {i}"})
    client.delete(f"/api/v1/wiki/pages/{pid}")

    events = client.get("/api/v1/timeline/events").json()["items"]
    types = [e["event_type"] for e in events]
    assert types == ["wiki_page_deleted", "wiki_page_updated", "wiki_page_created"]
    updated = events[1]
    assert updated["metadata"]["edit_count"] == 3 and updated["metadata"]["revision"] == 4
    assert all(e["source_id"] == pid for e in events)


def test_import_decodes_rfc2047_filenames_sent_by_dotnet(client):
    from app.services.file_import_service import clean_filename

    assert clean_filename("=?utf-8?B?66mU66qoLnR4dA==?=") == "메모.txt"
    assert clean_filename("C:\\Users\\me\\노트.md") == "노트.md"
    r = client.post("/api/v1/wiki/import", files={"file": ("=?utf-8?B?66mU66qoLnR4dA==?=", "내용".encode())})
    assert r.status_code == 201, r.text
    assert r.json()["title"] == "메모" and r.json()["source_ref"] == "메모.txt"
