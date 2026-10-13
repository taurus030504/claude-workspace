#!/usr/bin/env bash
# Backend setup for development on Linux/macOS (the desktop app itself is Windows-only).
set -euo pipefail
cd "$(dirname "$0")/../backend"
python3 -m venv .venv
.venv/bin/pip install -q -r requirements-dev.txt
echo "backend ready: .venv/bin/python -m app   (PAW_LLM_PROVIDER=mock to run without Ollama)"
