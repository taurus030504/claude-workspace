"""Application factory and server entry point (``python -m app``)."""

from __future__ import annotations

import logging
import logging.handlers
import sqlite3
from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app import __version__
from app.ai.llm_provider import LLMProvider
from app.ai.mock_provider import MockProvider
from app.ai.ollama_provider import OllamaProvider
from app.api.deps import require_token
from app.api.routers import chat, search, system, timeline, wiki
from app.config import Settings, get_settings
from app.core.errors import AppError
from app.db.connection import connect
from app.db.migrator import migrate
from app.security import ensure_token
from app.services.wiki_service import WikiService

log = logging.getLogger("app")


def configure_logging(settings: Settings) -> None:
    root = logging.getLogger()
    if any(getattr(h, "_paw", False) for h in root.handlers):
        return
    root.setLevel(settings.log_level.upper())
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    file_handler = logging.handlers.RotatingFileHandler(
        settings.logs_dir / "backend.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    file_handler._paw = True  # type: ignore[attr-defined]
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    console._paw = True  # type: ignore[attr-defined]
    root.addHandler(file_handler)
    root.addHandler(console)


def build_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "mock":
        log.warning("LLM provider is 'mock': answers are placeholders, not model output")
        return MockProvider()
    return OllamaProvider(
        settings.ollama_base_url,
        timeout=settings.ollama_timeout_seconds,
        num_ctx=settings.ollama_num_ctx,
        default_temperature=settings.llm_temperature,
    )


def prepare_database(settings: Settings) -> int:
    """Migrate, then verify the derived search index. Returns the schema version."""
    conn = connect(settings.db_path)
    try:
        migrate(conn, settings.backups_dir)
        version = conn.execute("SELECT coalesce(max(version), 0) FROM schema_migrations").fetchone()[0]
        wiki = WikiService(conn, settings)
        if not wiki.index_is_consistent():
            log.warning("search index out of sync with wiki pages; rebuilding")
            wiki.reindex_all()
        return version
    finally:
        conn.close()


def _error(status: int, code: str, message: str, details: dict | None = None) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message, "details": details or {}}})


def create_app(settings: Settings | None = None, provider: LLMProvider | None = None) -> FastAPI:
    settings = settings or get_settings()
    settings.validate_network_policy()
    settings.ensure_dirs()
    configure_logging(settings)

    schema_version = prepare_database(settings)
    provider = provider or build_provider(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        log.info("backend %s ready: data_dir=%s schema=%s llm=%s", __version__, settings.data_dir, schema_version, provider.name)
        yield
        close = getattr(provider, "close", None)
        if close:
            close()

    app = FastAPI(
        title="Personal AI Wiki & Memory API",
        version=__version__,
        description="Local-only API. Every route except /api/v1/health needs the X-PAW-Token header.",
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.state.provider = provider
    app.state.api_token = ensure_token(settings.token_path)
    app.state.schema_version = schema_version

    hosts = ["127.0.0.1", "localhost", "[::1]", "::1", settings.host, *settings.extra_allowed_hosts]
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=sorted(set(hosts)))

    @app.exception_handler(AppError)
    async def app_error(_: Request, exc: AppError):
        return _error(exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, exc: RequestValidationError):
        errors = [{"loc": list(e.get("loc", [])), "msg": e.get("msg", "")} for e in exc.errors()]
        return _error(422, "validation_error", "request validation failed", {"errors": errors})

    @app.exception_handler(sqlite3.Error)
    async def db_error(_: Request, exc: sqlite3.Error):
        log.exception("database error", exc_info=exc)
        return _error(500, "database_error", "database error; see backend.log")

    app.include_router(system.public_router)
    secured = [Depends(require_token)]
    for r in (wiki.router, search.router, chat.router, timeline.router, system.router):
        app.include_router(r, dependencies=secured)
    return app


def run() -> None:
    settings = get_settings()
    app = create_app(settings)
    config = uvicorn.Config(app, host=settings.host, port=settings.port, log_config=None, access_log=False)
    server = uvicorn.Server(config)
    app.state.server = server
    server.run()
