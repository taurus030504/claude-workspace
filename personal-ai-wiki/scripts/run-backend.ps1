<#
.SYNOPSIS
  Runs only the backend in this console (useful for development or other API clients).
  Listens on http://127.0.0.1:8765 . Stop with Ctrl+C.
.EXAMPLE
  scripts\run-backend.ps1
  scripts\run-backend.ps1 -Mock      # without Ollama: placeholder answers
#>
param([switch]$Mock)
$ErrorActionPreference = "Stop"
$backend = Join-Path (Split-Path -Parent $PSScriptRoot) "backend"
$py = Join-Path $backend ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { throw "가상환경이 없습니다. 먼저 scripts\setup.ps1 을 실행하세요." }
if ($Mock) { $env:PAW_LLM_PROVIDER = "mock" }
$env:PYTHONUTF8 = "1"
Push-Location $backend
try { & $py -m app } finally { Pop-Location }
