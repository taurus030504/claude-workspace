# 데이터베이스 설계

파일: `%LOCALAPPDATA%\PersonalAIWiki\data\paw.db` (SQLite 3.40+, WAL)

## 공통 규칙

- **ID**: 모든 엔터티는 UUID4 문자열 (`TEXT PRIMARY KEY`).
- **시각**: UTC ISO-8601, 밀리초, `Z` 접미사 (`2026-10-13T12:35:13.430Z`). 고정 형식이라 문자열 정렬 = 시간 정렬. 화면에서만 현지 시각으로 변환.
- **실제 시각 vs 기록 시각**: 가져온 과거 자료는 `occurred_at`/`started_at`/`created_at`에 원래 시각을, `recorded_at`/`created_at(세션)`에 저장 시각을 둔다.
- **다형 참조**: 여러 종류를 가리키는 컬럼은 `(entity_type, entity_id)` 쌍이며 FK가 없다. 참조 대상이 영구 삭제될 때 서비스 계층이 정리한다 (아래 삭제 정책).
- **CHECK 제약**은 바뀌지 않을 값(상태 등)에만 둔다. 앞으로 늘어날 종류(`entity_type`, `source_type`, `event_type`)는 코드에서 검증해, 새 종류를 추가할 때 테이블 재생성이 필요 없게 했다.
- **연결 설정**: `foreign_keys=ON`, `journal_mode=WAL`, `synchronous=FULL`, `busy_timeout=10000`. 모든 쓰기는 `BEGIN IMMEDIATE … COMMIT`.

## 마이그레이션 정책

- `backend/app/db/migrations/NNNN_name.sql`, 순서대로 각각 한 트랜잭션에서 적용. 적용 기록: `schema_migrations(version, name, checksum, applied_at)`.
- 적용된 파일이 수정되면(체크섬 불일치) 시작을 거부한다.
- DB가 앱보다 새 버전이면(모르는 번호) 시작을 거부한다 — 구버전 앱이 데이터를 망가뜨리지 않도록.
- 데이터가 있는 DB에 새 마이그레이션을 적용하기 전에 검증된 백업(`backups/paw-pre-migration-NNNN-*.db`)을 만든다.
- `-- paw:destructive` 표시가 있는 마이그레이션은 자동 실행하지 않는다. `python -m app.tools.migrate --allow-destructive`로만 실행.
- 실패한 마이그레이션은 롤백되고 기록되지 않는다.

## Phase 0 테이블 (구현됨 — `0001_initial.sql`)

### wiki_pages — 문서의 현재 상태
| 컬럼 | 타입 | 설명 |
|---|---|---|
| page_id | TEXT PK | UUID |
| title | TEXT | 제목 (NFC 정규화) |
| folder | TEXT | `게임/설계` 형태 경로, 루트는 `''` |
| content | TEXT | Markdown 본문 (NFC, LF) |
| summary | TEXT NULL | AI 요약 (이후 단계) |
| source_type | TEXT | `user` / `import_file` / `import_chat` / `ai_draft` |
| source_ref | TEXT NULL | 원본 파일명 등 |
| current_revision | INTEGER | 낙관적 동시성 제어용 |
| status | TEXT | `active` / `deleted`(휴지통) |
| created_at, updated_at, deleted_at | TEXT | UTC |

인덱스: `(status, updated_at DESC)`, `folder`, `title COLLATE NOCASE`.

### wiki_revisions — 모든 저장의 전체 스냅샷
`revision_id PK`, `page_id → wiki_pages ON DELETE CASCADE`, `revision_number`, `title`, `folder`, `content`, `content_hash(SHA-256)`, `change_note`, `author(user|ai|import|system)`, `created_at`. `UNIQUE(page_id, revision_number)`.
내용이 바뀌지 않은 저장은 리비전을 만들지 않는다. 태그만 바뀐 경우도 리비전 없음(태그는 메타데이터).

### wiki_chunks — 검색·RAG 단위
`chunk_id PK`, `page_id → CASCADE`, `revision_number`, `chunk_index`, `heading`(제목 경로, 예: `캐릭터 > 조작`), `content`, `char_start`, `char_end`(본문 내 위치), `content_hash`. 제목 단위로 나누고 900자 초과 시 문단·줄·문장 경계에서 분할. 코드 블록 안의 `#`은 제목으로 보지 않음. Phase 6 임베딩은 `chunk_id`를 키로 저장한다.

### search_index — 통합 전문 검색 (FTS5 가상 테이블)
`title`, `body`(색인됨) + `entity_type`, `entity_id`, `chunk_id`(색인 안 됨). 토크나이저는 `trigram`(미지원 SQLite면 `unicode61`로 대체하고 검색은 부분 문자열 방식으로 동작). 원본과 같은 트랜잭션에서 갱신되며, 시작 시 개수 불일치를 발견하면 자동 재생성한다. 이후 메모리·대화도 `entity_type`만 달리해 같은 테이블에 들어간다.

### tags / entity_tags
`tags(tag_id PK, name UNIQUE COLLATE NOCASE, created_at)`, `entity_tags(tag_id → CASCADE, entity_type, entity_id, created_at, PK(tag_id, entity_type, entity_id))`. 위키·메모리·프로젝트·작업·대화 공용.

