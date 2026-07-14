# =========================================================================
# Olist E-Commerce SQL Analysis
# Database: olist_ecommerce.db
# Domain: Logistics
# Script: freight_pct_by_category.py
# Objective: Calculate the average freight value as a percentage of
# product price by category for the Olist E-Commerce dataset
# =========================================================================

from helper.utils import run_query

sql = """
SELECT
    p.product_category_name,
    ROUND(SUM(oi.price), 2) AS total_product_price,
    ROUND(SUM(oi.freight_value), 2) AS total_freight_value,
    ROUND(
        (SUM(oi.freight_value) / NULLIF(SUM(oi.price), 0)) * 100.0,
        2
    ) AS freight_percentage_of_price
FROM olist_order_items_dataset AS oi
JOIN olist_products_dataset AS p
    ON oi.product_id = p.product_id
JOIN olist_orders_dataset AS o
    ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY p.product_category_name
ORDER BY freight_percentage_of_price DESC;
"""

run_query(
    "Average Freight Value as % of Product Price by Category",
    sql,
    export_csv=True,
    filename="freight_pct_by_category.csv",
)
