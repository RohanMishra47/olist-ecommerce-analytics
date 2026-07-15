# =========================================================================
# Olist E-Commerce SQL Analysis
# Database: olist_ecommerce.db
# Domain: Customers
# Script: repeat_purchase_by_state.py
# Objective: Calculate repeat purchase rates by state
# for Olist E-Commerce dataset
# =========================================================================

from helper.utils import run_query

sql_query = """
WITH customer_state_orders AS (
    SELECT 
        c.customer_unique_id,
        c.customer_state,
        COUNT(DISTINCT o.order_id) AS total_orders
    FROM olist_customers_dataset c
    INNER JOIN olist_orders_dataset o 
        ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id, c.customer_state
)
SELECT 
    customer_state,
    COUNT(customer_unique_id) AS total_unique_customers,
    SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) AS repeat_customers_count,
    ROUND(
        SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(customer_unique_id), 
        2
    ) AS repeat_purchase_rate_percentage
FROM customer_state_orders
GROUP BY customer_state
ORDER BY total_unique_customers DESC;
"""

run_query("Repeat Purchase Rate by State", sql_query)
