"""
Feature Engineering module for Brazilian E-Commerce Analytics.
Calculates RFM Segmentation, Cohort Retention Matrices, Seller Tiers,
Logistics Efficiency, and Category Performance metrics.
"""
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Tuple, Dict

from src.config import PROCESSED_DATA_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def compute_rfm_segments(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes Recency, Frequency, and Monetary (RFM) metrics per customer_unique_id.
    Assigns granular customer segment labels.
    """
    logger.info("Calculating RFM Metrics and Customer Segmentation...")

    # Filter for delivered orders to represent realized revenue
    valid_orders = df[df['order_status'] == 'delivered'].copy()

    # Reference snapshot date (1 day after max date in dataset)
    snapshot_date = valid_orders['order_purchase_timestamp'].max() + pd.Timedelta(days=1)

    # Customer level aggregation
    rfm = valid_orders.groupby('customer_unique_id').agg(
        recency=('order_purchase_timestamp', lambda x: (snapshot_date - x.max()).days),
        frequency=('order_id', 'nunique'),
        monetary=('price', 'sum'),
        total_freight=('freight_value', 'sum'),
        items_bought=('order_item_id', 'count'),
        avg_review_score=('review_score', 'mean'),
        first_purchase=('order_purchase_timestamp', 'min'),
        last_purchase=('order_purchase_timestamp', 'max'),
        customer_state=('customer_state', lambda x: x.iloc[0]),
        customer_city=('customer_city', lambda x: x.iloc[0])
    ).reset_index()

    # Add total order spend including freight
    rfm['total_spend'] = rfm['monetary'] + rfm['total_freight']

    # 1. Recency Score: 5 is best (most recent), 1 is worst (oldest)
    rfm['r_score'] = pd.qcut(rfm['recency'], q=5, labels=[5, 4, 3, 2, 1]).astype(int)

    # 2. Frequency Score: Since e-commerce has high 1-time buyers, we use custom thresholds
    # 1 order -> 1, 2 orders -> 3, 3+ orders -> 5
    def score_frequency(freq):
        if freq == 1:
            return 1
        elif freq == 2:
            return 3
        elif freq == 3:
            return 4
        else:
            return 5

    rfm['f_score'] = rfm['frequency'].apply(score_frequency)

    # 3. Monetary Score: 5 is best (highest spend), 1 is lowest
    rfm['m_score'] = pd.qcut(rfm['total_spend'], q=5, labels=[1, 2, 3, 4, 5]).astype(int)

    # Combined RFM Score string
    rfm['rfm_score'] = rfm['r_score'].astype(str) + rfm['f_score'].astype(str) + rfm['m_score'].astype(str)
    rfm['rfm_sum'] = rfm['r_score'] + rfm['f_score'] + rfm['m_score']

    # Customer Segment Tagging Strategy
    def assign_segment(row):
        r, f, m = row['r_score'], row['f_score'], row['m_score']

        if r >= 4 and f >= 3 and m >= 4:
            return "Champions"
        elif r >= 3 and f >= 2 and m >= 3:
            return "Loyal Customers"
        elif r >= 4 and f <= 2 and m >= 3:
            return "High-Value New/Recent"
        elif r >= 4 and f <= 2 and m <= 2:
            return "New Active Customers"
        elif r == 3 and f >= 2:
            return "Potential Loyalists"
        elif r == 3 and f == 1:
            return "Promising Customers"
        elif r == 2 and f >= 2:
            return "At Risk"
        elif r == 2 and f == 1:
            return "Need Attention / Cooling"
        elif r == 1 and (f >= 2 or m >= 4):
            return "Can't Lose Them / Inactive VIP"
        else:
            return "Hibernating / Lost"

    rfm['customer_segment'] = rfm.apply(assign_segment, axis=1)

    # Save to processed
    rfm_path = PROCESSED_DATA_DIR / "rfm_customer_segments.parquet"
    rfm.to_parquet(rfm_path, index=False)
    logger.info(f"RFM segmentation saved: {rfm.shape} -> {rfm_path}")

    return rfm


def compute_cohort_retention(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Computes monthly cohort retention count and percentage matrices.
    """
    logger.info("Calculating Monthly Cohort Retention Analysis...")

    valid = df[df['order_status'] == 'delivered'].copy()

    # Determine customer's first purchase month (CohortMonth)
    valid['order_month'] = valid['order_purchase_timestamp'].dt.to_period('M')
    cohort_df = valid.groupby('customer_unique_id')['order_month'].min().reset_index()
    cohort_df.columns = ['customer_unique_id', 'cohort_month']

    merged = valid.merge(cohort_df, on='customer_unique_id', how='left')

    # Calculate Cohort Index (integer number of months between order and cohort start)
    merged['cohort_year'] = merged['cohort_month'].apply(lambda x: x.year)
    merged['cohort_month_num'] = merged['cohort_month'].apply(lambda x: x.month)
    merged['order_year'] = merged['order_month'].apply(lambda x: x.year)
    merged['order_month_num'] = merged['order_month'].apply(lambda x: x.month)

    merged['cohort_index'] = (
        (merged['order_year'] - merged['cohort_year']) * 12 +
        (merged['order_month_num'] - merged['cohort_month_num'])
    )

    # Build Cohort Count Matrix (Unique customers per cohort and month index)
    cohort_counts = merged.groupby(['cohort_month', 'cohort_index'])['customer_unique_id'].nunique().reset_index()
    cohort_matrix = cohort_counts.pivot(index='cohort_month', columns='cohort_index', values='customer_unique_id')

    # Convert period index to string for serialization
    cohort_matrix.index = cohort_matrix.index.astype(str)

    # Calculate Retention Percentage Matrix
    cohort_size = cohort_matrix.iloc[:, 0]
    retention_matrix = cohort_matrix.divide(cohort_size, axis=0) * 100

    # Save to parquet / csv
    cohort_matrix.to_parquet(PROCESSED_DATA_DIR / "cohort_counts_matrix.parquet")
    retention_matrix.to_parquet(PROCESSED_DATA_DIR / "cohort_retention_matrix.parquet")

    logger.info("Cohort matrices saved successfully.")
    return cohort_matrix, retention_matrix


def compute_seller_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes seller-level performance KPIs, Pareto distribution, and tiering.
    """
    logger.info("Calculating Seller Performance Metrics...")

    valid = df[df['order_status'] == 'delivered'].copy()

    seller_kpis = valid.groupby('seller_id').agg(
        total_revenue=('price', 'sum'),
        total_freight=('freight_value', 'sum'),
        items_sold=('order_item_id', 'count'),
        unique_orders=('order_id', 'nunique'),
        avg_item_price=('price', 'mean'),
        avg_review_score=('review_score', 'mean'),
        avg_delivery_days=('delivery_days', 'mean'),
        late_delivery_count=('is_late_delivery', 'sum'),
        seller_state=('seller_state', lambda x: x.iloc[0]),
        seller_city=('seller_city', lambda x: x.iloc[0]),
        first_sale=('order_purchase_timestamp', 'min'),
        last_sale=('order_purchase_timestamp', 'max')
    ).reset_index()

    seller_kpis['late_delivery_rate'] = (seller_kpis['late_delivery_count'] / seller_kpis['items_sold']) * 100
    seller_kpis['on_time_delivery_rate'] = 100 - seller_kpis['late_delivery_rate']

    # Pareto 80/20 Analysis (Cumulative Revenue Share)
    seller_kpis = seller_kpis.sort_values('total_revenue', ascending=False).reset_index(drop=True)
    seller_kpis['cumulative_revenue'] = seller_kpis['total_revenue'].cumsum()
    seller_kpis['cumulative_revenue_pct'] = (seller_kpis['cumulative_revenue'] / seller_kpis['total_revenue'].sum()) * 100
    seller_kpis['seller_rank'] = np.arange(1, len(seller_kpis) + 1)
    seller_kpis['seller_pct'] = (seller_kpis['seller_rank'] / len(seller_kpis)) * 100

    # Seller Tiering
    def assign_seller_tier(row):
        rev = row['total_revenue']
        score = row['avg_review_score']
        if rev >= 50000 and score >= 4.0:
            return "Tier 1 - Powerhouse"
        elif rev >= 15000 and score >= 3.8:
            return "Tier 2 - Growth Partner"
        elif rev >= 3000:
            return "Tier 3 - Established"
        elif score < 3.5:
            return "Tier 4 - Quality Risk"
        else:
            return "Tier 5 - Emerging / Long Tail"

    seller_kpis['seller_tier'] = seller_kpis.apply(assign_seller_tier, axis=1)

    seller_kpis.to_parquet(PROCESSED_DATA_DIR / "seller_performance.parquet", index=False)
    logger.info(f"Seller performance saved: {seller_kpis.shape}")
    return seller_kpis


def compute_category_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes category performance metrics, average price, review score, and fulfillment metrics.
    """
    logger.info("Calculating Product Category Performance Metrics...")

    cat_kpis = df.groupby('product_category_name_english').agg(
        total_revenue=('price', 'sum'),
        total_freight=('freight_value', 'sum'),
        items_sold=('order_item_id', 'count'),
        unique_orders=('order_id', 'nunique'),
        unique_sellers=('seller_id', 'nunique'),
        unique_products=('product_id', 'nunique'),
        avg_price=('price', 'mean'),
        median_price=('price', 'median'),
        avg_freight=('freight_value', 'mean'),
        avg_review_score=('review_score', 'mean'),
        avg_delivery_days=('delivery_days', 'mean'),
        late_delivery_count=('is_late_delivery', 'sum'),
        total_canceled=('order_status', lambda x: (x == 'canceled').sum())
    ).reset_index()

    cat_kpis['freight_to_price_ratio'] = (cat_kpis['total_freight'] / (cat_kpis['total_revenue'] + cat_kpis['total_freight'])) * 100
    cat_kpis['late_delivery_rate'] = (cat_kpis['late_delivery_count'] / cat_kpis['items_sold']) * 100
    cat_kpis['cancellation_rate'] = (cat_kpis['total_canceled'] / cat_kpis['items_sold']) * 100

    cat_kpis = cat_kpis.sort_values('total_revenue', ascending=False).reset_index(drop=True)
    cat_kpis.to_parquet(PROCESSED_DATA_DIR / "category_metrics.parquet", index=False)
    logger.info(f"Category metrics saved: {cat_kpis.shape}")
    return cat_kpis


def compute_logistics_metrics(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Computes State-level and Route-level delivery latency, freight costs, and delays.
    """
    logger.info("Calculating Logistics & Supply Chain Metrics...")

    valid = df[df['order_status'] == 'delivered'].copy()

    # 1. State-level destination metrics
    state_kpis = valid.groupby('customer_state').agg(
        total_orders=('order_id', 'nunique'),
        total_revenue=('price', 'sum'),
        total_freight=('freight_value', 'sum'),
        avg_delivery_days=('delivery_days', 'mean'),
        median_delivery_days=('delivery_days', 'median'),
        avg_estimated_days=('estimated_delivery_days', 'mean'),
        avg_delay_days=('delivery_delay_days', 'mean'),
        late_orders=('is_late_delivery', 'sum'),
        avg_review_score=('review_score', 'mean')
    ).reset_index()

    state_kpis['late_delivery_pct'] = (state_kpis['late_orders'] / state_kpis['total_orders']) * 100
    state_kpis['avg_freight_per_order'] = state_kpis['total_freight'] / state_kpis['total_orders']
    state_kpis = state_kpis.sort_values('total_orders', ascending=False).reset_index(drop=True)

    # 2. Route-level origin-destination metrics
    route_kpis = valid.groupby(['seller_state', 'customer_state']).agg(
        route_orders=('order_id', 'nunique'),
        avg_delivery_days=('delivery_days', 'mean'),
        avg_freight=('freight_value', 'mean'),
        late_orders=('is_late_delivery', 'sum')
    ).reset_index()
    route_kpis['late_rate'] = (route_kpis['late_orders'] / route_kpis['route_orders']) * 100

    state_kpis.to_parquet(PROCESSED_DATA_DIR / "logistics_state_metrics.parquet", index=False)
    route_kpis.to_parquet(PROCESSED_DATA_DIR / "logistics_route_metrics.parquet", index=False)

    logger.info("Logistics metrics saved successfully.")
    return state_kpis, route_kpis


def run_all_feature_engineering():
    """
    Runs full feature engineering pipeline on the master dataset.
    """
    master_path = PROCESSED_DATA_DIR / "master_dataset.parquet"
    if not master_path.exists():
        raise FileNotFoundError(f"Master dataset not found at {master_path}. Run data_cleaning first.")

    logger.info("Loading master dataset for feature engineering...")
    df = pd.read_parquet(master_path)

    rfm = compute_rfm_segments(df)
    cohort_matrix, retention_matrix = compute_cohort_retention(df)
    sellers = compute_seller_performance(df)
    categories = compute_category_metrics(df)
    states, routes = compute_logistics_metrics(df)

    logger.info("All feature engineering tasks completed successfully!")


if __name__ == "__main__":
    run_all_feature_engineering()
