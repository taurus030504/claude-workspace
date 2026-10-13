<#
.SYNOPSIS
  Runs all automated tests: backend (pytest) and desktop core (xUnit, including
  contract tests that start the real backend with a mock LLM).
.PARAMETER Ollama
  Also run the real Ollama integration tests (Ollama running + model pulled).
#>
param([switch]$Ollama, [string]$Model = "gemma3:4b")
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$py = Join-Path $root "backend\.venv\Scripts\python.exe"

if ($Ollama) { $env:PAW_TEST_OLLAMA = "1"; $env:PAW_TEST_OLLAMA_MODEL = $Model }
Push-Location (Join-Path $root "backend")
try { & $py -m pytest; if ($LASTEXITCODE -ne 0) { throw "backend tests failed" } } finally { Pop-Location }

& dotnet test (Join-Path $root "desktop\PersonalAIWiki.sln")
if ($LASTEXITCODE -ne 0) { throw "desktop tests failed" }
Write-Host "모든 테스트 통과" -ForegroundColor Green
