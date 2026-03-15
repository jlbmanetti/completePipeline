# Start dependencies after PC restart

One script starts **all** dependencies (Airflow + Airbyte). One-time setup makes it run **automatically at every logon**.

---

## Fully automatic (recommended)

### One-time setup

1. **Enable Docker at login**  
   Docker Desktop → **Settings** (gear) → **General** → enable **“Start Docker Desktop when you sign in to your computer”**.

2. **Register auto-start** (run once in PowerShell from project root):
   ```powershell
   .\scripts\register-auto-start.ps1
   ```
   This creates a Windows scheduled task that runs **45 seconds after you log on** and starts:
   - **Airflow** (Postgres + Webserver + Scheduler) → http://localhost:8080  
   - **Airbyte** (abctl), if it’s in your PATH → http://localhost:8000  

3. **Optional:** Ensure **abctl** is on your system PATH so Airbyte starts too (Phase 1 guide). If abctl is not in PATH, only Airflow will start automatically.

After the next restart (or log off/log on), wait about a minute. Airflow and Airbyte will start in the background. No need to run anything by hand.

### Remove automatic start

To stop dependencies from starting at logon:

```powershell
.\scripts\unregister-auto-start.ps1
```

---

## What runs and in what order

The script **scripts/start-all-dependencies.ps1** (run by the scheduled task or by you) does:

1. **Wait for Docker** (up to ~90 seconds) so Docker Desktop is ready.
2. **Start Airflow stack**: `docker compose -f docker-compose.airflow.yaml up -d`.
3. **Start Airbyte** (if `abctl` is in PATH): runs `abctl local install` in the background so the script exits quickly; Airbyte keeps starting on its own.

Logs are written to **logs/start-dependencies-YYYYMMDD.log** in the project folder (one file per day). Use them to confirm startup or debug.

---

## Manual start (when you need it)

To start everything once without using the scheduled task:

```powershell
.\scripts\start-all-dependencies.ps1
```

To start only Airflow (no Airbyte):

```powershell
.\scripts\start-airflow.ps1
```

To stop Airflow:

```powershell
.\scripts\stop-airflow.ps1
```

---

## Summary

| Goal | Action |
|------|--------|
| **Automatic at every logon** | Run once: `.\scripts\register-auto-start.ps1` and enable Docker “Start when you sign in”. |
| **Stop automatic start** | Run: `.\scripts\unregister-auto-start.ps1` |
| **Start everything now** | Run: `.\scripts\start-all-dependencies.ps1` |
| **Start only Airflow** | Run: `.\scripts\start-airflow.ps1` |
| **Stop Airflow** | Run: `.\scripts\stop-airflow.ps1` |
| **Check logs** | Open `logs/start-dependencies-YYYYMMDD.log` |

**URLs:** Airflow → http://localhost:8080 (admin / admin) | Airbyte → http://localhost:8000
