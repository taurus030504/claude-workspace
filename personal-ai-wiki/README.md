# Personal AI Wiki & Memory

쌓일수록 더 쓸모 있어지는 **개인 AI 작업 공간**입니다. 내 위키 문서와 기록을 로컬 LLM(Ollama)이 근거로 삼아 답하는 Windows 데스크톱 앱으로, 모든 데이터는 이 PC에만 저장됩니다.

- 데스크톱: C# WPF (.NET 10, Fluent 다크 테마)
- 백엔드: Python FastAPI + SQLite (FTS5 trigram 한국어 검색)
- AI: Ollama 로컬 모델 (GPU 없이 CPU에서 동작하는 경량 모델)

설계 문서: [아키텍처](docs/ARCHITECTURE.md) · [데이터베이스](docs/DATABASE.md) · [API](docs/API.md)

## 현재 상태: Phase 0 (기반)

| 기능 | 상태 |
|---|---|
| 위키 문서 작성·수정·삭제, 폴더, 태그 | ✅ 구현·테스트 |
| Markdown 편집기 + 미리보기 (편집/분할/미리보기), `[[문서 링크]]` | ✅ 구현 (렌더링은 Windows에서 직접 확인 필요*) |
| 리비전 기록, 리비전 보기·복원, 동시 편집 충돌 감지 | ✅ |
| 휴지통 → 복원 / 영구 삭제 (검색 색인·파생 데이터까지 제거) | ✅ |
| .md / .txt 파일 가져오기 (UTF-8, CP949) | ✅ |
| 한국어 전문 검색 (조사 제거, 2글자 단어, 하이라이트, 제목·출처·본문 구절 표시) | ✅ |
| AI 채팅 (Ollama, 스트리밍, 위키 근거 검색, 출처 표시, 중지) | ✅ (모의 LLM으로 테스트, 실제 Ollama는 아래 참고) |
| Ollama/모델이 없을 때 설치 안내 | ✅ |
| 타임라인 이벤트 기록 (문서 생성·수정·삭제·복원) | ✅ 수집 중 (화면은 Phase 4) |
| 백업 (앱 안에서), 복원 (스크립트), 마이그레이션 전 자동 백업 | ✅ |
| AI 메모리, 프로젝트, 대화 가져오기, 타임라인 화면, 지식 그래프 | ⏳ Phase 1~5 (앱에 "구현 예정" 화면으로 표시) |
| PDF 가져오기, AI 문서 요약, 임베딩 검색 | ⏳ 이후 단계 |

