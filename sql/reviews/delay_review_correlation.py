# =========================================================================
# Olist E-Commerce SQL Analysis
# Database: olist_ecommerce.db
# Domain: Reviews
# Script: delay_review_correlation.py
# Objective: Calculate the Pearson correlation between
# delivery delay and review score after excluding extreme
# delivery delay outliers in the Olist E-Commerce dataset
# =========================================================================

from helper.utils import run_query

sql = """
WITH delivery_reviews AS (
    SELECT
        CAST(
            julianday(DATE(o.order_delivered_customer_date)) -
            julianday(DATE(o.order_estimated_delivery_date))
            AS INTEGER
        ) AS delivery_delay_days,
        r.review_score
    FROM olist_orders_dataset AS o
    JOIN olist_order_reviews_dataset AS r
        ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
),

filtered_data AS (
    SELECT *
    FROM delivery_reviews
    WHERE NOT (
        delivery_delay_days > 100
        AND review_score = 5
    )
)

SELECT
    COUNT(*) AS total_orders,
    ROUND(
        (
            COUNT(*) * SUM(delivery_delay_days * review_score) -
            SUM(delivery_delay_days) * SUM(review_score)
        ) /
        (
            SQRT(
                (COUNT(*) * SUM(delivery_delay_days * delivery_delay_days) -
                 SUM(delivery_delay_days) * SUM(delivery_delay_days))
                *
                (COUNT(*) * SUM(review_score * review_score) -
                 SUM(review_score) * SUM(review_score))
            )
        ),
        4
    ) AS pearson_correlation_coefficient
FROM filtered_data;
"""

run_query("Delivery Delay vs Review Score Correlation (Outliers Removed)", sql)
