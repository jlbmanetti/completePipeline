# Project Guide (Clean Version)

This project is now intentionally split into two parts:

1. **Part 1 (Archive):** what we built first with **Airflow + S3 + Airbyte**.
2. **Part 2 (Current path):** **manual upload to Snowflake**, then **DBT**, **Snowpark + ML**, and later **Power BI + Cursor MCP**.

The active path is **Part 2**.

---

## Current Objective

Build an end-to-end analytics project with Olist data:

1. Load raw CSVs into Snowflake (manual/UI-driven for now).
2. Build DBT transformations (raw -> staging/silver/gold).
3. Train/apply ML with Snowpark + Python.
4. Publish analysis and visuals with Power BI and Cursor MCP.

---

## Project Structure (Meaningful Files)

- `docs/PART_1_ARCHIVE_AIRFLOW_S3_AIRBYTE.md`  
  Historical context only (not current execution path).

- `docs/PART_2_CURRENT_MANUAL_SNOWFLAKE_DBT_SNOWPARK_ML_DV.md`  
  Main execution guide from now on.

- `data/raw/olist/README.md`  
  Dataset source and expected files.

- `scripts/download_olist.py`  
  Optional helper to fetch dataset.

- `scripts/upload_olist_to_s3.py`  
  Optional helper when S3 is needed.

---

## Decision Record

- **Ingestion now:** manual via Snowflake UI (or SQL worksheet), one file -> one table.
- **Airbyte:** no longer part of current path.
- **Airflow:** archived for Part 1 context; may return later only if orchestration is needed.
- **Warehouse schema recommendation:** use a dedicated schema (e.g. `RAW`) instead of `PUBLIC` for cleaner organization.

---

## Next Milestones (Part 2)

1. Confirm all Olist CSV tables loaded in Snowflake.
2. Initialize DBT project and build staging models.
3. Build silver/gold marts for analytics.
4. Start Snowpark feature engineering + first ML baseline.
5. Create initial Power BI report and a Cursor MCP-generated analysis output.

