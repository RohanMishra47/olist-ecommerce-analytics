# =========================================================================
# Olist E-Commerce SQL Analysis
# Database: olist_ecommerce.db
# Domain: Sales
# Script: 03_monthly_gmv_trend.py
# Objective: Monthly GMV trend analysis for Olist E-Commerce dataset
# =========================================================================

from helper.utils import run_query

run_query(
    "Revenue (GMV) by Month (Time Trend)",
    """
    SELECT
        STRFTIME('%Y-%m', o.order_purchase_timestamp) AS order_month,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(oi.price + oi.freight_value) AS gross_merchandise_value
    FROM olist_order_items_dataset oi
    INNER JOIN olist_orders_dataset o
        ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY order_month
    ORDER BY order_month ASC;
""",
)
