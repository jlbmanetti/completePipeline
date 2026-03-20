# Olist Brazilian E-Commerce — raw landing

Landing zone for the **Brazilian E-Commerce Public Dataset by Olist** (2016–2018, ~100k orders). CSVs are not committed; download or sync them here.

## Source

- **Kaggle:** [olistbr/brazilian-ecommerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- **GitHub (mirror):** [spdrio/Brazilian-E-Commerce-Public-Dataset-by-Olist](https://github.com/spdrio/Brazilian-E-Commerce-Public-Dataset-by-Olist)

## CSV files (place in this folder)

| File | Description |
|------|-------------|
| `olist_customers_dataset.csv` | Customer IDs and location |
| `olist_orders_dataset.csv` | Order id, status, timestamps, delivery |
| `olist_order_items_dataset.csv` | Order line items (product, seller, price, freight) |
| `olist_order_payments_dataset.csv` | Payment type and value per order |
| `olist_order_reviews_dataset.csv` | Review score and comments |
| `olist_products_dataset.csv` | Product id, category, dimensions, weight |
| `olist_sellers_dataset.csv` | Seller id and location |
| `olist_geolocation_dataset.csv` | Zip code → lat/long (BR) |
| `product_category_name_translation.csv` | Category name (PT → EN) |

## How to get the data

1. **Kaggle:** Install [Kaggle API](https://github.com/Kaggle/kaggle-api), then run from repo root:
   ```bash
   python scripts/download_olist.py
   ```
   Or download the dataset from the Kaggle page and extract the CSVs into `data/raw/olist/`.

2. **GitHub:** Clone the mirror repo and copy the CSVs into `data/raw/olist/`:
   ```bash
   git clone https://github.com/spdrio/Brazilian-E-Commerce-Public-Dataset-by-Olist.git _tmp_olist
   copy _tmp_olist\*.csv data\raw\olist\
   ```

Downstream: load manually to Snowflake (UI/SQL), or copy to S3 first using `scripts/upload_olist_to_s3.py`.
