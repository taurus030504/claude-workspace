"""Import Markdown / plain-text files as wiki pages.

Files are untrusted input: size and type are checked, binary content is
rejected, nothing is executed, and the text is stored as-is (Markdown is
rendered by the desktop app without scripts or remote resources).
PDF import arrives in a later phase; until then it is refused explicitly
rather than guessed at.
"""

from __future__ import annotations

import re
from email.header import decode_header, make_header
from pathlib import PurePath

from app.core.errors import PayloadTooLargeError, UnsupportedFormatError
from app.schemas.wiki import Page, PageCreate
from app.services.markdown_tools import normalize_text
from app.services.wiki_service import WikiService

TEXT_EXTENSIONS = {".md", ".markdown", ".txt"}
PLANNED_EXTENSIONS = {".pdf": "PDF 가져오기는 이후 단계에서 지원할 예정입니다."}
_H1_RE = re.compile(r"^#[ \t]+(.+?)[ \t#]*$", re.MULTILINE)


def clean_filename(filename: str) -> str:
    """Base name only, with RFC 2047 encoded-words decoded.

    .NET's MultipartFormDataContent sends non-ASCII names as ``=?utf-8?B?...?=``,
    which the multipart parser passes through verbatim.
    """
    name = filename.strip()
    if "=?" in name and "?=" in name:
        try:
            name = str(make_header(decode_header(name)))
        except (ValueError, LookupError, UnicodeDecodeError):
            pass
    return PurePath(name.replace("\\", "/")).name


def decode_text(data: bytes) -> str:
    if b"\x00" in data[:8192]:
        raise UnsupportedFormatError("binary file; only UTF-8 or CP949 text is supported")
    for encoding in ("utf-8-sig", "cp949"):  # cp949 covers legacy Korean Windows text files
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise UnsupportedFormatError("could not decode file as UTF-8 or CP949 text")


class FileImportService:
    def __init__(self, wiki: WikiService):
        self.wiki = wiki

    def import_file(self, filename: str, data: bytes, *, folder: str = "", tags: list[str] | None = None) -> Page:
        name = clean_filename(filename) or "untitled.txt"
        ext = PurePath(name).suffix.lower()
        if ext in PLANNED_EXTENSIONS:
            raise UnsupportedFormatError(PLANNED_EXTENSIONS[ext])
        if ext not in TEXT_EXTENSIONS:
            raise UnsupportedFormatError(f"unsupported file type '{ext or name}'. Supported: .md, .markdown, .txt")
        if len(data) > self.wiki.settings.max_import_bytes:
            raise PayloadTooLargeError(
                f"file is larger than {self.wiki.settings.max_import_bytes // (1024 * 1024)} MB"
            )
        text = normalize_text(decode_text(data))
        title = PurePath(name).stem
        if ext != ".txt":
            m = _H1_RE.search(text)
            if m:
                title = m.group(1).strip()
        return self.wiki.create_page(
            PageCreate(title=title[:300] or "untitled", content=text, folder=folder, tags=tags or []),
            source_type="import_file",
            source_ref=name,
            author="import",
        )
