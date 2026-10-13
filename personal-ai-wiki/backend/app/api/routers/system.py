from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app import __version__
from app.ai.llm_provider import LLMProvider, model_available
from app.api.deps import AppSettingsDep, Conn, get_provider, settings_service, wiki_service
from app.db.backup import backup_database
from app.repositories import chat_repo, search_repo, timeline_repo, wiki_repo
from app.schemas.system import (
    AppSettings,
    AppSettingsUpdate,
    BackupResult,
    Health,
    LLMStatus,
    ReindexResult,
    SystemStatus,
)
from app.services.settings_service import SettingsService
from app.services.wiki_service import WikiService

public_router = APIRouter(prefix="/api/v1", tags=["system"])
router = APIRouter(prefix="/api/v1", tags=["system"])

LIGHT_MODELS = ["gemma3:4b", "exaone3.5:2.4b", "qwen2.5:3b"]


@public_router.get("/health", response_model=Health)
def health(request: Request):
    """Unauthenticated liveness probe; reveals nothing about stored data."""
    return Health(status="ok", app="personal-ai-wiki", version=__version__, schema_version=request.app.state.schema_version)


@router.get("/system/status", response_model=SystemStatus)
def system_status(request: Request, conn: Conn, settings: AppSettingsDep):
    return SystemStatus(
        version=__version__,
        data_dir=str(settings.data_dir),
        db_path=str(settings.db_path),
        schema_version=request.app.state.schema_version,
        fts_tokenizer=search_repo.tokenizer(conn),
        page_count=wiki_repo.count_pages(conn, "active"),
        deleted_page_count=wiki_repo.count_pages(conn, "deleted"),
        chat_session_count=chat_repo.count_sessions(conn),
        timeline_event_count=timeline_repo.count(conn),
        external_network_allowed=settings.allow_external_network,
    )


@router.get("/system/llm", response_model=LLMStatus)
def llm_status(
    provider: Annotated[LLMProvider, Depends(get_provider)],
    app_settings: Annotated[SettingsService, Depends(settings_service)],
):
    model = app_settings.get().llm_model
    st = provider.status()
    available = st.reachable and model_available(model, st.models)
    return LLMStatus(
        provider=st.provider,
        base_url=st.base_url,
        reachable=st.reachable,
        version=st.version,
        configured_model=model,
        model_available=available,
        models=st.models,
        error=st.error,
        guidance=llm_guidance(st.reachable, available, model, st.models),
    )


def llm_guidance(reachable: bool, available: bool, model: str, installed: list[str]) -> list[str]:
    if not reachable:
        return [
            "Ollama가 실행되고 있지 않거나 설치되어 있지 않습니다.",
            "1) https://ollama.com/download 에서 Windows용 Ollama를 설치하세요.",
            "2) 설치 후 Ollama 앱을 실행하세요 (또는 터미널에서 'ollama serve').",
            f"3) 터미널에서 'ollama pull {model}' 으로 모델을 내려받으세요.",
            "4) 이 화면에서 '다시 확인'을 누르세요.",
        ]
    if not available:
        tips = [
            f"설정된 모델 '{model}'이(가) 설치되어 있지 않습니다.",
            f"터미널에서 'ollama pull {model}' 을 실행하거나, 아래 목록에서 설치된 모델을 선택하세요.",
            "그래픽카드 없는 16GB PC 권장 모델: " + ", ".join(LIGHT_MODELS),
        ]
        if installed:
            tips.append("설치된 모델: " + ", ".join(installed))
        return tips
    return []


@router.get("/settings", response_model=AppSettings)
def get_app_settings(svc: Annotated[SettingsService, Depends(settings_service)]):
    return svc.get()


@router.patch("/settings", response_model=AppSettings)
def update_app_settings(body: AppSettingsUpdate, svc: Annotated[SettingsService, Depends(settings_service)]):
    return svc.update(body)


@router.post("/system/backup", response_model=BackupResult)
def backup(conn: Conn, settings: AppSettingsDep):
    path = backup_database(conn, settings.backups_dir, label="manual")
    return BackupResult(path=str(path), size_bytes=path.stat().st_size)


@router.post("/system/reindex", response_model=ReindexResult)
def reindex(wiki: Annotated[WikiService, Depends(wiki_service)]):
    """Rebuild chunks and the search index from page content (safe: derived data only)."""
    return ReindexResult(pages_indexed=wiki.reindex_all())


@router.post("/system/shutdown", status_code=202)
def shutdown(request: Request):
    """Graceful stop, used by the desktop app when it started the backend itself."""
    server = getattr(request.app.state, "server", None)
    if server is not None:
        server.should_exit = True
    return {"status": "shutting_down" if server is not None else "not_managed"}
