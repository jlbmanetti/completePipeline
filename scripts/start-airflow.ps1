# Start Airflow stack (Postgres + Webserver + Scheduler).
# Run from project root: .\scripts\start-airflow.ps1
# Or from anywhere: & "c:\Users\jlbma\OneDrive\6.0 Desenvolvimentos\2.0 - Teste Snowflake\scripts\start-airflow.ps1"
#
# For auto-start after PC restart: see docs/STARTUP_AFTER_RESTART.md

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path "$ProjectRoot\docker-compose.airflow.yaml")) {
    $ProjectRoot = "c:\Users\jlbma\OneDrive\6.0 Desenvolvimentos\2.0 - Teste Snowflake"
}
if (-not (Test-Path "$ProjectRoot\docker-compose.airflow.yaml")) {
    Write-Error "Project root not found (docker-compose.airflow.yaml missing)."
}

# Optional: wait for Docker to be ready (useful when run at Windows login)
$maxAttempts = 30
$attempt = 0
do {
    $running = docker info 2>$null
    if ($LASTEXITCODE -eq 0) { break }
    $attempt++
    if ($attempt -eq 1) { Write-Host "Waiting for Docker..." }
    Start-Sleep -Seconds 2
} while ($attempt -lt $maxAttempts)
if ($attempt -ge $maxAttempts) {
    Write-Error "Docker is not running. Start Docker Desktop and run this script again."
}

Set-Location $ProjectRoot
Write-Host "Starting Airflow stack in $ProjectRoot ..."
docker compose -f docker-compose.airflow.yaml up -d
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "Done. Airflow UI: http://localhost:8080 (admin / admin)"
docker compose -f docker-compose.airflow.yaml ps -a
