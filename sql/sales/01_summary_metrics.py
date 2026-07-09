# =========================================================================
# Olist E-Commerce SQL Analysis
# Database: olist_ecommerce.db
# Domain: Sales
# Script: 01_summary_metrics.py
# Objective: Summary metrics for Olist E-Commerce dataset
# =========================================================================

from helper.utils import run_query

run_query(
    "Total Number of Orders",
    """
    SELECT COUNT(DISTINCT order_id) AS total_orders
    FROM olist_orders_dataset;
""",
)

run_query(
    "Pure Product Revenue (Net Product Sales)",
    """
    SELECT
        SUM(oi.price) AS total_product_revenue
    FROM olist_order_items_dataset oi
    INNER JOIN olist_orders_dataset o
        ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered';
""",
)

run_query(
    "Gross Merchandise Value / GMV (Product + Freight)",
    """
    SELECT
        SUM(oi.price + oi.freight_value) AS gross_merchandise_value
    FROM olist_order_items_dataset oi
    INNER JOIN olist_orders_dataset o
        ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered';
""",
)

run_query(
    "Net Revenue",
    """
    SELECT
        SUM(p.payment_value) AS net_revenue
    FROM olist_order_payments_dataset p
    JOIN olist_orders_dataset o
        ON p.order_id = o.order_id
    WHERE o.order_status = 'delivered';
""",
)

run_query(
    "Date Range Covered",
    """
    SELECT
        MIN(order_purchase_timestamp) AS start_date,
        MAX(order_purchase_timestamp) AS end_date
    FROM olist_orders_dataset;
""",
)
