"""Markdown helpers: normalization, heading-aware chunking, internal links."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass

_HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t#]*$")
_FENCE_RE = re.compile(r"^[ \t]{0,3}(```|~~~)")
_WIKI_LINK_RE = re.compile(r"\[\[([^\[\]|#\n]+)(?:#[^\]|\n]*)?(?:\|[^\]\n]*)?\]\]")


def normalize_text(text: str) -> str:
    """NFC (macOS files arrive as decomposed Hangul, which would never match a
    search typed on Windows) and LF line endings."""
    return unicodedata.normalize("NFC", text).replace("\r\n", "\n").replace("\r", "\n")


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Chunk:
    index: int
    heading: str  # heading path, e.g. "캐릭터 > 조작"
    content: str
    start: int
    end: int


def _sections(text: str) -> list[tuple[str, int, int]]:
    """Split at ATX headings outside fenced code. Returns (heading_path, start, end)."""
    sections: list[tuple[str, int, int]] = []
    stack: list[tuple[int, str]] = []
    in_fence = False
    current_heading = ""
    current_start = 0
    pos = 0
    for line in text.splitlines(keepends=True):
        stripped = line.rstrip("\n")
        if _FENCE_RE.match(stripped):
            in_fence = not in_fence
        elif not in_fence:
            m = _HEADING_RE.match(stripped)
            if m:
                if pos > current_start:
                    sections.append((current_heading, current_start, pos))
                level = len(m.group(1))
                while stack and stack[-1][0] >= level:
                    stack.pop()
                stack.append((level, m.group(2).strip()))
                current_heading = " > ".join(h for _, h in stack)
                current_start = pos
        pos += len(line)
    if pos > current_start or not sections:
        sections.append((current_heading, current_start, pos))
    return sections


def _split_long(text: str, start: int, end: int, max_chars: int) -> list[tuple[int, int]]:
    """Split [start, end) into pieces <= max_chars, preferring paragraph, then line, then sentence breaks."""
    pieces: list[tuple[int, int]] = []
    s = start
    while end - s > max_chars:
        window = text[s : s + max_chars]
        cut = -1
        for sep in ("\n\n", "\n", ". ", "다. ", "? ", "! "):
            idx = window.rfind(sep)
            if idx > max_chars // 3:
                cut = idx + len(sep)
                break
        if cut <= 0:
            cut = max_chars
        pieces.append((s, s + cut))
        s += cut
    if end > s:
        pieces.append((s, end))
    return pieces


def chunk_markdown(text: str, max_chars: int = 900) -> list[Chunk]:
    """Heading-aware chunks with offsets into ``text``. Always returns at least one chunk."""
    chunks: list[Chunk] = []
    for heading, s, e in _sections(text):
        for ps, pe in _split_long(text, s, e, max_chars):
            body = text[ps:pe]
            if not body.strip():
                continue
            # Trim surrounding whitespace but keep offsets exact.
            lead = len(body) - len(body.lstrip())
            trail = len(body) - len(body.rstrip())
            ps, pe = ps + lead, pe - trail
            chunks.append(Chunk(len(chunks), heading, text[ps:pe], ps, pe))
    if not chunks:
        chunks.append(Chunk(0, "", "", 0, 0))
    return chunks


def extract_wiki_links(text: str) -> list[str]:
    """Targets of ``[[Title]]``, ``[[Title|label]]`` and ``[[Title#section]]`` links, in order, deduplicated."""
    seen: dict[str, None] = {}
    for m in _WIKI_LINK_RE.finditer(text):
        seen.setdefault(m.group(1).strip(), None)
    return [t for t in seen if t]


def excerpt(text: str, length: int = 140) -> str:
    plain = re.sub(r"[#>*`_\[\]|-]+", " ", text)
    plain = re.sub(r"\s+", " ", plain).strip()
    return plain if len(plain) <= length else plain[: length - 1] + "…"
