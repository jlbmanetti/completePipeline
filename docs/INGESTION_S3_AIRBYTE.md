# Ingestion: Local CSVs → S3 (Airflow) → Snowflake (Airbyte)

How the first pipeline step works and how to set it up.

## Flow

1. **Airflow** runs a task that uploads `data/raw/olist/*.csv` to **S3** (datalake raw layer).
2. **Airflow** triggers an **Airbyte** connection that syncs from **S3** (source) to **Snowflake** (destination).
3. Airbyte creates/updates raw tables in Snowflake (one stream per CSV or per configured stream).

## Prerequisites

- **AWS:** Account or LocalStack; bucket created (e.g. `completepipeline-raw`); IAM credentials or role for read/write.
- **Snowflake:** Trial or account; warehouse, database, schema for raw data; user/password or key-pair.
- **Airbyte:** Running (Docker or Cloud); S3 source and Snowflake destination configured; one connection S3 → Snowflake.
- **Airflow:** Running; connections: `aws_default` (S3), `airbyte_default` (Airbyte API); DAG `ingest_olist_s3_airbyte` deployed.

---

## 1. S3 layout

| Item | Value (example) |
|------|------------------|
| Bucket | `completepipeline-raw` (or your bucket name) |
| Prefix for Olist | `raw/olist/` |
| Full path | `s3://completepipeline-raw/raw/olist/olist_orders_dataset.csv` |

Use the same CSV filenames as in `data/raw/olist/` so Airbyte can map streams to tables.

---

## 2. Upload local → S3

- **Script (standalone):** `scripts/upload_olist_to_s3.py` — run from repo root. Needs env vars or args: `S3_BUCKET`, optional `S3_PREFIX`, optional `AWS_PROFILE`/credentials.
- **Airflow:** Same logic in the DAG task; local path can be set via Variable or default `data/raw/olist`.

---

## 3. Airbyte setup

1. **Source — S3**
   - Provider: S3.
   - Bucket: same as above.
   - Prefix: `raw/olist` (or leave empty if bucket is dedicated).
   - Format: CSV.
   - Add streams: one per CSV (or use globs), e.g. `olist_*.csv` → stream name = filename without extension → Snowflake table name.

2. **Destination — Snowflake**
   - Account, warehouse, database, schema, user, password (or key).
   - Default schema for raw: e.g. `raw` or `raw_olist`.

3. **Connection**
   - Source: S3 (above).
   - Destination: Snowflake (above).
   - Sync mode: Full refresh (for initial load) or incremental if supported.
   - Save and note the **Connection ID** (UUID) — Airflow will use it in `AirbyteTriggerSyncOperator`.

References: [Airbyte S3 source](https://docs.airbyte.com/integrations/sources/s3), [Airbyte Snowflake destination](https://docs.airbyte.com/integrations/destinations/snowflake).

---

## 4. Airflow

- **Connections (Airflow UI or env):**
  - `aws_default`: type Amazon Web Services; login = Access Key ID; password = Secret Access Key (or use IAM role).
  - `airbyte_default`: type HTTP; host = Airbyte server URL (e.g. `http://localhost:8000` for OSS); login = client_id; password = client_secret (for Airbyte Cloud or OSS with auth).

- **Variables (optional):**
  - `olist_local_path`: e.g. `data/raw/olist` (relative to DAGs folder or repo root).
  - `s3_bucket`: e.g. `completepipeline-raw`.
  - `s3_prefix_olist`: e.g. `raw/olist`.
  - `airbyte_connection_id_olist`: UUID of the S3 → Snowflake connection.

- **DAG:** `ingest_olist_s3_airbyte`
  - Task 1: upload local CSVs to S3 (Python or Bash using boto3/S3Hook).
  - Task 2: `AirbyteTriggerSyncOperator(connection_id=<airbyte_connection_id>)`.
  - Order: task1 >> task2.

---

## 5. Dependencies

- **Upload script:** `pip install boto3` (or use `requirements.txt`).
- **Airflow:** Install providers so the DAG runs: `apache-airflow-providers-amazon`, `apache-airflow-providers-airbyte`. In Docker, add to image or use `pip install -r requirements-airflow.txt` if you add one.

---

## 6. Order of operations (first time)

1. Create S3 bucket and set AWS credentials in Airflow.
2. Run upload script once (or run DAG once) to populate S3.
3. In Airbyte, create S3 source (point to bucket/prefix), Snowflake destination, then Connection; copy Connection ID.
4. Set Airflow connection `airbyte_default` and Variable `airbyte_connection_id_olist` (Airbyte connection UUID; otherwise the trigger task will fail).
5. Run DAG `ingest_olist_s3_airbyte` — it will upload and then trigger Airbyte sync.

After that, schedule the DAG as needed (e.g. daily); ensure new CSVs are in `data/raw/olist/` or adjust for incremental sources later.
