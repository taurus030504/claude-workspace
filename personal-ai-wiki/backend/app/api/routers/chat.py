from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.responses import StreamingResponse

from app.api.deps import chat_service
from app.schemas.chat import SendMessage, SendResult, Session, SessionCreate, SessionDetail, SessionUpdate
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])
Chat = Annotated[ChatService, Depends(chat_service)]


@router.get("/sessions", response_model=list[Session])
def list_sessions(
    chat: Chat,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return chat.list_sessions(limit=limit, offset=offset)


@router.post("/sessions", response_model=Session, status_code=status.HTTP_201_CREATED)
def create_session(body: SessionCreate, chat: Chat):
    return chat.create_session(body.title)


@router.get("/sessions/{session_id}", response_model=SessionDetail)
def get_session(session_id: str, chat: Chat):
    return chat.get_session(session_id)


@router.patch("/sessions/{session_id}", response_model=Session)
def rename_session(session_id: str, body: SessionUpdate, chat: Chat):
    return chat.rename_session(session_id, body.title)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: str, chat: Chat):
    chat.delete_session(session_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/sessions/{session_id}/messages",
    response_model=SendResult,
    responses={200: {"content": {"application/x-ndjson": {}}, "description": "stream=true: NDJSON events"}},
)
def send_message(session_id: str, body: SendMessage, chat: Chat):
    """Ask the assistant. Fails with 503 ``llm_unavailable`` (nothing saved)
    when Ollama or the model is missing.

    ``stream=true`` returns ``application/x-ndjson``, one JSON object per line:
    ``start`` (user message + sources) → ``delta``* → ``done`` | ``error``.
    """
    turn = chat.prepare(session_id, body)
    if not body.stream:
        return chat.send(turn)

    def lines():
        for event in chat.stream(turn):
            yield json.dumps(event, ensure_ascii=False) + "\n"

    return StreamingResponse(lines(), media_type="application/x-ndjson", headers={"Cache-Control": "no-store"})
