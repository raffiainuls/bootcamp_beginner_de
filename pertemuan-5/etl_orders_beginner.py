#!/usr/bin/env python3
"""Versi pemula: alur Extract dan Load ditulis lurus dari atas ke bawah."""
import clickhouse_connect
import pandas as pd
import psycopg2

# 1. Connect ke PostgreSQL.
postgres_connection = psycopg2.connect(
    host="localhost",
    port=5433,
    dbname="nusacode_db",
    user="postgresdev",
    password="adminpass123",
)

# 2. Extract data dari tabel orders.
query = """
    SELECT id, no_document, customer_id, vendor_id,
           total_order_items, created_at
    FROM bootcamp.orders
    ORDER BY id
"""
orders_df = pd.read_sql_query(query, postgres_connection)
postgres_connection.close()
print(f"Extract selesai: {len(orders_df)} baris")

# 3. Connect ke ClickHouse.
clickhouse_client = clickhouse_connect.get_client(
    host="localhost",
    port=8123,
    username="clickhousedev",
    password="adminpass123",
)

# 4. Siapkan database dan tabel tujuan.
clickhouse_client.command("CREATE DATABASE IF NOT EXISTS staging")
clickhouse_client.command("""
    CREATE TABLE IF NOT EXISTS staging.raw_orders (
        id Int32,
        no_document String,
        customer_id Int32,
        vendor_id Int32,
        total_order_items Int32,
        created_at DateTime
    ) ENGINE = MergeTree ORDER BY id
""")

# 5. Kosongkan tabel supaya saat script dijalankan ulang data tidak duplikat.
clickhouse_client.command("TRUNCATE TABLE staging.raw_orders")

# 6. Load data ke ClickHouse.
if not orders_df.empty:
    clickhouse_client.insert_df("staging.raw_orders", orders_df)

print("Load selesai: staging.raw_orders siap di ClickHouse")
