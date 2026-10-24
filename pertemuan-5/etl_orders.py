#!/usr/bin/env python3
"""Extract dan load banyak tabel berdasarkan config.yml."""

# Mengimpor os untuk membaca environment variable.
import os
# Mengimpor re untuk memeriksa pola nama tabel dan kolom.
import re
# Mengimpor Path untuk bekerja dengan lokasi file.
from pathlib import Path

# Mengimpor library untuk terhubung ke ClickHouse.
import clickhouse_connect
# Mengimpor Pandas untuk membaca data dari PostgreSQL.
import pandas as pd
# Mengimpor library untuk terhubung ke PostgreSQL.
import psycopg2
# Mengimpor PyYAML untuk membaca file konfigurasi YAML.
import yaml
# Mengimpor fungsi untuk memuat file environment .env.
from dotenv import load_dotenv


# Menyimpan folder tempat file script ini berada.
ROOT_DIR = Path(__file__).resolve().parent
# Membaca nilai konfigurasi dari file .env di folder yang sama.
load_dotenv(ROOT_DIR / ".env")


# Membuat function untuk membaca konfigurasi tabel dari config.yml.
def read_config():
    # Membuka file config.yml menggunakan encoding UTF-8.
    with open(ROOT_DIR / "config.yml", encoding="utf-8") as file:
        # Mengubah isi YAML menjadi dictionary Python.
        return yaml.safe_load(file)


# Membuat function untuk memastikan nama database, tabel, atau kolom aman digunakan.
def validate_identifier(value, label):
    # Memeriksa apakah nama hanya berisi huruf, angka, underscore, atau titik.
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", value):
        # Menghentikan program jika nama tidak sesuai aturan.
        raise ValueError(f"{label} tidak valid: {value}")
    # Mengembalikan nama yang sudah lolos validasi.
    return value


# Membuat function untuk membaca file schema SQL sebuah tabel.
def read_schema(table_config):
    # Mengambil lokasi file schema dari konfigurasi tabel.
    schema_path = ROOT_DIR / table_config["schema_file"]
    # Membuka file SQL schema dengan encoding UTF-8.
    with open(schema_path, encoding="utf-8") as file:
        # Membaca isi SQL dan mengisi nama database serta tabel tujuan.
        return file.read().format(
            # Mengisi placeholder nama database tujuan.
            target_database=table_config["target_database"],
            # Mengisi placeholder nama tabel tujuan.
            target_table=table_config["target_table"],
        )


# Membuat function untuk mengambil satu tabel dari PostgreSQL.
def extract_table(table_config, postgres_connection):
    # Membaca dan memvalidasi nama tabel sumber.
    source_table = validate_identifier(table_config["source_table"], "Nama tabel sumber")
    # Memvalidasi setiap nama kolom yang akan diambil.
    columns = [
        # Mengembalikan nama kolom yang sudah lolos validasi.
        validate_identifier(column, "Nama kolom")
        # Mengulang daftar kolom dari konfigurasi.
        for column in table_config["columns"]
    ]
    # Membaca dan memvalidasi kolom untuk pengurutan data.
    order_by = validate_identifier(table_config["order_by"], "Kolom pengurutan")
    # Menyusun query SELECT secara dinamis dari konfigurasi.
    query = "SELECT {} FROM {} ORDER BY {}".format(
        # Menggabungkan nama kolom dengan koma.
        ", ".join(columns),
        # Menambahkan nama tabel sumber.
        source_table,
        # Menambahkan kolom pengurutan.
        order_by,
    )
    # Menjalankan query dan mengembalikan hasil sebagai DataFrame.
    return pd.read_sql_query(query, postgres_connection)


