# 아키텍처 (Phase 0 기준)

## 1. 전체 구조

```
┌──────────────────────── Desktop (C# WPF, .NET 10) ────────────────────────┐
│ Views (XAML)  ─ 위키 편집기 · AI 채팅 · 대시보드 · 검색 · 설정 · (예정 화면)  │
│      │ 데이터 바인딩                                                        │
│ PersonalAIWiki.Core (net10.0, OS 독립)                                     │
│   ViewModels ─ MainViewModel / WikiViewModel / ChatViewModel / …           │
│   Api        ─ IPawApi / PawApiClient (HTTP + NDJSON 스트리밍)              │
│   Backend    ─ BackendLauncher (백엔드 자동 시작·종료, 토큰 읽기)            │
└───────────────────────────────┬────────────────────────────────────────────┘
                                │ HTTP, 127.0.0.1:8765, X-PAW-Token
┌──────────────────────── Backend (Python FastAPI) ─────────────────────────┐
│ api/routers  ─ wiki · search · chat · timeline · system                    │
│ services     ─ WikiService · SearchService · ChatService · TimelineService │
│                SettingsService · FileImportService                         │
│ ai           ─ LLMProvider(인터페이스) · OllamaProvider · MockProvider       │
│                Retriever · ContextBuilder · prompts                        │
│ repositories ─ 테이블별 SQL                                                 │
│ db           ─ connection(트랜잭션) · migrator · backup                    │
└───────────────────────────────┬────────────────────────────────────────────┘
               ┌────────────────┴───────────────┐
        SQLite (WAL, FTS5 trigram)         Ollama (127.0.0.1:11434)
        %LOCALAPPDATA%\PersonalAIWiki
```

### 계층 규칙
- **UI는 DB를 직접 건드리지 않는다.** 모든 데이터 접근은 REST API를 거친다 (`IPawApi`).
- **서비스 계층만 트랜잭션을 연다.** 원본 행, 리비전, 청크, 검색 색인, 타임라인 이벤트가 한 트랜잭션에서 함께 커밋되므로 색인과 원본이 어긋나지 않는다.
- **AI 계층은 인터페이스(`LLMProvider`)에만 의존한다.** Ollama 외 모델로 교체할 때 `chat_stream()`과 `status()`만 구현하면 된다.
- **뷰모델은 WPF에 의존하지 않는다** (`PersonalAIWiki.Core`는 `net10.0`). 그래서 리눅스 CI에서도 단위 테스트와 실제 백엔드 연동 테스트를 돌릴 수 있다.

## 2. 기술 스택 검토

| 영역 | 선택 | 이유 / 검토한 대안 |
|---|---|---|
| UI | WPF, **.NET 10 (LTS)**, 내장 Fluent 다크 테마 (`ThemeMode="Dark"`) | 서드파티 테마 라이브러리(ModernWpf: 유지보수 중단, WPF-UI: 의존성 증가) 없이 다크 모드 제공. .NET 8은 2026-11 지원 종료. |
| MVVM | CommunityToolkit.Mvvm 8.4 | 소스 생성기로 보일러플레이트 최소화, 마이크로소프트 공식. |
| Markdown | Markdig 0.41 + **자체 FlowDocument 렌더러** | Markdig.Wpf는 원격 이미지를 내려받아 "동의 없는 외부 전송 금지" 원칙과 충돌하고 HTML 처리 제어가 어렵다. 자체 렌더러는 HTML을 실행하지 않고, 이미지를 내려받지 않으며, 링크는 확인 후에만 연다. WebView2는 런타임 의존·보안 설정 부담이 커서 제외. |
| 백엔드 | FastAPI 0.115+, uvicorn, pydantic 2 | 타입 기반 검증, OpenAPI 문서 자동 생성(`/docs`), 스트리밍 응답 지원. |
| DB | SQLite (WAL, `synchronous=FULL`, FK on) | 단일 사용자 로컬 앱에 서버 불필요. 강제 종료 시에도 트랜잭션 단위 원자성. |
| 텍스트 검색 | **FTS5 trigram** + 짧은 단어용 부분 문자열 검색 | 한국어는 조사가 붙어 `unicode61` 토크나이저로는 "프로젝트를"과 "프로젝트"가 매칭되지 않는다. trigram은 부분 문자열 매칭이 되지만 3글자 미만은 못 찾으므로 2글자 단어(게임, 설계…)는 LIKE로 보완한다. |
| LLM | Ollama HTTP API, 기본 `gemma3:4b` | GPU 없는 16GB PC에서 Q4 4B 모델은 약 3GB RAM. 대안: `exaone3.5:2.4b`(한국어 특화·경량), `qwen2.5:3b`. 설정 화면에서 변경. |
| 임베딩 (Phase 6) | 후보: `bge-m3` (Ollama), `multilingual-e5-small` | CPU 호환 다국어 모델. `wiki_chunks.chunk_id`를 키로 벡터를 저장하도록 설계해 두었다. |
| HTTP 클라이언트 | httpx (백엔드→Ollama), HttpClient (데스크톱→백엔드) | 둘 다 스트리밍 지원. httpx는 `trust_env=False`로 시스템 프록시를 거치지 않는다. |
| 테스트 | pytest, xUnit v3 | xUnit v3의 `Assert.SkipWhen`으로 백엔드가 없을 때 연동 테스트를 "통과"가 아니라 "건너뜀"으로 표시. |

