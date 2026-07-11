# =========================================================================
# Olist E-Commerce SQL Analysis
# Database: olist_ecommerce.db
# Domain: Sales
# Script: 07_monthly_growth.py
# Objective: Calculate monthly growth in GMV for Olist E-Commerce dataset
# =========================================================================

from helper.utils import run_query

run_query(
    "Monthly Growth in GMV",
    """
WITH monthly_sales AS (
    SELECT 
        STRFTIME('%Y-%m', o.order_purchase_timestamp) AS order_month,
        SUM(oi.price + oi.freight_value) AS current_month_gmv
    FROM olist_order_items_dataset oi
    INNER JOIN olist_orders_dataset o 
        ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY order_month
),
lagged_sales AS (
    SELECT 
        order_month,
        current_month_gmv,
        LAG(current_month_gmv, 1) OVER (ORDER BY order_month ASC) AS previous_month_gmv
    FROM monthly_sales
)
SELECT 
    order_month,
    ROUND(current_month_gmv, 2) AS current_month_gmv,
    ROUND(previous_month_gmv, 2) AS previous_month_gmv,
    -- Handle the first month of the dataset where previous month data is NULL
    CASE 
        WHEN previous_month_gmv IS NULL THEN 0.00
        ELSE ROUND(((current_month_gmv - previous_month_gmv) / previous_month_gmv) * 100.0, 2)
    END AS mom_growth_percentage
FROM lagged_sales
ORDER BY order_month ASC;
""",
)
