#!/usr/bin/env bash
# Runs backend tests and the desktop core tests (WPF project is compiled, not run).
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
(cd "$root/backend" && .venv/bin/python -m pytest)
dotnet test "$root/desktop/PersonalAIWiki.sln"