# Membuat function untuk koneksi ke PostgreSQL menggunakan .env.
def create_connection():
    # Membuat koneksi menggunakan konfigurasi PostgreSQL dari environment variable.
    return psycopg2.connect(
        # Membaca alamat host PostgreSQL.
        host=os.environ["PGHOST"],
        # Mengubah nilai port dari teks menjadi integer.
        port=int(os.environ["PGPORT"]),
        # Membaca nama database PostgreSQL.
        dbname=os.environ["PGDATABASE"],
        # Membaca username PostgreSQL.
        user=os.environ["PGUSER"],
        # Membaca password PostgreSQL.
        password=os.environ["PGPASSWORD"],
    )


# Membuat function untuk koneksi ke ClickHouse menggunakan .env.
def create_clickhouse_client():
    # Membuat client ClickHouse menggunakan environment variable.
    return clickhouse_connect.get_client(
        # Membaca alamat host ClickHouse.
        host=os.environ["CH_HOST"],
        # Mengubah nilai port dari teks menjadi integer.
        port=int(os.environ["CH_PORT"]),
        # Membaca username ClickHouse.
        username=os.environ["CH_USER"],
        # Membaca password ClickHouse.
        password=os.environ["CH_PASSWORD"],
    )


# Membuat function untuk menyiapkan schema dan load data ke ClickHouse.
def load_table(dataframe, table_config, clickhouse_client):
    # Membaca dan memvalidasi nama database tujuan.
    database = validate_identifier(
        table_config["target_database"], "Nama database tujuan"
    )
    # Membaca dan memvalidasi nama tabel tujuan.
    table = validate_identifier(table_config["target_table"], "Nama tabel tujuan")

    # Membaca isi file schema SQL berdasarkan konfigurasi tabel.
    schema_sql = read_schema(table_config)
    # Memisahkan beberapa perintah SQL berdasarkan tanda titik koma.
    for statement in schema_sql.split(";"):
        # Hanya menjalankan statement yang tidak kosong.
        if statement.strip():
            # Membuat database atau tabel sesuai isi schema.
            clickhouse_client.command(statement)

    # Mengosongkan tabel tujuan agar data tidak terduplikasi saat dijalankan ulang.
    clickhouse_client.command(f"TRUNCATE TABLE {database}.{table}")
    # Hanya melakukan load jika DataFrame memiliki baris.
    if not dataframe.empty:
        # Memasukkan DataFrame ke tabel tujuan ClickHouse.
        clickhouse_client.insert_df(f"{database}.{table}", dataframe)


# Membuat function utama untuk menjalankan seluruh proses ETL.
def main():
    # Membaca daftar tabel dari file konfigurasi.
    config = read_config()
    # Membuka koneksi ke PostgreSQL.
    postgres_connection = create_connection()
    # Membuka koneksi client ke ClickHouse.
    clickhouse_client = create_clickhouse_client()

    # Memastikan koneksi ditutup meskipun proses mengalami error.
    try:
        # Mengulang setiap konfigurasi tabel.
        for table_config in config["tables"]:
            # Mengambil nama tabel sumber untuk pesan log.
            source_table = table_config["source_table"]
            # Membuat nama lengkap tabel tujuan untuk pesan log.
            target_table = "{}.{}".format(
                # Mengambil nama database tujuan.
                table_config["target_database"],
                # Mengambil nama tabel tujuan.
                table_config["target_table"],
            )
            # Mengambil data dari tabel PostgreSQL.
            dataframe = extract_table(table_config, postgres_connection)
            # Menampilkan jumlah data yang berhasil diambil.
            print(f"Extract selesai: {source_table} ({len(dataframe)} baris)")
            # Menyiapkan tabel dan mengirim data ke ClickHouse.
            load_table(dataframe, table_config, clickhouse_client)
            # Menampilkan pesan bahwa load sudah selesai.
            print(f"Load selesai: {target_table}")
    finally:
        # Menutup koneksi PostgreSQL setelah proses selesai.
        postgres_connection.close()
        # Menutup koneksi ClickHouse setelah proses selesai.
        clickhouse_client.close()


# Menjalankan function main hanya ketika file dieksekusi langsung.
if __name__ == "__main__":
    main()
