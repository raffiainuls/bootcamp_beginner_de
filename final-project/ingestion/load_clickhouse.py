"""Extract CSV files and load them unchanged into the ClickHouse bronze layer."""

import csv
import os
from pathlib import Path

import clickhouse_connect


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
SOURCE_CSV = DATA_DIR / "source" / "youtube_trending_dataset.csv"
CATEGORY_CSV = DATA_DIR / "master" / "category_master.csv"
SEASON_CSV = DATA_DIR / "master" / "season_calendar.csv"


def rows_from_csv(path: Path):
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        columns = reader.fieldnames or []
        rows = [[row.get(column, "") for column in columns] for row in reader]
    return columns, rows


def load_table(client, database, table, csv_path):
    columns, rows = rows_from_csv(csv_path)
    definition = ",\n".join(f"`{column}` String" for column in columns)
    client.command(f"CREATE DATABASE IF NOT EXISTS {database}")
    client.command(
        f"""CREATE TABLE IF NOT EXISTS {database}.{table}
        ({definition})
        ENGINE = MergeTree()
        ORDER BY tuple()"""
    )
    client.command(f"TRUNCATE TABLE {database}.{table}")
    if rows:
        client.insert(table, rows, column_names=columns, database=database)
    print(f"Loaded {len(rows):,} rows into {database}.{table}")


def main():
    client = clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_PORT", "18123")),
        username=os.getenv("CLICKHOUSE_USER", "clickhousedev"),
        password=os.getenv("CLICKHOUSE_PASSWORD", "adminpass123"),
    )
    load_table(client, "bronze", "raw_youtube_trending", SOURCE_CSV)
    load_table(client, "bronze", "raw_category_master", CATEGORY_CSV)
    load_table(client, "bronze", "raw_season_calendar", SEASON_CSV)
    print("Bronze load completed. All source columns remain String by design.")


if __name__ == "__main__":
    main()
