"""
================================================================================
Olist E-Commerce Analysis Project
Module: analysis/export_powerbi_data.py

Objective:
    Extracts, transforms, and exports clean analytical datasets from the
    Olist SQLite database for use in the Power BI dashboard. Each exported
    dataset is designed to support business reporting, KPI tracking, customer
    segmentation, and interactive visualizations.

Key Operations:
    - Connect to SQLite database
    - Execute SQL queries to create analytics-ready datasets
    - Export cleaned fact and dimension tables as CSV files
    - Generate monthly aggregated revenue data
    - Preview exported datasets for validation
    - Prepare a star-schema-friendly data model for Power BI

Database Source:
    olist_ecommerce.db (Project Root)

Outputs:
    - exports/powerbi/fact_orders_clean.csv
    - exports/powerbi/dim_customers_rfm.csv
    - exports/powerbi/agg_monthly_revenue.csv

Project Pipeline:
    01_data_cleaning.py
        ↓
    02_eda.py
        ↓
    03_delivery_outlier_investigation.py
        ↓
    SQL Analysis (Phase 3)
        ↓
    export_powerbi_data.py
        ↓
    Power BI Dashboard
================================================================================
"""

from helper.utils import run_query

sql1 = """
WITH orders_clean AS (

    SELECT
        o.order_id,
        o.order_status,

        o.order_purchase_timestamp,
        o.order_approved_at,
        o.order_delivered_customer_date,
        o.order_estimated_delivery_date,

        DATE(o.order_purchase_timestamp) AS order_date,
        strftime('%Y-%m', o.order_purchase_timestamp) AS order_month,

        c.customer_id,
        c.customer_unique_id,
        c.customer_city,
        c.customer_state,

        oi.seller_id,
        s.seller_city,
        s.seller_state,

        oi.product_id,
        COALESCE(
            pct.product_category_name_english,
            p.product_category_name
        ) AS product_category,

        ROUND(oi.price, 2) AS price,
        ROUND(oi.freight_value, 2) AS freight_value,
        ROUND(oi.price + oi.freight_value, 2) AS gmv,

        ROUND(
            (oi.freight_value / NULLIF(oi.price, 0)) * 100,
            2
        ) AS freight_percentage,

        r.review_score,

        CAST(
            julianday(DATE(o.order_delivered_customer_date)) -
            julianday(DATE(o.order_estimated_delivery_date))
            AS INTEGER
        ) AS delivery_delay_days

    FROM olist_orders_dataset AS o

    JOIN olist_customers_dataset AS c
        ON o.customer_id = c.customer_id

    JOIN olist_order_items_dataset AS oi
        ON o.order_id = oi.order_id

    JOIN olist_products_dataset AS p
        ON oi.product_id = p.product_id

    LEFT JOIN product_category_name_translation AS pct
        ON p.product_category_name = pct.product_category_name

    JOIN olist_sellers_dataset AS s
        ON oi.seller_id = s.seller_id

    LEFT JOIN olist_order_reviews_dataset AS r
        ON o.order_id = r.order_id

    WHERE o.order_status = 'delivered'
)

SELECT
    order_id,
    order_status,

    order_purchase_timestamp,
    order_approved_at,
    order_delivered_customer_date,
    order_estimated_delivery_date,

    order_date,
    order_month,

    customer_id,
    customer_unique_id,
    customer_city,
    customer_state,

    seller_id,
    seller_city,
    seller_state,

    CASE
        WHEN customer_state = seller_state
        THEN 'Intra-State'
        ELSE 'Inter-State'
    END AS shipping_type,

    product_id,
    product_category,

    price,
    freight_value,
    gmv,
    freight_percentage,

    review_score,
    delivery_delay_days,

    CASE
        WHEN delivery_delay_days > 0 THEN 1
        ELSE 0
    END AS late_delivery_flag,

    CASE
        WHEN (
            delivery_delay_days > 100
            AND review_score = 5
        )
        OR (
            delivery_delay_days < -100
            AND review_score = 1
        )
        THEN 1
        ELSE 0
    END AS delivery_delay_outlier_flag,

    CASE
        WHEN
            delivery_delay_days > 100
            AND review_score = 5
        THEN 'Late >100 days with 5-star review'

        WHEN
            delivery_delay_days < -100
            AND review_score = 1
        THEN 'Early <-100 days with 1-star review'

        ELSE 'None'
    END AS delivery_delay_outlier_reason

FROM orders_clean;"""
run_query("Fact Orders Export", sql1, export_csv=True, filename="fact_orders_clean.csv")

sql2 = """
WITH customer_rfm AS (

    SELECT
        c.customer_unique_id,

        MAX(DATE(o.order_purchase_timestamp)) AS last_order_date,

        COUNT(DISTINCT o.order_id) AS frequency,

        ROUND(
            SUM(oi.price + oi.freight_value),
            2
        ) AS monetary

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
        julianday('2018-10-17') -
        julianday(last_order_date)
        AS INTEGER
    ) AS recency,

    frequency,

    monetary

FROM customer_rfm;
"""
run_query(
    "Customer RFM Export", sql2, export_csv=True, filename="dim_customers_rfm.csv"
)

sql3 = """
SELECT
    strftime('%Y-%m', o.order_purchase_timestamp) AS order_month,

    ROUND(
        SUM(oi.price + oi.freight_value),
        2
    ) AS monthly_gmv

FROM olist_orders_dataset AS o

JOIN olist_order_items_dataset AS oi
    ON o.order_id = oi.order_id

WHERE o.order_status = 'delivered'

GROUP BY order_month

ORDER BY order_month;
"""

run_query(
    "Monthly Revenue Export", sql3, export_csv=True, filename="agg_monthly_revenue.csv"
)
