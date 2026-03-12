# Data-Driven Project Manager — End-to-End Pipeline Project Guide

## 1. Role & Objective

You are preparing for a **data-driven project manager** role. Your job is to take projects across different domains and connect the **business solution** to the **underlying data needs**. That means you need to be able to design and oversee pipelines that cover:

| Need | What it means |
|------|----------------|
| **Ingesting data** | Bringing data from sources (APIs, DBs, files) into the platform |
| **Feeding a datalake** | Storing raw/semi-raw data in a scalable, cheap storage layer |
| **Transforming data** | Cleaning, conforming, and modeling data (bronze → silver → gold) |
| **Feeding a data warehouse** | Loading structured, queryable data for analytics and BI |
| **Creating the gold layer** | Business-ready datasets (KPIs, dimensions, facts) for reporting and ML |
| **Creating ML models** | Training and serving models (e.g. predictions, segmentation) |
| **CI/CD for the pipeline** | Versioning, testing, and deploying code and pipelines |
| **Dataviz** | Dashboards and reports on top of the gold layer and ML outputs |

This project is a **hands-on portfolio piece** that uses mainstream technologies at each step so you can speak from experience in interviews and on the job.

---

## 2. Technology Map (Pipeline Stages ↔ Tools)

| Stage | Technology | Role in the pipeline |
|-------|------------|----------------------|
| **Ingestion** | **Airbyte** | Extract from APIs, DBs, files → load into datalake/warehouse (connectors, no-code/low-code) |
| **Datalake (storage)** | **S3** | Raw and staged data; cheap, durable, foundation for lakehouse/warehouse ingestion |
| **Orchestration** | **Airflow** | Schedule and coordinate: Airbyte syncs, DBT runs, ML jobs, alerts, retries |
| **Transformation** | **DBT** | SQL-based transformations in the warehouse: staging → silver → gold, tests, docs |
| **Data warehouse** | **Snowflake** | Central analytics store: tables fed by Airbyte/Spark, transformed by DBT, queried by BI/ML |
| **Processing / ML** | **Python** (e.g. scikit-learn, XGBoost), **PySpark ML** | Feature engineering and model training; no Databricks — run in Airflow or local/VM; write scores and metadata to Snowflake |
| **Query & logic** | **SQL** | DBT models, ad-hoc analysis, gold layer definitions, warehouse queries |
| **Scripting & APIs** | **Python** | Airflow DAGs, custom extractors, ML code, utilities, CI/CD scripts |
| **CI/CD** | (Git + Airflow/DBT best practices) | Version control, DBT tests, deployment of DAGs and ML scripts, optional GitHub Actions / GitLab CI |

*Dataviz:* **MCP-driven report creation** — Cursor (or Claude with MCP) generates the report/dashboard by querying Snowflake and producing the artifact (e.g. HTML, Markdown, or code for a BI tool). No separate BI tool required for the project; optional later: Metabase, Streamlit, etc.

---

## 3. Suggested Project: **“Product Analytics & Churn Prediction Pipeline”**

To touch every step of the pipeline with the stack above, a single end-to-end project is proposed.

### 3.1 Concept

A **fictional SaaS / product company** that wants:

- **Product analytics**: events (page views, signups, feature usage), users, and subscriptions in one place.
- **Churn risk**: a simple ML model that scores users or accounts by churn probability, fed by the gold layer.

No real company is required: we can use **synthetic or public datasets** that look like events, users, and subscriptions.

### 3.2 How each technology is used

| Step | What we do | Technologies |
|------|------------|--------------|
| 1. Ingest | Pull “product events” and “users” from a source (e.g. Postgres/CSV/API) into the platform | **Airbyte** (or Python script in Airflow if we simulate an API) |
| 2. Datalake | Store raw and staged data before loading into the warehouse | **S3** (buckets for raw/landing and optionally staged) |
| 3. Into the warehouse | Load from S3 (or directly from Airbyte) into Snowflake | **Airbyte** → Snowflake or **Airflow** + Snowflake stages from S3 |
| 4. Transform | Build staging → silver → gold (e.g. `user_events`, `dim_user`, `fct_subscriptions`, `gold_user_metrics`) | **DBT** + **SQL** in **Snowflake** |
| 5. Gold layer | Create clean tables: user-level metrics, engagement, tenure, subscription status | **DBT** (gold models) |
| 6. ML | Feature table from gold → train churn (or LTV) model with **Python** (scikit-learn/XGBoost) or **PySpark ML**; write scores and model metadata to **Snowflake** tables | **Python** / **PySpark** (e.g. in Airflow task or script); **Snowflake** for predictions table |
| 7. Orchestration | Schedule: ingestion → DBT run → ML training; handle failures and retries | **Airflow** (DAGs for Airbyte, DBT, ML job) |
| 8. CI/CD | DBT in Git, tests in CI; deploy DAGs and ML scripts | **Git** + **dbt test** + (e.g. **GitHub Actions**) |
| 9. Dataviz | Reports/dashboards on gold tables and ML scores | **MCP**: Cursor (or Claude with MCP) creates the report by querying Snowflake and generating the output (HTML, Markdown, or BI code) |

