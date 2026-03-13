# Pipeline build notes (study & thought process)

Concise log of what we build, why, and key decisions. Use this to follow step-by-step and to raise questions.

---

## Project choice

- **Dataset:** Brazilian E-Commerce (Olist) — [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) or [GitHub](https://github.com/spdrio/Brazilian-E-Commerce-Public-Dataset-by-Olist).
- **Repo:** [github.com/jlbmanetti/completePipeline](https://github.com/jlbmanetti/completePipeline) (this project).
- **Goal:** End-to-end pipeline: ingest → S3 → Snowflake → DBT (gold) → Python/PySpark ML (scores in Snowflake) → Airflow → CI/CD → dataviz via MCP.

---

## Pipeline steps (as we implement)

| Step | What | Status | Notes |
|------|------|--------|--------|
| 0 | Repo setup + docs | ✅ | PROJECT_GUIDE.md, BUILD_NOTES.md, git remote, first push |
| 1 | Dataset + ingestion | ✅ | Landing, download script, **S3 upload + Airbyte (orchestrated by Airflow)** |
| 2 | Datalake (S3) | ✅ | Upload to `s3://bucket/raw/olist/` (script + DAG task) |
| 3 | Snowflake raw | 🔄 | Airbyte S3 → Snowflake; set connection and run DAG |
| 4 | DBT (staging → silver → gold) | — | Models, tests |
| 5 | ML (Python/PySpark) | — | Train; write scores to Snowflake |
| 6 | Airflow | — | DAG: ingest → DBT → ML |
| 7 | CI/CD | — | dbt test, optional Actions |
| 8 | Dataviz (MCP) | — | Report from Snowflake |

---

## Key decisions & open questions

- **Ingestion (chosen):** Airflow *orchestrates* only. A task runs a copy (local → S3); Airbyte does the real *ingestion* (S3 → Snowflake). DBT does *not* read from S3 — it only runs inside Snowflake (raw → silver → gold) after data is already loaded. See **docs/INGESTION_S3_AIRBYTE.md** “Who does what”.
- **Environments:** Snowflake (trial), S3 (AWS or LocalStack), Airflow (local/Docker), Airbyte (Docker) — we'll set as we go.
- *Your questions can go here or inline under each step.*

---

## Step 0 — Repo & docs ✅

- **Done:** PROJECT_GUIDE.md, BUILD_NOTES.md, .gitignore. Git inited, remote `https://github.com/jlbmanetti/completePipeline.git`, first push to `main`.

---

## Step 1 — Dataset & ingestion ✅

- **Dataset:** Olist — 9 CSVs in `data/raw/olist/` (you downloaded them).
- **Done:**
  - Landing zone, `scripts/download_olist.py`, `scripts/upload_olist_to_s3.py` (local → S3).
  - **docs/INGESTION_S3_AIRBYTE.md** — full procedure: S3 layout, Airbyte setup (S3 source, Snowflake destination), Airflow connections/variables, order of operations.
  - **airflow/dags/ingest_olist_s3_airbyte.py** — DAG: `upload_olist_to_s3` >> `trigger_airbyte_s3_to_snowflake` (AirbyteTriggerSyncOperator).
  - **requirements.txt** — boto3, kaggle.
- **S3 bucket:** ✅ Created — `completepipeline-raw` (region **us-east-2**). **Upload:** ✅ Olist CSVs are in `s3://completepipeline-raw/raw/olist/`.
- **Credentials:** `.env` with AWS keys; IAM user has S3 policy for the bucket.
- **Next steps (S3 → Snowflake → Airflow):** see **"Next steps"** section below.

---

## Next steps (after S3 upload)

Do these in order. Full detail in **docs/INGESTION_S3_AIRBYTE.md**.

| # | Step | What you need / do |
|---|------|--------------------|
| **1** | **Snowflake** | Trial or account; create a **warehouse**, **database** (e.g. `COMPLETEPIPELINE`), **schema** (e.g. `RAW`). Note account id, user, password — Airbyte will use them. |
| **2** | **Airbyte** | Run Airbyte (Docker or Cloud). **Source:** S3 — bucket `completepipeline-raw`, prefix `raw/olist`, format CSV; add streams (one per CSV or glob). **Destination:** Snowflake — account, warehouse, database, schema, user, password. **Connection:** S3 → Snowflake; save and **copy the Connection ID** (UUID). |
| **3** | **Airflow** | Run Airflow. **Connections:** `aws_default` (AWS Access Key + Secret), `airbyte_default` (Airbyte API: host e.g. `http://localhost:8000`, and auth if needed). **Variable:** `airbyte_connection_id_olist` = the Connection ID from step 2. Optional: `s3_bucket`, `s3_prefix_olist`, `olist_local_path`. |
| **4** | **Run pipeline** | Trigger DAG `ingest_olist_s3_airbyte`. It uploads to S3 and triggers the Airbyte sync; raw tables appear in Snowflake. |

Then we can move on to **DBT** (staging → silver → gold in Snowflake).

---

*Update this file as we complete each step. Keep notes short so you can re-read and ask questions easily.*
