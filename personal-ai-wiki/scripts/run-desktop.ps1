<#
.SYNOPSIS
  Starts the desktop app. The app starts the backend itself (and stops it on exit)
  if it is not already running.
#>
param([string]$Configuration = "Release")
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$exe = Join-Path $root "desktop\src\PersonalAIWiki.Desktop\bin\$Configuration\net10.0-windows\PersonalAIWiki.exe"
if (-not (Test-Path $exe)) {
    & dotnet build (Join-Path $root "desktop\PersonalAIWiki.sln") -c $Configuration
}
Start-Process $exe
