"""Local API token.

The API listens on 127.0.0.1 only, but any program or web page running on the
same machine can still reach loopback ports. Every /api/v1 route except
/health therefore requires the per-installation token stored in the data
directory, which only the current Windows user can read. The desktop app
reads the same file. Host-header checking (in main.py) blocks DNS rebinding.
"""

from __future__ import annotations

import os
import secrets
import sys
from pathlib import Path

TOKEN_HEADER = "X-PAW-Token"


def ensure_token(path: Path) -> str:
    if path.exists():
        token = path.read_text(encoding="utf-8").strip()
        if len(token) >= 32:
            return token
    token = secrets.token_urlsafe(32)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(token, encoding="utf-8")
    if sys.platform != "win32":
        os.chmod(tmp, 0o600)
    os.replace(tmp, path)
    return token


def token_matches(expected: str, provided: str | None) -> bool:
    return bool(provided) and secrets.compare_digest(expected.encode(), provided.encode())
