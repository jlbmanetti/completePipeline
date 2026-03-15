# Phase 2 — Airflow with Docker (step-by-step)

This guide gets Airflow running in Docker and teaches enough concepts so you can use it confidently. Follow the steps in order.

---

## Part A: What is Airflow?

**Apache Airflow** is an **orchestrator**: it runs your tasks on a schedule (or on demand) and keeps track of what succeeded or failed. It does **not** move data by itself; it runs *code* that does (e.g. “upload files to S3”, “call the Airbyte API”).

### Main ideas

| Concept | What it means |
|--------|----------------|
| **DAG** (Directed Acyclic Graph) | A workflow: a set of **tasks** with dependencies. Example: “first upload to S3, then trigger Airbyte”. One DAG = one pipeline. |
| **Task** | One unit of work (e.g. “run this Python function”, “trigger this Airbyte connection”). |
| **Task dependency** | “Task B runs only after Task A succeeds.” In our DAG: `upload_to_s3 >> trigger_airbyte`. |
| **Scheduler** | Background process that decides *when* to run which task (e.g. “run this DAG every day at 6am”, or “run it now because the user clicked Trigger”). |
| **Webserver** | The UI you see at http://localhost:8080. You trigger DAGs, see logs, and manage connections/variables here. |
| **Executor** | *Where* tasks run. We use **LocalExecutor**: tasks run on the same machine as the scheduler (inside the scheduler container). No extra “worker” containers. |
| **Connection** | Stored credentials (e.g. AWS keys, Airbyte API URL). Tasks use them by **connection id** (e.g. `aws_default`, `airbyte_default`). |
| **Variable** | Key-value config (e.g. `airbyte_connection_id_olist` = the Airbyte connection UUID). So you don’t hardcode secrets or IDs in the DAG. |

### Our DAG in one sentence

**DAG `ingest_olist_s3_airbyte`:**  
Task 1 uploads `data/raw/olist/*.csv` to S3; Task 2 triggers the Airbyte connection so Airbyte syncs S3 → Snowflake. Task 2 runs only after Task 1 succeeds.

---

## Part B: Prerequisites

Before starting, have:

1. **Docker Desktop** installed and running (same as for Airbyte/abctl).
2. **Phase 1 done:** Airbyte running (e.g. `abctl local install`), with:
   - S3 source and Snowflake destination configured,
   - A **connection** S3 → Snowflake (Full refresh | Overwrite),
   - The connection **saved** and its **Connection ID** (UUID) copied — you’ll need it for Airflow.
3. **AWS credentials** (same as in `.env`): Access Key ID and Secret Access Key for the S3 bucket `completepipeline-raw`.
4. **Project on disk** with:
   - `airflow/dags/ingest_olist_s3_airbyte.py`
   - `data/raw/olist/` containing the Olist CSV files (so the upload task has something to send to S3).

If Airbyte is on your **host** (your PC) and Airflow runs **inside Docker**, Airflow will reach Airbyte at **`http://host.docker.internal:8000`** (we’ll set that as the Airbyte connection host).

---

## Part C: Start Airflow with Docker

All commands below are run from the **project root** (the folder that contains `airflow/`, `data/`, and `docker-compose.airflow.yaml`).

### Step 1 — Start PostgreSQL only (Airflow’s database)

Airflow stores its state (DAGs, run history, connections, variables) in a database. We use PostgreSQL.

```powershell
docker compose -f docker-compose.airflow.yaml up -d postgres
```

Wait until Postgres is healthy (about 10–20 seconds). You can check with:

```powershell
docker compose -f docker-compose.airflow.yaml ps
```

When `postgres` shows “healthy”, continue.

---

### Step 2 — Initialize the Airflow database

The first time you run Airflow, its database tables must be created. Run:

```powershell
docker compose -f docker-compose.airflow.yaml run --rm airflow-scheduler airflow db init
```

This creates all tables in the `airflow` database. You only need to do this **once** (unless you delete the Postgres volume).

---

### Step 3 — Create an Airflow admin user

You need at least one user to log in to the UI. Create an admin user (password `admin` — change it later if you want):

```powershell
docker compose -f docker-compose.airflow.yaml run --rm airflow-scheduler airflow users create --role Admin --username admin --email admin@example.com --firstname Admin --lastname User --password admin
```

If you get “User already exists”, that’s fine — you can use that user or create another.

---

