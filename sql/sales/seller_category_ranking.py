# ===================================================================
# Olist E-Commerce SQL Analysis
# Database: olist_ecommerce.db
# Domain: Sales
# Script: seller_category_ranking.py
# Objective: Rank sellers within each product category
# by revenue for Olist E-Commerce dataset
# ===================================================================

from helper.utils import run_query

sql_query = """
WITH seller_category_revenue AS (
    SELECT 
        COALESCE(t.product_category_name_english, p.product_category_name) AS category_name,
        oi.seller_id,
        ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue_gmv
    FROM olist_order_items_dataset oi
    INNER JOIN olist_orders_dataset o 
        ON oi.order_id = o.order_id
    INNER JOIN olist_products_dataset p 
        ON oi.product_id = p.product_id
    LEFT JOIN product_category_name_translation t 
        ON p.product_category_name = t.product_category_name
    WHERE o.order_status = 'delivered'
      AND p.product_category_name IS NOT NULL
    GROUP BY category_name, oi.seller_id
),
ranked_sellers AS (
    SELECT 
        category_name,
        seller_id,
        total_revenue_gmv,
        DENSE_RANK() OVER (
            PARTITION BY category_name 
            ORDER BY total_revenue_gmv DESC
        ) AS seller_rank
    FROM seller_category_revenue
)
SELECT 
    category_name,
    seller_id,
    total_revenue_gmv,
    seller_rank
FROM ranked_sellers
WHERE seller_rank <= 3
ORDER BY category_name ASC, seller_rank ASC;
"""

run_query("Top 3 Sellers Ranked Within Each Product Category", sql_query)
