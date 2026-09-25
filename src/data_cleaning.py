"""
Data Cleaning and Transformation Pipeline for Olist E-Commerce Dataset.
Handles missing values, date parsing, categorical standardizations,
geolocation aggregation, and joins across the relational schema.
"""
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Tuple, Dict

from src.config import PROCESSED_DATA_DIR
from src.data_loader import load_all_raw_datasets

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def clean_category_translations(products_df: pd.DataFrame, translations_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge products with translations, fill missing and unmapped categories.
    """
    logger.info("Cleaning product category names and translations...")

    # Custom mapping for unmapped categories in dataset
    manual_translations = {
        "pc_gamer": "gaming_pc",
        "portateis_cozinha_e_preparadores_de_alimentos": "kitchen_food_preparers_small_appliances",
    }

    # Clean translation df
    trans_dict = dict(zip(translations_df['product_category_name'], translations_df['product_category_name_english']))
    trans_dict.update(manual_translations)

    products_clean = products_df.copy()
    products_clean['product_category_name_english'] = products_clean['product_category_name'].map(trans_dict)

    # Impute missing categories
    products_clean['product_category_name_english'] = products_clean['product_category_name_english'].fillna('uncategorized')
    products_clean['product_category_name'] = products_clean['product_category_name'].fillna('nao_especificado')

    # Impute missing dimensions with median
    for col in ['product_name_lenght', 'product_description_lenght', 'product_photos_qty',
                'product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']:
        if col in products_clean.columns:
            median_val = products_clean[col].median()
            products_clean[col] = products_clean[col].fillna(median_val)

    return products_clean


def clean_geolocation(geo_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compress 1M+ geolocation rows to unique zip codes using median coordinates.
    """
    logger.info("Aggregating geolocation data by zip code prefix...")

    # Filter out invalid lat/lng for Brazil bounding box (approx -34 to 6 lat, -74 to -34 lng)
    valid_geo = geo_df[
        (geo_df['geolocation_lat'] >= -35.0) & (geo_df['geolocation_lat'] <= 6.0) &
        (geo_df['geolocation_lng'] >= -75.0) & (geo_df['geolocation_lng'] <= -30.0)
    ].copy()

    geo_agg = valid_geo.groupby('geolocation_zip_code_prefix').agg({
        'geolocation_lat': 'median',
        'geolocation_lng': 'median',
        'geolocation_city': lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0],
        'geolocation_state': lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0]
    }).reset_index()

    return geo_agg


def clean_order_reviews(reviews_df: pd.DataFrame) -> pd.DataFrame:
    """
    Deduplicate reviews (keep latest by answer timestamp per order) and fill text indicators.
    """
    logger.info("Cleaning order reviews...")
    rev = reviews_df.sort_values('review_answer_timestamp').drop_duplicates(subset=['order_id'], keep='last').copy()
    rev['has_comment_title'] = rev['review_comment_title'].notnull().astype(int)
    rev['has_comment_message'] = rev['review_comment_message'].notnull().astype(int)
    rev['comment_message_length'] = rev['review_comment_message'].fillna('').apply(len)
    return rev