### Step 4 — Start the webserver and scheduler

```powershell
docker compose -f docker-compose.airflow.yaml up -d
```

This starts:

- **airflow-webserver** (UI on port 8080)
- **airflow-scheduler** (runs your DAGs and tasks)

Give it 1–2 minutes. The first time, the images may need to install the extra providers (Amazon, Airbyte), so the scheduler might restart once.

---

### Step 5 — Open the Airflow UI and log in

1. Open a browser and go to: **http://localhost:8080**
2. Log in with:
   - **Username:** `admin`
   - **Password:** `admin`

You should see the **DAGs** list. If the DAGs folder is mounted correctly, you’ll see **`ingest_olist_s3_airbyte`** (it might take up to a minute to appear; the scheduler scans the `dags` folder periodically).

**If the DAG does not appear:**  
Check that the path `./airflow/dags` on your machine contains `ingest_olist_s3_airbyte.py` and that the file has no syntax errors. In the UI: **Browse → DAGs** and look for import errors in the list.

---

## Part D: Configure Airflow (connections and variables)

Airflow needs to know:

- How to talk to **AWS** (to upload to S3),
- How to talk to **Airbyte** (to trigger the sync),
- The **Airbyte connection ID** and (for Docker) the **path where the Olist CSVs live inside the container**.

### Step 6 — Add the AWS connection

1. In the Airflow UI, go to **Admin → Connections**.
2. Click **+ Add a new record**.
3. Fill in:

   | Field | Value |
   |-------|--------|
   | **Connection id** | `aws_default` |
   | **Connection type** | Amazon Web Services |
   | **AWS Access Key ID** | Your access key (same as in `.env`) |
   | **AWS Secret Access Key** | Your secret key (same as in `.env`) |
   | **Extra** | Optional. You can put `{"region_name": "us-east-2"}` if you want to fix the region. |

4. Click **Save**.

The DAG uses `aws_default` to get AWS credentials when uploading files to S3.

---

### Step 7 — Add the Airbyte connection

1. Still in **Admin → Connections**, click **+ Add a new record** again.
2. Fill in:

   | Field | Value |
   |-------|--------|
   | **Connection id** | `airbyte_default` |
   | **Connection type** | Airbyte |
   | **Host** | `http://host.docker.internal:8000/api/public/v1/` |
   | **Token URL** | (optional) `/api/public/v1/applications/token` |
   | **Client ID** / **Password** | If your Airbyte requires API auth: create an Application in Airbyte (Settings → Applications) and paste Client ID and Client Secret here. Otherwise leave blank. |

   **Why `host.docker.internal`?**  
   Airflow runs *inside* Docker. Airbyte runs on your *host* at `localhost:8000`. From inside a container, `localhost` is the container itself, not your PC. `host.docker.internal` points to your host, so Airflow can call the Airbyte API.

   **If the second DAG task (trigger_airbyte_s3_to_snowflake) fails:**  
   The Host must include the API path `/api/public/v1/`. See **docs/AIRFLOW_AIRBYTE_CONNECTION_FIX.md** for step-by-step fix and optional API credentials.

3. Click **Save**.

---

### Step 8 — Add Variables

Variables are key-value pairs the DAG reads (e.g. `Variable.get("airbyte_connection_id_olist")`).

1. Go to **Admin → Variables**.
2. Click **+ Add a new record** and add these **one by one**:

   **Variable 1 — Airbyte connection ID (required)**

   | Key | Val |
   |-----|-----|
   | `airbyte_connection_id_olist` | The **Connection ID** (UUID) from Airbyte. You find it in Airbyte: open your S3 → Snowflake connection; the URL or the connection settings show the UUID. Copy it here. |

   **Variable 2 — Path to Olist CSVs inside the container (required for Docker)**

   | Key | Val |
   |-----|-----|
   | `olist_local_path` | ` /opt/airflow/data/raw/olist` |

   In the compose file we mount `./data` to `/opt/airflow/data`, so `data/raw/olist` on your PC is `/opt/airflow/data/raw/olist` inside the container. The upload task runs inside the container, so it must use this path.

   **Optional — S3 target (the DAG has defaults)**

   | Key | Val |
   |-----|-----|
   | `s3_bucket` | `completepipeline-raw` |
   | `s3_prefix_olist` | `raw/olist` |

   If you don’t set these, the DAG uses these defaults anyway.

3. Save each variable.

