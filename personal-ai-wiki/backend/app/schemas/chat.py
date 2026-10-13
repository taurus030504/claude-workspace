from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator

MAX_MESSAGE_CHARS = 20_000


class SessionCreate(BaseModel):
    title: str | None = Field(default=None, max_length=200)


class SessionUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class Session(BaseModel):
    session_id: str
    title: str
    origin: str
    source_service: str | None
    model: str | None
    message_count: int
    started_at: str
    created_at: str
    updated_at: str


class SourceRef(BaseModel):
    """A passage given to the model as context. ``cited`` is true when the answer
    referred to it with a [n] marker."""

    number: int
    source_type: str  # wiki_page
    source_id: str
    title: str
    heading: str
    quote: str
    chunk_id: str | None = None
    revision: int | None = None
    char_start: int | None = None
    char_end: int | None = None
    cited: bool = False


class Message(BaseModel):
    message_id: str
    session_id: str
    seq: int
    role: str
    content: str
    model: str | None
    status: str
    created_at: str
    recorded_at: str
    sources: list[SourceRef] = []
    metadata: dict[str, Any] = {}


class SessionDetail(Session):
    messages: list[Message]


class SendMessage(BaseModel):
    content: str = Field(min_length=1, max_length=MAX_MESSAGE_CHARS)
    stream: bool = True
    model: str | None = Field(default=None, description="Override the configured model for this message")
    use_wiki: bool | None = Field(default=None, description="Override the wiki search setting for this message")

    @field_validator("content")
    @classmethod
    def _not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("message must not be blank")
        return v


class SendResult(BaseModel):
    user_message: Message
    assistant_message: Message
