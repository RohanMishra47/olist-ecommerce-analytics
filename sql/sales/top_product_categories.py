# =========================================================================
# Olist E-Commerce SQL Analysis
# Database: olist_ecommerce.db
# Domain: Sales
# Script: top_product_categories.py
# Objective: Top product categories analysis for Olist E-Commerce dataset
# =========================================================================

from helper.utils import run_query

run_query(
    "Top 10 Categories by Revenue (GMV)",
    """
    SELECT
        COALESCE(t.product_category_name_english, p.product_category_name) AS category_name,
        ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue_gmv,
        COUNT(DISTINCT o.order_id) AS unique_orders
    FROM olist_order_items_dataset oi
    INNER JOIN olist_orders_dataset o
        ON oi.order_id = o.order_id
    INNER JOIN olist_products_dataset p
        ON oi.product_id = p.product_id
    LEFT JOIN product_category_name_translation t
        ON p.product_category_name = t.product_category_name
    WHERE o.order_status = 'delivered'
    GROUP BY category_name
    ORDER BY total_revenue_gmv DESC
    LIMIT 10;
""",
)

run_query(
    "Top 10 Categories by Order Volume",
    """
    SELECT
        COALESCE(t.product_category_name_english, p.product_category_name) AS category_name,
        COUNT(DISTINCT o.order_id) AS unique_orders,
        COUNT(oi.order_id) AS total_items_sold,
        ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue_gmv
    FROM olist_order_items_dataset oi
    INNER JOIN olist_orders_dataset o
        ON oi.order_id = o.order_id
    INNER JOIN olist_products_dataset p
        ON oi.product_id = p.product_id
    LEFT JOIN product_category_name_translation t
        ON p.product_category_name = t.product_category_name
    WHERE o.order_status = 'delivered'
    GROUP BY category_name
    ORDER BY unique_orders DESC
    LIMIT 10;
""",
)