### chat_sessions / chat_messages
- `chat_sessions`: `session_id PK`, `title`, `origin(app|import)`, `source_service`, `external_id`, `content_hash`, `model`, `started_at`(실제 대화 시각), `created_at`(기록 시각), `updated_at`, `archived`. `UNIQUE(source_service, external_id) WHERE external_id IS NOT NULL` — Phase 3 중복 가져오기 방지.
- `chat_messages`: `message_id PK`, `session_id → CASCADE`, `seq`, `role(user|assistant|system)`, `content`, `model`, `status(complete|partial|error)`, `external_id`, `created_at`, `recorded_at`, `metadata(JSON)`. `UNIQUE(session_id, seq)`. 오류·중단 답변은 이후 대화 맥락에 넣지 않는다.

### source_references — 출처·근거 기록
`reference_id PK`, `owner_type/owner_id`(근거를 가진 쪽: chat_message, 이후 memory 등), `source_type/source_id`(근거: wiki_page, chat_message, memory, file), `relation(cited|context|extracted_from|derived_from)`, `quote`(당시 인용문), `locator(JSON: chunk_id, revision, char_start, char_end, heading, title, number)`, `rank`, `created_at`.
청크 ID는 문서 수정 시 바뀌므로 근거는 `wiki_page` + 위치 정보로 저장한다.

### timeline_events
`event_id PK`, `event_type`, `title`, `description`, `occurred_at`, `recorded_at`, `source_type`, `source_id`, `project_id`, `importance(0~2)`, `metadata(JSON)`.
인덱스: `occurred_at`, `(event_type, occurred_at)`, `(project_id, occurred_at)`, `(source_type, source_id)`.
Phase 0에서 기록: `wiki_page_created / updated / deleted / restored`. 예약: `memory_created/updated`, `project_created`, `project_status_changed`, `task_completed`, `decision_recorded`, `conversation_imported`.

### app_settings
`key PK`, `value(JSON)`, `updated_at`. UI에서 바꾼 설정(모델명, 검색 소스 ON/OFF). 환경 변수 기본값을 덮어쓴다.

## 삭제 정책

| 동작 | 결과 |
|---|---|
| 문서 휴지통 이동 | `status='deleted'`, 청크·검색 색인 제거, 리비전·태그 유지, 복원 가능 |
| 문서 복원 | `status='active'`, 청크·색인 재생성 |
| 문서 영구 삭제 (휴지통에 있을 때만) | 문서·리비전·청크(CASCADE), 태그 연결, 이 문서를 근거로 한 `source_references`, 이 문서의 타임라인 이벤트 삭제 |
| 대화 삭제 | 메시지(CASCADE)와 메시지가 가진 `source_references` 삭제 |

## 이후 단계 테이블 설계 (아직 생성하지 않음)

> 각 단계 시작 시 별도 마이그레이션으로 추가한다. 구현하면서 정규화를 개선할 수 있다.

**Phase 1 — `memory_items`**: `memory_id PK`, `memory_type`(UserProfile, Preferences, Goals, Projects, Decisions, Experiences, ConversationSummary), `title`, `content`, `related_entity_type`, `related_entity_id`, `source_type`, `source_id`, `provenance`(`user_statement` / `document_verified` / `ai_inference`), `confidence REAL`, `status`(`candidate` / `approved` / `rejected` / `outdated`), `is_sensitive INTEGER`, `sensitive_consent_at`, `supersedes_id → memory_items`, `created_at`, `updated_at`, `last_confirmed_at`.
**`memory_revisions`**: `memory_id → CASCADE`, `revision_number`, 이전 값 스냅샷, `changed_by`, `created_at`.
정책: AI가 만든 항목은 항상 `candidate`로 시작하고 사용자 승인 후에만 `approved`가 된다. 근거는 `source_references(owner_type='memory')`.

**Phase 2 — `projects`**(`project_id`, `name`, `description`, `goals`, `status`, `start_date`, `target_date`, `progress_mode`(count|weighted), timestamps), **`project_tasks`**(`task_id`, `project_id → CASCADE`, `parent_task_id`(하위 작업), `title`, `description`, `status`(todo|in_progress|blocked|done), `priority`(low|medium|high), `due_date`, `weight REAL DEFAULT 1`, `completed_at`, timestamps), **`task_dependencies`**(`task_id`, `depends_on_task_id`, 순환 검사는 서비스에서), **`project_milestones`**(`milestone_id`, `project_id`, `title`, `due_date`, `completed_at`), **`project_links`**(`project_id`, `entity_type`, `entity_id`, `created_at`) — 프로젝트↔위키·메모리·대화 다대다.

**Phase 3 — `import_sources`**(`source_id`, `file_name`, `file_sha256 UNIQUE`, `format`, `size_bytes`, `stored_path`(원본 보존), `imported_at`), **`import_jobs`**(`job_id`, `source_id`, `status`(pending|running|cancelled|done|failed), `total`, `processed`, `error`, `selected_ids JSON`, timestamps). 대화는 기존 `chat_sessions(origin='import')`에 저장.

**Phase 3 이후 — `attachments`**(`attachment_id`, `entity_type`, `entity_id`, `file_name`, `stored_path`(attachments 폴더 기준 상대 경로), `mime_type`, `size_bytes`, `sha256`, `created_at`).

**Phase 5 — `knowledge_edges`**: `edge_id PK`, `from_type`, `from_id`, `to_type`, `to_id`, `relation`(related_to, belongs_to, supports, depends_on, decided_in, supersedes), `origin`(user|ai|system), `status`(confirmed|suggested|rejected), `confidence`, `evidence_reference_id`, `created_at`; `UNIQUE(from_type, from_id, to_type, to_id, relation)`, 양방향 조회 인덱스.

**Phase 6 — `chunk_embeddings`**: `chunk_id → wiki_chunks CASCADE`, `model`, `dim`, `vector BLOB`(float32), `content_hash`(재계산 필요 여부 판단). 메모리용 `memory_embeddings` 동일 구조.
