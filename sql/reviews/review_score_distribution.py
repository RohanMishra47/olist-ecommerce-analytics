# =========================================================================
# Olist E-Commerce SQL Analysis
# Database: olist_ecommerce.db
# Domain: Reviews
# Script: review_score_distribution.py
# Objective: Review score distribution analysis for Olist E-Commerce dataset
# =========================================================================

from helper.utils import run_query

run_query(
    "Review Score Distribution & Global Average",
    """
    SELECT
        review_score,
        COUNT(review_id) AS total_reviews,
        ROUND(COUNT(review_id) * 100.0 / SUM(COUNT(review_id)) OVER(), 2) AS percentage_share,
        ROUND((SELECT AVG(review_score) FROM olist_order_reviews_dataset), 2) AS global_avg_score
    FROM olist_order_reviews_dataset
    GROUP BY review_score
    ORDER BY review_score DESC;
""",
)
