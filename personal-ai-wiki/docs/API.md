# API 명세 (v1, Phase 0)

- 주소: `http://127.0.0.1:8765` (루프백 전용)
- 실행 중 대화형 문서: `http://127.0.0.1:8765/docs` (OpenAPI)
- 인증: `/api/v1/health`를 제외한 모든 경로에 헤더 `X-PAW-Token: <토큰>` (또는 `Authorization: Bearer <토큰>`).
  토큰 파일: `%LOCALAPPDATA%\PersonalAIWiki\api_token` (백엔드가 처음 시작할 때 생성). 다른 LLM·AI 허브 연동도 이 토큰으로 접근한다.
- JSON 필드는 snake_case, 시각은 UTC ISO-8601.

## 오류 형식

```json
{ "error": { "code": "conflict", "message": "page was changed by someone else; reload before saving",
             "details": { "current_revision": 4 } } }
```

| HTTP | code | 의미 |
|---|---|---|
| 401 | unauthorized | 토큰 없음/틀림 |
| 400 | — | 허용되지 않은 Host 헤더 (DNS rebinding 차단) |
| 404 | not_found | 대상 없음 |
| 409 | conflict | 리비전 충돌, 휴지통 문서 편집, 휴지통이 아닌 문서 영구 삭제 |
| 413 | payload_too_large | 가져오기 파일 5MB 초과 |
| 415 | unsupported_format | 지원하지 않는 파일 형식 (PDF는 이후 단계) |
| 422 | validation_error | 입력 검증 실패 (`details.errors`) |
| 503 | llm_unavailable | Ollama 미실행(`details.reason=unreachable`) 또는 모델 미설치(`model_missing`) |

## 시스템

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/api/v1/health` | 인증 없음. `{status, app, version, schema_version}` |
| GET | `/api/v1/system/status` | 데이터 폴더, DB 경로, 스키마 버전, 토크나이저, 문서/대화/이벤트 수 |
| GET | `/api/v1/system/llm` | Ollama 연결·버전·설치 모델·설정 모델 사용 가능 여부·**한국어 설치 안내(guidance)** |
| GET / PATCH | `/api/v1/settings` | `llm_model`, `search_wiki`, `search_memory`, `search_projects`, `search_conversations` (현재 효과가 있는 것은 `available_search_sources`에 표시: Phase 0은 `wiki`) |
| POST | `/api/v1/system/backup` | 실행 중 일관된 백업 생성 → `{path, size_bytes}` |
| POST | `/api/v1/system/reindex` | 문서 내용으로 청크·검색 색인 재생성 |
| POST | `/api/v1/system/shutdown` | 정상 종료 (데스크톱 앱이 사용) |

## 위키

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/api/v1/wiki/pages?status=active\|deleted&folder=&tag=&limit=&offset=` | 목록(본문 제외, excerpt 포함). folder는 하위 폴더 포함 |
| POST | `/api/v1/wiki/pages` | `{title, content, folder, tags[], change_note}` → 201 Page |
| GET | `/api/v1/wiki/pages/{id}` | Page (`links`: 본문의 `[[링크]]` 대상) |
| PATCH | `/api/v1/wiki/pages/{id}` | `{expected_revision, title?, content?, folder?, tags?, change_note?}` → 변경 시 새 리비전. 리비전 불일치 409 |
| DELETE | `/api/v1/wiki/pages/{id}` | 휴지통으로 이동 → Page |
| DELETE | `/api/v1/wiki/pages/{id}?permanent=true` | 휴지통 문서 영구 삭제 → 204 |
| POST | `/api/v1/wiki/pages/{id}/restore` | 휴지통에서 복원 |
| GET | `/api/v1/wiki/pages/{id}/revisions` | 리비전 목록(최신순) |
| GET | `/api/v1/wiki/pages/{id}/revisions/{n}` | 리비전 내용 |
| POST | `/api/v1/wiki/pages/{id}/revisions/{n}/restore` | `{expected_revision}` → 그 내용으로 새 리비전 생성 |
| GET | `/api/v1/wiki/resolve?title=` | `[[링크]]` 대상 찾기 (대소문자 무시 정확히 일치) |
| GET | `/api/v1/wiki/folders` | `[{folder, page_count}]` |
| GET | `/api/v1/wiki/tags` | `[{name, usage}]` |
| POST | `/api/v1/wiki/import` | multipart: `file`(.md/.markdown/.txt, UTF-8 또는 CP949), `folder`, `tags`(쉼표 구분) → 201 Page |

