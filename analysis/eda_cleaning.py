"""
================================================================================
Olist E-Commerce Pipeline — Phase 2: Python EDA & Data Cleaning
Module: src/eda_cleaning.py

Objective:
    Extracts core relational tables from SQLite, applies functional data hygiene
    pipelines (timestamp standardizing, spatial deduplication, localized translations),
    and programmatically exports diagnostic plots for reporting.

Pipeline Functions:
    - load_table()
    - convert_datetime_columns()
    - flag_outliers()

Database Source: olist_ecommerce.db (Project Root)
Target Export Folder: /plots
================================================================================
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns

sns.set_theme(style="whitegrid")
from helper.utils import load_table, convert_datetime_columns, flag_outliers

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
# Investigating null values in the orders dataset
# ======================================================

# 1. Delivered orders with missing timestamps (Suspicious)
timestamp_cols = [
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
]

for col in timestamp_cols:
    # print(f"\nChecking: {col}")

    suspicious = orders_clean.loc[
        (orders_clean["order_status"] == "delivered") & (orders_clean[col].isna()),
        ["order_id", "order_status", col],
    ]

#     print(suspicious)
#     print(f"Suspicious rows: {len(suspicious)}")

# 2. Canceled orders with customer delivery dates
unexpected = orders_clean.loc[
    (orders_clean["order_status"] == "canceled")
    & (orders_clean["order_delivered_customer_date"].notna()),
    ["order_id", "order_status", "order_delivered_customer_date"],
]

# print("\nCanceled orders with customer delivery dates:")
# print(unexpected)
# print(f"Unexpected rows: {len(unexpected)}")

# 3. Status distribution for missing timestamps
# for col in timestamp_cols:
#     print(f"\nMissing values in: {col}")

#     print(orders_clean.loc[orders_clean[col].isna(), "order_status"].value_counts())

# ======================================================
# Deduplicate geolocation table (one row per ZIP prefix)
# ======================================================

geo_clean = geolocation_raw.groupby("geolocation_zip_code_prefix", as_index=False).agg(
    {"geolocation_lat": "mean", "geolocation_lng": "mean"}
)

# # Verify the result
# print(f"Original shape: {geolocation_raw.shape}")
# print(f"Cleaned shape: {geo_clean.shape}")

# # Check that every ZIP prefix is now unique
# print(f"Unique ZIP prefixes: {geo_clean['geolocation_zip_code_prefix'].nunique()}")
# print(f"Total rows: {len(geo_clean)}")

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

# # Verify the results
# print(f"Original products shape: {products_raw.shape}")
# print(f"Cleaned products shape: {products_clean.shape}")

# print("\nMissing English categories after cleaning:")
# print(products_clean["product_category_name_english"].isna().sum())

# print("\nCategory sample:")
# print(
#     products_clean[["product_category_name", "product_category_name_english"]].head(10)
# )

# ======================================================================================
# Outlier Detection and Flagging for "price", "freight_value", and "physical_dimensions"
# ======================================================================================

# Order Items table
# items_clean = flag_outliers(items_clean, "price")
# items_clean = flag_outliers(items_clean, "freight_value")

# Products table
# products_clean = flag_outliers(products_clean, "product_weight_g")
# products_clean = flag_outliers(products_clean, "product_length_cm")
# products_clean = flag_outliers(products_clean, "product_height_cm")
# products_clean = flag_outliers(products_clean, "product_width_cm")

# ==========================
# Charts and Visualizations
# ==========================

# ── Chart 1 · Monthly Revenue Trend (Line Chart) ─────────────
# df = pd.merge(items_clean, orders_clean, on="order_id")
# df = df[df["order_status"] == "delivered"]

# monthly_revenue = (
#     df.assign(GMV=df["price"] + df["freight_value"])
#     .groupby(df["order_purchase_timestamp"].dt.to_period("M"))["GMV"]
#     .sum()
#     .reset_index()
# )

# monthly_revenue["order_purchase_timestamp"] = monthly_revenue[
#     "order_purchase_timestamp"
# ].dt.to_timestamp()

# fig, ax = plt.subplots(figsize=(10, 5))

# sns.lineplot(
#     data=monthly_revenue, x="order_purchase_timestamp", y="GMV", marker="o", ax=ax
# )

# ax.set_title("Monthly Revenue Trend")
# ax.set_xlabel("Month")
# ax.set_ylabel("Revenue")
# ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${x:,.0f}"))

# plt.tight_layout()
# plt.savefig("plots/monthly_revenue_trend.png", dpi=150)
# plt.show()

# ── Chart 2 · Order Status Distribution (Bar Chart) ─────────────
# fig, ax = plt.subplots()

# # Sort by count and plot
# order = orders_clean["order_status"].value_counts().index
# sns.countplot(
#     data=orders_clean,
#     x="order_status",
#     order=order,
#     color="steelblue",
#     palette="Blues_d",
#     ax=ax,
# )

# # Add labels with commas
# for container in ax.containers:
#     ax.bar_label(container, padding=3)

# ax.set_title("Distribution of Order Statuses", fontsize=14, fontweight="bold", pad=20)
# ax.set_xlabel("Order Status", fontsize=12)
# ax.set_ylabel("Number of Orders", fontsize=12)

# # Rotate x-labels
# ax.tick_params(axis="x", rotation=45)

# plt.tight_layout()
# plt.savefig("plots/order_status_distribution.png", dpi=150)
# plt.show()

# ── Chart 3 · Review Score Distribution (Bar Chart) ─────────────
# fig, ax = plt.subplots(figsize=(8, 5))

# order = reviews_clean["review_score"].value_counts().index
# sns.countplot(
#     data=reviews_clean,
#     x="review_score",
#     order=order,
#     color="steelblue",
#     palette="Blues_d",
#     ax=ax,
# )

# for container in ax.containers:
#     ax.bar_label(container, padding=3)

# ax.set_title("Review Score Distribution", fontsize=14, fontweight="bold", pad=20)
# ax.set_xlabel("Review Score", fontsize=12)
# ax.set_ylabel("Number of Reviews", fontsize=12)

# plt.tight_layout()
# plt.savefig("plots/review_score_distribution.png", dpi=150)
# plt.show()

# ── Chart 4 · Top Product Categories by Revenue (GMV) (Horizontal Bar Chart) ─────────────
# filtered = items_clean.merge(orders_clean, on="order_id", how="inner").merge(
#     products_clean, on="product_id", how="inner"
# )

# filtered = filtered[filtered["order_status"] == "delivered"]

# filtered["total_revenue_gmv"] = filtered["price"] + filtered["freight_value"]

# grouped = (
#     filtered.groupby("product_category_name_english", as_index=False)[
#         "total_revenue_gmv"
#     ]
#     .sum()
#     .rename(columns={"product_category_name_english": "category_name"})
# )

# grouped["total_revenue_gmv"] = grouped["total_revenue_gmv"].round(2)

# result = grouped.sort_values("total_revenue_gmv", ascending=False).head(10)

# # --- Format category names ---
# result["category_name_formatted"] = (
#     result["category_name"]
#     .str.replace("_", " ")
#     .str.title()
#     .str.replace(" And ", " & ")
#     .str.replace(" Of ", " of ")
# )


# # --- Format revenue values ---
# def format_revenue(x, pos):
#     # Convert to millions if values are large (e.g., 1.2M)
#     if x >= 1e6:
#         return f"${x/1e6:.1f}M"
#     # Convert to thousands if values are medium (e.g., 1.2K)
#     elif x >= 1e3:
#         return f"${x/1e3:.1f}K"
#     # Default: Show as-is with 2 decimal places
#     else:
#         return f"${x:.2f}"


# # Apply FuncFormatter to the x-axis
# revenue_formatter = FuncFormatter(format_revenue)

# fig, ax = plt.subplots(figsize=(10, 6))

# sns.barplot(
#     x="total_revenue_gmv",
#     y="category_name_formatted",
#     hue="category_name_formatted",
#     data=result,
#     palette="viridis",
#     legend=False,
#     ax=ax,
# )

# ax.xaxis.set_major_formatter(revenue_formatter)
# for bar in ax.patches:
#     width = bar.get_width()

#     ax.text(
#         width + 5000,
#         bar.get_y() + bar.get_height() / 2,
#         f"${width/1_000_000:.2f}M",
#         va="center",
#         fontsize=10,
#     )

# ax.set_title(
#     "Top Product Categories by Revenue", fontsize=14, fontweight="bold", pad=20
# )
# ax.set_ylabel("Categories", fontsize=12)
# ax.set_xlabel("Revenue", fontsize=12)
# ax.set_xlim(0, result["total_revenue_gmv"].max() * 1.15)

# ax.grid(axis="x", linestyle="--", alpha=0.6)

# plt.tight_layout()
# plt.savefig("plots/top_product_categories_revenue.png", dpi=150)
# plt.show()

# ── Chart 5 · Customer Geographic Distribution (State Level Horizontal Bar Chart) ─────────────
# result = (
#     customers_raw.groupby("customer_state")["customer_unique_id"]
#     .nunique()
#     .reset_index()
#     .rename(columns={"customer_unique_id": "unique_customer_count"})
#     .sort_values(by="unique_customer_count", ascending=False)
# )

# fig, ax = plt.subplots(figsize=(10, 6))

# sns.barplot(
#     x="unique_customer_count",
#     y="customer_state",
#     data=result,
#     color="#4C72B0",
#     ax=ax,
# )

# ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}"))
# for bar in ax.patches:
#     width = bar.get_width()

#     ax.text(
#         width + 200,
#         bar.get_y() + bar.get_height() / 2,
#         f"{int(width):,}",
#         va="center",
#         ha="left",
#         fontsize=10,
#     )

# ax.set_title(
#     "Customer State Level Geographic Distribution",
#     fontsize=14,
#     fontweight="bold",
#     pad=20,
# )
# ax.set_ylabel("States", fontsize=12)
# ax.set_xlabel("Customer Counts", fontsize=12)

# ax.grid(axis="x", linestyle="--", alpha=0.6)

# plt.tight_layout()
# plt.savefig("plots/customer_state_distribution.png", dpi=150)
# plt.show()

# ── Chart 6 · Price and Freight Value Distributions (Histograms + Boxplots for Outliers) ─────────────
"""
To improve readability, this histogram displays prices, and freight values up to the 99th percentile. 
Extreme values are excluded only from the visualization and are analyzed separately using the boxplot.
"""

# # ── Price Distribution Histogram ─────────────

# # Calculate the 99th percentile
# price_limit = items_clean["price"].quantile(0.99)

# # Filter only for visualization
# price_zoomed = items_clean[items_clean["price"] <= price_limit]

# fig, ax = plt.subplots(figsize=(10, 6))

# sns.histplot(
#     data=price_zoomed,
#     x="price",
#     kde=True,
#     edgecolor="gray",
#     linewidth=0.4,
#     bins=40,
#     color="#4C72B0",
#     ax=ax,
# )
# ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"R${x:,.0f}"))

# ax.set_title(
#     "Product Price Distribution (Up to 99th Percentile)",
#     fontsize=14,
#     fontweight="bold",
#     pad=20,
# )
# ax.set_xlabel("Product Price (R$)", fontsize=12)
# ax.set_ylabel("Number of Orders", fontsize=12)

# sns.despine()
# plt.tight_layout()
# plt.savefig("plots/price_distribution_histogram.png", dpi=150)
# plt.show()

# # ── Freight Value Distribution Histogram ─────────────

# # Calculate the 99th percentile
# freight_limit = items_clean["freight_value"].quantile(0.99)

# # Filter only for visualization
# freight_zoomed = items_clean[items_clean["freight_value"] <= freight_limit]

# fig, ax = plt.subplots(figsize=(10, 6))

# sns.histplot(
#     data=freight_zoomed,
#     x="freight_value",
#     bins=40,
#     kde=True,
#     color="#4C72B0",
#     edgecolor="gray",
#     linewidth=0.4,
#     ax=ax,
# )

# ax.set_title(
#     "Freight Value Distribution (Up to 99th Percentile)",
#     fontsize=14,
#     fontweight="bold",
#     pad=20,
# )
# ax.set_xlabel("Freight Value (R$)", fontsize=12)
# ax.set_ylabel("Number of Orders", fontsize=12)

# ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"R${x:,.0f}"))

# sns.despine()
# plt.tight_layout()
# plt.savefig("plots/freight_value_distribution_histogram.png", dpi=150)
# plt.show()

# # ── Price Distribution Boxplot ─────────────
# fig, ax = plt.subplots(figsize=(10, 2.5))

# sns.boxplot(
#     data=items_clean,
#     x="price",
#     color="#4C72B0",
#     width=0.5,
#     flierprops={
#         "marker": "o",
#         "markersize": 3,
#         "markerfacecolor": "red",
#         "markeredgecolor": "red",
#         "alpha": 0.4,
#     },
#     ax=ax,
# )

# ax.set_title(
#     "Product Price Distribution (Boxplot)", fontsize=14, fontweight="bold", pad=20
# )
# ax.set_xlabel("Product Price (R$)", fontsize=12)

# ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"R${x:,.0f}"))

# sns.despine(left=True)
# plt.tight_layout()
# plt.savefig("plots/price_distribution_boxplot.png", dpi=150)
# plt.show()

# # ── Freight Value Distribution Boxplot ─────────────
# fig, ax = plt.subplots(figsize=(10, 2.5))

# sns.boxplot(
#     data=items_clean,
#     x="freight_value",
#     color="#4C72B0",
#     width=0.5,
#     flierprops={
#         "marker": "o",
#         "markersize": 3,
#         "markerfacecolor": "red",
#         "markeredgecolor": "red",
#         "alpha": 0.4,
#     },
#     ax=ax,
# )

# ax.set_title(
#     "Freight Value Distribution (Boxplot)", fontsize=14, fontweight="bold", pad=20
# )
# ax.set_xlabel("Freight Value (R$)", fontsize=12)

# ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"R${x:,.0f}"))

# sns.despine(left=True)
# plt.tight_layout()
# plt.savefig("plots/freight_value_distribution_boxplot.png", dpi=150)
# plt.show()

# ── Chart 7 · Delivery Performance Analysis ─────────────

# ── Distribution of Actual Delivery Time (Purchase → Delivery) ─────────────
# Keep only delivered orders with valid delivery dates
# delivered_orders = orders_clean[
#     (orders_clean["order_status"] == "delivered")
#     & (orders_clean["order_delivered_customer_date"].notna())
# ].copy()

# # Calculate delivery time in days
# delivered_orders["delivery_time_days"] = (
#     delivered_orders["order_delivered_customer_date"]
#     - delivered_orders["order_purchase_timestamp"]
# ).dt.days

# fig, ax = plt.subplots(figsize=(10, 6))

# sns.histplot(
#     data=delivered_orders, x="delivery_time_days", bins=30, kde=True, color="steelblue"
# )

# ax.set_title(
#     "Distribution of Actual Delivery Time", fontsize=14, fontweight="bold", pad=20
# )
# ax.set_xlabel("Delivery Time (Days)", fontsize=12)
# ax.set_ylabel("Number of Orders", fontsize=12)

# plt.tight_layout()
# plt.savefig("plots/delivery_time_distribution.png", dpi=150)
# plt.show()

# ── Distribution of Delivery Delay (Actual vs. Estimated Delivery) ─────────────
# Keep only delivered orders
# delivered_orders = orders_clean[
#     (orders_clean["order_status"] == "delivered")
#     & (orders_clean["order_delivered_customer_date"].notna())
# ].copy()

# # Calculate delivery delay in days
# delivered_orders["delivery_delay_days"] = (
#     delivered_orders["order_delivered_customer_date"]
#     - delivered_orders["order_estimated_delivery_date"]
# ).dt.days

# fig, ax = plt.subplots(figsize=(10, 6))

# sns.histplot(
#     data=delivered_orders,
#     x="delivery_delay_days",
#     bins=30,
#     kde=True,
#     color="tomato",
#     ax=ax,
# )

# # Reference line for on-time delivery
# ax.axvline(x=0, color="black", linestyle="--", linewidth=1.5, label="On-Time Delivery")

# ax.set_title("Distribution of Delivery Delay", fontsize=14, fontweight="bold", pad=20)
# ax.set_xlabel("Delivery Delay (Days)", fontsize=12)
# ax.set_ylabel("Number of Orders", fontsize=12)
# ax.legend()

# plt.tight_layout()
# plt.savefig("plots/delivery_delay_distribution.png", dpi=150)
# plt.show()

# ── Chart 8 . Correlation Check: Delivery Time vs. Review Score (Scatter Plot) ─────────────

merged_data = orders_clean.merge(reviews_clean, on="order_id", how="left")

delivered_orders = merged_data[
    (merged_data["order_status"] == "delivered")
    & (merged_data["order_delivered_customer_date"].notna())
].copy()

delivered_orders["delivery_delay_days"] = (
    delivered_orders["order_delivered_customer_date"]
    - delivered_orders["order_estimated_delivery_date"]
).dt.days

delivered_orders = delivered_orders.dropna(
    subset=["delivery_delay_days", "review_score"]
)

fig, ax = plt.subplots(figsize=(10, 6))

ax.scatter(
    data=delivered_orders, x="delivery_delay_days", y="review_score", alpha=0.2, s=15
)

ax.set_title("Delivery Delay vs Review Score", fontsize=14, fontweight="bold", pad=20)
ax.set_xlabel("Delivery Delay (Days)", fontsize=12)
ax.set_ylabel("Review Score", fontsize=12)

ax.set_yticks([1, 2, 3, 4, 5])

ax.grid(alpha=0.3)

plt.tight_layout()
plt.show()
