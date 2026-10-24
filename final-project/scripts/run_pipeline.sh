#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

docker compose up -d clickhouse
python3 ingestion/load_clickhouse.py
if command -v dbt >/dev/null 2>&1; then
  DBT_CMD=(dbt)
else
  DBT_CMD=(python3 -m dbt.cli.main)
fi
"${DBT_CMD[@]}" run --project-dir dbt --profiles-dir dbt
"${DBT_CMD[@]}" test --project-dir dbt --profiles-dir dbt
