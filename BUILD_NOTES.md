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
| 0 | Repo setup + docs | — | PROJECT_GUIDE.md, BUILD_NOTES.md, git remote |
| 1 | Dataset + ingestion | Next | Get Olist CSVs → landing (local/S3); decide Airbyte vs script |
| 2 | Datalake (S3) | — | Buckets, layout (raw/landing) |
| 3 | Snowflake raw | — | Load from S3 or Airbyte |
| 4 | DBT (staging → silver → gold) | — | Models, tests |
| 5 | ML (Python/PySpark) | — | Train; write scores to Snowflake |
| 6 | Airflow | — | DAG: ingest → DBT → ML |
| 7 | CI/CD | — | dbt test, optional Actions |
| 8 | Dataviz (MCP) | — | Report from Snowflake |

---

## Key decisions & open questions

- **Ingestion:** Olist is CSV. Options: (A) Download once → place in S3 or folder; (B) Airbyte file connector (if path/S3 available); (C) Airflow task that downloads/syncs. We'll pick one in Step 1.
- **Environments:** Snowflake (trial), S3 (AWS or LocalStack), Airflow (local/Docker), Airbyte (Docker) — we'll set as we go.
- *Your questions can go here or inline under each step.*

---

## Step 0 — Repo & docs (current)

- **Done:** PROJECT_GUIDE.md (full spec), BUILD_NOTES.md (this file).
- **Next:** Git init (if needed), remote `https://github.com/jlbmanetti/completePipeline.git`, initial commit and push.

---

## Step 1 — Dataset & ingestion (next)

- **Dataset:** Olist — multiple CSVs (orders, customers, order_items, products, etc.).
- **Planned:** Download or clone dataset → define landing (e.g. `data/raw/olist/` or S3 prefix) → document schema/sources → choose ingestion path (script vs Airbyte) for later automation.

---

*Update this file as we complete each step. Keep notes short so you can re-read and ask questions easily.*
