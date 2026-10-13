"""AI chat: sessions, messages, retrieval-augmented answers with citations.

Flow for one user message:
  1. check the model is ready (fail fast with setup guidance, nothing saved)
  2. save the user message
  3. retrieve passages from enabled sources (Phase 0: wiki)
  4. build the prompt (sources as untrusted data, recent history)
  5. stream the answer from the provider
  6. save the assistant message, even when interrupted (status partial/error),
     and record which passages were given and which were cited
"""

from __future__ import annotations

import json
import logging
import sqlite3
from dataclasses import dataclass
from typing import Callable, Iterator

from app.ai.context_builder import BuiltContext, build_messages, cited_numbers
from app.ai.llm_provider import ChatTurn, LLMProvider, model_available
from app.ai.retrieval import Retriever
from app.config import Settings
from app.core.errors import LLMUnavailableError, NotFoundError
from app.core.ids import new_id
from app.core.timeutil import now_iso
from app.db.connection import transaction
from app.repositories import chat_repo, reference_repo
from app.schemas.chat import Message, SendMessage, SendResult, Session, SessionDetail, SourceRef
from app.services.settings_service import SettingsService

log = logging.getLogger(__name__)

DEFAULT_TITLE = "새 대화"
MAX_QUOTE_CHARS = 2000


@dataclass
class PreparedTurn:
    session_id: str
    model: str
    user_message: Message
    context: BuiltContext
    sources: list[SourceRef]


