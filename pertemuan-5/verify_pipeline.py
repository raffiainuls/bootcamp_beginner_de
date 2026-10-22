#!/usr/bin/env python3
"""Verifikasi semua tabel yang terdaftar di config.yml."""
import os
import re
from pathlib import Path

import clickhouse_connect
import psycopg2
import yaml
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")


def identifier(value, label):
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", value):
        raise ValueError(f"{label} tidak valid: {value}")
    return value


def read_config():
    with open(ROOT_DIR / "config.yml", encoding="utf-8") as file:
        return yaml.safe_load(file)


def main():
    config = read_config()
    postgres = psycopg2.connect(
        host=os.environ["PGHOST"],
        port=int(os.environ["PGPORT"]),
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
    )
    clickhouse = clickhouse_connect.get_client(
        host=os.environ["CH_HOST"],
        port=int(os.environ["CH_PORT"]),
        username=os.environ["CH_USER"],
        password=os.environ["CH_PASSWORD"],
    )

    all_tables_match = True
    try:
        with postgres.cursor() as cursor:
            for table_config in config["tables"]:
                source_table = identifier(table_config["source_table"], "Tabel sumber")
                cursor.execute(f"SELECT count(*) FROM {source_table}")
                source_count = cursor.fetchone()[0]

                target_database = identifier(
                    table_config["target_database"], "Database tujuan"
                )
                target_table = identifier(table_config["target_table"], "Tabel tujuan")
                target_name = f"{target_database}.{target_table}"
                target_count = clickhouse.command(f"SELECT count() FROM {target_name}")

                print(
                    f"{source_table:<24}: "
                    f"PostgreSQL={source_count}, ClickHouse={target_count}"
                )
                if source_count != target_count:
                    all_tables_match = False

        mart_count = clickhouse.command(
            "SELECT count() FROM datamart.mart_daily_orders"
        )
        print(f"datamart.mart_daily_orders : {mart_count} baris")
    finally:
        postgres.close()
        clickhouse.close()

    if not all_tables_match:
        raise SystemExit("GAGAL: jumlah baris sumber dan target berbeda")
    if mart_count == 0:
        raise SystemExit("GAGAL: datamart kosong")
    print("VERIFIKASI BERHASIL")


if __name__ == "__main__":
    main()