### 3.3 Data source: public dataset (Kaggle or GitHub)

The project **must use a public dataset** from Kaggle or GitHub. See **Section 8** for concrete options and how to ingest them.

---

## 4. Pipeline Diagram (High level)

```text
[Sources: Public dataset — Kaggle / GitHub]
         │
         ▼
    ┌─────────┐     ┌─────┐
    │ Airbyte │────►│ S3  │  (raw / landing)
    │ or copy │     └──┬──┘
    └────┬────┘        │
         │             │ load into Snowflake
         ▼             ▼
    ┌─────────────────────────┐
    │      Snowflake          │
    │  (raw → DBT → gold)     │
    └────────────┬────────────┘
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
   [Gold tables] [DBT docs] [Python/PySpark ML]
        │                          │
        │                          ▼
        │                   [Scores table in Snowflake]
        │                          │
        ▼                          ▼
   ┌─────────────────────────────────────┐
   │  Airflow (orchestrates all)          │
   └─────────────────────────────────────┘
        │
        ▼
   [Dataviz: MCP — Cursor/Claude creates report from Snowflake]
```

---

## 5. Success Criteria for This Project

- **Ingestion:** At least one source (DB or file) loaded via Airbyte or an Airflow-driven process into S3 and/or Snowflake.
- **Datalake:** S3 used for raw/landing (and optionally staging) with clear naming.
- **Warehouse:** Snowflake has raw/staging tables and DBT-managed silver/gold layers.
- **Transformation:** DBT project with staging, intermediate, and gold models + at least one test.
- **Gold layer:** At least one business-ready table (e.g. user metrics or subscription snapshot) consumed by BI or ML.
- **ML:** One model (e.g. churn or LTV) trained on gold/feature data using **Python** (scikit-learn, XGBoost) or **PySpark ML**; results (scores, optional metadata) written to **Snowflake** tables; training orchestrated by Airflow.
- **Orchestration:** One Airflow DAG that runs ingestion (or S3 load), DBT, and the ML job.
- **CI/CD:** Repo with DBT project and (optional) Airflow DAGs; CI runs `dbt test` (and optionally lint); deployment steps documented.
- **Dataviz:** At least one report or dashboard created via **MCP** (Cursor or Claude with MCP) querying Snowflake (gold + ML scores) and generating the deliverable (e.g. HTML report, Markdown, or code for a BI tool).

---

## 6. Next Steps

1. **Choose a public dataset** from Section 8 (Kaggle or GitHub); download or clone and place in S3 or a path Airbyte/Airflow can read.
2. **Set up environments:** Snowflake (trial), S3 (e.g. AWS trial or LocalStack), Airflow (local or cloud), Airbyte (Docker or cloud).
3. **Implement in order:** Ingest dataset → S3 → Snowflake raw → DBT (staging → silver → gold) → Airflow DAG → Python/PySpark ML job (write scores to Snowflake) → CI/CD → Dataviz via MCP.
4. **Document:** Keep this guide updated with the chosen dataset, project name, and any tool swaps.

---

## 7. Add-ons: Real-Time, Data Quality, Governance, Cost Control

How each of these works in practice when you add them to the pipeline:

### 7.1 Real-time

| Idea | How it works |
|------|----------------|
| **Streaming ingestion** | Events (clicks, logs, IoT) are sent to a **message bus** (e.g. **Kafka**, **Amazon Eventbridge**, **Kinesis**) instead of (or in addition to) batch files. A **connector** or **Snowpipe** reads from the stream and loads into Snowflake in near real time (e.g. every minute or on file arrival). |
| **Where it fits** | After "ingestion" in the diagram: a second path *Sources → Kafka/Eventbridge → Snowpipe → Snowflake raw*. DBT and ML can still run on a schedule; you can have both batch (Airbyte/S3) and streaming (Snowpipe) feeding the same raw layer. |
| **Typical stack** | Kafka or Kinesis → Snowpipe (Snowflake) or Kafka Connector → S3 → Snowpipe. Optionally **dbt with incremental models** so only new rows are processed. |

### 7.2 Data quality

| Idea | How it works |
|------|----------------|
| **DBT tests (first line)** | In DBT you define **schema tests** (e.g. `unique`, `not_null`, `accepted_values`) and **data tests** (custom SQL that must return 0 rows). CI and Airflow run `dbt test`; if any test fails, the pipeline can stop or alert. |
| **Great Expectations** | You define **expectations** (e.g. "column X has no nulls", "values in Y are in this set") and run them in a Python task (e.g. in Airflow) against a table or file. Results can be logged to a store or sent to Slack/email. |
| **Soda** | Similar idea: **Soda Core** (or Soda Cloud) runs **checks** (SQL or file-based) against your data; you run it as a step in the pipeline and act on failures. |
| **Where it fits** | After raw load (validate raw), after key DBT models (validate silver/gold), and optionally after ML (validate score distribution). Same DAG, extra tasks that run tests/expectations and fail the run or trigger alerts. |

