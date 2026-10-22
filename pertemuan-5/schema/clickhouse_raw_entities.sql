CREATE DATABASE IF NOT EXISTS {target_database};

CREATE TABLE IF NOT EXISTS {target_database}.{target_table} (
    id Int32,
    code String,
    name String,
    entity_type_id Int16,
    is_vendor Int16,
    status Int16,
    created_at DateTime
) ENGINE = MergeTree ORDER BY id;
