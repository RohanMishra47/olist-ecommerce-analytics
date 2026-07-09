# =========================================================================
# Olist E-Commerce SQL Analysis
# Database: olist_ecommerce.db
# Domain: Customers
# Script: 06_customer_state_distribution.py
# Objective: Customer state distribution analysis for Olist E-Commerce dataset
# =========================================================================

from helper.utils import run_query

run_query(
    "Customer Count by State",
    """
    SELECT
        customer_state,
        COUNT(DISTINCT customer_unique_id) AS unique_customer_count,
        COUNT(customer_id) AS total_orders_placed,
        ROUND(COUNT(DISTINCT customer_unique_id) * 100.0 / SUM(COUNT(DISTINCT customer_unique_id)) OVER(), 2) AS percentage_share
    FROM olist_customers_dataset
    GROUP BY customer_state
    ORDER BY unique_customer_count DESC;
""",
)
