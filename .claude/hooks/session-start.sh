#!/bin/bash
# Installs Serena (MCP server registered in .mcp.json) in Claude Code cloud sessions.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

export PATH="$HOME/.local/bin:$PATH"

if ! command -v uv >/dev/null 2>&1; then
  python3 -m pip install --user --quiet uv
fi

if ! command -v serena >/dev/null 2>&1; then
  uv tool install --quiet --from git+https://github.com/oraios/serena serena-agent
fi

echo "export PATH=\"$HOME/.local/bin:\$PATH\"" >> "${CLAUDE_ENV_FILE:-/dev/null}"
