# Stop Airflow stack.
# Run from project root: .\scripts\stop-airflow.ps1

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path "$ProjectRoot\docker-compose.airflow.yaml")) {
    $ProjectRoot = "c:\Users\jlbma\OneDrive\6.0 Desenvolvimentos\2.0 - Teste Snowflake"
}
if (-not (Test-Path "$ProjectRoot\docker-compose.airflow.yaml")) {
    Write-Error "Project root not found."
}
Set-Location $ProjectRoot
docker compose -f docker-compose.airflow.yaml down
Write-Host "Airflow stack stopped."
