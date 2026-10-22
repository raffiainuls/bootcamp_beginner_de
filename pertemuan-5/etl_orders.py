#!/usr/bin/env python3
"""Extract dan load banyak tabel berdasarkan config.yml."""
import os
import re
from pathlib import Path

import clickhouse_connect
import pandas as pd
import psycopg2
import yaml
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")


def read_config():
    with open(ROOT_DIR / "config.yml", encoding="utf-8") as file:
        return yaml.safe_load(file)


def validate_identifier(value, label):
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", value):
        raise ValueError(f"{label} tidak valid: {value}")
    return value


def read_schema(table_config):
    schema_path = ROOT_DIR / table_config["schema_file"]
    with open(schema_path, encoding="utf-8") as file:
        return file.read().format(
            target_database=table_config["target_database"],
            target_table=table_config["target_table"],
        )


def extract_table(table_config, postgres_connection):
    source_table = validate_identifier(table_config["source_table"], "Nama tabel sumber")
    columns = [
        validate_identifier(column, "Nama kolom")
        for column in table_config["columns"]
    ]
    order_by = validate_identifier(table_config["order_by"], "Kolom pengurutan")
    query = "SELECT {} FROM {} ORDER BY {}".format(
        ", ".join(columns), source_table, order_by
    )
    return pd.read_sql_query(query, postgres_connection)


def create_connection():
    return psycopg2.connect(
        host=os.environ["PGHOST"],
        port=int(os.environ["PGPORT"]),
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
    )


def create_clickhouse_client():
    return clickhouse_connect.get_client(
        host=os.environ["CH_HOST"],
        port=int(os.environ["CH_PORT"]),
        username=os.environ["CH_USER"],
        password=os.environ["CH_PASSWORD"],
    )


def load_table(dataframe, table_config, clickhouse_client):
    database = validate_identifier(
        table_config["target_database"], "Nama database tujuan"
    )
    table = validate_identifier(table_config["target_table"], "Nama tabel tujuan")

    schema_sql = read_schema(table_config)
    for statement in schema_sql.split(";"):
        if statement.strip():
            clickhouse_client.command(statement)

    clickhouse_client.command(f"TRUNCATE TABLE {database}.{table}")
    if not dataframe.empty:
        clickhouse_client.insert_df(f"{database}.{table}", dataframe)


def main():
    config = read_config()
    postgres_connection = create_connection()
    clickhouse_client = create_clickhouse_client()

    try:
        for table_config in config["tables"]:
            source_table = table_config["source_table"]
            target_table = "{}.{}".format(
                table_config["target_database"], table_config["target_table"]
            )
            dataframe = extract_table(table_config, postgres_connection)
            print(f"Extract selesai: {source_table} ({len(dataframe)} baris)")
            load_table(dataframe, table_config, clickhouse_client)
            print(f"Load selesai: {target_table}")
    finally:
        postgres_connection.close()
        clickhouse_client.close()


if __name__ == "__main__":
    main()
