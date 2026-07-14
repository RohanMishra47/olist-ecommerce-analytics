# =========================================================================
# Olist E-Commerce SQL Analysis
# Database: olist_ecommerce.db
# Domain: Reviews
# Script: order_status_avg_review.py
# Objective: Analyze cancellation and non-delivery rates and
# their relationship to review scores in the Olist E-Commerce dataset
# =========================================================================

from helper.utils import run_query

sql = """
SELECT
    o.order_status,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(
        COUNT(DISTINCT o.order_id) * 100.0 /
        (
            SELECT COUNT(*)
            FROM olist_orders_dataset
        ),
        2
    ) AS order_percentage,
    ROUND(AVG(r.review_score), 2) AS average_review_score
FROM olist_orders_dataset AS o
LEFT JOIN olist_order_reviews_dataset AS r
    ON o.order_id = r.order_id
GROUP BY o.order_status
ORDER BY total_orders DESC;
"""

run_query(
    "Order Status Distribution and Review Scores",
    sql,
    export_csv=True,
    filename="order_status_avg_review.csv",
)
