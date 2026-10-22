{{ config(materialized='table', schema='datamart') }}

SELECT
    order_date,
    count() AS total_orders,
    sum(total_order_items) AS total_items_ordered,
    uniqExact(customer_id) AS unique_customers
FROM {{ ref('stg_orders') }}
GROUP BY order_date
ORDER BY order_date
