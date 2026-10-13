"""Builds the message list sent to the model.

Retrieved text is untrusted: it may contain "ignore previous instructions"
style text (imported web pages, pasted conversations). It is wrapped in
<source> elements inside the *user* turn, with markup-like sequences
neutralised so a document cannot close its own element and impersonate the
system prompt. The system prompt tells the model to treat it as data.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.ai.llm_provider import ChatTurn
from app.ai.prompts import NO_SOURCES_NOTE, SOURCES_DISABLED_NOTE, SYSTEM_PROMPT
from app.ai.retrieval import RetrievedPassage

_TAG_RE = re.compile(r"</?\s*(sources?|system|instructions?)\b[^>]*>", re.IGNORECASE)
_CITE_RE = re.compile(r"\[(\d{1,2})\]")


def sanitize_source_text(text: str) -> str:
    return _TAG_RE.sub(lambda m: m.group(0).replace("<", "‹").replace(">", "›"), text)


def _attr(value: str) -> str:
    return value.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


@dataclass
class BuiltContext:
    messages: list[ChatTurn]
    passages: list[RetrievedPassage]  # numbered 1..n in this order


def build_messages(
    question: str,
    history: list[ChatTurn],
    passages: list[RetrievedPassage],
    *,
    max_context_chars: int,
    retrieval_enabled: bool,
) -> BuiltContext:
    used: list[RetrievedPassage] = []
    blocks: list[str] = []
    budget = max_context_chars
    for p in passages:
        text = sanitize_source_text(p.text)
        if len(text) > budget:
            if budget < 200:
                break
            text = text[:budget] + "…"
        n = len(used) + 1
        heading = f' section="{_attr(p.heading)}"' if p.heading else ""
        blocks.append(
            f'<source id="{n}" title="{_attr(p.title)}"{heading} updated="{p.updated_at[:10]}">\n{text}\n</source>'
        )
        used.append(p)
        budget -= len(text)

    if blocks:
        user_content = "<sources>\n" + "\n".join(blocks) + "\n</sources>\n\n질문: " + question
    elif retrieval_enabled:
        user_content = f"({NO_SOURCES_NOTE})\n\n질문: {question}"
    else:
        user_content = f"({SOURCES_DISABLED_NOTE})\n\n질문: {question}"

    messages = [ChatTurn("system", SYSTEM_PROMPT), *history, ChatTurn("user", user_content)]
    return BuiltContext(messages, used)


def cited_numbers(answer: str, count: int) -> set[int]:
    return {n for n in (int(m) for m in _CITE_RE.findall(answer)) if 1 <= n <= count}
