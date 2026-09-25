"""
Configuration module for Olist Brazilian E-Commerce Analytics Project.
Defines paths, constants, and settings used across the analytical pipeline.
"""
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
REPORTS_DIR = BASE_DIR / "reports"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"
APP_DIR = BASE_DIR / "app"

# Ensure directories exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, REPORTS_DIR, NOTEBOOKS_DIR, APP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Raw Data Filenames
FILES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

# Date Columns per dataset
DATE_COLUMNS = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "order_items": ["shipping_limit_date"],
    "order_reviews": ["review_creation_date", "review_answer_timestamp"],
}

# RFM Quantile Segments Mapping
RFM_SEGMENT_MAP = {
    r"[4-5][4-5][4-5]": "Champions",
    r"[2-5][3-5][3-5]": "Loyal Customers",
    r"[3-5][1-3][1-3]": "Potential Loyalists",
    r"[4-5][1-2][1-2]": "Recent Customers",
    r"[3-4][1-2][1-2]": "Promising",
    r"[2-3][2-3][2-3]": "Customers Needing Attention",
    r"[2-3][1-2][1-2]": "About to Sleep",
    r"[1-2][2-5][2-5]": "At Risk",
    r"[1-2][1-2][3-5]": "Can't Lose Them",
    r"[1-2][1-2][1-2]": "Hibernating",
    r"[1-2][1-2][1]": "Lost",
}