---

## Part E: Run the pipeline

### Step 9 — Unpause the DAG

1. Go to **DAGs**.
2. Find **`ingest_olist_s3_airbyte`**.
3. Turn the toggle on the left from **Off** to **On** (unpaused).  
   When unpaused, the scheduler can run the DAG (on schedule or when you trigger it). Our DAG has `schedule=None`, so it runs **only when you trigger it manually**.

---

### Step 10 — Trigger a run

1. Click the name **`ingest_olist_s3_airbyte`** to open the DAG view.
2. Click the **Play** button (Trigger DAG) on the right.
3. Optionally add a **config** (we don’t need it for this DAG). Click **Trigger**.

You’ll see a new **run** (DAG Run) appear. The circle next to it will go from “running” to “success” (green) when both tasks finish.

---

### Step 11 — Watch the tasks

1. Click the **run** (e.g. the orange “running” circle or the date/time of the run).
2. You’ll see the **Graph** or **Grid** view with two tasks:
   - **upload_olist_to_s3**
   - **trigger_airbyte_s3_to_snowflake**
3. Click a task → **Log** to see the logs (upload count, or Airbyte trigger result).
4. When both are green, the run is successful:
   - CSVs are in S3,
   - Airbyte has been triggered and has synced S3 → Snowflake.

---

### Step 12 — Check Snowflake

In Snowflake, in database **COMPLETEPIPELINE**, schema **RAW**, you should see the tables created by Airbyte (one per stream). That confirms the full path: **local CSVs → (Airflow) S3 → (Airbyte) Snowflake**.

---

## Part F: Airflow concepts you’ll use often

- **DAGs** = list of pipelines. **Trigger DAG** = run the pipeline once (or on schedule if you set one).
- **Task** = one step. **Logs** = stdout/stderr of that step; use them to debug.
- **Connections** = credentials (AWS, Airbyte, DBs). Never put secrets in the DAG code; use connections (and variables for non-secret config).
- **Variables** = config (IDs, paths, feature flags). Easier to change without editing code.
- **Schedule** = cron or preset (`@daily`, `None`). Our DAG uses `None` so it only runs when you click Trigger.
- **Clear / Retry** = from a task instance you can “clear” it (and downstream) to re-run, or “retry” after a failure.

---

## Part G: Useful commands

| Goal | Command |
|------|--------|
| Start Airflow | `docker compose -f docker-compose.airflow.yaml up -d` |
| Stop Airflow | `docker compose -f docker-compose.airflow.yaml down` |
| View logs (scheduler) | `docker compose -f docker-compose.airflow.yaml logs -f airflow-scheduler` |
| View logs (webserver) | `docker compose -f docker-compose.airflow.yaml logs -f airflow-webserver` |
| Run a one-off Airflow CLI command | `docker compose -f docker-compose.airflow.yaml run --rm airflow-scheduler airflow <command>` |

---

## Part H: Troubleshooting

**DAG not showing in the list**  
- Check that `airflow/dags/ingest_olist_s3_airbyte.py` exists and has no Python errors.  
- Check scheduler logs: `docker compose -f docker-compose.airflow.yaml logs airflow-scheduler` for import errors.

**“Connection is not available” or timeout when triggering Airbyte**  
- From inside Docker, Airflow must use `http://host.docker.internal:8000`, not `http://localhost:8000`.  
- Ensure Airbyte is actually running on the host (open http://localhost:8000 in your browser).

**Upload task: “Local Olist dir not found”**  
- You must set variable `olist_local_path` = `/opt/airflow/data/raw/olist` (path *inside* the container).  
- Ensure `./data` is mounted (see `docker-compose.airflow.yaml` volumes) and that `data/raw/olist/` contains CSV files on your PC.

**Permission errors on Windows (e.g. when writing logs)**  
- The compose file uses `AIRFLOW_UID: ${AIRFLOW_UID:-0}`. On Windows you can set in a `.env` file (in the same folder as the compose file): `AIRFLOW_UID=0`. Then run the compose again.

**Change admin password**  
- Use the UI: **Admin → Users** → edit the user.  
- Or CLI: `docker compose -f docker-compose.airflow.yaml run --rm airflow-scheduler airflow users reset-password -u admin -p <new_password>`.

---

*Next: Phase 3 is simply “run the DAG and verify in Snowflake”. After that, move on to DBT for raw → silver → gold.*
