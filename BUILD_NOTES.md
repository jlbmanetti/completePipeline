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
| 1 | Dataset + ingestion | 🔄 | Landing `data/raw/olist/`, README, download script; next: get CSVs then S3/Snowflake |
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

## Step 0 — Repo & docs ✅

- **Done:** PROJECT_GUIDE.md, BUILD_NOTES.md, .gitignore. Git inited, remote `https://github.com/jlbmanetti/completePipeline.git`, first push to `main`.

---

## Step 1 — Dataset & ingestion (in progress)

- **Dataset:** Olist — 9 CSVs (customers, orders, order_items, order_payments, order_reviews, products, sellers, geolocation, product_category_name_translation).
- **Done:**
  - Landing zone: `data/raw/olist/` with `README.md` (file list, sources, how to get data).
  - Script: `scripts/download_olist.py` (Kaggle API) for optional one-shot download.
- **Next:** You download the CSVs (Kaggle or GitHub) into `data/raw/olist/`. Then we can add S3 upload (or Airbyte) and Snowflake load.

---

*Update this file as we complete each step. Keep notes short so you can re-read and ask questions easily.*
