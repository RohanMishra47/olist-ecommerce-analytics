# =========================================================================
# Olist E-Commerce SQL Analysis
# Database: olist_ecommerce.db
# Domain: Logistics
# Script: 02_late_delivery_by_state.py
# Objective: Calculate the late delivery rate by customer state
# after excluding extreme delivery delay outliers
# in the Olist E-Commerce dataset
# =========================================================================

from helper.utils import run_query

sql = """
WITH delivery_delays AS (
    SELECT
        c.customer_state,
        r.review_score,
        CAST(
            julianday(DATE(o.order_delivered_customer_date)) -
            julianday(DATE(o.order_estimated_delivery_date))
            AS INTEGER
        ) AS delivery_delay_days
    FROM olist_orders_dataset AS o
    JOIN olist_customers_dataset AS c
        ON o.customer_id = c.customer_id
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
    customer_state,
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
FROM filtered_deliveries
GROUP BY customer_state
ORDER BY late_delivery_rate_percentage DESC;
"""

run_query(
    "Late Delivery Rate by State",
    sql,
    export_csv=True,
    filename="02_late_delivery_by_state.csv",
)
