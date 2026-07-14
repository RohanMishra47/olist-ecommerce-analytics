# =========================================================================
# Olist E-Commerce SQL Analysis
# Database: olist_ecommerce.db
# Domain: Reviews
# Script: avg_review_by_seller.py
# Objective: Calculate the average review score by
# seller for high-volume sellers in the Olist E-Commerce dataset
# =========================================================================

from helper.utils import run_query

sql = """
SELECT
    oi.seller_id,
    COUNT(DISTINCT o.order_id) AS total_delivered_orders,
    ROUND(AVG(r.review_score), 2) AS average_review_score
FROM olist_orders_dataset AS o
JOIN olist_order_reviews_dataset AS r
    ON o.order_id = r.order_id
JOIN olist_order_items_dataset AS oi
    ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY oi.seller_id
HAVING COUNT(DISTINCT o.order_id) >= 50
ORDER BY
    average_review_score DESC,
    total_delivered_orders DESC;
"""

run_query(
    "Average Review Score by Seller",
    sql,
    export_csv=True,
    filename="avg_review_by_seller.csv",
)
