@echo off
REM Start Airflow stack. Double-click or run from project root.
REM Requires Docker Desktop running.

cd /d "%~dp0.."
if not exist "docker-compose.airflow.yaml" (
  cd /d "c:\Users\jlbma\OneDrive\6.0 Desenvolvimentos\2.0 - Teste Snowflake"
)
if not exist "docker-compose.airflow.yaml" (
  echo Project root not found.
  pause
  exit /b 1
)

echo Starting Airflow stack...
docker compose -f docker-compose.airflow.yaml up -d
echo.
echo Airflow UI: http://localhost:8080
docker compose -f docker-compose.airflow.yaml ps -a
pause
