"""
================================================================================
Olist E-Commerce Analysis Project
Module: analysis/01_data_cleaning.py

Objective:
    Loads the Olist SQLite database, performs initial data cleaning and
    preprocessing, standardizes datetime columns, creates derived analytical
    features, and prepares clean DataFrames for exploratory data analysis (EDA)
    and downstream business investigations.

Key Operations:
    - Connect to SQLite database
    - Load project tables into pandas DataFrames
    - Convert timestamp columns to datetime
    - Handle and document missing values
    - Merge category translation data
    - Create derived analytical features
    - Flag potential outliers for later investigation
    - Validate overall data quality

Database Source:
    olist_ecommerce.db (Project Root)

Outputs:
    - Cleaned pandas DataFrames
    - Optional exported datasets
    - Foundation for subsequent analysis scripts

Project Pipeline:
    01_data_cleaning.py
        ↓
    02_eda.py
        ↓
    03_delivery_outlier_investigation.py
        ↓
    SQL Analysis (Phase 3)
        ↓
    export_powerbi_data.py
        ↓
    Power BI Dashboard
================================================================================
"""

from helper.utils import (
    load_table,
    convert_datetime_columns,
    flag_outliers,
    validate_order_timestamps,
)

# Load core relational tables from SQLite database
orders_raw = load_table("olist_orders_dataset")
order_items_raw = load_table("olist_order_items_dataset")
customers_raw = load_table("olist_customers_dataset")
payments_raw = load_table("olist_order_payments_dataset")
reviews_raw = load_table("olist_order_reviews_dataset")
products_raw = load_table("olist_products_dataset")
translation_raw = load_table("product_category_name_translation")
sellers_raw = load_table("olist_sellers_dataset")
geolocation_raw = load_table("olist_geolocation_dataset")

# ======================================================
# Convert timestamp columns to datetime objects for consistency
# ======================================================
orders_datetime_cols = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]
orders_clean = convert_datetime_columns(orders_raw, orders_datetime_cols)

items_datetime_cols = ["shipping_limit_date"]
items_clean = convert_datetime_columns(order_items_raw, items_datetime_cols)

reviews_datetime_cols = ["review_creation_date", "review_answer_timestamp"]
reviews_clean = convert_datetime_columns(reviews_raw, reviews_datetime_cols)

# ======================================================
# Deduplicate geolocation table (one row per ZIP prefix)
# ======================================================

geo_clean = geolocation_raw.groupby("geolocation_zip_code_prefix", as_index=False).agg(
    {"geolocation_lat": "mean", "geolocation_lng": "mean"}
)

# ======================================================
# Category Translation and Fallback Handling
# ======================================================

# Join products with the category translation table
products_clean = products_raw.merge(
    translation_raw, on="product_category_name", how="left"
)

# Replace missing English category names with "uncategorized"
products_clean["product_category_name_english"] = products_clean[
    "product_category_name_english"
].fillna("uncategorized")

# ======================================================================================
# Outlier Detection and Flagging for "price", "freight_value", and "physical_dimensions"
# ======================================================================================

# Order Items table
items_clean = flag_outliers(items_clean, "price")
items_clean = flag_outliers(items_clean, "freight_value")

# Products table
products_clean = flag_outliers(products_clean, "product_weight_g")
products_clean = flag_outliers(products_clean, "product_length_cm")
products_clean = flag_outliers(products_clean, "product_height_cm")
products_clean = flag_outliers(products_clean, "product_width_cm")

# ======================================================
# Investigating null values in the orders dataset
# ======================================================
validate_order_timestamps(orders_clean)

# ==============================
# Exporting Cleaned Data to CSV
# ==============================
orders_clean.to_csv("exports/cleaned/orders_clean.csv", index=False)
items_clean.to_csv("exports/cleaned/items_clean.csv", index=False)
reviews_clean.to_csv(
    "exports/cleaned/reviews_clean.csv", index=False, encoding="utf-8-sig"
)
geo_clean.to_csv("exports/cleaned/geo_clean.csv", index=False)
products_clean.to_csv(
    "exports/cleaned/products_clean.csv", index=False, encoding="utf-8-sig"
)
