# =========================================================================
# Olist E-Commerce SQL Analysis
# Database: olist_ecommerce.db
# Domain: Customers
# Script: repeat_purchase_rate.py
# Objective: Calculate the overall repeat purchase rate for
# unique customers in the Olist E-Commerce dataset
# =========================================================================

from helper.utils import run_query

# Script: 09_repeat_purchase_rate.py

sql_query = """
WITH customer_order_counts AS (
    SELECT 
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS total_orders
    FROM olist_customers_dataset c
    INNER JOIN olist_orders_dataset o 
        ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
)
SELECT 
    COUNT(customer_unique_id) AS total_unique_customers,
    SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) AS repeat_customers_count,
    ROUND(
        SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(customer_unique_id), 
        2
    ) AS repeat_purchase_rate_percentage
FROM customer_order_counts;
"""

run_query("Repeat Purchase Rate Overall", sql_query)