\* 개발 환경이 Linux라 WPF 앱은 **빌드까지만 검증**했고 실제 화면 실행은 하지 못했습니다. 뷰모델·API·백엔드 연동은 자동 테스트로 검증했습니다. 자세한 내용은 [검증 결과](#검증-결과)를 보세요.

## 요구 사항

- Windows 10 / 11, RAM 16GB (GPU 불필요)
- [Python 3.11 이상](https://www.python.org/downloads/) (설치 시 "Add python.exe to PATH" 체크)
- [.NET 10 SDK](https://dotnet.microsoft.com/download/dotnet/10.0)
- [Ollama](https://ollama.com/download) — AI 채팅에만 필요. 위키·검색은 Ollama 없이도 동작합니다.

## 설치

PowerShell에서 저장소의 `personal-ai-wiki` 폴더로 이동한 뒤:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
# 모델까지 한 번에 받으려면:
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1 -PullModel gemma3:4b
```

`setup.ps1`이 하는 일: Python 버전·FTS5 trigram 지원 확인 → `backend\.venv` 생성 및 패키지 설치 → .NET 10 SDK 확인 → 데스크톱 앱 빌드(Release) → Ollama 설치 여부 확인.

### 로컬 모델 고르기 (CPU 전용 16GB 기준)

| 모델 | 크기(Q4) | 특징 |
|---|---|---|
| `gemma3:4b` (기본) | 약 3.3GB | 다국어 품질과 속도의 균형 |
| `exaone3.5:2.4b` | 약 1.6GB | 한국어 특화, 가장 가벼움 |
| `qwen2.5:3b` | 약 1.9GB | 가볍고 빠름 |

```powershell
ollama pull gemma3:4b
```
앱의 **설정 → 로컬 LLM**에서 설치된 모델을 고를 수 있습니다. 7B 이상 모델은 CPU에서 답변이 매우 느릴 수 있습니다.

## 실행

```powershell
scripts\run-desktop.ps1
```

데스크톱 앱이 백엔드가 실행 중인지 확인하고, 없으면 `backend\.venv`의 Python으로 **숨김 프로세스로 자동 시작**합니다. 앱을 닫으면 앱이 시작한 백엔드도 정상 종료됩니다.

백엔드만 따로 실행하려면 (다른 프로그램에서 API 사용, 개발용):
```powershell
scripts\run-backend.ps1          # http://127.0.0.1:8765, API 문서: /docs
scripts\run-backend.ps1 -Mock    # Ollama 없이 "[모의 응답]"으로 동작 확인
```

### 단축키
`Ctrl+N` 새 문서 · `Ctrl+S` 저장 · `Ctrl+F` 전체 검색 · 채팅 입력에서 `Enter` 보내기 / `Shift+Enter` 줄바꿈

## 데이터 저장 위치

| 경로 | 내용 |
|---|---|
| `%LOCALAPPDATA%\PersonalAIWiki\data\paw.db` | SQLite 데이터베이스 (문서, 리비전, 대화, 이벤트, 설정) |
| `%LOCALAPPDATA%\PersonalAIWiki\backups\` | 수동 백업, 마이그레이션 전 자동 백업 |
| `%LOCALAPPDATA%\PersonalAIWiki\logs\` | `backend.log`, `desktop.log` (대화 내용은 기록하지 않음) |
| `%LOCALAPPDATA%\PersonalAIWiki\api_token` | 로컬 API 토큰 (자동 생성) |
| `%LOCALAPPDATA%\PersonalAIWiki\attachments\` | 첨부 파일 (이후 단계) |

데이터 폴더를 바꾸려면 백엔드에 `PAW_DATA_DIR`, 데스크톱 `appsettings.json`의 `Backend:DataDir`을 **같은 값**으로 설정하세요.

### 백업과 복원
- 백업: 앱의 **설정 → 지금 백업** (실행 중에도 일관된 복사본 생성 후 무결성 검사)
- 복원: 앱을 닫고
  ```powershell
  scripts\restore-backup.ps1 -List
  scripts\restore-backup.ps1 "%LOCALAPPDATA%\PersonalAIWiki\backups\paw-manual-....db"
  ```
  현재 DB는 삭제되지 않고 `paw.before-restore-<시각>.db`로 옆에 보관됩니다.

## 설정

### 백엔드 (환경 변수 또는 `backend\.env`)
| 변수 | 기본값 | 설명 |
|---|---|---|
| `PAW_DATA_DIR` | `%LOCALAPPDATA%\PersonalAIWiki` | 데이터 폴더 |
| `PAW_HOST` / `PAW_PORT` | `127.0.0.1` / `8765` | 루프백이 아닌 주소는 `PAW_ALLOW_REMOTE_BIND=true` 없이는 시작 거부 |
| `PAW_LLM_PROVIDER` | `ollama` | `mock`이면 Ollama 없이 모의 응답 |
| `PAW_OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | 다른 PC의 Ollama는 `PAW_ALLOW_EXTERNAL_NETWORK=true` 필요 |
| `PAW_OLLAMA_MODEL` | `gemma3:4b` | 기본 모델 (앱 설정 화면 값이 우선) |
| `PAW_OLLAMA_NUM_CTX` | `4096` | 모델 컨텍스트 길이 (클수록 RAM 사용 증가) |
| `PAW_RETRIEVAL_TOP_K` / `PAW_MAX_CONTEXT_CHARS` | `6` / `6000` | 답변에 넣는 위키 구절 수와 총 글자 수 |
| `PAW_MAX_IMPORT_BYTES` | 5MB | 가져오기 파일 최대 크기 |

### 데스크톱 (`desktop\src\PersonalAIWiki.Desktop\appsettings.json`, 빌드 출력 폴더로 복사됨)
`Backend:BaseUrl`, `AutoStart`, `BackendDirectory`, `PythonExecutable`, `DataDir`, `StartupTimeoutSeconds`, `Environment`(자동 시작하는 백엔드에 넘길 `PAW_*` 변수). 빈 값은 자동 탐지입니다.

## 테스트

```powershell
scripts\test.ps1               # 백엔드 pytest + 데스크톱 xUnit (실제 백엔드와의 계약 테스트 포함)
scripts\test.ps1 -Ollama       # + 실제 Ollama 연동 테스트 (Ollama 실행, gemma3:4b 설치 필요)
scripts\test.ps1 -Ollama -Model exaone3.5:2.4b
```

- **모의(mock) 테스트**와 **실제 Ollama 테스트**는 분리되어 있습니다. 기본 실행은 결정적인 `MockProvider`와 가짜 Ollama HTTP 서버를 쓰며, `-Ollama`를 줄 때만 실제 모델에 질문합니다.
- 데스크톱 계약 테스트는 `BackendLauncher`로 실제 Python 백엔드(모의 LLM)를 띄워 C# 클라이언트·뷰모델을 검증합니다. 가상환경이 없으면 "통과"가 아니라 **건너뜀**으로 표시됩니다.

## 검증 결과

Phase 0을 Linux 개발 환경(Python 3.13, SQLite 3.45, .NET SDK 10.0.401)에서 검증했습니다.

| 항목 | 결과 |
|---|---|
| 백엔드 pytest | 72 통과, 2 건너뜀 (실제 Ollama 테스트: 이 환경에서 Ollama 다운로드가 차단됨) |
| 데스크톱 xUnit (단위 + 실제 백엔드 계약 테스트) | 24 통과 |
| 백엔드 실서버 (uvicorn + curl) | 토큰 401, Host 헤더 차단 400, 한국어 검색, Ollama 미설치 시 503 + 안내, 정상 종료 확인 |
| WPF 앱 | Release/Debug 빌드 경고·오류 0 (XAML 컴파일 포함). **화면 실행은 미검증** — Windows에서 첫 실행 시 확인 필요 |
| PowerShell 스크립트 | PowerShell 파서로 구문 검사 통과, Windows PowerShell 5.1용 UTF-8 BOM. **실제 Windows 실행은 미검증** |

Windows에서 처음 실행할 때 확인할 것: 앱 시작 시 백엔드 자동 시작, 문서 작성·저장·미리보기, 검색, Ollama 설치 후 채팅 스트리밍, 오른쪽 패널 접기, 앱 종료 시 백엔드 종료.

## 문제 해결

| 증상 | 해결 |
|---|---|
| "Python 가상환경이 없습니다" | `scripts\setup.ps1` 실행 |
| "백엔드가 시작 직후 종료되었습니다" | `%LOCALAPPDATA%\PersonalAIWiki\logs\backend.log` 확인. 포트 8765를 다른 프로그램이 쓰면 `PAW_PORT`와 `appsettings.json`의 `BaseUrl`을 함께 변경 |
| "Ollama에 연결할 수 없습니다" | Ollama 앱 실행 (작업 표시줄 아이콘) 또는 `ollama serve` |
| "모델 'x'이(가) 설치되어 있지 않습니다" | `ollama pull x` 또는 설정 화면에서 설치된 모델 선택 |
| 답변이 매우 느림 | 더 작은 모델(`exaone3.5:2.4b`), `PAW_OLLAMA_NUM_CTX=2048` |
| "migration … was modified" / "newer version" | 데이터 보호를 위한 시작 거부입니다. 앱을 최신 버전으로 맞추고, 필요하면 `backups`의 백업으로 복원 |
| 검색이 안 됨 | 설정 → **검색 색인 다시 만들기** (원본 데이터는 변경되지 않음) |
