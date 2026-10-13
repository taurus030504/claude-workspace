"""Application settings.

Every value can be overridden with an environment variable prefixed ``PAW_``
(for example ``PAW_PORT=9000``) or in a ``.env`` file next to the backend.
The data directory is shared with the desktop app, which reads the API token
from it, so both sides must resolve it the same way (see ``default_data_dir``).
"""

from __future__ import annotations

import ipaddress
import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

APP_DIR_NAME = "PersonalAIWiki"


def default_data_dir() -> Path:
    """%LOCALAPPDATA%\\PersonalAIWiki on Windows, XDG data dir elsewhere."""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / APP_DIR_NAME
    base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    return Path(base) / APP_DIR_NAME


def is_loopback_host(host: str) -> bool:
    if host in ("localhost", ""):
        return True
    try:
        return ipaddress.ip_address(host.strip("[]")).is_loopback
    except ValueError:
        return False


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PAW_", env_file=".env", extra="ignore")

    data_dir: Path = Field(default_factory=default_data_dir)

    # Server. Binding outside loopback needs allow_remote_bind, which nothing sets by default.
    host: str = "127.0.0.1"
    port: int = 8765
    allow_remote_bind: bool = False
    # Extra Host header values to accept (DNS-rebinding protection). Tests add "testserver".
    extra_allowed_hosts: list[str] = []

    # Network policy. Ollama on this machine is allowed; anything else must be opted into.
    allow_external_network: bool = False

    # LLM. "mock" runs the app without Ollama (answers are labelled as mock output).
    llm_provider: Literal["ollama", "mock"] = "ollama"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "gemma3:4b"
    ollama_timeout_seconds: float = 300.0
    ollama_num_ctx: int = 4096
    llm_temperature: float = 0.3

    # Retrieval / context budget (characters; Korean is roughly 1.5-2 chars per token)
    retrieval_top_k: int = 6
    max_context_chars: int = 6000
    max_history_messages: int = 8

    # Wiki
    chunk_max_chars: int = 900
    max_import_bytes: int = 5 * 1024 * 1024
    max_page_chars: int = 2_000_000

    log_level: str = "INFO"

    @property
    def db_path(self) -> Path:
        return self.data_dir / "data" / "paw.db"

    @property
    def backups_dir(self) -> Path:
        return self.data_dir / "backups"

    @property
    def attachments_dir(self) -> Path:
        return self.data_dir / "attachments"

    @property
    def logs_dir(self) -> Path:
        return self.data_dir / "logs"

    @property
    def token_path(self) -> Path:
        return self.data_dir / "api_token"

    def ensure_dirs(self) -> None:
        for d in (self.db_path.parent, self.backups_dir, self.attachments_dir, self.logs_dir):
            d.mkdir(parents=True, exist_ok=True)

    def validate_network_policy(self) -> None:
        """Refuse configurations that would send data off this machine without opt-in."""
        if not is_loopback_host(self.host) and not self.allow_remote_bind:
            raise ValueError(
                f"PAW_HOST={self.host} is not a loopback address. "
                "Set PAW_ALLOW_REMOTE_BIND=true only if you really want to expose the API."
            )
        ollama_host = urlparse(self.ollama_base_url).hostname or ""
        if not is_loopback_host(ollama_host) and not self.allow_external_network:
            raise ValueError(
                f"PAW_OLLAMA_BASE_URL points to a non-local host ({ollama_host}). "
                "Set PAW_ALLOW_EXTERNAL_NETWORK=true to allow sending data to it."
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()
