"""
Exploratory Data Analytics and Business Intelligence helper module.
Provides analytical functions for KPIs, temporal trends, product performance,
customer distributions, logistics efficiency, and review sentiment drivers.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from pathlib import Path

from src.config import PROCESSED_DATA_DIR


def load_master_dataset() -> pd.DataFrame:
    """Loads the processed master dataset from parquet."""
    path = PROCESSED_DATA_DIR / "master_dataset.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Master dataset not found at {path}")
    return pd.read_parquet(path)


def get_executive_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes top-level executive KPIs.
    """
    delivered = df[df['order_status'] == 'delivered']

    total_revenue = delivered['price'].sum()
    total_freight = delivered['freight_value'].sum()
    total_gmv = total_revenue + total_freight

    total_orders = delivered['order_id'].nunique()
    total_items = len(delivered)
    total_unique_customers = delivered['customer_unique_id'].nunique()
    total_sellers = delivered['seller_id'].nunique()

    avg_order_value = total_revenue / total_orders if total_orders else 0
    avg_items_per_order = total_items / total_orders if total_orders else 0
    avg_freight_per_order = total_freight / total_orders if total_orders else 0

    avg_delivery_days = delivered['delivery_days'].mean()
    median_delivery_days = delivered['delivery_days'].median()
    late_delivery_rate = (delivered['is_late_delivery'].sum() / len(delivered)) * 100

    avg_review_score = delivered['review_score'].mean()
    positive_review_rate = (delivered['review_score'] >= 4).sum() / delivered['review_score'].notnull().sum() * 100

    repeat_customers = (delivered.groupby('customer_unique_id')['order_id'].nunique() > 1).sum()
    repeat_customer_rate = (repeat_customers / total_unique_customers) * 100

    return {
        "total_revenue": total_revenue,
        "total_freight": total_freight,
        "total_gmv": total_gmv,
        "total_orders": total_orders,
        "total_items": total_items,
        "total_unique_customers": total_unique_customers,
        "total_sellers": total_sellers,
        "avg_order_value": avg_order_value,
        "avg_items_per_order": avg_items_per_order,
        "avg_freight_per_order": avg_freight_per_order,
        "avg_delivery_days": avg_delivery_days,
        "median_delivery_days": median_delivery_days,
        "late_delivery_rate": late_delivery_rate,
        "avg_review_score": avg_review_score,
        "positive_review_rate": positive_review_rate,
        "repeat_customers_count": repeat_customers,
        "repeat_customer_rate": repeat_customer_rate
    }


def get_monthly_sales_trend(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes monthly sales, revenue, order count, and average order value.
    """
    valid = df[df['order_status'] == 'delivered'].copy()
    monthly = valid.groupby('purchase_year_month').agg(
        revenue=('price', 'sum'),
        freight=('freight_value', 'sum'),
        total_gmv=('total_payment_value', 'sum'),
        orders=('order_id', 'nunique'),
        items_sold=('order_item_id', 'count'),
        avg_delivery_days=('delivery_days', 'mean'),
        avg_review_score=('review_score', 'mean')
    ).reset_index()

    monthly['aov'] = monthly['revenue'] / monthly['orders']
    monthly['revenue_growth_pct'] = monthly['revenue'].pct_change() * 100
    return monthly


def get_day_and_hour_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes order intensity matrix by Day of Week and Hour of Day.
    """
    valid = df.drop_duplicates(subset=['order_id']).copy()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap = valid.groupby(['purchase_day_name', 'purchase_hour'])['order_id'].count().reset_index()
    matrix = heatmap.pivot(index='purchase_day_name', columns='purchase_hour', values='order_id').reindex(day_order)
    return matrix


def get_top_categories(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Returns top N product categories by revenue and order count.
    """
    valid = df[df['order_status'] == 'delivered']
    cat = valid.groupby('product_category_name_english').agg(
        revenue=('price', 'sum'),
        orders=('order_id', 'nunique'),
        items_sold=('order_item_id', 'count'),
        avg_price=('price', 'mean'),
        avg_review_score=('review_score', 'mean')
    ).reset_index()
    return cat.sort_values('revenue', ascending=False).head(top_n)


def get_payment_method_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyzes payment types, transaction volume, value, and installment behavior.
    """
    valid = df.drop_duplicates(subset=['order_id']).copy()
    pay_summary = valid.groupby('primary_payment_type').agg(
        total_orders=('order_id', 'nunique'),
        total_value=('total_payment_value', 'sum'),
        avg_installments=('payment_installments_mean', 'mean'),
        max_installments=('payment_installments_max', 'max')
    ).reset_index()

    pay_summary['orders_share_pct'] = (pay_summary['total_orders'] / pay_summary['total_orders'].sum()) * 100
    pay_summary['value_share_pct'] = (pay_summary['total_value'] / pay_summary['total_value'].sum()) * 100
    pay_summary['avg_ticket_size'] = pay_summary['total_value'] / pay_summary['total_orders']

    return pay_summary.sort_values('total_value', ascending=False)


def get_review_score_drivers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyzes drivers of customer review scores (delivery latency, freight ratio, price).
    """
    valid = df[df['order_status'] == 'delivered'].copy()

    drivers = valid.groupby('review_score').agg(
        order_count=('order_id', 'nunique'),
        avg_delivery_days=('delivery_days', 'mean'),
        avg_estimated_days=('estimated_delivery_days', 'mean'),
        avg_delay_days=('delivery_delay_days', 'mean'),
        late_delivery_rate=('is_late_delivery', lambda x: x.mean() * 100),
        avg_freight_ratio=('freight_ratio', lambda x: x.mean() * 100),
        avg_price=('price', 'mean'),
        has_comment_pct=('has_comment_message', lambda x: x.mean() * 100)
    ).reset_index()

    return drivers


if __name__ == "__main__":
    df = load_master_dataset()
    kpis = get_executive_kpis(df)
    print("Executive KPIs:")
    for k, v in kpis.items():
        print(f"  {k}: {v:,.2f}" if isinstance(v, float) else f"  {k}: {v:,}")
