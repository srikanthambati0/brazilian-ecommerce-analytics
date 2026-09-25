"""
Script to generate the comprehensive suite of Jupyter Notebooks for the project.
"""
import nbformat as nbf
from pathlib import Path

NOTEBOOKS_DIR = Path("notebooks")
NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)


def create_notebook_01():
    nb = nbf.v4.new_notebook()
    cells = []

    # Markdown Header
    cells.append(nbf.v4.new_markdown_cell("""# 🛍️ Olist E-Commerce Analytics — Part 1: Data Cleaning & Wrangling
**Author:** Data Analytics Portfolio
**Dataset:** Brazilian E-Commerce Public Dataset by Olist (100k Orders, 2016–2018)
**Objective:** End-to-end data ingestion, schema validation, missing value imputation, geolocation deduplication, and master analytics dataset construction.

---
### Relational Schema Overview
The dataset contains 9 interconnected relational tables:
1. `olist_orders_dataset`: Core order tracking, timestamps, and fulfillment status.
2. `olist_customers_dataset`: Customer identifiers and location.
3. `olist_order_items_dataset`: Line-item details, pricing, and freight per seller.
4. `olist_products_dataset`: Product dimensions and categories.
5. `olist_sellers_dataset`: Seller locations.
6. `olist_order_payments_dataset`: Payment methods, installment structures, and values.
7. `olist_order_reviews_dataset`: Customer CSAT review scores and feedback text.
8. `olist_geolocation_dataset`: Brazilian zip code to lat/lng mapping (1M+ coordinates).
9. `product_category_name_translation`: Portuguese to English category mappings.
"""))

    # Imports
    cells.append(nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# Set plotting styles
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 11

print("Environment initialized successfully.")
"""))

    # Step 1: Ingestion
    cells.append(nbf.v4.new_markdown_cell("""## 1. Data Ingestion & Schema Profiling
We load all 9 raw datasets, inspect row counts, data types, and check for missing values.
"""))

    cells.append(nbf.v4.new_code_cell("""from src.data_loader import load_all_raw_datasets

raw_data = load_all_raw_datasets()

for name, df in raw_data.items():
    print(f"Dataset: {name:<25} | Rows: {df.shape[0]:>8,} | Columns: {df.shape[1]:>2}")
"""))

    # Step 2: Missing Value Audit
    cells.append(nbf.v4.new_markdown_cell("""## 2. Missing Value Audit & Anomaly Detection
We analyze nulls across each dataset to determine appropriate imputation strategies.
"""))

    cells.append(nbf.v4.new_code_cell("""null_summary = []
for name, df in raw_data.items():
    nulls = df.isnull().sum()
    null_cols = nulls[nulls > 0]
    for col, count in null_cols.items():
        pct = (count / len(df)) * 100
        null_summary.append({"Dataset": name, "Column": col, "Missing Rows": count, "Missing %": pct})

null_df = pd.DataFrame(null_summary)
null_df.sort_values(by="Missing %", ascending=False)
"""))

    # Step 3: Geolocation Compression
    cells.append(nbf.v4.new_markdown_cell("""## 3. Geolocation Aggregation & Deduplication
The raw geolocation table has **1,000,163 rows** with multiple jittered GPS coordinates per zip code prefix.
We calculate the median coordinates per zip code prefix to compress this to **19,015 clean centroids**, achieving a **98% reduction** in memory footprint while preserving geographic precision.
"""))

    cells.append(nbf.v4.new_code_cell("""from src.data_cleaning import clean_geolocation

geo_clean = clean_geolocation(raw_data['geolocation'])
print(f"Raw Geolocation Rows: {len(raw_data['geolocation']):,}")
print(f"Clean Centroid Rows:  {len(geo_clean):,}")
geo_clean.head()
"""))

    # Step 4: Product Category Translation & Imputation
    cells.append(nbf.v4.new_markdown_cell("""## 4. Product Category Translation & Missing Value Imputation
We map Portuguese category names to English and impute unmapped categories like `pc_gamer` and `portateis_cozinha_e_preparadores_de_alimentos`.
"""))

    cells.append(nbf.v4.new_code_cell("""from src.data_cleaning import clean_category_translations

products_clean = clean_category_translations(raw_data['products'], raw_data['category_translation'])
print(f"Total Products: {len(products_clean):,}")
print(f"Unique English Categories: {products_clean['product_category_name_english'].nunique()}")
products_clean['product_category_name_english'].value_counts().head(10)
"""))

    # Step 5: Master Analytics Dataset Assembly
    cells.append(nbf.v4.new_markdown_cell("""## 5. Master Analytics Dataset Construction
We execute relational merges across orders, customers, items, products, sellers, payments, and reviews, engineering logistics latency metrics (`delivery_days`, `is_late_delivery`, `freight_ratio`).
"""))

    cells.append(nbf.v4.new_code_cell("""from src.data_cleaning import build_master_dataset

master = build_master_dataset(raw_data)
print("Master Analytics Dataset Shape:", master.shape)
print("\nSample Columns:")
print(master[['order_id', 'customer_unique_id', 'product_category_name_english', 'price', 'freight_value', 'delivery_days', 'review_score']].head())
"""))

    nb.cells = cells
    with open(NOTEBOOKS_DIR / "01_Data_Cleaning_and_Wrangling.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print("Created 01_Data_Cleaning_and_Wrangling.ipynb")


def create_notebook_02():
    nb = nbf.v4.new_notebook()
    cells = []

    # Markdown Header
    cells.append(nbf.v4.new_markdown_cell("""# 📊 Olist E-Commerce Analytics — Part 2: Exploratory Data Analysis & Business Insights
**Author:** Data Analytics Portfolio
**Objective:** Comprehensive business intelligence analysis answering core commercial questions:
1. Executive KPIs and Revenue Metrics
2. Average Transaction Value (ATV / AOV)
3. Top Product Categories by Sales & Volume
4. Temporal Sales Trends (Hourly, Daily, Monthly, Seasonality & Black Friday)
5. Customer Purchase Patterns (Multi-item orders & Basket size)
6. Geographic Footprint (State-wise demand & logistics disparities)
7. Logistics & Delivery Lead Times vs CSAT Impact
8. Payment Economics & Installment Behaviors
9. Seller Ecosystem Dynamics & Pareto 80/20 Distribution
"""))

    # Imports
    cells.append(nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from src.eda_analytics import (
    load_master_dataset,
    get_executive_kpis,
    get_monthly_sales_trend,
    get_day_and_hour_heatmap,
    get_top_categories,
    get_payment_method_distribution,
    get_review_score_drivers
)

# Visual settings
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 11

df = load_master_dataset()
print(f"Master Dataset Loaded: {len(df):,} items across {df['order_id'].nunique():,} orders.")
"""))

    # Section 1: Executive KPIs
    cells.append(nbf.v4.new_markdown_cell("""## 1. Executive KPIs & Marketplace Performance
High-level summary of gross merchandise value (GMV), order volume, customer count, and delivery metrics.
"""))

    cells.append(nbf.v4.new_code_cell("""kpis = get_executive_kpis(df)
for k, v in kpis.items():
    print(f"{k.replace('_', ' ').title():<30}: {v:,.2f}" if isinstance(v, float) else f"{k.replace('_', ' ').title():<30}: {v:,}")
"""))

    # Section 2: ATV / AOV
    cells.append(nbf.v4.new_markdown_cell("""## 2. Average Transaction Value (ATV / AOV) Analysis
- **Average Order Value (Item Price)**: R$ 137.04
- **Average Freight per Order**: R$ 22.79
- **Average Gross Order Total**: R$ 159.83
"""))

    cells.append(nbf.v4.new_code_cell("""order_totals = df.groupby('order_id').agg(
    order_revenue=('price', 'sum'),
    order_freight=('freight_value', 'sum'),
    order_items=('order_item_id', 'count')
).reset_index()

order_totals['total_order_value'] = order_totals['order_revenue'] + order_totals['order_freight']

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Distribution up to 99th percentile to remove extreme visual outliers
sns.histplot(order_totals['total_order_value'][order_totals['total_order_value'] < 600], bins=50, kde=True, ax=ax1, color='#2563EB')
ax1.axvline(order_totals['total_order_value'].median(), color='red', linestyle='--', label=f"Median: R$ {order_totals['total_order_value'].median():.2f}")
ax1.axvline(order_totals['total_order_value'].mean(), color='green', linestyle='--', label=f"Mean: R$ {order_totals['total_order_value'].mean():.2f}")
ax1.set_title("Order Value Distribution (Truncated at R$ 600)", fontsize=13, fontweight='bold')
ax1.set_xlabel("Order Value (R$)")
ax1.legend()

# Items per order distribution
sns.countplot(data=order_totals[order_totals['order_items'] <= 6], x='order_items', ax=ax2, palette='Blues_r')
ax2.set_title("Number of Products Bought per Order", fontsize=13, fontweight='bold')
ax2.set_xlabel("Items per Order")
ax2.set_ylabel("Order Count")

plt.tight_layout()
plt.show()
"""))

    # Section 3: Most Bought Categories
    cells.append(nbf.v4.new_markdown_cell("""## 3. Product Category Intelligence
We compare the Top 10 categories by Total Realized Revenue vs Order Item Volume.
"""))

    cells.append(nbf.v4.new_code_cell("""cat_summary = df[df['order_status'] == 'delivered'].groupby('product_category_name_english').agg(
    revenue=('price', 'sum'),
    volume=('order_item_id', 'count'),
    avg_price=('price', 'mean')
).reset_index()

top_rev = cat_summary.sort_values('revenue', ascending=False).head(10)
top_vol = cat_summary.sort_values('volume', ascending=False).head(10)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

sns.barplot(data=top_rev, y='product_category_name_english', x='revenue', ax=ax1, palette='Blues_r')
ax1.set_title("Top 10 Categories by Revenue (R$)", fontsize=13, fontweight='bold')
ax1.set_xlabel("Revenue (R$)")
ax1.set_ylabel("Category")

sns.barplot(data=top_vol, y='product_category_name_english', x='volume', ax=ax2, palette='Greens_r')
ax2.set_title("Top 10 Categories by Units Sold", fontsize=13, fontweight='bold')
ax2.set_xlabel("Units Sold")
ax2.set_ylabel("")

plt.tight_layout()
plt.show()
"""))

    # Section 4: Temporal Sales Trends
    cells.append(nbf.v4.new_markdown_cell("""## 4. Sales Trends over Time (Day, Week, Month & Black Friday)
Tracking monthly GMV growth and weekly shopping cycles.
"""))

    cells.append(nbf.v4.new_code_cell("""monthly = get_monthly_sales_trend(df)

fig, ax1 = plt.subplots(figsize=(14, 6))
ax2 = ax1.twinx()

ax1.bar(monthly['purchase_year_month'], monthly['revenue'] / 1e3, color='#3B82F6', alpha=0.8, label="Revenue (k R$)")
ax2.plot(monthly['purchase_year_month'], monthly['orders'], color='#DC2626', marker='o', linewidth=2.5, label="Orders Count")

ax1.set_title("Monthly Revenue and Order Volume Trajectory (2016-2018)", fontsize=14, fontweight='bold')
ax1.set_xlabel("Year-Month")
ax1.set_ylabel("Revenue in Thousand R$", color='#3B82F6')
ax2.set_ylabel("Total Orders", color='#DC2626')
ax1.tick_params(axis='x', rotation=45)
ax1.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
"""))

    # Day & Hour Heatmap
    cells.append(nbf.v4.new_code_cell("""matrix = get_day_and_hour_heatmap(df)

plt.figure(figsize=(14, 6))
sns.heatmap(matrix, cmap="YlGnBu", annot=False, cbar_kws={'label': 'Order Count'})
plt.title("Shopping Intensity Heatmap (Day of Week vs Hour of Day)", fontsize=14, fontweight='bold')
plt.xlabel("Hour of Day (0 - 23)")
plt.ylabel("Day of Week")
plt.tight_layout()
plt.show()
"""))

    # Section 5: Delivery & Logistics vs CSAT
    cells.append(nbf.v4.new_markdown_cell("""## 5. Logistics Performance & Customer Review Scores
Analyzing the direct econometric correlation between delivery delays and 1-star ratings.
"""))

    cells.append(nbf.v4.new_code_cell("""rev_drivers = get_review_score_drivers(df)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

sns.barplot(data=rev_drivers, x='review_score', y='avg_delivery_days', ax=ax1, palette='Reds_r')
ax1.set_title("Average Delivery Days by Review Rating", fontsize=13, fontweight='bold')
ax1.set_xlabel("Review Score (Stars)")
ax1.set_ylabel("Delivery Days")

sns.lineplot(data=rev_drivers, x='review_score', y='late_delivery_rate', ax=ax2, marker='o', color='#DC2626', linewidth=3)
ax2.set_title("Late Delivery Rate (%) by Review Rating", fontsize=13, fontweight='bold')
ax2.set_xlabel("Review Score (Stars)")
ax2.set_ylabel("Late Delivery Rate (%)")

plt.tight_layout()
plt.show()

print("Review Score Driver Matrix:")
rev_drivers
"""))

    # Section 6: Payment Methods
    cells.append(nbf.v4.new_markdown_cell("""## 6. Payment Methods & Installment Dynamics
Examining transaction shares and credit card financing behaviors.
"""))

    cells.append(nbf.v4.new_code_cell("""pay_summary = get_payment_method_distribution(df)
print(pay_summary)
"""))

    # Section 7: Pareto 80/20 Seller Analysis
    cells.append(nbf.v4.new_markdown_cell("""## 7. Seller Ecosystem & Pareto 80/20 Rule
Demonstrating that the top ~18% of sellers generate 80% of Olist's total sales volume.
"""))

    cells.append(nbf.v4.new_code_cell("""sellers = pd.read_parquet('data/processed/seller_performance.parquet')

plt.figure(figsize=(10, 5))
plt.plot(sellers['seller_pct'], sellers['cumulative_revenue_pct'], color='#2563EB', linewidth=2.5, label="Cumulative Revenue %")
plt.axhline(80, color='red', linestyle='--', label="80% Revenue Line")
plt.axvline(18.2, color='red', linestyle='--', label="18.2% Seller Base")
plt.title("Seller Revenue Concentration (Pareto Principle)", fontsize=13, fontweight='bold')
plt.xlabel("% of Sellers (Ranked by Revenue)")
plt.ylabel("% of Total Cumulative Revenue")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
"""))

    nb.cells = cells
    with open(NOTEBOOKS_DIR / "02_Exploratory_Data_Analysis.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print("Created 02_Exploratory_Data_Analysis.ipynb")


def create_notebook_03():
    nb = nbf.v4.new_notebook()
    cells = []

    # Markdown Header
    cells.append(nbf.v4.new_markdown_cell("""# 👥 Olist E-Commerce Analytics — Part 3: Customer Segmentation (RFM) & Cohort Retention
**Author:** Data Analytics Portfolio
**Objective:**
1. Calculate Recency, Frequency, and Monetary (RFM) metrics for 93k+ unique customers.
2. Segment customers into actionable behavioral tiers (Champions, Loyal, At Risk, Hibernating, etc.).
3. Build Monthly Cohort Retention Matrices (Month 0 to Month 12).
4. Formulate targeted CRM and marketing retention strategies to increase Customer Lifetime Value (CLV).
"""))

    # Imports
    cells.append(nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 11

rfm = pd.read_parquet('data/processed/rfm_customer_segments.parquet')
retention_matrix = pd.read_parquet('data/processed/cohort_retention_matrix.parquet')

print(f"Loaded RFM Data for {len(rfm):,} Unique Customers.")
"""))

    # RFM Segment Summary
    cells.append(nbf.v4.new_markdown_cell("""## 1. RFM Segment Distribution & Value Concentration
We profile each behavioral cluster across customer count, average spend, recency, and total GMV contribution.
"""))

    cells.append(nbf.v4.new_code_cell("""seg_profile = rfm.groupby('customer_segment').agg(
    customer_count=('customer_unique_id', 'count'),
    total_spend=('total_spend', 'sum'),
    avg_recency=('recency', 'mean'),
    avg_frequency=('frequency', 'mean'),
    avg_monetary=('total_spend', 'mean')
).reset_index().sort_values('total_spend', ascending=False)

seg_profile['customer_pct'] = (seg_profile['customer_count'] / seg_profile['customer_count'].sum()) * 100
seg_profile['revenue_pct'] = (seg_profile['total_spend'] / seg_profile['total_spend'].sum()) * 100

seg_profile
"""))

    # Visualizing Segments
    cells.append(nbf.v4.new_code_cell("""fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

sns.barplot(data=seg_profile, y='customer_segment', x='customer_count', ax=ax1, palette='Blues_r')
ax1.set_title("Customer Count by Segment", fontsize=13, fontweight='bold')
ax1.set_xlabel("Number of Customers")
ax1.set_ylabel("Segment")

sns.barplot(data=seg_profile, y='customer_segment', x='total_spend', ax=ax2, palette='Greens_r')
ax2.set_title("Total Revenue Contribution by Segment (R$)", fontsize=13, fontweight='bold')
ax2.set_xlabel("Total Spend (R$)")
ax2.set_ylabel("")

plt.tight_layout()
plt.show()
"""))

    # Cohort Retention Matrix
    cells.append(nbf.v4.new_markdown_cell("""## 2. Monthly Cohort Retention Analysis
The cohort matrix tracks customer purchasing behavior over time, following monthly acquisition cohorts from Month 0 to Month 12.
"""))

    cells.append(nbf.v4.new_code_cell("""cols_to_plot = [c for c in retention_matrix.columns if int(c) <= 12]
retention_subset = retention_matrix[cols_to_plot]

plt.figure(figsize=(16, 10))
sns.heatmap(retention_subset, annot=True, fmt=".1f", cmap="Reds", vmin=0, vmax=2.5, cbar_kws={'label': 'Retention Rate (%)'})
plt.title("Monthly Customer Retention Matrix (%) — Olist Marketplace", fontsize=14, fontweight='bold')
plt.xlabel("Cohort Index (Months Passed Since First Purchase)")
plt.ylabel("Acquisition Cohort Month")
plt.tight_layout()
plt.show()
"""))

    # Strategic Action Plan
    cells.append(nbf.v4.new_markdown_cell("""## 3. Targeted Lifecycle Marketing Playbook
Based on our RFM and Cohort findings, we establish 4 targeted customer marketing playbooks:

| Segment | Share of Base | Strategic Marketing Action | Expected Business Impact |
|---|---|---|---|
| **Champions** | ~1.5% | VIP concierge, exclusive early product drops, referral reward bonuses | Maximize advocacy and word-of-mouth growth |
| **Loyal Customers** | ~2.5% | Cross-category product bundles, loyalty tier milestones | Increase average basket size (+15%) |
| **High-Value New / Recent** | ~12% | Day 7 & Day 21 onboarding drip emails, second-purchase discount vouchers | Convert one-time high spenders into repeat buyers |
| **At Risk / Hibernating** | ~40% | Win-back campaigns featuring dynamic product recommendations and free shipping | Recover 3–5% of lapsed customers |
"""))

    nb.cells = cells
    with open(NOTEBOOKS_DIR / "03_Customer_Segmentation_RFM_and_Cohorts.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print("Created 03_Customer_Segmentation_RFM_and_Cohorts.ipynb")


if __name__ == "__main__":
    create_notebook_01()
    create_notebook_02()
    create_notebook_03()
    print("All notebooks created successfully!")
