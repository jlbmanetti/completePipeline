"""
Upload Olist CSVs from data/raw/olist/ to S3 (datalake raw layer).

Usage:
  1. Copy .env.example to .env and set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY (and optionally S3_BUCKET).
  2. Run: python scripts/upload_olist_to_s3.py
  Or pass args: python scripts/upload_olist_to_s3.py --bucket completepipeline-raw

No further AWS Console steps after creating the bucket — this script uses your credentials to write to S3.
Airflow DAG uses the same idea but gets credentials from Airflow connection aws_default.
"""
import argparse
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load .env from repo root when running this script locally (so you don't have to export vars)
_env_file = os.path.join(REPO_ROOT, ".env")
if os.path.isfile(_env_file):
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_file)
    except ImportError:
        pass  # run without dotenv: use system env or --bucket
DEFAULT_LOCAL_DIR = os.path.join(REPO_ROOT, "data", "raw", "olist")
DEFAULT_S3_PREFIX = "raw/olist"


def upload_to_s3(bucket: str, prefix: str, local_dir: str) -> None:
    try:
        import boto3
    except ImportError:
        print("boto3 required: pip install boto3", file=sys.stderr)
        sys.exit(1)

    prefix = prefix.rstrip("/")
    client = boto3.client("s3")
    count = 0
    for name in os.listdir(local_dir):
        if not name.endswith(".csv"):
            continue
        path = os.path.join(local_dir, name)
        if not os.path.isfile(path):
            continue
        key = f"{prefix}/{name}"
        client.upload_file(path, bucket, key)
        print(f"Uploaded {path} -> s3://{bucket}/{key}")
        count += 1
    if count == 0:
        print(f"No CSV files in {local_dir}", file=sys.stderr)
        sys.exit(1)
    print(f"Done. Uploaded {count} file(s) to s3://{bucket}/{prefix}/")


def main():
    parser = argparse.ArgumentParser(description="Upload Olist CSVs to S3")
    parser.add_argument("--bucket", default=os.environ.get("S3_BUCKET"), help="S3 bucket name")
    parser.add_argument("--prefix", default=os.environ.get("S3_PREFIX", DEFAULT_S3_PREFIX), help="S3 key prefix")
    parser.add_argument("--local-dir", default=os.environ.get("OLIST_LOCAL_DIR", DEFAULT_LOCAL_DIR), help="Local dir with CSVs")
    args = parser.parse_args()
    if not args.bucket:
        print("Set S3_BUCKET or use --bucket", file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(args.local_dir):
        print(f"Local dir not found: {args.local_dir}", file=sys.stderr)
        sys.exit(1)
    upload_to_s3(args.bucket, args.prefix, args.local_dir)


if __name__ == "__main__":
    main()
