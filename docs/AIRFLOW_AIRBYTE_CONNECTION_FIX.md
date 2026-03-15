# Fix: Airflow cannot trigger Airbyte (task trigger_airbyte_s3_to_snowflake fails)

If the second task in the DAG **trigger_airbyte_s3_to_snowflake** is red (failed), check the following.

**Note:** This project uses a **custom trigger** that supports OAuth. If you get **401 Unauthorized**, set **Login** = Client ID and **Password** = Client Secret in the `airbyte_default` connection (from Airbyte: **User → User settings → Applications**).

---

## 1. Fix the Host URL (required)

The Airflow Airbyte provider expects the **full API base URL**, not just the server root.

1. In **Airflow** go to **Admin → Connections**.
2. Find **airbyte_default** and click **Edit** (pencil).
3. Set **Host** to exactly:
   ```text
   http://host.docker.internal:8000/api/public/v1/
   ```
   (Include the trailing slash. Use `host.docker.internal` so the Airflow container can reach Airbyte on your PC.)
4. Click **Save**.

Then **clear** the failed task and re-run the DAG (or trigger a new run):

- Open the DAG **ingest_olist_s3_airbyte** → **Grid** → click the failed run.
- Click the failed task **trigger_airbyte_s3_to_snowflake** → **Clear** (and clear downstream if asked).
- Trigger the DAG again, or wait for the cleared task to run.

---

## 2. If you get 401 Unauthorized: set API credentials

Your Airbyte instance requires API authentication. In the DAG we obtain a token from your Client ID and Client Secret.

1. In **Airbyte** go to **User** (top right) → **User settings** → **Applications**.
2. Create an application (or use the default one in Airbyte Core) and copy the **Client ID** and **Client Secret** (click the icon to reveal the secret).
3. In **Airflow** → **Admin → Connections** → edit **airbyte_default**.
4. Set **Login** = Client ID, **Password** = Client Secret. Save.
5. Clear the failed task and trigger the DAG again.

---

## 3. Check from the Airflow container (optional)

To confirm the container can reach Airbyte:

```powershell
docker compose -f docker-compose.airflow.yaml exec airflow-scheduler curl -s -o NUL -w "%{http_code}" http://host.docker.internal:8000/api/public/v1/health
```

A `200` response means the host and path are reachable.

---

## Summary

| What | Value |
|------|--------|
| **Host** (required) | `http://host.docker.internal:8000/api/public/v1/` |
| **Login** | Client ID (from Airbyte: User settings → Applications) |
| **Password** | Client Secret (same place) |

After updating the connection, clear the failed task and trigger the DAG again.
