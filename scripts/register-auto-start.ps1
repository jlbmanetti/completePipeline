# One-time setup: create a Windows scheduled task that runs start-all-dependencies.ps1
# at every logon (with a delay so Docker Desktop is ready).
#
# Run once as yourself (no admin required): .\scripts\register-auto-start.ps1
# To remove auto-start later: .\scripts\unregister-auto-start.ps1

$ErrorActionPreference = "Stop"

$ProjectRoot = if ($PSScriptRoot) { (Resolve-Path (Join-Path (Split-Path -Parent $PSScriptRoot))).Path } else { Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }
if (-not (Test-Path "$ProjectRoot\docker-compose.airflow.yaml")) {
    $ProjectRoot = "c:\Users\jlbma\OneDrive\6.0 Desenvolvimentos\2.0 - Teste Snowflake"
}
$StartScript = Join-Path $ProjectRoot "scripts\start-all-dependencies.ps1"
if (-not (Test-Path $StartScript)) {
    Write-Error "Start script not found: $StartScript"
}

$TaskName = "Start completePipeline (Airflow + Airbyte)"
$DelaySeconds = 45

$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$StartScript`""
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$trigger.Delay = "PT${DelaySeconds}S"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

try {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
    Write-Host "OK: Scheduled task '$TaskName' created."
    Write-Host "    It will run $DelaySeconds seconds after you log on and start:"
    Write-Host "    - Airflow (Postgres + Webserver + Scheduler) -> http://localhost:8080"
    Write-Host "    - Airbyte (abctl), if in PATH -> http://localhost:8000"
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "  1. Docker Desktop -> Settings -> General -> enable 'Start Docker Desktop when you sign in'."
    Write-Host "  2. Restart the PC (or log off and back on) to test."
    Write-Host ""
    Write-Host "To remove auto-start: .\scripts\unregister-auto-start.ps1"
} catch {
    Write-Error "Failed to register task: $_"
    exit 1
}
