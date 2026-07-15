# =========================================================================
# Olist E-Commerce SQL Analysis
# Database: olist_ecommerce.db
# Domain: Sales
# Script: running_gmv.py
# Objective: Calculate running GMV for Olist E-Commerce dataset
# =========================================================================

from helper.utils import run_query

run_query(
    "Cumulative GMV Over Time",
    """
WITH monthly_sales AS (
    SELECT 
        STRFTIME('%Y-%m', o.order_purchase_timestamp) AS order_month,
        SUM(oi.price + oi.freight_value) AS monthly_gmv
    FROM olist_order_items_dataset oi
    INNER JOIN olist_orders_dataset o 
        ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY order_month
)
SELECT 
    order_month,
    ROUND(monthly_gmv, 2) AS current_month_gmv,
    ROUND(SUM(monthly_gmv) OVER (
        ORDER BY order_month ASC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 2) AS cumulative_running_total_gmv
FROM monthly_sales
ORDER BY order_month ASC;
""",
)
