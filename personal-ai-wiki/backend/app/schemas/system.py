from __future__ import annotations

from pydantic import BaseModel, Field


class Health(BaseModel):
    status: str
    app: str
    version: str
    schema_version: int


class LLMStatus(BaseModel):
    provider: str
    base_url: str
    reachable: bool
    version: str | None
    configured_model: str
    model_available: bool
    models: list[str]
    error: str | None
    guidance: list[str] = Field(description="Korean setup instructions when something is missing")


class SystemStatus(BaseModel):
    version: str
    data_dir: str
    db_path: str
    schema_version: int
    fts_tokenizer: str
    page_count: int
    deleted_page_count: int
    chat_session_count: int
    timeline_event_count: int
    external_network_allowed: bool


class BackupResult(BaseModel):
    path: str
    size_bytes: int


class ReindexResult(BaseModel):
    pages_indexed: int


class AppSettings(BaseModel):
    llm_model: str
    search_wiki: bool
    search_memory: bool
    search_projects: bool
    search_conversations: bool
    # Read-only: which search sources exist in this build (others arrive in later phases).
    available_search_sources: list[str]


class AppSettingsUpdate(BaseModel):
    llm_model: str | None = Field(default=None, min_length=1, max_length=200)
    search_wiki: bool | None = None
    search_memory: bool | None = None
    search_projects: bool | None = None
    search_conversations: bool | None = None
