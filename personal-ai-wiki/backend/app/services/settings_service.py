"""User settings: environment defaults overridden by values saved from the UI."""

from __future__ import annotations

import sqlite3

from app.config import Settings
from app.core.timeutil import now_iso
from app.db.connection import transaction
from app.repositories import settings_repo
from app.schemas.system import AppSettings, AppSettingsUpdate

# Search sources that exist in this build. Others are accepted and stored but
# have no effect until their phase ships (the UI shows them as disabled).
AVAILABLE_SEARCH_SOURCES = ["wiki"]


class SettingsService:
    def __init__(self, conn: sqlite3.Connection, settings: Settings):
        self.conn = conn
        self.settings = settings

    def get(self) -> AppSettings:
        stored = settings_repo.get_all(self.conn)
        return AppSettings(
            llm_model=stored.get("llm_model", self.settings.ollama_model),
            search_wiki=stored.get("search_wiki", True),
            search_memory=stored.get("search_memory", True),
            search_projects=stored.get("search_projects", True),
            search_conversations=stored.get("search_conversations", False),
            available_search_sources=AVAILABLE_SEARCH_SOURCES,
        )

    def update(self, patch: AppSettingsUpdate) -> AppSettings:
        now = now_iso()
        with transaction(self.conn):
            for key, value in patch.model_dump(exclude_none=True).items():
                settings_repo.set_value(self.conn, key, value.strip() if isinstance(value, str) else value, now)
        return self.get()