def clean_order_payments(payments_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Clean payments and aggregate to order-level summary.
    """
    logger.info("Cleaning and aggregating order payments...")
    pay = payments_df[payments_df['payment_type'] != 'not_defined'].copy()

    # Order level aggregation
    pay_order = pay.groupby('order_id').agg(
        total_payment_value=('payment_value', 'sum'),
        payment_installments_max=('payment_installments', 'max'),
        payment_installments_mean=('payment_installments', 'mean'),
        payment_types_count=('payment_type', 'nunique'),
        primary_payment_type=('payment_type', lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0]),
        payment_sequences_count=('payment_sequential', 'max')
    ).reset_index()

    return pay, pay_order


def build_master_dataset(raw_data: Dict[str, pd.DataFrame] = None) -> pd.DataFrame:
    """
    Executes the entire data cleaning pipeline and constructs the consolidated master analytics table.
    """
    if raw_data is None:
        raw_data = load_all_raw_datasets()

    orders = raw_data['orders'].copy()
    customers = raw_data['customers'].copy()
    order_items = raw_data['order_items'].copy()
    sellers = raw_data['sellers'].copy()

    products_clean = clean_category_translations(raw_data['products'], raw_data['category_translation'])
    geo_clean = clean_geolocation(raw_data['geolocation'])
    reviews_clean = clean_order_reviews(raw_data['order_reviews'])
    payments_clean, payments_order = clean_order_payments(raw_data['order_payments'])

    logger.info("Building consolidated master dataset...")

    # 1. Merge Order Items with Products and Sellers
    items_enriched = order_items.merge(
        products_clean[['product_id', 'product_category_name', 'product_category_name_english',
                        'product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm', 'product_photos_qty']],
        on='product_id',
        how='left'
    ).merge(
        sellers,
        on='seller_id',
        how='left'
    )

    # Add seller geolocation
    items_enriched = items_enriched.merge(
        geo_clean.rename(columns={
            'geolocation_zip_code_prefix': 'seller_zip_code_prefix',
            'geolocation_lat': 'seller_lat',
            'geolocation_lng': 'seller_lng',
            'geolocation_city': 'seller_geo_city',
            'geolocation_state': 'seller_geo_state'
        }),
        on='seller_zip_code_prefix',
        how='left'
    )

    # 2. Merge Orders with Customers
    orders_cust = orders.merge(customers, on='customer_id', how='left')

    # Add customer geolocation
    orders_cust = orders_cust.merge(
        geo_clean.rename(columns={
            'geolocation_zip_code_prefix': 'customer_zip_code_prefix',
            'geolocation_lat': 'customer_lat',
            'geolocation_lng': 'customer_lng',
            'geolocation_city': 'customer_geo_city',
            'geolocation_state': 'customer_geo_state'
        }),
        on='customer_zip_code_prefix',
        how='left'
    )

    # 3. Merge with Reviews and Payment summaries
    orders_full = orders_cust.merge(
        reviews_clean[['order_id', 'review_id', 'review_score', 'has_comment_title',
                       'has_comment_message', 'comment_message_length', 'review_creation_date', 'review_answer_timestamp']],
        on='order_id',
        how='left'
    ).merge(
        payments_order,
        on='order_id',
        how='left'
    )

    # 4. Merge Orders with Items (item-grain master dataset)
    master = items_enriched.merge(orders_full, on='order_id', how='inner')

    # 5. Add Core Delivery & Logistics Metrics
    master['delivery_days'] = (master['order_delivered_customer_date'] - master['order_purchase_timestamp']).dt.total_seconds() / 86400.0
    master['estimated_delivery_days'] = (master['order_estimated_delivery_date'] - master['order_purchase_timestamp']).dt.total_seconds() / 86400.0
    master['delivery_delay_days'] = (master['order_delivered_customer_date'] - master['order_estimated_delivery_date']).dt.total_seconds() / 86400.0
    master['is_late_delivery'] = (master['delivery_delay_days'] > 0).astype(int)
    master['freight_ratio'] = master['freight_value'] / (master['price'] + master['freight_value']).replace(0, np.nan)
    master['is_same_state_shipping'] = (master['seller_state'] == master['customer_state']).astype(int)

    # Order purchase temporal features
    master['purchase_year'] = master['order_purchase_timestamp'].dt.year
    master['purchase_month'] = master['order_purchase_timestamp'].dt.month
    master['purchase_year_month'] = master['order_purchase_timestamp'].dt.to_period('M').astype(str)
    master['purchase_day_name'] = master['order_purchase_timestamp'].dt.day_name()
    master['purchase_day_of_week'] = master['order_purchase_timestamp'].dt.dayofweek
    master['purchase_hour'] = master['order_purchase_timestamp'].dt.hour
    master['purchase_date'] = master['order_purchase_timestamp'].dt.date

    # Save clean datasets
    logger.info(f"Master dataset built with shape: {master.shape}")

    # Save to disk
    master_parquet_path = PROCESSED_DATA_DIR / "master_dataset.parquet"
    master_csv_path = PROCESSED_DATA_DIR / "master_dataset.csv"

    master.to_parquet(master_parquet_path, index=False)
    master.to_csv(master_csv_path, index=False)
    logger.info(f"Saved master dataset to {master_parquet_path} and {master_csv_path}")

    # Also save clean dimensions
    geo_clean.to_parquet(PROCESSED_DATA_DIR / "clean_geolocation.parquet", index=False)
    products_clean.to_parquet(PROCESSED_DATA_DIR / "clean_products.parquet", index=False)
    orders_full.to_parquet(PROCESSED_DATA_DIR / "clean_orders_summary.parquet", index=False)

    return master


if __name__ == "__main__":
    df = build_master_dataset()
    print("Master dataset creation completed successfully.")