**의도적으로 쓰지 않은 것:** ORM(SQLAlchemy) — 테이블 수가 적고 FTS5·트랜잭션을 직접 제어하는 편이 명확하다. LangChain 등 LLM 프레임워크 — 의존성이 크고 Phase 0 기능에 필요한 것은 프롬프트 조립과 HTTP 호출뿐이다.

## 3. 디렉터리 구조

```
personal-ai-wiki/
├─ README.md                   설치·실행·설정·데이터 위치
├─ docs/                       ARCHITECTURE / DATABASE / API
├─ scripts/                    setup.ps1, run-desktop.ps1, run-backend.ps1, test.ps1, restore-backup.ps1
├─ backend/
│  ├─ requirements.txt, requirements-dev.txt, pyproject.toml
│  ├─ app/
│  │  ├─ main.py               앱 팩토리, 미들웨어, 오류 형식, `python -m app`
│  │  ├─ config.py             PAW_* 설정, 데이터 폴더, 네트워크 정책
│  │  ├─ security.py           로컬 API 토큰
│  │  ├─ core/                 ids, timeutil(UTC), errors
│  │  ├─ db/                   connection, migrator, backup, migrations/0001_initial.sql
│  │  ├─ repositories/         wiki, tag, search, chat, timeline, reference, settings
│  │  ├─ services/             wiki, search, chat, timeline, settings, file_import, markdown_tools, text_analysis
│  │  ├─ ai/                   llm_provider, ollama_provider, mock_provider, retrieval, context_builder, prompts
│  │  ├─ schemas/              API 계약 (pydantic)
│  │  ├─ api/                  deps, routers/
│  │  └─ tools/                migrate, restore (CLI)
│  └─ tests/                   pytest 74개 (그중 실제 Ollama 연동 2개는 PAW_TEST_OLLAMA=1일 때만)
└─ desktop/
   ├─ PersonalAIWiki.sln, Directory.Build.props
   ├─ src/PersonalAIWiki.Core/       Models, Api, Backend, Services(인터페이스), ViewModels
   ├─ src/PersonalAIWiki.Desktop/    App, MainWindow, Views, Controls(MarkdownViewer, Highlight), Markdown, Converters, Themes
   └─ tests/PersonalAIWiki.Core.Tests/  단위 테스트 + 실제 백엔드 계약 테스트
```

## 4. 핵심 흐름

### 문서 저장
`PATCH /wiki/pages/{id}` (expected_revision 포함) → 리비전 불일치면 409 → 일치하면 한 트랜잭션에서
`wiki_revisions` 새 스냅샷 → `wiki_pages` 갱신 → 청크 재생성 → `search_index` 교체 → 타임라인 이벤트(10분 내 연속 수정은 하나로 병합).

