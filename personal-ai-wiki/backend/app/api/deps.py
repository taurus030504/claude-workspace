"""FastAPI dependencies: settings, per-request DB connection, auth, services."""

from __future__ import annotations

import sqlite3
from typing import Annotated, Iterator

from fastapi import Depends, Header, Request

from app.ai.llm_provider import LLMProvider
from app.config import Settings
from app.core.errors import AppError
from app.db.connection import connect
from app.security import token_matches
from app.services.chat_service import ChatService
from app.services.search_service import SearchService
from app.services.settings_service import SettingsService
from app.services.timeline_service import TimelineService
from app.services.wiki_service import WikiService


class UnauthorizedError(AppError):
    status_code = 401
    code = "unauthorized"


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_provider(request: Request) -> LLMProvider:
    return request.app.state.provider


def get_conn(request: Request) -> Iterator[sqlite3.Connection]:
    conn = connect(request.app.state.settings.db_path)
    try:
        yield conn
    finally:
        conn.close()


def require_token(
    request: Request,
    x_paw_token: Annotated[str | None, Header()] = None,
    authorization: Annotated[str | None, Header()] = None,
) -> None:
    provided = x_paw_token
    if provided is None and authorization and authorization.lower().startswith("bearer "):
        provided = authorization[7:].strip()
    if not token_matches(request.app.state.api_token, provided):
        raise UnauthorizedError("missing or invalid API token (header X-PAW-Token)")


Conn = Annotated[sqlite3.Connection, Depends(get_conn)]
AppSettingsDep = Annotated[Settings, Depends(get_settings)]


def wiki_service(conn: Conn, settings: AppSettingsDep) -> WikiService:
    return WikiService(conn, settings)


def search_service(conn: Conn) -> SearchService:
    return SearchService(conn)


def timeline_service(conn: Conn) -> TimelineService:
    return TimelineService(conn)


def settings_service(conn: Conn, settings: AppSettingsDep) -> SettingsService:
    return SettingsService(conn, settings)


def chat_service(
    conn: Conn, settings: AppSettingsDep, provider: Annotated[LLMProvider, Depends(get_provider)]
) -> ChatService:
    return ChatService(conn, settings, provider, lambda: connect(settings.db_path))
