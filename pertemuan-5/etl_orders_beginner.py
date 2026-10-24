#!/usr/bin/env python3
"""Versi pemula: alur Extract dan Load ditulis lurus dari atas ke bawah."""

# Mengimpor library untuk mengirim query dan data ke ClickHouse.
import clickhouse_connect
# Mengimpor Pandas untuk membaca hasil query sebagai DataFrame.
import pandas as pd
# Mengimpor library untuk membuat koneksi ke PostgreSQL.
import psycopg2

# 1. Membuat koneksi ke PostgreSQL sebagai sumber data.
postgres_connection = psycopg2.connect(
    # Menentukan alamat server PostgreSQL.
    host="localhost",
    # Menentukan port PostgreSQL.
    port=5433,
    # Menentukan nama database sumber.
    dbname="nusacode_db",
    # Menentukan username database.
    user="postgresdev",
    # Menentukan password database.
    password="adminpass123",
)

# 2. Menulis query untuk mengambil data dari tabel orders.
query = """
    SELECT id, no_document, customer_id, vendor_id,
           total_order_items, created_at
    FROM bootcamp.orders
    ORDER BY id
"""
# Menjalankan query dan menyimpan hasilnya sebagai DataFrame.
orders_df = pd.read_sql_query(query, postgres_connection)
# Menutup koneksi PostgreSQL setelah proses extract selesai.
postgres_connection.close()
# Menampilkan jumlah baris yang berhasil diambil.
print(f"Extract selesai: {len(orders_df)} baris")

# 3. Membuat koneksi ke ClickHouse sebagai tujuan data.
clickhouse_client = clickhouse_connect.get_client(
    # Menentukan alamat server ClickHouse.
    host="localhost",
    # Menentukan port ClickHouse.
    port=8123,
    # Menentukan username ClickHouse.
    username="clickhousedev",
    # Menentukan password ClickHouse.
    password="adminpass123",
)

# 4. Membuat database staging jika database belum tersedia.
clickhouse_client.command("CREATE DATABASE IF NOT EXISTS staging")
# Membuat tabel tujuan jika tabel belum tersedia.
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

# 5. Mengosongkan tabel agar eksekusi ulang tidak membuat data duplikat.
clickhouse_client.command("TRUNCATE TABLE staging.raw_orders")

# 6. Memastikan DataFrame memiliki data sebelum proses load.
if not orders_df.empty:
    # Memasukkan seluruh DataFrame ke tabel ClickHouse.
    clickhouse_client.insert_df("staging.raw_orders", orders_df)

# Menampilkan pesan bahwa proses load sudah selesai.
print("Load selesai: staging.raw_orders siap di ClickHouse")
