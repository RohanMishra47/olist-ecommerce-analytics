# =========================================================================
# Olist E-Commerce SQL Analysis
# Database: olist_ecommerce.db
# Domain: Logistics
# Script: freight_pct_state_pairs.py
# Objective: Calculate the average freight value as a percentage of
# product price by customer-seller state pair in
# the Olist E-Commerce dataset
# =========================================================================

from helper.utils import run_query

sql = """
SELECT
    c.customer_state,
    s.seller_state,
    ROUND(SUM(oi.price), 2) AS total_product_price,
    ROUND(SUM(oi.freight_value), 2) AS total_freight_value,
    ROUND(
        (SUM(oi.freight_value) / NULLIF(SUM(oi.price), 0)) * 100.0,
        2
    ) AS freight_percentage_of_price
FROM olist_orders_dataset AS o
JOIN olist_order_items_dataset AS oi
    ON o.order_id = oi.order_id
JOIN olist_customers_dataset AS c
    ON o.customer_id = c.customer_id
JOIN olist_sellers_dataset AS s
    ON oi.seller_id = s.seller_id
WHERE o.order_status = 'delivered'
GROUP BY
    c.customer_state,
    s.seller_state
HAVING COUNT(DISTINCT o.order_id) >= 20
ORDER BY freight_percentage_of_price DESC;
"""

run_query(
    "Average Freight Value as % of Product Price by Customer-Seller State Pair", sql
)
