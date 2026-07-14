# =========================================================================
# Olist E-Commerce SQL Analysis
# Database: olist_ecommerce.db
# Domain: Logistics
# Script: 01_late_delivery_rate.py
# Objective: Calculate the overall late delivery rate for
# delivered orders after excluding extreme delivery delay outliers
# in the Olist E-Commerce dataset
# =========================================================================

from helper.utils import run_query

sql = """
WITH delivery_delays AS (
    SELECT
        o.order_id,
        r.review_score,
        CAST(
            julianday(DATE(o.order_delivered_customer_date)) -
            julianday(DATE(o.order_estimated_delivery_date))
            AS INTEGER
        ) AS delivery_delay_days
    FROM olist_orders_dataset AS o
    JOIN olist_order_reviews_dataset AS r
        ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
),

filtered_deliveries AS (
    SELECT *
    FROM delivery_delays
    WHERE NOT (
        delivery_delay_days > 100
        AND review_score = 5
    )
)

SELECT
    COUNT(*) AS total_delivered_orders,
    SUM(
        CASE
            WHEN delivery_delay_days > 0 THEN 1
            ELSE 0
        END
    ) AS late_delivered_orders,
    ROUND(
        SUM(
            CASE
                WHEN delivery_delay_days > 0 THEN 1
                ELSE 0
            END
        ) * 100.0 / COUNT(*),
        2
    ) AS late_delivery_rate_percentage
FROM filtered_deliveries;
"""

run_query(
    "Overall Late Delivery Rate",
    sql,
    export_csv=True,
    filename="01_late_delivery_rate.csv",
)
