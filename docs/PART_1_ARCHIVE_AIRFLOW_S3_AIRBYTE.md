# Part 1 (Archive): Airflow + S3 + Airbyte

This part documents the initial approach used in this project.
It is kept only for historical reference.

## What it was

1. Local Olist CSVs uploaded to S3.
2. Airflow used as orchestrator.
3. Airbyte used to sync S3 -> Snowflake.

## Why archived

- The project direction changed to reduce complexity.
- Current path favors manual Snowflake loading first, then DBT + Snowpark ML.

## Status

- Not the active execution path.
- Do not use this as the primary runbook.

