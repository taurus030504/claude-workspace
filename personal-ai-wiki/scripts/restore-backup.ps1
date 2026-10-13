<#
.SYNOPSIS
  Restores the database from a backup. Close the app first.
  The current database is moved aside (never deleted).
.EXAMPLE
  scripts\restore-backup.ps1 -List
  scripts\restore-backup.ps1 "$env:LOCALAPPDATA\PersonalAIWiki\backups\paw-manual-20261013T120000Z.db"
#>
param([string]$BackupFile = "", [switch]$List)
$ErrorActionPreference = "Stop"
$backend = Join-Path (Split-Path -Parent $PSScriptRoot) "backend"
$py = Join-Path $backend ".venv\Scripts\python.exe"
Push-Location $backend
try {
    if ($List -or -not $BackupFile) { & $py -m app.tools.restore --list }
    else { & $py -m app.tools.restore $BackupFile }
} finally { Pop-Location }