class ChatService:
    def __init__(
        self,
        conn: sqlite3.Connection,
        settings: Settings,
        provider: LLMProvider,
        connect: Callable[[], sqlite3.Connection],
    ):
        self.conn = conn
        self.settings = settings
        self.provider = provider
        self.connect = connect

    # ------------------------------------------------------------ sessions
    def create_session(self, title: str | None = None) -> Session:
        now = now_iso()
        session_id = new_id()
        with transaction(self.conn):
            chat_repo.insert_session(
                self.conn,
                {
                    "session_id": session_id,
                    "title": (title or "").strip() or DEFAULT_TITLE,
                    "model": None,
                    "started_at": now,
                    "created_at": now,
                    "updated_at": now,
                },
            )
        return self.get_session_info(session_id)

    def list_sessions(self, *, limit: int = 50, offset: int = 0) -> list[Session]:
        return [_to_session(r) for r in chat_repo.list_sessions(self.conn, origin=None, limit=limit, offset=offset)]

    def get_session_info(self, session_id: str) -> Session:
        return _to_session(self._require(session_id))

    def get_session(self, session_id: str) -> SessionDetail:
        row = self._require(session_id)
        msgs = chat_repo.list_messages(self.conn, session_id)
        refs = reference_repo.for_owners(self.conn, "chat_message", [m["message_id"] for m in msgs])
        return SessionDetail(
            **_to_session(row).model_dump(),
            messages=[_to_message(m, refs.get(m["message_id"], [])) for m in msgs],
        )

    def rename_session(self, session_id: str, title: str) -> Session:
        with transaction(self.conn):
            self._require(session_id)
            chat_repo.update_session(self.conn, session_id, title=title.strip(), updated_at=now_iso())
        return self.get_session_info(session_id)

    def delete_session(self, session_id: str) -> None:
        with transaction(self.conn):
            self._require(session_id)
            reference_repo.delete_by_owner(self.conn, "chat_message", chat_repo.message_ids(self.conn, session_id))
            chat_repo.delete_session(self.conn, session_id)

    # ------------------------------------------------------------ messages
    def prepare(self, session_id: str, req: SendMessage) -> PreparedTurn:
        session = self._require(session_id)
        app_settings = SettingsService(self.conn, self.settings).get()
        model = (req.model or app_settings.llm_model).strip()
        self._ensure_ready(model)

        use_wiki = app_settings.search_wiki if req.use_wiki is None else req.use_wiki
        now = now_iso()
        with transaction(self.conn):
            seq = chat_repo.next_seq(self.conn, session_id)
            user_row = {
                "message_id": new_id(),
                "session_id": session_id,
                "seq": seq,
                "role": "user",
                "content": req.content,
                "model": None,
                "status": "complete",
                "created_at": now,
                "recorded_at": now,
                "metadata": {"use_wiki": use_wiki},
            }
            chat_repo.insert_message(self.conn, user_row)
            new_title = None
            if session["title"] == DEFAULT_TITLE and seq == 1:
                first_line = req.content.strip().splitlines()[0]
                new_title = first_line[:40] + ("…" if len(first_line) > 40 else "")
            chat_repo.update_session(self.conn, session_id, title=new_title, updated_at=now)

        history = self._history(session_id, seq)
        passages = Retriever(self.conn).retrieve(req.content, use_wiki=use_wiki, top_k=self.settings.retrieval_top_k)
        context = build_messages(
            req.content, history, passages,
            max_context_chars=self.settings.max_context_chars, retrieval_enabled=use_wiki,
        )
        sources = [
            SourceRef(
                number=i + 1,
                source_type=p.source_type,
                source_id=p.source_id,
                title=p.title,
                heading=p.heading,
                quote=p.text[:MAX_QUOTE_CHARS],
                chunk_id=p.chunk_id,
                revision=p.revision,
                char_start=p.char_start,
                char_end=p.char_end,
            )
            for i, p in enumerate(context.passages)
        ]
        user_message = _to_message(
            self.conn.execute("SELECT * FROM chat_messages WHERE message_id = ?", (user_row["message_id"],)).fetchone(),
            [],
        )
        return PreparedTurn(session_id, model, user_message, context, sources)

    def stream(self, turn: PreparedTurn) -> Iterator[dict]:
        """Yields NDJSON-ready events: start, delta*, then done or error."""
        yield {
            "type": "start",
            "user_message": turn.user_message.model_dump(),
            "sources": [s.model_dump() for s in turn.sources],
            "model": turn.model,
        }
        parts: list[str] = []
        error: Exception | None = None
        completed = False
        saved: Message | None = None
        try:
            for piece in self.provider.chat_stream(
                turn.context.messages, model=turn.model, temperature=self.settings.llm_temperature
            ):
                parts.append(piece)
                yield {"type": "delta", "text": piece}
            completed = True
        except LLMUnavailableError as exc:
            error = exc
        except Exception as exc:  # noqa: BLE001 - reported to the client, logged here
            log.exception("chat generation failed")
            error = exc
        finally:
            status = "complete" if completed else ("error" if error else "partial")
            saved = self._save_assistant(turn, "".join(parts), status, error)
        if error is not None:
            yield {
                "type": "error",
                "code": getattr(error, "code", "internal_error"),
                "message": getattr(error, "message", str(error)),
                "details": getattr(error, "details", {}),
                "assistant_message": saved.model_dump() if saved else None,
            }
        else:
            yield {"type": "done", "assistant_message": saved.model_dump() if saved else None}

    def send(self, turn: PreparedTurn) -> SendResult:
        assistant: Message | None = None
        for event in self.stream(turn):
            if event["type"] == "error":
                raise LLMUnavailableError(event["message"], details=event["details"])
            if event["type"] == "done":
                assistant = Message(**event["assistant_message"])
        assert assistant is not None
        return SendResult(user_message=turn.user_message, assistant_message=assistant)

    # ------------------------------------------------------------ helpers
    def _ensure_ready(self, model: str) -> None:
        status = self.provider.status()
        if not status.reachable:
            raise LLMUnavailableError(
                "로컬 LLM(Ollama)에 연결할 수 없습니다. 설정 화면의 안내를 확인하세요.",
                details={"reason": "unreachable", "base_url": status.base_url, "error": status.error},
            )
        if not model_available(model, status.models):
            raise LLMUnavailableError(
                f"모델 '{model}'이(가) 설치되어 있지 않습니다. 터미널에서 'ollama pull {model}'을 실행하세요.",
                details={"reason": "model_missing", "model": model, "installed": status.models},
            )

    def _history(self, session_id: str, before_seq: int) -> list[ChatTurn]:
        rows = chat_repo.recent_messages(self.conn, session_id, self.settings.max_history_messages, before_seq)
        turns = [ChatTurn(r["role"], r["content"]) for r in rows if r["role"] in ("user", "assistant")]
        budget = self.settings.max_context_chars
        kept: list[ChatTurn] = []
        for t in reversed(turns):
            budget -= len(t.content)
            if budget < 0:
                break
            kept.append(t)
        return list(reversed(kept))

    def _save_assistant(self, turn: PreparedTurn, content: str, status: str, error: Exception | None) -> Message:
        conn = self.connect()
        try:
            now = now_iso()
            message_id = new_id()
            cited = cited_numbers(content, len(turn.sources))
            metadata: dict = {"source_count": len(turn.sources)}
            if error is not None:
                metadata["error"] = getattr(error, "message", str(error))
            with transaction(conn):
                row = {
                    "message_id": message_id,
                    "session_id": turn.session_id,
                    "seq": chat_repo.next_seq(conn, turn.session_id),
                    "role": "assistant",
                    "content": content,
                    "model": turn.model,
                    "status": status,
                    "created_at": now,
                    "recorded_at": now,
                    "metadata": metadata,
                }
                chat_repo.insert_message(conn, row)
                for s in turn.sources:
                    reference_repo.add(
                        conn,
                        owner_type="chat_message",
                        owner_id=message_id,
                        source_type=s.source_type,
                        source_id=s.source_id,
                        relation="cited" if s.number in cited else "context",
                        quote=s.quote,
                        locator={
                            "number": s.number,
                            "title": s.title,
                            "heading": s.heading,
                            "chunk_id": s.chunk_id,
                            "revision": s.revision,
                            "char_start": s.char_start,
                            "char_end": s.char_end,
                        },
                        rank=s.number,
                        created_at=now,
                    )
                chat_repo.update_session(conn, turn.session_id, updated_at=now)
                conn.execute(
                    "UPDATE chat_sessions SET model = ? WHERE session_id = ?", (turn.model, turn.session_id)
                )
            msg = conn.execute("SELECT * FROM chat_messages WHERE message_id = ?", (message_id,)).fetchone()
            refs = reference_repo.for_owners(conn, "chat_message", [message_id])[message_id]
            return _to_message(msg, refs)
        finally:
            conn.close()

    def _require(self, session_id: str) -> sqlite3.Row:
        row = chat_repo.get_session(self.conn, session_id)
        if row is None:
            raise NotFoundError(f"chat session {session_id} not found")
        return row


