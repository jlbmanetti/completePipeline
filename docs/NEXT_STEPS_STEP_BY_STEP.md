# Next steps — step by step

Follow this order. **Snowflake** is already set up (warehouse `COMPUTE_WH`, database `COMPLETEPIPELINE`, schema `RAW`).

---

## Phase 1 — Airbyte (Docker via abctl)

Airbyte no longer ships a root `docker-compose` in their repo. The official way to run Airbyte OSS locally is **abctl** (it uses Docker + Kubernetes under the hood).

1. **Install Docker Desktop** (if not already): [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/). Keep it running in the background.
2. **Install abctl** (Windows):
   - Open [abctl releases on GitHub](https://github.com/airbytehq/abctl/releases/latest).
   - Check your CPU: **Settings → System → About** → under "Processor", if it says **AMD** or **Intel**, download **windows-amd64**; if **ARM**, download **windows-arm64**.
   - Download the `.zip` for your architecture, extract it to a folder (e.g. `C:\tools\abctl`), and add that folder to your **Path** (Search "environment variables" → Edit system environment variables → Environment Variables → Path → Edit → New → paste the folder path → OK).
   - Open a **new** PowerShell or Command Prompt and run:
   ```powershell
   abctl version
   ```
   If you see a version number, abctl is ready.
3. **Run Airbyte** in a terminal:
   ```powershell
   abctl local install
   ```
   - First run can take up to ~30 minutes (downloads images). Use `--low-resource-mode` if you have only 2 CPUs / 8 GB RAM.
   - When it finishes, the browser should open at `http://localhost:8000`. If not, open that URL yourself.
4. **Get login credentials** (in another terminal while Airbyte is running):
   ```powershell
   abctl local credentials
   ```
   Use the **password** (and email) shown there to log in at `http://localhost:8000`.
   **After a PC restart:** If you started Airbyte again with `abctl local install`, the old credentials no longer work — Airbyte creates new ones each time. Run `abctl local credentials` again and use the new email/password to log in.
5. **Create Source — S3:**
   - Connections → **New source** → search **S3**.
   - **Bucket:** `completepipeline-raw`
   - **Prefix:** `raw/olist`
   - **Region:** `us-east-2`
   - **AWS credentials:** Access Key ID and Secret Access Key (same as in your `.env`).
   - **Format:** CSV (configure date/datetime if needed).
   - **Streams:** Add streams for each CSV (e.g. glob `**/*.csv` or add one stream per file). Map stream name to desired Snowflake table name.
   - **Test** and **Set up source**.
6. **Create Destination — Snowflake:**
   - Connections → **New destination** → search **Snowflake**.
   - **Host:** Use the exact value from Snowflake: in the Snowflake UI, click your **Account** (bottom-left) → **View account details** → copy **Account/Server URL** and paste into Airbyte’s Host field (without `https://`). Example: `sr65175.us-east-2.aws.snowflakecomputing.com` or `orgname-account.snowflakecomputing.com`.
   - **Role:** e.g. `ACCOUNTADMIN` (see Account menu → Switch Role).
   - **Warehouse:** `COMPUTE_WH`
   - **Database:** `COMPLETEPIPELINE`
   - **Schema:** `RAW`
   - **Username** and **Password** (Snowflake user).
   - **Test** and **Set up destination**.
   - If you get **"Connection is not available, request timed out" (HikariPool)**, see **Troubleshooting — Snowflake destination** below.
7. **Create Connection:**
   - **New connection** → Source: your S3 source → Destination: your Snowflake destination.
   - For each stream, set **Sync mode** to **Full refresh | Overwrite** (no primary key required). If you leave **Incremental | Append + Deduped**, Airbyte will show "Primary key missing" because file/CSV sources often have no unique key.
   - **Set up connection** / **Finish & Sync** → save.
8. **Copy the Connection ID:** Open the connection you just created; the URL or connection settings will show a **Connection ID** (UUID). Copy it — Airflow will need it.

### Troubleshooting — Snowflake destination: "Connection is not available, request timed out" (HikariPool)

This usually means Airbyte (running in Docker/Kubernetes) cannot reach Snowflake within 30 seconds. Try in order:

1. **Use the exact Host from Snowflake**  
   In Snowflake: **Account menu** (bottom-left) → **View account details** → copy **Account/Server URL**. Paste that into Airbyte’s **Host** field (strip `https://`). If your account uses the org format, the host may look like `qvefmdd-sr65175.snowflakecomputing.com` instead of `sr65175.us-east-2.aws.snowflakecomputing.com`.

2. **Snowflake network policy**  
   If your account has a **network policy** that restricts by IP, Airbyte’s outbound IP may be blocked. In Snowflake: **Admin** → **Network policies** (or ask your admin). Either add your machine’s **public IP** to the allowed list, or temporarily disable the policy to test. To see your public IP: open [https://whatismyip.com](https://whatismyip.com) from the same network where Airbyte runs.

3. **Firewall / VPN**  
   Ensure outbound **HTTPS (443)** to `*.snowflakecomputing.com` is allowed. If you’re on a corporate VPN or firewall, try from a different network (e.g. home) or have IT allow Snowflake.

4. **Try the other host format**  
   - If you used `sr65175.us-east-2.aws.snowflakecomputing.com`, try the org-based host: `qvefmdd-sr65175.snowflakecomputing.com` (replace with your org and account from the Snowflake URL).  
   - If you used the org-based host, try the regional one: `sr65175.us-east-2.aws.snowflakecomputing.com`.

5. **Airbyte version**  
   Old Airbyte versions (e.g. 0.40.28) had a known HikariPool timeout with Snowflake. Update with `abctl local install` to get the latest image.

---

## Phase 2 — Airflow (Docker)

**→ Full step-by-step (with Airflow concepts): [docs/PHASE2_AIRFLOW_DOCKER_STEP_BY_STEP.md](PHASE2_AIRFLOW_DOCKER_STEP_BY_STEP.md)**

Summary:

1. **Docker setup:** Use `docker-compose.airflow.yaml` in the project root. It uses the official `apache/airflow` image, installs `apache-airflow-providers-amazon` and `apache-airflow-providers-airbyte`, and mounts `./airflow/dags` and `./data`.
2. **Start:** From project root: `docker compose -f docker-compose.airflow.yaml up -d postgres` → then run `airflow db init` and `airflow users create` (see Phase 2 doc) → then `docker compose -f docker-compose.airflow.yaml up -d`.
3. **Open UI:** http://localhost:8080 (login: `admin` / `admin` unless you changed it).
4. **Connections:** `aws_default` (AWS), `airbyte_default` (Host: `http://host.docker.internal:8000`).
5. **Variables:** `airbyte_connection_id_olist` = Airbyte connection UUID; `olist_local_path` = `/opt/airflow/data/raw/olist` (path inside container).
6. **Unpause** the DAG `ingest_olist_s3_airbyte` and **Trigger** a run.

---

## Phase 3 — Run the pipeline

1. **Trigger the DAG** `ingest_olist_s3_airbyte` (manual trigger).
2. **Task 1** uploads local CSVs to S3 (requires `olist_local_path` or default path to have the CSV files; if Airflow runs in Docker, mount `data/raw/olist` or run upload script once so S3 is already populated).
3. **Task 2** triggers the Airbyte connection; Airbyte syncs S3 → Snowflake.
4. **Check Snowflake:** In database `COMPLETEPIPELINE`, schema `RAW`, you should see tables created by Airbyte (one per stream).

---

## After a PC restart

Containers stop when the PC restarts. To bring everything back up:

- **Fully automatic at login:** Run once `.\scripts\register-auto-start.ps1`, then enable Docker “Start when you sign in”. After that, Airflow + Airbyte start automatically ~45 s after each logon. See **[docs/STARTUP_AFTER_RESTART.md](STARTUP_AFTER_RESTART.md)**.
- **Manual once:** Run `.\scripts\start-all-dependencies.ps1` (all) or `.\scripts\start-airflow.ps1` (Airflow only).

---

## After that

- **DBT:** Configure DBT to use Snowflake (database `COMPLETEPIPELINE`, schema for silver/gold). Build staging, silver, and gold models on top of the raw tables.
- **ML:** Use gold (or a feature table) to train a churn/LTV model; write scores back to Snowflake.
- **Dataviz:** Use MCP (Cursor/Claude) to generate reports from Snowflake.

---

*Reference: **docs/INGESTION_S3_AIRBYTE.md** for concepts and details.*
