# =========================================================================
# Olist E-Commerce SQL Analysis
# Database: olist_ecommerce.db
# Domain: Finances
# Script: payment_type_analysis.py
# Objective: Payment type analysis for Olist E-Commerce dataset
# =========================================================================

from helper.utils import run_query

run_query(
    "Payment Type Distribution and The Average Number of Installments Per Payment Type",
    """
    SELECT
        p.payment_type,
        COUNT(p.order_id) AS payment_count,
        ROUND(COUNT(p.order_id) * 100.0 / SUM(COUNT(p.order_id)) OVER(), 2) AS payment_percentage,
        ROUND(SUM(p.payment_value), 2) AS total_monetary_value,
        ROUND(AVG(p.payment_installments), 2) AS avg_installments
    FROM olist_order_payments_dataset p
    INNER JOIN olist_orders_dataset o
        ON p.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY p.payment_type
    ORDER BY payment_count DESC;
""",
)
