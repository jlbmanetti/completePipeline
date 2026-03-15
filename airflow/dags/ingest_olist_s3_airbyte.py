"""
Ingestion DAG: upload Olist CSVs to S3, then trigger Airbyte sync (S3 -> Snowflake).

Requires Airflow connections:
  - aws_default: AWS credentials (S3).
  - airbyte_default: Host = Airbyte API base URL (e.g. http://host.docker.internal:8000/api/public/v1/).
    Login = Client ID, Password = Client Secret (from Airbyte: User settings → Applications). Required if your Airbyte requires API auth.

Optional Variables:
  - olist_local_path: path to data/raw/olist (default: repo_root/data/raw/olist).
  - s3_bucket, s3_prefix_olist: S3 target.
  - airbyte_connection_id_olist: Airbyte connection UUID (S3 source -> Snowflake destination).
"""
from datetime import datetime
import os
import time

import requests

from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook

# Repo root: airflow/dags -> project root
DAGS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(DAGS_DIR))
DEFAULT_LOCAL_OLIST = os.path.join(REPO_ROOT, "data", "raw", "olist")
DEFAULT_S3_PREFIX = "raw/olist"


def _upload_olist_to_s3(**context):
    """Upload data/raw/olist/*.csv to S3 using Airflow S3Hook."""
    from airflow.providers.amazon.aws.hooks.s3 import S3Hook

    bucket = Variable.get("s3_bucket", default_var="completepipeline-raw")
    prefix = Variable.get("s3_prefix_olist", default_var=DEFAULT_S3_PREFIX).rstrip("/")
    local_dir = Variable.get("olist_local_path", default_var=DEFAULT_LOCAL_OLIST)

    if not os.path.isdir(local_dir):
        raise FileNotFoundError(f"Local Olist dir not found: {local_dir}")

    hook = S3Hook(aws_conn_id="aws_default")
    count = 0
    for name in os.listdir(local_dir):
        if not name.endswith(".csv"):
            continue
        path = os.path.join(local_dir, name)
        if not os.path.isfile(path):
            continue
        key = f"{prefix}/{name}"
        hook.load_file(filename=path, key=key, bucket_name=bucket, replace=True)
        count += 1
    if count == 0:
        raise FileNotFoundError(f"No CSV files in {local_dir}")
    return {"uploaded": count, "bucket": bucket, "prefix": prefix}


def _get_airbyte_headers(conn):
    """Build headers for Airbyte API. If Login/Password (client_id/secret) are set, get a Bearer token."""
    base_url = (conn.host or "").rstrip("/")
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    client_id = (conn.login or "").strip()
    client_secret = conn.password or ""
    if client_id and client_secret:
        token_url = f"{base_url}/applications/token"
        token_payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant-type": "client_credentials",
        }
        r = requests.post(token_url, json=token_payload, headers=headers, timeout=30)
        r.raise_for_status()
        token = r.json().get("access_token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
    return headers


def _trigger_airbyte_sync_and_wait(**context):
    """Trigger an Airbyte connection sync via public API and wait for completion."""
    connection_id = Variable.get("airbyte_connection_id_olist", default_var="")
    if not connection_id:
        raise ValueError("Variable airbyte_connection_id_olist is not set")

    conn = BaseHook.get_connection("airbyte_default")
    base_url = (conn.host or "").rstrip("/")
    if not base_url:
        raise ValueError("airbyte_default connection Host is not set")

    headers = _get_airbyte_headers(conn)

    # POST create job (Airbyte OSS public API); jobType is required
    create_url = f"{base_url}/jobs"
    payload = {"connectionId": connection_id, "jobType": "sync"}
    resp = requests.post(create_url, json=payload, headers=headers, timeout=30)
    if resp.status_code == 401:
        raise RuntimeError(
            "401 Unauthorized from Airbyte API. In Airflow set airbyte_default: "
            "Login = Client ID, Password = Client Secret (from Airbyte: User settings → Applications)."
        )
    if not resp.ok:
        import logging
        logging.getLogger(__name__).error(
            "Airbyte create job failed: status=%s body=%s", resp.status_code, resp.text[:2000]
        )
        resp.raise_for_status()
    data = resp.json()
    # API returns jobId (camelCase) at top level, or nested in "job" as "id"
    job_id = data.get("jobId") or (data.get("job") or {}).get("id") or data.get("id")
    if job_id is None:
        raise RuntimeError(f"Create job response missing job id: {data}")
    job_id = str(job_id)

    # Poll until job completes (match AirbyteTriggerSyncOperator asynchronous=False)
    job_url = f"{base_url}/jobs/{job_id}"
    poll_interval = 10
    max_wait_seconds = 3600
    started = time.monotonic()
    while True:
        if time.monotonic() - started > max_wait_seconds:
            raise RuntimeError(f"Job {job_id} did not finish within {max_wait_seconds}s")
        r = requests.get(job_url, headers=headers, timeout=30)
        r.raise_for_status()
        job = r.json()
        # API may return status at top level or under "job"
        status = (job.get("status") or (job.get("job") or {}).get("status") or "").upper()
        if status in ("SUCCEEDED", "COMPLETED"):
            return {"job_id": job_id, "status": status}
        if status in ("FAILED", "CANCELLED", "ERROR"):
            raise RuntimeError(f"Airbyte job {job_id} finished with status: {status}")
        time.sleep(poll_interval)


with DAG(
    dag_id="ingest_olist_s3_airbyte",
    start_date=datetime(2025, 1, 1),
    schedule=None,  # trigger manually or set e.g. "@daily"
    catchup=False,
    tags=["ingestion", "olist", "s3", "airbyte"],
) as dag:
    upload_to_s3 = PythonOperator(
        task_id="upload_olist_to_s3",
        python_callable=_upload_olist_to_s3,
    )

    trigger_airbyte = PythonOperator(
        task_id="trigger_airbyte_s3_to_snowflake",
        python_callable=_trigger_airbyte_sync_and_wait,
    )

    upload_to_s3 >> trigger_airbyte
