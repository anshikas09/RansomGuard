# RansomGuard Setup Script
# Detects Python, configures .venv, installs backend requirements, checks ONNX model, DB, and frontend dependencies.

$ErrorActionPreference = "Stop"

# Determine project root directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Resolve-Path "$ScriptDir\.." | Select-Object -ExpandProperty Path

Write-Host "[RansomGuard] Project root detected: $ProjectRoot" -ForegroundColor Cyan

# 1. Detect Python & Virtual Environment
$VenvDir = "$ProjectRoot\.venv"
$VenvPython = "$VenvDir\Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "[RansomGuard] Virtual environment (.venv) not found. Locating system Python..." -ForegroundColor Yellow
    $SystemPython = $null
    
    foreach ($cmd in @("python.exe", "py.exe", "python3.exe")) {
        try {
            $sysPy = (Get-Command $cmd -ErrorAction SilentlyContinue).Source
            if ($sysPy) {
                $SystemPython = $sysPy
                break
            }
        } catch {}
    }

    if (-not $SystemPython) {
        Write-Host "[RansomGuard] ERROR: Python installation not found on system PATH. Please install Python 3.10+." -ForegroundColor Red
        exit 1
    }

    Write-Host "[RansomGuard] Creating Python virtual environment using $SystemPython..." -ForegroundColor Cyan
    & $SystemPython -m venv $VenvDir
    if (-not (Test-Path $VenvPython)) {
        Write-Host "[RansomGuard] ERROR: Failed to create virtual environment at $VenvDir" -ForegroundColor Red
        exit 1
    }
}

Write-Host "[RansomGuard] Python virtual environment: OK ($VenvPython)" -ForegroundColor Green

# 2. Check & Install Backend Dependencies into .venv
$ReqFile = "$ProjectRoot\backend\requirements.txt"
if (Test-Path $ReqFile) {
    Write-Host "[RansomGuard] Checking backend dependencies in .venv..." -ForegroundColor Cyan
    # Verify uvicorn import as primary indicator
    $UvicornCheck = & $VenvPython -c "import uvicorn" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[RansomGuard] Installing backend dependencies from $ReqFile into .venv..." -ForegroundColor Yellow
        & $VenvPython -m pip install --upgrade pip
        & $VenvPython -m pip install -r $ReqFile
    }
} else {
        Write-Host "[RansomGuard] WARNING: Backend requirements file not found at $ReqFile" -ForegroundColor Yellow
}

# Verify backend packages in .venv
$VerifyScript = "import uvicorn, fastapi, sqlalchemy, pydantic, email_validator, jose, passlib, bcrypt, onnxruntime, torch, numpy, pandas, sklearn, watchdog, psutil; print('OK')"
$CheckResult = & $VenvPython -c $VerifyScript 2>&1
if ($LASTEXITCODE -eq 0 -and $CheckResult -match "OK") {
    Write-Host "[RansomGuard] Backend dependencies: OK" -ForegroundColor Green
} else {
    Write-Host "[RansomGuard] WARNING: Some backend packages may missing or failing to import: $CheckResult" -ForegroundColor Yellow
    Write-Host "[RansomGuard] Attempting automatic repair via pip install..." -ForegroundColor Yellow
    & $VenvPython -m pip install -r $ReqFile
}

# 3. Verify ML Model & Scaler Artifacts
$ModelFile = "$ProjectRoot\models\ransomware_detector.onnx"
$ScalerFile = "$ProjectRoot\models\scaler.pkl"

if (Test-Path $ModelFile) {
    Write-Host "[RansomGuard] ONNX Model artifact: OK ($ModelFile)" -ForegroundColor Green
} else {
    Write-Host "[RansomGuard] WARNING: ONNX Model artifact missing at $ModelFile" -ForegroundColor Yellow
}

if (Test-Path $ScalerFile) {
    Write-Host "[RansomGuard] Scaler artifact: OK ($ScalerFile)" -ForegroundColor Green
} else {
    Write-Host "[RansomGuard] WARNING: Scaler artifact missing at $ScalerFile" -ForegroundColor Yellow
}

# 4. Verify Database & Lab Workspace
$DbFile = "$ProjectRoot\ransomguard.db"
if (Test-Path $DbFile) {
    Write-Host "[RansomGuard] Database: OK ($DbFile)" -ForegroundColor Green
} else {
    Write-Host "[RansomGuard] Database: Not initialized yet (will auto-create on first backend start)" -ForegroundColor Cyan
}

$SimDir = "$ProjectRoot\scratch\ransim_lab"
if (-not (Test-Path $SimDir)) {
    New-Item -ItemType Directory -Path $SimDir -Force | Out-Null
}
Write-Host "[RansomGuard] Safe simulation sandbox directory: OK ($SimDir)" -ForegroundColor Green

# 5. Check Frontend Dependencies
$FrontendNodeModules = "$ProjectRoot\frontend\node_modules"
if (-not (Test-Path $FrontendNodeModules)) {
    Write-Host "[RansomGuard] Frontend node_modules missing. Running npm install in frontend directory..." -ForegroundColor Yellow
    Push-Location "$ProjectRoot\frontend"
    try {
        npm install
    } finally {
        Pop-Location
    }
}
Write-Host "[RansomGuard] Frontend node_modules: OK" -ForegroundColor Green

Write-Host "[RansomGuard] Setup verification completed successfully!" -ForegroundColor Green
