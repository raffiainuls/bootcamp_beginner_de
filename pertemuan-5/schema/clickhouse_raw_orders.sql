CREATE DATABASE IF NOT EXISTS {target_database};

CREATE TABLE IF NOT EXISTS {target_database}.{target_table} (
    id Int32,
    no_document String,
    customer_id Int32,
    vendor_id Int32,
    total_order_items Int32,
    created_at DateTime
) ENGINE = MergeTree ORDER BY id;