Page 예시:
```json
{ "page_id": "3c9a…", "title": "중세 등반 게임", "folder": "게임", "content": "# 핵심\n창으로 벽에 고정한다",
  "tags": ["게임"], "summary": null, "source_type": "user", "source_ref": null, "current_revision": 1,
  "status": "active", "links": [], "created_at": "2026-10-13T12:38:22.900Z", "updated_at": "…", "deleted_at": null }
```

## 검색

`GET /api/v1/search?q=창 고정&types=wiki_page&limit=20&group=true`

```json
{ "query": "창 고정", "terms": ["고정"], "tokenizer": "trigram",
  "items": [ { "entity_type": "wiki_page", "entity_id": "3c9a…", "chunk_id": "405c…",
               "title": "중세 등반 게임", "heading": "핵심", "snippet": "# 핵심 창으로 벽에 고정한다",
               "highlights": [[13, 15]], "matched_terms": ["고정"], "score": 10.3 } ] }
```
`group=false`면 문서당 여러 청크(최대 2)를 돌려준다. 1글자 단어와 불용어("어떻게", "알려줘")는 무시된다.

## 채팅

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/api/v1/chat/sessions` | 세션 목록 (최근순, 메시지 수 포함) |
| POST | `/api/v1/chat/sessions` | `{title?}` → 201 |
| GET | `/api/v1/chat/sessions/{id}` | 세션 + 메시지 + 각 답변의 출처 |
| PATCH | `/api/v1/chat/sessions/{id}` | `{title}` |
| DELETE | `/api/v1/chat/sessions/{id}` | 204 |
| POST | `/api/v1/chat/sessions/{id}/messages` | `{content, stream=true, model?, use_wiki?}` |

`stream=false` → `{user_message, assistant_message}`.
`stream=true` → `application/x-ndjson`, 한 줄에 하나의 이벤트:

```
{"type":"start","user_message":{…},"sources":[{"number":1,"source_type":"wiki_page","source_id":"…","title":"창 물리","heading":"","quote":"…","cited":false}],"model":"gemma3:4b"}
{"type":"delta","text":"창은 "}
{"type":"delta","text":"벽에 고정됩니다 [1]"}
{"type":"done","assistant_message":{…,"status":"complete","sources":[{…,"cited":true}]}}
```
생성 중 오류는 `{"type":"error","code":"llm_unavailable","message":"…","assistant_message":{…,"status":"error"}}`. 모델이 아예 준비되지 않았다면 스트림 시작 전에 503을 반환하고 아무것도 저장하지 않는다. 클라이언트가 연결을 끊으면 받은 부분까지 `partial`로 저장된다.

## 타임라인

`GET /api/v1/timeline/events?start=&end=&types=a,b&project_id=&min_importance=0&cursor=&limit=50`
→ `{items: [TimelineEvent], next_cursor}` (`occurred_at` 내림차순, 커서 기반 페이지).

## 이후 단계 API (계획)

- Phase 1: `/api/v1/memory/items` CRUD, `/memory/candidates` (추출 결과), `/memory/candidates/{id}/approve|reject`, `/memory/conflicts`
- Phase 2: `/api/v1/projects`, `/projects/{id}/tasks`, `/projects/{id}/links`, `/projects/{id}/dashboard`
- Phase 3: `/api/v1/imports` (파일 분석·미리보기), `/imports/{job}/select`, `/imports/{job}/cancel`, `/imports/{job}/candidates`
- Phase 5: `/api/v1/graph/neighborhood?node=&depth=`, `/graph/edges` CRUD, `/graph/suggestions`
