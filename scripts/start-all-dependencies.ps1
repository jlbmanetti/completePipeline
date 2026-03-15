# Start all pipeline dependencies: Docker (wait) -> Airflow stack -> Airbyte (abctl).
# Used by: run manually, or by the scheduled task created with register-auto-start.ps1
#
# Prerequisites:
# - Docker Desktop set to "Start when you sign in" (Settings -> General).
# - abctl in PATH (optional; if missing, only Airflow is started).

$ErrorActionPreference = "Stop"

# Project root (same logic as start-airflow.ps1)
$ProjectRoot = if ($PSScriptRoot) { Split-Path -Parent (Split-Path -Parent $PSScriptRoot) } else { Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }
if (-not (Test-Path "$ProjectRoot\docker-compose.airflow.yaml")) {
    $ProjectRoot = "c:\Users\jlbma\OneDrive\6.0 Desenvolvimentos\2.0 - Teste Snowflake"
}
if (-not (Test-Path "$ProjectRoot\docker-compose.airflow.yaml")) {
    Write-Error "Project root not found (docker-compose.airflow.yaml missing)."
}

$LogDir = "$ProjectRoot\logs"
$LogFile = "$LogDir\start-dependencies-$(Get-Date -Format 'yyyyMMdd').log"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }

function Log {
    param([string]$Message)
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
    Add-Content -Path $LogFile -Value $line -ErrorAction SilentlyContinue
    if ($env:CPIPELINE_SHOW_LOG -eq "1") { Write-Host $line }
}

# --- 1. Wait for Docker ---
Log "Checking Docker..."
$maxAttempts = 45
$attempt = 0
do {
    $null = docker info 2>&1
    if ($LASTEXITCODE -eq 0) { break }
    $attempt++
    Log "  Waiting for Docker... ($attempt/$maxAttempts)"
    Start-Sleep -Seconds 2
} while ($attempt -lt $maxAttempts)
if ($attempt -ge $maxAttempts) {
    Log "ERROR: Docker did not become ready. Start Docker Desktop and run this script again."
    exit 1
}
Log "Docker is ready."

# --- 2. Start Airflow stack ---
Set-Location $ProjectRoot
Log "Starting Airflow stack..."
$ErrorActionPreferencePrev = $ErrorActionPreference
$ErrorActionPreference = "Continue"
try {
    $out = docker compose -f docker-compose.airflow.yaml up -d 2>&1
    foreach ($line in $out) { Log "  $line" }
} finally {
    $ErrorActionPreference = $ErrorActionPreferencePrev
}
if ($LASTEXITCODE -ne 0) {
    Log "ERROR: Airflow stack failed to start."
    exit 1
}
Log "Airflow stack started (UI: http://localhost:8080)."

# Give Airflow a moment before starting Airbyte
Start-Sleep -Seconds 10

# --- 3. Start Airbyte (abctl) if available ---
$abctl = Get-Command abctl -ErrorAction SilentlyContinue
if ($abctl) {
    Log "Starting Airbyte in background (abctl local install)..."
    # Run in background so the script/task finishes; Airbyte keeps starting in its own process
    $abctlPath = $abctl.Source
    Start-Process -FilePath $abctlPath -ArgumentList "local", "install" -WorkingDirectory $ProjectRoot -WindowStyle Hidden
    Log "Airbyte process started (UI: http://localhost:8000 when ready; first time can take several minutes)."
} else {
    Log "Airbyte (abctl) not in PATH - skipping. Add abctl to PATH or start manually: abctl local install"
}

Log "Done. Airflow: http://localhost:8080 | Airbyte: http://localhost:8000 (if started)."
exit 0
