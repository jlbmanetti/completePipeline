# Part 2 (Current): Manual Snowflake -> DBT -> Snowpark ML -> Dataviz

This is the active project path.

## Scope

1. **Manual ingest into Snowflake** (UI-driven, one CSV -> one table).
2. **DBT transformations** (raw -> staging/silver/gold).
3. **Snowpark + ML** (feature engineering, model training/scoring).
4. **Dataviz** with Power BI + Cursor MCP-generated analysis outputs.

---

## Step 1: Manual ingest (current focus)

Use Snowflake UI:

1. Open **Data > Add Data > Load data into a Table**.
2. Select **one file at a time** (important).
3. Pick target database/schema (recommended: `COMPLETEPIPELINE.RAW`).
4. Create a table with a clear short name:
   - `olist_customers_dataset.csv` -> `CUSTOMERS`
   - `olist_orders_dataset.csv` -> `ORDERS`
   - `olist_order_items_dataset.csv` -> `ORDER_ITEMS`
   - `olist_order_payments_dataset.csv` -> `ORDER_PAYMENTS`
   - `olist_order_reviews_dataset.csv` -> `ORDER_REVIEWS`
   - `olist_products_dataset.csv` -> `PRODUCTS`
   - `olist_sellers_dataset.csv` -> `SELLERS`
   - `olist_geolocation_dataset.csv` -> `GEOLOCATION`
   - `product_category_name_translation.csv` -> `CATEGORY_TRANSLATION`
5. Repeat for all files.

Validation:
- Confirm all 9 tables exist.
- Confirm each table has non-zero rows.

---

## Step 2: DBT transformations

Planned logical layers:

- **RAW**: manually loaded source tables.
- **STAGING/SILVER**: cleaned types, normalized keys, standardized timestamps.
- **GOLD**: business-ready marts and KPIs.

Suggested first gold outputs:
- Order lifecycle KPI table.
- Customer behavior summary.
- Product/seller performance table.

---

## Step 3: Snowpark + ML

Goal:
- Build a first supervised model (e.g. churn risk or order delay risk).

Expected outputs:
- Feature table in Snowflake.
- Prediction table in Snowflake (versioned by run date/model version).

---

## Step 4: Dataviz

1. Power BI dashboard using gold + prediction tables.
2. Cursor MCP output for narrative analysis and quick reporting.

---

## Notes

- `PUBLIC` schema is acceptable for tests, but `RAW` is cleaner and recommended.
- Airflow/Airbyte materials are archived in Part 1 and should not drive current execution.

---

## Execution Checklist

Use this as the day-to-day tracker.

### Part 2.1 - Manual Snowflake ingest

- [ ] Warehouse created and active.
- [ ] Database created (recommended: `COMPLETEPIPELINE`).
- [ ] Schema created (recommended: `RAW`).
- [ ] Loaded `CUSTOMERS`.
- [ ] Loaded `ORDERS`.
- [ ] Loaded `ORDER_ITEMS`.
- [ ] Loaded `ORDER_PAYMENTS`.
- [ ] Loaded `ORDER_REVIEWS`.
- [ ] Loaded `PRODUCTS`.
- [ ] Loaded `SELLERS`.
- [ ] Loaded `GEOLOCATION`.
- [ ] Loaded `CATEGORY_TRANSLATION`.
- [ ] Validated all 9 tables exist.
- [ ] Validated all loaded tables have non-zero rows.

### Part 2.2 - DBT setup and transformations

- [ ] Initialize DBT project.
- [ ] Configure Snowflake profile/target.
- [ ] Create staging models for all raw tables.
- [ ] Add basic tests (`not_null`, `unique`, `relationships` where applicable).
- [ ] Build first silver models.
- [ ] Build first gold marts.
- [ ] Document models and run `dbt docs generate`.

### Part 2.3 - Snowpark + ML

- [ ] Define first ML target (churn, delay, or other).
- [ ] Build feature table in Snowflake.
- [ ] Train baseline model.
- [ ] Write predictions table in Snowflake.
- [ ] Version model run metadata (date/version/metrics).

### Part 2.4 - Dataviz

- [ ] Build first Power BI report on gold layer.
- [ ] Add prediction view (ML outputs) in Power BI.
- [ ] Generate one Cursor MCP narrative analysis artifact.
- [ ] Publish/export first stakeholder-friendly report.

