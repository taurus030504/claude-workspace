<#
.SYNOPSIS
  One-time setup on Windows 10/11: Python venv + backend packages, .NET build, Ollama check.
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
  powershell -ExecutionPolicy Bypass -File scripts\setup.ps1 -PullModel gemma3:4b
#>
param(
    [string]$PullModel = ""
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"
$desktop = Join-Path $root "desktop"

function Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }

Step "Python 확인 (3.11 이상 필요)"
$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) { $python = "py"; $pyArgs = @("-3") } else {
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    $pyArgs = @()
    $python = if ($cmd) { $cmd.Source } else { $null }
    if (-not $python) { throw "Python이 없습니다. https://www.python.org/downloads/ 에서 3.11 이상을 설치하세요 ('Add to PATH' 체크)." }
}
$ver = & $python @pyArgs -c "import sys; print('%d.%d' % sys.version_info[:2])"
if ([version]$ver -lt [version]"3.11") { throw "Python $ver 은(는) 너무 오래되었습니다. 3.11 이상이 필요합니다." }
& $python @pyArgs -c "import sqlite3; c=sqlite3.connect(':memory:'); c.execute(""create virtual table t using fts5(x, tokenize='trigram')"")" 2>$null
if ($LASTEXITCODE -ne 0) { Write-Warning "이 Python의 SQLite는 FTS5 trigram을 지원하지 않습니다. 한국어 검색이 느린 대체 방식으로 동작합니다." }
Write-Host "Python $ver OK"

Step "백엔드 가상환경과 패키지 설치"
$venvPy = Join-Path $backend ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) { & $python @pyArgs -m venv (Join-Path $backend ".venv") }
& $venvPy -m pip install --upgrade pip --quiet
& $venvPy -m pip install -r (Join-Path $backend "requirements-dev.txt") --quiet
Write-Host "backend\.venv 준비 완료"

Step ".NET SDK 확인 (10.0 이상 필요)"
$dotnet = Get-Command dotnet -ErrorAction SilentlyContinue
if (-not $dotnet) { throw ".NET SDK가 없습니다. https://dotnet.microsoft.com/download/dotnet/10.0 에서 SDK를 설치하세요." }
$sdks = & dotnet --list-sdks
if (-not ($sdks | Where-Object { $_ -match '^(1[0-9])\.' })) { throw ".NET 10 SDK가 필요합니다. 설치된 SDK: $sdks" }

Step "데스크톱 앱 빌드"
& dotnet build (Join-Path $desktop "PersonalAIWiki.sln") -c Release
if ($LASTEXITCODE -ne 0) { throw "빌드 실패" }

Step "Ollama 확인"
$ollama = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollama) {
    Write-Warning "Ollama가 설치되어 있지 않습니다. AI 채팅을 쓰려면 https://ollama.com/download 에서 설치하세요. (위키 기능은 Ollama 없이도 동작합니다.)"
} else {
    Write-Host "Ollama: $(& ollama --version)"
    if ($PullModel) {
        Step "모델 내려받기: $PullModel"
        & ollama pull $PullModel
    } else {
        Write-Host "모델이 없다면: ollama pull gemma3:4b   (가벼운 한국어 모델: ollama pull exaone3.5:2.4b)"
    }
}

Write-Host "`n설치 완료. 실행: scripts\run-desktop.ps1" -ForegroundColor Green
