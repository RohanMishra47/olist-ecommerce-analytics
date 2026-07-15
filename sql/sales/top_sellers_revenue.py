# =========================================================================
# Olist E-Commerce SQL Analysis
# Database: olist_ecommerce.db
# Domain: Sales
# Script: top_sellers_revenue.py
# Objective: Top sellers revenue analysis for Olist E-Commerce dataset
# =========================================================================

from helper.utils import run_query

run_query(
    "Top 10 Sellers by Revenue (GMV)",
    """
    SELECT
        oi.seller_id,
        s.seller_city,
        s.seller_state,
        COUNT(DISTINCT oi.order_id) AS unique_orders_handled,
        COUNT(oi.order_id) AS physical_units_sold,
        ROUND(SUM(oi.price), 2) AS pure_product_revenue,
        ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue_gmv
    FROM olist_order_items_dataset oi
    INNER JOIN olist_orders_dataset o
        ON oi.order_id = o.order_id
    INNER JOIN olist_sellers_dataset s
        ON oi.seller_id = s.seller_id
    WHERE o.order_status = 'delivered'
    GROUP BY oi.seller_id, s.seller_city, s.seller_state
    ORDER BY total_revenue_gmv DESC
    LIMIT 10;
""",
)
