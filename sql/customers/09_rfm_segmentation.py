# =========================================================================
# Olist E-Commerce SQL Analysis
# Database: olist_ecommerce.db
# Domain: Customers
# Script: 09_rfm_segmentation.py
# Objective: Calculate RFM (Recency, Frequency, Monetary) metrics
# for each unique customer in the Olist E-Commerce dataset
# =========================================================================

from helper.utils import run_query

sql = """
WITH customer_rfm AS (
    SELECT
        c.customer_unique_id,
        MAX(DATE(o.order_purchase_timestamp)) AS last_order_date,
        COUNT(DISTINCT o.order_id) AS frequency,
        ROUND(SUM(oi.price + oi.freight_value), 2) AS monetary
    FROM olist_customers_dataset AS c
    JOIN olist_orders_dataset AS o
        ON c.customer_id = o.customer_id
    JOIN olist_order_items_dataset AS oi
        ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
)

SELECT
    customer_unique_id,
    CAST(
        julianday('2018-10-17') - julianday(last_order_date)
        AS INTEGER
    ) AS recency_days,
    frequency,
    monetary
FROM customer_rfm
ORDER BY
    recency_days ASC,
    frequency DESC,
    monetary DESC;
"""

run_query("RFM Metrics by Customer", sql, export_csv=True, filename="customer_rfm.csv")
