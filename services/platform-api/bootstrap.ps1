Param(
    [switch]$SkipDocker
)

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptRoot "..")

function Resolve-PythonExecutable {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        return $pythonCommand.Source
    }

    $pyCommand = Get-Command py -ErrorAction SilentlyContinue
    if ($pyCommand) {
        return $pyCommand.Source
    }

    throw "Python executable not found. Install Python 3.10+ and ensure it is available on PATH."
}

Write-Host "[1/6] Navigating to platform-api..."
Set-Location $scriptRoot

if (-not $SkipDocker) {
    $composeFile = Join-Path $repoRoot "docker-compose.yml"
    if (-not (Test-Path $composeFile)) {
        throw "docker-compose.yml not found at repository root: $composeFile"
    }

    Write-Host "[2/6] Starting PostgreSQL with Docker Compose..."
    docker compose -f $composeFile up -d postgres
}
else {
    Write-Host "[2/6] Skipping Docker startup because -SkipDocker was provided."
}

Write-Host "[3/6] Creating Python virtual environment (if needed)..."
$pythonExeSystem = Resolve-PythonExecutable

if (-not (Test-Path ".venv")) {
    & $pythonExeSystem -m venv .venv
}

$pythonExe = Join-Path $scriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    Write-Host "Existing virtual environment is incomplete. Recreating it..."
    Remove-Item -Recurse -Force ".venv" -ErrorAction SilentlyContinue
    & $pythonExeSystem -m venv .venv
}

if (-not (Test-Path $pythonExe)) {
    throw "Python executable not found in virtual environment: $pythonExe"
}

Write-Host "[4/6] Installing dependencies..."
& $pythonExe -m pip install --upgrade pip
& $pythonExe -m pip install -r requirements.txt

Write-Host "[5/6] Running Alembic migrations..."
$versionsDir = Join-Path $scriptRoot "alembic\versions"
New-Item -ItemType Directory -Force -Path $versionsDir | Out-Null

$hasMigration = Get-ChildItem -Path $versionsDir -Filter "*.py" -File -ErrorAction SilentlyContinue |
Where-Object { $_.Name -ne "__init__.py" } |
Select-Object -First 1

if (-not $hasMigration) {
    & $pythonExe -m alembic revision --autogenerate -m "create analyses table"
}

& $pythonExe -m alembic upgrade head

Write-Host "[6/6] Starting API with uvicorn..."
$env:PYTHONPATH = Join-Path $scriptRoot "src"
& $pythonExe -m uvicorn src.main:app --reload