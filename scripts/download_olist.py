"""
Download Olist Brazilian E-Commerce dataset into data/raw/olist/.

Requires: pip install kaggle
Configure: place kaggle.json in ~/.kaggle/ (or set KAGGLE_USERNAME / KAGGLE_KEY).

Alternative: download from Kaggle page and extract CSVs to data/raw/olist/.
"""
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DIR = os.path.join(REPO_ROOT, "data", "raw", "olist")
KAGGLE_DATASET = "olistbr/brazilian-ecommerce"

def main():
    os.makedirs(TARGET_DIR, exist_ok=True)
    try:
        subprocess.run(
            ["kaggle", "datasets", "download", "-p", TARGET_DIR, KAGGLE_DATASET, "--unzip"],
            check=True,
            cwd=REPO_ROOT,
        )
        print(f"Downloaded Olist dataset into {TARGET_DIR}")
    except FileNotFoundError:
        print("Kaggle CLI not found. Install: pip install kaggle", file=sys.stderr)
        print("Or download from https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce and extract to", TARGET_DIR, file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print("Kaggle download failed. Check credentials (~/.kaggle/kaggle.json).", file=sys.stderr)
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
