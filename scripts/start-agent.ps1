# RansomGuard Endpoint Agent Launcher Script
# Monitors strictly inside scratch\ransim_lab\ for safe ransomware telemetry simulation

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Resolve-Path "$ScriptDir\.." | Select-Object -ExpandProperty Path
$VenvPython = "$ProjectRoot\.venv\Scripts\python.exe"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " STARTING RANSOMGUARD ENDPOINT AGENT" -ForegroundColor Cyan
Write-Host " Target Directory: $ProjectRoot\scratch\ransim_lab" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if (-not (Test-Path $VenvPython)) {
    Write-Host "[RansomGuard] ERROR: Virtual environment Python not found. Run scripts\setup.ps1 first." -ForegroundColor Red
    exit 1
}

Set-Location "$ProjectRoot"
& $VenvPython "endpoint_agent\agent.py"
