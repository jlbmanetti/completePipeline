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

- **Ingestion (chosen):** Airflow uploads local `data/raw/olist/*.csv` → S3; Airflow triggers Airbyte connection S3 → Snowflake. So: datalake (S3) + warehouse load (Airbyte) both orchestrated by one DAG.
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
- **Your next steps (study):**
  1. Create S3 bucket; set AWS credentials in Airflow (`aws_default`).
  2. Run `python scripts/upload_olist_to_s3.py --bucket <your-bucket>` once to populate S3 (or run the DAG).
  3. In Airbyte: create S3 source (bucket + prefix `raw/olist`), Snowflake destination, Connection; copy Connection ID.
  4. In Airflow: set connection `airbyte_default` (Airbyte API), Variable `airbyte_connection_id_olist`, and optional `s3_bucket` / `s3_prefix_olist` / `olist_local_path`.
  5. Run DAG `ingest_olist_s3_airbyte` to upload and sync to Snowflake.

---

*Update this file as we complete each step. Keep notes short so you can re-read and ask questions easily.*
