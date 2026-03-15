# Remove the scheduled task that starts dependencies at logon.
# Run: .\scripts\unregister-auto-start.ps1

$TaskName = "Start completePipeline (Airflow + Airbyte)"
try {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction Stop
    Write-Host "OK: Task '$TaskName' removed. Dependencies will no longer start at logon."
} catch {
    if ($_.Exception.Message -match "Cannot find") {
        Write-Host "Task '$TaskName' was not found (already removed or never created)."
    } else {
        Write-Error "Failed to remove task: $_"
        exit 1
    }
}
