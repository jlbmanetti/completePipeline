"""
Ingestion DAG: upload Olist CSVs to S3, then trigger Airbyte sync (S3 -> Snowflake).

Requires Airflow connections:
  - aws_default: AWS credentials (S3).
  - airbyte_default: Airbyte API (host = server URL; login = client_id; password = client_secret for Cloud/OSS).

Optional Variables:
  - olist_local_path: path to data/raw/olist (default: repo_root/data/raw/olist).
  - s3_bucket, s3_prefix_olist: S3 target.
  - airbyte_connection_id_olist: Airbyte connection UUID (S3 source -> Snowflake destination).
"""
from datetime import datetime
import os

from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.providers.airbyte.operators.airbyte import AirbyteTriggerSyncOperator

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

    trigger_airbyte = AirbyteTriggerSyncOperator(
        task_id="trigger_airbyte_s3_to_snowflake",
        connection_id=Variable.get("airbyte_connection_id_olist", default_var=""),
        airbyte_conn_id="airbyte_default",
        asynchronous=False,
    )

    upload_to_s3 >> trigger_airbyte
