# RansomGuard Windows One-Command Development Launcher
# Starts FastAPI backend (port 8000) and React frontend (port 3000)

$ErrorActionPreference = "Continue"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Resolve-Path "$ScriptDir\.." | Select-Object -ExpandProperty Path

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " STARTING RANSOMGUARD SOC PLATFORM" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Run Setup Verification
& "$ScriptDir\setup.ps1"
if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) {
    Write-Host "[RansomGuard] ERROR: Setup verification failed." -ForegroundColor Red
    exit 1
}

$VenvPython = "$ProjectRoot\.venv\Scripts\python.exe"

# 2. Helper function to test port availability
function Test-PortOpen([string]$HostName, [int]$Port) {
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $asyncResult = $client.BeginConnect($HostName, $Port, $null, $null)
        $waitHandle = $asyncResult.AsyncWaitHandle
        if (-not $waitHandle.WaitOne(1000, $false)) {
            $client.Close()
            return $false
        }
        $client.EndConnect($asyncResult)
        $client.Close()
        return $true
    } catch {
        return $false
    }
}

# Helper function to test HTTP status
function Test-UrlResponding([string]$Url) {
    try {
        $req = [System.Net.WebRequest]::Create($Url)
        $req.Timeout = 2000
        $res = $req.GetResponse()
        $res.Close()
        return $true
    } catch {
        return $false
    }
}

# 3. Backend Management (Port 8000)
$BackendPortOpen = Test-PortOpen "127.0.0.1" 8000

if ($BackendPortOpen) {
    if (Test-UrlResponding "http://127.0.0.1:8000/api/v1/health") {
        Write-Host "[RansomGuard] Backend: ALREADY RUNNING at http://127.0.0.1:8000" -ForegroundColor Green
    } else {
        Write-Host "[RansomGuard] WARNING: Port 8000 is occupied by another process. Please check port 8000." -ForegroundColor Yellow
    }
} else {
    Write-Host "[RansomGuard] Starting FastAPI backend service..." -ForegroundColor Cyan
    $BackendProcess = Start-Process -FilePath $VenvPython `
        -ArgumentList "-m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000" `
        -WorkingDirectory "$ProjectRoot\backend" `
        -PassThru `
        -WindowStyle Hidden

    Write-Host "[RansomGuard] Waiting for FastAPI backend health check..." -ForegroundColor Cyan
    $HealthOk = $false
    for ($i = 0; $i -lt 15; $i++) {
        Start-Sleep -Seconds 1
        if (Test-UrlResponding "http://127.0.0.1:8000/api/v1/health") {
            $HealthOk = $true
            break
        }
    }

    if ($HealthOk) {
        Write-Host "[RansomGuard] Backend: STARTED successfully at http://127.0.0.1:8000" -ForegroundColor Green
    } else {
        Write-Host "[RansomGuard] ERROR: FastAPI backend failed to respond at http://127.0.0.1:8000/api/v1/health" -ForegroundColor Red
        Write-Host "[RansomGuard] Check backend logs or run python -m uvicorn app.main:app manually in backend/" -ForegroundColor Yellow
    }
}

# 4. Print Status Box
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " RansomGuard is running." -ForegroundColor Green
Write-Host ""
Write-Host " Frontend:  http://localhost:3000" -ForegroundColor White
Write-Host " Backend:   http://localhost:8000" -ForegroundColor White
Write-Host " API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 5. Open Browser
try {
    Start-Process "http://localhost:3000"
} catch {
    Write-Host "[RansomGuard] Please open http://localhost:3000 in your browser." -ForegroundColor Yellow
}

# 6. Start React Frontend (Port 3000)
Write-Host "[RansomGuard] Launching React frontend server..." -ForegroundColor Cyan
Set-Location "$ProjectRoot\frontend"
$env:BROWSER = "none"
$env:PORT = "3000"

# Run react-scripts via node directly
& node node_modules/react-scripts/scripts/start.js