### 7.3 Governance

| Idea | How it works |
|------|----------------|
| **Lineage** | "Where did this column come from?" — **OpenLineage** (or provider-specific tools) collects metadata from Airflow (task runs), DBT (model runs), and sometimes Spark: which tables/columns were read and written. That metadata is sent to a **catalog** (e.g. **OpenMetadata**, **Datahub**, **Collibra**) so you get a graph of dependencies. |
| **Catalog & discovery** | A **data catalog** stores table/column names, descriptions, owners, tags, and (if integrated) lineage. Analysts search for "revenue" and find the right gold table and its upstream sources. |
| **Where it fits** | You add OpenLineage (or similar) to Airflow and DBT; the catalog is updated on each run. No change to the core pipeline logic — it's observability and documentation. |

### 7.4 Cost control

| Idea | How it works |
|------|----------------|
| **Snowflake** | **Resource monitors** cap credit usage per warehouse (or per set of warehouses). You set a limit (e.g. 10 credits/day); when hit, the warehouse can suspend or notify. **Query tagging** and **usage views** (`SNOWFLAKE.ACCOUNT_USAGE`) help see which warehouses and queries cost the most so you can optimize or downsize. |
| **S3** | **Lifecycle rules**: e.g. move raw data to **Infrequent Access** or **Glacier** after 30 days so hot storage stays small. **Bucket policies** and **request metrics** help avoid accidental overuse. |
| **Where it fits** | Configuration only: create monitors and lifecycle rules; use usage reports in your operational reviews. No change to DAG logic unless you want "cost check" tasks (e.g. fail if daily credits > threshold). |

---

## 8. Public dataset options (Kaggle & GitHub)

Pick **one** of these to base the project on. All can be ingested into S3 and Snowflake and support gold layers + a simple churn or LTV-style ML model.

### Kaggle

| Dataset | Link | Description | Why it fits |
|--------|------|-------------|-------------|
| **Brazilian E-Commerce (Olist)** | [kaggle.com/datasets/.../brazilian-e-commerce-public-dataset-by-olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) | ~100k orders (2016–2018), orders, customers, products, reviews, payments, geolocation; multiple CSVs | Real e-commerce schema; gold = orders, customers, sellers; ML = churn or satisfaction prediction |
| **E-Commerce Customer Churn** | [kaggle.com/datasets/.../e-commerce-customer-churn](https://www.kaggle.com/datasets/samuelsemaya/e-commerce-customer-churn) | Customer-level features: cashback, days since last order, complaints, satisfaction, tenure, categories | Ready for churn binary classification; good for a simple gold → ML flow |
| **E-Commerce Behavior Dataset** | Search Kaggle for "e-commerce behavior" | ~20k events (views, cart, purchase), users, products, 8 brands, 5 categories | Event-style data; gold = funnel and user metrics; ML = purchase or churn prediction |
| **E-Commerce Churn 2025 / Insights** | [kaggle.com/datasets/.../e-commerce-customer-insights-and-churn-dataset](https://www.kaggle.com/datasets/nabihazahid/e-commerce-customer-insights-and-churn-dataset) | Customer insights and churn-oriented attributes | Same idea as above; pick the one with the schema you prefer |

### GitHub

| Dataset / Repo | Link | Description | Why it fits |
|----------------|------|-------------|-------------|
| **Brazilian E-Commerce by Olist** | [github.com/spdrio/Brazilian-E-Commerce-Public-Dataset-by-Olist](https://github.com/spdrio/Brazilian-E-Commerce-Public-Dataset-by-Olist) | Same Olist dataset as Kaggle; CSVs in the repo or linked | No Kaggle account needed; clone repo or download CSVs → S3 → Snowflake |
| **E-Commerce Customer / Order / Product** | [github.com/luissanchezquintero/ecommerce](https://github.com/luissanchezquintero/ecommerce) | Three CSVs: customers, orders, products | Simple schema; quick to model in DBT and add a small ML layer |

**Suggested for this project:** **Brazilian E-Commerce (Olist)** from Kaggle or GitHub — rich schema, well-known, and good for storytelling in interviews. Alternative: **E-Commerce Customer Churn** (Kaggle) if you want minimal transform and maximum focus on ML and MCP dataviz.

---

*This document is the single source of truth for the pipeline’s purpose, technology choices, and the suggested “Product Analytics & Churn Prediction” project. Update it with your chosen dataset and any tool or scope changes.*
