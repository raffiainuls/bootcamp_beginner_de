{{ config(materialized='view', schema='staging') }}

SELECT
    id AS order_id,
    no_document,
    customer_id,
    vendor_id,
    total_order_items,
    toDate(created_at) AS order_date
FROM {{ source('staging', 'raw_orders') }}