def _to_session(r: sqlite3.Row) -> Session:
    return Session(
        session_id=r["session_id"],
        title=r["title"],
        origin=r["origin"],
        source_service=r["source_service"],
        model=r["model"],
        message_count=r["message_count"],
        started_at=r["started_at"],
        created_at=r["created_at"],
        updated_at=r["updated_at"],
    )


def _to_message(m: sqlite3.Row, refs: list[sqlite3.Row]) -> Message:
    sources = []
    for r in refs:
        loc = json.loads(r["locator"])
        sources.append(
            SourceRef(
                number=loc.get("number", r["rank"] or 0),
                source_type=r["source_type"],
                source_id=r["source_id"],
                title=loc.get("title", ""),
                heading=loc.get("heading", ""),
                quote=r["quote"] or "",
                chunk_id=loc.get("chunk_id"),
                revision=loc.get("revision"),
                char_start=loc.get("char_start"),
                char_end=loc.get("char_end"),
                cited=r["relation"] == "cited",
            )
        )
    return Message(
        message_id=m["message_id"],
        session_id=m["session_id"],
        seq=m["seq"],
        role=m["role"],
        content=m["content"],
        model=m["model"],
        status=m["status"],
        created_at=m["created_at"],
        recorded_at=m["recorded_at"],
        sources=sources,
        metadata=json.loads(m["metadata"]),
    )
