#!/bin/bash
# Makes sure uv is available and pre-downloads Serena so the "serena" MCP server
# in .mcp.json (launched via uvx) starts quickly on any machine.
# Never blocks the session: failures only print a hint.

export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

if ! command -v uvx >/dev/null 2>&1; then
  if [ "${CLAUDE_CODE_REMOTE:-}" = "true" ]; then
    python3 -m pip install --user --quiet uv >/dev/null 2>&1 || true
  else
    case "$(uname -s)" in
      MINGW*|MSYS*|CYGWIN*)
        powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex" >/dev/null 2>&1 || true
        export PATH="$USERPROFILE/.local/bin:$PATH" ;;
      *)
        curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1 || true ;;
    esac
  fi
fi

if ! command -v uvx >/dev/null 2>&1; then
  echo "uv could not be installed automatically, so the Serena MCP server will not start. Install uv: https://docs.astral.sh/uv/getting-started/installation/"
  exit 0
fi

uvx --from serena-agent serena --version >/dev/null 2>&1 \
  || echo "Serena could not be pre-downloaded; the Serena MCP server may fail to start."

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export PATH=\"$HOME/.local/bin:\$PATH\"" >> "$CLAUDE_ENV_FILE"
fi
exit 0
