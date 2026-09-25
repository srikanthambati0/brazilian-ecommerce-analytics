# 🛍️ Brazilian E-Commerce Analytics & Executive Intelligence Platform (Olist)

[![Python](https://img.shields.io/badge/Python-3.12%20%7C%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Plotly](https://img.shields.io/badge/Plotly-5.0+-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

An end-to-end data analytics and business intelligence platform built on the **Olist Brazilian E-Commerce Dataset** (100k+ orders, R$ 15.4M GMV, 2016–2018). This repository features a production-grade ETL pipeline, RFM customer segmentation, cohort retention modeling, supply chain root-cause analysis, and an interactive 8-module Streamlit executive dashboard.

---

## 📌 Executive Summary & Key Metrics

| Metric | Value | Business Significance |
|---|---|---|
| **Gross Merchandise Value (GMV)** | **R$ 15.42M** | Total transaction volume across items and freight |
| **Delivered Orders** | **96,478** | Completed marketplace orders across 27 Brazilian states |
| **Average Order Value (AOV)** | **R$ 137.04** | R$ 159.83 including logistics freight |
| **Customer CSAT Rating** | **4.08 / 5.0** | 76.8% positive feedback ratings (4 & 5 stars) |
| **Repeat Purchase Rate** | **3.00%** | Severe retention deficit; 97% are 1-time buyers |
| **Late Delivery Rate** | **7.91%** | Strongest driver of 1-star reviews (48.2% attribution) |
| **Seller Pareto Concentration** | **18.2% / 80%** | Top 18.2% of sellers generate 80% of total marketplace GMV |

---

## 🏗️ System Architecture & Analytical Pipeline

```
+-----------------------------------------------------------------------------------------+
|                                    DATA PIPELINE                                        |
+-----------------------------------------------------------------------------------------+
| 1. RAW INGESTION     --> 9 Relational Tables (Orders, Customers, Items, Payments, etc.) |
| 2. DATA WRANGLING    --> Geolocation Centroid Aggregation (98% compression), BOM fix    |
| 3. FEATURE ENGINE    --> RFM Scoring, Cohort Index, Seller Tiers, Delivery Delays       |
| 4. PARQUET STORAGE   --> Columnar, compressed analytics tables for sub-second queries    |
| 5. SERVING & BI      --> 8-Module Interactive Streamlit Web App & Jupyter Notebooks     |
+-----------------------------------------------------------------------------------------+
```

---

## 🔍 Key Analytical Highlights & Findings

### 1. 🚚 Logistics Friction Directly Controls Customer Satisfaction
- **Root Cause**: **48.2% of all 1-star reviews are caused by late deliveries**.
- **Delivery Disparity**: 5-star orders take an average of **10.2 days**, whereas 1-star orders take **19.5 days** (a 91% increase in delivery latency).
- **Regional Bottlenecks**: Lead times in Northern states (RR, AP, AM) exceed **25+ days** vs **8.5 days** in São Paulo.

### 2. 👥 Customer Retention & RFM Segmentation
- **Cohort Retention**: Average Month-1 retention rate across historical cohorts is **< 0.6%**.
- **Opportunity**: Doubling the repeat customer rate from 3% to 6% via targeted CRM and loyalty rewards unlocks **+R$ 1.85M in incremental annual GMV** with zero additional acquisition cost.

### 3. 💳 Installment Credit Financing Drives High-Value Baskets
- **Credit Card** accounts for **76.8% of total GMV**, with **51.3% of orders financed via installments** (up to 24 months).
- Installment orders generate significantly higher basket values (**R$ 163.20**) compared to single-payment methods.

---

## 🖥️ Interactive Streamlit Dashboard Modules

The platform includes an interactive multi-tab web application:
1. **📊 Executive Overview**: Real-time KPI metric tiles, monthly GMV growth, order status distribution, top categories.
2. **📈 Sales & Growth Trends**: Time-series revenue trajectories, Black Friday surge analysis, Day-of-Week & Hour-of-Day order intensity heatmaps.
3. **👥 Customer & RFM Segmentation**: 10 behavioral customer tiers, 3D RFM scatter plots, and 12-month cohort retention heatmaps.
4. **🚚 Logistics & Operations**: State-by-state delivery lead times, late delivery rates, and freight-to-price ratios.
5. **💳 Payments & Financials**: Payment instrument market shares, installment breakdown, and average ticket sizes.
6. **⭐ Reviews & Customer CSAT**: Review score distributions, delay elasticity curves, and comment frequency analysis.
7. **🗺️ Geography & Seller Ecosystem**: Pareto 80/20 seller distribution curve, state trade flows, and top sellers leaderboard.
8. **💡 Business Recommendations**: 5-pillar strategic roadmap for executive decision-makers.

---

## 📂 Repository Structure

```
├── data/
│   ├── raw/                      # 9 raw CSV datasets
│   └── processed/                # Cleaned, enriched Parquet & CSV analytics tables
├── src/
│   ├── config.py                 # Paths, constants, and segment mapping definitions
│   ├── data_loader.py            # Typed CSV ingestion with BOM & date handling
│   ├── data_cleaning.py          # Data cleaning, normalization & master dataset creation
│   ├── feature_engineering.py    # RFM segmentation, cohort matrices & seller tiers
│   └── eda_analytics.py          # Analytical queries and KPI aggregation helpers
├── notebooks/
│   ├── 01_Data_Cleaning_and_Wrangling.ipynb
│   ├── 02_Exploratory_Data_Analysis.ipynb
│   └── 03_Customer_Segmentation_RFM_and_Cohorts.ipynb
├── app/
│   └── app.py                    # Production Streamlit Interactive Web Application
├── reports/
│   ├── Executive_Summary_Report.md  # Formal C-suite business intelligence report
│   ├── Resume_Bullet_Points.md      # STAR-format bullet points for resumes
│   └── Interview_Talking_Points.md  # 15+ technical & behavioral interview Q&As
├── requirements.txt              # Project dependencies
├── .gitignore                    # Clean git tracking exclusions
└── README.md                     # Project documentation
```

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/srikanthambati0/brazilian-ecommerce-analytics.git
cd brazilian-ecommerce-analytics
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Data Pipeline (Optional - Preprocessed files included)
```bash
python -m src.data_cleaning
python -m src.feature_engineering
```

### 5. Launch the Interactive Streamlit Dashboard
```bash
streamlit run app/app.py
```
Open your browser and navigate to `http://localhost:8501`.

---

## 💡 Strategic Recommendations Summary

1. **🚚 Regional Cross-Docking**: Establish fulfillment hubs in Brasília (DF) and Salvador (BA) to reduce North/Northeast delivery times by 35%.
2. **🔁 "Olist Rewards" Loyalty Program**: Deploy cross-seller reward points and automated lifecycle CRM to lift repeat buyer rates from 3% to 6%.
3. **⭐ Merchant Quality Badges & SLAs**: Prioritize search ranking for merchants with ≥ 4.2 CSAT and ≥ 95% on-time dispatch.
4. **💳 Instant PIX Checkout**: Replace slow Boleto vouchers with instant PIX payments to cut abandoned carts by 8.5%.
5. **🎯 Dynamic ML Delivery ETAs**: Implement predictive delivery dates on product pages to align customer expectations and prevent 1-star reviews.

---

## 👤 Author
* **Portfolio Project**: Brazilian E-Commerce Executive Intelligence Platform
* **GitHub Repository**: [srikanthambati0/brazilian-ecommerce-analytics](https://github.com/srikanthambati0/brazilian-ecommerce-analytics)
* **GitHub Profile**: [@srikanthambati0](https://github.com/srikanthambati0)
