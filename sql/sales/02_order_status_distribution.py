# =========================================================================
# Olist E-Commerce SQL Analysis
# Database: olist_ecommerce.db
# Domain: Sales
# Script: 02_order_status_distribution.py
# Objective: Order status distribution analysis for Olist E-Commerce dataset
# =========================================================================

from helper.utils import run_query

run_query(
    "Absolute Volume (Count) and the Relative Share (%) of Orders",
    """
    SELECT
        order_status,
        COUNT(order_id) AS order_count,
        ROUND(COUNT(order_id) * 100.0 / SUM(COUNT(order_id)) OVER(), 2) AS percentage
    FROM olist_orders_dataset
    GROUP BY order_status
    ORDER BY order_count DESC;
""",
)