### AI 질문 (RAG)
```
질문 → 모델 준비 확인(없으면 503 + 설치 안내, 아무것도 저장 안 함)
     → 사용자 메시지 저장
     → 질의 분석(조사·불용어 제거) → FTS5/부분문자열 검색 → 점수화 → 문서당 최대 2청크, 상위 k개
     → 컨텍스트 조립: 시스템 프롬프트 + <sources>(데이터로 취급, 태그 무력화) + 최근 대화
     → Ollama 스트리밍 → NDJSON(start/delta/done|error)
     → 답변 저장(중단돼도 partial/error 상태로 저장) + 제공·인용된 출처를 source_references에 기록
```

### 데스크톱 시작
`BackendLauncher`: `/health` 확인 → 없으면 `backend\.venv\Scripts\python.exe -m app`을 숨김 프로세스로 시작 → 최대 45초 대기 → 데이터 폴더의 `api_token`을 읽어 클라이언트 생성. 앱 종료 시 자신이 시작한 백엔드만 `/system/shutdown`으로 정상 종료(실패 시 강제 종료).

## 5. 보안·개인정보 설계

| 요구사항 | 구현 |
|---|---|
| 로컬 저장 | `%LOCALAPPDATA%\PersonalAIWiki` (사용자 전용 폴더) |
| 외부 네트워크 기본 차단 | 백엔드는 루프백만 바인딩(`PAW_ALLOW_REMOTE_BIND` 없이는 시작 거부), Ollama 주소가 로컬이 아니면 `PAW_ALLOW_EXTERNAL_NETWORK` 없이는 시작 거부, 렌더러는 원격 이미지 로드 안 함 |
| 같은 PC의 다른 프로그램·웹페이지 차단 | 모든 API에 설치별 토큰(`X-PAW-Token`) 필요, Host 헤더 검사로 DNS rebinding 차단, CORS 미허용 |
| 가져온 파일은 신뢰하지 않음 | 크기·확장자 검사, 바이너리 거부, 실행 안 함, HTML은 텍스트로 표시 |
| 프롬프트 주입 | 검색된 문서는 `<source>` 안의 데이터로만 전달, 문서 안의 `</source>`·`<system>` 등은 무력화, 시스템 프롬프트에서 지시 무시 규칙 명시 |
| 삭제 시 파생 데이터 제거 | 휴지통 이동 시 청크·색인 제거, 영구 삭제 시 리비전·태그·인용 기록·타임라인까지 제거 |
| 데이터 손상 방지 | WAL + FULL sync, 모든 쓰기 트랜잭션, 마이그레이션 전 자동 백업, 파괴적 마이그레이션 자동 실행 금지 |
| 로그 | 메시지 본문은 로그에 남기지 않음 (메타데이터만) |

## 6. 이후 단계가 붙는 자리 (재구조화 없이)

| 단계 | 추가 위치 |
|---|---|
| Phase 1 메모리 | `0002_memory.sql`(memory_items, memory_revisions) · `services/memory_service.py` · `ai/memory_extractor.py` · `Retriever._memory()` · `search_index`에 `entity_type='memory'` · 기존 `source_references`로 출처 연결 · `EventType.MEMORY_*` |
| Phase 2 프로젝트 | `0003_projects.sql` · `project_links`(프로젝트↔위키·메모리·대화) · `Retriever._projects()` · 작업 완료 시 `TimelineService.record()` |
| Phase 3 대화 가져오기 | `chat_sessions.origin='import'`, `source_service`, `external_id`, `content_hash`(중복 방지 인덱스 이미 존재) · `ai/parsers/`(ChatGPT JSON, Markdown/TXT) · `import_jobs`(진행률·취소) · 과거 시각은 `occurred_at`으로 기록 |
| Phase 4 타임라인 | 이벤트는 Phase 0부터 수집 중. API(`/timeline/events` 필터·커서)도 존재. 화면만 추가 |
| Phase 5 그래프 | `knowledge_edges`(origin: user/ai, status: confirmed/suggested) · 노드는 기존 ID 참조 |
| Phase 6 임베딩 | `chunk_embeddings(chunk_id, model, vector)` · `Retriever`에서 키워드·벡터 결과 병합(RRF) |
